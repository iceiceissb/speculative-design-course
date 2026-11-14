"""Build a local pilot screening page and sampled-frame sheets. No API requests."""
from html import escape
import json
from pathlib import Path
from urllib.parse import quote

from PIL import Image, ImageDraw, ImageFont
from f11_pilot import RUN
from workflow import Workflow, probe, read_json, run_tool, write_json, stamp


def contact_sheet(video, destination, label, duration):
    folder = destination.parent / destination.stem
    folder.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
    sheet = Image.new('RGB', (1600, 226), '#17191e')
    draw = ImageDraw.Draw(sheet)
    draw.text((10, 5), label, fill='white', font=font)
    for index, fraction in enumerate((0, .25, .5, .75, .98)):
        second = min(duration * fraction, max(0, duration - .1))
        frame = folder / f'{index:02}.jpg'
        run_tool(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(second),
                  '-i', str(video), '-frames:v', '1', '-vf', 'scale=320:-1', '-y', str(frame)])
        with Image.open(frame) as image:
            image.thumbnail((320, 180))
            sheet.paste(image, (index * 320, 42))
        draw.text((index * 320 + 10, 25), f'{second:.1f}s', fill='#b6c5d5', font=font)
    sheet.save(destination, quality=90)


def main():
    review = RUN / '检查'
    review.mkdir(parents=True, exist_ok=True)
    assessments = read_json(review / '画面检查.json', {})
    cards, rows = [], []
    for profile in ('连接测试', '五镜试片'):
        folder = RUN / profile
        workflow = Workflow(folder)
        for candidate in workflow.state()['candidates']:
            job = workflow.jobs[candidate['job_id']]
            row = {key: candidate[key] for key in ('id', 'job_id', 'task_id', 'status', 'usage', 'error') if key in candidate}
            row.update(profile=profile, title=job['title'], creative_review='pending')
            row['visual_review'] = assessments.get(job['id'], {})
            label = f"{job['id']} · {job['title']}"
            media = ''
            if candidate.get('file') and (folder / candidate['file']).is_file():
                video = folder / candidate['file']
                info = probe(video)
                row['media'] = info
                row['file'] = str(video)
                tokens = candidate.get('usage', {}).get('completion_tokens')
                if tokens is not None:
                    row['estimated_rmb_from_usage'] = round(tokens * 70 / 1000000, 4)
                sheet = review / f"{profile}_{job['id']}_{candidate['id']}.jpg"
                contact_sheet(video, sheet, label, info['duration'])
                row['contact_sheet'] = str(sheet)
                relative = quote(video.relative_to(RUN).as_posix())
                sheet_relative = quote(sheet.relative_to(RUN).as_posix())
                media = (f'<video controls preload="metadata" src="{relative}"></video>'
                         f'<p>{info["width"]}×{info["height"]} · {info["duration"]:.2f} 秒 · '
                         f'{"有音轨" if info["has_audio"] else "无音轨"}</p>'
                         f'<a href="{sheet_relative}">查看动作抽帧</a> · <a href="{relative}">打开原视频</a>')
            else:
                media = f'<p>{escape(candidate.get("error", "任务尚未下载"))}</p>'
            assessment = row['visual_review']
            review_text = escape(assessment.get('note', '动作与声音待审阅'))
            cards.append(f'<article><small>{escape(profile)}</small><h2>{escape(label)}</h2>'
                         f'<p>{escape(candidate["status"])}</p>{media}<p>{review_text}</p></article>')
            rows.append(row)
    report = {'checked_at': stamp(), 'candidates': rows,
              'estimated_total_rmb_from_usage': round(sum(r.get('estimated_rmb_from_usage', 0) for r in rows), 4),
              'note': '费用按实际返回tokens折算，最终看账单；动作与声音待人工审阅，未作为成片定稿。'}
    write_json(review / '实际生成记录.json', report)
    reel = RUN / '试片连看/F11_五镜试片_39秒.mp4'
    reel_html = ('<h2>五镜完整连看</h2><video controls preload="metadata" src="'
                 + quote(reel.relative_to(RUN).as_posix()) + '"></video>') if reel.is_file() else ''
    html = ('<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>F11 首轮视频试片</title><style>'
            'body{margin:0;background:#15171b;color:#eee;font:16px/1.6 "Microsoft YaHei",sans-serif}'
            'main{max-width:1400px;margin:auto;padding:36px}h1{font-size:30px}h2{font-size:20px}'
            '.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:24px}'
            'article{background:#23262d;border-radius:12px;padding:20px}video{width:100%;border-radius:8px}'
            'small,p{color:#bac3ce}a{color:#b9dacb}</style><main><h1>《不用麻烦她》首轮视频试片</h1>'
            '<p>官方 API 实际生成候选。先看人物、手部、轮椅运动和接触关系；试片声音尚未统一。'
            '16镜入口台阶沿用当前首帧，数量与机构仍待统一。这些片段尚未作为成片定稿。</p>'
            f'<p>本轮按返回token用量折算约 {report["estimated_total_rmb_from_usage"]:.2f} 元，最终以账单为准。</p>'
            + reel_html + '<h2>逐镜查看与检查备注</h2><div class="grid">'
            + ''.join(cards) + '</div></main></html>')
    (RUN / '看试片.html').write_text(html, encoding='utf-8')
    print(json.dumps({'page': str(RUN / '看试片.html'), 'candidates': len(rows),
                      'downloaded': sum('file' in r for r in rows),
                      'estimated_rmb_from_usage': report['estimated_total_rmb_from_usage']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
