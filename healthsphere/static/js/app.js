// app.js - application bootstrap for HealthSphere
console.log('app.js loaded');

// Provide a safe global HealthSphereApp with an init() hook so templates
// that call HealthSphereApp.init() won't throw when a richer app
// implementation is not present (development placeholders).
window.HealthSphereApp = window.HealthSphereApp || {
  init: function() {
    // Initialize lightweight behaviors if available
    try {
      if (typeof initSidebar === 'function') initSidebar();
      if (typeof initAlerts === 'function') initAlerts();
      if (typeof initFormValidation === 'function') initFormValidation();
      console.log('HealthSphereApp.init() executed');
    } catch (e) {
      console.warn('HealthSphereApp.init error:', e);
    }
  }
};

document.addEventListener('DOMContentLoaded', function() {
  try { window.HealthSphereApp.init(); } catch (e) { console.warn(e); }
});
