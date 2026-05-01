/* ============================================
   ANRCHARO PHOTOGRAPHE — MAIN JS (Flask)
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ---- NAVBAR SCROLL ---- */
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 60);
  });

  /* ---- MOBILE MENU ---- */
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  const mobileClose = document.getElementById('mobileClose');
  if (hamburger) hamburger.addEventListener('click', () => mobileMenu.classList.add('open'));
  if (mobileClose) mobileClose.addEventListener('click', () => mobileMenu.classList.remove('open'));
  if (mobileMenu) mobileMenu.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => mobileMenu.classList.remove('open'));
  });

  /* ---- SCROLL REVEAL ---- */
  const revealEls = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');
  const revealObs = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => entry.target.classList.add('visible'), i * 80);
        revealObs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  revealEls.forEach(el => revealObs.observe(el));

  /* ---- COUNTER ANIMATION ---- */
  const statsSection = document.getElementById('stats');
  let statsAnimated = false;
  if (statsSection) {
    const statsObs = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && !statsAnimated) {
        statsAnimated = true;
        document.querySelectorAll('.stat-num[data-target]').forEach(el => {
          const target = parseInt(el.dataset.target);
          const suffix = el.dataset.suffix || '';
          let start = null;
          const step = (ts) => {
            if (!start) start = ts;
            const progress = Math.min((ts - start) / 1800, 1);
            const ease = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.floor(ease * target) + suffix;
            if (progress < 1) requestAnimationFrame(step);
          };
          requestAnimationFrame(step);
        });
      }
    }, { threshold: 0.4 });
    statsObs.observe(statsSection);
  }

  /* ---- PORTFOLIO — AJAX LOAD ---- */
  const portfolioGrid = document.getElementById('portfolioGrid');
  const filterBtns    = document.querySelectorAll('.filter-btn');
  let currentCat = 'all';

  function renderPortfolio(photos) {
    if (!portfolioGrid) return;

    if (!photos.length) {
      portfolioGrid.innerHTML = '<div class="portfolio-empty">Aucune photo dans cette catégorie.</div>';
      return;
    }

    // Layout patterns: alternate between sizes
    const layouts = [
      ['pc-1','pc-2','pc-3','pc-4','pc-5','pc-6','pc-7'],
    ];

    portfolioGrid.innerHTML = photos.map((photo, i) => {
      const sizeClasses = ['pc-1','pc-2','pc-3','pc-4','pc-5','pc-6','pc-7'];
      const cls = sizeClasses[i % sizeClasses.length];
      return `
        <div class="photo-card ${cls} reveal" data-cat="${photo.category}" style="opacity:0">
          <img src="${photo.thumb_url}"
               alt="${photo.title}"
               class="card-img"
               loading="lazy"
               onerror="this.style.display='none'">
          <div class="photo-overlay">
            <div class="photo-meta">
              <span>${photo.category}</span>
              <h4>${photo.title}</h4>
            </div>
          </div>
        </div>`;
    }).join('');

    // Trigger reveal animations
    requestAnimationFrame(() => {
      portfolioGrid.querySelectorAll('.photo-card').forEach((el, i) => {
        setTimeout(() => {
          el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
          el.style.opacity    = '1';
          el.style.transform  = 'none';
          el.classList.add('visible');
        }, i * 60);
      });
    });
  }

  async function loadPortfolio(cat = 'all') {
    if (!portfolioGrid) return;
    portfolioGrid.innerHTML = '<div class="portfolio-loading">Chargement…</div>';
    try {
      const res    = await fetch(`/api/photos?cat=${cat}`);
      const photos = await res.json();
      renderPortfolio(photos);
    } catch (e) {
      portfolioGrid.innerHTML = '<div class="portfolio-empty">Erreur de chargement.</div>';
    }
  }

  // Filter buttons
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentCat = btn.dataset.filter;
      loadPortfolio(currentCat);
    });
  });

  // Initial load
  loadPortfolio('all');

  /* ---- CONTACT FORM — AJAX ---- */
  const form      = document.getElementById('reservationForm');
  const formInner = document.getElementById('formInner');
  const formSucc  = document.getElementById('formSuccess');
  const submitBtn = document.getElementById('submitBtn');

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      submitBtn.textContent = 'Envoi en cours…';
      submitBtn.disabled = true;

      try {
        const res  = await fetch('/reserver', {
          method: 'POST',
          body:   new FormData(form),
        });
        const data = await res.json();

        if (data.success) {
          formInner.style.display = 'none';
          formSucc.classList.add('show');
        } else {
          alert(data.message || 'Une erreur est survenue.');
          submitBtn.textContent = 'Envoyer ma demande';
          submitBtn.disabled = false;
        }
      } catch {
        alert('Erreur réseau. Veuillez réessayer.');
        submitBtn.textContent = 'Envoyer ma demande';
        submitBtn.disabled = false;
      }
    });
  }

  /* ---- SMOOTH ANCHOR ---- */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

});
