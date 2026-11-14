"""Fee-free tests against a local HTTP server, with actual video downloads/probing."""
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
from unittest.mock import patch
import workflow

from workflow import ROOT, Workflow, SeedanceClient, run_tool, write_json


class WorkflowTests(unittest.TestCase):
    def test_atomic_json_recovers_from_transient_windows_read_handle(self):
        target=self.root/'atomic-state.json'
        replace=workflow.os.replace
        attempts=[]
        def busy_then_replace(source,destination):
            attempts.append(1)
            if len(attempts)<3:
                raise PermissionError('simulated Windows read handle')
            return replace(source,destination)
        with patch('workflow.os.replace',side_effect=busy_then_replace):
            write_json(target,{'task_id':'already-submitted-task','status':'running'})
        self.assertEqual(len(attempts),3)
        self.assertEqual(json.loads(target.read_text('utf-8'))['task_id'],'already-submitted-task')
        self.assertFalse(list(self.root.glob('atomic-state.json.*.tmp')))

    @classmethod
    def setUpClass(cls):
        cls.test_dir=ROOT/'reports/test-tmp';cls.test_dir.mkdir(parents=True,exist_ok=True)
        cls.fixture_dir=tempfile.TemporaryDirectory(dir=cls.test_dir)
        cls.fixture=Path(cls.fixture_dir.name)/'fixture.mp4'
        run_tool(['ffmpeg','-hide_banner','-loglevel','error','-f','lavfi','-i','color=c=green:s=640x360:r=24',
                  '-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t','4','-c:v','libx264','-pix_fmt','yuv420p',
                  '-c:a','aac','-y',str(cls.fixture)])

    @classmethod
    def tearDownClass(cls):
        assert Path(cls.fixture_dir.name).resolve().is_relative_to(cls.test_dir.resolve())
        cls.fixture_dir.cleanup()

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=self.test_dir); self.root=Path(self.temp.name)
        project=json.loads((ROOT/'project.json').read_text(encoding='utf-8'))
        job=deepcopy(project['jobs'][1]);job['duration']=4
        project['jobs']=[job];project['timeline']=[{'id':'22','job_id':'22','title':'灯亮','source_start':0,'duration':4}]
        project['api'].update(poll_seconds=.001,wait_seconds=1)
        project['limits']={'max_total_api_tasks':2,'max_total_generated_seconds':8}
        write_json(self.root/'project.json',project)
        (self.root/'assets').mkdir()
        for frame in job['frames']:shutil.copy2(ROOT/'assets'/frame['file'],self.root/'assets'/frame['file'])
        self.w=Workflow(self.root);self.created=[];self.download_headers=[];self.lookups=0
        test=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def send_json(self,data):
                body=json.dumps(data).encode();self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
            def do_POST(self):
                test.created.append(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
                test.post_auth=self.headers.get('Authorization')
                self.send_json({'id':'task_mock_1'})
            def do_GET(self):
                if self.path=='/video':
                    test.download_headers.append(self.headers.get('Authorization'))
                    data=test.fixture.read_bytes();self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
                else:
                    test.lookups+=1
                    self.send_json({'id':'task_mock_1','status':'succeeded','content':{'video_url':f'http://127.0.0.1:{test.http.server_port}/video'},'usage':{'completion_tokens':123}})
        self.http=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        self.thread=threading.Thread(target=self.http.serve_forever,daemon=True);self.thread.start()
        self.client=SeedanceClient(f'http://127.0.0.1:{self.http.server_port}/api/v3','mock-key',allow_test_http=True)

    def tearDown(self):
        self.http.shutdown();self.http.server_close()
        assert self.root.resolve().is_relative_to(self.test_dir.resolve())
        self.temp.cleanup()

    def test_round_trip_resume_and_unauthenticated_download(self):
        result=self.w.generate(client=self.client)
        self.assertTrue(result['completed']);self.assertEqual(len(self.created),1)
        self.assertEqual(self.post_auth,'Bearer mock-key');self.assertEqual(self.download_headers,[None])
        self.assertEqual(self.created[0]['content'][1]['role'],'first_frame')
        self.assertEqual(self.created[0]['ratio'],'adaptive')
        self.assertTrue(self.created[0]['content'][1]['image_url']['url'].startswith('data:image/png;base64,'))
        state=self.w.state();self.assertNotIn('mock-key',json.dumps(state))
        c=state['candidates'][0];self.assertTrue((self.root/c['file']).exists())
        self.w.generate(client=self.client);self.assertEqual(len(self.created),1)
        (self.root/c['file']).unlink()
        self.w.generate(client=self.client);self.assertEqual(len(self.created),1);self.assertEqual(len(self.download_headers),2)

    def test_ambiguous_submission_does_not_resubmit(self):
        class BrokenClient:
            def create(self,payload):raise RuntimeError('模拟提交后断线')
        with self.assertRaises(RuntimeError):self.w.generate(client=BrokenClient())
        self.assertEqual(self.w.state()['candidates'][0]['status'],'uncertain')
        result=self.w.generate(client=self.client)
        self.assertEqual(len(self.created),0);self.assertEqual(result['uncertain'],1);self.assertFalse(result['completed'])

    def test_interrupted_submission_can_attach_and_resume(self):
        self.w.generate(client=self.client);state=self.w.state();c=state['candidates'][0]
        (self.root/c['file']).unlink();c.pop('file');c.pop('task_id');c['status']='submitting';self.w.save(state)
        self.w.generate(client=self.client);self.assertEqual(len(self.created),1)
        self.w.attach_task(c['id'],'task_mock_1');self.w.generate(client=self.client)
        self.assertEqual(len(self.created),1);self.assertEqual(self.w.state()['candidates'][0]['status'],'succeeded')

    def test_limits_are_checked_before_creating_tasks(self):
        self.w.project['limits']['max_total_api_tasks']=1
        with self.assertRaises(ValueError):self.w.generate(variants=2,client=self.client)
        self.assertEqual(self.created,[])

    def test_changed_prompt_creates_distinct_version(self):
        self.w.generate(client=self.client);old=self.w.state()['candidates'][0]['signature']
        self.w.jobs['22']['prompt']+=' 镜头保持静止。'
        self.w.generate(client=self.client)
        self.assertEqual(len(self.created),2)
        self.assertNotEqual(old,self.w.state()['candidates'][1]['signature'])
        self.assertFalse(self.w.public_state()['candidates'][0]['current_version'])

    def test_import_dedup_selection_and_trim_bounds(self):
        c=self.w.import_video('22',self.fixture);again=self.w.import_video('22',self.fixture)
        self.assertEqual(c['id'],again['id']);self.w.select('22',c['id'])
        self.assertEqual(len(self.w.resolved_timeline()),1)
        self.w.update_timing('22',3,2)
        with self.assertRaises(ValueError):self.w.resolved_timeline()

    def test_first_frame_ratio_compatibility(self):
        job=deepcopy(self.w.jobs['22']);self.w.project['api']['ratio']='16:9'
        for model in ('doubao-seedance-2-5-260628','doubao-seedance-2.5'):
            self.w.project['api']['model']=model
            for roles in (['first_frame'],['first_frame','last_frame']):
                with self.subTest(model=model,roles=roles):
                    frame=deepcopy(job['frames'][0])
                    job['frames']=[dict(frame,role=role) for role in roles]
                    self.assertEqual(self.w.payload(job,1)['ratio'],'adaptive')
        self.w.project['api']['model']='doubao-seedance-2-0-260128'
        self.assertEqual(self.w.payload(job,1)['ratio'],'16:9')

    def test_asset_path_cannot_escape_into_credentials(self):
        (self.root/'.env').write_text('ARK_API_KEY=do-not-upload',encoding='utf-8')
        self.w.jobs['22']['frames'][0]['file']='../.env'
        with self.assertRaises(ValueError):self.w.payload(self.w.jobs['22'],1)

    def test_rough_cut_audio_mix_and_reused_draft_material(self):
        from array import array
        import subprocess
        shutil.copytree(ROOT/'vendor',self.root/'vendor',ignore=shutil.ignore_patterns('__pycache__'))
        audio=self.root/'audio/tone.wav';audio.parent.mkdir()
        run_tool(['ffmpeg','-hide_banner','-loglevel','error','-f','lavfi','-i','sine=frequency=440:duration=1','-y',str(audio)])
        self.w.project['audio_tracks']=[{'file':'audio/tone.wav','start':1,'source_start':0,'duration':1,'volume':1}]
        self.w.project['subtitles']=[{'start':.5,'duration':1,'text':'字幕测试'}]
        self.w.project['timeline']=[{'id':'a','job_id':'22','title':'前半段','source_start':0,'duration':2},
                                  {'id':'b','job_id':'22','title':'后半段','source_start':2,'duration':2}]
        c=self.w.import_video('22',self.fixture);self.w.select('22',c['id'])
        result=self.w.assemble('both');self.assertAlmostEqual(result['media']['duration'],4,delta=.15)
        content=json.loads((self.root/result['draft']/'draft_info.json').read_text(encoding='utf-8'))
        self.assertEqual(len(content['materials']['videos']),1)
        self.assertEqual(len(content['materials']['audios']),1)
        track=next(x for x in content['tracks'] if x['type']=='audio')
        self.assertEqual(track['segments'][0]['target_timerange'],{'duration':1000000,'start':1000000})
        result_pcm=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss','1.2','-i',str(self.root/result['mp4']),
             '-t','0.3','-map','0:a','-f','s16le','-'],capture_output=True)
        self.assertEqual(result_pcm.returncode,0,result_pcm.stderr.decode('utf-8',errors='replace'))
        pcm=result_pcm.stdout
        samples=array('h');samples.frombytes(pcm)
        self.assertGreater((sum(x*x for x in samples)/len(samples))**.5,100)


if __name__=='__main__':unittest.main(verbosity=2)
