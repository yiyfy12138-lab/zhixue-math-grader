# 智学数学阅卷助手 · 使用教程

> 适用版本：**v0.3.2**  
> 适用场景：智学网网页阅卷（高中数学解答题）  
> 形态：Tampermonkey 油猴脚本 + 你自己的多模态 AI API

---

## 写在前面

这是一个运行在**智学网阅卷页**的浏览器脚本，帮教师做三件事：

1. 抓取当前学生的答题图；
2. 调用支持图片输入的 AI，按你写的评分细则逐点给分；
3. 把分数填回智学网，并按设置提交、进入下一份。

它**不包含 AI 能力**，需要你自备一个 OpenAI 兼容的多模态接口（DeepSeek、通义千问 VL、智谱 GLM-4V 等）。

> **重要**：AI 只做初评。正式考试、统考等高利害场景，请保留人工复核；连续阅卷的自动提交只建议在您已经验证过评分标准、并符合学校规定的前提下使用。

---

[TOC]

---

## 1. 它是怎么工作的

```text
智学网阅卷页
   │
   ├─ 脚本抓取答题图（img / canvas / 背景图 / 同源 iframe）
   │
   ├─ 连同题目、标准解答、评分点发给多模态 AI
   │
   ├─ AI 返回：转写 + 每个给分点得分 + 理由 + 置信度
   │
   ├─ 脚本显示结果，按设置自动填分
   │
   └─ 提交分数 → 检测下一份 → 重复
```

脚本默认不自动提交；只有开启「连续阅卷」并确认后，才会自动填分、提交、进入下一份。

---

## 2. 准备清单

| 需要 | 说明 |
|---|---|
| 浏览器 | Edge / Chrome / Firefox（推荐 Edge 或 Chrome） |
| Tampermonkey | 免费油猴扩展 |
| 智学网账号 | 已登录、有未完成阅卷任务 |
| 多模态 API Key | DeepSeek、通义千问 VL、智谱 GLM-4V 等 |
| 评分细则 | 题目、标准解答、每个给分点及分值 |

不需要把智学网账号密码交给任何人，也不需要把 API Key 发给我。

---

## 3. 安装脚本

### 3.1 安装 Tampermonkey

| 浏览器 | 地址 |
|---|---|
| Edge | https://microsoftedge.microsoft.com/addons/detail/tampermonkey/iikmkjmpaadaobahmlepeloendndfphd |
| Chrome | https://chromewebstore.google.com/detail/tampermonkey/dhdgffkkebhmkfojejmpbldmpobfkfo |
| Firefox | https://addons.mozilla.org/zh-CN/firefox/addon/tampermonkey/ |

### 3.2 安装脚本

**方式 A（推荐）**：把 `zhixue-math-grader.user.js` 拖进浏览器窗口，Tampermonkey 会弹出安装页，点“安装”。

**方式 B**：Tampermonkey 管理面板 → 添加新脚本 → 删除模板 → 粘贴脚本全文 → `Ctrl + S`。

脚本会申请：

- `*://*.zhixue.com/*`：在智学网页面运行；
- `GM_xmlhttpRequest`：下载答题图、调用你填的 API；
- `GM_getValue / GM_setValue`：在本地保存配置；
- `GM_registerMenuCommand`：在 Tampermonkey 菜单里提供“显示/隐藏面板”。

### 3.3 确认脚本运行

打开阅卷页后，按 `Ctrl + Shift + I` 打开 Console（不是 F12，部分笔记本 F12 是音量键），应看到：

```text
[智学阅卷] v0.3.2 已加载，marking=true，iframe=...
[智学阅卷] 面板已注入，roots=...
```

如果完全没有这两行，说明 Tampermonkey 没加载脚本，检查脚本是否启用、是否允许了 `*.zhixue.com`。

---

## 4. 打开阅卷页：普通页与容器页

### 4.1 普通阅卷页

```text
https://*.zhixue.com/marking/...
https://*.zhixue.com/webmarking/...
```

打开后右上角出现面板。

### 4.2 容器页（新版微前端）

智学网现在常用这种地址打开阅卷：

```text
https://www.zhixue.com/htm-container-web/index.html?app-0=...%2Fwebmarking...%2Fmarking...
```

真正的阅卷地址在 `app-0` 参数里，而且是**双重 URL 编码**，页面可能再把 `/webmarking/.../#/marking/...` 装进一个同源 iframe。

v0.2 以后脚本会：

- 匹配整个 `*.zhixue.com`；
- 对 URL 解码两次；
- 同时扫描主页面和同源 iframe；
- 只在检测到阅卷页面/元素时才显示面板。

所以容器页也能用，不需要改脚本。

### 4.3 `iframe=0` 是正常的

脚本刚加载时打印：

```text
iframe=0
```

只代表那一刻 iframe 还没创建。容器页的内层 iframe 可能 1–3 秒后才出现；v0.3.2 会在 roots 数量变化时再打印：

```text
[智学阅卷] roots=2，iframe=1 [...]
```

如果等 5 秒后仍然只有 `roots=1`，说明阅卷界面不在同源 iframe 里（可能在 Shadow DOM 或跨域 iframe），需要看“页面诊断”。

---

## 5. 面板说明

![阅卷面板](images/panel-crop.png)

> 图为演示模式截图，7.5/10 是假分数；真实评分会显示 AI 的逐点理由。演示模式永远标记“建议复核”，这是正常的。

从上到下：

1. **状态条**：正在抓图 / AI 评分 / 评分完成 / 失败原因；
2. **当前题目**：切换评分细则；
3. **识别并评分**：抓图 + 调 AI；
4. **添加答题图**：手动点选，或点“上传本地图”；
5. **连续阅卷**：自动评分、填分、提交、下一份；
6. **答题图缩略图**：可移除、重新抓取、上传本地图；
7. **评分结果**：总分、置信度、逐点得分理由、转写；
8. **填分按钮**：填入分数 / 填入并提交；
9. **设置 / 评分细则**：API、评分标准、页面校准。

> 截图是演示模式，所以显示“建议复核”；真实评分是否复核取决于 AI 置信度和你的设置。

---

## 6. 配置 AI 接口

打开：面板 → **设置 / 评分细则** → **AI 接口**。

### 6.1 先选服务商预设

v0.2.2 以后设置里有「服务商预设」：

| 预设 | 接口地址 | 模型 |
|---|---|---|
| DeepSeek 官方 | `https://api.deepseek.com/chat/completions` | `deepseek-flash` |
| 阿里云百炼（中国站） | `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions` | `qwen-vl-max` |
| 阿里云百炼（国际站） | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions` | `qwen-vl-max` |
| 智谱 BigModel | `https://open.bigmodel.cn/api/paas/v4/chat/completions` | `glm-4v-plus` |
| OpenAI | `https://api.openai.com/v1/chat/completions` | `gpt-4o` |
| 本地 Ollama | `http://localhost:11434/v1/chat/completions` | `qwen2.5vl:7b` 等 |

选预设会自动填接口地址和模型名，你只需要填对应服务商的 API Key。

### 6.2 DeepSeek 配置（推荐给已有 DeepSeek Key 的用户）

| 字段 | 值 |
|---|---|
| 接口地址 | `https://api.deepseek.com/chat/completions` |
| 模型 | `deepseek-flash` |
| API Key | `platform.deepseek.com` 申请的 Key |
| 最大输出 tokens | `8192` |

注意：

- 必须用 `deepseek-flash`，它支持图片输入；
- `deepseek-v4-pro` **不支持**图片；
- 不要用旧的纯文本 `deepseek-chat / deepseek-reasoner` 做图片识别；
- DeepSeek 默认开启思考模式，v0.2.4 以后脚本会自动发送 `thinking: {"type":"disabled"}`，避免正文为空；
- 如果仍然 `finish_reason=length`，把 tokens 提到 8192。

### 6.3 通义千问 VL 配置

| 字段 | 值 |
|---|---|
| 接口地址 | `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions` |
| 模型 | `qwen-vl-max` 或 `qwen-vl-plus` |
| API Key | 阿里云百炼控制台的 API Key |

国际站账号用：

```text
https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions
```

### 6.4 401：Key 和接口地址不是同一家

如果报：

```text
API Key 无效或未授权（401）：Incorrect API key provided
```

先看接口地址：

- 地址是 `dashscope.aliyuncs.com`，但你填的是 DeepSeek Key → 401；
- 地址是 `api.deepseek.com`，但你填的是阿里云 Key → 401；
- 把阿里云主账号的 AccessKey ID/Secret 当成百炼 API Key → 401（百炼 Key 通常以 `sk-` 开头）；
- Key 复制时带了空格/换行、已被删除、换了账号 → 401。

**Key 必须和接口地址同一家。** 用「服务商预设」可以避免大部分混用。

### 6.5 测试连接

填完 Key 后点 **测试连接**。测试会发一张 1×1 图片：

- 返回内容 → 接口和 Key 可用；
- 401 → 查 Key/服务商；
- 404 → 查接口地址/模型名；
- 429 → 限流或额度不足。

---

## 7. 写评分细则

设置 → **评分细则** → 新建/导入/编辑。

### 7.1 三个核心字段

| 字段 | 写什么 |
|---|---|
| 题目内容 | 完整题干，包括小问、范围、量词 |
| 标准解答 / 参考步骤 | 你提供的详细解法，越完整越好 |
| 评分点 | 每行：`分值｜给分点｜判定说明` |

### 7.2 评分点语法

```text
2 | 正确求导并化为 (1-ax)/x | 只写 1/x-a 给 1 分
1 | 写出定义域 x>0 |
2 | a>0 时写出 (0,1/a) 增、(1/a,+∞) 减 | 只写“先增后减”给 1 分
```

- 分值放最前面；
- 给分点写“可观察的动作”，不要写“酌情给分”；
- 判定说明写“只写 X 给几分”“漏 Y 扣几分”；
- 分值合计应等于满分；不一致时脚本会提示，但仍可保存。

### 7.3 分小题

平台有两个分数框时，用 `##` 分段：

```text
## (1) 6分
2 | 由 m=-5 求出 B=(-10,-6) |
2 | 正确求补集 |
2 | 正确求交集 | 必须包含中间区间

## (2) 7分
1 | 由 A∪B=A 得 B⊆A |
3 | B=∅ 时得 m≥-1 |
2 | B≠∅ 时分类得 m≤-2 |
1 | 综上 |
```

保存后，AI 会返回 `sub_scores`，脚本逐框填入，不会把总分塞进第一个框。

### 7.4 导入/导出

- 设置 → 评分细则 → **导入 JSON**；
- 可导入 `rubrics/example-derivative.json` 或 `rubrics/zhixue-15-sets.json`；
- 也可点 **导出 JSON** 备份；
- 不同题目可以保存多个评分细则，用面板顶部“当前题目”切换。

### 7.5 提高准确率

1. 评分点写到“可判定”，不要“酌情”；
2. 标准解答写完整，包括分类讨论、检验、取舍、综上；
3. 在“补充说明”写常见错误和扣分规则；
4. 图片只裁答题区，别带姓名/学号；
5. 先用“标准/严格”尺度，抽 10–20 份和手动分对照；
6. 不要只看总分，重点看每一步的得分理由。

---

## 8. 单份阅卷

### 8.1 取图

三种方式：

1. **自动**：点「识别并评分」，脚本自动找答题图；
2. **手动点选**：点「添加答题图」→ 鼠标变十字 → 点学生答题图（支持同源 iframe）；
3. **上传本地图**：截图后点「上传本地图」，不依赖页面 DOM/OSS。

如果自动抓错（抓到题目公式图），移除缩略图后手动点选。

### 8.2 评分

点「识别并评分」后，AI 返回：

- 学生解答转写（OCR）；
- 每个给分点的得分/扣分理由；
- 总分、置信度、建议复核标记；
- 简短评语。

分数可以直接在结果下方修改，再点「填入分数」。

### 8.3 提交

- 「填入分数」：只填分，不提交；
- 「填入并提交」：填分后弹确认，确认后点平台提交按钮；
- 连续阅卷：按设置自动提交。

### 8.4 演示模式

设置 → 评分选项 → 勾选「演示模式」：

- 不调用 API；
- 用假分数测试取图、填分、提交按钮；
- 演示结果永远标记“建议复核”，这是正常的。

---

## 9. 页面校准

### 9.1 自动检测

脚本内置智学网常见选择器：

- 答题图：`div[name="topicImg"] img`、`.enhance-definition-bright`、`#containter_topicTxt img`
- 分数框：`#txt_marking_all`、`#containter_topicTxt input[name="topicTxt"]`、`input[placeholder*="分"]`
- 提交：`#bnt_save`、文字含“提交分数/提交/下一份”

### 9.2 手动点选

设置 → 页面校准：

1. **选择答题图**：点学生答题图本身；
2. **选择分数框**：点分数输入框；有多个小小题时点一个，脚本会匹配同类；
3. **选择提交按钮**：点“提交分数”或“下一份”。

v0.2.1 以后支持点进**同源 iframe**，选择器会保存成：

```text
iframe选择器 >>> 内部选择器
```

### 9.3 页面诊断

设置 → 页面校准 → **复制页面诊断**，会把以下信息复制到剪贴板：

- 当前 URL、viewport；
- roots/iframe 数量；
- 每个 iframe 的 name/src/是否可访问、input/image/button 数量；
- Shadow DOM 宿主；
- 页面上的图片、输入框、按钮候选；
- 脚本检测到的答题图/分数框/提交按钮数量。

排查页面问题时，先发这个 JSON（先把学生姓名/学号遮掉）。

### 9.4 Edge 跟踪防护拦截 OSS 图片

如果 Console 出现：

```text
Tracking Prevention blocked access to storage for
https://zhixue-sc.oss-cn-hangzhou.aliyuncs.com/...
```

处理：

1. Edge 设置 → 隐私、搜索和服务 → 跟踪防护 → 例外；
2. 添加 `https://www.zhixue.com` 和 `https://zhixue-sc.oss-cn-hangzhou.aliyuncs.com`；
3. 或点地址栏锁图标 → Cookies 和站点数据 → 允许；
4. 刷新页面。

仍取不到图，就用「上传本地图」。

---

## 10. 连续阅卷

### 10.1 两种提交方式（二选一）

| 方式 | 智学网“自动提交” | 脚本设置 | 谁提交 |
|---|---|---|---|
| 脚本提交 | **关闭** | 提交方式 = 脚本点击“提交”按钮 | 脚本 |
| 平台提交 | **开启** | 提交方式 = 平台自动提交（脚本只填分） | 智学网 |

**不要两边同时开**，避免重复提交。

### 10.2 设置

设置 → 评分选项：

| 设置 | 建议 |
|---|---|
| 连续阅卷上限 | 先 5 份，稳定后 20–50 |
| 提交方式 | 按上面二选一 |
| 遇到“建议复核”时暂停 | 想全自动就取消勾选；v0.3.2 默认关闭 |
| 自动填分 | 连续模式会自己填，不影响 |

### 10.3 开始/停止

1. 回到面板，点 **连续阅卷**；
2. 确认风险提示；
3. 按钮变成 **停止连续**；
4. 随时可点停止。

停止条件：

- 达到上限；
- 评分失败；
- 找不到提交按钮；
- 20 秒等不到下一份；
- 开启“建议复核暂停”且当前卷被标记；
- 你手动停止。

### 10.4 换卷检测

v0.3.2 在提交后：

- 最多等 15 秒，直到新的答题图加载 + 新的分数框出现；
- 比对提交前的图片签名，避免抓到上一份旧图；
- 抓图失败重试 4 次；
- 等不到才暂停。

如果平台提交后是**整页刷新**（不是 SPA 换卷），脚本会重新注入，连续状态会断，需要重新点一次「连续阅卷」。

### 10.5 首次使用建议

1. 先用演示模式，上限 2–3 份，确认换卷和填分；
2. 再用真实 API，上限 3–5 份；
3. 对照手动评分，确认稳定后再放开上限；
4. 高利害考试保留人工复核。

---

## 11. 常见报错与处理

### 11.1 面板不见了

1. 页面右下角找深色浮动胶囊「智学 AI 阅卷」，点它；
2. `Alt + Shift + Z` 显示/隐藏；
3. Tampermonkey 图标 → 「显示/隐藏智学阅卷面板」；
4. 刷新页面；
5. 检查脚本是否启用。

### 11.2 按 F12 变成音量

用：

- `Ctrl + Shift + I`；
- 页面右键 → 检查；
- Edge 菜单 → 更多工具 → 开发人员工具；
- `Fn + F12`。

### 11.3 插件完全没运行 / 容器页没反应

- v0.1 只匹配 `/marking`、`/webmarking`，容器页 `/htm-container-web/` 不会运行；
- v0.2 以后匹配 `*.zhixue.com/*`，并对 URL 解码两次；
- 更新后必须刷新页面；
- Console 应有 `[智学阅卷] v... 已加载`。

### 11.4 `iframe=0` / `roots=1`

初始化快照，不代表最终状态；等 1–3 秒，v0.3.2 会打印 roots 变化。一直 `roots=1` 就发页面诊断。

### 11.5 401 Incorrect API key

见 6.4：Key 与接口地址不是同一家，或用了 AccessKey/过期 Key。

### 11.6 模型未返回合法 JSON

常见两种原因：

1. **裸 LaTeX 反斜杠**：`\{`、`\mid`、`\text` 不是合法 JSON 转义；
2. **输出被截断**：停在 `\begin{`、`finish_reason=length`。

v0.2.3 以后会：

- 自动把裸 LaTeX 反斜杠修成合法 JSON；
- 失败时提高 tokens 重试一次；
- 限制转写 600 字。

仍失败：

- 最大输出 tokens 调到 4096–8192；
- 关掉“要求 JSON 输出”；
- 换更强的视觉模型；
- 缩短题目/评分细则。

### 11.7 模型返回内容为空（finish_reason: length）

DeepSeek 默认思考模式会把额度花在 `reasoning_content`，正文为空。

v0.2.4 以后对 DeepSeek 自动发送：

```json
{"thinking": {"type": "disabled"}}
```

并把 tokens 调高重试。仍为空：

- 最大 tokens 8192；
- 换 `qwen-vl-max` / `glm-4v-plus`；
- 看 Console 的 `reasoning长度=` 日志。

### 11.8 添加答题图抓不到

- v0.2.1 以后支持同源 iframe 点选；
- 点按钮后要直接点**学生答题图**；
- 跨域 iframe/OSS 被拦截 → 用「上传本地图」；
- Edge 跟踪防护按 9.4 加例外。

### 11.9 下一题不会自动抓图评分

- v0.3.2 最多等 15 秒新图+分数框，抓图重试 4 次；
- 如果平台整页刷新，连续状态会停，需要重新点「连续阅卷」；
- 如果一直停：看 Console 是否 `已换卷，但 15 秒内没有等到新的答题图/分数框`；发页面诊断。

### 11.10 连续阅卷总是停在“建议复核”

- 设置 → 评分选项 → 取消勾选“遇到建议复核时暂停”；
- v0.3.2 点连续阅卷时会提示你是否关闭；
- AI 置信度低/转写为空/总分不一致都会触发复核标记；看具体 review_reasons。

### 11.11 提交后没有下一份 / 重复提交

- 脚本提交模式：智学网自动提交要关闭；
- 平台提交模式：智学网自动提交要开启；
- 不要两边同时开；
- 若平台弹“确定”确认框，脚本目前不会自动点，需把截图发开发者适配。

---

## 12. 安全、隐私与合规

- API Key 保存在 Tampermonkey 本地存储，只发送给你填写的接口；
- 学生答题图会发送给该接口；**不要**把含姓名、学号、身份证的整页图发出去；
- 建议只裁答题区，或使用学校许可的模型/本地模型；
- 脚本没有统计、没有远程配置、没有自动更新；
- `@connect *` 是为了允许任意 OpenAI 兼容接口，如果你只用一家，可把脚本头部改成对应域名；
- 使用前请遵守学校/平台的数据管理规定；
- AI 评分可能出错，正式成绩必须由教师复核；连续自动提交的风险由使用者承担。

---

## 13. 文件与版本

```text
zhixue-math-grader/
├─ zhixue-math-grader.user.js      # 主脚本
├─ README.md                       # 快速说明
├─ SUPPORT.md                      # 支持作者
├─ docs/
│  ├─ TUTORIAL.md                  # 本教程
│  ├─ index.html                   # 网页版教程
│  └─ images/
│     ├─ panel-crop.png            # 面板截图
│     └─ alipay-qr.jpg             # 支付宝收款码
├─ rubrics/
│  ├─ example-derivative.json      # 示例评分细则
│  ├─ zhixue-15-sets.json          # 第15题集合评分细则
│  └─ template.md                  # 评分细则模板
└─ tests/                          # 本地回归测试（模拟页）
```

版本要点：

| 版本 | 关键变化 |
|---|---|
| v0.1 | 初版：智学网 marking/webmarking |
| v0.2 | 支持 htm-container-web、容器 URL 解码、同源 iframe |
| v0.2.1 | iframe 内手动取图/选分数框 |
| v0.2.3 | 修复裸 LaTeX JSON、截断自动重试 |
| v0.2.4 | DeepSeek 关闭思考模式、空正文重试 |
| v0.3.0 | 连续阅卷、平台/脚本两种提交方式 |
| v0.3.1 | 面板显示/隐藏快捷键与 Tampermonkey 菜单 |
| v0.3.2 | 换卷后等待新图/分数框、抓图重试、默认不暂停复核 |

---

## 14. 一页检查清单

安装后：

- [ ] Tampermonkey 已启用脚本；
- [ ] Console 有 `[智学阅卷] v0.3.2 已加载`；
- [ ] 面板能显示；
- [ ] API 服务商/地址/模型/Key 对应；
- [ ] 测试连接成功；
- [ ] 评分细则已保存，分值合计=满分；
- [ ] 演示模式能取图、填分、提交；
- [ ] 真实 API 试改 3–5 份，和手动分对照；
- [ ] 连续阅卷上限先设 5；
- [ ] 提交方式只选一种；
- [ ] 学生隐私已脱敏；
- [ ] 正式成绩保留人工复核。

---

## 15. 支持作者

如果这个脚本帮你节省了一点时间，可以自愿请作者吃碗白饭。金额随意，**不影响任何功能**，也不构成对评分准确性的承诺。

<img src="images/alipay-qr.jpg" alt="支付宝收款码" width="300">

打开支付宝扫一扫即可。

> 打赏完全自愿；不接受“付费保证提分”“按份收费”等约定。学校/机构采购请走正规合同与发票，不要用个人收款码。

---

*本教程由实际使用过程整理，已去掉账号、密钥、学生答题图等个人信息。*
