import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import {
  FilePlus2,
  Clock3,
  Workflow,
  BookOpen,
  Settings2,
  Laptop,
  Play,
  ArrowRight,
  FileText,
  Search,
  Sparkles,
  MousePointer2,
  ListChecks,
  UserRound,
  UsersRound,
  Info,
  Download,
  ChevronLeft,
  Check,
  LoaderCircle,
  Camera,
  Upload,
  ChevronDown,
  ChevronRight,
  X,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";
import "./styles.css";

const SAMPLE = {
  title: "火星基地 · 临时休息空间",
  story:
    "三位同学在火星上，利用纸板、绳子和手电筒，合作搭建一个临时的休息空间。\n这是一项即兴的建造任务，他们不知道火星的环境是否安全。\n需要在有限的材料和时间内，讨论、分工并尝试搭建出一个可以躲避风沙、并让彼此感到安心的空间。\n故事中的设备可通过动作象征性表达，现场没有真实的航天设备。",
  constraints:
    "只能使用纸板、绳子和手电筒三种材料。\n全程站立完成，不能使用桌椅等现有教室设施。\n3 分钟内完成，并在结束后用 1 分钟说明设计思路。",
  participants: "3",
  remaining: "3",
};
const NAV = [
  ["new", "新建演练", FilePlus2],
  ["history", "运行记录", Clock3],
  ["workflow", "工作流", Workflow],
  ["knowledge", "知识资料", BookOpen],
  ["settings", "模型设置", Settings2],
];
const STATES = [
  ["exploring", "正在自主探索"],
  ["uncertain", "不确定是否卡住"],
  ["help", "需要一点提示"],
  ["more", "需要更多方向"],
  ["example", "需要一个动作起点"],
];
const FEEDBACK = {
  offered: "尚未反馈",
  adopted: "采纳或修改",
  rejected: "已拒绝",
  not_shown: "尚未展示",
};
const INITIAL = { ...SAMPLE, title: "", story: "", constraints: "" };

async function api(path, body) {
  const res = await fetch(
    "/api" + path,
    body === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        },
  );
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "请求未完成");
  return data;
}
function download(data, name, type = "application/json") {
  const url = URL.createObjectURL(
    new Blob(
      [typeof data === "string" ? data : JSON.stringify(data, null, 2)],
      { type },
    ),
  );
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function Button({
  children,
  busy,
  disabled,
  variant = "primary",
  className = "",
  ...props
}) {
  return (
    <button
      className={`button ${variant} ${className}`}
      disabled={busy || disabled}
      {...props}
    >
      {busy && <LoaderCircle className="spin" size={17} />} {children}
    </button>
  );
}
function Notice({ children, error = false, onClose }) {
  return (
    <div
      role={error ? "alert" : "status"}
      className={`notice ${error ? "error" : ""}`}
    >
      <AlertCircle size={17} />
      <span>{children}</span>
      {onClose && (
        <button aria-label="关闭消息" className="icon-button" onClick={onClose}>
          <X size={16} />
        </button>
      )}
    </div>
  );
}
function Stepper({ step }) {
  return (
    <div className="stepper">
      {["编写情境", "选择扰动", "现场引导"].map((t, i) => (
        <React.Fragment key={t}>
          <div
            className={`step ${step === i + 1 ? "current" : ""} ${step > i + 1 ? "passed" : ""}`}
          >
            <span>
              {step > i + 1 ? (
                <Check size={22} />
              ) : (
                String(i + 1).padStart(2, "0")
              )}
            </span>
            <b>{t}</b>
          </div>
          {i < 2 && <div className="step-line" />}
        </React.Fragment>
      ))}
    </div>
  );
}
function SideContext() {
  return (
    <aside className="context-panel">
      <h2>这次，我们如何介入？</h2>
      <p>AI 在表演圈外提供扰动，选择和行动留给你。</p>
      <div className="principles">
        <div>
          <UserRound />
          <section>
            <h3>身体与空间</h3>
            <p>改变身体状态、空间条件或感官环境，激发表演与行动的新可能。</p>
          </section>
        </div>
        <div>
          <FileText />
          <section>
            <h3>角色与叙事</h3>
            <p>引入新的身份、角色关系或情节线索，拓展故事的走向。</p>
          </section>
        </div>
        <div>
          <UsersRound />
          <section>
            <h3>即兴与协作</h3>
            <p>制造不确定性，促进互动与协商，观察集体的创造过程。</p>
          </section>
        </div>
      </div>
      <h3>工作流程</h3>
      <div className="mini-flow">
        {[
          [FileText, "剧情提炼"],
          [Search, "资料检索"],
          [Sparkles, "事件生成"],
          [MousePointer2, "人工选择"],
          [ListChecks, "分级提示"],
          [FileText, "记录反思"],
        ].map(([Icon, t], i) => (
          <React.Fragment key={t}>
            <div>
              <span>
                <Icon size={19} />
              </span>
              <small>{t}</small>
            </div>
            {i < 5 && <ArrowRight className="flow-arrow" size={13} />}
          </React.Fragment>
        ))}
      </div>
    </aside>
  );
}
function ScenarioForm({ form, setForm, busy, onGenerate, onDraft, onSample }) {
  return (
    <div className="form-grid">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onGenerate();
        }}
        className="scenario-form"
      >
        <div className="field-title">
          <label htmlFor="story">你的情境</label>
          <button
            type="button"
            className="text-button"
            onClick={onSample}
            disabled={busy}
          >
            加载示例
          </button>
        </div>
        <textarea
          id="story"
          placeholder="描述你们的角色、目标，以及正在发生的事情……"
          value={form.story}
          onChange={(e) => setForm({ ...form, story: e.target.value })}
          required
          disabled={busy}
        />
        <label htmlFor="constraints">课堂约束</label>
        <textarea
          id="constraints"
          className="constraints"
          placeholder="有哪些道具、空间和时间限制？哪些条件不能改变？"
          value={form.constraints}
          onChange={(e) => setForm({ ...form, constraints: e.target.value })}
          required
          disabled={busy}
        />
        <div className="form-row">
          <div>
            <label htmlFor="participants">人数</label>
            <select
              id="participants"
              value={form.participants}
              onChange={(e) =>
                setForm({ ...form, participants: e.target.value })
              }
              disabled={busy}
            >
              {[2, 3, 4, 5, 6, 8, 10].map((n) => (
                <option key={n} value={String(n)}>
                  {n} 人
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="remaining">剩余时间</label>
            <select
              id="remaining"
              value={form.remaining}
              onChange={(e) => setForm({ ...form, remaining: e.target.value })}
              disabled={busy}
            >
              {[1, 2, 3, 5, 10, 15].map((n) => (
                <option key={n} value={String(n)}>
                  {n} 分钟
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="actions">
          <Button busy={busy} type="submit">
            {busy ? "正在运行节点…" : "生成 5 个突发事件"}{" "}
            {!busy && <ArrowRight size={19} />}
          </Button>
          <Button
            variant="outline"
            type="button"
            onClick={onDraft}
            disabled={busy}
          >
            保存草稿
          </Button>
        </div>
      </form>
      <SideContext />
    </div>
  );
}
function Events({ session, busy, onSelect, onBack }) {
  return (
    <div className="events-page">
      <div className="section-intro">
        <div>
          <h2>让情境转向另一个可能。</h2>
          <p>选择一个扰动，如何回应由你们决定。</p>
        </div>
        <button className="text-button" onClick={onBack} disabled={busy}>
          <ChevronLeft size={16} />
          修改情境
        </button>
      </div>
      {session.mode === "demo" && (
        <Notice>
          这里展示的是手写演示事件，用于查看操作流程；它们不是模型根据剧本生成的结果。
        </Notice>
      )}
      <div className="event-list">
        {session.events.map((event, i) => (
          <article key={event.id} className="event-row">
            <div className="event-number">{String(i + 1).padStart(2, "0")}</div>
            <div className="event-body">
              <div className="event-title">
                <h3>{event.title}</h3>
                <span>{event.type}</span>
              </div>
              <p>{event.content}</p>
              <div className="body-hint">
                <UserRound size={15} />
                <span>{event.body_hint}</span>
              </div>
              <small>{event.fiction}</small>
            </div>
            <Button
              variant="outline"
              disabled={busy}
              onClick={() => onSelect(event.id)}
            >
              选择这个事件 <ArrowRight size={16} />
            </Button>
          </article>
        ))}
      </div>
      <details className="details">
        <summary>查看剧情提炼结果</summary>
        <pre>{JSON.stringify(session.summary, null, 2)}</pre>
      </details>
    </div>
  );
}
function Guidance({
  session,
  busy,
  onGuide,
  onFeedback,
  onBack,
  onExport,
  run,
}) {
  const [observation, setObservation] = useState(session.observation || "");
  const [state, setState] = useState("help");
  const [photo, setPhoto] = useState(null);
  const [vision, setVision] = useState(null);
  const latest = session.hints.at(-1);
  async function readPhoto(file) {
    if (!file) return;
    if (file.size > 6 * 1024 * 1024) throw new Error("照片需小于 6MB。");
    if (!["image/png", "image/jpeg", "image/webp"].includes(file.type))
      throw new Error("请使用 PNG、JPEG 或 WebP。");
    const value = await new Promise((resolve, reject) => {
      const r = new FileReader();
      r.onload = () => resolve(r.result);
      r.onerror = reject;
      r.readAsDataURL(file);
    });
    setPhoto(value);
    setVision(null);
  }
  return (
    <div className="guidance-grid">
      <div>
        <div className="selected-event">
          <span>当前扰动 · {session.selected_event.id}</span>
          <h2>{session.selected_event.title}</h2>
          <p>{session.selected_event.content}</p>
          <button className="text-button" disabled={busy} onClick={onBack}>
            重新选择事件
          </button>
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onGuide(observation, state);
          }}
        >
          <div className="field-title">
            <label htmlFor="observation">现场发生了什么？</label>
            <button
              type="button"
              className="text-button"
              disabled={busy}
              onClick={() =>
                setObservation(
                  "团队停下约40秒，重复讨论恢复原先的电力。刚有人明确请求一点提示，之前的备用电池方案已被拒绝。",
                )
              }
            >
              填入求助示例
            </button>
          </div>
          <textarea
            id="observation"
            placeholder="输入你观察到的动作与对话，也可以粘贴已有的语音转写。"
            value={observation}
            onChange={(e) => setObservation(e.target.value)}
            required
            disabled={busy}
          />
          <label htmlFor="support">现在需要怎样的支持？</label>
          <select
            id="support"
            value={state}
            onChange={(e) => setState(e.target.value)}
            disabled={busy}
          >
            {STATES.map(([v, t]) => (
              <option key={v} value={v}>
                {t}
              </option>
            ))}
          </select>
          <p className="helper">
            由你确认现场状态。沉默和静止也可能意味着思考。
          </p>
          <div className="actions">
            <Button busy={busy} type="submit">
              判断并提供支持 <ArrowRight size={18} />
            </Button>
          </div>
        </form>
        <details className="details">
          <summary>
            <Camera size={16} />
            用一张照片补充观察
          </summary>
          <p className="helper">
            需要所配置的模型支持视觉。描述结果须先确认；单张照片无法判断沉默时长或情绪。
          </p>
          <input
            aria-label="选择现场照片"
            type="file"
            accept="image/png,image/jpeg,image/webp"
            onChange={(e) => run(() => readPhoto(e.target.files[0]))}
            disabled={busy}
          />
          {photo && (
            <img className="photo-preview" src={photo} alt="待确认的现场快照" />
          )}
          <Button
            variant="outline"
            disabled={!photo || busy || session.mode === "demo"}
            onClick={() =>
              run(async () =>
                setVision(
                  await api("/observe", { image: photo, note: observation }),
                ),
              )
            }
          >
            分析这张照片
          </Button>
          {session.mode === "demo" && (
            <p className="helper">演示模式下不调用视觉模型。</p>
          )}
          {vision && (
            <div className="vision-output">
              <p>{vision.observation}</p>
              <small>{vision.uncertainty}</small>
              <button
                className="text-button"
                onClick={() => {
                  setObservation(
                    [
                      observation,
                      vision.observation,
                      "不确定之处：" + vision.uncertainty,
                    ]
                      .filter(Boolean)
                      .join("\n"),
                  );
                  setVision(null);
                }}
              >
                确认并加入观察
              </button>
            </div>
          )}
        </details>
      </div>
      <aside className="guidance-result">
        <div className="section-intro">
          <h2>留一点空间给行动。</h2>
          {latest && (
            <span className="level">
              {latest.level === "confirm" ? "待确认" : latest.level}
            </span>
          )}
        </div>
        {!latest ? (
          <div className="empty-guidance">
            <UserRound size={45} strokeWidth={1} />
            <h3>从现场的一句话开始</h3>
            <p>
              我们会根据当前事件与观察，
              <br />
              选择最少、但足够的支持。
            </p>
          </div>
        ) : (
          <>
            <p className="prompt-message">{latest.message}</p>
            <div className="guidance-evidence">
              <h3>依据</h3>
              <p>{latest.basis}</p>
              <h3>接下来可以观察</h3>
              <p>{latest.next_observation}</p>
              <small>{latest.knowledge_status}</small>
            </div>
            <label className="feedback-label" htmlFor="feedback">
              你们怎样使用这条提示？
            </label>
            <select
              id="feedback"
              value={latest.feedback}
              onChange={(e) => onFeedback(latest.id, e.target.value)}
              disabled={busy}
            >
              {Object.entries(FEEDBACK).map(([v, t]) => (
                <option key={v} value={v}>
                  {t}
                </option>
              ))}
            </select>
            <details className="details">
              <summary>
                查看本轮检索资料（{latest.evidence?.length || 0}）
              </summary>
              {latest.evidence?.length ? (
                latest.evidence.map((e) => (
                  <div key={e.id} className="citation">
                    <b>{e.title}</b>
                    <p>{e.text}</p>
                    <small>{e.source || "用户导入，未填来源"}</small>
                  </div>
                ))
              ) : (
                <p>没有匹配的资料，不代表领域事实已得到核验。</p>
              )}
            </details>
          </>
        )}
        {session.hints.length > 1 && (
          <details className="details">
            <summary>之前的提示（{session.hints.length - 1}）</summary>
            {session.hints
              .slice(0, -1)
              .reverse()
              .map((h) => (
                <div key={h.id} className="history-hint">
                  <small>
                    {h.level} · {FEEDBACK[h.feedback]}
                  </small>
                  <p>{h.message}</p>
                </div>
              ))}
          </details>
        )}
        <div className="export-actions">
          <button className="text-button" onClick={() => onExport("md")}>
            <Download size={16} />
            导出给学姐看的记录
          </button>
          <button className="text-button" onClick={() => onExport("json")}>
            JSON
          </button>
        </div>
      </aside>
    </div>
  );
}
function Logs({ session }) {
  return (
    <details className="details logs">
      <summary>
        <Workflow size={16} />
        节点运行记录（{session.logs.length}）
      </summary>
      <div className="log-list">
        {session.logs.map((log) => (
          <details key={log.id}>
            <summary>
              <span className={`log-dot ${log.status}`} />
              <b>{log.name}</b>
              <span>{log.kind}</span>
              <small>
                {log.status === "done"
                  ? "完成"
                  : log.status === "error"
                    ? "失败"
                    : "运行中"}{" "}
                · {log.duration_ms ?? "…"}ms
              </small>
            </summary>
            <div className="log-detail">
              <b>输入</b>
              <pre>{JSON.stringify(log.inputs, null, 2)}</pre>
              <b>{log.error ? "错误" : "输出"}</b>
              <pre>{log.error || JSON.stringify(log.output, null, 2)}</pre>
            </div>
          </details>
        ))}
      </div>
    </details>
  );
}
function WorkflowPage({ nodes }) {
  const [selected, setSelected] = useState(0);
  const n = nodes[selected];
  return (
    <>
      <h1>每一步，都看得清楚。</h1>
      <p className="subtitle">
        节点已连接。模型、检索、程序规则和人的决定各有边界。
      </p>
      <div className="workflow-layout">
        <div className="node-list">
          {nodes.map((n, i) => (
            <button
              key={n.id}
              className={selected === i ? "active" : ""}
              onClick={() => setSelected(i)}
            >
              <span>{String(i + 1).padStart(2, "0")}</span>
              <div>
                <b>{n.name}</b>
                <small>{n.kind}</small>
              </div>
              <ChevronRight size={17} />
            </button>
          ))}
        </div>
        {n && (
          <section className="node-inspector">
            <span className="muted">{n.kind}</span>
            <h2>{n.name}</h2>
            <p>{n.description}</p>
            <h3>{n.prompt_text ? "当前节点提示词" : "运行说明"}</h3>
            <pre>{n.prompt_text || n.description}</pre>
            <p className="helper">
              运行输入与输出会保存在对应演练的节点记录中。
            </p>
          </section>
        )}
      </div>
    </>
  );
}
function KnowledgePage({ docs, onAdd, busy }) {
  const [title, setTitle] = useState("");
  const [source, setSource] = useState("");
  const [text, setText] = useState("");
  async function readFile(e) {
    const file = e.target.files[0];
    if (file) {
      setText(await file.text());
      if (!title) setTitle(file.name);
    }
  }
  async function submit(e) {
    e.preventDefault();
    if (await onAdd({ title, source, text })) {
      setTitle("");
      setSource("");
      setText("");
    }
  }
  return (
    <>
      <h1>给每个依据，一个出处。</h1>
      <p className="subtitle">
        导入你核对过的文本资料。系统按词句检索，不联网抓取，也不把检索当作事实验证。
      </p>
      <div className="knowledge-grid">
        <form onSubmit={submit}>
          <label htmlFor="doc-title">资料标题</label>
          <input
            id="doc-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <label htmlFor="doc-source">来源或链接</label>
          <input
            id="doc-source"
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="作者、页码，或原始链接"
          />
          <label htmlFor="doc-body">资料正文</label>
          <textarea
            id="doc-body"
            value={text}
            onChange={(e) => setText(e.target.value)}
            required
            placeholder="粘贴原文或核对后的笔记，也可以读取 TXT / Markdown 文件。"
          />
          <input
            aria-label="读取知识资料文件"
            type="file"
            accept=".txt,.md"
            onChange={readFile}
          />
          <div className="actions">
            <Button type="submit" busy={busy}>
              <BookOpen size={17} />
              加入资料库
            </Button>
          </div>
        </form>
        <div className="documents">
          <h2>本地资料 · {docs.length}</h2>
          {docs.length ? (
            docs.map((d) => (
              <details key={d.id} className="document">
                <summary>
                  <FileText size={20} />
                  <b>{d.title}</b>
                </summary>
                <small>{d.source || "未提供来源"}</small>
                <p>{d.text}</p>
              </details>
            ))
          ) : (
            <div className="empty-state">
              <BookOpen size={34} strokeWidth={1} />
              <p>
                还没有导入资料。
                <br />
                未匹配资料时，运行记录会如实显示为空。
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
function SettingsPage({ config, onSave, onTest, busy }) {
  const [form, setForm] = useState({ ...config, api_key: "" });
  useEffect(() => setForm((c) => ({ ...c, ...config, api_key: "" })), [config]);
  return (
    <>
      <h1>接入你选择的模型。</h1>
      <p className="subtitle">
        支持兼容 Chat Completions
        的模型服务。密钥只交给本机后端，关闭服务后需重新填写。
      </p>
      <form
        className="settings-form"
        onSubmit={(e) => {
          e.preventDefault();
          onSave(form);
        }}
      >
        <label htmlFor="base">API Base URL</label>
        <input
          id="base"
          value={form.base_url || ""}
          onChange={(e) => setForm({ ...form, base_url: e.target.value })}
          placeholder="https://api.deepseek.com"
          required
        />
        <label htmlFor="model">模型名称 / 接入点 ID</label>
        <input
          id="model"
          value={form.model || ""}
          onChange={(e) => setForm({ ...form, model: e.target.value })}
          required
        />
        <label htmlFor="key">API 密钥</label>
        <input
          id="key"
          type="password"
          autoComplete="off"
          value={form.api_key}
          onChange={(e) => setForm({ ...form, api_key: e.target.value })}
          placeholder={
            config.configured
              ? "已在本机内存中配置；留空保留当前密钥"
              : "在本机填写，不用发送给聊天助手"
          }
        />
        <label className="checkbox">
          <input
            type="checkbox"
            checked={!!form.json_mode}
            onChange={(e) => setForm({ ...form, json_mode: e.target.checked })}
          />
          请求 JSON 输出模式
        </label>
        <p className="helper">
          模型提示词始终要求 JSON。服务商不支持 response_format
          时，可取消此选项。
        </p>
        <div className="actions">
          <Button busy={busy} type="submit">
            保存本次配置
          </Button>
          <Button
            disabled={!config.configured || busy}
            variant="outline"
            type="button"
            onClick={onTest}
          >
            测试真实连接
          </Button>
        </div>
        <p className="helper">
          “已配置”仅表示本机持有密钥；测试连接会发起一次真实请求，可能产生服务商费用。只有测试成功才说明这次连接可用。
        </p>
        <button
          type="button"
          className="text-button"
          onClick={() => onSave({ ...form, api_key: "", clear_key: true })}
          disabled={busy || !config.configured}
        >
          清除内存中的密钥
        </button>
      </form>
      <div className="settings-note">
        <h3>后续接入视觉</h3>
        <p>
          现场引导页支持上传照片，经你确认后加入观察。请配置支持 image_url
          的视觉模型。普通文本模型不一定支持图片。
        </p>
        <h3>语音与检索</h3>
        <p>
          当前可粘贴已有语音转写；未实现实时麦克风识别。本地知识资料支持实际检索，尚未接入联网搜索。
        </p>
      </div>
    </>
  );
}
function App() {
  const [page, setPage] = useState("new");
  const [mode, setMode] = useState("demo");
  const [form, setForm] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("outactor_draft")) || INITIAL;
    } catch {
      return INITIAL;
    }
  });
  const [session, setSession] = useState(null);
  const [step, setStep] = useState(1);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [config, setConfig] = useState({ configured: false });
  const [nodes, setNodes] = useState([]);
  const [docs, setDocs] = useState([]);
  const [history, setHistory] = useState([]);
  useEffect(() => {
    Promise.all([
      api("/config"),
      api("/workflow"),
      api("/knowledge"),
      api("/sessions"),
    ])
      .then(([c, n, d, h]) => {
        setConfig(c);
        setNodes(n);
        setDocs(d);
        setHistory(h);
      })
      .catch((e) => setError(e.message));
  }, []);
  async function run(fn) {
    if (busy) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await fn();
      return true;
    } catch (e) {
      setError(e.message);
      return false;
    } finally {
      setBusy(false);
    }
  }
  function navigate(p) {
    if (!busy) {
      setPage(p);
      setError("");
      setMessage("");
      if (p === "history")
        api("/sessions")
          .then(setHistory)
          .catch((e) => setError(e.message));
    }
  }
  function newSession() {
    setSession(null);
    setStep(1);
    setPage("new");
    setError("");
    setMessage("");
  }
  function editForm(next) {
    setForm(next);
    if (session) {
      setSession(null);
      setStep(1);
    }
  }
  async function generate() {
    await run(async () => {
      if (!form.story.trim() || !form.constraints.trim())
        throw new Error("请先填写情境和课堂约束。");
      if (mode === "live" && !config.configured) {
        setPage("settings");
        throw new Error(
          "真实模型模式需要先配置 API。也可以切换到明确标记的演示模式。",
        );
      }
      const d = await api("/sessions", {
        ...form,
        title: form.title || form.story.split("\n")[0].slice(0, 24) || "未命名演练",
        mode,
      });
      setSession(d);
      try {
        const result = await api(`/sessions/${d.id}/generate`, {});
        setSession(result);
        setStep(2);
      } catch (e) {
        setSession(await api(`/sessions/${d.id}`));
        throw e;
      }
    });
  }
  async function select(id) {
    await run(async () => {
      setSession(await api(`/sessions/${session.id}/select`, { event_id: id }));
      setStep(3);
    });
  }
  async function guide(observation, state) {
    await run(async () => {
      try {
        setSession(
          await api(`/sessions/${session.id}/guide`, { observation, state }),
        );
      } catch (e) {
        setSession(await api(`/sessions/${session.id}`));
        throw e;
      }
    });
  }
  async function feedback(hint_id, feedback) {
    await run(async () =>
      setSession(
        await api(`/sessions/${session.id}/feedback`, { hint_id, feedback }),
      ),
    );
  }
  async function exportRecord(format) {
    await run(async () => {
      const res = await fetch(
        `/api/sessions/${session.id}/export?format=${format}`,
      );
      if (!res.ok) throw new Error("导出失败");
      const text = await res.text();
      download(
        text,
        `场外_演练记录_${session.id.slice(0, 6)}.${format}`,
        format === "md" ? "text/markdown" : "application/json",
      );
    });
  }
  const crumbs = Object.fromEntries(NAV.map(([k, t]) => [k, t]));
  return (
    <div className="app">
      <aside className="sidebar">
        <button
          className="brand"
          onClick={newSession}
          aria-label="场外工作台"
        >
          <span className="brand-ring" />
          <span>
            <b>场外</b>
            <small>OUT-ACTOR</small>
          </span>
        </button>
        <nav>
          {NAV.map(([key, text, Icon]) => (
            <button
              key={key}
              className={page === key ? "active" : ""}
              disabled={busy}
              onClick={() => key === "new" ? newSession() : navigate(key)}
            >
              <Icon size={24} strokeWidth={1.6} />
              <span>{text}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <Laptop size={21} />
          <span>本地工作台</span>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div>
            工作台 <span>/</span> {crumbs[page]}
          </div>
          <div className="top-actions">
            <button
              className="mode-button"
              disabled={busy}
              onClick={() => {
                setMode(mode === "demo" ? "live" : "demo");
                newSession();
              }}
            >
              <Play size={16} />
              {mode === "demo" ? "演示模式" : "真实模型"}
            </button>
            <button
              className="connection"
              disabled={busy}
              onClick={() => navigate("settings")}
            >
              <i className={config.configured ? "configured" : ""} />
              {config.configured ? "API 已配置" : "API 未连接"}
            </button>
          </div>
        </header>
        <main>
          {error && (
            <Notice error onClose={() => setError("")}>
              {error}
            </Notice>
          )}
          {message && <Notice onClose={() => setMessage("")}>{message}</Notice>}
          {page === "new" && (
            <>
              <h1>给即兴，一个新的可能。</h1>
              <p className="subtitle">从一个情境开始，让行动生长出新的设计。</p>
              <Stepper step={step} />
              {step === 1 && (
                <ScenarioForm
                  form={form}
                  setForm={editForm}
                  busy={busy}
                  onGenerate={generate}
                  onDraft={() => {
                    localStorage.setItem(
                      "outactor_draft",
                      JSON.stringify(form),
                    );
                    setMessage("草稿已保存在当前浏览器。");
                  }}
                  onSample={() => editForm({ ...SAMPLE })}
                />
              )}
              {step === 2 && session && (
                <Events
                  session={session}
                  busy={busy}
                  onSelect={select}
                  onBack={() => {
                    setStep(1);
                    setSession(null);
                  }}
                />
              )}
              {step === 3 && session && (
                <Guidance
                  key={session.selected_event.id + session.id}
                  session={session}
                  busy={busy}
                  onGuide={guide}
                  onFeedback={feedback}
                  onBack={() => setStep(2)}
                  onExport={exportRecord}
                  run={run}
                />
              )}
              {session && <Logs session={session} />}
              <footer>
                <Info size={17} />
                <span>
                  {mode === "demo"
                    ? "演示模式使用手写内容，可查看完整流程；真实生成请切换模型模式。"
                    : "真实模型模式：输出来自你配置的服务，规则节点会单独标记。"}
                </span>
              </footer>
            </>
          )}
          {page === "workflow" && <WorkflowPage nodes={nodes} />}
          {page === "knowledge" && (
            <KnowledgePage
              docs={docs}
              busy={busy}
              onAdd={async (data) =>
                run(async () => {
                  await api("/knowledge", data);
                  setDocs(await api("/knowledge"));
                  setMessage("资料已加入；下一次运行会实际检索。");
                })
              }
            />
          )}
          {page === "settings" && (
            <SettingsPage
              config={config}
              busy={busy}
              onSave={(data) =>
                run(async () => {
                  setConfig(await api("/config", data));
                  setMessage(
                    data.clear_key
                      ? "密钥已清除。"
                      : "本机配置已保存，尚未证明连接可用。",
                  );
                })
              }
              onTest={() =>
                run(async () => {
                  const r = await api("/config/test", {});
                  setMessage(r.message);
                })
              }
            />
          )}
          {page === "history" && (
            <>
              <div className="section-intro">
                <div>
                  <h1>把过程留下来。</h1>
                  <p className="subtitle">
                    继续演练，或查看每个节点的输入与输出。
                  </p>
                </div>
                <Button onClick={newSession}>
                  <FilePlus2 size={17} />
                  新建演练
                </Button>
              </div>
              {history.length ? (
                <div className="history-list">
                  {history.map((h) => (
                    <button
                      key={h.id}
                      className="session-row"
                      onClick={() =>
                        run(async () => {
                          const d = await api(`/sessions/${h.id}`);
                          setSession(d);
                          setForm({
                            title: d.title,
                            story: d.story,
                            constraints: d.constraints,
                            participants: d.participants,
                            remaining: d.remaining,
                          });
                          setMode(d.mode);
                          setStep(
                            d.selected_event ? 3 : d.events.length ? 2 : 1,
                          );
                          setPage("new");
                        })
                      }
                    >
                      <FileText size={23} />
                      <div>
                        <b>{h.title}</b>
                        <small>
                          {new Date(h.updated_at).toLocaleString("zh-CN")} ·{" "}
                          {h.mode === "demo" ? "演示" : "真实模型"} ·{" "}
                          {h.event_count} 个事件 / {h.hint_count} 条提示
                        </small>
                      </div>
                      <ChevronRight size={20} />
                    </button>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <Clock3 size={40} strokeWidth={1} />
                  <p>从一次新的演练开始。</p>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}
createRoot(document.getElementById("root")).render(<App />);
