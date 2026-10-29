// LocalWeb - Core Interactive Logic & Animations

document.addEventListener('DOMContentLoaded', () => {
  initKaraokeTitle();
  initScrollReveal();
  initSpotlight();
  initMessengerSelector();
  initContactForm();
  initFaqAccordion();
  initDynamicDate();
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

// Конфигурация вебхука для сбора заявок (Яндекс.Облако, 152-ФЗ шлюз)
window.LEAD_ENDPOINT = window.LEAD_ENDPOINT || 'https://functions.yandexcloud.net/d4e23a85l1pnpv0skdum';

// 5. Contact Form Submission & Success Dialog
function initContactForm() {
  const form = document.getElementById('lead-form');
  const dialog = document.getElementById('success-dialog');
  const closeBtn = document.getElementById('dialog-close-btn');

  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;

    // Сбор данных формы
    const payload = {
      name: form.querySelector('#user-name')?.value.trim() || '',
      surname: form.querySelector('#user-surname')?.value.trim() || '',
      company: form.querySelector('#user-company')?.value.trim() || '',
      niche: form.querySelector('#user-niche')?.value.trim() || '',
      messenger: form.querySelector('#selected-messenger')?.value || 'Telegram',
      contact: form.querySelector('#contact-input')?.value.trim() || '',
      notes: form.querySelector('#user-notes')?.value.trim() || '',
      timestamp: new Date().toLocaleString('ru-RU', { timeZone: 'Europe/Moscow' }),
      source: window.location.href
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
      // Если подключен рабочий эндпоинт — отправляем реальный запрос
      if (window.LEAD_ENDPOINT && window.LEAD_ENDPOINT.trim() !== '') {
        const response = await fetch(window.LEAD_ENDPOINT, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          console.warn('Сервер вернул статус:', response.status);
        }
      } else {
        // Имитация быстрой сетевой задержки для плавности анимации
        await new Promise(resolve => setTimeout(resolve, 600));
      }

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

  if (closeBtn && dialog) {
    closeBtn.addEventListener('click', () => dialog.close());
  }

  if (dialog) {
    dialog.addEventListener('click', (e) => {
      const rect = dialog.getBoundingClientRect();
      const isInDialog = (
        rect.top <= e.clientY &&
        e.clientY <= rect.top + rect.height &&
        rect.left <= e.clientX &&
        e.clientX <= rect.left + rect.width
      );
      if (!isInDialog) {
        dialog.close();
      }
    });
  }
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
