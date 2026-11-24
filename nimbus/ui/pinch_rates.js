// Click / false-click rates over 40 noise seeds. Usage: node nimbus/ui/pinch_rates.js nimbus/ui/pinch.js nimbus/ui/pinch_test.js
const fs = require("fs");
let src = fs.readFileSync(process.argv[3], "utf8");
src = src.slice(0, src.indexOf("const results = [];"));
const out = { quick: [0, 0], normal: [0, 0], bias3: [0, 0], bias35: [0, 0], near: [0, 0], hover2x: [0, 0] };
for (let s = 1; s <= 40; s++) {
  process.env.SEED = s;
  const run = new Function("require", "process", "argv", src + `
    const R = {};
    { const P = fresh(); const r = sim(P, taps(0.012, 70), 8000); R.quick = r.on; }
    { const P = fresh(); const r = sim(P, taps(0.012, 150), 8000); R.normal = r.on;
      R.near = [0.022, 0.026, 0.030].reduce((a, g) => a + sim(P, hold(g), 3000).on, 0);
      R.hover2x = sim(P, t => ({ g: t < 500 ? 0.08 : 0.031 + 0.005 * Math.sin(t / 300) }), 8000, { noise: 2 }).on; }
    { const P = fresh(); R.bias3 = sim(P, taps(0.012), 8000, { bias: 0.018 }).on; }
    { const P = fresh(); R.bias35 = sim(P, taps(0.012), 8000, { bias: 0.024 }).on; }
    return R;`);
  const R = run(require, process, process.argv);
  out.quick[0] += R.quick; out.quick[1] += 10; out.normal[0] += R.normal; out.normal[1] += 10;
  out.bias3[0] += R.bias3; out.bias3[1] += 10; out.bias35[0] += R.bias35; out.bias35[1] += 10;
  out.near[0] += R.near; out.near[1] += 3; out.hover2x[0] += R.hover2x; out.hover2x[1] += 1;
}
const pct = ([a, b]) => `${a}/${b} (${(100 * a / b).toFixed(1)}%)`;
console.log("taps that clicked, normal tap (150 ms touch):      ", pct(out.normal));
console.log("taps that clicked, quick flick (70 ms touch):      ", pct(out.quick));
console.log("taps that clicked, camera reads touch as ~3 cm:    ", pct(out.bias3));
console.log("taps that clicked, camera reads touch as ~3.5 cm:  ", pct(out.bias35));
console.log("near-miss holds (2.2 / 2.6 / 3.0 cm) that clicked: ", pct(out.near));
console.log("7.5 s hovers 2.6-3.6 cm, double noise, any click:  ", pct(out.hover2x));
