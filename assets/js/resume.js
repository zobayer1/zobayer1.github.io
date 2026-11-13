/* Resume page behavior (_tabs/resume.html). Progressive enhancement only: without this file
   every card, section and detail still renders; the lens control and the timeline are the only
   parts that need it.

   - Lens: "Read as" buttons set data-lens on .rz. CSS does the dimming, reordering and lead-line
     swap; this file animates the reorder (FLIP) and mirrors the lens into ?lens= so a tailored
     view can be shared as a link (e.g. /resume/?lens=ai).
   - Stats count up once when they scroll into view.
   - Timeline: built from the JSON in #rz-tl-data. Bars link to their card; clicking opens the
     card's details and scrolls to it; hovering a bar or a card highlights the other.

   Kept in a separate file because Chirpy's `compress` layout collapses inline scripts onto one
   line, which breaks any `//` comment. */
(() => {
  'use strict';

  const root = document.querySelector('.rz');
  if (!root) return;
  root.classList.add('rz-js');

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const LENSES = ['all', 'architect', 'ic', 'lead', 'ai', 'security'];
  const grid = root.querySelector('.rz-cards');
  const lead = root.querySelector('.rz-lead');
  const buttons = [...root.querySelectorAll('[data-lens-btn]')];

  /* ---------- lens ---------- */

  function setLens(lens, { animate = true, updateUrl = true } = {}) {
    if (!LENSES.includes(lens)) lens = 'all';
    if (lens === root.dataset.lens) return;

    const cards = grid ? [...grid.children] : [];
    const before = new Map(cards.map((c) => [c, c.getBoundingClientRect()]));

    root.dataset.lens = lens;
    buttons.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.lensBtn === lens)));

    if (animate && !reduce) {
      lead.classList.remove('rz-swap');
      void lead.offsetWidth; // restart the animation
      lead.classList.add('rz-swap');

      cards.forEach((c) => {
        const a = before.get(c);
        const b = c.getBoundingClientRect();
        const dx = a.left - b.left;
        const dy = a.top - b.top;
        if (dx || dy) {
          c.animate([{ transform: `translate(${dx}px, ${dy}px)` }, { transform: 'none' }], {
            duration: 420,
            easing: 'cubic-bezier(.2, .7, .2, 1)'
          });
        }
      });
    }

    if (updateUrl) {
      const url = new URL(window.location.href);
      if (lens === 'all') url.searchParams.delete('lens');
      else url.searchParams.set('lens', lens);
      window.history.replaceState(null, '', url);
    }
  }

  buttons.forEach((b) => b.addEventListener('click', () => setLens(b.dataset.lensBtn)));
  setLens(new URLSearchParams(window.location.search).get('lens') || 'all', {
    animate: false,
    updateUrl: false
  });

  /* ---------- stats ---------- */

  const counters = [...root.querySelectorAll('[data-count]')];
  if (!reduce && 'IntersectionObserver' in window && counters.length) {
    const show = (el, v) => {
      el.textContent = `${v}${el.dataset.suffix || ''}`;
    };
    const run = (el) => {
      const to = Number(el.dataset.count);
      const from = Number(el.dataset.from || 0);
      const t0 = performance.now();
      const step = (t) => {
        const p = Math.min(1, (t - t0) / 1100);
        show(el, Math.round(from + (to - from) * (1 - (1 - p) ** 3)));
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (!e.isIntersecting) return;
          io.unobserve(e.target);
          run(e.target);
        });
      },
      { threshold: 0.6 }
    );
    counters.forEach((el) => io.observe(el));
  }

  /* ---------- timeline ---------- */

  const dataEl = document.getElementById('rz-tl-data');
  const wrap = root.querySelector('.rz-tl-wrap');
  const tl = root.querySelector('.rz-tl');

  if (dataEl && wrap && tl) {
    const items = JSON.parse(dataEl.textContent);
    const MIN = 2013;
    const MAX = 2027;
    const NOW = 2026 + 10.5 / 12;
    const LANES = [
      ['gov', 'National platforms'],
      ['prod', 'Products'],
      ['edu', 'Teaching & community']
    ];
    const pct = (y) => ((y - MIN) / (MAX - MIN)) * 100;
    const yearOf = (y) => (y >= NOW ? 'present' : String(Math.floor(y)));
    const make = (tag, cls, attrs = {}) => {
      const n = document.createElement(tag);
      if (cls) n.className = cls;
      Object.entries(attrs).forEach(([k, v]) => n.setAttribute(k, v));
      return n;
    };

    // Every cell is placed explicitly. The "now" line spans all rows of column 2; left to
    // auto-placement, the other cells would flow around it and land in the wrong columns.
    const place = (n, col, row) => {
      n.style.gridColumn = String(col);
      n.style.gridRow = String(row);
      return n;
    };

    const axis = place(make('div', 'rz-tl-axis', { 'aria-hidden': 'true' }), 2, 1);
    // The current year gets no tick: the "now" label sits in its place.
    for (let y = MIN; y < Math.floor(NOW); y += 1) {
      const t = make('span', `rz-tl-tick${y % 2 ? ' rz-odd' : ''}`);
      t.style.left = `${pct(y + 0.5)}%`;
      t.textContent = String(y);
      axis.append(t);
    }
    tl.append(axis);

    LANES.forEach(([lane, name], i) => {
      const laneItems = items
        .filter((d) => d.lane === lane)
        .sort((a, b) => a.start - b.start || b.end - a.end);

      // Greedy interval packing: each bar takes the first row that is free by its start.
      const rowEnds = [];
      laneItems.forEach((d) => {
        let row = rowEnds.findIndex((end) => end <= d.start - 0.1);
        if (row < 0) {
          row = rowEnds.length;
          rowEnds.push(0);
        }
        rowEnds[row] = d.end;
        d.row = row;
      });

      const label = place(make('div', 'rz-tl-name', { 'data-lane': lane }), 1, i + 2);
      label.textContent = name;
      const track = place(make('div', 'rz-tl-track', { 'data-lane': lane }), 2, i + 2);
      track.style.setProperty('--rows', rowEnds.length);

      laneItems.forEach((d) => {
        const span = `${Math.floor(d.start)} – ${yearOf(d.end)}`;
        const bar = make('a', 'rz-tl-bar', {
          href: `#${d.card}`,
          'data-card': d.card,
          'data-tags': d.tags,
          title: `${d.label}, ${span}`,
          'aria-label': `${d.label}, ${span}`
        });
        bar.style.left = `${pct(d.start)}%`;
        bar.style.width = `${pct(Math.min(d.end, NOW)) - pct(d.start)}%`; // ongoing work stops at "now"
        bar.style.top = `calc(${d.row} * var(--rz-row))`;
        const text = make('span');
        text.textContent = d.label;
        bar.append(text);
        track.append(bar);
      });

      tl.append(label, track);
    });

    const now = make('div', 'rz-tl-now', { 'aria-hidden': 'true' });
    now.style.gridColumn = '2';
    now.style.gridRow = `1 / span ${LANES.length + 1}`;
    now.style.setProperty('--x', `${pct(NOW)}%`);
    tl.append(now);

    wrap.hidden = false;

    const hot = (id, on) => {
      root.querySelectorAll(`.rz-tl-bar[data-card="${id}"]`).forEach((n) => n.classList.toggle('rz-hot', on));
      const card = document.getElementById(id);
      if (card && card.classList.contains('rz-card')) card.classList.toggle('rz-hot', on);
    };

    tl.addEventListener('click', (e) => {
      const bar = e.target.closest('.rz-tl-bar');
      const target = bar && document.getElementById(bar.dataset.card);
      if (!target) return;
      e.preventDefault();
      const details = target.querySelector('details');
      if (details) details.open = true;
      target.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
      target.classList.remove('rz-flash');
      void target.offsetWidth;
      target.classList.add('rz-flash');
    });

    const hover = (container, pick, idOf) => {
      container.addEventListener('pointerover', (e) => {
        const n = e.target.closest(pick);
        if (n) hot(idOf(n), true);
      });
      container.addEventListener('pointerout', (e) => {
        const n = e.target.closest(pick);
        if (n && !n.contains(e.relatedTarget)) hot(idOf(n), false);
      });
    };
    hover(tl, '.rz-tl-bar', (n) => n.dataset.card);
    if (grid) hover(grid, '.rz-card', (n) => n.id);
  }

  /* ---------- print: show every detail ---------- */

  const opened = [];
  window.addEventListener('beforeprint', () => {
    root.querySelectorAll('details:not([open])').forEach((d) => {
      d.open = true;
      opened.push(d);
    });
  });
  window.addEventListener('afterprint', () => {
    opened.splice(0).forEach((d) => {
      d.open = false;
    });
  });
})();
