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
    btn.setAttribute('aria-label', isDark ? 'Comută la Modul Luminos' : 'Comută la Modul Întunecat');
    btn.setAttribute('title', isDark ? 'Activează Modul Luminos (Light)' : 'Activează Modul Întunecat (Dark)');
    const icon = btn.querySelector('.theme-toggle-icon');
    if (icon) {
      if (isDark) {
        icon.className = 'theme-toggle-icon ph-bold ph-sun text-amber-400 text-base';
      } else {
        icon.className = 'theme-toggle-icon ph-bold ph-moon text-indigo-600 text-base';
      }
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
    btn.className = 'copy-btn absolute top-2 right-2 px-2 py-1 rounded bg-slate-800/80 border border-slate-700 text-[10px] font-mono text-slate-400 hover:text-emerald-400 hover:border-emerald-500/40 transition-all opacity-0 group-hover:opacity-100';
    btn.innerHTML = '<i class="ph-bold ph-copy"></i> COPY';

    preBlock.classList.add('group', 'relative');
    preBlock.appendChild(btn);

    btn.addEventListener('click', async () => {
      const code = preBlock.querySelector('code') || preBlock;
      const text = code.innerText.replace(/COPY$/, '').trim();
      try {
        await navigator.clipboard.writeText(text);
        btn.innerHTML = '<i class="ph-bold ph-check text-emerald-400"></i> COPIED';
        btn.classList.add('text-emerald-400', 'border-emerald-500/50');
        setTimeout(() => {
          btn.innerHTML = '<i class="ph-bold ph-copy"></i> COPY';
          btn.classList.remove('text-emerald-400', 'border-emerald-500/50');
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
});
