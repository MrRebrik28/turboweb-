// TurboWeb / Web48 - Core Interactive Logic

document.addEventListener('DOMContentLoaded', () => {
  initSavingsCalculator();
  initPortfolioModal();
  initQuiz();
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

    // Tilda: ~9 000 руб/год подписка + базовая разработка в студии от 40 000 руб
    const tildaTotal = 45000 + (years * 9600);
    // TurboWeb: 14 900 руб разово + 0 руб хостинг (только домен ~300 руб/год)
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

// 2. Portfolio Showcase & Interactive Preview Modal
const portfolioData = {
  detailing: {
    title: '«AvtoGloss» — Детейлинг & Защитные пленки',
    niche: 'Автобизнес',
    result: 'Конверсия 7.4%, 18 заявок в первую неделю',
    speed: '0.38 сек',
    demoHtml: `
      <div class="p-6 bg-slate-900 text-slate-100 rounded-2xl">
        <div class="flex justify-between items-center border-b border-slate-800 pb-4 mb-4">
          <span class="font-bold text-emerald-400 text-lg">AvtoGloss Detailing</span>
          <a href="#" class="px-3 py-1 bg-emerald-500 text-slate-950 font-bold rounded-lg text-xs">+7 (999) 000-11-22</a>
        </div>
        <div class="my-6 text-center">
          <span class="px-3 py-1 bg-emerald-500/10 text-emerald-400 text-xs rounded-full uppercase tracking-wider font-semibold">Сезонная акция</span>
          <h3 class="text-2xl font-black mt-3 mb-2">Бронирование кузова полиуретаном в Москве</h3>
          <p class="text-slate-400 text-sm">Гарантия 5 лет. Премиальные пленки SunTek и Stek. Скидка 15% до конца недели.</p>
        </div>
        <div class="grid grid-cols-2 gap-3 mb-6">
          <div class="p-3 bg-slate-800/60 rounded-xl border border-slate-700/50 text-center">
            <div class="text-emerald-400 font-bold text-lg">от 18 000 ₽</div>
            <div class="text-xs text-slate-400">Оклейка передней части</div>
          </div>
          <div class="p-3 bg-slate-800/60 rounded-xl border border-slate-700/50 text-center">
            <div class="text-emerald-400 font-bold text-lg">от 9 500 ₽</div>
            <div class="text-xs text-slate-400">Керамика в 2 слоя</div>
          </div>
        </div>
        <div class="bg-slate-800/40 p-4 rounded-xl border border-slate-700/40">
          <label class="block text-xs font-semibold text-slate-300 mb-1">Марка авто и телефон для расчета:</label>
          <div class="flex gap-2">
            <input type="text" placeholder="BMW X5 / +7 999..." class="w-full text-xs bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white">
            <button class="bg-emerald-500 text-slate-950 px-4 py-2 text-xs font-bold rounded-lg whitespace-nowrap">Узнать цену</button>
          </div>
        </div>
      </div>
    `
  },
  renovation: {
    title: '«СтройКомфорт» — Ремонт квартир под ключ',
    niche: 'Строительство и Ремонт',
    result: 'Снижение стоимости заявки с 2400 ₽ до 850 ₽',
    speed: '0.41 сек',
    demoHtml: `
      <div class="p-6 bg-slate-900 text-slate-100 rounded-2xl">
        <div class="flex justify-between items-center border-b border-slate-800 pb-4 mb-4">
          <span class="font-bold text-amber-400 text-lg">СтройКомфорт</span>
          <span class="text-xs text-slate-400">Работаем по договору</span>
        </div>
        <div class="my-6">
          <h3 class="text-2xl font-black mb-2">Капитальный ремонт квартир в новостройках без предоплаты</h3>
          <p class="text-slate-400 text-sm">Фиксированная смета. Оплата поэтапно. Страховка объекта на 5 000 000 ₽ в подарок.</p>
        </div>
        <div class="bg-amber-400/10 border border-amber-400/20 p-4 rounded-xl mb-4">
          <div class="font-bold text-sm text-amber-300">Калькулятор предварительной сметы:</div>
          <div class="text-xs text-slate-400 mt-1">1-комнатная квартира (42 м²) = от 380 000 ₽ (срок 35 дней)</div>
        </div>
        <button class="w-full py-3 bg-amber-400 text-slate-950 font-bold rounded-xl text-sm">Получить смету с выездом замерщика (0 ₽)</button>
      </div>
    `
  },
  barbershop: {
    title: '«Blade & Craft» — Сеть мужских парикмахерских',
    niche: 'Красота и Услуги',
    result: '82% онлайн-записей через мобильную версию',
    speed: '0.35 сек',
    demoHtml: `
      <div class="p-6 bg-slate-900 text-slate-100 rounded-2xl">
        <div class="text-center pb-4 border-b border-slate-800">
          <h4 class="font-extrabold text-xl tracking-wider uppercase text-rose-400">Blade & Craft</h4>
          <p class="text-xs text-slate-400">Classic Barbershop</p>
        </div>
        <div class="py-6 text-center">
          <h3 class="text-xl font-bold mb-2">Мужские стрижки и моделирование бороды</h3>
          <p class="text-xs text-slate-400 mb-4">Скидка 20% на первый визит к топ-барберу</p>
          <div class="flex justify-center gap-2">
            <button class="px-5 py-2.5 bg-rose-500 text-white font-bold rounded-xl text-xs">Записаться онлайн</button>
            <button class="px-4 py-2.5 bg-slate-800 text-slate-300 rounded-xl text-xs">Прайс-лист</button>
          </div>
        </div>
      </div>
    `
  },
  legal: {
    title: '«ЮристЭксперт» — Банкротство и защита активов',
    niche: 'Юридические услуги',
    result: 'Конверсия 9.1% за счет калькулятора долгов',
    speed: '0.40 сек',
    demoHtml: `
      <div class="p-6 bg-slate-900 text-slate-100 rounded-2xl">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3 mb-4">
          <span class="font-bold text-sky-400">ЮристЭксперт</span>
          <span class="text-xs text-slate-400">ФЗ-127</span>
        </div>
        <h3 class="text-xl font-bold mb-2">Законное списание долгов и кредитов с гарантией в договоре</h3>
        <p class="text-slate-400 text-xs mb-4">Если не спишем долг — вернем 100% средств по договору.</p>
        <div class="p-3 bg-slate-800 rounded-lg text-xs mb-4">
          Бесплатный правовой анализ вашей ситуации за 15 минут в Telegram.
        </div>
        <button class="w-full py-2.5 bg-sky-500 text-slate-950 font-bold rounded-lg text-xs">Получить разбор ситуации</button>
      </div>
    `
  }
};

function initPortfolioModal() {
  const dialog = document.getElementById('portfolio-dialog');
  const closeBtn = document.getElementById('dialog-close-btn');
  const modalTitle = document.getElementById('modal-title');
  const modalNiche = document.getElementById('modal-niche');
  const modalResult = document.getElementById('modal-result');
  const modalSpeed = document.getElementById('modal-speed');
  const modalContent = document.getElementById('modal-demo-container');

  if (!dialog) return;

  document.querySelectorAll('.open-demo-btn').forEach(button => {
    button.addEventListener('click', () => {
      const demoKey = button.dataset.demo;
      const data = portfolioData[demoKey];
      if (!data) return;

      modalTitle.textContent = data.title;
      modalNiche.textContent = data.niche;
      modalResult.textContent = data.result;
      modalSpeed.textContent = data.speed;
      modalContent.innerHTML = data.demoHtml;

      dialog.showModal();
    });
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => dialog.close());
  }

  // Graceful light dismiss handling per modern web guidance
  dialog.addEventListener('click', (e) => {
    const rect = dialog.getBoundingClientRect();
    if (
      e.clientX < rect.left ||
      e.clientX > rect.right ||
      e.clientY < rect.top ||
      e.clientY > rect.bottom
    ) {
      dialog.close();
    }
  });
}

// 3. Quiz / Step-by-Step Price Estimator
function initQuiz() {
  const form = document.getElementById('quiz-form');
  if (!form) return;

  const steps = form.querySelectorAll('.quiz-step');
  const nextBtns = form.querySelectorAll('.quiz-next-btn');
  const prevBtns = form.querySelectorAll('.quiz-prev-btn');
  const progressFill = document.getElementById('quiz-progress-fill');
  const progressText = document.getElementById('quiz-progress-text');
  let currentStep = 0;

  const updateStep = (index) => {
    steps.forEach((step, i) => {
      step.classList.toggle('hidden', i !== index);
    });
    currentStep = index;
    const percent = ((index + 1) / steps.length) * 100;
    if (progressFill) progressFill.style.width = `${percent}%`;
    if (progressText) progressText.textContent = `Шаг ${index + 1} из ${steps.length}`;
  };

  nextBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (currentStep < steps.length - 1) {
        updateStep(currentStep + 1);
      }
    });
  });

  prevBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (currentStep > 0) {
        updateStep(currentStep - 1);
      }
    });
  });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const niche = form.querySelector('input[name="quiz-niche"]:checked')?.value || 'Не выбрано';
    const goal = form.querySelector('input[name="quiz-goal"]:checked')?.value || 'Новый сайт';
    const contact = form.querySelector('#quiz-contact')?.value || '';

    showNotificationSuccess(`Заявка принята! Ниша: "${niche}". Мы подготовим предварительный концепт и свяжемся с вами в Telegram/WhatsApp (${contact}).`);
    form.reset();
    updateStep(0);
  });
}

// 4. Contact Form with Telegram Simulation
function initContactForm() {
  const form = document.getElementById('contact-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const name = form.querySelector('#user-name')?.value;
    const phone = form.querySelector('#user-phone')?.value;
    const plan = form.querySelector('#user-plan')?.value;
    const note = form.querySelector('#user-note')?.value;

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;

    submitBtn.disabled = true;
    submitBtn.innerHTML = `
      <svg class="animate-spin -ml-1 mr-2 h-4 w-4 inline text-white" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
      </svg> Отправка в Telegram...
    `;

    setTimeout(() => {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
      showNotificationSuccess(`Спасибо, ${name || 'клиент'}! Заявка на тариф "${plan}" принята. Скоро напишем вам на ${phone} с готовым предложением.`);
      form.reset();
    }, 900);
  });
}

function showNotificationSuccess(message) {
  const alertEl = document.getElementById('success-toast');
  const alertMsg = document.getElementById('success-toast-msg');
  if (!alertEl || !alertMsg) {
    alert(message);
    return;
  }
  alertMsg.textContent = message;
  alertEl.classList.remove('hidden', 'translate-y-10', 'opacity-0');
  alertEl.classList.add('translate-y-0', 'opacity-100');

  setTimeout(() => {
    alertEl.classList.add('translate-y-10', 'opacity-0');
    setTimeout(() => alertEl.classList.add('hidden'), 300);
  }, 5000);
}

// 5. Mobile Menu Toggle
function initMobileMenu() {
  const toggleBtn = document.getElementById('mobile-menu-toggle');
  const menu = document.getElementById('mobile-menu');
  if (!toggleBtn || !menu) return;

  toggleBtn.addEventListener('click', () => {
    menu.classList.toggle('hidden');
  });

  menu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      menu.classList.add('hidden');
    });
  });
}
