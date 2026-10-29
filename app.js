// LocalWeb - Core Interactive Logic & Animations

document.addEventListener('DOMContentLoaded', () => {
  initKaraokeTitle();
  initScrollReveal();
  initSpotlight();
  initMessengerSelector();
  initContactForm();
  initDynamicDate();
});

// 1. Karaoke / Subtitle reading animation on Hero Title
// Строго по 1 букве, без неона, черновик гарантированно темный, зеленым остается только "потом"
function initKaraokeTitle() {
  const title = document.getElementById('hero-title');
  if (!title) return;

  const blackText = "Сайт для вашего дела за 24 часа. Сначала рабочий черновик, оплата — ";
  const greenText = "потом";

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
          charSpan.style.color = '#10B981';
          charSpan.style.fontWeight = '900';
        } else {
          charSpan.style.color = '#0F172A';
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

  // Запуск бегущей подсветки ровно по 1 букве
  setTimeout(() => {
    let index = 0;
    let currentActive = null;
    const speed = 30; // мс на букву

    const timer = setInterval(() => {
      // Предыдущая буква мгновенно гаснет
      if (currentActive) {
        currentActive.classList.remove('karaoke-active');
        if (currentActive.dataset.isGreen === "true") {
          currentActive.style.color = '#10B981';
        } else {
          currentActive.style.color = '#0F172A';
        }
      }

      if (index < allCharSpans.length) {
        currentActive = allCharSpans[index];
        currentActive.classList.add('karaoke-active');
        currentActive.style.color = '#10B981';
        index++;
      } else {
        clearInterval(timer);
        currentActive = null;
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

// 5. Contact Form Submission & Success Dialog
function initContactForm() {
  const form = document.getElementById('lead-form');
  const dialog = document.getElementById('success-dialog');
  const closeBtn = document.getElementById('dialog-close-btn');

  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;

    submitBtn.disabled = true;
    submitBtn.innerHTML = `
      <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
      </svg>
      Отправка...
    `;

    const name = form.querySelector('#user-name')?.value || 'клиент';
    const messenger = form.querySelector('#selected-messenger')?.value || 'Telegram';
    const contact = form.querySelector('#contact-input')?.value || '';

    setTimeout(() => {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;

      const userNameEl = document.getElementById('modal-user-name');
      const userDetailsEl = document.getElementById('modal-user-details');
      if (userNameEl) userNameEl.textContent = name;
      if (userDetailsEl) {
        userDetailsEl.textContent = `Мы свяжемся с вами через ${messenger} (${contact}) в течение 15 минут, чтобы обсудить первый черновик.`;
      }

      if (dialog && typeof dialog.showModal === 'function') {
        dialog.showModal();
      } else {
        alert(`Спасибо, ${name}! Заявка принята. Свяжемся с вами через ${messenger}: ${contact}`);
      }

      form.reset();
      
      const defaultBtn = document.querySelector('.messenger-btn[data-messenger="Telegram"]');
      if (defaultBtn) {
        document.querySelectorAll('.messenger-btn').forEach(b => b.classList.remove('active'));
        defaultBtn.classList.add('active');
        if (contactInput) {
          contactInput.placeholder = defaultBtn.getAttribute('data-placeholder') || '@username или номер в Telegram';
        }
      }
    }, 700);
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

// 6. Dynamic slot date
function initDynamicDate() {
  const dateEl = document.getElementById('current-date');
  if (dateEl) {
    const today = new Date();
    const options = { day: 'numeric', month: 'long' };
    dateEl.textContent = today.toLocaleDateString('ru-RU', options);
  }
}
