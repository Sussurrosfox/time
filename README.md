# 《存在与时间》数字化研读与义理题解体系

> **Sein und Zeit · Heidegger Reading & Annotation Project**  
> 致力于构建系统、严谨、沉浸的海德格尔《存在与时间》德汉对照逐段精读与义理题解导读体系。

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Ready-brightgreen)](docs/index.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Quality Gate](https://img.shields.io/badge/7--Gate%20Validation-100%25%20PASS-success)](MIGRATION_REPORT.md)
[![Chapters](https://img.shields.io/badge/Chapters-83%20Complete-orange)](#)
[![Segments](https://img.shields.io/badge/Segments-1284%20Paired-purple)](#)

---

## 📖 项目简介

《存在与时间》（*Sein und Zeit*, 1927）是二十世纪西方哲学的经典巨著。本项目将全书 **83 个章节**进行细密切片，共划分为 **1,284 组精读片段**，并针对每一个片段构建了深度的五维义理题解导读：

1. **术语释义**：解构 Dasein（此在）、Sein-zum-Tode（向死存在）、In-der-Welt-sein（在世界之中存在）等核心哲学术语的德文源义与汉译辨析。
2. **逐句转译**：化解海德格尔式繁复的长句与特殊语法，转换为明晰晓畅的当代学术中文。
3. **论证逻辑梳理**：理清现象学还原与生存论剖析的推导链条。
4. **整体概括**：提炼本节的核心思想命题与哲学关切。
5. **争议与说明**：提示学术界不同译本（如陈嘉映/王庆节译本等）的争议点与文本深层意涵。

本项目已完全转换为符合现代化工程标准的静态站点，原生支持 **GitHub Pages** 一键部署与离线浏览。

---

## 🌐 在线阅读与 GitHub Pages 部署指南

### 1. 开启 GitHub Pages
若您将本项目推送到您的 GitHub 仓库（例如 `https://github.com/<username>/<repo>`）：
1. 访问仓库的 **Settings** -> **Pages**。
2. 在 **Build and deployment** -> **Source** 下选择 **Deploy from a branch**。
3. 在 **Branch** 下选择 `main`（或 `master`），并将目录设置为 **`/docs`**，点击 **Save**。
4. 等待 1~2 分钟，GitHub Pages 将自动上线，您即可在 `https://<username>.github.io/<repo>/` 畅读全书。

### 2. 站点核心阅读特性
- **双栏同步沉浸阅读**：大屏下左侧为德汉精读原文，右侧为系统题解导读，左右独立滚动、对齐参考。
- **全端响应式适配**：移动端自动平滑折叠为流式阅读，排版清晰不局促。
- **深浅色主题自适应**：支持典雅宣纸白与深黛黑夜间模式，实时切换并记住偏好。
- **毫秒级纯前端搜索**：无需后端服务，基于 505KB 倒排索引实现全书全文、章节、术语瞬时检索。
- **键盘导航捷径**：阅读片段时按 `[`（或 `P`）切换上一节，按 `]`（或 `N`）切换下一节。
- **电子书随身下载**：首页导航栏提供全本校订 `time.epub` 原件一键下载。

---

## 💻 本地运行与浏览

本项目全站均采用纯静态 HTML/CSS/JS 编写，无任何外链 CDN 强依赖，**完全支持离线本地运行**。

### 方式一：本地 HTTP 服务浏览（推荐）
在项目根目录下运行 Python 内置简易 HTTP 服务器：
```bash
python -m http.server 8000 -d docs
```
随后在浏览器中打开：[http://127.0.0.1:8000](http://127.0.0.1:8000) 即可享受极速访问与离线全文检索。

### 方式二：直接双击静态文件
直接在文件资源管理器中打开 `docs/index.html` 亦可进行常规浏览。

---

## 📂 项目结构概览

```text
├── .gitignore                    # Git 忽略配置（杜绝凭据、备份及中间产物泄露）
├── LICENSE                       # MIT 开源许可证与学术研究免责声明
├── README.md                     # 项目使用与部署说明文档
├── requirements.txt              # Python 构建依赖 (markdown>=3.5.0)
├── MIGRATION_REPORT.md           # 迁移全景审计报告与 7 项门禁验证记录
├── GITHUB_PAGES_GUIDE.md         # 原始架构改造与设计指南
│
├── content/                      # 【标准化内容源】（干净、无敏感信息）
│   ├── metadata.json             # 全书 83 章节与 1284 片段的总元数据台账
│   ├── chapters/                 # 章节库（004 至 102 补零排序）
│   │   └── {DDD}/                # 例如 004/
│   │       ├── chapter.json      # 章节元数据
│   │       ├── raw.txt           # 章节德汉参考底本全文
│   │       └── segments/         # 切片库（001 至 NNN 补零排序）
│   │           ├── {NNN}.txt     # 原文片段
│   │           └── {NNN}_solution.md # 五大维度逐段义理题解
│   └── prompts/                  # 题解生成提示词模板沉淀 (Yao_prompt1~4.md)
│
├── archive/                      # 【归档资产】
│   └── time.epub                 # 《存在与时间》完整 EPUB 电子书备份
│
├── scripts/                      # 【工程脚本库】
│   ├── migrate_content.py        # 幂等式自动化内容标准化迁移脚本
│   ├── build_site.py             # 静态站点与轻量倒排检索索引生成引擎
│   └── validate_content.py       # 7 重质量与安全自动化门禁核验器
│
├── docs/                         # 【GitHub Pages 交付产物】（静态网站根目录）
│   ├── .nojekyll                 # 声明跳过 Jekyll，保障纯静态资源直传
│   ├── index.html                # 站点首页（总目录大纲、统计面板与全局搜索）
│   ├── 404.html                  # 友好 404 错误页
│   ├── search-index.json         # 客户端全文搜索倒排索引数据
│   ├── assets/
│   │   ├── style.css             # 现代化无依赖样式表
│   │   └── site.js               # 主题切换、即时检索与键盘快捷键
│   ├── archive/
│   │   └── time.epub             # 供在线读者直接下载的电子书副本
│   └── chapters/
│       └── {DDD}/
│           ├── index.html        # 章节总览与片段索引页
│           └── segments/
│               └── {NNN}.html    # 原文与题解双栏研读页
│
└── private-backup/               # 【本地私有隔离区】（被 .gitignore 忽略，永不入库）
    ├── apis.csv                  # 敏感 API Key 隔离文件
    ├── YaoOr.py                  # 私有调用脚本隔离文件
    └── raw_archive.zip           # 迁移前历史平铺目录完整压缩包备份
```

---

## 🛠️ 构建与门禁运行说明

本项目内置完整的构建引擎与零信任自动化质量安全门禁工具。

### 1. 安装构建依赖
```bash
pip install -r requirements.txt
```

### 2. 重建 GitHub Pages 静态站点
当您修改或增补了 `content/` 中的文本或题解后，运行以下命令即可重新编译全站：
```bash
python scripts/build_site.py
```
构建引擎将自动完成：
- 增量编译 1,284 篇精读页与 83 篇章节总览页；
- 提取义理导读正文，剥离 LaTeX 格式标记；
- 更新全局全文搜索索引（`docs/search-index.json`）；
- 拷贝全书 EPUB 电子书发布副本。

### 3. 运行 7 项自动化质量与安全门禁
在任何提交前，必须运行门禁脚本以确保数据完整性与信息安全：
```bash
python scripts/validate_content.py
```
门禁核验包含以下 7 大防线：
- **门禁 1**：`metadata.json` 格式完整性与 83 章节升序排列校验；
- **门禁 2**：逐章校验 1,284 组片段文件物理存在与配对完整性（0 缺失）；
- **门禁 3**：全量文本文件 UTF-8 解码与无乱码替换符（`\ufffd`）核验；
- **门禁 4**：抽样比对原始底稿 SHA-256 哈希值，确保 100% 内容守恒；
- **门禁 5**：全库敏感信息排查（API Key / Token / 密码 / 私有 IP / 宿主路径）；
- **门禁 6**：`.gitignore` 敏感隔离规则有效性核查；
- **门禁 7**：全站 1,368 个 HTML 静态产物无死链（14,957 个站内相对链接 100% 可用）与路径泄漏校验。

---

## 📜 许可证与学术声明

本项目源码与脚本采用 [MIT License](LICENSE) 开源。

**学术声明**：  
本项目所收录之《存在与时间》原文文本及逐段义理题解，仅用于哲学学术交流、个人研读与教育研究目的。读者在引用相关研究成果时，请遵守学术道德规范并注明出处。
