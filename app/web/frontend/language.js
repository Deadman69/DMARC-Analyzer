let currentLang = 'en'; // or 'fr', or read from localStorage

async function loadTranslations(lang) {
  const res = await fetch(`/locales/${lang}.json`);
  const dict = await res.json();
  applyTranslations(dict);
}

function applyTranslations(dict) {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) {
      el.textContent = dict[key];
    }
  });
}

document.getElementById('langSelector').addEventListener('change', (e) => {
    currentLang = e.target.value;
    loadTranslations(currentLang);
    localStorage.setItem('lang', currentLang);
  });
  

document.addEventListener('DOMContentLoaded', () => {
    currentLang = localStorage.getItem('lang') || 'en';
    loadTranslations(currentLang);
  });
  