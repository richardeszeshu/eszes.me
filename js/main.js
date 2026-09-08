(function () {
  'use strict';

  var themeToggleBtn = document.getElementById('theme-toggle');
  var sunIcon = document.getElementById('sun-icon');
  var moonIcon = document.getElementById('moon-icon');

  function getPreferredTheme() {
    var saved = localStorage.getItem('site-theme');
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    var isDark = theme === 'dark';
    document.documentElement.classList.toggle('dark', isDark);

    if (sunIcon && moonIcon) {
      if (isDark) {
        sunIcon.classList.remove('hidden');
        moonIcon.classList.add('hidden');
      } else {
        sunIcon.classList.add('hidden');
        moonIcon.classList.remove('hidden');
      }
    }

    if (themeToggleBtn) {
      themeToggleBtn.setAttribute('aria-label', isDark ? 'Switch to light theme' : 'Switch to dark theme');
    }
  }

  applyTheme(getPreferredTheme());

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function () {
      var isDark = document.documentElement.classList.contains('dark');
      var nextTheme = isDark ? 'light' : 'dark';
      localStorage.setItem('site-theme', nextTheme);
      applyTheme(nextTheme);
    });
  }

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
    if (!localStorage.getItem('site-theme')) {
      applyTheme(e.matches ? 'dark' : 'light');
    }
  });

  var langHuBtn = document.getElementById('lang-btn-hu');
  var langEnBtn = document.getElementById('lang-btn-en');

  function getPreferredLanguage() {
    var saved = localStorage.getItem('site-lang');
    if (saved) return saved;
    var browserLang = (navigator.language || navigator.userLanguage || '').toLowerCase();
    return browserLang.startsWith('hu') ? 'hu' : 'en';
  }

  function updateCvDownloadLinks(lang) {
    var filename = lang === 'hu' ? 'Richard_Eszes_Software_Developer_CV_HU.pdf' : 'Richard_Eszes_Software_Developer_CV_EN.pdf';
    var path = 'assets/cv/' + filename;
    document.querySelectorAll('.cv-download-btn').forEach(function (btn) {
      btn.setAttribute('href', path);
      btn.setAttribute('download', filename);
    });
  }

  function applyLanguage(lang) {
    document.documentElement.setAttribute('data-lang', lang);
    document.documentElement.setAttribute('lang', lang);

    var activeClasses = ['bg-white', 'text-zinc-900', 'shadow-sm', 'dark:bg-zinc-800', 'dark:text-zinc-100'];
    var inactiveClasses = ['text-zinc-500', 'hover:text-zinc-900', 'dark:text-zinc-400', 'dark:hover:text-zinc-100'];

    if (langHuBtn && langEnBtn) {
      if (lang === 'hu') {
        langHuBtn.classList.add.apply(langHuBtn.classList, activeClasses);
        langHuBtn.classList.remove.apply(langHuBtn.classList, inactiveClasses);
        langEnBtn.classList.remove.apply(langEnBtn.classList, activeClasses);
        langEnBtn.classList.add.apply(langEnBtn.classList, inactiveClasses);
      } else {
        langEnBtn.classList.add.apply(langEnBtn.classList, activeClasses);
        langEnBtn.classList.remove.apply(langEnBtn.classList, inactiveClasses);
        langHuBtn.classList.remove.apply(langHuBtn.classList, activeClasses);
        langHuBtn.classList.add.apply(langHuBtn.classList, inactiveClasses);
      }
    }

    updateCvDownloadLinks(lang);
  }

  applyLanguage(getPreferredLanguage());

  if (langHuBtn) {
    langHuBtn.addEventListener('click', function () {
      localStorage.setItem('site-lang', 'hu');
      applyLanguage('hu');
    });
  }

  if (langEnBtn) {
    langEnBtn.addEventListener('click', function () {
      localStorage.setItem('site-lang', 'en');
      applyLanguage('en');
    });
  }

  var mobileToggleBtn = document.getElementById('mobile-toggle');
  var mobileNav = document.getElementById('mobile-nav');

  if (mobileToggleBtn && mobileNav) {
    mobileToggleBtn.addEventListener('click', function () {
      var isHidden = mobileNav.classList.toggle('hidden');
      mobileToggleBtn.setAttribute('aria-expanded', (!isHidden).toString());
    });

    mobileNav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        mobileNav.classList.add('hidden');
        mobileToggleBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  function setupProtectedEmails() {
    var emailLinks = document.querySelectorAll('.email-link');
    emailLinks.forEach(function (el) {
      var user = el.getAttribute('data-u');
      var domain = el.getAttribute('data-d');
      if (user && domain) {
        var email = user + '@' + domain;
        el.setAttribute('href', 'mailto:' + email);
        var textNode = el.querySelector('.email-text');
        if (textNode) {
          textNode.textContent = email;
        }
      }
    });
  }
  setupProtectedEmails();

  var copyEmailBtn = document.getElementById('copy-email-btn');
  var copyFeedback = document.getElementById('copy-feedback');

  if (copyEmailBtn && copyFeedback) {
    copyEmailBtn.addEventListener('click', function () {
      var email = ['richard', 'eszes.me'].join('@');
      navigator.clipboard.writeText(email).then(function () {
        var currentLang = document.documentElement.getAttribute('data-lang') || 'hu';
        copyFeedback.textContent = currentLang === 'hu' ? 'Másolva!' : 'Copied!';
        copyFeedback.classList.remove('opacity-0');
        setTimeout(function () {
          copyFeedback.classList.add('opacity-0');
        }, 2000);
      });
    });
  }
})();
