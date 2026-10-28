// TurboWeb / Web48 - Core Interactive Logic

document.addEventListener('DOMContentLoaded', () => {
  initSavingsCalculator();
  initPortfolioModal();
  initHeroPreviewSwitcher(); // Новая функция
  initContactForm();
  initMobileMenu();
});

// 1. Savings Calculator (Tilda vs TurboWeb)
function initSavingsCalculator() {
  const yearsSlider = document.getElementById('calc-years');
  const yearsVal = document.getElementById('calc-years-val');
  const tildaCostEl = document.getElementById('calc-tilda-cost');
  const turbowebCostEl = document.getElementById('calc-turboweb-cost');
  const savedAmountEl = document.getElementById('calc-saved-amount');

  if (!yearsSlider) return;

  const updateCalc = () => {
    const years = parseInt(yearsSlider.value, 10);
    yearsVal.textContent = `${years} ${getPluralYears(years)}`;

    const tildaTotal = 45000 + (years * 9600);
    const turbowebTotal = 14900 + (years * 300);
    const saved = tildaTotal - turbowebTotal;

    tildaCostEl.textContent = `${tildaTotal.toLocaleString('ru-RU')} ₽`;
    turbowebCostEl.textContent = `${turbowebTotal.toLocaleString('ru-RU')} ₽`;
    savedAmountEl.textContent = `${saved.toLocaleString('ru-RU')} ₽`;
  };

  yearsSlider.addEventListener('input', updateCalc);
  updateCalc();
}

function getPluralYears(n) {
  if (n === 1) return 'год';
  if (n >= 2 && n <= 4) return 'года';
  return 'лет';
}

// 2. Portfolio Showcase
const portfolioData = {
  detailing: { title: 'AvtoGloss Detailing', niche: 'Автобизнес' },
  renovation: { title: 'СтройКомфорт', niche: 'Ремонт' },
  barbershop: { title: 'Blade & Craft', niche: 'Услуги' },
  legal: { title: 'ЮристЭксперт', niche: 'Юристы' }
};

function initPortfolioModal() {
  const dialog = document.getElementById('portfolio-dialog');
  const closeBtn = document.getElementById('dialog-close-btn');

  if (!dialog) return;

  document.querySelectorAll('.open-demo-btn').forEach(button => {
    button.addEventListener('click', () => {
      dialog.showModal();
    });
  });

  closeBtn?.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (e) => {
    if (e.target === dialog) dialog.close();
  });
}

// New: Hero Preview Switcher
function initHeroPreviewSwitcher() {
  const container = document.getElementById('hero-preview-container');
  const buttons = document.querySelectorAll('.hero-preview-btn');

  if (!container || buttons.length === 0) return;

  const previews = {
    coffee: '<div class="h-full flex items-center justify-center bg-amber-50 text-amber-800 font-bold">Макет: Кофейня (Уютный дизайн)</div>',
    auto: '<div class="h-full flex items-center justify-center bg-blue-50 text-blue-800 font-bold">Макет: Автосервис (Строгий дизайн)</div>',
    master: '<div class="h-full flex items-center justify-center bg-emerald-50 text-emerald-800 font-bold">Макет: Мастер (Портфолио)</div>'
  };

  buttons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      buttons.forEach(b => b.classList.remove('bg-[#2563EB]', 'text-white'));
      btn.classList.add('bg-[#2563EB]', 'text-white');
      container.innerHTML = previews[btn.dataset.preview];
    });
  });
}

// 4. Contact Form with Validation
function initContactForm() {
  const form = document.getElementById('contact-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!form.checkValidity()) return;

    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Отправка...';

    setTimeout(() => {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Получить бесплатный MVP за 24 часа';
      showNotificationSuccess('Заявка успешно отправлена! Скоро свяжемся.');
      form.reset();
    }, 900);
  });
}

function showNotificationSuccess(message) {
  alert(message); // Упрощено для MVP
}

function initMobileMenu() {
  // Simple implementation
}
