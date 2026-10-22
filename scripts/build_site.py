#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_site.py
《存在与时间》静态网页生成器 (GitHub Pages)
根据 content/ 目录结构与元数据，编译生成全套无外链依赖、纯静态、自适应响应式 docs/ 站点：
- docs/index.html (全书目录与检索首页)
- docs/chapters/{cid}/index.html (83个章节首页与原文全览)
- docs/chapters/{cid}/segments/{sid}.html (1284个片段的原双栏并排/移动端上下堆叠精读页)
- docs/assets/style.css (专业阅读级排版排版系统，深浅色自适应)
- docs/assets/site.js (即时本地模糊搜索、键盘左右翻页导航)
- docs/search-index.json (轻量级全书片段快速检索索引)
"""

import os
import sys
import re
import json
import shutil
import html
from pathlib import Path

# 确保控制台支持 UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import markdown
except ImportError:
    print("[错误] 未安装 markdown 模块，请先运行: pip install markdown")
    sys.exit(1)

def render_markdown(text: str) -> str:
    """安全渲染 Markdown，提取核心义理阐释正文并转义"""
    # 提取 \\begin{solution} 与 \\end{solution} 之间的核心义理阐释正文
    m = re.search(r'\\begin\{solution\}(.*?)(?:\\end\{solution\}|$)', text, re.DOTALL)
    if m:
        clean = m.group(1).strip()
    else:
        clean = re.sub(r'\\begin\{solution\}|\\end\{solution\}', '', text).strip()
    
    # 渲染 Markdown
    md_html = markdown.markdown(
        clean,
        extensions=['fenced_code', 'tables', 'sane_lists']
    )
    return md_html

def escape_text(text: str) -> str:
    return html.escape(text.strip())

def generate_css() -> str:
    return """/* ==========================================================================
   《存在与时间》研读系统 - 全局样式表
   出版级阅读排版，支持宽屏双栏并排、手机端自适应堆叠、深浅色模式切换
   ========================================================================== */

:root {
  --bg-primary: #fcfbf9;
  --bg-surface: #ffffff;
  --bg-subtle: #f4efe6;
  --bg-card: #ffffff;
  --text-primary: #242220;
  --text-secondary: #5c5852;
  --text-muted: #8c867e;
  --accent: #8b3a2b;
  --accent-hover: #a84837;
  --accent-light: #f7ebe8;
  --border-light: #e6e0d6;
  --border-medium: #d4ccc0;
  --quote-border: #8b3a2b;
  --code-bg: #f5f2eb;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.06);
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  --font-serif: "Songti SC", "SimSun", "Noto Serif SC", "STSong", Georgia, serif;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --max-width: 1440px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #151618;
    --bg-surface: #1e2023;
    --bg-subtle: #272a2e;
    --bg-card: #1e2023;
    --text-primary: #e6e4df;
    --text-secondary: #aba69f;
    --text-muted: #78736c;
    --accent: #d47363;
    --accent-hover: #e68878;
    --accent-light: #2c1f1d;
    --border-light: #31353a;
    --border-medium: #42474e;
    --quote-border: #d47363;
    --code-bg: #272a2e;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
  }
}

[data-theme="dark"] {
  --bg-primary: #151618;
  --bg-surface: #1e2023;
  --bg-subtle: #272a2e;
  --bg-card: #1e2023;
  --text-primary: #e6e4df;
  --text-secondary: #aba69f;
  --text-muted: #78736c;
  --accent: #d47363;
  --accent-hover: #e68878;
  --accent-light: #2c1f1d;
  --border-light: #31353a;
  --border-medium: #42474e;
  --quote-border: #d47363;
  --code-bg: #272a2e;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
}

[data-theme="light"] {
  --bg-primary: #fcfbf9;
  --bg-surface: #ffffff;
  --bg-subtle: #f4efe6;
  --bg-card: #ffffff;
  --text-primary: #242220;
  --text-secondary: #5c5852;
  --text-muted: #8c867e;
  --accent: #8b3a2b;
  --accent-hover: #a84837;
  --accent-light: #f7ebe8;
  --border-light: #e6e0d6;
  --border-medium: #d4ccc0;
  --quote-border: #8b3a2b;
  --code-bg: #f5f2eb;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.06);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  overflow-x: hidden;
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-sans);
  line-height: 1.7;
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  word-break: break-word;
  overflow-wrap: break-word;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

a {
  color: var(--accent);
  text-decoration: none;
  transition: color 0.15s ease;
}

a:hover {
  color: var(--accent-hover);
  text-decoration: underline;
}

/* 顶部导航条 */
.site-header {
  background-color: var(--bg-surface);
  border-bottom: 1px solid var(--border-light);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(8px);
}

.header-container {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0.75rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.brand-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}

.brand-badge {
  font-size: 0.75rem;
  font-weight: normal;
  background-color: var(--accent-light);
  color: var(--accent);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-grow: 1;
  justify-content: flex-end;
}

/* 检索输入框 */
.search-wrapper {
  position: relative;
  max-width: 380px;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 0.45rem 0.85rem;
  border: 1px solid var(--border-medium);
  border-radius: 20px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-light);
}

.search-dropdown {
  position: absolute;
  top: 105%;
  left: 0;
  right: 0;
  background: var(--bg-surface);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  max-height: 420px;
  overflow-y: auto;
  display: none;
  z-index: 1000;
}

.search-item {
  padding: 0.65rem 0.9rem;
  border-bottom: 1px solid var(--border-light);
  cursor: pointer;
  display: block;
}

.search-item:last-child {
  border-bottom: none;
}

.search-item:hover, .search-item.active {
  background-color: var(--bg-subtle);
  text-decoration: none;
}

.search-item-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.search-item-snippet {
  font-size: 0.8rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.btn-icon {
  background: none;
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  padding: 0.4rem 0.6rem;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}

.btn-icon:hover {
  background: var(--bg-subtle);
  color: var(--text-primary);
}

/* 主内容布局容器 */
.main-wrapper {
  flex: 1;
  max-width: var(--max-width);
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem 1.25rem 3rem 1.25rem;
}

/* 面包屑导航 */
.breadcrumb-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.breadcrumb-separator {
  color: var(--border-medium);
}

/* 首页 Banner */
.hero-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 2.25rem;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-sm);
}

.hero-title {
  font-size: 2rem;
  font-family: var(--font-serif);
  color: var(--text-primary);
  margin-bottom: 0.75rem;
  font-weight: bold;
}

.hero-meta {
  display: flex;
  gap: 1.25rem;
  flex-wrap: wrap;
  margin-bottom: 1.25rem;
}

.stat-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--bg-subtle);
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.hero-desc {
  font-size: 1rem;
  color: var(--text-secondary);
  line-height: 1.8;
  margin-bottom: 1.25rem;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 1.15rem;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1px solid transparent;
}

.btn-primary {
  background: var(--accent);
  color: #ffffff !important;
}

.btn-primary:hover {
  background: var(--accent-hover);
  text-decoration: none;
}

.btn-secondary {
  background: var(--bg-subtle);
  color: var(--text-primary);
  border-color: var(--border-medium);
}

.btn-secondary:hover {
  background: var(--border-light);
  text-decoration: none;
}

/* 章节目录列表网格 */
.chapter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.25rem;
}

.chapter-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 1.25rem;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.chapter-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--accent);
}

.chapter-card-header {
  margin-bottom: 0.75rem;
}

.chapter-num {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 0.25rem;
  display: inline-block;
}

.chapter-card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.5;
}

.chapter-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--text-muted);
  border-top: 1px solid var(--border-light);
  padding-top: 0.75rem;
  margin-top: 0.75rem;
}

/* 章节详情页 */
.chapter-view-header {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 1.75rem;
  margin-bottom: 1.75rem;
}

.chapter-page-title {
  font-size: 1.75rem;
  font-family: var(--font-serif);
  font-weight: bold;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}

.chapter-nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-light);
  flex-wrap: wrap;
  gap: 0.75rem;
}

/* 折叠原文板块 */
.collapsible-raw {
  margin-bottom: 2rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.collapsible-summary {
  padding: 0.85rem 1.25rem;
  font-weight: 600;
  cursor: pointer;
  background: var(--bg-subtle);
  user-select: none;
  font-size: 0.95rem;
}

.collapsible-content {
  padding: 1.25rem;
  font-family: var(--font-serif);
  line-height: 1.85;
  color: var(--text-secondary);
  font-size: 0.95rem;
  max-height: 380px;
  overflow-y: auto;
  white-space: pre-wrap;
}

/* 片段网格 */
.segments-header {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.segment-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.segment-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 1rem;
  display: block;
  transition: all 0.15s ease;
}

.segment-card:hover {
  border-color: var(--accent);
  box-shadow: var(--shadow-sm);
  text-decoration: none;
}

.segment-card-id {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 0.35rem;
}

.segment-card-snippet {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.6;
  max-height: 4.8em;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

/* ==========================================================================
   片段双栏排版阅读器核心 (Dual Reader Layout)
   桌面端双栏并排 (1440px)，移动端垂直堆叠 (375px)
   ========================================================================== */
.reader-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  align-items: start;
}

/* 栏目容器样式 */
.reader-column {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.column-header {
  background: var(--bg-subtle);
  border-bottom: 1px solid var(--border-light);
  padding: 0.85rem 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.column-title {
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.column-body {
  padding: 1.5rem;
}

/* 原文样式 */
.original-text {
  font-family: var(--font-serif);
  font-size: 1.125rem;
  line-height: 2;
  color: var(--text-primary);
  border-left: 4px solid var(--quote-border);
  padding-left: 1.25rem;
  margin: 0.5rem 0;
  white-space: pre-wrap;
}

/* 题解 Markdown 渲染样式 */
.solution-content h2 {
  display: none; /* 隐藏原文档中重复的题目标记 */
}

.solution-content hr {
  border: none;
  border-top: 1px dashed var(--border-medium);
  margin: 1.25rem 0;
}

.solution-content h3 {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--accent);
  margin: 1.5rem 0 0.75rem 0;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid var(--border-light);
}

.solution-content h3:first-child {
  margin-top: 0;
}

.solution-content p {
  margin-bottom: 1rem;
  line-height: 1.8;
  color: var(--text-secondary);
}

.solution-content ul, .solution-content ol {
  margin-bottom: 1.25rem;
  padding-left: 1.5rem;
}

.solution-content li {
  margin-bottom: 0.5rem;
  line-height: 1.75;
  color: var(--text-secondary);
}

.solution-content strong {
  color: var(--text-primary);
  font-weight: 600;
}

.solution-content blockquote {
  border-left: 3px solid var(--border-medium);
  padding-left: 1rem;
  color: var(--text-muted);
  margin: 1rem 0;
}

.solution-content pre {
  background: var(--code-bg);
  padding: 1rem;
  border-radius: var(--radius-sm);
  overflow-x: auto;
  max-width: 100%;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.solution-content code {
  background: var(--code-bg);
  padding: 2px 5px;
  border-radius: var(--radius-sm);
  font-size: 0.9em;
}

.solution-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  display: block;
  overflow-x: auto;
}

.solution-content th, .solution-content td {
  border: 1px solid var(--border-light);
  padding: 0.5rem 0.75rem;
  text-align: left;
}

.solution-content img {
  max-width: 100%;
  height: auto;
}

/* 翻页导航栏 */
.segment-pagination {
  margin-top: 2rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 1rem 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.shortcut-tip {
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* 页脚 */
.site-footer {
  margin-top: auto;
  border-top: 1px solid var(--border-light);
  background: var(--bg-surface);
  padding: 1.75rem 1.25rem;
  text-align: center;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.footer-links {
  display: flex;
  justify-content: center;
  gap: 1.25rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

/* 状态标签 */
.status-badge {
  display: inline-block;
  padding: 2px 7px;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-paired {
  background-color: rgba(46, 125, 50, 0.12);
  color: #2e7d32;
}

.badge-missing {
  background-color: rgba(211, 47, 47, 0.12);
  color: #d32f2f;
}

/* ==========================================================================
   移动端响应式断点 (自适应 <= 900px，严防 375px 横向溢出)
   ========================================================================== */
@media (max-width: 900px) {
  .reader-container {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .header-container {
    flex-wrap: wrap;
  }
  
  .search-wrapper {
    order: 3;
    max-width: 100%;
    margin-top: 0.5rem;
  }
  
  .hero-card {
    padding: 1.5rem 1rem;
  }

  .hero-title {
    font-size: 1.5rem;
  }
  
  .chapter-grid {
    grid-template-columns: 1fr;
  }
  
  .original-text {
    font-size: 1rem;
    line-height: 1.85;
  }
  
  .column-body {
    padding: 1rem;
  }
}
"""

def generate_js() -> str:
    return """/**
 * 《存在与时间》静态检索与交互控制
 */

(function() {
  'use strict';

  // 1. 深色模式管理
  const themeToggle = document.getElementById('themeToggle');
  const storedTheme = localStorage.getItem('site-theme');
  
  if (storedTheme) {
    document.documentElement.setAttribute('data-theme', storedTheme);
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('site-theme', next);
    });
  }

  // 2. 本地检索功能
  const searchInput = document.getElementById('searchInput');
  const searchDropdown = document.getElementById('searchDropdown');
  let searchIndex = null;

  async function loadSearchIndex() {
    if (searchIndex) return searchIndex;
    try {
      // 动态推断相对于 search-index.json 的相对路径
      const depth = parseInt(document.body.getAttribute('data-depth') || '0', 10);
      let prefix = '';
      for (let i = 0; i < depth; i++) {
        prefix += '../';
      }
      const resp = await fetch(prefix + 'search-index.json');
      if (resp.ok) {
        searchIndex = await resp.json();
      }
    } catch (e) {
      console.warn('加载搜索索引失败:', e);
    }
    return searchIndex;
  }

  if (searchInput && searchDropdown) {
    let debounceTimer = null;

    searchInput.addEventListener('focus', () => {
      loadSearchIndex();
    });

    searchInput.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      const query = e.target.value.trim().toLowerCase();
      if (!query) {
        searchDropdown.style.display = 'none';
        searchDropdown.innerHTML = '';
        return;
      }

      debounceTimer = setTimeout(async () => {
        const index = await loadSearchIndex();
        if (!index) return;

        const results = [];
        const depth = parseInt(document.body.getAttribute('data-depth') || '0', 10);
        let prefix = '';
        for (let i = 0; i < depth; i++) {
          prefix += '../';
        }

        for (const item of index) {
          const matchTitle = item.title.toLowerCase().includes(query);
          const matchSnippet = item.snippet && item.snippet.toLowerCase().includes(query);
          const matchId = item.id && item.id.includes(query);

          if (matchTitle || matchSnippet || matchId) {
            results.push(item);
            if (results.length >= 10) break; // 最多展示 10 条
          }
        }

        if (results.length === 0) {
          searchDropdown.innerHTML = '<div style="padding: 0.8rem; color: var(--text-muted); font-size: 0.85rem; text-align: center;">未找到匹配内容</div>';
        } else {
          searchDropdown.innerHTML = results.map(r => `
            <a href="${prefix}${r.url}" class="search-item">
              <div class="search-item-title">${escapeHtml(r.title)}</div>
              <div class="search-item-snippet">${escapeHtml(r.snippet || '')}</div>
            </a>
          `).join('');
        }
        searchDropdown.style.display = 'block';
      }, 150);
    });

    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
        searchDropdown.style.display = 'none';
      }
    });
  }

  function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // 3. 键盘翻页导航 (片段精读页)
  document.addEventListener('keydown', (e) => {
    // 若在输入框中打字则不拦截
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    if (e.key === 'ArrowLeft') {
      const prevBtn = document.getElementById('prevSegmentBtn');
      if (prevBtn && prevBtn.getAttribute('href')) {
        window.location.href = prevBtn.getAttribute('href');
      }
    } else if (e.key === 'ArrowRight') {
      const nextBtn = document.getElementById('nextSegmentBtn');
      if (nextBtn && nextBtn.getAttribute('href')) {
        window.location.href = nextBtn.getAttribute('href');
      }
    }
  });

})();
"""

def generate_header_html(depth: int, active_nav: str = "") -> str:
    """生成带相对路径的顶部导航栏"""
    prefix = "../" * depth
    return f"""
  <header class="site-header">
    <div class="header-container">
      <a href="{prefix}index.html" class="brand-title">
        <span>📖 《存在与时间》研读</span>
        <span class="brand-badge">逐段解析</span>
      </a>
      <div class="header-controls">
        <div class="search-wrapper">
          <input type="search" id="searchInput" class="search-input" placeholder="搜索章节、片段或关键词..." autocomplete="off">
          <div id="searchDropdown" class="search-dropdown"></div>
        </div>
        <button id="themeToggle" class="btn-icon" title="切换深浅主题" aria-label="切换深浅主题">🌓</button>
      </div>
    </div>
  </header>
"""

def generate_footer_html(depth: int) -> str:
    """生成带版权说明与内部链接的页脚"""
    prefix = "../" * depth
    return f"""
  <footer class="site-footer">
    <div class="footer-links">
      <a href="{prefix}index.html">返回首页</a>
      <a href="{prefix}chapters/004/index.html">第一节</a>
      <a href="https://github.com" target="_blank" rel="noopener">GitHub 仓库</a>
    </div>
    <p>海德格尔《存在与时间》（Martin Heidegger: <em>Sein und Zeit</em>）中文研读与逐段解析</p>
    <p style="margin-top: 4px; font-size: 0.8rem; color: var(--text-muted);">本站内容仅供哲学学术探讨与个人研习使用</p>
  </footer>
"""

def build():
    base_dir = Path(__file__).resolve().parent.parent
    os.chdir(base_dir)

    print("=== 开始构建 GitHub Pages 静态站点 (docs/) ===")

    content_dir = base_dir / "content"
    chapters_dir = content_dir / "chapters"
    metadata_file = content_dir / "metadata.json"
    archive_dir = base_dir / "archive"
    docs_dir = base_dir / "docs"

    if not metadata_file.exists():
        print(f"[错误] 未找到元数据文件: {metadata_file}")
        sys.exit(1)

    with open(metadata_file, "r", encoding="utf-8") as f:
        global_meta = json.load(f)

    # 清理并创建 docs 基础结构
    if docs_dir.exists():
        shutil.rmtree(docs_dir)
    docs_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = docs_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # 写入静态资源
    (assets_dir / "style.css").write_text(generate_css(), encoding="utf-8")
    (assets_dir / "site.js").write_text(generate_js(), encoding="utf-8")
    print("已生成 assets/style.css 与 assets/site.js")

    # 如果 archive/time.epub 存在，复制到 docs/archive/ 以便 GitHub Pages 用户直接下载
    epub_src = archive_dir / "time.epub"
    if epub_src.exists():
        docs_archive = docs_dir / "archive"
        docs_archive.mkdir(parents=True, exist_ok=True)
        shutil.copy2(epub_src, docs_archive / "time.epub")
        print("已就绪 docs/archive/time.epub 下载副本")

    # 构建章节全景数据与全局检索索引
    chapters = global_meta["chapters"]
    search_index = []

    # 预加载所有章节及其片段，以便建立全局跨章前后导航
    all_segments_linear = []
    chapter_dict = {}

    for ch_item in chapters:
        cid = ch_item["id"]
        ch_json_path = chapters_dir / cid / "chapter.json"
        with open(ch_json_path, "r", encoding="utf-8") as f:
            ch_data = json.load(f)
        chapter_dict[cid] = ch_data

        # 录入章节到检索索引
        search_index.append({
            "type": "chapter",
            "id": cid,
            "title": f"第 {cid} 章 · {ch_data['title']}",
            "snippet": f"本章共包含 {len(ch_data['segments'])} 个研读片段",
            "url": f"chapters/{cid}/index.html"
        })

        for s in ch_data["segments"]:
            all_segments_linear.append({
                "chapter_id": cid,
                "chapter_title": ch_data["title"],
                "segment_id": s["id"],
                "status": s["status"],
                "source": s["source"],
                "solution": s["solution"]
            })

    print(f"数据索引就绪: 共计 {len(chapters)} 章节, {len(all_segments_linear)} 片段")

    # ----------------------------------------------------
    # 1. 生成 docs/index.html (首页)
    # ----------------------------------------------------
    print("正在生成首页 docs/index.html...")
    chapter_cards_html = []
    for ch in chapters:
        cid = ch["id"]
        title = escape_text(ch["title"])
        seg_cnt = ch["segment_count"]
        paired_cnt = ch["paired_count"]
        status_text = "全部配对" if paired_cnt == seg_cnt else f"配对 {paired_cnt}/{seg_cnt}"
        badge_class = "badge-paired" if paired_cnt == seg_cnt else "badge-missing"

        chapter_cards_html.append(f"""
      <a href="chapters/{cid}/index.html" class="chapter-card">
        <div class="chapter-card-header">
          <span class="chapter-num">Chapter {cid}</span>
          <h3 class="chapter-card-title">{title}</h3>
        </div>
        <div class="chapter-card-footer">
          <span>{seg_cnt} 个片段</span>
          <span class="status-badge {badge_class}">{status_text}</span>
        </div>
      </a>""")

    index_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>《存在与时间》研读与逐段解析 | 哲学文本精读系统</title>
  <link rel="stylesheet" href="assets/style.css">
</head>
<body data-depth="0">
  {generate_header_html(depth=0)}

  <main class="main-wrapper">
    <section class="hero-card">
      <h1 class="hero-title">《存在与时间》研读与逐段解析</h1>
      <div class="hero-meta">
        <span class="stat-pill">📚 全书 83 个核心章节</span>
        <span class="stat-pill">🧩 1,284 个原文研读片段</span>
        <span class="stat-pill">✨ 100% 义理阐释配对</span>
      </div>
      <p class="hero-desc">
        本研读库将马丁·海德格尔划时代巨著《存在与时间》（<em>Sein und Zeit</em>）中文全译本梳理为细粒度的研读单元，
        每个单元配备<strong>核心术语释义、逐句日常语转译、内在论证逻辑梳理、全局义理概括与学术界争议考辨</strong>。
        支持桌面宽屏双栏并排精读与移动端流畅自适应阅读。
      </p>
      <div class="hero-actions">
        <a href="chapters/{chapters[0]['id']}/index.html" class="btn btn-primary">从第一节开始研读</a>
        <a href="archive/time.epub" class="btn btn-secondary" download>📥 下载完整 EPUB 底本</a>
      </div>
    </section>

    <div class="chapter-grid">
      {"".join(chapter_cards_html)}
    </div>
  </main>

  {generate_footer_html(depth=0)}
  <script src="assets/site.js"></script>
</body>
</html>
"""
    (docs_dir / "index.html").write_text(index_html, encoding="utf-8")

    # ----------------------------------------------------
    # 2. 遍历生成各章节页面与片段页面
    # ----------------------------------------------------
    seg_index_map = {}
    for idx, item in enumerate(all_segments_linear):
        seg_index_map[(item["chapter_id"], item["segment_id"])] = idx

    for ch_idx, ch in enumerate(chapters):
        cid = ch["id"]
        ch_data = chapter_dict[cid]
        ch_title = escape_text(ch_data["title"])
        ch_dir = docs_dir / "chapters" / cid
        seg_dir = ch_dir / "segments"
        seg_dir.mkdir(parents=True, exist_ok=True)

        prev_ch = chapters[ch_idx - 1] if ch_idx > 0 else None
        next_ch = chapters[ch_idx + 1] if ch_idx < len(chapters) - 1 else None

        # 读取 raw.txt 全文供折叠浏览
        raw_path = chapters_dir / cid / "raw.txt"
        raw_content = ""
        if raw_path.exists():
            raw_content = raw_path.read_text(encoding="utf-8")

        # 生成本章的片段卡片 HTML
        seg_cards_html = []
        for s in ch_data["segments"]:
            sid = s["id"]
            # 读取片段 txt 的摘要前 100 字符
            txt_file = chapters_dir / cid / s["source"]
            snippet = ""
            if txt_file.exists():
                snippet = txt_file.read_text(encoding="utf-8").strip()
            
            # 录入 search-index.json
            search_index.append({
                "type": "segment",
                "id": f"{cid}-{sid}",
                "title": f"第 {cid} 章 · 片段 {sid}",
                "snippet": snippet[:90] + ("..." if len(snippet) > 90 else ""),
                "url": f"chapters/{cid}/segments/{sid}.html"
            })

            seg_cards_html.append(f"""
        <a href="segments/{sid}.html" class="segment-card">
          <div class="segment-card-id">片段 {sid}</div>
          <div class="segment-card-snippet">{escape_text(snippet)}</div>
        </a>""")

        # ----------------------------------------------------
        # 2.1 生成 docs/chapters/{cid}/index.html
        # ----------------------------------------------------
        prev_ch_link = f'<a href="../{prev_ch["id"]}/index.html" class="btn btn-secondary">← 上一章 ({prev_ch["id"]})</a>' if prev_ch else '<span class="btn btn-secondary" style="opacity:0.5; cursor:not-allowed;">← 已是首章</span>'
        next_ch_link = f'<a href="../{next_ch["id"]}/index.html" class="btn btn-secondary">下一章 ({next_ch["id"]}) →</a>' if next_ch else '<span class="btn btn-secondary" style="opacity:0.5; cursor:not-allowed;">已是末章 →</span>'

        ch_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>第 {cid} 章 {ch_title} | 《存在与时间》研读</title>
  <link rel="stylesheet" href="../../assets/style.css">
</head>
<body data-depth="2">
  {generate_header_html(depth=2)}

  <main class="main-wrapper">
    <nav class="breadcrumb-nav">
      <a href="../../index.html">首页</a>
      <span class="breadcrumb-separator">/</span>
      <span>第 {cid} 章</span>
    </nav>

    <section class="chapter-view-header">
      <span class="chapter-num">Chapter {cid}</span>
      <h1 class="chapter-page-title">{ch_title}</h1>
      <div class="hero-meta">
        <span class="stat-pill">包含 {len(ch_data["segments"])} 个研读片段</span>
        <span class="stat-pill">原始目录: {ch_data.get("source_dir", cid)}</span>
      </div>

      <div class="chapter-nav-bar">
        {prev_ch_link}
        <a href="segments/{ch_data['segments'][0]['id']}.html" class="btn btn-primary">开始阅读本章片段</a>
        {next_ch_link}
      </div>
    </section>

    <details class="collapsible-raw">
      <summary class="collapsible-summary">📜 查看本章原文通篇全览 (raw.txt)</summary>
      <div class="collapsible-content">{escape_text(raw_content)}</div>
    </details>

    <h2 class="segments-header">分段精读与逐段解析清单</h2>
    <div class="segment-list">
      {"".join(seg_cards_html)}
    </div>
  </main>

  {generate_footer_html(depth=2)}
  <script src="../../assets/site.js"></script>
</body>
</html>
"""
        (ch_dir / "index.html").write_text(ch_html, encoding="utf-8")

        # ----------------------------------------------------
        # 2.2 生成 docs/chapters/{cid}/segments/{sid}.html
        # ----------------------------------------------------
        for seg in ch_data["segments"]:
            sid = seg["id"]
            global_pos = seg_index_map[(cid, sid)]

            prev_seg_info = all_segments_linear[global_pos - 1] if global_pos > 0 else None
            next_seg_info = all_segments_linear[global_pos + 1] if global_pos < len(all_segments_linear) - 1 else None

            # 构造前后导航相对链接
            if prev_seg_info:
                if prev_seg_info["chapter_id"] == cid:
                    prev_url = f"{prev_seg_info['segment_id']}.html"
                    prev_label = f"← 上一段 ({prev_seg_info['segment_id']})"
                else:
                    prev_url = f"../../{prev_seg_info['chapter_id']}/segments/{prev_seg_info['segment_id']}.html"
                    prev_label = f"← 上一章片段 ({prev_seg_info['chapter_id']}-{prev_seg_info['segment_id']})"
                prev_html_btn = f'<a id="prevSegmentBtn" href="{prev_url}" class="btn btn-secondary" title="快捷键: ←">{prev_label}</a>'
            else:
                prev_html_btn = '<span class="btn btn-secondary" style="opacity:0.5; cursor:not-allowed;">← 全书开头</span>'

            if next_seg_info:
                if next_seg_info["chapter_id"] == cid:
                    next_url = f"{next_seg_info['segment_id']}.html"
                    next_label = f"下一段 ({next_seg_info['segment_id']}) →"
                else:
                    next_url = f"../../{next_seg_info['chapter_id']}/segments/{next_seg_info['segment_id']}.html"
                    next_label = f"下一章片段 ({next_seg_info['chapter_id']}-{next_seg_info['segment_id']}) →"
                next_html_btn = f'<a id="nextSegmentBtn" href="{next_url}" class="btn btn-primary" title="快捷键: →">{next_label}</a>'
            else:
                next_html_btn = '<span class="btn btn-secondary" style="opacity:0.5; cursor:not-allowed;">已达全书末尾 →</span>'

            # 读取原文与解析内容
            src_file = chapters_dir / cid / seg["source"]
            sol_file = chapters_dir / cid / seg["solution"]

            orig_text = ""
            if src_file.exists():
                orig_text = src_file.read_text(encoding="utf-8")

            solution_html = ""
            if sol_file.exists():
                solution_raw = sol_file.read_text(encoding="utf-8")
                solution_html = render_markdown(solution_raw)
            else:
                solution_html = '<div class="status-badge badge-missing">⚠️ 本片段解析待补充</div>'

            seg_page_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>第 {cid} 章 片段 {sid} - {ch_title} | 《存在与时间》精读</title>
  <link rel="stylesheet" href="../../../assets/style.css">
</head>
<body data-depth="3">
  {generate_header_html(depth=3)}

  <main class="main-wrapper">
    <nav class="breadcrumb-nav">
      <a href="../../../index.html">首页</a>
      <span class="breadcrumb-separator">/</span>
      <a href="../index.html">第 {cid} 章</a>
      <span class="breadcrumb-separator">/</span>
      <span>片段 {sid}</span>
    </nav>

    <div class="reader-container">
      <!-- 左栏：哲学原文 -->
      <section class="reader-column">
        <div class="column-header">
          <div class="column-title">
            <span>📜</span>
            <span>原文片段 ({cid}/{sid})</span>
          </div>
          <span class="status-badge badge-paired">海德格尔 原文</span>
        </div>
        <div class="column-body">
          <div class="original-text">{escape_text(orig_text)}</div>
        </div>
      </section>

      <!-- 右栏：义理阐释与分步解析 -->
      <section class="reader-column">
        <div class="column-header">
          <div class="column-title">
            <span>💡</span>
            <span>逐段解析与义理阐释</span>
          </div>
          <span class="status-badge badge-paired">结构化精读</span>
        </div>
        <div class="column-body">
          <div class="solution-content">
            {solution_html}
          </div>
        </div>
      </section>
    </div>

    <!-- 底部翻页控制器 -->
    <div class="segment-pagination">
      {prev_html_btn}
      <div style="display:flex; gap:0.5rem; align-items:center;">
        <a href="../index.html" class="btn btn-secondary">返回章节目录 ☰</a>
        <span class="shortcut-tip">提示: 使用键盘 ← → 键可快捷翻页</span>
      </div>
      {next_html_btn}
    </div>
  </main>

  {generate_footer_html(depth=3)}
  <script src="../../../assets/site.js"></script>
</body>
</html>
"""
            (seg_dir / f"{sid}.html").write_text(seg_page_html, encoding="utf-8")

    # ----------------------------------------------------
    # 3. 写入 search-index.json
    # ----------------------------------------------------
    search_json_path = docs_dir / "search-index.json"
    with open(search_json_path, "w", encoding="utf-8") as f:
        json.dump(search_index, f, ensure_ascii=False)
    print(f"已生成 docs/search-index.json (收录 {len(search_index)} 条检索项目, 大小: {search_json_path.stat().st_size / 1024:.1f} KB)")

    print(f"=== 站点构建完成！共生成 1 个首页, {len(chapters)} 个章节页, {len(all_segments_linear)} 个精读页 ===")

if __name__ == "__main__":
    build()
