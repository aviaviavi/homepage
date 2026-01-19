(() => {
  const storageKey = 'avi.press.theme';
  const modes = ['system', 'light', 'dark'];

  const getSavedMode = () => {
    const saved = window.localStorage.getItem(storageKey);
    return modes.includes(saved) ? saved : 'system';
  };

  const applyMode = (mode) => {
    const root = document.documentElement;

    if (mode === 'system') {
      root.removeAttribute('data-theme');
    } else {
      root.setAttribute('data-theme', mode);
    }

    const btn = document.getElementById('theme-toggle');
    if (btn) {
      const label = mode === 'system' ? 'System' : mode[0].toUpperCase() + mode.slice(1);
      btn.textContent = `Theme: ${label}`;
      btn.setAttribute('aria-label', `Theme: ${label}`);
    }
  };

  const cycleMode = () => {
    const current = getSavedMode();
    const next = modes[(modes.indexOf(current) + 1) % modes.length];
    window.localStorage.setItem(storageKey, next);
    applyMode(next);
  };

  const init = () => {
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.addEventListener('click', cycleMode);
    applyMode(getSavedMode());
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
