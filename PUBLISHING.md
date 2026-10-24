# 发布到 GitHub / Greasy Fork 指南

这份文档说明如何把「智学数学阅卷助手」公开分享出去。两种渠道可以只选一个，也可以同时用：

- **GitHub**：放源码、教程、Release 安装包；适合长期维护、收集 Issue。
- **Greasy Fork（油猴脚本站）**：让用户点“安装”就能用；适合非技术用户。

> 发布前请先看最后一节「发布前检查」，不要把真实学生答题图、评分记录、API Key 传上公开仓库。

---

## 一、发布前整理

当前项目结构：

```text
zhixue-math-grader/
├─ zhixue-math-grader.user.js   # 主脚本（发布核心）
├─ README.md
├─ LICENSE                      # MIT
├─ CHANGELOG.md
├─ PRIVACY.md
├─ PUBLISHING.md
├─ SUPPORT.md                    # 支持作者 / 支付宝收款码
├─ .gitignore
├─ docs/
│  ├─ TUTORIAL.md
│  ├─ index.html                # 自包含教程
│  ├─ build_tutorial.py         # 可选：重新生成教程
│  ├─ requirements.txt
│  └─ images/
│     ├─ panel-crop.png
│     └─ alipay-qr.jpg
├─ rubrics/
│  ├─ example-derivative.json
│  ├─ zhixue-15-sets.json
│  └─ template.md
└─ tests/                       # 本地模拟页，可不发布
```

公开前确认：

- [ ] 没有 API Key、Cookie、账号密码；
- [ ] 没有真实学生姓名、学号、答题图、评分记录；
- [ ] `reports/` 里的真实样卷报告已移出项目；
- [ ] 截图是演示数据；
- [ ] `LICENSE` 保留；
- [ ] `README.md` 里没有你的私人地址/联系方式（想留可加）。

---

## 二、发布到 GitHub

### 方式 A：网页上传（不需要安装 Git）

1. 注册/登录 https://github.com；
2. 右上角 `+` → **New repository**；
3. 填写：
   - Repository name：`zhixue-math-grader`
   - Description：`智学网数学阅卷 Tampermonkey 脚本：AI 初评、步骤分、连续阅卷`
   - Public
   - 不勾选 “Add a README file”（你已经有 README）
4. 点 **Create repository**；
5. 在空仓库页点 **uploading an existing file**；
6. 把项目里的文件和文件夹拖进去（`docs`、`rubrics`、`tests`、`.user.js`、`README.md` 等）；
7. Commit message：`feat: initial release v0.3.2`；
8. 点 **Commit changes**。

> GitHub 网页上传支持拖文件夹；如果文件太多，可以分两次上传。

### 方式 B：Git 命令行

先安装 Git for Windows：https://git-scm.com/download/win

```powershell
cd "D:\工作区\zhixue-math-grader"

git init
git add .
git commit -m "feat: initial release v0.3.2"
git branch -M main

# 把 YOUR_NAME 换成你的 GitHub 用户名
git remote add origin https://github.com/YOUR_NAME/zhixue-math-grader.git

git push -u origin main
```

如果 push 要求登录，用 GitHub 的 Personal Access Token（不是账号密码）：

- GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)；
- 生成 `repo` 权限 token；
- push 时用户名填 GitHub 用户名，密码填 token。

### 方式 C：GitHub Desktop

不想用命令行，可以安装 GitHub Desktop，登录后：

1. File → Add local repository → 选项目文件夹；
2. 填 commit message → Commit to main；
3. Publish repository → 选择 Public。

### 2.1 完善仓库信息

在仓库首页点齿轮 **About**：

- Description：`智学网数学阅卷 Tampermonkey 脚本，支持 AI 步骤评分、连续阅卷、DeepSeek/Qwen-VL。`
- Website：可填 GitHub Pages 或教程链接；
- Topics：

```text
tampermonkey
userscript
zhixue
grading
education
ai
deepseek
qwen-vl
```

### 2.2 创建 Release（推荐）

1. 仓库右侧 **Releases** → **Draft a new release**；
2. Tag：`v0.3.2`；
3. Title：`v0.3.2 - 连续阅卷 + 换卷等待 + DeepSeek 修复`；
4. 描述里写更新要点；
5. 附件上传：
   - `zhixue-math-grader.user.js`
   - `zhixue-math-grader.zip`（如果本地有打包）
   - `docs/智学数学阅卷助手-使用教程.pdf`
6. **Publish release**。

用户可以从 Release 下载脚本，也可以点 raw 链接安装。

### 2.3 raw 安装链接

仓库 public 后，脚本的 raw 地址是：

```text
https://raw.githubusercontent.com/YOUR_NAME/zhixue-math-grader/main/zhixue-math-grader.user.js
```

把 `YOUR_NAME` 换成你的用户名，在浏览器打开这个链接，Tampermonkey 会弹出安装页。

### 2.4 更新脚本元数据（让 Tampermonkey 能检查更新）

在 `zhixue-math-grader.user.js` 头部加入/修改：

```js
// @homepageURL  https://github.com/YOUR_NAME/zhixue-math-grader
// @supportURL   https://github.com/YOUR_NAME/zhixue-math-grader/issues
// @downloadURL  https://raw.githubusercontent.com/YOUR_NAME/zhixue-math-grader/main/zhixue-math-grader.user.js
// @updateURL    https://raw.githubusercontent.com/YOUR_NAME/zhixue-math-grader/main/zhixue-math-grader.user.js
// @namespace    https://github.com/YOUR_NAME/zhixue-math-grader
```

同时把 `@author` 改成你的名字/ID。

> 如果你同时发布到 Greasy Fork，**不要让两边的 updateURL 互相指向不同源**。推荐：
> - Greasy Fork 作为主分发：不要在脚本里写 GitHub 的 `@updateURL`，让 Greasy Fork 自己管理更新；
> - GitHub 作为主分发：用 GitHub raw 的 `@updateURL`，并在 README 说明。

### 2.5 GitHub Pages（可选）

想让教程有网页地址：

1. 仓库 Settings → Pages；
2. Source 选 `Deploy from a branch`；
3. Branch 选 `main`，目录选 `/docs`；
4. Save；
5. 地址：`https://YOUR_NAME.github.io/zhixue-math-grader/`。

注意：`docs/index.html` 里的“下载脚本/完整包”链接目前是 `../` 相对路径，在 GitHub Pages 上会指到仓库外，需要改成：

```text
https://raw.githubusercontent.com/YOUR_NAME/zhixue-math-grader/main/zhixue-math-grader.user.js
```

或者不启用 Pages，直接分享 PDF / HTML 文件。

---

## 三、发布到 Greasy Fork（油猴脚本站）

Greasy Fork 是 Tampermonkey 用户最常用的脚本站。发布后用户点“安装”即可。

### 3.1 注册

打开 https://greasyfork.org/ ，用 GitHub 账号或邮箱注册。

### 3.2 发布新脚本

1. 登录后点右上角头像 → **New script** / **发布脚本**；
2. 填写：
   - **Script name**：`智学数学阅卷助手`
   - **Description**：说明支持智学网、AI 步骤评分、连续阅卷、DeepSeek/Qwen-VL；
   - **Language**：Chinese (Simplified)；
   - **License**：MIT；
   - **Script type**：Public；
3. 把 `zhixue-math-grader.user.js` 全文粘贴到代码框；
4. 上传一张截图（可用 `docs/images/panel-crop.png`）；
5. 添加标签：`zhixue`、`grading`、`education`、`ai`、`tampermonkey`；
6. 提交。

Greasy Fork 对新脚本可能有人工/自动审核，等待通过。

### 3.3 Greasy Fork 的脚本要求

- 必须是可读的 userscript，不能压缩/混淆；
- 必须带完整的 UserScript 元数据（`@name`、`@version`、`@match`、`@grant` 等）；
- 描述里要说明它做什么、需要什么 API；
- 不要上传包含密钥、账号、学生隐私的代码；
- 遵守平台条款；在描述里写明“教师辅助工具，AI 分数需人工复核”。

### 3.4 更新版本

1. 修改脚本头 `@version`（例如 `0.3.3`）；
2. Greasy Fork 脚本页 → **Update script** / 上传新版本；
3. 写更新说明；
4. 提交。

Greasy Fork 会自动处理已安装用户的更新检查，不需要你写 `@updateURL`。

### 3.5 同时发布 GitHub + Greasy Fork

推荐做法：

- GitHub 放源码、Issue、Release、教程；
- Greasy Fork 放“用户安装入口”；
- README 里同时给两个链接；
- 脚本 `@namespace` 用 GitHub 仓库地址，保证唯一；
- 不要让 GitHub raw 的 `@updateURL` 和 Greasy Fork 的更新机制打架。二选一作为主更新源。

---

## 四、版本发布检查清单

每次发新版：

- [ ] 修改 `@version` 和 `CHANGELOG.md`；
- [ ] `node --check zhixue-math-grader.user.js` 通过；
- [ ] 本地模拟页测试通过（`tests/`）；
- [ ] 真实阅卷页试 1–2 份；
- [ ] 更新 README/教程里的版本号；
- [ ] 重新生成 `docs/index.html` 和 PDF（如改了教程）；
- [ ] 打包 zip；
- [ ] GitHub Release 上传 `.user.js` + zip + PDF；
- [ ] Greasy Fork 上传新版本；
- [ ] 检查安装链接能弹出 Tampermonkey。

重新生成教程：

```powershell
python -m pip install markdown
python docs/build_tutorial.py
```

再用 Edge 打印 PDF：

```powershell
msedge --headless=new --no-pdf-header-footer `
  --print-to-pdf="docs\智学数学阅卷助手-使用教程.pdf" `
  "file:///D:/工作区/zhixue-math-grader/docs/index.html"
```

---

## 五、发布前检查（重要）

公开仓库不要包含：

- 真实学生答题图、姓名、学号、得分记录；
- 你的 API Key、Cookie、账号密码；
- 带 `markingPaperId` / `examId` 的真实阅卷 URL；
- 学校内部资料。

建议在 README 和 Greasy Fork 描述里加免责声明：

> 本工具仅用于教师阅卷辅助，AI 评分结果仅供参考，正式成绩须由教师复核。使用本工具产生的后果由使用者承担，请遵守智学网及学校的使用条款。本项目与智学网官方无关。

---

## 六、赞助 / 收款码

项目已经带 `SUPPORT.md` 和支付宝收款码 `docs/images/alipay-qr.jpg`。

建议：

- 放在 README 的「支持作者」、教程末尾、Release 说明里；
- **不要**放进脚本面板或弹窗，避免打扰和平台判定为营销；
- 描述写“自愿打赏，不影响功能，不承诺评分结果”；
- 不要做“付费解锁/按份收费/保证提分”；
- 学校/机构采购走合同与发票，不要用个人收款码；
- 二维码是公开图片，注意保护 `main` 分支，避免被 PR 替换。

README 示例：

```markdown
## 支持作者

如果这个脚本帮你节省了一点时间，可以自愿请作者吃碗白饭。
金额随意，不影响任何功能，也不构成对评分准确性的承诺。

<img src="docs/images/alipay-qr.jpg" alt="支付宝收款码" width="260">
```

GitHub 仓库首页的 Sponsor 按钮需要 GitHub Sponsors 或 `FUNDING.yml` 里的赞助页 URL；只有收款码图片时不会自动出现 Sponsor 按钮。

---

## 七、常见问题

**Q：GitHub 上传后 raw 链接打开是代码，不是安装页？**
Tampermonkey 会拦截 `.user.js` 链接；如果没弹，检查 Tampermonkey 是否启用、链接是否以 `.user.js` 结尾。

**Q：Greasy Fork 审核不通过？**
常见原因：代码压缩/混淆、描述太短、没有说明依赖 API、脚本涉及平台自动化。把用途、依赖、免责声明写清楚，代码保持可读。

**Q：需要买域名吗？**
不需要。GitHub 仓库 + Release 足够；Greasy Fork 自带页面。

**Q：可以只发 Greasy Fork，不发 GitHub 吗？**
可以。但 GitHub 更适合放教程、Issue 和完整包；建议至少保留一个源码仓库。

**Q：更新后用户怎么收到？**
- Greasy Fork：自动检查更新；
- GitHub：脚本头 `@updateURL` 指向 raw 链接，Tampermonkey 会定期检查；
- 手动：重新打开安装链接覆盖安装。
