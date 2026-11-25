/* NIMBUS: the PGDM intelligence layer. Made by RUBIN.
   Wake screen, HUD, sound set, a voice you can talk to, spoken explanations,
   compare mode, a quiz and the morning briefing. Drives the board through
   window.BH (defined inside the board's module). */
(() => {
  "use strict";
  const $ = (h) => { const t = document.createElement("template"); t.innerHTML = h.trim(); return t.content.firstChild; };
  const BHok = () => window.BH && typeof window.BH.openNote === "function";
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  let KB = [], QUIZ = [];
  fetch("/api/nimbus.json").then(r => r.json()).then(d => { KB = d.kb || []; QUIZ = d.quiz || []; }).catch(() => {});

  /* ================= sound set =================
     Everything is synthesised live (no audio files): glassy bells and soft
     air through a small reverb. ?sound=0 mutes it. */
  const SFX = (() => {
    const muted = /[?&]sound=0\b/.test(location.search);
    let ac = null, out = null, wet = null;
    function ctx() {
      if (muted) return null;
      try {
        if (!ac) {
          ac = new (window.AudioContext || window.webkitAudioContext)();
          out = ac.createDynamicsCompressor(); out.threshold.value = -16; out.ratio.value = 3; out.connect(ac.destination);
          const verb = ac.createConvolver(), n = Math.floor(ac.sampleRate * 2.4), b = ac.createBuffer(2, n, ac.sampleRate);
          for (let c = 0; c < 2; c++) { const d = b.getChannelData(c); for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / n, 3); }
          verb.buffer = b; wet = ac.createGain(); wet.gain.value = 0.5; wet.connect(verb); verb.connect(out);
        }
        if (ac.state === "suspended") ac.resume();
        return ac;
      } catch (e) { return null; }
    }
    function send(a, node, rev) { if (rev) { const s = a.createGain(); s.gain.value = rev; node.connect(s); s.connect(wet); } }
    function tone(f, o = {}) {
      const a = ctx(); if (!a) return;
      const t = a.currentTime + (o.delay || 0), dur = o.dur || 0.25, osc = a.createOscillator(), g = a.createGain();
      osc.type = o.type || "sine"; osc.frequency.setValueAtTime(f, t);
      if (o.to) osc.frequency.exponentialRampToValueAtTime(o.to, t + dur);
      if (o.detune) osc.detune.value = o.detune;
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(o.gain || 0.05, t + (o.attack || 0.004));
      g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      osc.connect(g); g.connect(out); send(a, g, o.rev);
      osc.start(t); osc.stop(t + dur + 0.05);
    }
    function air(o = {}) {
      const a = ctx(); if (!a) return;
      const t = a.currentTime + (o.delay || 0), dur = o.dur || 0.3, n = Math.floor(a.sampleRate * dur), b = a.createBuffer(1, n, a.sampleRate);
      const d = b.getChannelData(0); for (let i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
      const src = a.createBufferSource(); src.buffer = b;
      const f = a.createBiquadFilter(); f.type = o.ftype || "bandpass"; f.Q.value = o.q || 1.2; f.frequency.setValueAtTime(o.f || 1000, t);
      if (o.to) f.frequency.exponentialRampToValueAtTime(o.to, t + dur);
      const g = a.createGain();
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(o.gain || 0.04, t + (o.attack || 0.01));
      g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      src.connect(f); f.connect(g); g.connect(out); send(a, g, o.rev);
      src.start(t); src.stop(t + dur + 0.05);
    }
    const bell = (f, gain = 0.04, delay = 0, dur = 1.1, rev = 0.6) => {
      tone(f, { gain, delay, dur, rev });
      tone(f * 2.01, { gain: gain * 0.42, delay, dur: dur * 0.55, rev });
      tone(f * 3.98, { gain: gain * 0.16, delay, dur: dur * 0.3, rev });
    };
    const PENTA = [0, 2, 4, 7, 9];
    const note = (i) => 587.33 * Math.pow(2, (PENTA[((i % 5) + 5) % 5] + 12 * Math.floor(i / 5)) / 12);   // D major pentatonic from D5
    return {
      unlock() { ctx(); },
      boot() {   // air rising into a shimmering open chord, then a sparkle
        air({ f: 260, to: 3400, q: 0.8, dur: 2.5, gain: 0.045, attack: 1.7, rev: 0.8 });
        [146.83, 220, 293.66, 369.99, 440, 554.37].forEach((f, i) =>
          tone(f, { type: i ? "sine" : "triangle", gain: 0.03, attack: 1.0, dur: 3.4, delay: 0.14 * i, rev: 0.9, detune: i % 2 ? 7 : -7 }));
        [1174.66, 1479.98, 1760, 2349.32].forEach((f, i) => bell(f, 0.026, 2.1 + i * 0.09, 1.5, 0.9));
      },
      line() { tone(1567.98, { gain: 0.018, dur: 0.07, rev: 0.25 }); },
      ok() { tone(1975.5, { gain: 0.02, dur: 0.09, rev: 0.3 }); tone(2637, { gain: 0.016, dur: 0.12, delay: 0.05, rev: 0.3 }); },
      wake() { bell(880, 0.03, 0, 0.6, 0.5); bell(1318.5, 0.03, 0.09, 0.8, 0.5); },
      click() { tone(2349.3, { gain: 0.04, dur: 0.05, rev: 0.25 }); tone(3520, { gain: 0.018, dur: 0.035, rev: 0.2 });
                air({ f: 6000, ftype: "highpass", q: 0.7, dur: 0.02, gain: 0.012, attack: 0.001 }); },
      grab() { tone(392, { to: 587.3, gain: 0.026, dur: 0.12, attack: 0.01, rev: 0.3 }); },
      place() { tone(587.3, { to: 392, gain: 0.026, dur: 0.16, attack: 0.01, rev: 0.35 }); },
      toss() { air({ f: 500, to: 3000, q: 1.4, dur: 0.32, gain: 0.055, attack: 0.04, rev: 0.4 }); },
      poof() { air({ f: 2200, to: 300, q: 1, dur: 0.35, gain: 0.045, rev: 0.5 }); tone(784, { to: 392, gain: 0.022, dur: 0.3, rev: 0.5 }); },
      arrive() { [5, 7, 9].forEach((k, i) => bell(note(k), 0.026, i * 0.07, 0.9)); },
      pull() { air({ f: 300, to: 2400, q: 2, dur: 0.25, gain: 0.045, rev: 0.3 }); tone(220, { to: 880, type: "triangle", gain: 0.025, dur: 0.25 }); },
      key(i) { bell(note(Math.max(0, i) % 10), 0.032, 0, 0.45, 0.35); },
      alarm() { for (let r = 0; r < 3; r++) [5, 7, 9].forEach((k, i) => bell(note(k), 0.06, r * 0.8 + i * 0.12, 1.2)); },
      success() { [3, 4, 5, 6, 8].forEach((k, i) => bell(note(k), 0.03, i * 0.08, 1.0)); },
      step() { bell(note(7), 0.032, 0, 0.7); },
    };
  })();
  window.NimbusSFX = SFX;

  /* ================= wake screen ================= */
  document.body.appendChild($(`<div class="nb-vignette"></div>`));
  const init = $(`<div id="nb-init" class="nb-ui">
      <div class="nb-aurora"><i></i><i></i><i></i></div><div class="nb-stars"></div>
      <div class="nb-halo"><i class="r2"></i><i class="r1"></i><i class="r3"></i><i class="core"></i><b class="m1"></b><b class="m2"></b><b class="m3"></b></div>
      <div class="nb-title">NIMBUS</div>
      <div class="nb-sub">PGDM INTELLIGENCE</div>
      <div class="nb-btn">Wake Nimbus</div>
      <div class="nb-log"></div>
      <div class="nb-credit">MADE BY RUBIN</div>
    </div>`);
  document.body.appendChild(init);
  const log = init.querySelector(".nb-log");
  let started = false;

  async function logLine(txt, state) {
    const row = document.createElement("div"); row.innerHTML = `<span></span>`; log.appendChild(row);
    const span = row.firstChild;
    for (let i = 0; i <= txt.length; i++) { span.textContent = txt.slice(0, i); await sleep(10); }
    SFX.line();
    if (state) { await sleep(110); const b = document.createElement("b"); b.textContent = state; row.appendChild(b); SFX.ok(); }
  }

  async function start() {
    if (started) return; started = true;
    SFX.unlock();
    init.querySelector(".nb-btn").style.display = "none";
    SFX.boot();
    await sleep(500);
    await logLine("Waking core", "OK");
    await logLine("Hand tracking  ·  21 points per hand",
      window.NOCAM ? "NO CAMERA · MOUSE" : BHok() && BH.ready() ? "OK" : "WARMING UP");
    await logLine("PGDM knowledge  ·  " + (KB.length || 13) + " topics", "OK");
    await logLine("Memory  ·  " + (window.NimbusMemory ? NimbusMemory.count() : 0) + " items", "OK");
    await sleep(600);
    init.classList.add("gone");
    hud.style.display = "";
    setTimeout(() => init.remove(), 1100);
    const h = new Date().getHours();
    say(`${h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening"}, ${USER()}. Nimbus is ready.`, { short: true });
  }
  init.addEventListener("click", start);
  addEventListener("keydown", (e) => { if (!started && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); start(); } }, true);

  /* ================= HUD ================= */
  const hud = $(`<div id="nb-hud" style="display:none">
      <div class="nb-top">
        <div class="nb-brand"><i class="nb-mark"></i><b>NIMBUS</b><span>PGDM INTELLIGENCE</span></div>
        <div class="nb-status"><div class="nb-chip" id="nb-hands"><i class="nb-dot"></i><span>HANDS 0</span></div>
          <div class="nb-chip on" id="nb-type"><i class="nb-dot"></i><span>ENTER = TYPE A COMMAND</span></div></div>
        <div class="nb-right"><div class="nb-membtn nb-ui" title="NIMBUS Memory: upload files">
          <i>⇪</i><span>Memory</span><b class="nb-memn">0</b></div><div class="nb-clock"></div></div>
      </div>
      <div class="nb-said"><div class="nb-heard"></div><div class="nb-reply"></div></div>
    </div>`);
  document.body.appendChild(hud);
  const heardEl = hud.querySelector(".nb-heard"), replyEl = hud.querySelector(".nb-reply");
  const handsChip = hud.querySelector("#nb-hands");
  const clock = hud.querySelector(".nb-clock");
  setInterval(() => {
    const d = new Date();
    clock.textContent = d.toLocaleDateString(undefined, { weekday: "short", day: "2-digit", month: "short" }).toUpperCase() + "   " +
      d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
    if (BHok()) {
      const n = BH.hands();
      handsChip.querySelector("span").textContent = n ? "HANDS " + n : "NO HANDS";
      handsChip.classList.toggle("on", n > 0);
    }
  }, 250);

  let heardT = 0, replyT = 0;
  function showHeard(t) { heardEl.textContent = t ? "“" + t + "”" : ""; heardEl.classList.toggle("show", !!t); clearTimeout(heardT); heardT = setTimeout(() => heardEl.classList.remove("show"), 4000); }
  function showReply(t) { replyEl.textContent = t; replyEl.classList.add("show"); clearTimeout(replyT); }
  function hideReplySoon(ms = 2500) { clearTimeout(replyT); replyT = setTimeout(() => replyEl.classList.remove("show"), ms); }

  /* ================= replies (on screen; NIMBUS does not speak) ================= */
  function ring(state) { if (BHok()) BH.setRing(state); }
  function say(text, opts = {}) {
    showReply(text); ring("idle");
    hideReplySoon(opts.short ? 2600 : 3600 + text.length * 35);
    if (opts.then) setTimeout(opts.then, 1200 + text.length * 35);
  }
  const WAKE = /\b(hey\s+)?(nimbus)\b[\s,.!]*/i;   // "hey nimbus, ..." typed still works

  /* ================= typed command (Enter) ================= */
  const box = $(`<input id="nb-cmd" class="nb-ui" placeholder='Ask Nimbus   e.g. "compare SWOT and Porter"' autocomplete="off">`);
  document.body.appendChild(box);
  addEventListener("keydown", (e) => {
    if (!started) return;
    if (e.key === "Enter" && document.activeElement !== box) { e.preventDefault(); box.classList.add("show"); box.value = ""; box.focus(); }
    else if (e.key === "Escape" && document.activeElement === box) { box.classList.remove("show"); box.blur(); }
  });
  box.addEventListener("keydown", (e) => {
    e.stopPropagation();
    if (e.key === "Enter") { const v = box.value.trim(); box.classList.remove("show"); box.blur(); if (v) { showHeard(v); handle(v.replace(WAKE, "")); } }
    if (e.key === "Escape") { box.classList.remove("show"); box.blur(); }
  });

  /* ================= NIMBUS Memory =================
     One central store for everything you give NIMBUS: images, PDFs and text
     notes. Kept in this browser (IndexedDB), so it survives reloads and works
     offline. Upload from the Memory button (top right) or drop files anywhere.
     Everything in Memory opens as a card from the ring's Memory circle, the
     drawer, or by typing "show <name>". */
  const Memory = (() => {
    const MAX = 25 * 1024 * 1024;
    const OK = /^(image\/|application\/pdf$|text\/)|\.(md|txt|csv|json|pdf|png|jpe?g|gif|webp|svg)$/i;
    let db = null, meta = [];
    const listeners = [];
    const changed = () => { listeners.forEach(f => { try { f(); } catch (e) {} }); };
    const open = () => new Promise((res, rej) => {
      if (db) return res(db);
      const rq = indexedDB.open("nimbus-memory", 1);
      rq.onupgradeneeded = () => rq.result.createObjectStore("items", { keyPath: "id" });
      rq.onsuccess = () => { db = rq.result; res(db); };
      rq.onerror = () => rej(rq.error);
    });
    const tx = async (mode, fn) => { const d = await open(); return new Promise((res, rej) => {
      const t = d.transaction("items", mode), st = t.objectStore("items"), out = fn(st);
      t.oncomplete = () => res(out && out.result !== undefined ? out.result : out); t.onerror = () => rej(t.error); }); };
    async function refresh() {
      try {
        const all = await tx("readonly", st => st.getAll());
        meta = (all || []).map(({ id, name, type, size, added }) => ({ id, name, type, size, added })).sort((a, b) => b.added - a.added);
      } catch (e) { meta = []; }
      changed();
    }
    const kindOf = m => /^image\//.test(m.type) || /\.(png|jpe?g|gif|webp|svg)$/i.test(m.name) ? "image"
      : m.type === "application/pdf" || /\.pdf$/i.test(m.name) ? "pdf" : "text";
    async function add(files) {
      let n = 0; const skipped = [];
      for (const f of files) {
        if (!OK.test(f.type) && !OK.test(f.name)) { skipped.push(f.name + " (type)"); continue; }
        if (f.size > MAX) { skipped.push(f.name + " (over 25 MB)"); continue; }
        const item = { id: Date.now().toString(36) + Math.random().toString(36).slice(2, 7), name: f.name, type: f.type || "",
                       size: f.size, added: Date.now(), blob: f };
        try { await tx("readwrite", st => st.put(item)); n++; } catch (e) { skipped.push(f.name + " (storage full)"); }
      }
      await refresh();
      return { n, skipped };
    }
    async function remove(id) { await tx("readwrite", st => st.delete(id)); await refresh(); }
    async function clear() { await tx("readwrite", st => st.clear()); await refresh(); }
    async function get(id) { return tx("readonly", st => st.get(id)); }
    async function show(id) {
      const it = await get(id); if (!it || !BHok()) return false;
      const title = it.name.replace(/\.[a-z0-9]+$/i, ""), k = kindOf(it);
      if (k === "image") BH.openImage(URL.createObjectURL(it.blob), title);
      else if (k === "pdf") BH.openDoc(URL.createObjectURL(it.blob), title);
      else BH.openText(title, await it.blob.text());
      SFX.arrive();
      return true;
    }
    function find(q) {
      const t = q.toLowerCase().replace(/^(show|open|display)\s+(me\s+)?(my\s+)?(the\s+)?/, "").trim();
      if (!t) return null;
      return meta.find(m => m.name.toLowerCase().replace(/\.[a-z0-9]+$/, "") === t) ||
             meta.find(m => m.name.toLowerCase().includes(t)) || null;
    }
    refresh();
    return { add, remove, clear, show, find, kindOf, count: () => meta.length, list: () => meta.slice(), onChange: f => listeners.push(f) };
  })();
  window.NimbusMemory = Memory;

  // ---- the Memory drawer (top right) ----
  const memBtn = hud.querySelector(".nb-membtn"), memN = hud.querySelector(".nb-memn");
  const drawer = $(`<div id="nb-mem" class="nb-ui">
      <div class="mh"><div><div class="k">NIMBUS · MEMORY</div><div class="sub">Everything you give Nimbus, in one place</div></div><b class="mx">✕</b></div>
      <label class="mup"><input type="file" multiple accept="image/*,.pdf,.md,.txt,.csv,.json,text/*"><span>⇪ Upload files</span><small>Images, PDFs, notes · or drop files anywhere</small></label>
      <div class="ml"></div>
      <div class="mf"><span class="mcount"></span><b class="mclear">Clear all</b></div>
    </div>`);
  document.body.appendChild(drawer);
  const drop = $(`<div id="nb-drop" class="nb-ui"><div><i>⇪</i>Drop to add to NIMBUS Memory</div></div>`);
  document.body.appendChild(drop);
  const fmtSize = b => b > 1048576 ? (b / 1048576).toFixed(1) + " MB" : Math.max(1, Math.round(b / 1024)) + " KB";
  const ICON = { image: "▣", pdf: "▤", text: "≡" };
  function renderDrawer() {
    const list = Memory.list();
    memN.textContent = list.length;
    drawer.querySelector(".mcount").textContent = list.length + (list.length === 1 ? " item" : " items");
    drawer.querySelector(".mclear").style.display = list.length ? "" : "none";
    drawer.querySelector(".ml").innerHTML = list.length ? list.map(m =>
      `<div class="mi" data-id="${m.id}"><i class="mk-${Memory.kindOf(m)}">${ICON[Memory.kindOf(m)]}</i>
        <div class="mn"><b>${m.name.replace(/[<>&]/g, "")}</b><small>${fmtSize(m.size)} · ${new Date(m.added).toLocaleDateString(undefined, { day: "numeric", month: "short" })}</small></div>
        <b class="mo">Show</b><b class="md" title="Delete">✕</b></div>`).join("")
      : `<div class="mempty">Nothing here yet. Upload your timetable, a case PDF, notes or a photo of the whiteboard.</div>`;
  }
  Memory.onChange(renderDrawer);
  renderDrawer();
  const toggleDrawer = (on) => drawer.classList.toggle("show", on ?? !drawer.classList.contains("show"));
  memBtn.addEventListener("click", () => toggleDrawer());
  drawer.querySelector(".mx").addEventListener("click", () => toggleDrawer(false));
  async function addFiles(files) {
    if (!files || !files.length) return;
    const r = await Memory.add([...files]);
    SFX.success();
    say(r.n ? `Added ${r.n} item${r.n > 1 ? "s" : ""} to memory.` + (r.skipped.length ? ` Skipped ${r.skipped.join(", ")}.` : "")
            : "Couldn't add that. Use images, PDFs or text files under 25 MB.", { short: true });
    toggleDrawer(true);
  }
  drawer.querySelector("input[type=file]").addEventListener("change", (e) => { addFiles(e.target.files); e.target.value = ""; });
  drawer.querySelector(".ml").addEventListener("click", async (e) => {
    const row = e.target.closest(".mi"); if (!row) return;
    if (e.target.closest(".md")) { await Memory.remove(row.dataset.id); return; }
    if (await Memory.show(row.dataset.id)) toggleDrawer(false);
  });
  drawer.querySelector(".mclear").addEventListener("click", async () => {
    if (confirm("Delete everything in NIMBUS Memory on this browser? This can't be undone.")) await Memory.clear();
  });
  // drop files anywhere
  let dragN = 0;
  addEventListener("dragenter", (e) => { if (e.dataTransfer && [...e.dataTransfer.types].includes("Files")) { dragN++; drop.classList.add("show"); } });
  addEventListener("dragleave", () => { if (--dragN <= 0) { dragN = 0; drop.classList.remove("show"); } });
  addEventListener("dragover", (e) => { if (e.dataTransfer && [...e.dataTransfer.types].includes("Files")) e.preventDefault(); });
  addEventListener("drop", (e) => { if (!e.dataTransfer || !e.dataTransfer.files.length) return; e.preventDefault(); dragN = 0; drop.classList.remove("show"); addFiles(e.dataTransfer.files); });

  /* ================= the day: routine, calendar, plan =================
     Everything is stored on this device (localStorage), per date. The calendar
     starts from a sample PGDM week; add or remove events by voice or typing:
     "add finance quiz at 3 pm", "remove mentor call". */
  const USER = () => { try { return localStorage.getItem("nimbus.user") || "Rubin"; } catch (e) { return "Rubin"; } };
  const Day = (() => {
    const pad = n => String(n).padStart(2, "0");
    const hm = m => pad(Math.floor(m / 60) % 24) + ":" + pad(m % 60);
    const toMin = s => { const [h, m] = s.split(":").map(Number); return h * 60 + m; };
    const dkey = (off = 0) => { const d = new Date(Date.now() + off * 864e5); return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); };
    const nowMin = () => { const d = new Date(); return d.getHours() * 60 + d.getMinutes(); };
    const load = (k, def) => { try { return JSON.parse(localStorage.getItem(k)) ?? def; } catch (e) { return def; } };
    const save = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} };
    const ROUTINE = [["06:30", 15, "Wake up, water, no phone"], ["06:45", 45, "Workout or run"], ["07:30", 30, "Business news: ET + Mint"],
      ["08:00", 30, "Breakfast"], ["13:00", 45, "Lunch"], ["17:30", 30, "Walk and reset"], ["20:00", 45, "Dinner"],
      ["21:30", 45, "Revise notes, plan tomorrow"]];
    const WEEK = [   // sample timetable, Sunday first: [start, minutes, title, where]
      [["11:00", 60, "Weekly review and goals", "Home"], ["17:00", 30, "Family call", ""]],
      [["09:30", 90, "Marketing Management", "Room 204"], ["11:15", 90, "Corporate Finance", "Room 112"], ["15:00", 60, "Placement prep: aptitude", "Seminar hall"], ["18:00", 60, "Consulting club meet", "Library"]],
      [["09:30", 90, "Operations Management", "Room 204"], ["11:15", 90, "Business Analytics lab", "Lab 2"], ["14:30", 90, "Group project: market entry case", "Library"], ["19:00", 60, "Toastmasters", "Auditorium"]],
      [["09:30", 90, "Organisational Behaviour", "Room 108"], ["11:15", 90, "Managerial Economics", "Room 112"], ["16:00", 60, "Guest talk: industry leader", "Auditorium"]],
      [["09:30", 90, "Corporate Finance", "Room 112"], ["11:15", 90, "Marketing Management", "Room 204"], ["14:00", 60, "Mock GD session", "Seminar hall"], ["18:30", 60, "Case competition team sync", "Online"]],
      [["09:30", 90, "Business Analytics", "Lab 2"], ["11:15", 90, "Operations Management", "Room 204"], ["15:00", 45, "Quiz: financial ratios", "Room 112"], ["17:00", 30, "Mentor call", "Online"]],
      [["10:00", 60, "Live project: client call", "Online"], ["15:00", 90, "Sports and club activity", "Ground"]],
    ];
    const FOCUS = ["Case practice: profit tree", "Revise SWOT and Porter", "Finance drill: NPV and ratios", "Mock GD: current affairs",
      "Assignment: marketing plan", "Placement: CV and LinkedIn", "Read one HBR case"];
    let ver = 1, plan = null;
    const bump = () => { ver++; };
    const done = (off = 0) => load("nimbus.done." + dkey(off), {});
    const extra = (off = 0) => load("nimbus.cal." + dkey(off), { add: [], del: [] });
    function routine() { return ROUTINE.map(([t, d, l]) => ({ id: "r" + t, s: toMin(t), d, label: l, kind: "routine" })); }
    function events(off = 0) {
      const x = extra(off);
      const base = WEEK[(new Date().getDay() + off) % 7].map(([t, d, l, w]) => ({ id: "e" + t + l, s: toMin(t), d, label: l, where: w, kind: "event" }));
      return base.concat(x.add.map(e => ({ ...e, kind: "event" }))).filter(e => !x.del.includes(e.label.toLowerCase())).sort((a, b) => a.s - b.s);
    }
    let planDay = 0;
    function build() {   // fixed blocks + events, then focus blocks and breaks in the free gaps from now on
      planDay = nowMin() >= 22 * 60 + 15 ? 1 : 0;           // late evening: plan tomorrow instead
      const fixed = routine().concat(events(planDay)).sort((a, b) => a.s - b.s);
      const out = [], start = planDay ? 6 * 60 + 30 : Math.max(nowMin() - (nowMin() % 5), 6 * 60 + 30), END = 23 * 60;
      let f = new Date().getDate() % FOCUS.length, cur = start;
      const fill = (until) => {
        while (until - cur >= 40) {
          const len = Math.min(90, until - cur - (until - cur > 105 ? 15 : 0));
          out.push({ id: "f" + cur, s: cur, d: len, label: FOCUS[f++ % FOCUS.length], kind: "focus" });
          cur += len;
          if (until - cur >= 55) { out.push({ id: "b" + cur, s: cur, d: 15, label: "Break: stretch, water", kind: "break" }); cur += 15; }
        }
      };
      for (const b of fixed) {
        if (b.s + b.d <= start) continue;
        if (b.s > cur) fill(b.s);
        out.push(b); cur = Math.max(cur, b.s + b.d);
      }
      fill(END);
      return out;
    }
    function row(it, i, nowFlag, isDone, past) {
      const sub = it.kind === "event" ? (it.where ? it.where + " · " : "") + it.d + " min" : it.kind === "focus" ? "Focus · " + it.d + " min" : it.kind === "break" ? "" : it.d ? it.d + " min" : "";
      return `<b data-a="tog:${i}" class="drow k-${it.kind}${isDone ? " done" : ""}${nowFlag ? " now" : ""}${past ? " past" : ""}"><span class="dt">${hm(it.s)}</span>` +
        `<span class="dl">${it.label}${sub ? `<small>${sub}</small>` : ""}</span>${nowFlag ? '<em>NOW</em>' : ""}<i class="dck"></i></b>`;
    }
    function list(kind) {
      if (kind === "routine") return routine();
      if (kind === "calendar") return events();
      if (!plan) plan = build();
      const n = planDay ? 0 : nowMin();
      return plan.filter(p => p.s + p.d > n).slice(0, 7);
    }
    function html(kind) {
      const items = list(kind), n = nowMin();
      const off = kind === "plan" ? planDay : 0, dn = done(off);
      const d = new Date(), date = d.toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "short" });
      const head = kind === "calendar" ? `${date} · ${items.length} event${items.length === 1 ? "" : "s"}`
        : kind === "routine" ? `${items.filter(i => dn[i.id]).length} of ${items.length} done today`
        : planDay ? "Tomorrow · tap a row when it's done" : `From ${hm(n)} · tap a row when it's done`;
      if (!items.length) return `<div class="dhead">${head}</div><div class="dempty">${kind === "calendar" ? "Nothing scheduled today." : "That's the day done. Rest well."}</div>`;
      const live = !(kind === "plan" && planDay);
      return `<div class="dhead">${head}</div>` + items.map((it, i) => row(it, i, live && n >= it.s && n < it.s + it.d, !!dn[it.id],
        live && kind !== "routine" && n >= it.s + it.d)).join("");
    }
    function act(kind, a) {
      if (a === "replan") { plan = build(); bump(); return; }
      if (a.startsWith("tog:")) {
        const it = list(kind)[+a.slice(4)]; if (!it) return;
        const off = kind === "plan" ? planDay : 0, dn = done(off); dn[it.id] = !dn[it.id]; save("nimbus.done." + dkey(off), dn); bump();
      }
    }
    function parseTime(s) {
      const m = s.match(/(\d{1,2})(?::|\.)?(\d{2})?\s*(a\.?m\.?|p\.?m\.?)?/i); if (!m) return null;
      let h = +m[1]; const mi = +(m[2] || 0), ap = (m[3] || "").toLowerCase();
      if (ap.startsWith("p") && h < 12) h += 12; if (ap.startsWith("a") && h === 12) h = 0;
      if (!ap && h >= 1 && h <= 7) h += 12;                // "at 3" means 3 pm on a student's day
      return h < 24 && mi < 60 ? h * 60 + mi : null;
    }
    function add(label, when, dur) {
      const s = parseTime(when); if (s == null) return null;
      const x = extra(); x.add.push({ id: "x" + s + label, s, d: dur || 60, label: label.replace(/^\w/, c => c.toUpperCase()), where: "" });
      x.del = x.del.filter(l => l !== label.toLowerCase()); save("nimbus.cal." + dkey(), x); plan = build(); bump();
      return hm(s);
    }
    function remove(q) {
      const ev = events().find(e => e.label.toLowerCase().includes(q.toLowerCase().trim())); if (!ev) return null;
      const x = extra(); x.add = x.add.filter(e => e.label !== ev.label); x.del.push(ev.label.toLowerCase());
      save("nimbus.cal." + dkey(), x); plan = build(); bump(); return ev.label;
    }
    function next() { if (!plan) plan = build(); const n = planDay ? 0 : nowMin(), dn = done(planDay); return plan.find(p => p.s + p.d > n && !dn[p.id]) || null; }
    function summary() {
      plan = build(); bump();
      const ev = events(planDay).filter(e => planDay || e.s + e.d > nowMin()), focus = plan.filter(p => p.kind === "focus").length, nx = next();
      return { tomorrow: !!planDay, events: ev.length, first: ev[0] ? `${ev[0].label} at ${hm(ev[0].s)}` : null, focus, next: nx ? `${nx.label} at ${hm(nx.s)}` : null };
    }
    setInterval(bump, 30000);                              // the NOW marker moves with the clock
    return { get ver() { return ver; }, html, act, add, remove, next, summary, hm };
  })();
  window.NimbusDay = Day;

  /* ================= "all systems online": the morning sequence ================= */
  const sys = $(`<div id="nb-sys" class="nb-ui"><div class="k">NIMBUS · SYSTEMS</div><div class="rows"></div></div>`);
  document.body.appendChild(sys);
  const scan = $(`<div class="nb-scan"></div>`);
  document.body.appendChild(scan);
  let morningBusy = false;
  async function morning(parts = { routine: 1, calendar: 1, plan: 1 }) {
    if (morningBusy || !BHok()) return; morningBusy = true;
    try {
      ring("thinking");
      const rows = sys.querySelector(".rows"); rows.innerHTML = "";
      const list = [["Hand tracking", BH.hands() ? "ONLINE" : window.NOCAM ? "MOUSE" : "STANDBY"], ["Memory", (window.NimbusMemory ? NimbusMemory.count() : 0) + " ITEMS"],
        ["Knowledge base", "ONLINE"], ["Calendar", "SYNCED"], ["Day planner", "ONLINE"], ["Study tools", "ONLINE"]];
      list.forEach(([n]) => rows.insertAdjacentHTML("beforeend", `<div class="sr"><span>${n}</span><i><u></u></i><b></b></div>`));
      sys.classList.add("show"); scan.classList.remove("go"); void scan.offsetWidth; scan.classList.add("go");
      SFX.boot();
      BH.closeAll(); BH.ringTo(0.12, 0.5, 0.6);
      await sleep(500);
      for (let i = 0; i < list.length; i++) {
        const r = rows.children[i]; r.classList.add("run");
        await sleep(260);
        r.classList.add("ok"); r.querySelector("b").textContent = list[i][1]; SFX.ok();
      }
      await sleep(450);
      sys.classList.remove("show");
      // the three cards, side by side to the right of the ring
      const W = innerWidth, H = innerHeight, x0 = W * 0.24, col = (W - 16 - x0) / 3;
      const sc = Math.min(1, (col - 14) / 360, (H - 150) / 620);
      const kinds = ["routine", "calendar", "plan"].filter(k => parts[k]);
      for (let i = 0; i < kinds.length; i++) {
        const t = BH.openTool(kinds[i], { x: x0 + col * (kinds.length === 3 ? i * 2 + 1 : i * 2 + 2) / 2, y: H * 0.5, scale: sc });
        if (t) t.scale = Math.min(1, (col - 14) / t.el.offsetWidth, (H - 200) / t.el.offsetHeight);
        SFX.arrive(); await sleep(380);
      }
      const s = Day.summary(), h = new Date().getHours();
      const hi = h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
      say(`${hi}, ${USER()}. All systems online. ` +
        (s.tomorrow ? (s.events ? `Today's done. Tomorrow you have ${s.events} event${s.events > 1 ? "s" : ""}, starting with ${s.first}. ` : "Today's done, and tomorrow's calendar is clear. ")
         : s.events ? `You have ${s.events} event${s.events > 1 ? "s" : ""} left today, starting with ${s.first}. ` : "Your calendar is clear for the rest of today. ") +
        (s.focus ? `I've planned ${s.focus} focus block${s.focus > 1 ? "s" : ""} around them.` : "") +
        (s.next ? ` Next up: ${s.next}.` : ""));
    } finally { morningBusy = false; }
  }

  /* ================= understanding ================= */
  function find(text) {
    const t = " " + text.toLowerCase().replace(/[^a-z0-9/ ]+/g, " ") + " ";
    let best = null, bestScore = 0;
    for (const e of KB) for (const k of e.keys) {
      if (t.includes(k) && k.length > bestScore) { best = e; bestScore = k.length; }
    }
    return best;
  }

  let quiz = null;
  function handle(raw) {
    const c = raw.toLowerCase().replace(/[.?!]+$/, "").trim();
    if (!BHok()) { say("Give me a moment, I'm still waking up."); return; }
    ring("thinking"); SFX.wake();

    if (quiz && /\b(answer|reveal|tell me|i don'?t know|skip|give up)\b/.test(c)) return revealQuiz();
    // the day: briefing, routine, calendar, plan, add / remove events, what's next
    const call = c.match(/^call me\s+(\w+)/);
    if (call) { try { localStorage.setItem("nimbus.user", call[1].replace(/^\w/, x => x.toUpperCase())); } catch (e) {} return say(`Got it, ${USER()}.`, { short: true }); }
    const addm = c.match(/^(?:add|schedule|put)\s+(.+?)\s+(?:at|@)\s+([0-9: .apm]+?)(?:\s+for\s+(\d+)\s*(hour|hr|minute|min))?(?:\s+(?:to|in|on)\s+(?:my\s+)?calendar)?$/);
    if (addm) {
      const dur = addm[3] ? +addm[3] * (/^h/.test(addm[4]) ? 60 : 1) : 60;
      const at = Day.add(addm[1].replace(/\s+(to|in|on)\s+(my\s+)?calendar$/, ""), addm[2], dur);
      if (at) { BH.openTool("calendar"); return say(`Added at ${at}.`, { short: true }); }
      return say("What time? Try: add finance quiz at 3 pm.", { short: true });
    }
    const delm = c.match(/^(?:remove|delete|cancel)\s+(?:the\s+)?(.+?)(?:\s+from\s+(?:my\s+)?calendar)?$/);
    if (delm) { const gone = Day.remove(delm[1]); if (gone) { BH.openTool("calendar"); return say(`Removed ${gone}.`, { short: true }); } }
    if (/\b(what'?s next|next task|what now|what should i do now)\b/.test(c)) {
      const n = Day.next(); return say(n ? `Next: ${n.label} at ${Day.hm(n.s)}.` : "Nothing left on today's plan.", { short: true });
    }
    if (/\bexams?\b|\bexam (calendar|schedule|dates)\b/.test(c)) { BH.openNote("0/Exam Calendar.md", "Exam Calendar"); return say("Your exam calendar. End-terms start Monday the 7th of December.", { short: true }); }
    if (/\btime ?table\b/.test(c)) { BH.openNote("0/Weekly Timetable.md", "Weekly Timetable"); return say("Your weekly timetable.", { short: true }); }
    const wants = { routine: /\broutine\b/.test(c), calendar: /\b(calendar|schedule|agenda|meetings|events|classes|lectures)\b/.test(c),
                    plan: /\bplan\b/.test(c) && !/\bmarketing plan\b/.test(c) };
    const nWant = Object.values(wants).filter(Boolean).length;
    if (/\b(all systems|systems online|start my day|good morning|morning briefing|daily briefing|brief me|wake up|online)\b/.test(c) || nWant >= 2)
      return morning(nWant >= 2 ? wants : undefined);
    if (nWant === 1) {
      const k = Object.keys(wants).find(k => wants[k]);
      if (k === "plan") Day.summary();
      BH.openTool(k);
      const s = Day.summary();
      return say(k === "calendar" ? (s.events ? `${s.events} event${s.events > 1 ? "s" : ""} left today. First, ${s.first}.` : "Your calendar is clear.")
        : k === "plan" ? (s.next ? `Here's your day. Next up: ${s.next}.` : "Here's your day.") : "Your routine.", { short: true });
    }
    const tool = /\bstop ?watch\b/.test(c) ? "stopwatch" : /\b(timer|countdown|count down)\b/.test(c) ? "timer" : null;
    if (tool) return toolCommand(tool, c);
    if (/\b(close|clear|dismiss|hide|reset|remove)\b/.test(c)) { BH.closeAll(); hideQuiz(); return say("Cleared.", { short: true }); }
    if (/\b(menu|options|home|open the ring|main screen)\b/.test(c)) { if (!BH.menuOpen()) BH.toggleMenu(); return say("Menu.", { short: true }); }
    if (/\b(quiz|test me|question me|ask me)\b/.test(c)) return startQuiz();
    if (/\bwho (made|built|created|designed) you\b|\byour (creator|maker)\b/.test(c)) return say("I was built by Rubin, for PGDM students who would rather learn with their hands than a scroll wheel.");
    if (/\b(who are you|introduce yourself|what can you do|help|what are you)\b/.test(c))
      return say("I'm Nimbus. Type all systems online for your day, show a framework, start a timer, quiz me, or open memory.");
    if (/\b(thank|thanks|good job|well done)\b/.test(c)) return say("Always a pleasure.", { short: true });

    const cmp = c.match(/\b(?:compare|versus|vs)\b\s*(.+?)\s+(?:and|with|vs|versus|to)\s+(.+)/);
    if (cmp) {
      const a = find(cmp[1]), b = find(cmp[2]);
      if (a && b && a.img && b.img && a !== b) {
        BH.openProp(a.img, { x: 0.27, y: 0.5, scale: 0.92 });
        setTimeout(() => BH.openProp(b.img, { x: 0.73, y: 0.5, scale: 0.92 }), 350);
        return say(`${a.name} and ${b.name}, side by side.`, { short: true });
      }
      return say("I can compare two frameworks. Try: compare SWOT and Porter.");
    }

    if (/^(open |show )?(my )?(memory|uploads?|files)$/.test(c)) { toggleDrawer(true); return say("Your memory.", { short: true }); }
    const mm = /^(show|open|display)\b/.test(c) ? Memory.find(c) : null;
    if (mm) { Memory.show(mm.id); return say(mm.name.replace(/\.[a-z0-9]+$/i, "") + ", from memory.", { short: true }); }
    const e = find(c);
    if (!e) return say("Try: show SWOT, start a 5 minute timer, quiz me, or upload files to Memory.", { short: true });
    if (/\b(explain|tell me about|what is|what's|teach|describe|walk me through|summari[sz]e|read)\b/.test(c)) {
      BH.openNote(e.note, e.name);
      return say(e.say);
    }
    if (e.img) BH.openProp(e.img); else BH.openNote(e.note, e.name);
    say(e.line, { short: true });
  }

  const NUMW = { one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10, fifteen: 15, twenty: 20, thirty: 30, half: 0.5, a: 1 };
  function toolCommand(tool, c) {
    if (/\b(close|hide|dismiss|remove)\b/.test(c)) { BH.closeTool(tool); return say("Closed.", { short: true }); }
    if (tool === "timer") {
      const m = c.match(/(\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|fifteen|twenty|thirty|half|a)\s*-?\s*(minute|min|second|sec|hour)/);
      if (m) {
        const n = isNaN(+m[1]) ? NUMW[m[1]] : +m[1];
        const ms = n * (m[2].startsWith("h") ? 3600000 : m[2].startsWith("s") ? 1000 : 60000);
        BH.tool("timer", "set", ms); BH.tool("timer", "start");
        return say(`Timer set for ${m[1] === "a" ? "one" : m[1]} ${m[2].startsWith("m") ? "minutes" : m[2] + "s"}.`.replace("one minutes", "one minute"), { short: true });
      }
      if (/\b(stop|pause)\b/.test(c)) { BH.tool("timer", "pause"); return say("Paused.", { short: true }); }
      if (/\breset\b/.test(c)) { BH.tool("timer", "rs"); return say("Reset.", { short: true }); }
      if (/\b(start|resume|go)\b/.test(c)) { BH.tool("timer", "start"); return say("Timer running.", { short: true }); }
      BH.openTool("timer"); return say("Timer.", { short: true });
    }
    if (tool === "stopwatch") {
      if (/\blap\b/.test(c)) { BH.tool("stopwatch", "lap"); return; }
      if (/\b(stop|pause)\b/.test(c)) { BH.tool("stopwatch", "pause"); return say("Stopped.", { short: true }); }
      if (/\breset\b/.test(c)) { BH.tool("stopwatch", "rs"); return say("Reset.", { short: true }); }
      BH.tool("stopwatch", "start"); return say("Stopwatch running.", { short: true });
    }
  }

  /* opening things by hand stays silent */
  const hookOpen = setInterval(() => { if (!BHok()) return; clearInterval(hookOpen); BH.onOpen = () => {}; }, 200);

  /* ================= quiz ================= */
  const qcard = $(`<div id="nb-quiz" class="nb-ui"><div class="k">NIMBUS · QUIZ</div><div class="q"></div><div class="a"></div><div class="bar"><i></i></div></div>`);
  document.body.appendChild(qcard);
  let qTimer = 0, qIdx = -1;
  function startQuiz() {
    if (!QUIZ.length) return say("The quiz bank is still loading.");
    qIdx = (qIdx + 1 + Math.floor(Math.random() * (QUIZ.length - 1))) % QUIZ.length;
    quiz = QUIZ[qIdx];
    qcard.querySelector(".q").textContent = quiz.q;
    qcard.querySelector(".a").textContent = "";
    const bar = qcard.querySelector(".bar i");
    bar.style.transition = "none"; bar.style.width = "0";
    qcard.classList.add("show"); SFX.arrive();
    say(quiz.q, { then: () => {
      void bar.offsetWidth; bar.style.transition = "width 8s linear"; bar.style.width = "100%";
      clearTimeout(qTimer); qTimer = setTimeout(revealQuiz, 8000);
    } });
  }
  function revealQuiz() {
    if (!quiz) return;
    clearTimeout(qTimer);
    qcard.querySelector(".a").textContent = quiz.a;
    SFX.success();
    const q = quiz; quiz = null;
    say("Answer. " + q.a + " Say quiz me for another.", { then: () => setTimeout(() => { if (!quiz) hideQuiz(); }, 2500) });
  }
  function hideQuiz() { clearTimeout(qTimer); quiz = null; qcard.classList.remove("show"); }
  qcard.addEventListener("click", () => (quiz ? revealQuiz() : hideQuiz()));
})();
