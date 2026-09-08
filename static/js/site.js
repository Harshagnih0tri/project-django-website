'use strict';

// Mobile slide-in menu — trimmed from the Anon template's script.js,
// with null-guards since this build drops the template's newsletter
// modal / fake purchase toast / mega-menu accordion.
(function () {
  const openBtns = document.querySelectorAll('[data-mobile-menu-open-btn]');
  const menu = document.querySelector('[data-mobile-menu]');
  const closeBtn = document.querySelector('[data-mobile-menu-close-btn]');
  const overlay = document.querySelector('[data-overlay]');

  if (!menu || !overlay) return;

  const closeMenu = function () {
    menu.classList.remove('active');
    overlay.classList.remove('active');
  };

  openBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      menu.classList.add('active');
      overlay.classList.add('active');
    });
  });

  if (closeBtn) closeBtn.addEventListener('click', closeMenu);
  overlay.addEventListener('click', closeMenu);
})();

// Account dropdown in the header (click to toggle, click outside to close).
(function () {
  const menu = document.querySelector('.user-menu');
  if (!menu) return;
  const btn = menu.querySelector('.action-btn');

  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    menu.classList.toggle('open');
  });

  document.addEventListener('click', function () {
    menu.classList.remove('open');
  });
})();
