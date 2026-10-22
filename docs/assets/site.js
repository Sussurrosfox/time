/**
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
