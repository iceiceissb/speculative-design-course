import React, { useEffect, useState } from "react";
import { ExternalLink, Maximize2, Monitor, Send } from "lucide-react";

export function PresentationControls({ session, latest, busy, onPresent }) {
  const view = session.presentation;
  const current =
    !view || view.kind === "blank"
      ? "留白，等待行动"
      : view.kind === "event"
        ? "正在展示事件"
        : "正在展示已确认的提示";
  return (
    <div className="presentation-controls">
      <div className="presentation-heading">
        <Monitor size={20} />
        <b>学生投屏</b>
        <a href={`/?classroom=${session.id}`} target="_blank" rel="noreferrer">
          打开投屏页 <ExternalLink size={15} />
        </a>
      </div>
      <p>{current}。新生成的提示会先留在操作端。</p>
      <div className="presentation-actions">
        <button
          className="button outline"
          disabled={busy}
          onClick={() => onPresent("event")}
        >
          投屏当前事件
        </button>
        <button
          className="text-button"
          disabled={busy || !view || view.kind === "blank"}
          onClick={() => onPresent("blank")}
        >
          暂时留白
        </button>
      </div>
      {latest && latest.level !== "L0" && (
        <button
          className="button primary publish-hint"
          disabled={
            busy || (view?.hint_id === latest.id && view?.kind === "hint")
          }
          onClick={() => onPresent("hint", latest.id)}
        >
          <Send size={16} />
          {view?.hint_id === latest.id && view?.kind === "hint"
            ? "这条提示已投屏"
            : "确认，把这条提示发到投屏"}
        </button>
      )}
      {latest?.level === "L0" && (
        <p className="helper">本轮选择自主探索，可以让投屏留白。</p>
      )}
    </div>
  );
}

export function Classroom({ id }) {
  const [doc, setDoc] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    let timer;
    async function load() {
      try {
        const response = await fetch(
          `/api/classroom/${encodeURIComponent(id)}`,
        );
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "无法读取活动");
        if (active) {
          setDoc(data);
          setError("");
        }
      } catch (e) {
        if (active) setError(e.message);
      }
      if (active) timer = setTimeout(load, 1800);
    }
    load();
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [id]);
  const view = doc?.presentation;
  const blank = !view || view.kind === "blank";
  return (
    <div className={`classroom-screen ${blank ? "is-blank" : ""}`}>
      <header>
        <div className="classroom-brand">
          <span className="brand-ring" />
          <b>场外</b>
          <span>把可能交给行动</span>
        </div>
        <button
          aria-label="全屏显示"
          onClick={() => {
            if (document.fullscreenElement)
              document.exitFullscreen?.().catch(() => {});
            else document.documentElement.requestFullscreen?.().catch(() => {});
          }}
        >
          <Maximize2 size={20} />
        </button>
      </header>
      <div className="classroom-content">
        <div className="classroom-eyebrow">
          {doc?.title || "课堂即兴"}
          {doc?.mode === "demo" && <span>手写演示</span>}
        </div>
        {error && (
          <p role="alert" className="classroom-error">
            连接中断：{error}。请检查操作端服务。
          </p>
        )}
        {!doc && !error ? (
          <h1>正在连接课堂…</h1>
        ) : blank ? (
          <>
            <div className="blank-orbit" />
            <h1>接下来，交给你们。</h1>
            <p className="classroom-message">
              用身体、空间和彼此，试出一种新的可能。
            </p>
          </>
        ) : (
          <>
            <p className="classroom-label">
              {view.kind === "hint" ? "给行动一个起点" : "新的情境"}
            </p>
            <h1>{view.event.title}</h1>
            <p className="classroom-event">{view.event.content}</p>
            {view.kind === "hint" && (
              <div className="classroom-hint">
                <span>可以试着…</span>
                <p>{view.hint.message}</p>
              </div>
            )}
            {view.event.fiction && (
              <p className="classroom-fiction">{view.event.fiction}</p>
            )}
          </>
        )}
      </div>
      <footer>
        <span>选择和行动，由你们决定。</span>
        {doc && (
          <details>
            <summary>本轮活动条件</summary>
            <p>{doc.constraints}</p>
          </details>
        )}
      </footer>
    </div>
  );
}
