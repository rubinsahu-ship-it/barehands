// Simulated-hand tests for the NIMBUS pinch engine.
// Usage: node nimbus/ui/pinch_test.js nimbus/ui/pinch.js   (SEED=n for another noise run)
const fs = require("fs");
const store = {};
globalThis.localStorage = { getItem: k => store[k] ?? null, setItem: (k, v) => { store[k] = v; }, removeItem: k => { delete store[k]; } };
const SRC = fs.readFileSync(process.argv[2], "utf8");
function fresh() { for (const k in store) delete store[k]; eval(SRC); return globalThis.NimbusPinch; }

let seed = +(process.env.SEED || 7);
const rnd = () => { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; };
const gauss = () => { let u = 0; while (!u) u = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * rnd()); };

const W = 1280, H = 720, PPM = 1500;
const BASE = [
  [0, 0, 0], [-0.025, -0.02, -0.01], [-0.045, -0.045, -0.015], [-0.058, -0.068, -0.02], [-0.065, -0.09, -0.022],
  [-0.025, -0.09, 0], [-0.028, -0.13, 0], [-0.029, -0.152, 0], [-0.03, -0.172, 0],
  [0, -0.093, 0], [0, -0.137, 0], [0, -0.162, 0], [0, -0.184, 0],
  [0.02, -0.088, 0], [0.022, -0.128, 0], [0.023, -0.15, 0], [0.024, -0.168, 0],
  [0.038, -0.078, 0], [0.042, -0.105, 0], [0.044, -0.12, 0], [0.045, -0.135, 0]];
// pose with a thumb-tip/index-tip gap of g metres; the index curls down onto a still thumb
function hand(g, ox = 0) {
  const L = BASE.map(p => p.slice());
  const tt = [-0.052, -0.105, -0.03], u = [0.25, -0.97, 0];
  L[4] = tt; L[3] = [tt[0] - 0.012, tt[1] + 0.02, tt[2] + 0.004];
  L[8] = [tt[0] + u[0] * g, tt[1] + u[1] * g, tt[2]];
  L[7] = [L[8][0] + 0.006, L[8][1] - 0.018, L[8][2] + 0.008];
  L[6] = [-0.028, -0.13 + Math.max(0, 0.05 - g) * 0.2, 0.004];
  return L.map(([x, y, z]) => [x + ox, y, z]);
}
// bias = how far apart this camera "sees" touching fingertips (a real tracker never reads 0)
function observe(L, noise, bias) {
  const n = noise;
  const wl = L.map(([x, y, z]) => ({ x: x + gauss() * 0.0025 * n, y: y + gauss() * 0.0025 * n, z: z + gauss() * 0.004 * n }));
  const lms = L.map(([x, y, z]) => ({ x: (W / 2 + x * PPM + gauss() * 1.5 * n) / W, y: (H / 2 + y * PPM + gauss() * 1.5 * n) / H, z: (z * PPM + gauss() * 4 * n) / W }));
  if (bias) { const u = [0.25, -0.97]; for (const P of [wl]) { P[8].x += u[0] * bias; P[8].y += u[1] * bias; }
              lms[8].x += u[0] * bias * PPM / W; lms[8].y += u[1] * bias * PPM / H; }
  return { wl, lms };
}

function sim(P, script, ms, o = {}) {
  const st = {}; let on = 0, rel = 0; const onsets = [];
  let aim = null, maxTravel = 0;
  for (let t = 0; t < ms; t += 33.3) {
    const s = script(t);
    const { wl, lms } = observe(hand(s.g, s.ox || 0), o.noise || 1, o.bias || 0);
    const m = P.metrics(lms, wl, W, H);
    const scr = p => ({ x: (1 - p.x) * W, y: p.y * H });
    const a5 = scr(lms[5]), a9 = scr(lms[9]), t4 = scr(lms[4]), t8 = scr(lms[8]);
    const c = P.cursor(st, { x: (a5.x + a9.x) / 2, y: (a5.y + a9.y) / 2 }, { x: (t4.x + t8.x) / 2, y: (t4.y + t8.y) / 2 }, m.r, t);
    const out = P.step(st, m, t, { garbage: !!s.garbage, holding: false, speed: s.speed || 0, legacyIn: false, legacyRel: true });
    if (out.onset) { on++; onsets.push(Math.round(t)); }
    if (out.release) rel++;
    if (s.aim) { if (!aim) aim = { ...c }; maxTravel = Math.max(maxTravel, Math.hypot(c.x - aim.x, c.y - aim.y)); } else aim = null;
  }
  return { on, rel, onsets, maxTravel };
}
// a tap: open, close in 100 ms, hold `hold` ms, open in 100 ms. Each cycle is 800 ms.
const taps = (touchGap, hold = 150) => t => { const k = t % 800;
  const g = k < 450 ? 0.08 : k < 550 ? 0.08 - (k - 450) / 100 * (0.08 - touchGap) : k < 550 + hold ? touchGap
          : k < 650 + hold ? touchGap + (k - 550 - hold) / 100 * (0.08 - touchGap) : 0.08;
  return { g, aim: k >= 300 && k < 650 + hold }; };
const hold = (g, lead = 500) => t => ({ g: t < lead ? 0.08 : g });

const results = [];
const ok = (name, cond, detail) => results.push([cond ? "PASS" : "FAIL", name, detail]);

// 1. a normal hand (touch reads ~1.2 cm): the very first pinch already clicks
{ const P = fresh(); const r = sim(P, taps(0.012), 800);
  ok("first pinch of a fresh session clicks", r.on === 1, `${r.on} click(s), threshold ${P.cfg.tIn}`); }
// 2. quick taps with only 70 ms of contact all click, one click each
{ const P = fresh(); const r = sim(P, taps(0.012, 70), 8000);
  ok("quick taps (70 ms contact): at least 9 of 10 click, never a double", r.on >= 9 && r.on === r.rel, `${r.on} clicks / ${r.rel} releases`);
  ok("cursor holds still through each tap", r.maxTravel < 14, `moved ${r.maxTravel.toFixed(1)} px`);
  ok("it learned this hand's touch", P.cfg.learned > 0 && P.cfg.tIn < 0.3, `touch ${P.cfg.touch && P.cfg.touch.toFixed(2)} -> click below ${P.cfg.tIn}, release above ${P.cfg.tOut}`);
  // 3. after learning, near-misses don't click
  for (const g of [0.026, 0.030, 0.035]) { const n = sim(P, hold(g), 4000);
    ok(`after learning, fingers ${(g * 100).toFixed(1)} cm apart never click`, n.on === 0, `${n.on} clicks`); }
  const nn = sim(P, t => ({ g: t < 500 ? 0.08 : 0.031 + 0.005 * Math.sin(t / 300) }), 8000, { noise: 2 });
  ok("after learning, hovering 2.6-3.6 cm with double noise = 0 clicks", nn.on === 0, `${nn.on} clicks`);
  const sh = sim(P, t => ({ g: t < 500 ? 0.08 : 0.014 + 0.004 * Math.sin(t / 90) }), 6000, { noise: 2 });
  ok("long shaky hold with double noise = 1 click", sh.on === 1 && sh.rel === 0, `${sh.on} clicks / ${sh.rel} releases`);
  const dr = sim(P, t => ({ g: t < 500 ? 0.08 : 0.012, ox: t < 600 ? 0 : (t - 600) / 1000 * 0.4, speed: t > 600 ? 600 : 0 }), 2500);
  ok("dragging while pinched does not drop", dr.on === 1 && dr.rel === 0, `${dr.on} / ${dr.rel}`);
  const gl = sim(P, t => ({ g: t < 500 ? 0.08 : t < 2500 ? 0.012 : t < 3500 ? 0.08 : 0.012, garbage: t > 1200 && t < 1400 }), 4500);
  ok("tracking glitch mid-pinch does not re-click", gl.on === 2, `${gl.on} clicks (2 expected: before, and after the real reopen)`);
  const ar = sim(P, t => ({ g: t < 1500 ? 0.012 : t < 2000 ? 0.08 : 0.012 }), 3000);
  ok("hand arriving already pinched waits for an open hand", ar.on === 1 && ar.onsets[0] > 2000, `${ar.on} at ${ar.onsets}`); }
// 4. a camera that reads touching fingertips as ~3 cm apart: clicks from the start and keeps clicking
{ const P = fresh(); const r = sim(P, taps(0.012), 8000, { bias: 0.018 });
  const late = r.onsets.filter(o => o > 1600).length;
  ok("camera that reads touch as ~3 cm: from the 3rd tap on, at least 7 of 8 click", late >= 7, `${r.on}/10 clicks, ${late}/8 from the 3rd tap, learned click line ${P.cfg.tIn}`); }
// 5. a camera that reads touch as ~3.5 cm: may miss at first, learns within a few pinches
{ const P = fresh(); const r = sim(P, taps(0.012), 8000, { bias: 0.024 });
  const late = r.onsets.filter(o => o > 2400).length;
  ok("camera that reads touch as ~3.5 cm: learns, then most taps click", late >= 5, `${r.on} clicks total, ${late}/7 from the 4th tap, click line ${P.cfg.tIn}`); }
// 6. image-only fallback (no 3D world landmarks)
{ const P = fresh(); P.calibrate(0.15);
  const run = (g) => { const st = {}; let on = 0;
    for (let t = 0; t < 2000; t += 33.3) { const { lms } = observe(hand(t < 500 ? 0.08 : g), 1, 0);
      if (P.step(st, P.metrics(lms, null, W, H), t, { garbage: false, holding: false, speed: 0 }).onset) on++; } return on; };
  ok("image-only fallback: touch clicks, near-miss doesn't", run(0.010) === 1 && run(0.035) === 0, `${run(0.010)} / ${run(0.035)}`); }
// 7. calibration
{ const P = fresh(); const c = P.fromSamples(Array(20).fill(1.0), Array(20).fill(0.16));
  ok("calibration accepts open 1.0 / touch 0.16", c.ok, JSON.stringify(c));
  ok("calibration rejects a hand that never opened", !P.fromSamples(Array(20).fill(0.4), Array(20).fill(0.38)).ok, "");
  P.calibrate(0.16); ok("calibrated click line sits just above the touch", P.cfg.tIn > 0.24 && P.cfg.tIn < 0.3, `click < ${P.cfg.tIn}, release > ${P.cfg.tOut}`);
  const raw = store["nimbus.pinch.v2"]; const P2 = fresh(); store["nimbus.pinch.v2"] = raw; eval(SRC);
  ok("learned touch survives a reload", globalThis.NimbusPinch.cfg.touch === 0.16, raw); }

results.forEach(([s, n, d]) => console.log(`${s}  ${n}  (${d})`));
const fails = results.filter(r => r[0] === "FAIL").length;
console.log(`\n${results.length - fails}/${results.length} passed`);
process.exit(fails ? 1 : 0);
