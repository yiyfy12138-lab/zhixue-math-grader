# 智学数学阅卷助手

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-0.3.2-blue)
![Tampermonkey](https://img.shields.io/badge/Tampermonkey-userscript-green)

一个运行在 **智学网阅卷页** 的 Tampermonkey（油猴）脚本：抓取学生答题图 → 多模态 AI 按你的评分细则转写并逐点给分 → 你核对后一键填入分数。

![阅卷面板](docs/images/panel-crop.png)

> 默认 **不自动提交**。AI 只做初评，最终分数由你确认。脚本不包含任何 AI 服务，需自备一个支持图片输入的 OpenAI 兼容接口。
>
> **完整教程**：[docs/TUTORIAL.md](docs/TUTORIAL.md) · [网页版](docs/index.html) · [PDF](docs/智学数学阅卷助手-使用教程.pdf)
>
> **开发状态**：v0.3.2，支持智学网 `marking/webmarking` 页面以及 `htm-container-web` 容器页（含同源 iframe）；首次使用请先开「演示模式」确认取图、填分、提交按钮，再用真实 API。页面改版时用「页面校准」适配。

---

## 它解决什么

- 高中数学解答题步骤多，逐份看很耗时；
- 你可以把「题目 + 标准解答 + 每个给分点值多少分」喂给 AI，让它在同一把尺子下给步骤分；
- 识别结果会显示原文转写、每个给分点的得分/扣分理由、置信度；
- 你只需要核对，然后点「填入分数」，再决定是否提交。

## 不做什么

- 不替你登录，不保存智学网账号密码；
- 不默认自动提交，不绕过平台的阅卷流程；
- 不保证 AI 分数正确。**它是初评工具，不是最终裁判。**

---

## 已验证 / 未验证

已用 Node `--check` 通过语法检查，并用无头 Edge 跑了本地模拟页：

- 面板能注入、演示模式能出分；
- 两个小题分数框能分别填入 `3` 和 `4.5`；
- 模拟 OpenAI 兼容接口能收到题目、图片和 JSON 模式参数；
- 接口不支持 `response_format` 时能自动去掉并重试；
- 模型返回带 `json` 围栏的 Markdown 代码块时能正确解析；
- DeepSeek 空正文/`finish_reason=length` 时能自动关闭 thinking 并重试；
- 同源 iframe 里的答题图、分数框能识别并填入；
- 模拟 `htm-container-web` 的“URL 编码 marking 地址 + iframe 延迟加载”能正常出面板、评分、填分；
- 设置保存、评分细则保存、点击提交按钮各 1 次都正常。


---

## 安装

### 1. 安装 Tampermonkey

| 浏览器 | 安装地址 |
|---|---|
| Edge | https://microsoftedge.microsoft.com/addons/detail/tampermonkey/iikmkjmpaadaobahmlepeloendndfphd |
| Chrome | https://chromewebstore.google.com/detail/tampermonkey/dhdgffkkebhmkfojejmpbldmpobfkfo |
| Firefox | https://addons.mozilla.org/zh-CN/firefox/addon/tampermonkey/ |

### 2. 安装脚本

**方式 A（推荐）**：把 `zhixue-math-grader.user.js` 拖进浏览器窗口，Tampermonkey 会弹出安装页。

**方式 B**：打开 Tampermonkey 管理面板 → 添加新脚本 → 删掉模板 → 粘贴 `zhixue-math-grader.user.js` 全文 → Ctrl+S 保存。

脚本匹配智学网全站，但只在检测到阅卷页面时显示面板：

```text
https://*.zhixue.com/*
```

智学网现在常用容器页打开阅卷，例如：

```text
https://www.zhixue.com/htm-container-web/index.html?app-0=...%2Fwebmarking...%2Fmarking...
```

脚本会解码这个地址，并同时查找主页面和**同源 iframe** 里的答题图、分数框、提交按钮，所以这种容器页也能识别。如果面板没出现，按 F12 看 Console 里是否有 `[智学阅卷]` 报错，并检查页面里是否有阅卷元素。

### 3. 配置多模态 API

面板 → 设置 → AI 接口。脚本支持任何 **OpenAI Chat Completions 兼容** 且支持图片输入的接口。

常见配置示例（模型名请以服务商控制台为准）：

| 服务 | 接口地址 | 模型示例 |
|---|---|---|
| DeepSeek（官方） | `https://api.deepseek.com/chat/completions` | `deepseek-flash`（支持图片；`deepseek-v4-pro` 不支持图片） |
| 阿里云百炼（通义千问 VL） | `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions` | `qwen-vl-max` 或 `qwen-vl-plus` |
| 智谱 BigModel | `https://open.bigmodel.cn/api/paas/v4/chat/completions` | `glm-4v-plus` |
| 火山方舟 | `https://ark.cn-beijing.volces.com/api/v3/chat/completions` | 控制台创建的视觉模型接入点 ID（`ep-...`） |
| 硅基流动 | `https://api.siliconflow.cn/v1/chat/completions` | `Qwen/Qwen2.5-VL-72B-Instruct` 等 |
| OpenAI | `https://api.openai.com/v1/chat/completions` | `gpt-4o` / `gpt-4.1` |
| 本地 Ollama | `http://localhost:11434/v1/chat/completions` | `qwen2.5vl:7b` 等（需先 pull） |

填写 **API Key** 和 **模型名**，点「测试连接」。测试会发一张 1×1 图片，能返回内容即说明接口和密钥可用。

> 已有 DeepSeek Key 的话可以直接用：地址填 `https://api.deepseek.com/chat/completions`，模型填 `deepseek-flash`。注意不要填 `deepseek-v4-pro`，它不支持图片输入。没有 DeepSeek Key 时，推荐通义千问 VL 或智谱 GLM-4V。
>
> **Key 必须和接口地址同一家。** 看到 401 `Incorrect API key provided` 时，先检查是不是把 DeepSeek Key 填到了阿里云 DashScope 地址（或反过来）。设置里的「服务商预设」可以一键切换地址和模型。

### 4. 录入评分细则

设置 → 评分细则。三个核心字段：

1. **题目内容**：完整题干；
2. **标准解答 / 参考步骤**：你提供的详细解法；
3. **评分点**：每行 `分值 | 给分点 | 判定说明`。

示例：

```text
1 | 写出定义域 x>0 | 未写定义域但后续完整，可酌情不给
2 | 正确求导并化为 (1-ax)/x | 只写 1/x-a 给 1 分
1 | a≤0 时判断 f'(x)>0 | 
2 | a>0 时写出 (0,1/a) 增、(1/a,+∞) 减 | 只写“先增后减”给 1 分
```

如果平台按小小题分别给分，用 `##` 分段：

```text
## (1) 5分
1 | 写出定义域 x>0 |
2 | 正确求导 |
1 | a≤0 时单调递增 |
1 | a>0 时写出两个单调区间 |

## (2) 7分
1 | 说明 a≤0 时不恒成立 |
2 | 求出最大值 -ln a |
2 | 解 -ln a≤0 得 a≥1 |
1 | 综上 a∈[1,+∞) |
```

保存后，面板顶部「当前题目」可切换。平台页面有多个分数框时，脚本会要求评分结果也按小小题返回；否则会提示你改用 `##` 分段，避免把总分填进第一个框。

### 5. 先试改一份

1. 打开一份学生答题卡；
2. 点「识别并评分」；
3. 看「学生解答转写」是否准确；
4. 看每个给分点的得分理由；
5. 如果分数不对，直接在结果下方的分数框里改，再点「填入分数」；
6. 确认无误后，自己点平台的「提交分数」。

如果自动取图失败，可以点「上传本地图」：自己截图/裁剪答题区后上传。图片只保存在当前页面内存中，不会写入历史记录。

「添加答题图」的用法：点按钮后鼠标会变成十字，**直接点学生手写的答题图**（v0.3.2 支持点进同源 iframe）；点完会自动抓取并显示缩略图。如果图片在跨域 iframe 里，或点选仍失败，用「上传本地图」最稳。

建议先用「演示模式」确认面板、填分、提交按钮都能正常工作，再填 API Key 真正评分。

### 6. 连续阅卷（自动下一份）

v0.3.2 新增「连续阅卷」按钮。点击后会：

1. 自动抓取当前答题图；
2. AI 评分；
3. 自动填分；
4. 按设置提交；
5. 等下一份试卷加载；
6. 重复，直到达到上限、失败、超时或你点「停止连续」。

设置 → 评分选项：

| 设置 | 说明 |
|---|---|
| 连续阅卷上限 | 默认 20 份，防止挂机跑飞 |
| 提交方式 | **脚本点击提交按钮**：不需要开智学网自动提交；**平台自动提交**：需要先在智学网勾选自动提交，脚本只填分 |
| 遇到“建议复核”时暂停 | 默认关闭；开启后 AI 置信度低/标记复核时会停下来让你看 |

**两种提交方式不要同时用**：

- 用「脚本点击提交」：智学网的“自动提交”保持关闭，避免重复提交；
- 用「平台自动提交」：先在智学网开启自动提交，再把脚本设为平台模式，脚本填完分只等页面变化。

连续阅卷在换卷后会**等新的答题图和分数框加载完成**（最多 15 秒）再开始下一份评分，避免“检测到题目但抓不到图”。如果之前开过“建议复核暂停”，点「连续阅卷」时脚本会提示你是否关闭；关闭后不再逐份停。若平台提交后整页刷新（不是 SPA 换卷），脚本会重新注入，连续状态会停止，需要重新点一次「连续阅卷」。

---

## 页面校准（自动检测失败时）

脚本内置了智学网常见选择器：

- 答题图：`div[name="topicImg"] img`、`.enhance-definition-bright`、`#containter_topicTxt img`
- 分数框：`#txt_marking_all`、`#containter_topicTxt input[name="topicTxt"]`、`input[placeholder*="分"]`
- 提交：`#bnt_save`、文字含「提交分数/提交/下一份」

如果页面改版导致抓不到：

1. 设置 → 页面校准 → **选择答题图**：点学生答题图本身（不要点题目里的公式小图）；
2. **选择分数框**：点分数输入框；如果有多个小小题输入框，点其中一个，脚本会保存选择器并匹配同类输入框；
3. **选择提交按钮**：点「提交分数」或「下一份」；
4. 仍不行，点 **复制页面诊断**，把 JSON 发给开发者（先把学生姓名/学号遮掉）。

脚本会同时查找主页面和**同源 iframe** 里的答题图、分数框、提交按钮（新版微前端架构可能把阅卷界面放在 iframe 中）。跨域 iframe 无法访问其 DOM，仍需另做适配。

### Edge 跟踪防护导致图片/存储失败

如果 Console 出现：

```text
Tracking Prevention blocked access to storage for
https://zhixue-sc.oss-cn-hangzhou.aliyuncs.com/...
```

说明 Edge 的跟踪防护拦了智学网 OSS 图片域的存储/缓存。处理：

1. Edge 设置 → 隐私、搜索和服务 → 跟踪防护 → **例外**；
2. 添加 `https://www.zhixue.com` 和 `https://zhixue-sc.oss-cn-hangzhou.aliyuncs.com`；
3. 或者点地址栏锁图标 → Cookies 和站点数据 → 允许该站点；
4. 刷新页面再试。

如果图片仍然取不到，直接用「上传本地图」；这不依赖 OSS 和页面 DOM。

---

## 评分准确性怎么提高

1. **评分点写到“可判定”**：不要写“酌情给分”，写“写出定义域得 1 分”“只写求导公式给 1 分”。
2. **标准解答写完整**：包括分类讨论、检验、取舍、综上。
3. **提供常见错误**：在「补充说明」里写“只写答案不写步骤最多得 X 分”“分类讨论漏一种扣 X 分”。
4. **图片只裁答题区**：不要带姓名、学号、条形码；手写区域尽量占满画面，保持 1500–2000px 长边。
5. **先用标准/严格尺度**：数学步骤分宁严勿松；确认稳定后再考虑放宽。
6. **抽 10–20 份对照**：你手动打分，和 AI 分对比；把分歧写进评分点备注，再试。
7. **不要迷信总分**：重点看每一步的得分理由，尤其是“答案对但跳步”和“答案错但关键步骤对”的卷子。

---

## 隐私与权限

- API Key 保存在 Tampermonkey 的本地存储里，只发送给你填写的接口；
- 学生答题图会发送给该接口，**不要**把含姓名/学号/身份证的整页图发出去；
- 脚本没有统计、没有远程配置、没有自动更新；
- `@connect *` 是为了允许你填任意 OpenAI 兼容接口；如果你只用一家，可把脚本头部改成对应域名；
- 使用前请遵守学校/平台的数据管理规定。建议优先用学校许可的模型或本地模型。

---

## 常见问题

**Q：Console 显示 `iframe=0` / `roots=1`？**
这是脚本初始化时的快照，不代表最终状态：容器页的内层 iframe 可能 1–3 秒后才创建。v0.3.2 会在 roots 数量变化时再打印一条 `roots=2，iframe=1`。如果一直只有 `roots=1`，说明阅卷界面不在同源 iframe 里（可能在 Shadow DOM 或跨域 iframe）；点「复制页面诊断」，把 JSON 发我。

**Q：不小心把面板关了，怎么找回？**
1. 看页面右下角，有没有一个深色的 **「智学 AI 阅卷」** 浮动胶囊，点它；
2. 按 `Alt + Shift + Z` 显示/隐藏面板；
3. 点 Tampermonkey 图标 → 菜单里的 **「显示/隐藏智学阅卷面板」**；
4. 刷新页面（F5），脚本会重新注入；
5. 如果还没有，检查脚本是否启用、当前 URL 是否在阅卷页。

**Q：面板没出现？**
先确认脚本已更新到 v0.3.2（匹配智学网全站）；确认 Tampermonkey 已启用；F12 Console 看是否有 `[智学阅卷]` 报错。容器页 `/htm-container-web/` 需要等内层阅卷 iframe 加载，通常 1–3 秒后出现。

如果还没有，把下面这段贴到 F12 Console 回车，把输出发我：

```js
(() => {
  const q = (d, s) => { try { return d.querySelector(s); } catch (e) { return null; } };
  const sels = ['#bnt_save','#txt_marking_all','input[name="topicTxt"]','#containter_topicTxt','div[name="topicImg"]','.enhance-definition-bright'];
  const top = Object.fromEntries(sels.map(s => [s, !!q(document, s)]));
  const frames = [...document.querySelectorAll('iframe')].map(f => {
    let d = null;
    try { d = f.contentDocument; } catch (e) {}
    return { name: f.name, src: f.src.slice(0, 180), accessible: !!d,
      hits: d ? Object.fromEntries(sels.map(s => [s, !!q(d, s)])) : null };
  });
  console.log(JSON.stringify({ url: location.href, top, frames }, null, 2));
})();
```

**Q：答题图抓错（抓到题目公式图）？**
点「添加答题图」手动点学生答题图；或在设置里校准。

**Q：分数框抓不到 / 填不进去？**
先点「选择分数框」；填分前先手动点一下输入框再试。部分页面用 React/Vue 受控组件，脚本已用原生 setter + input/change 事件，但改版后仍可能失效。

**Q：页面有 2 个分数框，但 AI 只给一个总分？**
用 `## (1) 5分` / `## (2) 7分` 分小题写评分点；AI 会返回 `sub_scores`，脚本逐框填入。

**Q：模型返回内容为空 / `finish_reason: length`？**
DeepSeek 默认开启思考模式，容易把输出额度全花在 `reasoning_content` 上，正文为空。v0.3.2 会自动对 DeepSeek 发送 `thinking: {"type":"disabled"}`，并在空内容/截断时自动重试一次。仍为空时，把「最大输出 tokens」调到 `8192`；非 DeepSeek 模型也建议至少 `4096`。

**Q：模型返回的不是 JSON / 解析失败？**
先看错误里是不是 `finish_reason=length` 或输出停在 `\begin{`：这是**输出被截断**。把「最大输出 tokens」调到 `4096` 以上（DeepSeek `deepseek-flash` 建议 `4096–8192`）。v0.3.2 会自动把 LaTeX 裸反斜杠（`\{`、`\mid`、`\text`）修成合法 JSON，并在失败时用更高 tokens 重试一次。仍失败时：关掉「要求 JSON 输出」、换更强的视觉模型，或缩短题目/评分细则。

**Q：401 / 404 / 429？**
401 先看 **Key 和接口地址是不是同一家**：DeepSeek Key 不能配阿里云 `dashscope.aliyuncs.com`，阿里云 Key 也不能配 `api.deepseek.com`。设置里先用「服务商预设」选对应服务商，再填 Key。还要确认不是把阿里云 AccessKey ID/Secret 当成百炼 API Key（百炼 Key 以 `sk-` 开头），以及国际站 Key 要配 `dashscope-intl`。404 查接口地址和模型名；429 是限流或额度不足。

**Q：提交后没有下一份？**
脚本不会自动提交；你点的是「填入并提交」时它会先填再弹确认，确认后才点平台按钮。若平台没跳转，手动刷新或点「重新抓取」。

**Q：手机能用吗？**
不能。需要桌面浏览器 + Tampermonkey。

---

## 文件

```text
zhixue-math-grader/
├─ zhixue-math-grader.user.js      # 主脚本
├─ README.md                       # 本文件
├─ LICENSE                         # MIT
├─ CHANGELOG.md                    # 更新日志
├─ PRIVACY.md                      # 隐私说明
├─ PUBLISHING.md                   # 发布到 GitHub / Greasy Fork
├─ SUPPORT.md                      # 支持作者
├─ docs/
│  ├─ TUTORIAL.md                  # 完整教程（Markdown）
│  ├─ index.html                   # 完整教程（网页版）
│  ├─ build_tutorial.py            # 重新生成网页教程
│  ├─ requirements.txt             # 生成教程所需 Python 包
│  └─ images/panel-crop.png        # 面板截图
├─ rubrics/
│  ├─ example-derivative.json      # 示例评分细则（可导入）
│  ├─ zhixue-15-sets.json          # 第15题集合（13分）评分细则
│  └─ template.md                  # 评分细则填写模板
└─ tests/                          # 本地回归测试（模拟页）
```

导入示例：设置 → 评分细则 → 导入 JSON → 选 `example-derivative.json` 或 `zhixue-15-sets.json`。

---

## 支持作者

如果这个脚本帮你节省了一点时间，可以自愿请作者吃碗白饭。金额随意，不影响任何功能，也不构成对评分准确性的承诺。

<img src="docs/images/alipay-qr.jpg" alt="支付宝收款码" width="260">

打开支付宝扫一扫即可。详细说明见 [SUPPORT.md](SUPPORT.md)。

---

## 发布 / 隐私 / 更新

- [发布到 GitHub / Greasy Fork 的完整步骤](PUBLISHING.md)
- [隐私说明](PRIVACY.md)
- [更新日志](CHANGELOG.md)

---

## 免责声明

本工具仅用于辅助教师阅卷，AI 评分结果仅供参考，提交前必须由教师审核。使用本工具产生的评分后果由使用者承担；请遵守智学网及学校的使用条款。本项目与智学网官方无关。
