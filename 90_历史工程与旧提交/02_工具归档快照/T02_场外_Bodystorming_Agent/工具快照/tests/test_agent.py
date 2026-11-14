import copy
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from agent.demo import EVENTS
from agent.engine import Engine, check_references, export_markdown
from agent.knowledge import retrieve
from agent.model import AgentError, ModelClient
from agent.storage import Store
from server import make_server


class FakeModel:
    """Test double only. Not available in application live mode."""
    def __init__(self):
        self.calls=[]
        self.bad_refs=False
        self.fail=False

    def complete(self, system, payload, image=None):
        self.calls.append(copy.deepcopy(payload))
        if self.fail:
            raise AgentError('测试注入的服务商失败')
        if 'events' not in system and 'scene' in system:
            return dict(scene='火星',goal='搭建',constraints=payload['constraints'],resources='纸板绳子',missing='无')
        if '"events"' in system:
            events=copy.deepcopy(EVENTS)
            if self.bad_refs:
                events[0]['evidence_ids']=['fabricated-reference']
            return {'events':events}
        return dict(understanding=payload['selected_event']['content'],basis=payload['observation'],level=payload['level'],
                    message='测试用提示，不是真实模型输出。',next_observation='新的道具关系',knowledge_status='测试桩',evidence_ids=[])


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=Store(Path(self.tmp.name)/'test.sqlite3')
        self.model=FakeModel()
        self.engine=Engine(self.store,self.model)

    def tearDown(self):
        self.tmp.cleanup()

    def session(self,mode='live'):
        return self.store.create(dict(title='测试',story='火星基地用纸板与绳子搭建休息空间。',constraints='只有纸板、绳子，剩余3分钟。',mode=mode))

    def prepared(self):
        sid=self.session()['id']
        self.engine.generate(sid)
        self.engine.select(sid,'E1')
        return sid

    def test_selected_event_and_history_are_explicit_model_inputs(self):
        sid=self.prepared()
        doc=self.engine.guide(sid,'明确求助，备用电池方案已拒绝。','help')
        self.engine.feedback(sid,doc['hints'][0]['id'],'rejected')
        self.engine.guide(sid,'仍想要更多方向。','more')
        payload=self.model.calls[-1]
        self.assertEqual(payload['selected_event']['id'],'E1')
        self.assertIn('纸板',payload['constraints'])
        self.assertEqual(payload['previous_hints'][0]['feedback'],'rejected')
        self.assertEqual(payload['level'],'L2')

    def test_exploring_and_uncertain_do_not_call_model(self):
        sid=self.prepared()
        before=len(self.model.calls)
        doc=self.engine.guide(sid,'仍在探索两种连接方式','exploring')
        self.assertEqual(doc['hints'][-1]['level'],'L0')
        doc=self.engine.guide(sid,'没说话但仍在摆放纸板','uncertain')
        self.assertEqual(doc['hints'][-1]['level'],'confirm')
        self.assertEqual(len(self.model.calls),before)
        self.assertEqual(next(l for l in reversed(doc['logs']) if l['node']=='guide')['kind'],'规则')

    def test_event_change_clears_active_history(self):
        sid=self.prepared()
        self.engine.guide(sid,'需要一点提示','help')
        doc=self.engine.select(sid,'E2')
        self.assertEqual(doc['hints'],[])
        self.assertEqual(doc['observation'],'')
        self.assertTrue(len(doc['logs'])>4)

    def test_generation_failure_clears_old_candidates_and_never_falls_back(self):
        sid=self.prepared()
        self.model.fail=True
        with self.assertRaises(AgentError):self.engine.generate(sid)
        doc=self.store.get(sid)
        self.assertEqual(doc['events'],[])
        self.assertIsNone(doc['selected_event'])
        self.assertEqual(doc['logs'][-1]['status'],'error')
        self.assertEqual(doc['mode'],'live')

    def test_invented_citation_is_rejected(self):
        self.model.bad_refs=True
        sid=self.session()['id']
        with self.assertRaises(AgentError):self.engine.generate(sid)
        self.assertEqual(self.store.get(sid)['events'],[])
        self.assertEqual(self.store.get(sid)['logs'][-1]['node'],'validate')
        self.assertEqual(self.store.get(sid)['logs'][-1]['status'],'error')

    def test_local_retrieval_returns_real_source_and_no_random_fallback(self):
        doc=self.store.add_document('身体即兴','教学笔记 p.2','身体即兴可通过道具、空间与角色变化探索设计。')
        results=retrieve(self.store.documents(),'身体即兴道具')
        self.assertEqual(results[0]['source'],'教学笔记 p.2')
        self.assertTrue(results[0]['id'].startswith(doc['id']))
        self.assertEqual(retrieve(self.store.documents(),'xyzzy987654'),[])

    def test_demo_is_marked_and_persists(self):
        sid=self.session('demo')['id']
        doc=self.engine.generate(sid)
        self.assertTrue(all(l['mode']=='demo' for l in doc['logs']))
        self.assertEqual(len(self.model.calls),0)
        restored=Store(self.store.path).get(sid)
        self.assertEqual(restored['events'],doc['events'])
        self.assertIn('手写演示，非模型生成',export_markdown(doc))

    def test_unshown_hint_does_not_escalate_support(self):
        sid=self.prepared()
        doc=self.engine.guide(sid,'需要一点提示','help')
        self.engine.feedback(sid,doc['hints'][-1]['id'],'not_shown')
        doc=self.engine.guide(sid,'更多方向','more')
        self.assertEqual(doc['hints'][-1]['level'],'L1')

    def test_missing_observation_and_unknown_event_do_not_generate(self):
        sid=self.prepared()
        count=len(self.model.calls)
        with self.assertRaises(AgentError):self.engine.guide(sid,'  ','help')
        with self.assertRaises(AgentError):self.engine.select(sid,'does-not-exist')
        self.assertEqual(count,len(self.model.calls))


class TransportTests(unittest.TestCase):
    def test_real_http_adapter_and_structured_output(self):
        received=[]
        class Provider(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_POST(self):
                received.append((self.path,json.loads(self.rfile.read(int(self.headers['Content-Length'])))))
                body=json.dumps({'choices':[{'message':{'content':'{"ok":true}'}}]}).encode()
                self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        server=ThreadingHTTPServer(('127.0.0.1',0),Provider)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            client=ModelClient()
            client.configure(dict(base_url=f'http://127.0.0.1:{server.server_port}/v1',model='test-only',api_key='test-only'))
            answer=client.complete('Return JSON',{'test':'explicit input'})
            self.assertEqual(answer,{'ok':True})
            self.assertEqual(received[0][0],'/v1/chat/completions')
            self.assertEqual(received[0][1]['response_format'],{'type':'json_object'})
            self.assertEqual(received[0][1]['messages'][1]['content'],'{"test": "explicit input"}')
        finally:
            server.shutdown();server.server_close();thread.join()


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.server=make_server(0,self.tmp.name)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.url=f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()

    def request(self,path,data=None,origin=None):
        headers={'Content-Type':'application/json'}
        if origin:headers['Origin']=origin
        req=urllib.request.Request(self.url+path,data=None if data is None else json.dumps(data).encode(),headers=headers)
        with urllib.request.urlopen(req) as response:return json.loads(response.read())

    def test_http_demo_to_export(self):
        d=self.request('/api/sessions',dict(story='测试故事',constraints='只有纸板',mode='demo'))
        sid=d['id']
        d=self.request(f'/api/sessions/{sid}/generate',{})
        self.assertEqual(len(d['events']),5)
        self.request(f'/api/sessions/{sid}/select',{'event_id':'E1'})
        d=self.request(f'/api/sessions/{sid}/guide',{'observation':'需要帮助','state':'help'})
        self.assertEqual(len(d['hints']),1)
        self.assertEqual(self.request(f'/api/sessions/{sid}/export')['id'],sid)

    def test_public_config_never_contains_secret(self):
        data=self.request('/api/config',{'base_url':'https://example.com/v1','model':'test','api_key':'test-only-secret'})
        self.assertNotIn('test-only-secret',json.dumps(data))
        self.assertNotIn('test-only-secret',json.dumps(self.request('/api/config')))
        self.assertTrue(data['configured'])

    def test_foreign_origin_is_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as exc:
            self.request('/api/config',{},'https://foreign.example')
        self.assertEqual(exc.exception.code,403)

    def test_path_traversal_is_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as exc:
            self.request('/%2e%2e/server.py')
        self.assertEqual(exc.exception.code,403)


if __name__=='__main__':unittest.main()
