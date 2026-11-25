#!/usr/bin/env python3
"""Build the static Netlify site (./site) from ./repo: NIMBUS, RUBIN's PGDM board (nimbus/ = the UI, voice, sound and pinch layers)."""
import json, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).parent          # nimbus/
REPO, SITE = ROOT.parent, ROOT / "site"   # the barehands repo root holds stage.html

saved = None
if (SITE / ".netlify" / "state.json").exists():
    saved = (SITE / ".netlify" / "state.json").read_text()
shutil.rmtree(SITE, ignore_errors=True)
SITE.mkdir()
if saved:
    (SITE / ".netlify").mkdir()
    (SITE / ".netlify" / "state.json").write_text(saved)

# ======================= NOTES (orb 0) =======================
NOTES = {
"Exam Calendar.md": """# Exam Calendar · Term III

**End-term exams** (3 hours each, 10:00 to 13:00, Exam Hall A)
- **Mon 7 Dec** · Marketing Management
- **Tue 8 Dec** · Corporate Finance (formula sheet allowed)
- **Wed 9 Dec** · Operations Management
- **Thu 10 Dec** · Business Analytics (lab exam, 14:00)
- **Fri 11 Dec** · Organisational Behaviour
- **Sat 12 Dec** · Managerial Economics

**Before the exams**
- **Mon 30 Nov** · Group project report due (Marketing), 23:59 on the portal
- **Thu 3 Dec** · Case competition final round
- **Fri 4 Dec** · Viva: Business Analytics project
- **Sat 5 Dec** · Last day to collect hall tickets

**Revision plan**
- **28 Nov to 2 Dec**: one pass of every subject, two subjects a day
- **3 to 6 Dec**: past papers under a timer, one paper a day
- **The evening before each exam**: formulas, frameworks, sleep by 23:00

Say "start a 3 hour timer" for a full mock paper.
""",
"Weekly Timetable.md": """# Weekly Timetable · Term III

**Monday**
- 09:30 · Marketing Management · Room 204
- 11:15 · Corporate Finance · Room 112
- 15:00 · Placement prep: aptitude · Seminar hall

**Tuesday**
- 09:30 · Operations Management · Room 204
- 11:15 · Business Analytics lab · Lab 2
- 14:30 · Group project: market entry case · Library

**Wednesday**
- 09:30 · Organisational Behaviour · Room 108
- 11:15 · Managerial Economics · Room 112
- 16:00 · Guest talk: industry leader · Auditorium

**Thursday**
- 09:30 · Corporate Finance · Room 112
- 11:15 · Marketing Management · Room 204
- 14:00 · Mock GD session · Seminar hall

**Friday**
- 09:30 · Business Analytics · Lab 2
- 11:15 · Operations Management · Room 204
- 15:00 · Quiz: financial ratios · Room 112

**Saturday**
- 10:00 · Live project: client call · Online
- 15:00 · Sports and club activity · Ground

Each lecture is 90 minutes. Say "show my calendar" for today only.
""",
"Start Here.md": """# Start Here

Welcome to **NIMBUS**, the PGDM intelligence interface. Made by RUBIN.

**With your hands**
- **Pinch** (index + thumb, other fingers up like an OK sign) on something to grab it, release to drop.
- **Quick pinch** on the ring = open the menu. Quick pinch on a row or a key = press it.
- **Flick** while holding = throw it.
- **Two hands** pinching one card = stretch it bigger.
- **Pinch the title bar** of a note quickly = close it.

**With your voice** (just say it)
- "Show SWOT"
- "Explain BCG matrix"
- "Compare SWOT and Porter"
- "Start a 5 minute timer" / "Start stopwatch"
- "Quiz me" / "Clear"

**Tools** (tap the ring, then Tools): Timer for presentations and GDs, Stopwatch.

No camera or mic? Use the mouse, or press Enter to type a command.
""",
"Strategy/SWOT Analysis.md": """# SWOT Analysis

- **Strengths**: internal, helpful
- **Weaknesses**: internal, harmful
- **Opportunities**: external, helpful
- **Threats**: external, harmful

**Make it useful:**
- Cross it: use Strengths to capture Opportunities (SO), fix Weaknesses that expose you to Threats (WT).
- Keep each box to 3 to 5 specific, evidence-backed points.
- Finish with 2 or 3 priorities, not a list of everything.
""",
"Strategy/Porter's Five Forces.md": """# Porter's Five Forces

A tool for judging how attractive an industry is.

1. **Threat of new entrants**: low barriers mean more competition.
2. **Bargaining power of suppliers**: few suppliers means they set the terms.
3. **Bargaining power of buyers**: concentrated or price-sensitive customers push margins down.
4. **Threat of substitutes**: other ways to solve the same need.
5. **Rivalry among existing competitors**: number of players, growth, differentiation.

**How to use it:** score each force Low / Medium / High, then ask where the profit pool is and which force you can shift in your favour.
""",
"Strategy/BCG Matrix.md": """# BCG Growth-Share Matrix

Plot each business unit by **market growth** and **relative market share**.

- **Stars**: high growth, high share. Invest to keep the lead.
- **Cash Cows**: low growth, high share. Harvest the cash.
- **Question Marks**: high growth, low share. Pick winners, fund or drop.
- **Dogs**: low growth, low share. Fix, hold or divest.

Limits: market definition drives the answer, and share is not the only source of advantage.
""",
"Strategy/Ansoff Matrix.md": """# Ansoff Matrix

Four routes to growth, from safest to riskiest:

- **Market penetration**: existing products, existing markets. Sell more to the people you already serve.
- **Product development**: new products, existing markets.
- **Market development**: existing products, new markets (new cities, segments, countries).
- **Diversification**: new products, new markets. Highest risk, highest learning curve.
""",
"Marketing/STP and the 4Ps.md": """# STP and the 4Ps

**STP** decides where to play:
- **Segmentation**: split the market into groups with distinct needs.
- **Targeting**: choose the segments you can serve best and profitably.
- **Positioning**: the one clear idea you own in the customer's mind.

**4Ps** decides how to win there:
- **Product**: what problem it solves.
- **Price**: value captured, not just cost plus.
- **Place**: channels and availability.
- **Promotion**: how people find out and are persuaded.
""",
"Marketing/Funnel, CAC and LTV.md": """# Funnel, CAC and LTV

Awareness, Interest, Consideration, Purchase, Loyalty.

- **CAC** = total acquisition spend / new customers
- **LTV** = average margin per period x expected lifetime
- Healthy rule of thumb: **LTV : CAC of 3 or more**, payback under 12 months.

Fix the biggest drop-off first. Improving a leaky middle beats buying more top-of-funnel traffic.
""",
"Finance/Financial Statements.md": """# The Three Statements

- **Income statement**: revenue minus costs equals profit, over a period.
- **Balance sheet**: assets = liabilities + equity, at a moment in time.
- **Cash flow statement**: operating, investing and financing cash movements.

Profit is not cash. A growing company can be profitable and still run out of cash because of receivables and inventory.
""",
"Finance/NPV, IRR and WACC.md": """# NPV, IRR and WACC

- **NPV** = sum of future cash flows discounted at the required return, minus the investment. Accept projects with NPV > 0.
- **IRR**: the discount rate that makes NPV zero. Accept if IRR > hurdle rate.
- **WACC**: blended cost of debt (after tax) and equity, weighted by capital structure.

NPV is the safer rule when projects are mutually exclusive or cash flows change sign more than once.
""",
"Finance/Key Ratios.md": """# Key Ratios Cheat Sheet

- Gross margin = (Revenue - COGS) / Revenue
- Operating margin = Operating income / Revenue
- ROE = Net income / Equity
- ROIC = NOPAT / Invested capital
- Current ratio = Current assets / Current liabilities
- Debt to equity = Total debt / Equity
- P/E = Price / Earnings per share

Compare to the company's own history and to peers, never in isolation.
""",
"Operations/Lean and Six Sigma.md": """# Lean and Six Sigma

**Lean** removes waste: overproduction, waiting, transport, over-processing, inventory, motion, defects.

**Six Sigma** reduces variation with **DMAIC**: Define, Measure, Analyze, Improve, Control.

**Little's Law:** Inventory = Throughput x Flow time. Cut queues and you cut lead time.
""",
"Placements/How to Crack a Case.md": """# How to Crack a Case

1. **Clarify**: restate the question, goal and constraints.
2. **Structure**: pick or build a framework (profit tree, 3Cs, market entry).
3. **Hypothesis**: state your best guess early, then test it.
4. **Analyze**: do the math out loud, sanity check magnitudes.
5. **Synthesize**: give a recommendation, 2 or 3 reasons, risks, next steps.

Always answer first, then support.

**Worked example:** a coffee chain's profit fell 20%. Profit = Revenue - Costs. Revenue = traffic x average ticket x stores. Costs = COGS + labour + rent + marketing. Ask for traffic and ticket by store cohort, compare cost lines year on year, then recommend.
""",
"Placements/Interview Prep.md": """# PGDM Placement Interview Prep

- **Tell me about yourself**: 90 seconds, present, past, future.
- **Why PGDM, why this specialisation**: a specific goal, a gap, and how the programme closes it.
- **Behavioural stories (STAR)**: Situation, Task, Action, Result. Keep 5 stories that flex across leadership, conflict, failure, impact.
- **Domain round**: be ready on your summer internship project, numbers included.
- **Questions for them**: ask about something you could not find online.
""",
}
notes_root = SITE / "notes"
for rel, text in NOTES.items():
    p = notes_root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)

# ======================= FRAMEWORK IMAGES (orb 1) =======================
FONTS = ["/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf"]
def font(size, bold=False):
    for f in FONTS:
        try:
            return ImageFont.truetype(f, size, index=1 if bold and f.endswith(".ttc") else 0)
        except Exception:
            pass
    return ImageFont.load_default()

W, H = 1200, 800
BG, FG, CY = (9, 10, 26), (238, 240, 255), (150, 160, 255)
PAL = [(143, 227, 255), (150, 160, 255), (255, 200, 120), (255, 140, 200)]

def canvas(title, sub):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    for y in range(H):                                   # night-sky wash, violet at the top
        k = 1 - y / H
        d.line((0, y, W, y), fill=(int(9 + 20 * k * k), int(10 + 8 * k * k), int(26 + 34 * k * k)))
    for x in range(30, W, 60):                           # faint star-dot grid
        for y in range(30, H, 60):
            d.point((x, y), fill=(52, 52, 92))
    d.rounded_rectangle((12, 12, W - 13, H - 13), 26, outline=(70, 72, 140), width=2)
    d.text((54, 34), title.upper(), font=font(50, True), fill=FG)
    d.text((56, 96), sub, font=font(22), fill=(175, 182, 225))
    for i in range(1092):                                # ice -> violet -> rose rule
        k = i / 1092
        c = (int(143 + (183 - 143) * min(1, k * 2) + (255 - 183) * max(0, k * 2 - 1)),
             int(227 + (148 - 227) * min(1, k * 2) + (159 - 148) * max(0, k * 2 - 1)),
             int(255 + (255 - 255) * min(1, k * 2) + (216 - 255) * max(0, k * 2 - 1)))
        d.line((54 + i, 131, 54 + i, 133), fill=c)
    d.text((54, H - 50), "NIMBUS  //  PGDM INTELLIGENCE  //  MADE BY RUBIN", font=font(20), fill=(130, 134, 196))
    return im, d

def box(d, xy, col, text, size=30):
    x0, y0, x1, y1 = xy
    d.rounded_rectangle(xy, 22, fill=tuple(int(BG[i] + (c - BG[i]) * 0.16) for i, c in enumerate(col)), outline=col, width=3)
    lines = text.split("\n")
    lh = size + 10
    y = (y0 + y1) / 2 - lh * len(lines) / 2
    for i, ln in enumerate(lines):
        f = font(size if i == 0 else int(size * 0.68), i == 0)
        w = d.textlength(ln, font=f)
        d.text(((x0 + x1) / 2 - w / 2, y), ln, font=f, fill=FG if i == 0 else (196, 200, 238))
        y += lh if i == 0 else int(size * 0.68) + 10

def glow(im):
    g = im.filter(ImageFilter.GaussianBlur(6))
    return Image.blend(im, g, 0.18)

def swot():
    im, d = canvas("SWOT Analysis", "Internal vs external  x  helpful vs harmful")
    cells = [("Strengths\nInternal  |  helpful", PAL[0]), ("Weaknesses\nInternal  |  harmful", PAL[3]),
             ("Opportunities\nExternal  |  helpful", PAL[1]), ("Threats\nExternal  |  harmful", PAL[2])]
    for i, (t, c) in enumerate(cells):
        x, y = 54 + (i % 2) * 556, 160 + (i // 2) * 280
        box(d, (x, y, x + 536, y + 260), c, t, 42)
    return im

def porter():
    im, d = canvas("Porter's Five Forces", "How attractive is this industry?")
    for a, b in [((600, 250), (600, 320)), ((600, 520), (600, 590)), ((340, 420), (410, 420)), ((790, 420), (860, 420))]:
        d.line((*a, *b), fill=CY, width=4)
    box(d, (410, 320, 790, 520), PAL[0], "Industry\nRivalry", 42)
    box(d, (400, 160, 800, 250), PAL[1], "Threat of New Entrants", 28)
    box(d, (400, 590, 800, 680), PAL[1], "Threat of Substitutes", 28)
    box(d, (54, 330, 340, 510), PAL[2], "Supplier\nPower", 34)
    box(d, (860, 330, 1146, 510), PAL[2], "Buyer\nPower", 34)
    return im

def bcg():
    im, d = canvas("BCG Matrix", "Market growth  x  relative market share")
    q = [("Stars\nInvest", PAL[0], 0, 0), ("Question Marks\nPick winners", PAL[2], 1, 0),
         ("Cash Cows\nHarvest", PAL[1], 0, 1), ("Dogs\nFix or divest", PAL[3], 1, 1)]
    for t, c, cx, cy in q:
        x, y = 110 + cx * 520, 160 + cy * 275
        box(d, (x, y, x + 500, y + 255), c, t, 40)
    return im

def ansoff():
    im, d = canvas("Ansoff Matrix", "Four routes to growth, safest to riskiest")
    q = [("Market Penetration\nExisting product, existing market", PAL[0], 0, 0),
         ("Product Development\nNew product, existing market", PAL[1], 1, 0),
         ("Market Development\nExisting product, new market", PAL[2], 0, 1),
         ("Diversification\nNew product, new market", PAL[3], 1, 1)]
    for t, c, cx, cy in q:
        x, y = 54 + cx * 556, 160 + cy * 280
        box(d, (x, y, x + 536, y + 260), c, t, 34)
    return im

def fourps():
    im, d = canvas("Marketing Mix: 4Ps", "How you win in the segment you chose")
    for i, (t, c) in enumerate([("Product\nWhat problem it solves", PAL[0]), ("Price\nValue captured", PAL[1]),
                                ("Place\nChannels & reach", PAL[2]), ("Promotion\nHow people find out", PAL[3])]):
        x, y = 54 + (i % 2) * 556, 160 + (i // 2) * 280
        box(d, (x, y, x + 536, y + 260), c, t, 42)
    return im

def funnel():
    im, d = canvas("Customer Funnel", "Fix the biggest drop-off first")
    for i, (l, w) in enumerate(zip(["Awareness", "Interest", "Consideration", "Purchase", "Loyalty"], [1060, 880, 700, 520, 340])):
        y = 160 + i * 112
        x0 = 600 - w / 2
        box(d, (x0, y, x0 + w, y + 96), PAL[i % 4], l, 36)
    return im

def profit_tree():
    im, d = canvas("Profit Tree", "The first structure for any profitability case")
    for a, b in [((600, 250), (300, 320)), ((600, 250), (900, 320))]:
        d.line((*a, *b), fill=CY, width=4)
    for x in (130, 300, 470):
        d.line((300, 410, x, 500), fill=CY, width=3)
    for x in (730, 900, 1070):
        d.line((900, 410, x, 500), fill=CY, width=3)
    box(d, (450, 160, 750, 250), PAL[0], "Profit", 42)
    box(d, (150, 320, 450, 410), PAL[1], "Revenue", 34)
    box(d, (750, 320, 1050, 410), PAL[3], "Costs", 34)
    for i, t in enumerate(["Volume", "Price", "Mix"]):
        box(d, (54 + i * 170, 500, 208 + i * 170, 590), PAL[1], t, 28)
    for i, t in enumerate(["Fixed", "Variable", "One-off"]):
        box(d, (656 + i * 170, 500, 810 + i * 170, 590), PAL[3], t, 26)
    return im

def statements():
    im, d = canvas("Financial Statements", "Profit is not cash")
    box(d, (54, 170, 384, 680), PAL[0], "Income\nRevenue - Costs\n= Profit\nover a period", 40)
    box(d, (435, 170, 765, 680), PAL[1], "Balance Sheet\nAssets =\nLiabilities + Equity\nat a moment", 36)
    box(d, (816, 170, 1146, 680), PAL[2], "Cash Flow\nOperating\nInvesting\nFinancing", 40)
    return im

media = SITE / "media"
media.mkdir()
IMGS = {
    "SWOT Analysis.png": swot, "Porter Five Forces.png": porter, "BCG Matrix.png": bcg,
    "Ansoff Matrix.png": ansoff, "Marketing Mix 4Ps.png": fourps, "Customer Funnel.png": funnel,
    "Profit Tree.png": profit_tree, "Financial Statements.png": statements,
}
for name, fn in IMGS.items():
    glow(fn()).save(media / name, optimize=True)

# ======================= NIMBUS KNOWLEDGE (voice topics + quiz) =======================
def N(p): return "0/" + p
KB = [
 {"keys": ["swot", "strength", "weakness", "opportunit", "threat"], "name": "SWOT analysis", "img": "SWOT Analysis.png", "note": N("Strategy/SWOT Analysis.md"),
  "line": "SWOT. Strengths and weaknesses are internal. Opportunities and threats come from outside.",
  "say": "SWOT splits a situation four ways. Strengths and weaknesses are inside the company. Opportunities and threats are outside it. The real value is crossing them: use strengths to grab opportunities, and fix the weaknesses that expose you to threats. End with two or three priorities, not a laundry list."},
 {"keys": ["porter", "five forces", "5 forces", "industry attractive", "rivalry"], "name": "Porter's Five Forces", "img": "Porter Five Forces.png", "note": N("Strategy/Porter's Five Forces.md"),
  "line": "Porter's Five Forces. Five pressures that decide how much profit an industry can keep.",
  "say": "Porter's Five Forces tells you how attractive an industry is. Look at the threat of new entrants, supplier power, buyer power, the threat of substitutes, and rivalry among existing players. Score each one low, medium or high. Where the forces are weak, profit pools are deep."},
 {"keys": ["bcg", "boston", "growth share", "cash cow", "star", "question mark"], "name": "BCG matrix", "img": "BCG Matrix.png", "note": N("Strategy/BCG Matrix.md"),
  "line": "The BCG matrix. Stars, cash cows, question marks and dogs.",
  "say": "The BCG matrix plots each business by market growth and relative market share. Stars are high growth and high share, so invest. Cash cows are low growth but high share, so harvest the cash. Question marks need a decision: fund them or drop them. Dogs should be fixed or divested."},
 {"keys": ["ansoff", "growth strateg", "diversification", "market penetration", "market development"], "name": "Ansoff matrix", "img": "Ansoff Matrix.png", "note": N("Strategy/Ansoff Matrix.md"),
  "line": "The Ansoff matrix. Four routes to growth, from safest to riskiest.",
  "say": "Ansoff gives four ways to grow. Market penetration sells more of what you have to who you already serve, which is the safest. Product development brings new products to existing customers. Market development takes existing products to new markets. Diversification does both at once, and carries the most risk."},
 {"keys": ["4p", "four p", "4 p", "marketing mix", "stp", "segment", "positioning", "target"], "name": "the marketing mix", "img": "Marketing Mix 4Ps.png", "note": N("Marketing/STP and the 4Ps.md"),
  "line": "The marketing mix. Product, price, place and promotion.",
  "say": "First decide where to play with STP: segment the market, target the segments you can win, and position yourself with one clear idea. Then win there with the four Ps: product, price, place and promotion."},
 {"keys": ["funnel", "cac", "ltv", "lifetime value", "acquisition", "unit economics"], "name": "the customer funnel", "img": "Customer Funnel.png", "note": N("Marketing/Funnel, CAC and LTV.md"),
  "line": "The customer funnel. Fix the biggest drop-off first.",
  "say": "Customers move from awareness to interest, consideration, purchase and loyalty. Measure the drop at every stage and fix the biggest leak first. Then check unit economics: lifetime value should be at least three times the cost of acquiring a customer."},
 {"keys": ["profit tree", "profitability", "profit", "case"], "name": "the profit tree", "img": "Profit Tree.png", "note": N("Placements/How to Crack a Case.md"),
  "line": "The profit tree. The first structure for any profitability case.",
  "say": "To crack a case, clarify the question, build a structure, state a hypothesis early, do the math out loud, and finish with a clear recommendation. For profitability, split profit into revenue and costs, then revenue into volume, price and mix, and costs into fixed and variable."},
 {"keys": ["financial statement", "balance sheet", "income statement", "cash flow", "statement"], "name": "the financial statements", "img": "Financial Statements.png", "note": N("Finance/Financial Statements.md"),
  "line": "The three financial statements. Remember: profit is not cash.",
  "say": "The income statement shows profit over a period. The balance sheet shows assets, liabilities and equity at one moment. The cash flow statement tracks cash from operations, investing and financing. A growing company can be profitable and still run out of cash."},
 {"keys": ["npv", "irr", "wacc", "net present", "discount"], "name": "NPV, IRR and WACC", "note": N("Finance/NPV, IRR and WACC.md"),
  "line": "NPV, IRR and WACC.",
  "say": "Net present value discounts future cash flows at your required return and subtracts the investment. Accept if it is positive. IRR is the rate where NPV hits zero; accept if it beats the hurdle rate. WACC is the blended cost of debt and equity, and it is usually that hurdle."},
 {"keys": ["ratio", "roe", "roic", "margin", "p/e", "pe ratio"], "name": "key ratios", "note": N("Finance/Key Ratios.md"),
  "line": "Key financial ratios.", "say": "Margins show profitability, ROE and ROIC show returns, the current ratio shows liquidity, and debt to equity shows leverage. Always compare against the company's own history and its peers."},
 {"keys": ["lean", "six sigma", "dmaic", "operations", "little"], "name": "Lean and Six Sigma", "note": N("Operations/Lean and Six Sigma.md"),
  "line": "Lean and Six Sigma.", "say": "Lean removes waste, Six Sigma removes variation using define, measure, analyze, improve and control. And Little's law says inventory equals throughput times flow time, so cut the queues and you cut lead time."},
 {"keys": ["interview", "placement", "tell me about yourself", "star method"], "name": "placement interview prep", "note": N("Placements/Interview Prep.md"),
  "line": "Placement interview prep.", "say": "Keep your introduction to ninety seconds: present, past, future. Prepare five STAR stories covering leadership, conflict, failure and impact. And know your summer internship project cold, numbers included."},
 {"keys": ["start here", "how to use", "instructions", "gesture", "tutorial"], "name": "the guide", "note": N("Start Here.md"),
  "line": "Here's how to use me.", "say": "Pinch to grab, flick to throw, use two hands to stretch. Or just talk: say show SWOT, start a five minute timer, or quiz me."},
]
QUIZ = [
 {"q": "In the BCG matrix, what do you call a business with low market growth but high market share?", "a": "A cash cow. Harvest it and use the cash to fund your stars and question marks."},
 {"q": "Which two parts of SWOT are external to the company?", "a": "Opportunities and threats. Strengths and weaknesses are internal."},
 {"q": "Name the five forces in Porter's model.", "a": "New entrants, supplier power, buyer power, substitutes, and rivalry among existing competitors."},
 {"q": "A project's NPV is negative. Should you accept it?", "a": "No. A negative NPV means it destroys value at your required rate of return."},
 {"q": "What is a healthy ratio of customer lifetime value to acquisition cost?", "a": "Three to one or better, with payback ideally under twelve months."},
 {"q": "Selling a new product in a new market is which Ansoff strategy?", "a": "Diversification, the riskiest of the four."},
 {"q": "What does DMAIC stand for?", "a": "Define, measure, analyze, improve, control."},
 {"q": "Can a profitable company run out of cash?", "a": "Yes. Growth ties cash up in receivables and inventory, so profit and cash can diverge."},
]

# ======================= STATIC API =======================
def walk_notes(d, idx, root):
    out = {"name": d.name, "notes": [], "dirs": []}
    for p in sorted(d.iterdir(), key=lambda p: (p.name != "Start Here.md", p.is_dir(), p.name)):
        if p.is_dir():
            sub = walk_notes(p, idx, root)
            if sub["notes"] or sub["dirs"]:
                out["dirs"].append(sub)
        elif p.suffix == ".md":
            out["notes"].append({"title": p.stem, "file": f"{idx}/{p.relative_to(root).as_posix()}"})
    return out

api = SITE / "api"
api.mkdir()
(api / "config.json").write_text(json.dumps({"name": "NIMBUS", "orbs": [
    {"title": "PGDM Notes", "kind": "notes"}, {"title": "Frameworks", "kind": "media"}, {"title": "Tools", "kind": "tools"}, {"title": "Memory", "kind": "memory"}]}))
# the pane shows a short curated list (every note stays reachable by voice)
PANE_NOTES = ["Exam Calendar.md", "Weekly Timetable.md"]
tree = {"name": "PGDM Notes", "dirs": [], "notes": [{"title": Path(f).stem, "file": "0/" + f} for f in PANE_NOTES]}
(api / "tree0.json").write_text(json.dumps(tree))
PANE_IMGS = ["SWOT Analysis.png", "BCG Matrix.png"]
(api / "props.json").write_text(json.dumps({"name": "Frameworks", "items": PANE_IMGS, "dirs": []}))
(api / "orb.json").write_text(json.dumps({"state": "idle", "mood": "green", "wave": None}))
(api / "state.json").write_text("{}")
(api / "nimbus.json").write_text(json.dumps({"kb": KB, "quiz": QUIZ}))
shutil.copytree(notes_root, api / "note" / "0")

# ======================= PAGE PATCHES =======================
html = (REPO / "stage.html").read_text()

def sub(old, new, count=1):
    global html
    assert html.count(old) >= 1, f"patch anchor missing: {old[:70]!r}"
    html = html.replace(old, new, count if count else -1)

# static endpoints
sub('fetch("/config")', 'fetch("/api/config.json")')
sub('fetch("/tree?orb=" + i)', 'fetch("/api/tree" + i + ".json")')
sub('fetch("/props")', 'fetch("/api/props.json")')
sub('    const r = await fetch("/note?f=" + encodeURIComponent(card.def.file));',
    '    const r = card.def.text != null ? { ok: true, text: async () => card.def.text } : await fetch("/api/note/" + encodeURI(card.def.file));')
sub('fetch("/note?f=" + encodeURIComponent(it.file))', 'fetch("/api/note/" + encodeURI(it.file))')
sub('fetch("/state", { cache: "no-store" })', 'fetch("/api/state.json", { cache: "no-store" })')
# no server: stop the 8x/second ring poll and the 45x/second state POST (NIMBUS drives the ring)
sub('''    const r = await fetch("/orb", { cache: "no-store" });
    if (r.ok) RING.data = await r.json();''', '''    /* static build: the NIMBUS layer drives RING.data */''')
sub('''  fetch("/state", { method: "POST", body: JSON.stringify(st) })
    .then(r => r.json()).then(applyCmds).catch(() => {});''', '''  void st;   /* static build: no render page to feed */''')
# foley sounds on by default (?sound=0 mutes)
sub('''const ICO = { dir0: "▸", dir1: "▾", note: "▤", prop: "▦", widget: "▣" };''', '''const ICO = { dir0: "▸", dir1: "▾", note: "▤", prop: "▦", widget: "▣", mem: "◆", memnone: "·" };''')
sub('const SOUND = Q.get("sound") === "1";', 'const SOUND = Q.get("sound") !== "0";')

# ---- NIMBUS LOOK + SOUND for the board itself ----
# sound effects come from the NIMBUS sound set (nimbus.js); ?sound=0 still mutes
sub('''const foley = {
  grab:    () => { _noise(0.04, 900, 2200, 0.10); _tone(150, 0.06, 0.10); },
  place:   () => _tone(120, 0.06, 0.07),
  throw_:  () => _noise(0.22, 300, 900, 0.14, 1600),
  void_:   () => { _noise(0.25, 500, 1400, 0.12, 180); _tone(280, 0.28, 0.09, "square", 70); },
  arrive:  () => { _tone(523, 0.10, 0.06); _tone(659, 0.10, 0.06, "sine", 0, 0.07); _tone(784, 0.14, 0.07, "sine", 0, 0.14); },
  yank:    () => { _tone(220, 0.12, 0.10, "sawtooth", 900); _noise(0.06, 1200, 3000, 0.08); },
};''', '''const _sfx = k => { if (SOUND && window.NimbusSFX && NimbusSFX[k]) NimbusSFX[k](); };
const foley = {
  grab:   () => _sfx("grab"),  place:  () => _sfx("place"), throw_: () => _sfx("toss"),
  void_:  () => _sfx("poof"),  arrive: () => _sfx("arrive"), yank:  () => _sfx("pull"),
};''')
# the ring: a NIMBUS halo (rotating ice-violet band, orbiting sparks, voice bars)
_i = html.index("function drawRing(sc) {"); _j = html.index("function renderRings() {")
html = html[:_i] + r'''function drawRing(sc) {
  const d = RING.data, st = d.state || "idle";
  const amp = st === "speaking" ? ringAmp() : (RING.amp *= 0.9);
  const t = Date.now() / 1000, x = sc.ctx;
  ensureRingRes(sc);
  const tap = Math.exp(-Math.max(0, t - sc.tapT) * 4);
  const ICE = [143, 227, 255], PERI = [140, 158, 255], VIO = [183, 148, 255], ROSE = [255, 159, 216], WH = [246, 244, 255];
  const C = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;
  x.setTransform(sc.RES, 0, 0, sc.RES, 0, 0);
  x.clearRect(0, 0, 440, 440);
  x.save(); x.translate(220, 220);
  // the nimbus: a soft violet cloud of light around the ring
  const gr = 214 + amp * 6;
  const halo = x.createRadialGradient(0, 0, 120, 0, 0, gr);
  halo.addColorStop(0, C(PERI, 0)); halo.addColorStop(0.6, C(VIO, 0.12 + amp * 0.18 + tap * 0.12)); halo.addColorStop(1, C(VIO, 0));
  x.fillStyle = halo; x.beginPath(); x.arc(0, 0, gr, 0, 7); x.fill();
  // the band: an ice > periwinkle > violet > rose gradient that slowly turns
  let band = C(PERI, 0.95);
  if (x.createConicGradient) {
    band = x.createConicGradient(t * 0.35, 0, 0);
    band.addColorStop(0, C(ICE, 1)); band.addColorStop(0.3, C(PERI, 1)); band.addColorStop(0.6, C(VIO, 1));
    band.addColorStop(0.82, C(ROSE, 1)); band.addColorStop(1, C(ICE, 1));
  }
  x.shadowColor = C(VIO, 0.95); x.shadowBlur = 16 + amp * 30 + tap * 18;
  x.strokeStyle = band; x.lineWidth = 9 + amp * 7 + tap * 3;
  x.beginPath(); x.arc(0, 0, 176, 0, 7); x.stroke();
  x.shadowBlur = 0;
  x.strokeStyle = C(WH, 0.5); x.lineWidth = 1.2; x.beginPath(); x.arc(0, 0, 191, 0, 7); x.stroke();
  x.strokeStyle = C(PERI, 0.32); x.lineWidth = 1; x.beginPath(); x.arc(0, 0, 161, 0, 7); x.stroke();
  // three sparks orbit on the band
  for (let k = 0; k < 3; k++) {
    const a = t * (0.55 + k * 0.22) + k * 2.1, rr = 176 + Math.sin(t * 1.3 + k) * 5;
    x.shadowColor = C(WH, 1); x.shadowBlur = 16; x.fillStyle = C(WH, 0.95);
    x.beginPath(); x.arc(Math.cos(a) * rr, Math.sin(a) * rr, 3.4 - k * 0.6, 0, 7); x.fill();
  }
  x.shadowBlur = 0;
  // state: idle = breathing dots, listening = ripples in, thinking = comet, speaking = voice bars
  if (st === "speaking") {
    const w = d.wave || [];
    x.lineCap = "round"; x.lineWidth = 3.2;
    for (let i = 0; i < 72; i++) {
      const a = i / 72 * Math.PI * 2 - Math.PI / 2, v = Math.min(1, Math.abs(w[i % (w.length || 1)] || 0) / 60);
      const len = 3 + v * (16 + amp * 14);
      x.strokeStyle = C(i % 2 ? ICE : VIO, 0.9);
      x.beginPath(); x.moveTo(Math.cos(a) * 134, Math.sin(a) * 134); x.lineTo(Math.cos(a) * (134 + len), Math.sin(a) * (134 + len)); x.stroke();
    }
  } else if (st === "listening") {
    for (let k = 0; k < 3; k++) {
      const p = (t * 0.8 + k / 3) % 1;
      x.globalAlpha = (1 - p) * p * 2.2; x.strokeStyle = C(ICE, 0.95); x.lineWidth = 2;
      x.beginPath(); x.arc(0, 0, 160 - p * 34, 0, 7); x.stroke();
    }
    x.globalAlpha = 1;
  } else if (st === "thinking") {
    const a0 = t * 3.2;
    for (let i = 0; i < 12; i++) {
      x.globalAlpha = 0.7 * (1 - i / 12); x.strokeStyle = C(i < 4 ? WH : VIO, 1); x.lineWidth = 6 - i * 0.35; x.lineCap = "round";
      x.beginPath(); x.arc(0, 0, 146, a0 - (i + 1) * 0.09, a0 - i * 0.09); x.stroke();
    }
    x.globalAlpha = 1;
  } else {
    for (let i = 0; i < 60; i++) {
      const a = i / 60 * Math.PI * 2;
      x.fillStyle = C(i % 5 ? PERI : ICE, 0.22 + 0.22 * Math.sin(t * 1.8 - i * 0.35));
      x.beginPath(); x.arc(Math.cos(a) * 146, Math.sin(a) * 146, i % 5 ? 1.3 : 2.2, 0, 7); x.fill();
    }
  }
  // glass core
  const core = x.createRadialGradient(0, -40, 8, 0, 0, 126);
  core.addColorStop(0, "rgba(255,255,255,0.10)"); core.addColorStop(1, C(PERI, 0.03));
  x.fillStyle = core; x.beginPath(); x.arc(0, 0, 124, 0, 7); x.fill();
  x.strokeStyle = C(PERI, 0.5); x.lineWidth = 1.4; x.beginPath(); x.arc(0, 0, 124, 0, 7); x.stroke();
  // wordmark + status
  const nm = (CFG.name || "NIMBUS").toUpperCase();
  x.textAlign = "center"; x.textBaseline = "middle";
  x.shadowColor = "rgba(5,6,22,0.9)"; x.shadowBlur = 8;
  const lg = x.createLinearGradient(-95, 0, 95, 0);
  lg.addColorStop(0, C(ICE, 1)); lg.addColorStop(0.5, "#ffffff"); lg.addColorStop(1, C(VIO, 1));
  x.fillStyle = lg;
  x.font = `300 ${nm.length <= 6 ? 31 : 22}px "Avenir Next", "Segoe UI", system-ui, sans-serif`;
  if ("letterSpacing" in x) x.letterSpacing = "9px";
  x.fillText(nm, 4.5, -10);
  x.fillStyle = C(ICE, 0.95);
  x.font = "600 11.5px ui-monospace, 'SF Mono', Menlo, monospace";
  if ("letterSpacing" in x) x.letterSpacing = "5px";
  const status = { idle: "READY", listening: "LISTENING", thinking: "THINKING", speaking: "SPEAKING" }[st] || "READY";
  x.fillText(status, 2.5, 26);
  if ("letterSpacing" in x) x.letterSpacing = "0px";
  x.shadowBlur = 0;
  x.restore();
}

''' + html[_j:]
# row + card titles without file extensions
sub('out.push({ d: depth, t: x.split("/").pop(), k: "prop", f: x });',
    'out.push({ d: depth, t: x.split("/").pop().replace(/\\.[a-z0-9]+$/i, ""), k: "prop", f: x });')

# ---- ONE AT A TIME: one folder pane, one open note/image ----
sub('''  const ex = items.find(i => i.type === "browser" && i.bkind === kind);
  if (ex) { killItem(ex); return; }''', '''  const ex = items.find(i => i.type === "browser" && i.bkind === kind);
  if (ex) { killItem(ex); return; }
  items.filter(i => i.type === "browser").forEach(killItem);   // one pane at a time''')
sub('''async function openPanel(card) {
  if (items.some(i => i.type === "panel" && i.def === card.def)) return;''', '''// new notes / images / tools land in the emptiest spot instead of stacking
function freeSpot(w = 480, h = 480) {
  // the spot where a w x h card overlaps the least: other cards, the ring and the arc where
  // its menu circles bloom all count; the card is kept fully on screen, clear of the HUD
  const W = innerWidth, H = innerHeight;
  const rects = items.filter(i => ["panel", "img", "model", "tool", "browser"].includes(i.type) &&
                                  i.el.isConnected && !(i.anim && i.anim.k === "out"))
    .map(i => { const s = i.scale || 1, a = i.el.offsetWidth * s / 2, b = i.el.offsetHeight * s / 2;
                return [i.x - a, i.y - b, i.x + a, i.y + b, 1]; });
  const ring = items.find(i => i.type === "widget" && i.def && i.def.w === "ring" && i.el.isConnected);
  if (ring) { const r = 200 * (ring.scale || 1), R = r + 130 + 80;
              rects.push([ring.x - r, ring.y - r, ring.x + r, ring.y + r, 20],       // the ring itself: never cover it
                         [ring.x + r, ring.y - R, ring.x + R, ring.y + R, 0.4]); }  // where its menu circles bloom
  const hw = Math.min(w, W - 40) / 2, hh = Math.min(h, H - 110) / 2;
  let best = { x: W / 2, y: H / 2 }, bs = Infinity;
  for (const fx of [.55, .72, .38, .86, .22]) for (const fy of [.5, .34, .66]) {
    const x = Math.min(Math.max(W * fx, hw + 20), W - hw - 20);
    const y = Math.min(Math.max(H * fy, hh + 64), H - hh - 40);
    let sc = Math.abs(fx - .6) * 3000 + Math.abs(fy - .5) * 2000;   // gentle pull to centre-right
    for (const q of rects) {
      const ox = Math.min(x + hw, q[2]) - Math.max(x - hw, q[0]), oy = Math.min(y + hh, q[3]) - Math.max(y - hh, q[1]);
      if (ox > 0 && oy > 0) sc += ox * oy * q[4];
    }
    if (sc < bs) { bs = sc; best = { x, y }; }
  }
  return best;
}
function closeContent() {
  items.filter(i => i.type === "panel" || i.type === "img" || i.type === "model").forEach(killItem);
}
async function openPanel(card) {
  if (items.some(i => i.type === "panel" && i.def && i.def.file === card.def.file &&
                      i.el.isConnected && !(i.anim && i.anim.k === "out"))) return;
  if (window.BH && BH.onOpen && !card.def.voice) BH.onOpen(card.def.file);''')
sub('''              body: el.querySelector(".scroll") };
  items.push(p);
}''', '''              body: el.querySelector(".scroll") };
  p.anim = { k: "in", t: 0 }; el.style.opacity = "0.05";
  { const f = freeSpot(Math.max(el.offsetWidth, 560) * p.scale, Math.max(el.offsetHeight, 700) * p.scale); p.x = f.x; p.y = f.y; }
  items.push(p);
}''')
sub('''      } else if (row.k === "prop") {
        const src = "/media/" + row.f;''', '''      } else if (row.k === "prop") {
        if (window.BH && BH.onOpen) BH.onOpen(row.f);
        const src = "/media/" + row.f;''')
# a pane retracts the orb menu (they sat under the pane and could not be reached),
# sits clear of the HUD, and shrinks to fit shorter screens
sub('''    b.anim = { k: "in", t: 0 }; b.el.style.opacity = "0.05";
    items.push(b);''', '''    b.anim = { k: "in", t: 0 }; b.el.style.opacity = "0.05";
    { const s = Math.min(1, (innerHeight - 150) / 720); b.scale = s;
      b.y = Math.min(Math.max(b.y, 360 * s + 72), innerHeight - 360 * s - 60); }
    items.filter(i => i.type === "orb").forEach(killItem);
    items.push(b);''')
sub('''  const p = { el, id: UID++, type: "panel", def: card.def, x: innerWidth * 0.5,
              y: innerHeight * 0.44, scale: 1,''', '''  const p = { el, id: UID++, type: "panel", def: card.def, x: innerWidth * 0.5,
              y: innerHeight * 0.5, scale: Math.min(1, (innerHeight - 170) / 720),''')
# opening the menu closes an open pane, so the orbs are never hidden under it
sub('''  if (up.length) { up.forEach(killItem); return; }''', '''  if (up.length) { up.forEach(killItem); return; }
  items.filter(i => i.type === "browser").forEach(killItem);''')
# notes list before folders, so "Start Here" is the first row
sub('''  const walk = (d, path, depth, isProps) => {
    d.dirs.forEach(sub => {''', '''  const walk = (d, path, depth, isProps) => {
    if (depth === 0 && !isProps) d.notes.forEach(x => out.push({ d: depth, t: x.title, k: "note", f: x.file }));
    d.dirs.forEach(sub => {''')
sub('''    (isProps ? d.items : d.notes).forEach(x => {''', '''    (isProps ? d.items : (depth === 0 ? [] : d.notes)).forEach(x => {''')
# orb captions
sub('''body: `${p.dirs} folders · ${p.leaves} props`, orb: "props" };''', '''body: `${p.leaves} frameworks`, orb: "props" };''')
sub('''body: `${v.dirs} folders · ${v.leaves} notes`, orb: i };''', '''body: `${v.dirs ? v.dirs + " subjects · " : ""}${v.leaves} notes`, orb: i };''')
# bigger framework images
sub('max-width:32vw; max-height:44vh;', 'max-width:46vw; max-height:60vh;')
# ---- TOOLS orb: Timer / Stopwatch as grabbable glass cards
sub('''    if (CFG.orbs[i].kind === "media") continue;''', '''    if (CFG.orbs[i].kind !== "notes") continue;''')
sub('''  const defs = (CFG.orbs || []).map((o, i) => {
    if (o.kind === "media") {''', '''  const defs = (CFG.orbs || []).map((o, i) => {
    if (o.kind === "tools")
      return { title: o.title || "Tools", body: "Timer · Stopwatch", orb: "tools" };
    if (o.kind === "memory") {
      const n = window.NimbusMemory ? NimbusMemory.count() : 0;
      return { title: o.title || "Memory", body: n + (n === 1 ? " upload" : " uploads"), orb: "memory" };
    }
    if (o.kind === "media") {''')
sub('''    const label = String(kind === "props" ? "Props"''', '''    const label = String(kind === "props" ? "Frameworks" : kind === "tools" ? "Tools" : kind === "memory" ? "Memory"''')
sub('''  if (b.bkind === "props" && PROPSTREE) walk(PROPSTREE, "", 0, true);''', '''  if (b.bkind === "memory") {
    const m = window.NimbusMemory ? NimbusMemory.list() : [];
    m.forEach(x => out.push({ d: 0, t: x.name.replace(/\.[a-z0-9]+$/i, ""), k: "mem", f: x.id }));
    if (!m.length) out.push({ d: 0, t: "Empty: use Memory, top right", k: "memnone", f: "" });
    return out;
  }
  if (b.bkind === "tools") {
    [["Timer", "timer"], ["Stopwatch", "stopwatch"]]
      .forEach(([t, f]) => out.push({ d: 0, t, k: "widget", f }));
    return out;
  }
  if (b.bkind === "props" && PROPSTREE) walk(PROPSTREE, "", 0, true);''')
sub('''      } else if (row.k === "prop") {''', '''      } else if (row.k === "mem") {
        if (window.NimbusMemory) NimbusMemory.show(row.f);
        killItem(b);
      } else if (row.k === "widget") {
        openTool(row.f);
        killItem(b);
      } else if (row.k === "prop") {''')
sub('''        it.x = Math.min(b.x + 480, innerWidth - 240); it.y = b.y;''', '''        { const f = freeSpot(innerWidth * 0.42, innerHeight * 0.52); it.x = f.x; it.y = f.y; }''')

# ---- HANDS: the original barehands tracking, pinch and gestures run UNCHANGED.
# Only additions for the NIMBUS cards: a quick pinch-tap on a timer / stopwatch / day-card key
# presses it, with the same tap test the original uses for menu rows (released within 350 ms,
# moved under 24 px); and these cards never latch into 3D rotate.
sub('''    // PHASE 2 quick-tap releases: the RING toggles its orbital bloom;''', '''    if (c.type === "tool" && !cur.probKill) {
      const kMs = performance.now() - (cur.grabT || 0);
      const kTr = Math.hypot(cur.x - (c.tapX ?? cur.x), cur.y - (c.tapY ?? cur.y));
      if (kMs < 350 && kTr < 24) toolTap(c, { x: c.tapX ?? cur.x, y: c.tapY ?? cur.y });
    }
    // PHASE 2 quick-tap releases: the RING toggles its orbital bloom;''')
sub('''if (mp >= 1) {               // LATCHED: 3D rotate''', '''if (mp >= 1 && held.type !== "tool") {               // LATCHED: 3D rotate''')
# the mouse cursor (id 9) is not a camera hand: never drop it for being unseen
sub('Object.keys(cursors).map(Number).forEach(i => { if (!seen.has(i)) dropCursor(i); });',
    'Object.keys(cursors).map(Number).forEach(i => { if (!seen.has(i) && i !== 9) dropCursor(i); });')

# branding
sub("<title>barehands</title>", "<title>NIMBUS | PGDM Intelligence</title>")
sub('''<div id="boot">BAREHANDS<br><span style="color:#a8d8cf;font-size:12px;letter-spacing:0.22em">by jaredrhod</span><br>''',
    '''<div id="boot">NIMBUS<br><span style="color:#aab0e0;font-size:12px;letter-spacing:0.22em">PGDM INTELLIGENCE INTERFACE</span><br>''')
sub('toast("barehands v1.0", 2000);', 'toast("NIMBUS online", 2000);')
sub('x: innerWidth * 0.30, y: innerHeight * 0.45, scale: 1,', 'x: innerWidth * 0.26, y: innerHeight * 0.47, scale: 0.76,')
import re
html, n = re.subn(r'<div id="hint">.*?</div>',
    '<div id="hint">Pinch = grab &nbsp;·&nbsp; Quick pinch the ring = menu &nbsp;·&nbsp; <b>Memory</b> (top right) = your uploads &nbsp;·&nbsp; <b>Enter</b> = type a command</div>', html, count=1, flags=re.S)
assert n == 1

# expose a small API + mouse backup, inside the module scope
BH_JS = r'''
// ---- NIMBUS bridge: the UI layer (nimbus.js) drives the board through this
window.BH = {
  onOpen: null,
  openNote(file, title) { return openPanel({ def: { file, title, voice: true } }); },
  openProp(path, opts = {}) {
    items.filter(i => i.type === "browser").forEach(killItem);
    const src = "/media/" + path;
    const it = isModelSrc(src) ? makeModel(src, path) : makeImage(src, path.replace(/\.[a-z0-9]+$/i, ""));
    const f = freeSpot(innerWidth * 0.42, innerHeight * 0.52);
    it.x = opts.x != null ? innerWidth * opts.x : f.x; it.y = opts.y != null ? innerHeight * opts.y : f.y;
    if (opts.scale) it.scale = opts.scale;
    it.anim = { k: "in", t: 0 }; it.el.style.opacity = "0.05";
    items.push(it); return it;
  },
  openImage(src, title) {
    items.filter(i => i.type === "browser").forEach(killItem);
    const it = makeImage(src, title);
    const f = freeSpot(innerWidth * 0.42, innerHeight * 0.52);
    it.x = f.x; it.y = f.y; it.anim = { k: "in", t: 0 }; it.el.style.opacity = "0.05";
    items.push(it); return it;
  },
  openText(title, text) { return openPanel({ def: { file: "memory/" + title, title, text: String(text).slice(0, 20000), voice: true } }); },
  openDoc(src, title) {
    const t = openTool("doc"); if (!t) return null;
    t.src = src; t.el.querySelector(".tbar").textContent = title; t.el.querySelector(".tdoc").src = src + "#toolbar=0&view=FitH";
    return t;
  },
  closeAll() { items.filter(i => !(i.type === "widget" && i.def && i.def.w === "ring")).forEach(killItem); },
  toggleMenu() {
    const r = items.find(i => i.type === "widget" && i.def && i.def.w === "ring");
    if (r) { const sc = RINGS.get(r.id); if (sc) sc.tapT = Date.now() / 1000; ringToggle(r); }
  },
  menuOpen() { return items.some(i => i.type === "orb" && i.el.isConnected && !(i.anim && i.anim.k === "out")); },
  setRing(state, wave) { RING.data = { state, mood: "green", wave: wave || null }; },
  hands() { return Object.keys(cursors).filter(k => k !== "9").length; },
  ready() { return !!landmarker; },
};

// ---- TOOLS: Timer, Stopwatch. Glass cards with big tap keys;
// pinch-drag moves them, a quick pinch on a key presses it.
const DAYK = { routine: 1, calendar: 1, plan: 1 };
const TOOL_DEF = {
  doc: { title: "Document", body: `<iframe class="tdoc" title="document"></iframe><div class="tkeys k2"><b data-a="full">Open full</b><b data-a="x" class="tx">Close</b></div>` },
  routine: { title: "Daily Routine", body: `<div class="dlist"></div><div class="tkeys k1"><b data-a="x" class="tx">Close</b></div>` },
  calendar: { title: "Today's Calendar", body: `<div class="dlist"></div><div class="tkeys k1"><b data-a="x" class="tx">Close</b></div>` },
  plan: { title: "Day Plan", body: `<div class="dlist"></div><div class="tkeys k2"><b data-a="replan" class="tgo">Replan</b><b data-a="x" class="tx">Close</b></div>` },
  timer: { title: "Timer", body:
    `<div class="tdisp">05:00</div><div class="tsub">presentation · GD · exam</div>
     <div class="tkeys k3"><b data-a="m1">+1 min</b><b data-a="m5">+5 min</b><b data-a="m10">+10 min</b>
     <b data-a="go" class="tgo">Start</b><b data-a="rs">Reset</b><b data-a="x" class="tx">Close</b></div>` },
  stopwatch: { title: "Stopwatch", body:
    `<div class="tdisp">00:00.0</div><div class="tsub tlaps">&nbsp;</div>
     <div class="tkeys k3"><b data-a="go" class="tgo">Start</b><b data-a="lap">Lap</b><b data-a="rs">Reset</b></div>
     <div class="tkeys k1"><b data-a="x" class="tx">Close</b></div>` },
};
function openTool(kind, opts = {}) {
  const d = TOOL_DEF[kind]; if (!d) return null;
  const ex = items.find(i => i.type === "tool" && i.tool === kind && i.el.isConnected && !(i.anim && i.anim.k === "out"));
  if (ex) return ex;
  const el = document.createElement("div");
  el.className = "card tool tool-" + kind;
  el.innerHTML = `<div class="tbar">${d.title}</div>` + d.body;
  BEHIND.appendChild(el);
  const t = { el, id: UID++, type: "tool", tool: kind, def: { title: d.title, file: "" },
    x: 0, y: 0, scale: Math.min(1, (innerHeight - 140) / 640),
    vx: 0, vy: 0, grabbedBy: [], ox: 0, oy: 0, flying: false, stretch: null,
    st: { left: 300000, end: 0, run: false, acc: 0, t0: 0, laps: [], expr: "", res: "" } };
  if (opts.scale) t.scale = opts.scale;
  toolDraw(t);                                   // fill it first, so placement knows its real size
  { const f = freeSpot(el.offsetWidth * t.scale, el.offsetHeight * t.scale); t.x = opts.x ?? f.x; t.y = opts.y ?? f.y; }
  t.anim = { k: "in", t: 0 }; el.style.opacity = "0.05";
  items.push(t); return t;
}
const fmt = (ms, tenths) => {
  ms = Math.max(0, ms); const m = Math.floor(ms / 60000), s = Math.floor(ms / 1000) % 60;
  return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0") + (tenths ? "." + Math.floor(ms / 100) % 10 : "");
};
function beep(n = 3) {
  try { const a = new (window.AudioContext || window.webkitAudioContext)();
    for (let i = 0; i < n; i++) { const o = a.createOscillator(), g = a.createGain(), t0 = a.currentTime + i * 0.45;
      o.frequency.value = 880; g.gain.setValueAtTime(0.0001, t0); g.gain.exponentialRampToValueAtTime(0.18, t0 + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.35); o.connect(g).connect(a.destination); o.start(t0); o.stop(t0 + 0.4); } } catch (e) {}
}
function toolDraw(t) {
  const s = t.st, q = sel => t.el.querySelector(sel), now = performance.now();
  if (DAYK[t.tool]) {
    if (window.NimbusDay && t.dv !== NimbusDay.ver) { t.dv = NimbusDay.ver; q(".dlist").innerHTML = NimbusDay.html(t.tool); }
    return;
  }
  if (t.tool === "timer") {
    const left = s.run ? s.end - now : s.left;
    if (s.run && left <= 0) { s.run = false; s.left = 0; if (window.NimbusSFX) NimbusSFX.alarm(); else beep(4); t.el.classList.add("tdone"); setTimeout(() => t.el.classList.remove("tdone"), 4000); }
    q(".tdisp").textContent = fmt(s.run ? left : s.left);
    q(".tdisp").classList.toggle("twarn", s.run && left < 60000);
    q(".tgo").textContent = s.run ? "Pause" : "Start";
  } else if (t.tool === "stopwatch") {
    q(".tdisp").textContent = fmt(s.acc + (s.run ? now - s.t0 : 0), true);
    q(".tgo").textContent = s.run ? "Pause" : "Start";
    q(".tlaps").innerHTML = s.laps.length ? s.laps.slice(-3).map((l, i, a) => `L${s.laps.length - a.length + i + 1} ${fmt(l, true)}`).join(" · ") : "&nbsp;";
  }
}
function toolAct(t, a, arg) {
  const s = t.st, now = performance.now();
  if (a === "x") { killItem(t); return; }
  if (DAYK[t.tool]) { if (window.NimbusDay) NimbusDay.act(t.tool, a); toolDraw(t); return; }
  if (t.tool === "doc") { if (a === "full" && t.src) window.open(t.src, "_blank"); return; }
  if (t.tool === "timer") {
    const left = s.run ? s.end - now : s.left;
    if (a[0] === "m") { s.left = Math.max(0, left) + 60000 * (+a.slice(1)); if (s.run) s.end = now + s.left; }
    else if (a === "set") { s.left = arg; s.run = false; }
    else if (a === "go") { if (s.run) { s.left = Math.max(0, left); s.run = false; } else if (s.left > 0) { s.end = now + s.left; s.run = true; } }
    else if (a === "start") { if (!s.run && s.left > 0) { s.end = now + s.left; s.run = true; } }
    else if (a === "pause") { if (s.run) { s.left = Math.max(0, left); s.run = false; } }
    else if (a === "rs") { s.run = false; s.left = 0; }
  } else if (t.tool === "stopwatch") {
    if (a === "go" || a === "start" || a === "pause") {
      if (s.run && a !== "start") { s.acc += now - s.t0; s.run = false; }
      else if (!s.run && a !== "pause") { s.t0 = now; s.run = true; }
    }
    else if (a === "lap") s.laps.push(s.acc + (s.run ? now - s.t0 : 0));
    else if (a === "rs") { s.run = false; s.acc = 0; s.laps = []; }
  }
  toolDraw(t);
}
// distance from a point to a key's box (0 = inside)
function keyDist(b, x, y) {
  const r = b.getBoundingClientRect();
  return Math.hypot(Math.max(r.left - x, 0, x - r.right), Math.max(r.top - y, 0, y - r.bottom));
}
function nearestKey(keys, x, y, max) {
  let best = null, bd = max;
  for (const b of keys) { const d = keyDist(b, x, y); if (d <= bd) { bd = d; best = b; } }
  return best;
}
function toolTap(t, cur) {
  const keys = [...t.el.querySelectorAll("[data-a]")];
  // what you saw lit up while aiming is what gets pressed; otherwise the key at / nearest the cursor
  let b = cur.hovKey && keys.includes(cur.hovKey) && performance.now() - (cur.hovT || 0) < 450 ? cur.hovKey : null;
  if (!b) b = nearestKey(keys, cur.x, cur.y, 34);
  if (!b) return false;
  b.classList.remove("hit"); void b.offsetWidth; b.classList.add("hit");
  const a = b.dataset.a;
  if (window.NimbusSFX) NimbusSFX.key(keys.indexOf(b));
  if (a === "x") setTimeout(() => toolAct(t, a), 0); else toolAct(t, a);
  return true;
}
setInterval(() => items.forEach(i => { if (i.type === "tool" && i.el.isConnected) toolDraw(i); }), 100);
BH.openTool = (kind, opts) => openTool(kind, opts || {});
BH.ringTo = (fx, fy, sc) => {
  const r = items.find(i => i.type === "widget" && i.def && i.def.w === "ring" && i.el.isConnected);
  if (!r) return;
  const x0 = r.x, y0 = r.y, s0 = r.scale || 1, x1 = innerWidth * fx, y1 = innerHeight * fy, t0 = performance.now();
  const step = () => {
    const k = Math.min(1, (performance.now() - t0) / 800), e = k * k * (3 - 2 * k);
    r.x = x0 + (x1 - x0) * e; r.y = y0 + (y1 - y0) * e; r.scale = s0 + (sc - s0) * e;
    if (k < 1) setTimeout(step, 16);
  };
  step();
};
BH.tool = (kind, a, arg) => { const t = openTool(kind); if (t) toolAct(t, a, arg); return t; };
BH.closeTool = (kind) => items.filter(i => i.type === "tool" && i.tool === kind).forEach(killItem);

// what a pinch would press right now: the key / row under each open hand lights up
setInterval(() => {
  document.querySelectorAll(".hov").forEach(e => e.classList.remove("hov"));
  const hs = [0, 1].map(k => cursors[k]).filter(c => c && !c.pinched && c.el.isConnected);
  if (!hs.length) return;
  for (const c of hs) {
    // the top card under this hand; on a tool card, light the ONE key a pinch would press (magnetic: the nearest within 34 px)
    const it = hitTest(c);
    if (!it || (it.anim && it.anim.k === "out")) { c.hovKey = null; continue; }
    if (it.type === "tool") {
      const k = nearestKey([...it.el.querySelectorAll("[data-a]")], c.x, c.y, 34);
      c.hovKey = k; c.hovT = performance.now();
      if (k) k.classList.add("hov");
    } else if (it.type === "browser") {
      c.hovKey = null;
      for (const b of it.el.querySelectorAll(".brow")) { const r = b.getBoundingClientRect();
        if (c.x >= r.left && c.x <= r.right && c.y >= r.top && c.y <= r.bottom) b.classList.add("hov"); }
    } else c.hovKey = null;
  }
}, 50);

// ---- MOUSE BACKUP: click = tap, drag = move/scroll, wheel = scroll
(() => {
  const MID = 9;
  const held = () => items.find(k => k.grabbedBy.includes(MID));
  addEventListener("mousedown", e => {
    if (e.button !== 0 || (e.target.closest && e.target.closest(".nb-ui"))) return;
    const cur = getCursor(MID);
    cur.el.style.display = "none";
    cur.x = e.clientX; cur.y = e.clientY; cur.probKill = false;
    cur.history = [{ x: cur.x, y: cur.y, t: performance.now() }];
    const c = hitTest(cur);
    if (c && c.grabbedBy.length < 2) beginGrab(c, MID, cur);
  });
  addEventListener("mousemove", e => {
    const cur = cursors[MID]; if (!cur) return;
    cur.x = e.clientX; cur.y = e.clientY;
    cur.history.push({ x: cur.x, y: cur.y, t: performance.now() });
    if (cur.history.length > 10) cur.history.shift();
    const h = held(); if (!h) return;
    if (h.mode === "scroll") {
      const box = h.body.parentElement.clientHeight;
      const maxS = Math.max(0, h.body.offsetHeight - box + 40);
      h.scrollY = Math.min(maxS, Math.max(0, h.scroll0 - (cur.y - h.grabY0)));
      h.body.style.transform = `translateY(${-h.scrollY}px)`;
    } else if (h.mode === "move" || h.mode === "rotate") {
      h.mode = "move"; h.x = cur.x + h.ox; h.y = cur.y + h.oy;
    }
  });
  addEventListener("mouseup", () => {
    const cur = cursors[MID]; if (!cur) return;
    const h = held(); if (h) endGrab(h, MID, cur);
    cur.el.remove(); delete cursors[MID];
  });
  addEventListener("wheel", e => {
    const p = hitTest({ x: e.clientX, y: e.clientY });
    if (!p || !p.body || (p.type !== "panel" && p.type !== "browser")) return;
    const box = p.body.parentElement.clientHeight;
    const maxS = Math.max(0, p.body.offsetHeight - box + 40);
    p.scrollY = Math.min(maxS, Math.max(0, (p.scrollY || 0) + e.deltaY));
    p.body.style.transform = `translateY(${-p.scrollY}px)`;
  }, { passive: true });
})();
'''
i = html.rfind("</script>")
html = html[:i] + BH_JS + html[i:]

badge = ('<div class="nb-badge">Made by <b>RUBIN</b>'
         '</div>')
sub("<body>", "<body>" + badge)
sub("</head>", '<link rel="stylesheet" href="/nimbus.css">\n'
    '<script>if (/[?&]raftest/.test(location.search)) window.requestAnimationFrame = cb => setTimeout(() => cb(performance.now()), 16);</script>\n</head>')
j = html.rfind("</body>")
html = html[:j] + '<script src="/nimbus.js"></script>\n' + html[j:]

# ---- RESILIENT BOOT: no camera (denied / none / busy) must not kill the board.
# The board, mouse backup and voice keep working; hand tracking simply waits.
sub('''async function boot() {
  await pickInitialCam();
  const vision = await FilesetResolver.forVisionTasks(''', '''async function boot() {
  try { await pickInitialCam(); }
  catch (e) { window.NOCAM = e.message || "no camera"; }
  try {
  const vision = await FilesetResolver.forVisionTasks(''')
sub('''    minHandPresenceConfidence: 0.5 });
  document.getElementById("boot").remove();''', '''    minHandPresenceConfidence: 0.5 });
  } catch (e) { landmarker = null; window.NOTRACK = e.message || "tracker failed"; }
  document.getElementById("boot").remove();''')
sub('''    if (cam.currentTime !== lastVideoTs) {
      lastVideoTs = cam.currentTime;''', '''    if (landmarker && cam.readyState >= 2 && cam.currentTime !== lastVideoTs) {
      lastVideoTs = cam.currentTime;''')
# the board's own teal / cyan palette becomes NIMBUS periwinkle-violet (same lightness, new hue)
import colorsys
def _remap(r, g, b):
    h, l, sat = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    hd = h * 360
    if 140 <= hd <= 200 and sat > 0.12:
        r2, g2, b2 = colorsys.hls_to_rgb((248 + (hd - 170) * 0.5) / 360, l, min(1, sat * 0.95))
        return round(r2 * 255), round(g2 * 255), round(b2 * 255)
    return r, g, b
html = re.sub(r"rgba\((\d+),\s*(\d+),\s*(\d+)", lambda m: "rgba(%d,%d,%d" % _remap(*map(int, m.groups())), html)
html = re.sub(r"#([0-9a-fA-F]{6})\b", lambda m: "#%02x%02x%02x" % _remap(*(int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4))), html)
(SITE / "index.html").write_text(html)

shutil.copy(ROOT / "ui" / "nimbus.js", SITE / "nimbus.js")
shutil.copy(ROOT / "ui" / "nimbus.css", SITE / "nimbus.css")
(SITE / "_redirects").write_text("/stage.html /index.html 200\n")
(SITE / "_headers").write_text("/*\n  Permissions-Policy: camera=(self), microphone=(self)\n")
(SITE / "LICENSE").write_text((REPO / "LICENSE").read_text())
print("built", len(NOTES), "notes,", len(IMGS), "framework images,", len(KB), "voice topics,", len(QUIZ), "quiz questions")
