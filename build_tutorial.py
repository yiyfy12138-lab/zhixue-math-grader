import base64
import pathlib
import markdown

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "TUTORIAL.md"
OUT = ROOT / "index.html"
IMAGE = ROOT / "images" / "panel-crop.png"
QR = ROOT / "images" / "alipay-qr.jpg"

body = markdown.markdown(
    SRC.read_text(encoding="utf-8"),
    extensions=["tables", "fenced_code", "toc", "sane_lists"],
)

# 把截图/收款码内嵌，方便只分享 index.html 一个文件
for path, needle in [
    (IMAGE, 'src="images/panel-crop.png"'),
    (QR, 'src="images/alipay-qr.jpg"'),
]:
    if path.exists():
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
        body = body.replace(needle, 'src="data:%s;base64,%s"' % (mime, data))

template = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>智学数学阅卷助手 · 使用教程</title>
<style>
  :root {
    --ink: #111827;
    --muted: #6b7280;
    --line: #e5e7eb;
    --blue: #2563eb;
    --blue-dark: #1d4ed8;
    --bg: #f8fafc;
    --card: #ffffff;
    --green: #047857;
    --amber: #92400e;
    --red: #991b1b;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0;
    color: var(--ink);
    background: var(--bg);
    font: 16px/1.75 -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  }
  a { color: var(--blue); text-decoration: none; }
  a:hover { text-decoration: underline; }
  .hero {
    background: linear-gradient(135deg, #0f172a, #1e3a8a 60%, #2563eb);
    color: #fff;
    padding: 52px 24px 44px;
  }
  .hero-inner { max-width: 1040px; margin: 0 auto; }
  .eyebrow { color: #bfdbfe; font-size: 13px; letter-spacing: .12em; text-transform: uppercase; }
  .hero h1 { margin: 10px 0 12px; font-size: 38px; line-height: 1.2; letter-spacing: -0.02em; }
  .hero p { margin: 0; color: #dbeafe; max-width: 780px; }
  .badges { margin-top: 18px; display: flex; flex-wrap: wrap; gap: 8px; }
  .badge {
    display: inline-block; padding: 4px 10px; border-radius: 999px;
    background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.2);
    color: #eff6ff; font-size: 12px;
  }
  .downloads { margin-top: 22px; display: flex; flex-wrap: wrap; gap: 10px; }
  .btn {
    display: inline-block; padding: 9px 16px; border-radius: 9px;
    background: #fff; color: #1e3a8a; font-weight: 700; font-size: 14px;
  }
  .btn:hover { text-decoration: none; background: #eff6ff; }
  .btn.ghost { background: transparent; border: 1px solid rgba(255,255,255,.45); color: #fff; }
  .btn.ghost:hover { background: rgba(255,255,255,.1); }
  .wrap { max-width: 1040px; margin: 0 auto; padding: 30px 24px 80px; }
  article {
    background: var(--card); border: 1px solid var(--line); border-radius: 16px;
    padding: 34px 42px; box-shadow: 0 10px 35px rgba(15,23,42,.06);
  }
  article > h1:first-child { display: none; }
  h1 { font-size: 30px; line-height: 1.3; margin: 36px 0 14px; }
  h2 {
    font-size: 24px; line-height: 1.35; margin: 42px 0 12px;
    padding-top: 18px; border-top: 1px solid var(--line);
  }
  h3 { font-size: 18px; margin: 26px 0 8px; }
  h4 { font-size: 16px; margin: 20px 0 6px; }
  p { margin: 10px 0; }
  ul, ol { padding-left: 24px; }
  li { margin: 4px 0; }
  blockquote {
    margin: 16px 0; padding: 12px 16px; border-left: 4px solid var(--blue);
    background: #eff6ff; color: #1e3a8a; border-radius: 0 8px 8px 0;
  }
  blockquote p { margin: 4px 0; }
  code {
    font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    font-size: 0.92em; background: #f1f5f9; border: 1px solid #e2e8f0;
    padding: 1px 5px; border-radius: 5px;
  }
  pre {
    background: #0f172a; color: #e2e8f0; padding: 16px 18px; border-radius: 10px;
    overflow: auto; line-height: 1.6; font-size: 13px;
  }
  pre code { background: transparent; border: 0; padding: 0; color: inherit; }
  table {
    width: 100%; border-collapse: collapse; margin: 14px 0 20px;
    font-size: 14px; background: #fff;
  }
  th, td { border: 1px solid var(--line); padding: 8px 10px; vertical-align: top; text-align: left; }
  th { background: #f8fafc; font-weight: 700; white-space: nowrap; }
  tr:nth-child(even) td { background: #fcfdff; }
  img { max-width: 100%; height: auto; border-radius: 10px; border: 1px solid var(--line); }
  hr { border: 0; border-top: 1px solid var(--line); margin: 28px 0; }
  .toc {
    background: #f8fafc; border: 1px solid var(--line); border-radius: 12px;
    padding: 16px 20px; margin: 22px 0 30px;
  }
  .toc::before {
    content: "目录"; display: block; font-weight: 800; color: #111827;
    margin-bottom: 8px; font-size: 16px;
  }
  .toc > ul { margin: 0; }
  .toc ul { list-style: none; padding-left: 18px; }
  .toc > ul > li { margin: 4px 0; font-weight: 600; }
  .toc a { color: #334155; }
  .toc a:hover { color: var(--blue); }
  .top {
    position: fixed; right: 20px; bottom: 20px; z-index: 9;
    width: 42px; height: 42px; border-radius: 50%;
    background: #111827; color: #fff; display: grid; place-items: center;
    box-shadow: 0 6px 20px rgba(0,0,0,.2); font-size: 18px;
  }
  .top:hover { text-decoration: none; background: #1f2937; }
  .footer { max-width: 1040px; margin: 24px auto 0; color: var(--muted); font-size: 12px; text-align: center; }
  @media (max-width: 720px) {
    .hero h1 { font-size: 28px; }
    article { padding: 22px 18px; }
    h2 { font-size: 21px; }
    table { display: block; overflow-x: auto; }
  }
  @media print {
    body { background: #fff; }
    .hero { background: #fff; color: #000; padding: 0 0 16px; }
    .hero p, .eyebrow { color: #333; }
    .badges, .downloads, .top { display: none; }
    article { border: 0; box-shadow: none; padding: 0; }
    .wrap { max-width: none; padding: 0; }
    h2 { break-after: avoid; }
    pre, table, img { break-inside: avoid; }
  }
</style>
</head>
<body id="top">
<header class="hero">
  <div class="hero-inner">
    <div class="eyebrow">Teacher's Guide · v0.3.2</div>
    <h1>智学数学阅卷助手<br>使用教程</h1>
    <p>从安装、配置 API、写评分细则，到单份阅卷与连续自动阅卷；含 401、JSON 截断、DeepSeek 空正文、容器页 iframe、Edge 跟踪防护等常见问题排查。</p>
    <div class="badges">
      <span class="badge">Tampermonkey 油猴脚本</span>
      <span class="badge">智学网 marking / webmarking / htm-container-web</span>
      <span class="badge">DeepSeek · 通义千问 VL · GLM-4V</span>
      <span class="badge">教师自用 · 人工复核优先</span>
    </div>
    <div class="downloads">
      <a class="btn" href="../zhixue-math-grader.user.js">下载脚本</a>
      <a class="btn ghost" href="../zhixue-math-grader.zip">下载完整包</a>
      <a class="btn ghost" href="../README.md">快速说明</a>
    </div>
  </div>
</header>
<main class="wrap">
  <article>
__BODY__
  </article>
  <div class="footer">
    本教程由实际使用过程整理，已去掉账号、密钥、学生答题图等个人信息。AI 评分仅供参考，正式成绩请由教师审核。
  </div>
</main>
<a class="top" href="#top" title="回到顶部">↑</a>
</body>
</html>
"""

OUT.write_text(template.replace("__BODY__", body), encoding="utf-8")
print("wrote", OUT)
