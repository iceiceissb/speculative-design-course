import React, { useState } from "react";
import {
  ArrowRight,
  Check,
  ClipboardList,
  Package,
  UsersRound,
} from "lucide-react";

export const MATERIALS = [
  "纸板",
  "绳子",
  "手电筒",
  "纸张",
  "胶带",
  "椅子",
  "桌子",
  "手机",
  "仅用身体",
];
export const SPACES = {
  fixed: "在固定活动区域内完成，不跨组移动。",
  open: "可在教师指定的教室空地移动。",
  table: "在指定桌面及周边完成。",
};
const BASE = {
  version: 1,
  materials: ["纸板", "绳子", "手电筒"],
  space: "fixed",
  focus: "即兴与协作",
  rules: { only_materials: true, symbolic: true, standing: false },
  notes: "",
};
export const INITIAL_ACTIVITY = {
  title: "",
  story: "",
  participants: "3",
  remaining: "3",
  constraints: "",
  preset: "",
  activity_config: BASE,
};
export const PRESETS = [
  {
    id: "mars",
    title: "太空建造",
    caption: "用有限材料协作",
    name: "火星基地 · 临时休息空间",
    story:
      "你们是火星探索队，需要合作搭建一个临时休息空间，让大家躲避风沙并感到安心。请用身体和现场材料表演角色分工与搭建过程；故事中的设备用动作象征性表达。",
    materials: ["纸板", "绳子", "手电筒"],
    focus: "即兴与协作",
  },
  {
    id: "campus",
    title: "校园服务",
    caption: "交换角色与视角",
    name: "校园服务 · 雨天取餐",
    story:
      "突来的大雨打乱了校园取餐秩序。你们分别扮演学生、工作人员和送餐者，用身体行动演出取餐过程，并尝试一个让各方更方便的服务方式。",
    materials: ["纸张", "椅子"],
    focus: "角色与叙事",
  },
  {
    id: "space",
    title: "空间协作",
    caption: "从身体关系出发",
    name: "共享空间 · 临时避雨点",
    story:
      "一群互不相识的人来到同一个临时避雨点。空间有限，每个人对舒适和距离的需求不同。通过移动、姿态与协商，探索大家如何共同使用这个空间。",
    materials: ["仅用身体"],
    focus: "身体与空间",
  },
];

export function normalizeForm(fields) {
  if (!fields) return structuredClone(INITIAL_ACTIVITY);
  return {
    ...structuredClone(INITIAL_ACTIVITY),
    ...fields,
    activity_config: fields.activity_config
      ? {
          ...structuredClone(BASE),
          ...fields.activity_config,
          rules: { ...BASE.rules, ...fields.activity_config.rules },
        }
      : fields.story
        ? null
        : structuredClone(BASE),
  };
}

export function constraintLines(form) {
  const c = form.activity_config;
  if (!c) return (form.constraints || "").split("\n");
  return [
    `每组 ${form.participants} 人，本轮表演时长 ${form.remaining} 分钟。`,
    `现场材料：${c.materials.length ? c.materials.join("、") : "尚未选择"}。`,
    `空间条件：${SPACES[c.space]}`,
    `学习重点：${c.focus}。`,
    c.rules.only_materials && "只使用上述现场材料，不引入额外实物。",
    c.rules.symbolic &&
      "故事中的设备或环境通过身体动作和道具象征性表达，不要求真实实现。",
    c.rules.standing && "全程站立完成。",
    c.notes.trim() && `补充要求：${c.notes.trim()}`,
  ].filter(Boolean);
}

export function ActivityForm({
  form,
  setForm,
  busy,
  onGenerate,
  onDraft,
  plans,
  onSavePlan,
}) {
  const [custom, setCustom] = useState("");
  const c = form.activity_config;
  const change = (delta) => setForm({ ...form, ...delta });
  const config = (delta) => change({ activity_config: { ...c, ...delta } });
  function toggleMaterial(m) {
    const items = c.materials.includes(m)
      ? c.materials.filter((x) => x !== m)
      : m === "仅用身体"
        ? [m]
        : [...c.materials.filter((x) => x !== "仅用身体"), m];
    config({ materials: items });
  }
  function preset(p) {
    setForm({
      ...normalizeForm(),
      title: p.name,
      story: p.story,
      preset: p.id,
      activity_config: {
        ...structuredClone(BASE),
        materials: p.materials,
        focus: p.focus,
      },
    });
  }
  return (
    <div className="activity-grid">
      <form
        className="activity-form"
        onSubmit={(e) => {
          e.preventDefault();
          onGenerate();
        }}
      >
        <fieldset disabled={busy}>
          <div className="activity-section-heading">
            <span className="section-index">01</span>
            <div>
              <h2>选一个活动起点</h2>
              <p>先选任务，再按这间教室的实际条件调整。</p>
            </div>
          </div>
          {plans.length > 0 && (
            <div className="saved-plan">
              <label htmlFor="saved-plan">复用已存方案</label>
              <select
                id="saved-plan"
                value=""
                onChange={(e) => {
                  const p = plans.find((x) => x.id === e.target.value);
                  if (p) setForm(normalizeForm(p.fields));
                }}
              >
                <option value="">选择一份课前方案…</option>
                {plans.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.fields.title || p.fields.story.slice(0, 24)}
                  </option>
                ))}
              </select>
            </div>
          )}
          <div className="preset-options">
            {PRESETS.map((p) => (
              <button
                type="button"
                key={p.id}
                aria-pressed={form.preset === p.id}
                onClick={() => preset(p)}
              >
                <b>{p.title}</b>
                <small>{p.caption}</small>
              </button>
            ))}
            <button
              type="button"
              aria-pressed={form.preset === "custom"}
              onClick={() => change({ preset: "custom", title: "", story: "" })}
            >
              <b>自定任务</b>
              <small>从自己的课程出发</small>
            </button>
          </div>
          <label htmlFor="activity-title">活动名称</label>
          <input
            id="activity-title"
            value={form.title}
            onChange={(e) => change({ title: e.target.value })}
            placeholder="给这次活动起个名字（可选）"
            maxLength={100}
          />
          <label htmlFor="story">活动情境</label>
          <textarea
            id="story"
            value={form.story}
            onChange={(e) => change({ story: e.target.value })}
            required
            placeholder="谁在什么情境中，要一起完成什么任务？选择上方起点后可直接调整。"
          />
          <div className="activity-section-heading">
            <span className="section-index">02</span>
            <div>
              <h2>这间教室，有什么条件？</h2>
              <p>勾选即可，右侧会自动整理成活动条件。</p>
            </div>
          </div>
          {c ? (
            <>
              <div className="activity-three">
                <div>
                  <label htmlFor="participants">每组人数</label>
                  <select
                    id="participants"
                    value={form.participants}
                    onChange={(e) => change({ participants: e.target.value })}
                  >
                    {[1, 2, 3, 4, 5, 6, 8, 10, 20, 40].map((n) => (
                      <option key={n} value={String(n)}>
                        {n} 人
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="remaining">本轮表演时长</label>
                  <select
                    id="remaining"
                    value={form.remaining}
                    onChange={(e) => change({ remaining: e.target.value })}
                  >
                    {[1, 2, 3, 5, 10, 15, 20, 30, 45, 60].map((n) => (
                      <option key={n} value={String(n)}>
                        {n} 分钟
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="focus">学习重点</label>
                  <select
                    id="focus"
                    value={c.focus}
                    onChange={(e) => config({ focus: e.target.value })}
                  >
                    {["身体与空间", "角色与叙事", "即兴与协作"].map((f) => (
                      <option key={f}>{f}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="field-title">
                <h3 id="material-label">现场可用材料</h3>
                <small>可多选</small>
              </div>
              <div
                className="material-options"
                role="group"
                aria-labelledby="material-label"
              >
                {[...new Set([...MATERIALS, ...c.materials])].map((m) => (
                  <label
                    key={m}
                    className={c.materials.includes(m) ? "chosen" : ""}
                  >
                    <input
                      type="checkbox"
                      checked={c.materials.includes(m)}
                      onChange={() => toggleMaterial(m)}
                    />
                    <span>{m}</span>
                  </label>
                ))}
              </div>
              <div className="custom-material">
                <input
                  aria-label="补充一种材料"
                  value={custom}
                  onChange={(e) => setCustom(e.target.value)}
                  placeholder="还有别的材料？填一个名称"
                  maxLength={40}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      if (custom.trim() && !c.materials.includes(custom.trim()))
                        toggleMaterial(custom.trim());
                      setCustom("");
                    }
                  }}
                />
                <button
                  type="button"
                  className="text-button"
                  disabled={!custom.trim()}
                  onClick={() => {
                    if (!c.materials.includes(custom.trim()))
                      toggleMaterial(custom.trim());
                    setCustom("");
                  }}
                >
                  加入材料
                </button>
              </div>
              <label htmlFor="space">空间条件</label>
              <select
                id="space"
                value={c.space}
                onChange={(e) => config({ space: e.target.value })}
              >
                <option value="fixed">固定区域 · 不跨组移动</option>
                <option value="open">教室空地 · 可在指定范围移动</option>
                <option value="table">桌面与周边 · 小范围活动</option>
              </select>
              <div className="rule-options">
                {[
                  ["only_materials", "只使用勾选的材料"],
                  ["symbolic", "允许用动作象征故事中的设备与环境"],
                  ["standing", "全程站立完成"],
                ].map(([key, text]) => (
                  <label key={key}>
                    <input
                      type="checkbox"
                      checked={c.rules[key]}
                      onChange={(e) =>
                        config({
                          rules: { ...c.rules, [key]: e.target.checked },
                        })
                      }
                    />
                    <span>{text}</span>
                  </label>
                ))}
              </div>
              <details className="details">
                <summary>补充特殊要求（可选）</summary>
                <textarea
                  aria-label="补充特殊要求"
                  className="extra-notes"
                  value={c.notes}
                  maxLength={2000}
                  onChange={(e) => config({ notes: e.target.value })}
                  placeholder="例如：本轮不使用语言；结束后留 1 分钟反思。"
                />
              </details>
            </>
          ) : (
            <div className="legacy-conditions">
              <p>这份旧记录使用文字条件，已原样保留。</p>
              <textarea
                aria-label="旧版活动条件"
                value={form.constraints}
                onChange={(e) => change({ constraints: e.target.value })}
              />
              <button
                className="text-button"
                type="button"
                onClick={() =>
                  config({ ...structuredClone(BASE), notes: form.constraints })
                }
              >
                改用勾选配置，原条件放入补充要求
              </button>
            </div>
          )}
          <div className="actions">
            <button className="button primary" type="submit">
              {busy ? "正在运行节点…" : "准备完成，生成扰动"}
              <ArrowRight size={18} />
            </button>
            <button
              className="button outline"
              type="button"
              onClick={onSavePlan}
            >
              保存为活动方案
            </button>
          </div>
          <button
            className="text-button draft-button"
            type="button"
            onClick={onDraft}
          >
            暂存到当前浏览器
          </button>
        </fieldset>
      </form>
      <aside className="activity-summary">
        <div className="summary-head">
          <ClipboardList size={22} />
          <span>活动条件确认单</span>
          <small>随选择自动更新</small>
        </div>
        <h2>{form.title || "这一次的课堂即兴"}</h2>
        <p className="summary-lead">
          {form.story || "选好活动起点后，在这里确认这轮要做的事。"}
        </p>
        <div className="summary-stat">
          <span>
            <UsersRound size={18} />
            {form.participants} 人 / 组
          </span>
          <span>{form.remaining} 分钟 / 轮</span>
        </div>
        <div className="condition-list">
          {constraintLines(form)
            .slice(1)
            .map((line, i) => (
              <p key={i}>
                <Check size={16} />
                <span>{line}</span>
              </p>
            ))}
        </div>
        {c && !c.materials.length && (
          <p role="status" className="material-warning">
            请至少选择一种材料，或选择「仅用身体」。
          </p>
        )}
        <div className="role-note">
          <Package size={18} />
          <p>
            这些条件会进入事件生成和每轮引导，保存方案后，下次课可以直接复用。
          </p>
        </div>
        <div className="role-flow">
          <h3>谁在什么时候使用？</h3>
          <p>
            <b>老师 / 助教</b>
            <span>课前准备条件，课堂中把握节奏。</span>
          </p>
          <p>
            <b>观察组</b>
            <span>记录动作，确认是否需要 AI 介入。</span>
          </p>
          <p>
            <b>表演组</b>
            <span>选择扰动，在投屏上查看确认后的内容。</span>
          </p>
        </div>
      </aside>
    </div>
  );
}

export const QUICK_OBSERVATIONS = [
  "正在尝试新动作",
  "正在调整道具关系",
  "反复讨论同一方案",
  "有人明确请求帮助",
  "暂时沉默，原因未确认",
  "拒绝了上一条提示",
];
