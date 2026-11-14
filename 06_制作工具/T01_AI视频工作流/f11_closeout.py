"""Record the delivered cut and narrow final draft validation; no API calls."""
import json
from pathlib import Path
from f11_production import ROOT, RUN
from f11_edit import OUT, read, write


def main():
    project_root=ROOT.parents[1]
    source=Path(read(OUT/'剪映草稿验证.json')['path'])
    installed=Path(read(OUT/'已安装剪映草稿.json')['draft'])
    checked=[]
    for folder in [source,installed]:
        content=read(folder/'draft_info.json');meta=read(folder/'draft_meta_info.json')
        assert content['fps']==24 and content['name']==folder.name==meta['draft_name']
        assert content['id']==meta['draft_id'] and Path(meta['draft_cover']).is_file()
        assert meta['tm_duration']==271958333
        assert sum(len(t['segments']) for t in content['tracks'] if t['type']=='video')==72
        for material in content['materials'].get('videos',[])+content['materials'].get('audios',[]):
            if material.get('path'):
                p=Path(material['path']).resolve()
                assert p.is_file() and p.is_relative_to(folder.resolve())
        checked.append(str(folder))
    result={'drafts_checked':checked,'fps':24,'name_id_cover_duration_correct':True,
            'self_contained_media_verified':True,'subtitle_version_full_decode':True,
            'without_dialogue_captions_full_decode':True,'native_window_open_verified':False,
            'all_cloud_submissions_terminal':True,'new_generation_rmb_estimate':208.2589}
    write(OUT/'最终交付复核.json',result)
    memo='''# 《不用麻烦她》全片制作与交付

2026-10-19｜V01｜S35 v9 / F11

用户充值后明确授权全片生成、复用样片和剪映剪辑。本轮已完成4分31.958秒，交付按4分32秒标注。

正式入口：[看成片与全部素材](../05_汇报与成片/V01_不用麻烦她_2026-10-19/看成片与素材.html)。影片、63段原始素材、72个剪辑片段、字幕、声音、后期界面及可编辑剪映草稿集中保存在该目录。

全片为59个视频镜头、11个后期镜头与2个分镜转场。复用20、21、53镜旧样片；其余使用本轮候选，02镜采用额外生成的坐姿修正版02R。03、39镜被方舟服务端拒绝，未重发相同请求，采用原分镜静帧加镜头运动。16镜以登阶中段接17镜进门，38镜去掉误生成的越门槛末段。

本轮59次新提交，57条成功、2条明确拒绝，无待处理或结果不确定任务。按接口返回用量与70元/百万token估算208.2589元；此前6条样片约61.9947元，两轮合计约270.2536元，实际以账单为准。

56个480p视频镜头经本地Real-ESRGAN三倍超分、80%增强画面与20%普通放大混合，输出1920×1080；复用720p样片常规放大。未使用剪映会员的云端高清功能。本地超分、语音识别和剪辑未调用付费服务。

对白逐镜生成，仅为当镜说话者提供声音要求；邱与徐的新任务明确指定老年女性。23个有台词镜头已做本地识别，52段字幕按实际时间对齐，保留剧本用字。没有做同一声纹克隆或逐句听感验收。第24镜门外呼喊延续至25镜。配乐为本地合成的原创三拍子钢琴段落。

通过已安装jianying-editor Skill的JyProject创建自包含草稿。72个画面段、59段对白与现场声、原创配乐、52段对白字幕与5段时间提示分轨保存；工程为24fps，名称、独立ID、封面、时长和所有素材路径均已核对。已安装到本机剪映草稿目录，名称为“不用麻烦她_全片剪辑_1019_093614”。本次11.5版窗口检查只返回主窗口，未完成原生打开或原生导出验证；交付MP4由本地FFmpeg输出。

字幕版与无对白字幕版均已全程解码，72段尺寸与切点、字幕边界、222个预览页本地链接均已检查。相关JSON检查记录集中在成片目录。没有替换此前提交包或Demo项目。
'''
    (project_root/'00_当前创作/16_全片生成与剪辑交付_2026-10-19.md').write_text(memo,'utf-8')
    marker='## 2026-10-19：全片剪辑初版已交付'
    entries={
        project_root/'00_当前创作/01_讨论共识与待定问题.md': '\n\n'+marker+'\n\nS35 v9 / F11已完成全片制作，4分32秒，正式输出在 `05_汇报与成片/V01_不用麻烦她_2026-10-19`。本轮新增生成用量估算208.26元，复用3条旧样片，汇集63条原片；72镜包含2个分镜转场。通过剪映Skill生成并安装24fps自包含草稿，MP4已导出。详情见 [全片生成与剪辑交付](16_全片生成与剪辑交付_2026-10-19.md)。原生剪映窗口打开未验收，后续审阅以完整成片、逐镜预览和交付记录为准。\n',
        project_root/'00_目录说明.md':'\n\n'+marker+'\n\n[《不用麻烦她》4分32秒成片与63条原始素材](05_汇报与成片/V01_不用麻烦她_2026-10-19/看成片与素材.html)，包含字幕版、无对白字幕版及可编辑剪映草稿。[制作与验证记录](00_当前创作/16_全片生成与剪辑交付_2026-10-19.md)。\n',
        ROOT/'README_先看这里.md':'\n\n'+marker+'\n\n全片API项目：`projects/F11_2026-10-19_480p全片`。正式成片与素材：`../../05_汇报与成片/V01_不用麻烦她_2026-10-19/看成片与素材.html`。所有云端任务均已结束；不需要再次调用generate来检查影片。\n\n完整剪辑由 `f11_edit.py` 管理，72镜时间线、切点、字幕与素材来源保存在正式成片目录。通过已安装剪映Skill输出自包含草稿，并生成本地MP4。窗口自动化未完成原生打开验证，写入草稿和完整MP4解码已验证。\n'}
    for path,addition in entries.items():
        if marker not in path.read_text('utf-8-sig'):
            with path.open('a',encoding='utf-8') as f:f.write(addition)
    p=RUN/'project.json';project=read(p)
    project['final_edit_manifest']=str(OUT/'剪辑时间线.json')
    project['final_movie']=str(OUT/'不用麻烦她_1080p_字幕版.mp4')
    project['production_status']='delivered_v01'
    write(p,project)
    (RUN/'检查/剪映窗口/native_main.png').unlink(missing_ok=True)
    print(json.dumps({'delivered':True,'duration_seconds':271.958333,'new_generation_rmb_estimate':208.2589,
                      'preview':str(OUT/'看成片与素材.html'),'native_project':installed.name},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
