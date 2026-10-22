# 将本目录整理并发布到 GitHub Pages

本文档是给执行整理工作的模型或开发者的实施规范。目标是把当前目录中的《存在与时间》原文片段、解释稿和章节信息整理成一个可搜索、可导航、适合手机阅读的静态网站，并通过 GitHub Pages 发布。

## 一、现状盘点

当前目录不是一个可以直接发布的网站，而是原始资料目录：

- 83 个数字目录，目录名对应章节编号，但编号并不连续，范围为 `4` 至 `102`。
- 每个章节目录通常包含 `raw.txt`、若干 `N.txt` 和对应的 `N_solution.md`。
- `raw.txt` 的首行是章节标题；`N.txt` 是原文片段；`N_solution.md` 是该片段的解释稿。
- 当前共有约 1,368 个 `.txt`、1,285 个 `.md`，总文件量约 10.8 MB。
- `4/` 中还包含 `Yao_prompt.txt`、`Yao_prompt_solution.md`、`YaoOr.py`、`apis.csv`；这些不是普通阅读内容。
- 根目录的 `time.epub` 是原始电子书归档，可作为下载附件，不应被当作网页入口。
- 文件内容应按 UTF-8 读取。PowerShell 使用默认编码查看时可能出现乱码，不要据此修改正文。

## 二、必须先做的安全处理

`4/apis.csv` 含账户信息和明文 API key，绝对不能进入公开 Git 仓库或 GitHub Pages。

执行顺序：

1. 立即将其中所有已经暴露的 key 作废并重新生成；不要只依赖 `.gitignore`。
2. 将 `apis.csv`、`YaoOr.py` 以及任何带有服务地址、密码、token 的文件移到仓库外的私有备份目录，例如 `private-backup/`（该目录也不能加入 Git）。
3. 搜索整个待发布仓库中的 `sk-`、`api_key`、`password`、`Authorization`、`Bearer`、私有 IP 等字符串；发现后停止发布并清除。
4. 在仓库根目录建立 `.gitignore`，至少包含：

   ```gitignore
   apis.csv
   private-backup/
   *.env
   .venv/
   __pycache__/
   failure.csv
   ```

5. 如果这些文件曾经进入 Git 历史，必须在发布前重写历史或建立一个不带历史的新仓库；仅删除工作区文件不够。

## 三、推荐的仓库组织

采用“内容源文件 + 生成脚本 + `docs/` 发布产物”的结构。GitHub Pages 可以直接选择 `main` 分支的 `/docs` 目录，不需要服务器或数据库。

```text
repository/
├─ README.md
├─ LICENSE                         # 按实际版权情况填写，不要擅自声称公版
├─ .gitignore
├─ GITHUB_PAGES_GUIDE.md           # 本实施规范
├─ content/
│  ├─ chapters/
│  │  ├─ 004/
│  │  │  ├─ chapter.json           # id、标题、原始目录名、状态
│  │  │  ├─ raw.txt
│  │  │  └─ segments/
│  │  │     ├─ 003.txt
│  │  │     ├─ 003_solution.md
│  │  │     └─ ...
│  │  └─ 102/
│  ├─ prompts/
│  │  ├─ Yao_prompt.txt
│  │  └─ Yao_prompt_solution.md     # 若决定公开，作为方法说明而非章节内容
│  └─ metadata.json                 # 全部章节和片段索引
├─ archive/
│  └─ time.epub                     # 可选下载附件；确认版权后再公开
├─ scripts/
│  ├─ build_site.py                 # 生成 docs/
│  └─ validate_content.py           # 完整性、编码和敏感信息检查
├─ requirements.txt                 # 生成器依赖，例如 Markdown 库
└─ docs/                            # 唯一的 GitHub Pages 发布目录
   ├─ index.html
   ├─ chapters/004/index.html
   ├─ chapters/004/segments/003.html
   ├─ assets/style.css
   ├─ assets/site.js
   └─ search-index.json
```

数字统一使用三位补零的目录和 URL（`4` -> `004`，`3` -> `003`），但页面标题中显示中文章节标题和原始编号。这样可以保证字典序和数字顺序一致，避免 `100` 排在 `11` 前面。

## 四、原目录到新目录的确定性映射

对每个当前数字目录 `D` 执行以下规则：

1. 新目录为 `content/chapters/{D:03d}/`。
2. `D/raw.txt` 原样复制为 `content/chapters/{D:03d}/raw.txt`。从第一行提取章节标题；若不存在 `raw.txt`，标题暂用“第 D 章（标题待补）”，并写入异常清单。
3. 每个 `D/N.txt` 原样复制为 `segments/{N:03d}.txt`。
4. 每个 `D/N_solution.md` 原样复制为 `segments/{N:03d}_solution.md`。
5. 只把同时存在的 `N.txt` 和 `N_solution.md` 标记为“已配对”。只有一方存在时仍保留文件，但在 `metadata.json` 中标记 `missing_source` 或 `missing_solution`，并在章节页显示提示。
6. 不要凭内容相似度合并、改写或删除片段；整理阶段只改变路径和元数据。
7. `raw.txt` 不是某个片段的解答，不要复制成 `raw_solution.md`。
8. `4/Yao_prompt*` 移到 `content/prompts/`。`YaoOr.py` 不放进公开内容树，除非先删除硬编码地址和所有密钥读取逻辑，并确认它确实需要公开。
9. `time.epub` 移到 `archive/`，网页提供“下载原始 EPUB”链接的前提是版权允许公开。
10. `.vscode/`、缓存、失败日志、临时文件全部排除。

迁移时使用结构化脚本或文件系统 API，不要用字符串替换批量改正文。复制后逐文件比较 SHA-256 或字节数，确保原文未被截断。

## 五、元数据格式

为每章生成一个 `chapter.json`，格式固定如下：

```json
{
  "id": "004",
  "source_dir": "4",
  "title": "第一节 突出地重提存在问题的必要性",
  "raw_file": "raw.txt",
  "segments": [
    {
      "id": "003",
      "source": "segments/003.txt",
      "solution": "segments/003_solution.md",
      "status": "paired"
    }
  ]
}
```

在 `content/metadata.json` 中汇总所有章节，并按数值 `id` 排序。每个片段页面至少显示：章节标题、片段编号、原文、解释稿、上一片段、下一片段和返回章节目录的链接。

## 六、网站功能要求

第一版保持简单、稳定和可读：

- 首页显示项目名称、资料说明、章节总数、片段总数和按数值排序的章节目录。
- 章节页显示 `raw.txt` 的标题、原文概览、片段列表及配对状态。
- 片段页使用左右或上下两个明确区域展示“原文”和“解读”；移动端改为上下排列。
- 支持按章节标题、章节编号和片段编号搜索。搜索索引只收录标题和正文摘要，避免把整套内容重复塞进每个页面。
- 对 `N_solution.md` 中的 Markdown 标题、列表、引用、代码块和 LaTeX 分隔符进行安全渲染。禁止把正文当作未经转义的 HTML 直接拼接，以免引入脚本。
- 所有链接使用相对路径并以 `/` 结尾或明确指向 `.html`，不能依赖本地绝对路径；在仓库名不是根域名时也必须正常工作。
- 页面包含 `<meta charset="utf-8">`、响应式布局、键盘可用的导航和清晰的页面标题。
- 不把 API、生成提示词中的服务配置或私有运行日志展示在网页上。

## 七、生成与发布流程

推荐让 `scripts/build_site.py` 负责从 `content/` 生成 `docs/`，而不是手工编辑 1,000 多个 HTML 文件。

```text
清理并迁移原始文件
        ↓
validate_content.py
        ↓（无错误才继续）
build_site.py
        ↓
本地静态服务器检查 docs/
        ↓
git diff、链接检查、敏感信息扫描
        ↓
推送 main 分支，Settings → Pages → Deploy from branch → main /docs
```

本地检查可以使用任意静态服务器，例如：

```bash
python -m http.server 8000 --directory docs
```

不要把 `apis.csv` 通过 GitHub Actions secret 以外的方式传给构建流程；本网站生成不需要任何 API key。

## 八、验证清单

执行模型在完成整理后必须给出检查结果，并满足以下条件：

- [ ] 83 个原始章节目录均已处理，章节编号和标题可追溯。
- [ ] `N.txt` 与 `N_solution.md` 的配对数、孤立数均已统计并写入报告。
- [ ] 所有源文件按 UTF-8 成功读取；中文没有乱码或异常替换字符。
- [ ] 复制前后随机抽查至少 10 个片段，并比较 SHA-256。
- [ ] `content/metadata.json` 可被标准 JSON 解析，章节和片段均按数值排序。
- [ ] `docs/index.html`、每个章节首页和每个片段页面均存在。
- [ ] 全站内部链接无 404；首页、一个短章节、一个长章节、缺配对章节各抽查一次。
- [ ] 手机宽度约 375px 和桌面宽度约 1440px 下无横向溢出，原文与解读不重叠。
- [ ] 全仓库扫描不到 `sk-`、`api_key`、密码、Bearer token 或私有服务地址。
- [ ] `apis.csv`、`private-backup/`、缓存和失败日志不在 Git 跟踪列表中。
- [ ] `time.epub` 的公开状态和版权说明已经明确。
- [ ] 页面中没有指向 `D:\time`、`C:\Users` 或其他本机路径的链接。

任何一项失败都应停止发布，先修复并重新运行验证脚本。

## 九、给执行模型的边界

执行模型可以创建目录、复制文件、生成元数据、生成 `docs/` 页面和修复链接；不得擅自改写哲学原文或解释内容，不得猜测缺失标题，不得提交密钥，不得为了“整齐”删除无法配对的片段。遇到编码、版权、缺配对或疑似敏感信息问题，应记录到 `MIGRATION_REPORT.md` 并保留原文件，等待人工决定。

最终提交至少包含：`README.md`、`.gitignore`、`content/`、`scripts/`、`docs/`、`MIGRATION_REPORT.md`，以及（确认可公开时）`archive/time.epub`。
