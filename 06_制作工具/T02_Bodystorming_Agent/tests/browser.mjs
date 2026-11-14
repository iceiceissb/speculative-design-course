import { chromium } from "@playwright/test";
import { spawn } from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";

const root = process.cwd();
const qa = path.join(root, "qa");
await fs.mkdir(qa, { recursive: true });
const proc = spawn(
  "python",
  [
    "server.py",
    "--no-browser",
    "--port",
    "8780",
    "--data-dir",
    path.join(qa, "data"),
  ],
  { cwd: root, windowsHide: true, stdio: ["ignore", "pipe", "pipe"] },
);
let out = "";
proc.stdout.on("data", (b) => (out += b.toString()));
proc.stderr.on("data", (b) => (out += b.toString()));
let browser;
try {
  for (let i = 0; i < 100 && !out.includes("http://127.0.0.1:"); i++)
    await new Promise((r) => setTimeout(r, 100));
  const url = out.match(/http:\/\/127\.0\.0\.1:\d+/)?.[0];
  assert.ok(url, `Test server not started: ${out}`);
  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1536, height: 1024 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(url);
  await page
    .getByRole("heading", { name: "把课堂准备好，把即兴留给学生。" })
    .waitFor();
  await page.getByRole("button", { name: /太空建造/ }).click();
  await page.getByLabel("纸张", { exact: true }).check();
  await page.getByLabel("本轮表演时长", { exact: true }).selectOption("5");
  await page.getByLabel("补充一种材料").fill("布料");
  await page.getByRole("button", { name: "加入材料", exact: true }).click();
  assert.ok(
    (await page.locator(".activity-summary").innerText()).includes(
      "纸板、绳子、手电筒、纸张、布料",
    ),
  );
  await page
    .getByRole("button", { name: "保存为活动方案", exact: true })
    .click();
  await page
    .locator("#saved-plan option")
    .nth(1)
    .waitFor({ state: "attached" });
  const planId = await page
    .locator("#saved-plan option")
    .nth(1)
    .getAttribute("value");
  await page.getByRole("button", { name: /校园服务/ }).click();
  await page.locator("#saved-plan").selectOption(planId);
  assert.equal(await page.locator("#remaining").inputValue(), "5");
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => {
    window.scrollTo(0, 0);
    return new Promise((resolve) =>
      requestAnimationFrame(() => requestAnimationFrame(resolve)),
    );
  });
  await page.screenshot({ path: path.join(qa, "desktop.png"), fullPage: true });
  await page
    .getByRole("button", { name: "暂存到当前浏览器", exact: true })
    .click();
  await page.reload();
  assert.ok((await page.locator("#story").inputValue()).includes("火星"));
  await page
    .getByRole("button", { name: "准备完成，生成扰动", exact: true })
    .click();
  await page.locator(".event-row").first().waitFor();
  assert.equal(await page.locator(".event-row").count(), 5);
  assert.ok((await page.locator(".notice").textContent()).includes("手写演示"));
  await page.getByRole("button", { name: "选择这个事件" }).first().click();
  const projection = await context.newPage();
  await projection.goto(
    await page
      .getByRole("link", { name: "打开投屏页" })
      .getAttribute("href")
      .then((p) => url + p),
  );
  await projection
    .getByRole("heading", { name: "接下来，交给你们。" })
    .waitFor();
  await page.getByRole("button", { name: "投屏当前事件", exact: true }).click();
  await projection.locator(".classroom-event").waitFor();
  await page
    .getByRole("button", { name: "有人明确请求帮助", exact: true })
    .click();
  await page.locator("#support").selectOption("help");
  await page.getByRole("button", { name: "判断并提供支持" }).click();
  await page.locator(".level").waitFor();
  assert.equal(await page.locator(".level").innerText(), "L1");
  assert.equal(await page.locator("#feedback").inputValue(), "not_shown");
  assert.equal(await projection.locator(".classroom-hint").count(), 0);
  await page
    .getByRole("button", { name: "确认，把这条提示发到投屏", exact: true })
    .click();
  await projection.locator(".classroom-hint").waitFor();
  assert.equal(
    await projection.locator(".sidebar, .logs, #observation").count(),
    0,
  );
  await projection.screenshot({
    path: path.join(qa, "projection.png"),
    fullPage: true,
  });
  await page.locator("#feedback").selectOption("rejected");
  await page.locator("#support").selectOption("more");
  await page.getByRole("button", { name: "判断并提供支持" }).click();
  await page.waitForFunction(
    () => document.querySelector(".level")?.textContent === "L2",
  );
  await page.getByRole("button", { name: "暂时留白", exact: true }).click();
  await projection
    .getByRole("heading", { name: "接下来，交给你们。" })
    .waitFor();
  await page
    .getByRole("button", { name: "有人明确请求帮助", exact: true })
    .click();
  await page
    .locator("#observation")
    .fill("团队持续尝试新的连接方式，没有人求助。");
  await page.locator("#support").selectOption("exploring");
  await page.getByRole("button", { name: "判断并提供支持" }).click();
  await page.waitForFunction(
    () => document.querySelector(".level")?.textContent === "L0",
  );
  assert.ok(
    (await page.locator(".prompt-message").innerText()).includes(
      "暂不追加提示",
    ),
  );
  const downloaded = page.waitForEvent("download");
  await page.getByRole("button", { name: "导出给学姐看的记录" }).click();
  const file = await downloaded;
  await file.saveAs(path.join(qa, "export.md"));
  const exported = await fs.readFile(path.join(qa, "export.md"), "utf8");
  assert.ok(exported.includes("手写演示，非模型生成"));
  assert.ok(exported.includes("rejected"));
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: path.join(qa, "guidance.png"),
    fullPage: true,
  });
  await page.getByRole("button", { name: "重新选择事件" }).click();
  await page.getByRole("button", { name: "选择这个事件" }).nth(1).click();
  assert.equal(await page.locator(".level").count(), 0);
  assert.equal(await page.locator("#observation").inputValue(), "");
  await page.getByRole("button", { name: "工作流", exact: true }).click();
  assert.equal(await page.locator(".node-list button").count(), 10);
  await page.getByRole("button", { name: /事件生成/ }).click();
  assert.ok(
    (await page.locator(".node-inspector pre").innerText()).includes("JSON"),
  );
  await page.getByRole("button", { name: "知识资料", exact: true }).click();
  const docTitle = "测试教学资料-" + Date.now();
  await page.locator("#doc-title").fill(docTitle);
  await page.locator("#doc-source").fill("浏览器测试，不是正式研究来源");
  await page
    .locator("#doc-body")
    .fill("身体即兴可以使用纸板、绳子和空间关系表达资源变化。");
  await page.getByRole("button", { name: "加入资料库" }).click();
  await page.getByText(docTitle, { exact: true }).waitFor();
  await page.getByRole("button", { name: "运行记录", exact: true }).click();
  await page.locator(".session-row").first().waitFor();
  assert.ok((await page.locator(".session-row").count()) > 0);
  await page.locator(".session-row").first().click();
  assert.ok(
    (await page.locator(".selected-event h2").innerText()).includes("动作交流"),
  );
  await page.getByRole("button", { name: "准备活动", exact: true }).click();
  await page.getByRole("button", { name: /太空建造/ }).click();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => {
    window.scrollTo(0, 0);
    return new Promise((resolve) =>
      requestAnimationFrame(() => requestAnimationFrame(resolve)),
    );
  });
  await page.screenshot({ path: path.join(qa, "mobile.png"), fullPage: true });
  assert.equal(
    await page.evaluate(
      () => document.documentElement.scrollWidth > innerWidth,
    ),
    false,
    "mobile overflow",
  );
  await page.getByRole("button", { name: "模型设置", exact: true }).click();
  assert.equal(await page.locator("#key").getAttribute("type"), "password");
  await page.setViewportSize({ width: 1536, height: 1024 });
  assert.deepEqual(errors, []);
  console.log(
    JSON.stringify(
      {
        ok: true,
        checks: 22,
        viewport: "1536x1024 + 390x844",
        consoleErrors: errors,
        qa,
      },
      null,
      2,
    ),
  );
} finally {
  if (browser) await browser.close();
  proc.kill();
}
