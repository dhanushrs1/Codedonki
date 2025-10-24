/* Global alerts utility and browser alert() override */
(function () {
  const CONTAINER_ID = 'global-alert-container';

  function ensureContainer() {
    let container = document.getElementById(CONTAINER_ID);
    if (!container) {
      container = document.createElement('div');
      container.id = CONTAINER_ID;
      document.body.appendChild(container);
    }
    return container;
  }

  function getIconHtml(type) {
    switch (type) {
      case 'success': return '<i class="fas fa-check"></i>';
      case 'error':   return '<i class="fas fa-exclamation"></i>';
      case 'warning': return '<i class="fas fa-exclamation-triangle"></i>';
      default:        return '<i class="fas fa-info"></i>';
    }
  }

  function removeAlertWithAnimation(alertEl) {
    try {
      alertEl.style.animation = 'slideOut 220ms ease-out forwards';
    } catch (e) { /* no-op */ }
    setTimeout(() => alertEl.remove(), 240);
  }

  function showAlert(message, options) {
    const opts = Object.assign({ type: 'info', duration: 4000, dismissible: true }, options);
    const container = ensureContainer();

    const wrapper = document.createElement('div');
    wrapper.className = `alert-popup ${opts.type} show`;
    wrapper.setAttribute('role', 'status');
    wrapper.setAttribute('aria-live', 'polite');

    const icon = document.createElement('div');
    icon.className = 'alert-icon';
    icon.innerHTML = getIconHtml(opts.type);

    const content = document.createElement('div');
    content.className = 'alert-content';

    const text = document.createElement('div');
    text.className = 'alert-message';
    text.textContent = String(message || '');

    content.appendChild(text);

    wrapper.appendChild(icon);
    wrapper.appendChild(content);

    if (opts.dismissible) {
      const closeBtn = document.createElement('button');
      closeBtn.className = 'alert-close';
      closeBtn.setAttribute('aria-label', 'Close alert');
      closeBtn.innerHTML = '<i class="fas fa-times"></i>';
      closeBtn.addEventListener('click', () => removeAlertWithAnimation(wrapper));
      wrapper.appendChild(closeBtn);
    }

    container.appendChild(wrapper);

    if (opts.duration && Number.isFinite(opts.duration) && opts.duration > 0) {
      setTimeout(() => {
        if (wrapper.isConnected) removeAlertWithAnimation(wrapper);
      }, opts.duration);
    }

    return wrapper;
  }

  // Expose globally
  window.showAlert = showAlert;

  // Override default browser alert with non-blocking custom alert
  window.alert = function (msg) {
    try {
      showAlert(String(msg), { type: 'info' });
    } catch (e) {
      // Fallback silently if anything goes wrong
      console && console.warn && console.warn('Custom alert failed, falling back to native alert');
      return (window.__nativeAlert || window.prompt || function () {})(String(msg));
    }
  };
})();


