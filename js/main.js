/**
 * vCard Portfolio Interactive Scripts - Scrolling Flow & Floating Menu
 * Eszes Richárd (eszes.me)
 */

(function () {
  'use strict';

  // ==========================================================================
  // 1. Navigation Menu Drawers (Static Header & Floating Button)
  // ==========================================================================
  const menuBtn = document.getElementById('menu-circle-btn');
  const navDrawer = document.getElementById('nav-drawer');

  const floatingMenuWrapper = document.getElementById('floating-menu-wrapper');
  const floatingMenuBtn = document.getElementById('floating-menu-btn');
  const floatingNavDrawer = document.getElementById('floating-nav-drawer');

  // Static top menu
  if (menuBtn && navDrawer) {
    menuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      navDrawer.classList.toggle('open');
    });

    navDrawer.querySelectorAll('.nav-drawer-link').forEach(link => {
      link.addEventListener('click', () => {
        navDrawer.classList.remove('open');
      });
    });
  }

  // Floating menu
  if (floatingMenuBtn && floatingNavDrawer) {
    floatingMenuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      floatingNavDrawer.classList.toggle('open');
    });

    floatingNavDrawer.querySelectorAll('.nav-drawer-link').forEach(link => {
      link.addEventListener('click', () => {
        floatingNavDrawer.classList.remove('open');
      });
    });
  }

  // Close menus when clicking outside
  document.addEventListener('click', (e) => {
    if (navDrawer && !navDrawer.contains(e.target) && e.target !== menuBtn) {
      navDrawer.classList.remove('open');
    }
    if (floatingNavDrawer && !floatingNavDrawer.contains(e.target) && e.target !== floatingMenuBtn) {
      floatingNavDrawer.classList.remove('open');
    }
  });

  // ==========================================================================
  // 2. Floating Menu Button Positioning on Scroll
  //    (Appears when top bar scrolls out of view, half overlapping the content card)
  // ==========================================================================
  function updateFloatingMenuPosition() {
    if (!floatingMenuWrapper) return;

    const mainWrapper = document.querySelector('.main-wrapper');
    const topBar = document.querySelector('.main-top-bar');
    if (!mainWrapper || !topBar) return;

    const topBarRect = topBar.getBoundingClientRect();
    const isPastTopBar = topBarRect.bottom < 0;

    if (isPastTopBar) {
      const mainRect = mainWrapper.getBoundingClientRect();
      // Button width is 44px; center it on the right edge so it half overlaps into the card (right - 22px)
      const targetLeft = Math.min(window.innerWidth - 56, Math.max(16, mainRect.right - 22));
      floatingMenuWrapper.style.left = `${targetLeft}px`;
      floatingMenuWrapper.classList.add('visible');
    } else {
      floatingMenuWrapper.classList.remove('visible');
      if (floatingNavDrawer) {
        floatingNavDrawer.classList.remove('open');
      }
    }
  }

  window.addEventListener('scroll', updateFloatingMenuPosition, { passive: true });
  window.addEventListener('resize', updateFloatingMenuPosition);
  updateFloatingMenuPosition();

  // ==========================================================================
  // 3. Mobile Sidebar Toggle ("Kapcsolatok" / "Contacts")
  // ==========================================================================
  const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
  const sidebarCollapsible = document.getElementById('sidebar-collapsible');

  if (sidebarToggleBtn && sidebarCollapsible) {
    sidebarToggleBtn.addEventListener('click', () => {
      const isOpen = sidebarCollapsible.classList.toggle('show');
      sidebarToggleBtn.classList.toggle('active', isOpen);
    });
  }

  // ==========================================================================
  // 4. Language Switcher (HU / EN)
  // ==========================================================================
  const langHuBtn = document.getElementById('lang-btn-hu');
  const langEnBtn = document.getElementById('lang-btn-en');

  function getPreferredLanguage() {
    const saved = localStorage.getItem('site-lang');
    if (saved) return saved;
    const browserLang = (navigator.language || navigator.userLanguage || '').toLowerCase();
    return browserLang.startsWith('hu') ? 'hu' : 'en';
  }

  function updateCvLinks(lang) {
    const filename = lang === 'hu' ? 'Richard_Eszes_Software_Developer_CV_HU.pdf' : 'Richard_Eszes_Software_Developer_CV_EN.pdf';
    const path = `assets/cv/${filename}`;
    document.querySelectorAll('.cv-download-btn').forEach(btn => {
      btn.setAttribute('href', path);
      btn.setAttribute('download', filename);
    });
  }

  function applyLanguage(lang) {
    document.documentElement.setAttribute('data-lang', lang);
    document.documentElement.setAttribute('lang', lang);

    if (langHuBtn && langEnBtn) {
      langHuBtn.classList.toggle('active', lang === 'hu');
      langEnBtn.classList.toggle('active', lang === 'en');
    }

    updateCvLinks(lang);
  }

  applyLanguage(getPreferredLanguage());

  if (langHuBtn) {
    langHuBtn.addEventListener('click', () => {
      localStorage.setItem('site-lang', 'hu');
      applyLanguage('hu');
    });
  }

  if (langEnBtn) {
    langEnBtn.addEventListener('click', () => {
      localStorage.setItem('site-lang', 'en');
      applyLanguage('en');
    });
  }

  // ==========================================================================
  // 5. Theme Switcher (Dark / Light)
  // ==========================================================================
  const themeToggleBtn = document.getElementById('theme-toggle');
  const sunIcon = document.getElementById('sun-icon');
  const moonIcon = document.getElementById('moon-icon');

  function getPreferredTheme() {
    const saved = localStorage.getItem('site-theme');
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    const isDark = theme === 'dark';
    document.documentElement.classList.toggle('dark', isDark);

    if (sunIcon && moonIcon) {
      sunIcon.style.display = isDark ? 'block' : 'none';
      moonIcon.style.display = isDark ? 'none' : 'block';
    }

    if (themeToggleBtn) {
      themeToggleBtn.setAttribute('aria-label', isDark ? 'Switch to light theme' : 'Switch to dark theme');
    }
  }

  applyTheme(getPreferredTheme());

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const isDark = document.documentElement.classList.contains('dark');
      const nextTheme = isDark ? 'light' : 'dark';
      localStorage.setItem('site-theme', nextTheme);
      applyTheme(nextTheme);
    });
  }

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    if (!localStorage.getItem('site-theme')) {
      applyTheme(e.matches ? 'dark' : 'light');
    }
  });

  // ==========================================================================
  // 6. Toast Notification Utility
  // ==========================================================================
  const toast = document.getElementById('toast-notice');

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2500);
  }

  // ==========================================================================
  // 7. Protected Email & Copy to Clipboard
  // ==========================================================================
  function setupProtectedEmails() {
    const emailLinks = document.querySelectorAll('.email-link');
    emailLinks.forEach(el => {
      const user = el.getAttribute('data-u');
      const domain = el.getAttribute('data-d');
      if (user && domain) {
        const email = `${user}@${domain}`;
        el.setAttribute('href', `mailto:${email}`);
        const textNode = el.querySelector('.email-text');
        if (textNode) {
          textNode.textContent = email;
        }
      }
    });
  }
  setupProtectedEmails();

  const copyEmailBtns = document.querySelectorAll('.copy-email-btn');
  copyEmailBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const email = ['richard', 'eszes.me'].join('@');
      navigator.clipboard.writeText(email).then(() => {
        const currentLang = document.documentElement.getAttribute('data-lang') || 'hu';
        showToast(currentLang === 'hu' ? 'E-mail cím másolva!' : 'Email copied to clipboard!');
      });
    });
  });

  // ==========================================================================
  // 8. Contact Form Action
  // ==========================================================================
  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = document.getElementById('form-name')?.value || '';
      const email = document.getElementById('form-email')?.value || '';
      const message = document.getElementById('form-message')?.value || '';

      const subject = encodeURIComponent(`Megkeresés eszes.me-ről: ${name}`);
      const body = encodeURIComponent(`Név: ${name}\nE-mail: ${email}\n\nÜzenet:\n${message}`);

      window.location.href = `mailto:richard@eszes.me?subject=${subject}&body=${body}`;

      const currentLang = document.documentElement.getAttribute('data-lang') || 'hu';
      showToast(currentLang === 'hu' ? 'Levelező megnyitása...' : 'Opening email client...');
    });
  }

})();
