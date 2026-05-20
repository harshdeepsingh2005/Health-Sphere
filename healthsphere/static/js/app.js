/**
 * HealthSphere AI - Application Bootstrap
 * ========================================
 * Handles topbar widget interactions: notification bell,
 * user menu dropdown, and click-outside-to-close logic.
 */

// ──────────────────────────────────────────────
// Utility: toggle a dropdown panel
// ──────────────────────────────────────────────
function openPanel(panel, trigger) {
  panel.hidden = false;
  trigger.setAttribute('aria-expanded', 'true');
  // re-trigger the CSS animation each open
  panel.style.animation = 'none';
  requestAnimationFrame(() => {
    panel.style.animation = '';
  });
}

function closePanel(panel, trigger) {
  panel.hidden = true;
  trigger.setAttribute('aria-expanded', 'false');
}

function togglePanel(panel, trigger, otherPanels) {
  const isOpen = !panel.hidden;
  // close any sibling panels first
  if (otherPanels) {
    otherPanels.forEach(({ p, t }) => { if (p && t) closePanel(p, t); });
  }
  if (isOpen) {
    closePanel(panel, trigger);
  } else {
    openPanel(panel, trigger);
  }
}

// ──────────────────────────────────────────────
// Notification Bell
// ──────────────────────────────────────────────
function initNotifBell() {
  const btn = document.getElementById('notif-btn');
  const panel = document.getElementById('notif-panel');
  const badge = document.getElementById('notif-badge');
  const markAllBtn = document.getElementById('notif-mark-all');
  if (!btn || !panel) return;

  // toggle on bell click
  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    const userPanel = document.getElementById('user-menu-panel');
    const userTrigger = document.getElementById('user-menu-btn');
    togglePanel(panel, btn, userPanel && userTrigger ? [{ p: userPanel, t: userTrigger }] : []);
  });

  // "Mark all read" — hide badge and fade urgent styling
  if (markAllBtn) {
    markAllBtn.addEventListener('click', () => {
      document.querySelectorAll('.notif-item--urgent').forEach(el => {
        el.classList.remove('notif-item--urgent');
      });
      if (badge) badge.hidden = true;
      markAllBtn.textContent = 'All read';
      markAllBtn.disabled = true;
    });
  }

  // dismiss individual notification items
  document.addEventListener('click', (e) => {
    const closeBtn = e.target.closest('.notif-item__close');
    if (!closeBtn) return;
    const item = closeBtn.closest('.notif-item');
    if (!item) return;
    e.stopPropagation();
    item.style.transition = 'opacity 0.2s, transform 0.2s';
    item.style.opacity = '0';
    item.style.transform = 'translateX(10px)';
    setTimeout(() => {
      item.remove();
      // update badge count
      const remaining = document.querySelectorAll('.notif-item').length;
      if (badge) {
        badge.textContent = remaining;
        if (remaining === 0) badge.hidden = true;
      }
    }, 200);
  });
}

// ──────────────────────────────────────────────
// User Menu
// ──────────────────────────────────────────────
function initUserMenu() {
  const btn = document.getElementById('user-menu-btn');
  const panel = document.getElementById('user-menu-panel');
  if (!btn || !panel) return;

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    const notifPanel = document.getElementById('notif-panel');
    const notifTrigger = document.getElementById('notif-btn');
    togglePanel(panel, btn, notifPanel && notifTrigger ? [{ p: notifPanel, t: notifTrigger }] : []);
  });

  // close on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (!panel.hidden) closePanel(panel, btn);
      const notifPanel = document.getElementById('notif-panel');
      const notifTrigger = document.getElementById('notif-btn');
      if (notifPanel && !notifPanel.hidden) closePanel(notifPanel, notifTrigger);
    }
  });
}

// ──────────────────────────────────────────────
// Click-outside-to-close
// ──────────────────────────────────────────────
function initClickOutside() {
  document.addEventListener('click', () => {
    const panels = [
      { p: document.getElementById('notif-panel'), t: document.getElementById('notif-btn') },
      { p: document.getElementById('user-menu-panel'), t: document.getElementById('user-menu-btn') },
    ];
    panels.forEach(({ p, t }) => {
      if (p && t && !p.hidden) closePanel(p, t);
    });
  });

  // stop clicks inside a panel from bubbling up and closing it
  ['notif-wrapper', 'user-menu-wrapper'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('click', e => e.stopPropagation());
  });
}

// ──────────────────────────────────────────────
// HealthSphereApp global
// ──────────────────────────────────────────────
window.HealthSphereApp = window.HealthSphereApp || {
  _initialized: false,
  init() {
    if (this._initialized) return;   // guard: only ever run once
    this._initialized = true;
    try {
      initNotifBell();
      initUserMenu();
      initClickOutside();
      if (typeof initSidebar === 'function') initSidebar();
      if (typeof initAlerts === 'function') initAlerts();
      console.log('HealthSphereApp.init() ✓');
    } catch (e) {
      console.warn('HealthSphereApp.init error:', e);
    }
  }
};

// Safety-net: fire init if the inline base.html script hasn't already.
// The _initialized guard above ensures listeners are never doubled.
document.addEventListener('DOMContentLoaded', () => {
  try { window.HealthSphereApp.init(); } catch (e) { console.warn(e); }
});
