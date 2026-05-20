// components.js - small glue file for HealthSphere UI components
console.log('components.js loaded');

// Re-use functions from base.js if present
if (window.HealthSphere) {
  console.log('HealthSphere utilities available');
}

// Minimal DOM helpers used by some templates
window.UIHelpers = {
  toggleClass: function(el, cls) { if (el) el.classList.toggle(cls); },
  showToast: function(message) { console.log('Toast:', message); }
};
