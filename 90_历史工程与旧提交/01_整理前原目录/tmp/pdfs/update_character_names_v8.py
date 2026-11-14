from pathlib import Path

root=Path(r'D:/课/大四上/思辨设计/output/10月8日汇报_剧本重构')
for path in root.glob('*.md'):
    text=path.read_text(encoding='utf-8')
    for old,new in [('林遥','邱懿贞'),('陈禾','徐月禾'),('小满','秀秀')]:
        text=text.replace(old,new)
    text=text.replace('河边犹豫半拍','河边面对同时发生的动作，短暂不知先帮哪一件')
    text=text.replace('用于结尾，检验秀秀是否把尊重误学成停止主动','用于结尾，表现突发协作中的短暂忙乱，而非再次讲授自主权')
    text=text.replace('鱼咬钩，秀秀两手分别伸向竿和网 | 它对主动帮助出现新的犹豫','鱼咬钩，竿、鱼线与收纳物同时动起来 | 秀秀一时不知该先帮哪一件事')
    text=text.replace('结尾为何还会迟疑：秀秀从尊重反馈中产生了过度谨慎，邱懿贞继续给出生活里的具体反馈。','结尾为何会愣一下：鱼突然咬钩，两人同时行动，秀秀一时分不清先扶竿、处理鱼线还是拿网。这是突发场面的忙乱，不是权限限制、记忆故障或尊重意愿的再次考核。')
    text=text.replace('秀秀一只手朝鱼竿，另一只朝抄网。短短半拍，它没有选定。\n\n**秀秀**  \n这次——', '邱懿贞猛地抬竿，徐月禾起身接住竿身。鱼线一紧，旁边的饵盒也被衣角带歪。\n\n秀秀一只手刚伸向鱼竿，见徐月禾已经接住，又转向晃动的饵盒。它看一眼鱼线，再看两人，短短半拍不知道该先帮哪件事。\n\n**秀秀**  \n我先——')
    path.write_text(text,encoding='utf-8')
print('Updated current reconstruction documents; historical drafts unchanged.')
