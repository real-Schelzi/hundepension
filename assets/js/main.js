/* Hundepension im Park – Interaktionen
   Navigation · Einblenden · Live-Status · Betriebsferien · Rechner · Formulare · Lightbox · Galerie */
(() => {
  'use strict';
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const SITE = window.SITE || {};
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const store = {
    get(k) { try { return JSON.parse(sessionStorage.getItem(k)); } catch (e) { return null; } },
    set(k, v) { try { sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* privat */ } },
    del(k) { try { sessionStorage.removeItem(k); } catch (e) { /* privat */ } },
  };
  const chf = (n) => 'CHF ' + new Intl.NumberFormat('de-CH').format(n) + '.–';

  /* ---------------------------------------------------------------- Navigation */
  const header = $('[data-header]');
  const burger = $('[data-burger]');
  const nav = $('[data-nav]');
  const moreBtn = $('[data-more]');

  function setMenu(open) {
    burger.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('is-open', open);
    header.classList.toggle('menu-open', open);
    document.body.classList.toggle('menu-locked', open);
    if (open) setTimeout(() => { const first = $('a', nav); first && first.focus(); }, 80);
  }
  burger && burger.addEventListener('click', () => setMenu(burger.getAttribute('aria-expanded') !== 'true'));
  nav && nav.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });

  function setMore(open) { moreBtn.setAttribute('aria-expanded', String(open)); }
  if (moreBtn) {
    moreBtn.addEventListener('click', (e) => { e.stopPropagation(); setMore(moreBtn.getAttribute('aria-expanded') !== 'true'); });
    document.addEventListener('click', (e) => { if (!e.target.closest('.nav__more')) setMore(false); });
    moreBtn.parentElement.addEventListener('focusout', (e) => {
      if (!moreBtn.parentElement.contains(e.relatedTarget)) setMore(false);
    });
  }
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    if (burger && burger.getAttribute('aria-expanded') === 'true') { setMenu(false); burger.focus(); }
    if (moreBtn && moreBtn.getAttribute('aria-expanded') === 'true') { setMore(false); moreBtn.focus(); }
  });
  matchMedia('(min-width: 1101px)').addEventListener('change', (m) => { if (m.matches) setMenu(false); });

  // Header über dem Startbild: transparent, danach mit Hintergrund
  if (header && header.classList.contains('hdr--overlay')) {
    const day = $('[data-day]');
    const onScroll = () => {
      const hero = day && day.classList.contains('day--static') ? day.querySelector('.day__hero') : null;
      const limit = hero ? hero.offsetHeight - header.offsetHeight - 10
        : day ? day.offsetTop + day.offsetHeight - header.offsetHeight - 10 : 80;
      header.classList.toggle('is-solid', window.scrollY > limit);
    };
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', onScroll);
    onScroll();
  }

  /* ---------------------------------------------------------------- Einblenden & Zähler */
  const io = 'IntersectionObserver' in window ? new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (!en.isIntersecting) return;
      en.target.classList.add('is-in');
      io.unobserve(en.target);
      $$('[data-count]', en.target).forEach(countUp);
    });
  }, { rootMargin: '0px 0px -3% 0px', threshold: 0.01 }) : null;
  $$('.reveal').forEach((el) => (io ? io.observe(el) : el.classList.add('is-in')));
  const facts = $('.facts');
  if (facts && io) io.observe(facts);

  function countUp(el) {
    const raw = el.dataset.count;
    if (!/^\d+$/.test(raw) || reduceMotion || el.dataset.done) return;
    el.dataset.done = '1';
    const target = parseInt(raw, 10);
    const t0 = performance.now();
    const dur = 1400;
    const tick = (t) => {
      const k = Math.min(1, (t - t0) / dur);
      const v = Math.round(target * (1 - Math.pow(1 - k, 3)));
      el.textContent = String(v);
      if (k < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  /* ---------------------------------------------------------------- Zeit in Waltenschwil */
  const WD = { Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6, Sun: 7 };
  const WD_NAME = ['', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'];
  function zurich(date = new Date()) {
    const parts = {};
    new Intl.DateTimeFormat('en-GB', {
      timeZone: 'Europe/Zurich', weekday: 'short', year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', hourCycle: 'h23',
    }).formatToParts(date).forEach((p) => { parts[p.type] = p.value; });
    return {
      iso: `${parts.year}-${parts.month}-${parts.day}`,
      wd: WD[parts.weekday],
      min: parseInt(parts.hour, 10) * 60 + parseInt(parts.minute, 10),
    };
  }
  window.HP_ZURICH = zurich;
  const toMin = (s) => { const [h, m] = s.split(':').map(Number); return h * 60 + m; };
  const fmt = (m) => `${String(Math.floor(m / 60)).padStart(2, '0')}.${String(m % 60).padStart(2, '0')}`;
  const addDays = (iso, n) => { const d = new Date(iso + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
  const ferien = (SITE.ferien || []);
  const ferienOn = (iso) => ferien.find((f) => iso >= f.from && iso <= f.to);
  const windowsFor = (wd) => {
    const h = SITE.hours || {};
    return wd <= 5 ? (h.weekdays || []) : wd === 6 ? (h.saturday || []) : (h.sunday || []);
  };
  const dateCH = (iso) => { const [y, m, d] = iso.split('-'); return `${d}.${m}.${y}`; };

  function liveStatus() {
    const now = zurich();
    const holiday = ferienOn(now.iso);
    if (holiday) {
      return { open: false, text: `Zurzeit Betriebsferien (${holiday.label}) bis ${dateCH(holiday.to)}.` };
    }
    for (const [a, b] of windowsFor(now.wd)) {
      if (now.min >= toMin(a) && now.min < toMin(b)) {
        return { open: true, text: `Jetzt Bring- und Abholzeit – noch bis ${fmt(toMin(b))} Uhr.` };
      }
    }
    for (let i = 0; i < 40; i++) {
      const iso = addDays(now.iso, i);
      const wd = ((now.wd - 1 + i) % 7) + 1;
      if (ferienOn(iso)) continue;
      const next = windowsFor(wd).find(([a]) => i > 0 || toMin(a) > now.min);
      if (next) {
        const when = i === 0 ? 'heute' : i === 1 ? 'morgen' : i < 7 ? `am ${WD_NAME[wd]}` : `am ${dateCH(iso)}`;
        return { open: false, text: `Nächste Bring- und Abholzeit ${when} ab ${fmt(toMin(next[0]))} Uhr.` };
      }
    }
    return null;
  }
  function paintLive() {
    const s = liveStatus();
    $$('[data-live-status]').forEach((el) => {
      if (!s) { el.textContent = ''; return; }
      el.textContent = s.text;
      el.classList.add('live');
      el.classList.toggle('is-open', s.open);
    });
  }
  paintLive();
  setInterval(paintLive, 60000);

  /* ---------------------------------------------------------------- Betriebsferien */
  $$('[data-ferien]').forEach((list) => {
    const today = zurich().iso;
    let nextFound = false;
    let past = 0;
    $$('.ferien__item', list).forEach((li) => {
      const { from, to } = li.dataset;
      const state = $('[data-ferien-state]', li);
      li.classList.remove('is-past', 'is-now', 'is-next');
      if (to < today) { li.classList.add('is-past'); state.textContent = 'vorbei'; past++; }
      else if (from <= today) { li.classList.add('is-now'); state.textContent = 'jetzt'; }
      else if (!nextFound) { li.classList.add('is-next'); state.textContent = 'als Nächstes'; nextFound = true; }
    });
    const summary = list.nextElementSibling;
    if (summary && summary.matches('[data-ferien-summary]')) {
      summary.textContent = past === ferien.length && past > 0
        ? 'Alle hier aufgeführten Betriebsferien liegen hinter uns. Neue Daten werden hier veröffentlicht, sobald sie feststehen.'
        : '';
    }
  });

  /* ---------------------------------------------------------------- Preisrechner */
  $$('[data-calc]').forEach((form) => {
    const out = $('.calc__total', form);
    const list = $('[data-calc-breakdown]', form);
    const tage = form.elements.tage;
    const feiertage = form.elements.feiertage;
    const clampInput = (inp) => {
      const min = +inp.min || 0;
      const max = +inp.max || 90;
      let v = parseInt(inp.value, 10);
      if (Number.isNaN(v)) v = min;
      inp.value = String(Math.max(min, Math.min(max, v)));
    };
    function calc() {
      const art = (form.elements.art.value || 'tag');
      const p = SITE.prices[art];
      const ex = SITE.extras;
      const days = Math.max(1, parseInt(tage.value, 10) || 1);
      feiertage.max = String(days);
      if ((parseInt(feiertage.value, 10) || 0) > days) feiertage.value = String(days);
      const hol = Math.min(days, Math.max(0, parseInt(feiertage.value, 10) || 0));
      const pup = form.elements.welpe.checked;
      const integ = form.elements.integration.checked;
      const rows = [[`${days} × ${p.title}`, days * p.price]];
      if (hol) rows.push([`${hol} × Feiertag`, hol * ex.feiertag]);
      if (pup) rows.push([`${days} × Welpen-Zuschlag`, days * ex.welpe]);
      if (integ) rows.push(['Rudelintegration (einmalig)', ex.integration]);
      const total = rows.reduce((s, r) => s + r[1], 0);
      out.textContent = chf(total);
      list.innerHTML = '';
      rows.forEach(([l, v]) => {
        const li = document.createElement('li');
        li.innerHTML = '<span></span><span></span>';
        li.children[0].textContent = l;
        li.children[1].textContent = chf(v);
        list.appendChild(li);
      });
      return { art: p.title, artId: art, days, hol, pup, integ, total };
    }
    form.addEventListener('input', calc);
    form.addEventListener('change', (e) => { if (e.target.type === 'number') clampInput(e.target); calc(); });
    $$('[data-step]', form).forEach((b) => b.addEventListener('click', () => {
      const inp = $('input', b.parentElement);
      inp.value = String((parseInt(inp.value, 10) || 0) + Number(b.dataset.step));
      clampInput(inp);
      calc();
    }));
    form.addEventListener('submit', (e) => e.preventDefault());
    calc();

    const req = $('[data-calc-request]', form);
    req && req.addEventListener('click', (e) => {
      const r = calc();
      const text = `Ich interessiere mich für: ${r.art}, ${r.days} ${r.days === 1 ? 'Tag' : 'Tage'}`
        + (r.hol ? ` (davon ${r.hol} ${r.hol === 1 ? 'Feiertag' : 'Feiertage'})` : '')
        + (r.pup ? ', Welpe' : '')
        + (r.integ ? ', erster Aufenthalt' : '')
        + `. Geschätzter Betrag gemäss Preisrechner: ${chf(r.total)}.`;
      const data = { text, anliegen: r.artId === 'tag' ? 'Tagesbetreuung' : 'Ferienbetreuung' };
      const local = $('#anfrage');
      if (local) { e.preventDefault(); prefill(local, data); local.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'start' }); }
      else store.set('hp-calc', data);
    });
  });

  function prefill(form, data) {
    if (!data) return;
    const msg = form.elements.nachricht;
    if (msg && !msg.value.trim()) msg.value = data.text;
    const radio = $$('input[name="anliegen"]', form).find((r) => r.value === data.anliegen);
    if (radio) radio.checked = true;
    setTimeout(() => { const n = form.elements.name; n && n.focus({ preventScroll: true }); }, 450);
  }

  /* ---------------------------------------------------------------- Formulare */
  const MSG = {
    required: 'Bitte ausfüllen.',
    email: 'Bitte eine gültige E-Mail-Adresse eingeben.',
    check: 'Bitte bestätigen.',
    number: 'Bitte eine gültige Zahl eingeben.',
  };

  function labelFor(el) {
    const lab = el.id && document.querySelector(`label[for="${el.id}"]`);
    if (lab) return lab.textContent.replace('*', '').trim();
    const fs = el.closest('fieldset');
    return fs ? $('legend', fs).textContent.replace(/Schritt \d+ von \d+/, '').trim() : el.name;
  }

  function setError(el, msg) {
    const id = `${el.id || el.name}-err`;
    let err = document.getElementById(id);
    const host = el.type === 'checkbox' ? el.closest('.check') : el.closest('.field');
    if (!msg) {
      el.removeAttribute('aria-invalid');
      if (err) err.remove();
      if (el.dataset.desc !== undefined) {
        if (el.dataset.desc) el.setAttribute('aria-describedby', el.dataset.desc); else el.removeAttribute('aria-describedby');
      }
      return;
    }
    if (!err) {
      err = document.createElement('p');
      err.id = id;
      err.className = el.type === 'checkbox' ? 'check__error' : 'field__error';
      (host || el.parentElement).appendChild(err);
    }
    err.textContent = msg;
    el.setAttribute('aria-invalid', 'true');
    if (el.dataset.desc === undefined) el.dataset.desc = el.getAttribute('aria-describedby') || '';
    el.setAttribute('aria-describedby', [el.dataset.desc, id].filter(Boolean).join(' '));
  }

  function check(el) {
    let msg = '';
    if (el.type === 'checkbox') { if (el.required && !el.checked) msg = MSG.check; }
    else if (el.required && !el.value.trim()) msg = MSG.required;
    else if (el.type === 'email' && el.value && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(el.value.trim())) msg = MSG.email;
    else if (el.type === 'number' && el.value && el.validity && el.validity.badInput) msg = MSG.number;
    setError(el, msg);
    return !msg;
  }

  function validate(scope) {
    const els = $$('input, select, textarea', scope).filter((el) => el.name && el.type !== 'hidden' && !el.closest('.hp'));
    let first = null;
    els.forEach((el) => { if (!check(el) && !first) first = el; });
    if (first) first.focus();
    return !first;
  }

  function summary(form) {
    const lines = [];
    const seen = new Set();
    const title = form.dataset.form === 'anmeldung' ? 'Anmeldung Hundepension im Park' : 'Anfrage Hundepension im Park';
    lines.push(title, '');
    $$('input, select, textarea', form).forEach((el) => {
      if (!el.name || el.type === 'hidden' || el.closest('.hp') || seen.has(el.name)) return;
      if (el.name === 'datenschutz' || el.name === 'agb') return;
      let val;
      if (el.type === 'checkbox' || el.type === 'radio') {
        seen.add(el.name);
        val = $$(`[name="${el.name}"]:checked`, form).map((c) => c.value).join(', ');
        if (!val) return;
        const fs = el.closest('fieldset');
        const lab = fs ? $('legend', fs).textContent.replace(/\(.*\)/, '').replace(/Schritt \d+ von \d+/, '').trim() : el.name;
        lines.push(`${lab}: ${val}`);
        return;
      }
      val = el.value.trim();
      if (val) lines.push(`${labelFor(el)}: ${val}`);
    });
    return lines.join('\n');
  }

  function draftKey(form) { return `hp-draft-${form.dataset.form}`; }
  function saveDraft(form) {
    const data = {};
    $$('input, select, textarea', form).forEach((el) => {
      if (!el.name || el.type === 'hidden' || el.closest('.hp') || el.name === 'datenschutz' || el.name === 'agb') return;
      if (el.type === 'checkbox') { (data[el.name] = data[el.name] || []); if (el.checked) data[el.name].push(el.value); }
      else if (el.type === 'radio') { if (el.checked) data[el.name] = el.value; }
      else data[el.name] = el.value;
    });
    store.set(draftKey(form), data);
  }
  function restoreDraft(form) {
    const data = store.get(draftKey(form));
    if (!data) return;
    Object.entries(data).forEach(([name, v]) => {
      $$(`[name="${name}"]`, form).forEach((el) => {
        if (el.type === 'checkbox') el.checked = Array.isArray(v) && v.includes(el.value);
        else if (el.type === 'radio') el.checked = el.value === v;
        else el.value = v;
      });
    });
  }

  $$('form[data-form]').forEach((form) => {
    const ts = form.elements.ts;
    if (ts) ts.value = String(Date.now());
    restoreDraft(form);
    if (form.id === 'anfrage') {
      prefill(form, store.get('hp-calc'));
      store.del('hp-calc');
    }
    const status = $('.form__status', form);
    const fallback = $('.form__fallback', form);

    form.addEventListener('input', () => saveDraft(form));
    form.addEventListener('change', (e) => { saveDraft(form); if (e.target.getAttribute('aria-invalid')) check(e.target); });
    form.addEventListener('focusout', (e) => { const el = e.target; if (el.matches('[aria-invalid="true"]')) check(el); });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!validate(form)) { showWizardStepOfInvalid(form); return; }
      status.className = 'form__status';
      status.textContent = 'Wird gesendet …';
      fallback.hidden = true;
      form.classList.add('is-sending');
      try {
        if (!form.dataset.endpoint) throw new Error('kein Endpunkt');
        const res = await fetch(form.dataset.endpoint, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } });
        const data = await res.json().catch(() => ({}));
        if (!res.ok || !data.ok) throw new Error(data.error || `HTTP ${res.status}`);
        status.classList.add('is-ok');
        status.textContent = form.dataset.form === 'anmeldung'
          ? 'Herzlichen Dank! Die Anmeldung ist bei uns angekommen. Wir melden uns bei euch.'
          : 'Herzlichen Dank! Die Anfrage ist bei uns angekommen. Wir melden uns so bald wie möglich.';
        store.del(draftKey(form));
        form.reset();
        if (ts) ts.value = String(Date.now());
        if (form.matches('[data-wizard]')) form.dispatchEvent(new CustomEvent('wizard:reset'));
        status.focus();
      } catch (err) {
        status.classList.add('is-error');
        status.textContent = '';
        const text = summary(form);
        const sms = $('[data-fallback-sms]', fallback);
        sms.href = `sms:${SITE.phone}?&body=${encodeURIComponent(text)}`;
        if (SITE.email && !$('[data-fallback-mail]', fallback)) {
          const a = document.createElement('a');
          a.className = 'btn btn--line btn--sm';
          a.dataset.fallbackMail = '';
          a.textContent = 'Per E-Mail senden';
          a.href = `mailto:${SITE.email}?subject=${encodeURIComponent(text.split('\n')[0])}&body=${encodeURIComponent(text)}`;
          $('.form__fallback-actions', fallback).prepend(a);
        }
        if (form.matches('[data-wizard]') && !$('[data-fallback-print]', fallback)) {
          const b = document.createElement('button');
          b.type = 'button';
          b.className = 'btn btn--line btn--sm';
          b.dataset.fallbackPrint = '';
          b.textContent = 'Drucken / als PDF speichern';
          b.addEventListener('click', () => window.print());
          $('.form__fallback-actions', fallback).appendChild(b);
        }
        const copy = $('[data-fallback-copy]', fallback);
        copy.onclick = async () => {
          try { await navigator.clipboard.writeText(text); copy.textContent = 'Kopiert ✓'; }
          catch (x) { copy.textContent = 'Kopieren nicht möglich'; }
        };
        fallback.hidden = false;
        fallback.setAttribute('tabindex', '-1');
        fallback.focus();
      } finally {
        form.classList.remove('is-sending');
      }
    });
  });

  // Hinweis bei unkastrierten Rüden
  const anm = $('#anmeldung');
  if (anm) {
    const hint = $('[data-kastriert-hint]', anm);
    const upd = () => {
      const male = anm.elements.hund_geschlecht && anm.elements.hund_geschlecht.value === 'Rüde';
      const k = $('input[name="kastriert"]:checked', anm);
      hint.hidden = !(male && k && k.value === 'Nein');
    };
    anm.addEventListener('change', upd);
    upd();
  }

  /* ---------------------------------------------------------------- Mehrstufiges Formular */
  function showWizardStepOfInvalid(form) {
    if (!form.matches('[data-wizard]')) return;
    const bad = $('[aria-invalid="true"]', form);
    const step = bad && bad.closest('[data-step]');
    if (step && form._goto) { form._goto(Number(step.dataset.step)); bad.focus(); }
  }
  $$('[data-wizard]').forEach((form) => {
    const steps = $$('fieldset.step', form);
    const dots = $$('[data-step-dot]', form);
    const bar = $('[data-step-bar]', form);
    const prev = $('[data-prev]', form);
    const next = $('[data-next]', form);
    let cur = 0;
    function go(i, focus = true) {
      cur = Math.max(0, Math.min(steps.length - 1, i));
      steps.forEach((s, k) => s.classList.toggle('is-current', k === cur));
      dots.forEach((d, k) => { d.classList.toggle('is-current', k === cur); d.classList.toggle('is-done', k < cur); });
      bar.style.width = `${((cur + 1) / steps.length) * 100}%`;
      prev.hidden = cur === 0;
      form.classList.toggle('is-last', cur === steps.length - 1);
      if (focus) {
        const top = form.getBoundingClientRect().top + window.scrollY - (header ? header.offsetHeight : 0) - 16;
        if (window.scrollY > top) window.scrollTo({ top, behavior: reduceMotion ? 'auto' : 'smooth' });
        steps[cur].setAttribute('tabindex', '-1');
        steps[cur].focus({ preventScroll: true });
      }
      store.set('hp-wizard-step', cur);
    }
    form._goto = go;
    next.addEventListener('click', () => { if (validate(steps[cur])) go(cur + 1); });
    prev.addEventListener('click', () => go(cur - 1));
    form.addEventListener('wizard:reset', () => go(0, false));
    go(Number(store.get('hp-wizard-step')) || 0, false);
  });

  /* ---------------------------------------------------------------- Galerie-Filter */
  $$('[data-filters]').forEach((bar) => {
    const gallery = bar.parentElement.querySelector('[data-gallery]');
    const live = bar.parentElement.querySelector('[data-filter-status]');
    bar.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-filter]');
      if (!btn) return;
      const f = btn.dataset.filter;
      $$('[data-filter]', bar).forEach((b) => { const on = b === btn; b.classList.toggle('is-active', on); b.setAttribute('aria-pressed', String(on)); });
      let n = 0;
      $$('.masonry__item', gallery).forEach((li) => {
        const show = f === 'alle' || (li.dataset.cats || '').split(' ').includes(f);
        li.hidden = !show;
        if (show) n++;
      });
      if (live) live.textContent = `${n} Fotos angezeigt`;
    });
  });

  /* ---------------------------------------------------------------- Laufband */
  $$('[data-marquee] .marquee__track').forEach((track) => {
    $$('li', track).forEach((li) => {
      const c = li.cloneNode(true);
      c.setAttribute('aria-hidden', 'true');
      $$('img', c).forEach((img) => { img.alt = ''; });
      track.appendChild(c);
    });
  });

  /* ---------------------------------------------------------------- AGB-Inhaltsverzeichnis */
  const toc = $('.agb__toc');
  if (toc && io) {
    const links = $$('a[href^="#agb-"]', toc);
    const spy = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        links.forEach((a) => a.classList.toggle('is-active', a.getAttribute('href') === `#${en.target.id}`));
      });
    }, { rootMargin: '-30% 0px -60% 0px' });
    $$('.agb__sec').forEach((s) => spy.observe(s));
  }

  /* ---------------------------------------------------------------- Lightbox */
  const ICON = {
    prev: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>',
    next: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  };
  let lb = null;
  let opener = null;
  let items = [];
  let idx = 0;
  function buildLightbox() {
    lb = document.createElement('dialog');
    lb.className = 'lb';
    lb.setAttribute('aria-label', 'Bildansicht');
    lb.innerHTML = `
      <div class="lb__top"><span class="lb__count" aria-live="polite"></span><button class="lb__btn lb__close" type="button" aria-label="Schliessen">${ICON.close}</button></div>
      <div class="lb__stage"><button class="lb__btn lb__prev" type="button" aria-label="Vorheriges Bild">${ICON.prev}</button><img class="lb__img" alt=""><button class="lb__btn lb__next" type="button" aria-label="Nächstes Bild">${ICON.next}</button></div>
      <p class="lb__cap"></p>`;
    document.body.appendChild(lb);
    $('.lb__close', lb).addEventListener('click', () => lb.close());
    $('.lb__prev', lb).addEventListener('click', () => show(idx - 1));
    $('.lb__next', lb).addEventListener('click', () => show(idx + 1));
    lb.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') show(idx - 1);
      if (e.key === 'ArrowRight') show(idx + 1);
    });
    lb.addEventListener('click', (e) => { if (e.target === lb || e.target.classList.contains('lb__stage')) lb.close(); });
    let x0 = null;
    const stage = $('.lb__stage', lb);
    stage.addEventListener('pointerdown', (e) => { x0 = e.clientX; });
    stage.addEventListener('pointerup', (e) => {
      if (x0 === null) return;
      const dx = e.clientX - x0;
      x0 = null;
      if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1));
    });
    lb.addEventListener('close', () => {
      document.body.classList.remove('menu-locked');
      if (opener) opener.focus({ preventScroll: true });
    });
  }
  function show(i) {
    idx = (i + items.length) % items.length;
    const a = items[idx];
    const img = $('.lb__img', lb);
    img.classList.add('is-loading');
    img.onload = () => img.classList.remove('is-loading');
    img.sizes = '100vw';
    img.srcset = a.dataset.srcset || '';
    img.src = a.href;
    img.width = Number(a.dataset.w) || 0;
    img.height = Number(a.dataset.h) || 0;
    const alt = a.dataset.caption || ($('img', a) && $('img', a).alt) || '';
    img.alt = alt;
    $('.lb__cap', lb).textContent = alt;
    $('.lb__count', lb).textContent = `${idx + 1} / ${items.length}`;
    const multi = items.length > 1;
    $('.lb__prev', lb).hidden = !multi;
    $('.lb__next', lb).hidden = !multi;
    [idx + 1, idx - 1].forEach((k) => { const n = items[(k + items.length) % items.length]; if (n) { const p = new Image(); p.sizes = '100vw'; p.srcset = n.dataset.srcset || ''; } });
  }
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[data-lightbox]');
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey) return;
    if (typeof HTMLDialogElement !== 'function') return; // alter Browser: Link öffnet das Bild direkt
    e.preventDefault();
    if (!lb) buildLightbox();
    opener = a;
    const group = a.dataset.lightbox;
    items = $$(`a[data-lightbox="${group}"]`).filter((x) => !x.closest('[hidden]') && !x.closest('[aria-hidden="true"]'));
    show(items.indexOf(a));
    lb.showModal();
    document.body.classList.add('menu-locked');
    $('.lb__close', lb).focus();
  });
})();
