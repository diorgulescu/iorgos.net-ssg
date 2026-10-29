/**
 * TACTICAL HUD // CLIENT SCRIPT
 * Standalone, zero-dependency JavaScript with Dynamic Dark/Light HUD
 */

const THEME_STORAGE_KEY = 'theme_preference';

function getSystemTheme() {
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    return 'light';
  }
  return 'dark';
}

function getActiveTheme() {
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  if (stored === 'light' || stored === 'dark') {
    return stored;
  }
  return getSystemTheme();
}

function applyTheme(theme, save = false) {
  const isDark = theme === 'dark';
  const root = document.documentElement;

  root.classList.remove('dark', 'light');
  root.classList.add(theme);
  root.setAttribute('data-theme', theme);

  if (save) {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  }

  // Update all theme toggle buttons across the UI
  document.querySelectorAll('.theme-toggle-btn').forEach((btn) => {
    btn.setAttribute('aria-label', isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme');
    btn.setAttribute('title', isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme');
    const icon = btn.querySelector('.theme-toggle-icon');
    if (icon) {
      icon.textContent = isDark ? '☼' : '☾';
      icon.className = 'theme-toggle-icon font-mono text-sm leading-none';
    }
  });

  // Update HUD indicator in top bar
  const telemetryStatus = document.getElementById('theme-status-hud') || document.getElementById('theme-status-telemetry');
  if (telemetryStatus) {
    telemetryStatus.textContent = isDark ? 'MODE // DARK' : 'MODE // LIGHT';
    telemetryStatus.className = isDark
      ? 'hidden sm:inline font-mono text-[10px] uppercase text-emerald-400'
      : 'hidden sm:inline font-mono text-[10px] uppercase text-sky-600 font-semibold';
  }
}

function toggleTheme() {
  const current = document.documentElement.classList.contains('light') ? 'light' : 'dark';
  const next = current === 'dark' ? 'light' : 'dark';
  applyTheme(next, true);
}

document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Theme & Bind Buttons
  applyTheme(getActiveTheme(), false);

  document.querySelectorAll('.theme-toggle-btn').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      toggleTheme();
    });
  });

  // Listen to OS / Browser color scheme change in real time
  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem(THEME_STORAGE_KEY)) {
        applyTheme(e.matches ? 'dark' : 'light', false);
      }
    });
  }

  // 2. Live System HUD Clock
  const clockElement = document.getElementById('hud-clock') || document.getElementById('telemetry-clock');
  function updateClock() {
    if (!clockElement) return;
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    clockElement.textContent = `${hours}:${minutes}:${seconds} // LOCAL`;
  }
  updateClock();
  setInterval(updateClock, 1000);

  // 3. Mobile Menu Toggle
  const menuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });
  }

  // 4. Current Year in Footer
  const yearElement = document.getElementById('current-year');
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  }

  // 5. Code Block Copy to Clipboard
  document.querySelectorAll('pre').forEach((preBlock) => {
    if (preBlock.querySelector('.copy-btn')) return;

    const btn = document.createElement('button');
    btn.className = 'copy-btn absolute top-2 right-2 px-2 py-0.5 rounded border border-slate-700 bg-slate-900/90 text-[11px] font-mono text-slate-400 hover:text-slate-200 transition-colors opacity-0 group-hover:opacity-100';
    btn.textContent = 'copy';

    preBlock.classList.add('group', 'relative');
    preBlock.appendChild(btn);

    btn.addEventListener('click', async () => {
      const code = preBlock.querySelector('code') || preBlock;
      const text = code.innerText.replace(/copy$/, '').replace(/copied!$/, '').trim();
      try {
        await navigator.clipboard.writeText(text);
        btn.textContent = 'copied!';
        btn.classList.add('text-amber-400');
        setTimeout(() => {
          btn.textContent = 'copy';
          btn.classList.remove('text-amber-400');
        }, 2000);
      } catch (err) {
        console.error('Copy failed:', err);
      }
    });
  });

  // 6. Client Search / Filter on List Pages
  const searchInput = document.getElementById('hud-filter-input');
  if (searchInput) {
    const filterTarget = searchInput.getAttribute('data-target') || '.journal-entry';
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase().trim();
      document.querySelectorAll(filterTarget).forEach((item) => {
        const text = item.textContent.toLowerCase();
        if (text.includes(query)) {
          item.style.display = '';
        } else {
          item.style.display = 'none';
        }
      });
    });
  }

  // 7. Advanced Site-Wide Search with lunr.js
  // Check if lunr.js is loaded and search index exists
  if (typeof lunr !== 'undefined') {
    let searchIndex = null;
    let searchData = [];
    
    // Load search index
    fetch('/js/search-index.json')
      .then((response) => {
        if (!response.ok) throw new Error('Search index not found');
        return response.json();
      })
      .then((data) => {
        searchData = data;
        
        // Build lunr index
        searchIndex = lunr(function () {
          this.ref('id');
          this.field('title', { boost: 10 });
          this.field('content_clean');
          this.field('excerpt', { boost: 5 });
          this.field('tag', { boost: 3 });
          this.field('category_name', { boost: 2 });
          this.metadataWhitelist = ['position'];
          
          data.forEach((doc) => {
            this.add(doc);
          });
        });
        
        // Set up search form if it exists
        const searchForm = document.getElementById('site-search-form');
        const searchField = document.getElementById('site-search-input');
        const searchResults = document.getElementById('search-results');
        
        if (searchForm && searchField) {
          searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            performSearch(searchField.value);
          });
          
          searchField.addEventListener('input', (e) => {
            if (e.target.value.length >= 2) {
              performSearch(e.target.value);
            } else if (searchResults) {
              searchResults.innerHTML = '';
              searchResults.style.display = 'none';
            }
          });
        }
        
        function performSearch(query) {
          if (!query || query.length < 2) {
            if (searchResults) {
              searchResults.innerHTML = '';
              searchResults.style.display = 'none';
            }
            return;
          }
          
          const results = searchIndex.search(query);
          
          if (searchResults) {
            if (results.length === 0) {
              searchResults.innerHTML = '<p class="p-4 text-slate-400 text-sm">No results found.</p>';
              searchResults.style.display = 'block';
            } else {
              const html = results
                .map((result) => {
                  const doc = searchData.find((d) => d.id === result.ref);
                  if (!doc) return '';
                  
                  return `
                    <a href="${doc.url}" class="block p-3 border-b border-slate-800 hover:bg-slate-900/50 transition-colors">
                      <div class="font-display font-semibold text-slate-200 text-sm mb-1">${doc.title}</div>
                      <div class="text-xs text-slate-400 font-mono mb-1">${doc.category_name} &bull; ${doc.date || ''}</div>
                      <p class="text-sm text-slate-400 line-clamp-2">${doc.excerpt || ''}</p>
                    </a>
                  `;
                })
                .join('');
              
              searchResults.innerHTML = html;
              searchResults.style.display = 'block';
            }
          }
        }
        
        // Global search function for programmatic access
        window.performSiteSearch = performSearch;
      })
      .catch((err) => {
        console.warn('[SEARCH] Could not load search index:', err.message);
      });
  }
});
