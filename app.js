// LocalWeb - Core Interactive Logic & Animations

document.addEventListener('DOMContentLoaded', () => {
  initReferralTracking();
  initKaraokeTitle();
  initScrollReveal();
  initSpotlight();
  initMessengerSelector();
  initContactForm();
  initFaqAccordion();
  initDynamicDate();
  initPartnerPage();
});

// 1. Karaoke / Subtitle reading animation on Hero Title
// Плавная волна с подсветкой; в финале светятся строго "оплата — потом"
function initKaraokeTitle() {
  const title = document.getElementById('hero-title');
  if (!title) return;

  const blackText = "Сайт для вашего дела за 24 часа. Сначала рабочий черновик, ";
  const greenText = "оплата — потом";

  title.innerHTML = '';
  const allCharSpans = [];

  function buildSpans(text, isPermanentGreen) {
    const words = text.split(' ');
    words.forEach((word, wIdx) => {
      if (word.length === 0) return;
      const wordSpan = document.createElement('span');
      wordSpan.className = 'inline-block whitespace-nowrap';

      for (let i = 0; i < word.length; i++) {
        const charSpan = document.createElement('span');
        charSpan.textContent = word[i];
        charSpan.className = 'karaoke-char';
        if (isPermanentGreen) {
          charSpan.dataset.isGreen = "true";
        }
        wordSpan.appendChild(charSpan);
        allCharSpans.push(charSpan);
      }

      title.appendChild(wordSpan);
      if (wIdx < words.length - 1 || text.endsWith(' ')) {
        title.appendChild(document.createTextNode(' '));
      }
    });
  }

  // Создаем структуру текста
  buildSpans(blackText, false);
  buildSpans(greenText, true);

  // Запуск плавной субтитровой волны
  setTimeout(() => {
    let index = 0;
    const speed = 28; // мс на символ

    const timer = setInterval(() => {
      if (index < allCharSpans.length) {
        const char = allCharSpans[index];
        char.classList.add('karaoke-active');

        // Мягкое угасание волны
        setTimeout(() => {
          char.classList.remove('karaoke-active');
          if (char.dataset.isGreen === "true") {
            char.classList.add('karaoke-final-green');
          }
        }, 180);

        index++;
      } else {
        clearInterval(timer);
      }
    }, speed);
  }, 350);
}

// 2. Smooth Scroll Reveal with IntersectionObserver
function initScrollReveal() {
  const reveals = document.querySelectorAll('.reveal');
  
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
          obs.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -30px 0px'
    });

    reveals.forEach(el => observer.observe(el));
  } else {
    reveals.forEach(el => el.classList.add('active'));
  }
}

// 3. Spotlight Hover Effect for Bento Cards
function initSpotlight() {
  const cards = document.querySelectorAll('.card-glass');
  cards.forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      card.style.setProperty('--x', `${x}px`);
      card.style.setProperty('--y', `${y}px`);
    });
  });
}

// 4. Messenger Button Selector in Form
function initMessengerSelector() {
  const buttons = document.querySelectorAll('.messenger-btn');
  const hiddenInput = document.getElementById('selected-messenger');
  const contactInput = document.getElementById('contact-input');

  buttons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const messenger = btn.getAttribute('data-messenger') || 'Telegram';
      const placeholder = btn.getAttribute('data-placeholder') || 'Ваш контакт';

      if (hiddenInput) {
        hiddenInput.value = messenger;
      }

      if (contactInput) {
        contactInput.placeholder = placeholder;
        contactInput.focus();
      }
    });
  });
}

// Конфигурация вебхуков для сбора заявок:
// 1. Основной шлюз: Google Таблица + моментальный пуш в Telegram
window.LEAD_ENDPOINT = window.LEAD_ENDPOINT || 'https://script.google.com/macros/s/AKfycbygm5pShoTm9MsR8gA2FM3y47aojBNUVxFz_TjOrC4zvUZsDEu-6A1UZgwSxcIJVSQD/exec';

// 2. Российский шлюз Яндекс.Облако: первичная фиксация по 152-ФЗ в РФ
window.YANDEX_152FZ_ENDPOINT = window.YANDEX_152FZ_ENDPOINT || 'https://functions.yandexcloud.net/d4e23a85l1pnpv0skdum';

// 4.1 Referral Tracking (?ref=partner_id)
function initReferralTracking() {
  try {
    const params = new URLSearchParams(window.location.search);
    const rawRef = params.get('ref');
    if (rawRef) {
      const cleanRef = rawRef.trim().replace(/[^a-zA-Z0-9_.-]/g, '').slice(0, 50);
      if (cleanRef) {
        sessionStorage.setItem('lw_partner_ref', cleanRef);
        localStorage.setItem('lw_partner_ref', cleanRef);
      }
    }
  } catch (e) {
    console.debug('Referral tracking skipped:', e);
  }
}

function getSourceWithReferral() {
  const baseUrl = window.location.href.slice(0, 160);
  try {
    const savedRef = sessionStorage.getItem('lw_partner_ref') || localStorage.getItem('lw_partner_ref') || '';
    if (savedRef && !baseUrl.includes('ref=')) {
      return `${baseUrl} | Партнёр: ref=${savedRef}`.slice(0, 200);
    }
  } catch (e) {
    // storage disabled
  }
  return baseUrl;
}

// 4.2 Shared Helpers (Transport, Cooldown, Dialog Light-Dismiss, Inline Validation)
function checkSubmissionCooldown() {
  const COOLDOWN_MS = 30000;
  const lastSubmit = parseInt(sessionStorage.getItem('lw_last_submit') || '0', 10);
  const now = Date.now();
  if (now - lastSubmit < COOLDOWN_MS) {
    return Math.ceil((COOLDOWN_MS - (now - lastSubmit)) / 1000);
  }
  return 0;
}

async function dispatchLeadRequest(payload, metrikaGoal = 'lead_form_submit') {
  if (window.LEAD_ENDPOINT && window.LEAD_ENDPOINT.trim() !== '') {
    const payloadString = JSON.stringify(payload);

    await fetch(window.LEAD_ENDPOINT, {
      method: 'POST',
      mode: 'no-cors',
      headers: {
        'Content-Type': 'text/plain;charset=utf-8'
      },
      body: payloadString
    });

    if (window.YANDEX_152FZ_ENDPOINT && window.YANDEX_152FZ_ENDPOINT.trim() !== '') {
      fetch(window.YANDEX_152FZ_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payloadString
      }).catch(err => console.debug('152-FZ log sync:', err));
    }
  } else {
    await new Promise(resolve => setTimeout(resolve, 600));
  }

  sessionStorage.setItem('lw_last_submit', Date.now().toString());

  if (typeof ym === 'function' && metrikaGoal) {
    try {
      ym(113958309, 'reachGoal', metrikaGoal);
    } catch (e) {
      console.debug('Yandex Metrika goal error:', e);
    }
  }
}

function bindDialogLightDismiss(dialog, closeBtn) {
  if (!dialog) return;

  if (closeBtn) {
    closeBtn.addEventListener('click', () => dialog.close());
  }

  dialog.addEventListener('close', () => {
    dialog.returnValue = '';
  });

  if (!('closedBy' in HTMLDialogElement.prototype)) {
    const isOutside = (e) => {
      const r = dialog.getBoundingClientRect();
      return e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom;
    };
    let pressedOutside = false;
    dialog.addEventListener('pointerdown', (e) => {
      pressedOutside = isOutside(e);
    });
    dialog.addEventListener('pointerup', (e) => {
      if (pressedOutside && isOutside(e)) dialog.close();
      pressedOutside = false;
    });
  }
}

function setupInlineValidation(form) {
  const fields = form.querySelectorAll('input[required], textarea[required], select[required]');
  fields.forEach(field => {
    let touched = false;
    field.addEventListener('input', () => {
      field.setCustomValidity('');
      field.removeAttribute('aria-invalid');
      const errEl = document.getElementById(`${field.id}-error`);
      if (errEl) errEl.textContent = '';
    });
    field.addEventListener('blur', () => {
      if (field.value.trim().length > 0) touched = true;
      if (!touched) return;
      if (!field.checkValidity()) {
        field.setAttribute('aria-invalid', 'true');
        const errEl = document.getElementById(`${field.id}-error`);
        if (errEl) errEl.textContent = field.validationMessage;
      }
    });
  });
}

// 5. Contact Form Submission & Success Dialog
function initContactForm() {
  const form = document.getElementById('lead-form');
  const dialog = document.getElementById('success-dialog');
  const closeBtn = document.getElementById('dialog-close-btn');

  if (!form) return;

  bindDialogLightDismiss(dialog, closeBtn);
  setupInlineValidation(form);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // 0. Защита от ботов: проверка honeypot-ловушки
    const honeypot = form.querySelector('#form-website-trap')?.value;
    if (honeypot && honeypot.trim() !== '') {
      console.warn('Bot detected via honeypot.');
      form.reset();
      if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
      return;
    }

    // 0.1. Защита от частого спама (Rate-limiting: 30 секунд между отправками)
    const remainingSec = checkSubmissionCooldown();
    if (remainingSec > 0) {
      alert(`Пожалуйста, подождите ${remainingSec} сек. перед отправкой следующей заявки.`);
      return;
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;

    const name = (form.querySelector('#user-name')?.value || '').trim().slice(0, 60);
    const surname = (form.querySelector('#user-surname')?.value || '').trim().slice(0, 60);
    const company = (form.querySelector('#user-company')?.value || '').trim().slice(0, 100);
    const niche = (form.querySelector('#user-niche')?.value || '').trim().slice(0, 100);
    const messenger = form.querySelector('#selected-messenger')?.value || 'Telegram';
    const contact = (form.querySelector('#contact-input')?.value || '').trim().slice(0, 100);
    const notes = (form.querySelector('#user-notes')?.value || '').trim().slice(0, 1000);

    // Валидация от случайных и мусорных кликов
    if (name.length < 2) {
      alert('Пожалуйста, укажите имя (не менее 2 букв).');
      form.querySelector('#user-name')?.focus();
      return;
    }
    if (contact.length < 3) {
      alert('Пожалуйста, укажите контакт для связи (телефон, @username или email).');
      form.querySelector('#contact-input')?.focus();
      return;
    }

    // Сбор и подготовка данных формы
    const payload = {
      name,
      surname,
      company,
      niche,
      messenger,
      contact,
      notes,
      timestamp: new Date().toLocaleString('ru-RU', { timeZone: 'Europe/Moscow' }),
      source: getSourceWithReferral()
    };

    submitBtn.disabled = true;
    submitBtn.innerHTML = `
      <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
      </svg>
      Отправка заявки...
    `;

    try {
      await dispatchLeadRequest(payload, 'lead_form_submit');

      // Заполняем данные в модальном окне
      const userNameEl = document.getElementById('modal-user-name');
      const userDetailsEl = document.getElementById('modal-user-details');
      if (userNameEl) userNameEl.textContent = payload.name || 'клиент';
      if (userDetailsEl) {
        userDetailsEl.textContent = `Мы свяжемся с вами через ${payload.messenger} (${payload.contact}) в течение 15 минут, чтобы обсудить первый черновик.`;
      }

      // Открываем модальное окно
      if (dialog && typeof dialog.showModal === 'function') {
        dialog.showModal();
      } else {
        alert(`Спасибо, ${payload.name}! Заявка принята. Свяжемся с вами через ${payload.messenger}: ${payload.contact}`);
      }

      // Сбрасываем форму к исходному состоянию
      form.reset();
      
      const defaultBtn = document.querySelector('.messenger-btn[data-messenger="Telegram"]');
      const contactInput = form.querySelector('#contact-input');
      if (defaultBtn) {
        document.querySelectorAll('.messenger-btn').forEach(b => b.classList.remove('active'));
        defaultBtn.classList.add('active');
        if (contactInput) {
          contactInput.placeholder = defaultBtn.getAttribute('data-placeholder') || '@username или номер в Telegram';
        }
      }

    } catch (err) {
      console.error('Ошибка при отправке заявки:', err);
      alert('Произошла временная ошибка отправки. Пожалуйста, напишите нам напрямую в Telegram.');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  });
}

// 6. FAQ Accordion (Smooth toggle)
function initFaqAccordion() {
  const items = document.querySelectorAll('.faq-item');
  items.forEach(item => {
    item.addEventListener('click', () => {
      const wasActive = item.classList.contains('active');
      items.forEach(i => i.classList.remove('active'));
      if (!wasActive) {
        item.classList.add('active');
      }
    });
  });
}

// 7. Dynamic slot date
function initDynamicDate() {
  const dateEl = document.getElementById('current-date');
  if (dateEl) {
    const today = new Date();
    const options = { day: 'numeric', month: 'long' };
    dateEl.textContent = today.toLocaleDateString('ru-RU', options);
  }
}

// 8. Partner Page Interactive Features (Calculator, Ref Link Generator & Partner Form)
function initPartnerPage() {
  initPartnerCalculator();
  initPartnerRefGenerator();
  initPartnerRegistrationForm();
}

function initPartnerCalculator() {
  const calc = document.getElementById('partner-calculator');
  if (!calc) return;

  const modeRadios = calc.querySelectorAll('input[name="calc-mode"]');
  const clientsSlider = document.getElementById('calc-clients');
  const clientsLabel = document.getElementById('calc-clients-val');
  const serviceSelect = document.getElementById('calc-service');
  const wlWrap = document.getElementById('calc-wl-price-wrap');
  const wlSlider = document.getElementById('calc-wl-price');
  const wlLabel = document.getElementById('calc-wl-price-val');
  const agentWrap = document.getElementById('calc-agent-service-wrap');
  const monthlyOut = document.getElementById('calc-monthly-income');
  const yearlyOut = document.getElementById('calc-yearly-income');
  const perClientOut = document.getElementById('calc-per-client');

  const formatRub = (n) => `${n.toLocaleString('ru-RU')} ₽`;

  const recalculate = () => {
    const mode = calc.querySelector('input[name="calc-mode"]:checked')?.value || 'agent';
    const clients = parseInt(clientsSlider?.value || '4', 10);
    if (clientsLabel) clientsLabel.textContent = `${clients}`;

    let profitPerClient = 1500;
    if (mode === 'whitelabel') {
      if (wlWrap) wlWrap.hidden = false;
      if (agentWrap) agentWrap.hidden = true;
      const retailPrice = parseInt(wlSlider?.value || '12000', 10);
      if (wlLabel) wlLabel.textContent = formatRub(retailPrice);
      profitPerClient = Math.max(0, retailPrice - 6000);
    } else {
      if (wlWrap) wlWrap.hidden = true;
      if (agentWrap) agentWrap.hidden = false;
      profitPerClient = parseInt(serviceSelect?.value || '1500', 10);
    }

    const monthly = profitPerClient * clients;
    const yearly = monthly * 12;

    if (perClientOut) perClientOut.textContent = formatRub(profitPerClient);
    if (monthlyOut) monthlyOut.textContent = formatRub(monthly);
    if (yearlyOut) yearlyOut.textContent = formatRub(yearly);
  };

  modeRadios.forEach(r => r.addEventListener('change', recalculate));
  clientsSlider?.addEventListener('input', recalculate);
  serviceSelect?.addEventListener('change', recalculate);
  wlSlider?.addEventListener('input', recalculate);
  recalculate();
}

function initPartnerRefGenerator() {
  const input = document.getElementById('ref-slug-input');
  const outputUrl = document.getElementById('ref-generated-url');
  const copyBtn = document.getElementById('ref-copy-btn');
  const copyStatus = document.getElementById('ref-copy-status');
  const formSlugInput = document.getElementById('partner-ref-slug');

  if (!input || !outputUrl) return;

  const updateLink = () => {
    const sanitized = input.value.trim().replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 32) || 'ivan_dir';
    const fullUrl = `https://local-web.ru/?ref=${sanitized}`;
    outputUrl.textContent = fullUrl;
    outputUrl.href = fullUrl;
    if (formSlugInput && document.activeElement !== formSlugInput) {
      formSlugInput.value = input.value.trim() ? sanitized : '';
    }
  };

  input.addEventListener('input', updateLink);

  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      const urlToCopy = outputUrl.textContent.trim();
      try {
        await navigator.clipboard.writeText(urlToCopy);
        if (copyStatus) copyStatus.textContent = 'Ссылка скопирована в буфер обмена!';
      } catch {
        const tmp = document.createElement('textarea');
        tmp.value = urlToCopy;
        tmp.setAttribute('readonly', '');
        tmp.style.position = 'absolute';
        tmp.style.left = '-9999px';
        document.body.appendChild(tmp);
        tmp.select();
        document.execCommand('copy');
        document.body.removeChild(tmp);
        if (copyStatus) copyStatus.textContent = 'Ссылка скопирована!';
      }
      setTimeout(() => {
        if (copyStatus) copyStatus.textContent = '';
      }, 3000);
    });
  }

  updateLink();
}

function initPartnerRegistrationForm() {
  const form = document.getElementById('partner-form');
  const dialog = document.getElementById('partner-success-dialog');
  const closeBtn = document.getElementById('partner-dialog-close-btn');
  const statusEl = document.getElementById('partner-form-status');

  if (!form) return;

  bindDialogLightDismiss(dialog, closeBtn);
  setupInlineValidation(form);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const honeypot = form.querySelector('#partner-website-trap')?.value;
    if (honeypot && honeypot.trim() !== '') {
      form.reset();
      if (dialog && typeof dialog.showModal === 'function') dialog.showModal();
      return;
    }

    const remainingSec = checkSubmissionCooldown();
    if (remainingSec > 0) {
      if (statusEl) statusEl.textContent = `Пожалуйста, подождите ${remainingSec} сек. перед повторной отправкой.`;
      return;
    }

    if (!form.checkValidity()) {
      const firstInvalid = form.querySelector(':invalid');
      if (firstInvalid) {
        firstInvalid.setAttribute('aria-invalid', 'true');
        firstInvalid.focus();
      }
      if (statusEl) statusEl.textContent = 'Пожалуйста, заполните обязательные поля формы.';
      return;
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;

    const name = (form.querySelector('#partner-name')?.value || '').trim().slice(0, 60);
    const specialty = (form.querySelector('#partner-specialty')?.value || '').trim().slice(0, 80);
    const model = form.querySelector('input[name="partner-model"]:checked')?.value || 'Агентская (20%)';
    const refSlugRaw = (form.querySelector('#partner-ref-slug')?.value || '').trim().replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 32);
    const messenger = form.querySelector('#selected-messenger')?.value || 'Telegram';
    const contact = (form.querySelector('#contact-input')?.value || '').trim().slice(0, 100);
    const notes = (form.querySelector('#partner-notes')?.value || '').trim().slice(0, 1000);

    const assignedRef = refSlugRaw || name.toLowerCase().replace(/[^a-z0-9]/g, '') || 'partner';
    const generatedRefLink = `https://local-web.ru/?ref=${assignedRef}`;

    const payload = {
      name,
      surname: '',
      company: `Партнёр (${model})`,
      niche: `ПАРТНЁРКА: ${specialty}`,
      messenger,
      contact,
      notes: `Желаемый ref-код: ${assignedRef} (${generatedRefLink})\n${notes}`.trim().slice(0, 1000),
      timestamp: new Date().toLocaleString('ru-RU', { timeZone: 'Europe/Moscow' }),
      source: window.location.href.slice(0, 200)
    };

    if (statusEl) statusEl.textContent = '';
    submitBtn.disabled = true;
    submitBtn.textContent = 'Регистрация партнёра...';

    try {
      await dispatchLeadRequest(payload, 'partner_form_submit');

      const nameEl = document.getElementById('partner-modal-name');
      const linkEl = document.getElementById('partner-modal-link');
      if (nameEl) nameEl.textContent = name;
      if (linkEl) {
        linkEl.textContent = generatedRefLink;
        linkEl.href = generatedRefLink;
      }

      if (dialog && typeof dialog.showModal === 'function') {
        dialog.showModal();
      } else {
        alert(`Заявка партнёра принята! Ваша реферальная ссылка: ${generatedRefLink}`);
      }

      form.reset();
    } catch (err) {
      console.error('Ошибка регистрации партнёра:', err);
      if (statusEl) statusEl.textContent = 'Временная ошибка отправки. Напишите нам напрямую в Telegram @LocalWebRu.';
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  });
}
