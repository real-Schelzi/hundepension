/* Ein Tag im Park – Scroll-Szene auf der echten Luftaufnahme der Villa.
   Beim Scrollen läuft der Tagesablauf von 06.30 bis zum Abend: Die Kamera schwebt wie eine Drohne
   über das Gelände, das Licht wechselt von Morgennebel über Mittagssonne und goldene Stunde bis
   zum Abend mit warm erleuchteten Fenstern und Glühwürmchen.
   Rendering per WebGL (ein Fragment-Shader auf dem Foto). Ohne WebGL: CSS-Transform und -Filter.
   Bei «Bewegung reduzieren» wird die Szene als ruhige, statische Liste gezeigt (siehe CSS .day--static). */
(() => {
  'use strict';
  const root = document.querySelector('[data-day]');
  if (!root) return;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) { root.classList.add('day--static'); return; }

  const steps = JSON.parse(root.dataset.day);
  const panels = [...root.querySelectorAll('.day__panel')];
  const N = panels.length; // Startbild + Abschnitte des Tages
  const rail = [...root.querySelectorAll('[data-rail]')];
  const timeEl = root.querySelector('[data-day-time]');
  const sunEl = root.querySelector('[data-day-sun]');
  const canvas = root.querySelector('[data-day-canvas]');
  const photo = root.querySelector('.day__img');

  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const smooth = (t) => t * t * (3 - 2 * t);
  const hm = (s) => { const [h, m] = s.split(':').map(Number); return h + m / 60; };

  /* ---------- Stundenverlauf über den Scrollweg ---------- */
  const ranges = steps.map((s) => {
    if (s.from && s.to) return [hm(s.from), hm(s.to)];
    if (s.from) return [hm(s.from), hm(s.from) + 0.5];
    return [18.9, 21.4];
  });
  const z = window.HP_ZURICH ? window.HP_ZURICH() : null;
  const live = z ? z.min / 60 : 10;
  const firstHour = ranges[0][0];
  const liveTarget = live <= 12 ? firstHour : firstHour + 24; // abends vorwärts durch die Nacht zum Morgen

  const hourPts = [];
  ranges.forEach(([a, b], k) => {
    const i = k + 1;
    hourPts.push([(i + 0.12) / N, a], [(i + 0.88) / N, b]);
  });
  function hourAt(p) {
    const p0 = 0.5 / N;
    const p1 = hourPts[0][0];
    if (p <= p0) return live;
    if (p < p1) return lerp(live, liveTarget, smooth((p - p0) / (p1 - p0))) % 24;
    for (let i = 0; i < hourPts.length - 1; i++) {
      const [pa, ha] = hourPts[i];
      const [pb, hb] = hourPts[i + 1];
      if (p <= pb) return lerp(ha, hb, clamp((p - pa) / (pb - pa), 0, 1));
    }
    return hourPts[hourPts.length - 1][1];
  }

  /* ---------- Kamerafahrt ---------- */
  const camPts = [[0, [0.5, 0.5, 1.0]], [0.45 / N, [0.5, 0.5, 1.02]]];
  steps.forEach((s, k) => camPts.push([(k + 1.5) / N, s.cam]));
  function camAt(p) {
    if (p <= camPts[0][0]) return camPts[0][1];
    for (let i = 0; i < camPts.length - 1; i++) {
      const [pa, ca] = camPts[i];
      const [pb, cb] = camPts[i + 1];
      if (p <= pb) {
        const t = smooth(clamp((p - pa) / (pb - pa), 0, 1));
        return [lerp(ca[0], cb[0], t), lerp(ca[1], cb[1], t), lerp(ca[2], cb[2], t)];
      }
    }
    return camPts[camPts.length - 1][1];
  }

  /* ---------- Lichtstimmungen nach Uhrzeit ----------
     [Stunde, Belichtung, Kontrast, Sättigung, Tönung rgb, Schattenfarbe rgb, Nebel, Nacht, Sonnenstärke, Sonnenfarbe rgb, Sonne x, y] */
  const NIGHT = [0.30, 1.05, 0.48, [0.56, 0.68, 1.0], [0.012, 0.028, 0.065], 0.18, 1.0, 0.0, [0.9, 0.5, 0.4], 0.5, 1.3];
  const LOOKS = [
    [0, ...NIGHT],
    [5.2, 0.33, 1.05, 0.5, [0.58, 0.70, 1.0], [0.012, 0.03, 0.065], 0.3, 1.0, 0.0, [1.0, 0.6, 0.5], -0.1, 0.9],
    [6.3, 0.56, 1.02, 0.62, [0.84, 0.80, 0.98], [0.03, 0.03, 0.06], 0.95, 0.55, 0.32, [1.0, 0.62, 0.52], -0.12, 0.92],
    [7.3, 0.80, 1.0, 0.82, [1.0, 0.90, 0.86], [0.02, 0.02, 0.035], 0.8, 0.08, 0.45, [1.0, 0.74, 0.52], -0.05, 0.85],
    [8.6, 0.97, 1.02, 0.95, [1.02, 0.98, 0.93], [0, 0, 0], 0.35, 0.0, 0.26, [1.0, 0.86, 0.66], 0.1, 0.95],
    [10.2, 1.04, 1.04, 1.04, [1.0, 1.0, 0.99], [0, 0, 0], 0.06, 0.0, 0.14, [1.0, 0.95, 0.86], 0.3, 1.1],
    [12.5, 1.07, 1.06, 1.06, [1.02, 1.01, 0.985], [0, 0, 0], 0.0, 0.0, 0.1, [1.0, 0.97, 0.9], 0.5, 1.25],
    [15.0, 1.04, 1.06, 1.1, [1.06, 1.0, 0.92], [0, 0, 0], 0.0, 0.0, 0.2, [1.0, 0.86, 0.62], 0.85, 1.05],
    [17.2, 0.95, 1.08, 1.14, [1.15, 0.95, 0.77], [0.02, 0.01, 0.0], 0.0, 0.0, 0.52, [1.0, 0.62, 0.3], 1.08, 0.82],
    [18.3, 0.74, 1.06, 0.98, [1.06, 0.82, 0.78], [0.02, 0.015, 0.03], 0.08, 0.3, 0.46, [1.0, 0.46, 0.34], 1.12, 0.68],
    [19.2, 0.5, 1.04, 0.72, [0.72, 0.71, 0.98], [0.015, 0.025, 0.06], 0.16, 0.82, 0.16, [0.95, 0.42, 0.5], 1.15, 0.6],
    [20.4, 0.34, 1.05, 0.52, [0.58, 0.69, 1.0], [0.012, 0.03, 0.065], 0.2, 1.0, 0.0, [0.9, 0.5, 0.4], 1.1, 0.9],
    [24, ...NIGHT],
  ];
  function lookAt(h) {
    h = ((h % 24) + 24) % 24;
    let i = 0;
    while (i < LOOKS.length - 2 && LOOKS[i + 1][0] <= h) i++;
    const A = LOOKS[i];
    const B = LOOKS[i + 1];
    const t = clamp((h - A[0]) / (B[0] - A[0]), 0, 1);
    const mix = (a, b) => (Array.isArray(a) ? a.map((v, k) => lerp(v, b[k], t)) : lerp(a, b, t));
    const r = A.slice(1).map((v, k) => mix(v, B[k + 1]));
    return { exp: r[0], con: r[1], sat: r[2], tint: r[3], lift: r[4], mist: r[5], night: r[6], sun: r[7], sunCol: r[8], sunPos: [r[9], r[10]] };
  }

  /* ---------- Scroll-Zustand ---------- */
  let pTarget = 0;
  let pSmooth = 0;
  let active = -1;
  function readScroll() {
    const rect = root.getBoundingClientRect();
    const total = root.offsetHeight - innerHeight;
    pTarget = clamp(-rect.top / total, 0, 1);
  }
  function setActive(i) {
    if (i === active) return;
    active = i;
    panels.forEach((p, k) => p.classList.toggle('is-active', k === i));
    rail.forEach((r, k) => { r.classList.toggle('is-active', k + 1 === i); r.classList.toggle('is-done', k + 1 < i); });
    root.classList.toggle('is-touring', i > 0);
  }
  const fmtTime = (h) => {
    let m = Math.round((((h % 24) + 24) % 24) * 12) * 5;
    m %= 1440;
    return `${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`;
  };

  // Anker wie #tag-ankommen auf die passende Scrollposition lenken
  function scrollToPanel(i, smoothScroll = true) {
    const total = root.offsetHeight - innerHeight;
    const top = root.offsetTop + total * ((i + 0.2) / N);
    window.scrollTo({ top, behavior: smoothScroll ? 'smooth' : 'auto' });
  }
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href^="#tag"]');
    if (!a) return;
    const id = a.getAttribute('href').slice(1);
    const i = panels.findIndex((p) => p.id === id);
    if (i < 0) return;
    e.preventDefault();
    scrollToPanel(i);
    history.replaceState(null, '', `#${id}`);
  });
  if (location.hash.startsWith('#tag-')) {
    const i = panels.findIndex((p) => p.id === location.hash.slice(1));
    if (i > 0) requestAnimationFrame(() => scrollToPanel(i, false));
  }

  /* ---------- WebGL ---------- */
  const VERT = 'attribute vec2 aPos;varying vec2 vUv;void main(){vUv=aPos*.5+.5;gl_Position=vec4(aPos,0.,1.);}';
  const FRAG = `
precision highp float;
varying vec2 vUv;
uniform sampler2D uImg, uMask;
uniform vec2 uRes, uSunPos;
uniform float uImgAspect, uTime, uExposure, uContrast, uSat, uMist, uNight, uSunStr;
uniform vec3 uCam, uTint, uLift, uSunCol;
uniform vec3 uFly[40];

float hash(vec2 p){ p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
float noise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1., 0.)), f.x), mix(hash(i + vec2(0., 1.)), hash(i + vec2(1., 1.)), f.x), f.y); }
float fbm(vec2 p){ float v = 0.0, a = 0.5; for (int i = 0; i < 5; i++){ v += a * noise(p); p *= 2.03; a *= 0.5; } return v; }

void main(){
  float ca = uRes.x / uRes.y;
  vec2 s = ca > uImgAspect ? vec2(1.0, uImgAspect / ca) : vec2(ca / uImgAspect, 1.0);
  vec2 uv = (vUv - 0.5) * s / uCam.z + uCam.xy;
  vec3 src = texture2D(uImg, uv).rgb;
  float l = dot(src, vec3(0.2126, 0.7152, 0.0722));
  vec3 c = mix(vec3(l), src, uSat);
  c = (c - 0.5) * uContrast + 0.5;
  c = c * uExposure * uTint + uLift * (1.0 - l);

  vec2 sp = (vUv - uSunPos) * vec2(ca, 1.0);
  c += uSunCol * uSunStr * exp(-dot(sp, sp) * 1.3) * (0.3 + 0.7 * l);

  float green = smoothstep(0.015, 0.09, src.g - max(src.r, src.b));
  if (uMist > 0.001) {
    vec2 q = uv * vec2(3.0 * uImgAspect, 3.0);
    float n = fbm(q + vec2(uTime * 0.016, uTime * 0.005)) * 0.62 + fbm(q * 1.7 - vec2(uTime * 0.011, 0.0)) * 0.48;
    float m = smoothstep(0.42, 0.86, n) * uMist * (0.5 + 0.5 * green);
    vec3 mc = mix(vec3(0.80, 0.85, 0.93), vec3(1.0, 0.88, 0.80), clamp(uSunStr * 1.6, 0.0, 1.0));
    c = mix(c, mc * max(uExposure, 0.6), m * 0.6);
  }

  vec3 mk = texture2D(uMask, uv).rgb;
  float flick = 0.95 + 0.05 * sin(uTime * 2.1 + uv.x * 37.0);
  float pane = smoothstep(0.75, 0.15, l);                      // dunkle Scheiben leuchten, helle Rahmen kaum
  c += uNight * (mk.r * pane * vec3(1.0, 0.72, 0.38) * 1.35 * flick + mk.g * vec3(1.0, 0.58, 0.24) * 0.3);

  if (uNight > 0.25) {
    float f = 0.0;
    vec2 pa = vec2(uImgAspect, 1.0) * uCam.z;
    for (int i = 0; i < 40; i++) {
      vec3 fl = uFly[i];
      vec2 p = fl.xy + 0.012 * vec2(sin(uTime * 0.33 + fl.z * 6.3), cos(uTime * 0.26 + fl.z * 9.1));
      vec2 d = (uv - p) * pa;
      float r2 = dot(d, d);
      float tw = 0.5 + 0.5 * sin(uTime * (1.1 + fl.z * 1.7) + fl.z * 40.0);
      tw = tw * tw * tw;
      f += tw * (exp(-r2 * 24000.0) * 1.6 + exp(-r2 * 1500.0) * 0.16);
    }
    c += vec3(0.82, 1.0, 0.45) * f * smoothstep(0.25, 0.9, uNight);
  }

  vec2 vq = (vUv - 0.5) * vec2(ca, 1.0);
  c *= mix(1.0, smoothstep(1.25, 0.25, length(vq)), 0.26 + 0.4 * uNight);
  c += (hash(vUv * uRes + fract(uTime)) - 0.5) * 0.026;
  gl_FragColor = vec4(c, 1.0);
}`;

  let gl = null;
  let prog = null;
  let U = {};
  let imgAspect = 4 / 3;
  let ready = false;
  let scale = 1;

  function loadImage(srcUrl) {
    return new Promise((res, rej) => {
      const im = new Image();
      im.decoding = 'async';
      im.onload = () => res(im);
      im.onerror = rej;
      im.src = srcUrl;
    });
  }

  function pickFireflies(im) {
    const w = 200;
    const h = Math.round(w * im.naturalHeight / im.naturalWidth);
    const cv = document.createElement('canvas');
    cv.width = w; cv.height = h;
    const cx = cv.getContext('2d', { willReadFrequently: true });
    cx.drawImage(im, 0, 0, w, h);
    const d = cx.getImageData(0, 0, w, h).data;
    const cand = [];
    for (let y = 2; y < h - 2; y++) {
      for (let x = 2; x < w - 2; x++) {
        const k = (y * w + x) * 4;
        const r = d[k], g = d[k + 1], b = d[k + 2];
        if (g > r * 1.06 && g > b * 1.18 && g > 45 && g < 210) cand.push([x / w, 1 - y / h]);
      }
    }
    let seed = 20260;
    const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
    const out = new Float32Array(120);
    for (let i = 0; i < 40; i++) {
      const c = cand.length ? cand[Math.floor(rnd() * cand.length)] : [rnd(), rnd()];
      out.set([c[0], c[1], rnd()], i * 3);
    }
    return out;
  }

  function texture(im, unit) {
    const t = gl.createTexture();
    gl.activeTexture(gl.TEXTURE0 + unit);
    gl.bindTexture(gl.TEXTURE_2D, t);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, im);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    return t;
  }

  async function initGL() {
    gl = canvas.getContext('webgl', { antialias: false, alpha: false, powerPreference: 'high-performance', preserveDrawingBuffer: false });
    if (!gl) throw new Error('kein WebGL');
    const sh = (type, src) => {
      const s = gl.createShader(type);
      gl.shaderSource(s, src);
      gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
      return s;
    };
    prog = gl.createProgram();
    gl.attachShader(prog, sh(gl.VERTEX_SHADER, VERT));
    gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FRAG));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
    gl.useProgram(prog);
    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(prog, 'aPos');
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    ['uImg', 'uMask', 'uRes', 'uSunPos', 'uImgAspect', 'uTime', 'uExposure', 'uContrast', 'uSat', 'uMist', 'uNight',
      'uSunStr', 'uCam', 'uTint', 'uLift', 'uSunCol', 'uFly'].forEach((n) => { U[n] = gl.getUniformLocation(prog, n); });

    const big = innerWidth > 900 ? 2000 : 1600;
    const srcUrl = (photo.currentSrc || photo.src).replace(/-\d+\.webp$/, `-${big}.webp`);
    const [im, mask] = await Promise.all([loadImage(srcUrl), loadImage('/assets/img/park-lichter.png')]);
    imgAspect = im.naturalWidth / im.naturalHeight;
    texture(im, 0);
    texture(mask, 1);
    gl.uniform1i(U.uImg, 0);
    gl.uniform1i(U.uMask, 1);
    gl.uniform1f(U.uImgAspect, imgAspect);
    gl.uniform3fv(U.uFly, pickFireflies(im));
    canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault(); ready = false; root.classList.remove('is-gl'); });
    resize();
    ready = true;
    draw(performance.now() / 1000, true);
    root.classList.add('is-gl');
  }

  function resize() {
    if (!gl) return;
    const dprMax = innerWidth < 900 ? 1.25 : 1.6;
    const dpr = Math.min(devicePixelRatio || 1, dprMax) * scale;
    const w = Math.round(canvas.clientWidth * dpr);
    const h = Math.round(canvas.clientHeight * dpr);
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
    gl.viewport(0, 0, w, h);
  }

  function camView(cam, t) {
    const ca = canvas.clientWidth / canvas.clientHeight || 1;
    const s = ca > imgAspect ? [1, imgAspect / ca] : [ca / imgAspect, 1];
    const zoom = Math.max(1, cam[2]);
    const hx = s[0] / (2 * zoom);
    const hy = s[1] / (2 * zoom);
    const drift = 0.004 / zoom;
    const x = clamp(cam[0] + Math.sin(t * 0.07) * drift, hx, 1 - hx);
    const y = clamp(1 - cam[1] + Math.cos(t * 0.05) * drift, hy, 1 - hy);
    return [x, y, zoom];
  }

  function draw(t, force) {
    const h = hourAt(pSmooth);
    const L = lookAt(h);
    const cam = camView(camAt(pSmooth), t);
    if (ready && gl) {
      gl.uniform2f(U.uRes, canvas.width, canvas.height);
      gl.uniform1f(U.uTime, t);
      gl.uniform1f(U.uExposure, L.exp);
      gl.uniform1f(U.uContrast, L.con);
      gl.uniform1f(U.uSat, L.sat);
      gl.uniform3fv(U.uTint, L.tint);
      gl.uniform3fv(U.uLift, L.lift);
      gl.uniform1f(U.uMist, L.mist);
      gl.uniform1f(U.uNight, L.night);
      gl.uniform1f(U.uSunStr, L.sun);
      gl.uniform3fv(U.uSunCol, L.sunCol);
      gl.uniform2fv(U.uSunPos, L.sunPos);
      gl.uniform3fv(U.uCam, cam);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    } else if (force || !ready) {
      // Ersatz ohne WebGL: Bildausschnitt und Lichtstimmung per CSS
      const warm = clamp(L.tint[0] - L.tint[2], -0.5, 0.5);
      photo.style.transformOrigin = '50% 50%';
      photo.style.transform = `scale(${cam[2].toFixed(3)}) translate(${((0.5 - cam[0]) * 100).toFixed(2)}%, ${((cam[1] - 0.5) * 100).toFixed(2)}%)`;
      photo.style.filter = `brightness(${L.exp.toFixed(3)}) saturate(${L.sat.toFixed(3)}) contrast(${L.con.toFixed(3)}) sepia(${Math.max(0, warm * 0.9).toFixed(3)}) hue-rotate(${(Math.min(0, warm) * 30).toFixed(1)}deg)`;
    }
    if (timeEl) timeEl.textContent = fmtTime(h);
    if (sunEl) {
      const hh = ((h % 24) + 24) % 24;
      sunEl.style.setProperty('--sun', `${(clamp((hh - 6) / 14.5, 0, 1) * 100).toFixed(1)}%`);
      sunEl.firstElementChild.style.opacity = hh > 20.6 || hh < 5.6 ? '0' : '1';
    }
  }

  /* ---------- Schleife ---------- */
  let visible = true;
  let last = performance.now();
  let frames = 0;
  let acc = 0;
  let raf = 0;
  function loop(now) {
    raf = 0;
    if (!visible) return;
    const dt = Math.min(0.1, (now - last) / 1000);
    last = now;
    readScroll(); // zusätzlich pro Frame – robust gegen gedrosselte Scroll-Events (z. B. iOS)
    pSmooth += (pTarget - pSmooth) * (1 - Math.exp(-dt * 5.5));
    if (Math.abs(pTarget - pSmooth) < 1e-5) pSmooth = pTarget;
    setActive(clamp(Math.floor(pTarget * N), 0, N - 1));
    draw(now / 1000);
    // Auflösung anpassen, falls das Gerät zu langsam ist
    if (ready && scale > 0.5) {
      frames++; acc += dt;
      if (frames === 90) {
        if (acc / frames > 1 / 40) { scale = Math.max(0.5, scale - 0.25); resize(); }
        frames = 0; acc = 0;
      }
    }
    raf = requestAnimationFrame(loop);
  }
  const kick = () => { if (!raf && visible) { last = performance.now(); raf = requestAnimationFrame(loop); } };
  addEventListener('scroll', () => { readScroll(); kick(); }, { passive: true });
  addEventListener('resize', () => { readScroll(); resize(); kick(); });
  new IntersectionObserver((en) => { visible = en[0].isIntersecting; kick(); }).observe(root);
  document.addEventListener('visibilitychange', () => { visible = !document.hidden; kick(); });

  readScroll();
  pSmooth = pTarget;
  setActive(clamp(Math.floor(pTarget * N), 0, N - 1));
  draw(0, true);
  kick();
  initGL().catch(() => { gl = null; ready = false; draw(0, true); });
})();
