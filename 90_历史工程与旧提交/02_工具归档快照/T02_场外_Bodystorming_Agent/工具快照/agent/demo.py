"""Explicitly labelled, hand-written fixtures. Never substitutes for a failed API call."""

EVENTS = [
    dict(id='E1', title='电力只在短暂窗口恢复', type='资源与节奏', content='故事中的供电变为间歇供应，原有任务无法连续进行。团队需要重新安排工作节奏。', body_hint='用手电明暗、动作停顿与恢复表现时间窗口。', fiction='课堂虚构扰动，未经领域核验。', evidence_ids=[]),
    dict(id='E2', title='角色之间只能用动作交流', type='协作与沟通', content='下一轮情境中，角色暂时无法使用语言沟通，但仍需要共同推进原来的目标。', body_hint='探索手势、队形和道具位置如何传递信息。', fiction='课堂虚构扰动，未经领域核验。', evidence_ids=[]),
    dict(id='E3', title='可使用的空间缩小一半', type='空间关系', content='故事中原来可用的区域临时受限，团队要在更小的空间重新组织活动。', body_hint='通过缩小站位、改变身体朝向表现新的空间边界。', fiction='课堂虚构扰动，未经领域核验。', evidence_ids=[]),
    dict(id='E4', title='一种材料开始改变形态', type='材料变化', content='故事里正在使用的一种材料逐渐变形，原先的组合方式需要重新考虑。', body_hint='通过纸板的象征性转向与身体姿态呈现变化，不实际损坏道具。', fiction='课堂虚构扰动，未经领域核验。', evidence_ids=[]),
    dict(id='E5', title='使用者提出了新的需求', type='目标与角色', content='故事中的使用者希望原来的设计同时容纳一位需要更多行动空间的人，团队要协商哪些条件可以改变。', body_hint='交换使用者与设计者角色，用移动和停留探索需求。', fiction='课堂虚构扰动，未经领域核验。', evidence_ids=[]),
]


def summary(payload):
    return dict(scene=payload['story'][:180], goal='以身体、道具和空间探索原故事中的设计选择',
                constraints=payload['constraints'], resources='以用户列出的实际道具为准', missing='演示为手写示例，不进行剧情识别')


def guidance(level, event, observation):
    hints = {'L0': '继续当前探索，暂不追加提示。',
             'L1': '如果暂时保留这个限制，你们手里尚未使用的道具能表达另一种关系吗？',
             'L2': '可以选一个方向继续：改变团队的动作时序，或重新分配角色和空间。由你们决定先试哪一个。',
             'L3': '先用一个动作标记当前限制，再让另一位成员用不同位置回应；只演出这个起点，后续由团队决定。',
             'confirm': '你们希望继续自主探索，还是需要一点提示？'}
    return dict(understanding=f"围绕「{event['title']}」继续原场景。", basis=observation,
                level=level, message=hints[level], next_observation='团队是否出现新的动作、角色协商或道具关系。',
                knowledge_status='手写演示内容；不是模型生成结果。', evidence_ids=[])

