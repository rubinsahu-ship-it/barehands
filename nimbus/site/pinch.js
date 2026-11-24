/* NIMBUS pinch engine. Made by RUBIN.
   Clicks when the thumb tip and the index tip meet, and learns what
   "touching" looks like for this hand on this camera:
   - Gap: thumb-tip to index-tip distance divided by the palm's own size,
     from the 3D world landmarks and the image landmarks together.
   - Learns your touch: every quick close of the fingers leaves a "valley"
     (the smallest gap reached). The typical valley is your real touching
     distance, and the click threshold sits just above it. It starts as
     forgiving as the original board and tightens after a few pinches.
   - Fast: a 3-frame median kills single-frame tracker spikes, and the
     click fires as soon as two of the last three frames say "touching".
   - One click per pinch: it opens only above a higher release line
     (hysteresis), and after a release or a tracking drop the fingers must
     open again before the next click.
   - Steady cursor: the cursor rides the knuckles while the fingers close
     (pinching doesn't drag it onto the next key), smoothed by a One Euro
     filter (Casiez, Roussel and Vogel, CHI 2012).
   Plain script; exposes window.NimbusPinch. */
(function (G) {
  "use strict";
  const KEY = "nimbus.pinch.v2";
  const DEF = { tIn: 0.40, tOut: 0.52, refractMs: 120, freezeHi: 0.85, open: 0.95 };
  const cfg = Object.assign({}, DEF, { calibrated: 0, learned: 0, touch: null });
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const d3 = (a, b, zw) => Math.hypot(a.x - b.x, a.y - b.y, ((a.z || 0) - (b.z || 0)) * zw);

  /* ---- learned touch level -> thresholds ---- */
  const valleys = [];
  function applyTouch(touch) {
    cfg.touch = touch;
    cfg.tIn = +clamp(touch + 0.10, 0.24, 0.52).toFixed(3);
    cfg.tOut = +clamp(Math.max(cfg.tIn + 0.12, cfg.tIn * 1.3), 0.36, 0.68).toFixed(3);
  }
  function persist() {
    try { G.localStorage.setItem(KEY, JSON.stringify({ touch: cfg.touch, cal: cfg.calibrated, t: Date.now() })); } catch (e) {}
  }
  try {
    const s = JSON.parse((G.localStorage && G.localStorage.getItem(KEY)) || "null");
    if (s && s.touch > 0.03 && s.touch < 0.5) {
      applyTouch(s.touch); cfg.calibrated = s.cal || 0;
      valleys.push(s.touch, s.touch);          // a prior, not a cage: fresh pinches still move it
    }
  } catch (e) {}
  function learn(v) {
    valleys.push(v); if (valleys.length > 9) valleys.shift();
    if (valleys.length >= 2) {
      const s = valleys.slice().sort((a, b) => a - b);
      applyTouch(s[Math.floor(s.length / 2)]);
      cfg.learned++;
      persist();
    }
  }

  /* ---- One Euro filter ---- */
  function alpha(cutoff, dt) { const tau = 1 / (2 * Math.PI * cutoff); return 1 / (1 + tau / dt); }
  function OneEuro(minCutoff, beta, dCutoff) { this.mc = minCutoff; this.b = beta; this.dc = dCutoff || 1; this.xp = null; this.dp = 0; this.tp = null; }
  OneEuro.prototype.filter = function (x, tMs) {
    if (this.tp == null) { this.tp = tMs; this.xp = x; this.dp = 0; return x; }
    const dt = Math.max(0.001, (tMs - this.tp) / 1000);
    const dx = (x - this.xp) / dt;
    const dh = this.dp + alpha(this.dc, dt) * (dx - this.dp);
    const xh = this.xp + alpha(this.mc + this.b * Math.abs(dh), dt) * (x - this.xp);
    this.xp = xh; this.dp = dh; this.tp = tMs;
    return xh;
  };

  /* ---- gap metric ---- */
  const palm = (P, zw) => (d3(P[0], P[5], zw) + d3(P[5], P[17], zw) + d3(P[0], P[17], zw)) / 3;
  function metrics(lms, wl, W, H) {
    // image landmarks: x, y in pixels; their depth guess is noisy, so it counts for a third
    const P = lms.map(p => ({ x: p.x * W, y: p.y * H, z: (p.z || 0) * W }));
    const pI = palm(P, 0.35);
    const rI = pI > 0 ? d3(P[4], P[8], 0.35) / pI : 9;
    let rW = rI, Q = P, zw = 0.35;
    if (wl && wl.length === 21) {
      const pW = palm(wl, 1);
      if (pW > 0) { rW = d3(wl[4], wl[8], 1) / pW; Q = wl; zw = 1; }
    }
    // the thumb meets the index TIP, not the side of the finger (a fist does that)
    const tip = d3(Q[4], Q[8], zw) <= 1.2 * Math.min(d3(Q[4], Q[7], zw), d3(Q[4], Q[6], zw));
    return { r: 0.5 * (rI + rW), rI, rW, tip };
  }

  /* ---- the click state machine ----
     ctx: { garbage, holding, speed, legacyIn, legacyRel }
     holding = this hand already carries something it caught without a pinch
     (the force-pull fist), which keeps the board's original fist-legal rule. */
  function step(st, m0, t, ctx) {
    const h = st.h || (st.h = []);
    h.push(m0.r); if (h.length > 3) h.shift();
    const r = h.length < 3 ? m0.r : h.slice().sort((a, b) => a - b)[1];
    st.r = r; st.raw = m0.r;

    // learn the touch level from quick closes of the fingers
    if (!ctx.garbage) {
      // a valley ends when the fingers spring back open or rest on it; record it first,
      // because one frame can jump straight from "touching" to "open"
      if (st.vArm && st.vT0 != null && (r > st.vMin + 0.1 || t - st.vMinT > 450)) {
        if (st.vMin < 0.5 && st.vMinT - st.vT0 < 500) learn(st.vMin);
        st.vArm = false; st.vT0 = null;
      }
      if (r > 0.6) { st.vArm = true; st.vT0 = null; st.vMin = 9; }
      else if (st.vArm) {
        if (st.vT0 == null) st.vT0 = t;
        if (r < st.vMin) { st.vMin = r; st.vMinT = t; }
      }
    }

    const was = !!st.pinched;
    let p = was;
    if (ctx.garbage) {
      p = false; st.armed = false; st.outRun = 0;
      if (was) st.lastRelT = t;
    } else if (!was) {
      if (!st.armed && r > cfg.tOut) st.armed = true;
      if (ctx.holding) {
        p = !!ctx.legacyIn; if (p) st.mode = "carry";
      } else {
        const bar = m0.tip ? cfg.tIn : cfg.tIn * 0.8;
        // two of the last three frames (the median) AND this frame must read "touching".
        // Well under the line = click now; only just under it (a near-miss grazing the
        // line) must hold for three frames (~0.1 s) first.
        const under = r < bar && m0.r < bar;
        const deep = r < bar - 0.05 && m0.r < bar - 0.03;
        st.shRun = under ? (st.shRun || 0) + 1 : 0;
        // before it has learned this hand, two frames are enough: the first pinch must just work
        if (st.armed && (deep || st.shRun >= (cfg.touch == null ? 2 : 3)) && t - (st.lastRelT == null ? -1e9 : st.lastRelT) > cfg.refractMs) {
          p = true; st.mode = "pinch"; st.outRun = 0;
        }
      }
    } else if (st.mode === "carry") {
      p = !ctx.legacyRel;
    } else {
      const bar = ctx.speed > 800 ? cfg.tOut * 1.25 : cfg.tOut;
      st.outRun = r > bar ? (st.outRun || 0) + 1 : 0;
      if (st.outRun >= 2 || m0.r > cfg.tOut * 1.7) p = false;
    }
    if (was && !p) { st.lastRelT = t; st.outRun = 0; st.armed = r > cfg.tOut; }
    st.pinched = p;
    return { pinched: p, onset: p && !was, release: was && !p };
  }

  /* ---- the stable cursor ----
     anchor = the knuckles (index + middle MCP), mid = between the two fingertips.
     The fingertip offset from the knuckles is followed while the hand is open
     and frozen while the fingers close or hold a pinch. */
  function cursor(st, anchor, mid, r, t) {
    const ox = mid.x - anchor.x, oy = mid.y - anchor.y;
    if (st.offX == null) { st.offX = ox; st.offY = oy; }
    let g = st.pinched ? 0 : clamp((r - cfg.tOut) / (cfg.freezeHi - cfg.tOut), 0, 1);
    g = g * g;
    if (st.rT != null && t > st.rT) { const v = (r - st.rp) / ((t - st.rT) / 1000); if (Math.abs(v) > 2.0) g = 0; }
    st.rp = r; st.rT = t;
    st.offX += (ox - st.offX) * g; st.offY += (oy - st.offY) * g;
    if (!st.fx) { st.fx = new OneEuro(1.6, 0.012, 1.0); st.fy = new OneEuro(1.6, 0.012, 1.0); }
    return { x: st.fx.filter(anchor.x + st.offX, t), y: st.fy.filter(anchor.y + st.offY, t) };
  }

  /* 0 = fingers wide open, 1 = at the click line */
  const meter = (r) => clamp((cfg.open - r) / (cfg.open - cfg.tIn), 0, 1);

  /* ---- explicit calibration: an open hand, then a touch ---- */
  function fromSamples(openS, touchS) {
    const srt = a => a.slice().sort((x, y) => x - y);
    const med = a => { const b = srt(a); return b.length ? b[Math.floor(b.length / 2)] : NaN; };
    const open = med(openS), touch = med(touchS);
    const ok = isFinite(open) && isFinite(touch) && touch < 0.5 && open > touch + 0.3;
    return { ok, open, touch };
  }
  function calibrate(touch) {
    valleys.length = 0; valleys.push(touch, touch, touch);
    applyTouch(touch); cfg.calibrated = Date.now(); persist();
  }
  function reset() {
    valleys.length = 0; cfg.touch = null; cfg.tIn = DEF.tIn; cfg.tOut = DEF.tOut; cfg.calibrated = 0; cfg.learned = 0;
    try { G.localStorage.removeItem(KEY); } catch (e) {}
  }

  G.NimbusPinch = { cfg, DEF, OneEuro, metrics, step, cursor, meter, fromSamples, calibrate, reset, valleys, calibrating: false };
})(typeof window !== "undefined" ? window : globalThis);
