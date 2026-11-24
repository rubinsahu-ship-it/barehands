# NIMBUS: PGDM Intelligence Interface

Made by RUBIN. Built on [barehands](https://github.com/jaredrhod/barehands) by Jared Rhodenizer (AGPL-3.0).

Live: https://barehands.netlify.app (Chrome, click **Wake Nimbus**, allow camera and microphone).

NIMBUS turns the barehands board into a study assistant for PGDM students: PGDM notes,
framework images, timer, stopwatch and calculator you control with your hands or voice, plus a
morning briefing ("Hey Nimbus, all systems online") with your routine, calendar and day plan.

## Folder

| Path | What it is |
|---|---|
| `build_site.py` | Builds the static site into `site/` from the repo's `stage.html` (patches it at build time; `stage.html` itself is not changed). Needs Python 3 + Pillow. |
| `ui/nimbus.js`, `ui/nimbus.css` | The NIMBUS layer: wake screen, HUD, sound set, voice, briefing, routine / calendar / plan, quiz, calibration. |
| `ui/pinch.js` | Pinch engine: 3D fingertip gap, learns your touch, one click per pinch, One Euro filtered cursor. |
| `ui/pinch_test.js`, `ui/pinch_rates.js` | Simulated-hand tests for the pinch engine. |
| `site/` | The built site, as deployed to Netlify. |
| `make_pdf.py`, `NIMBUS_PGDM_Project_Details.pdf` | Project details PDF for students (needs reportlab). |

## Build, test, deploy

```bash
python3 nimbus/build_site.py
node nimbus/ui/pinch_test.js nimbus/ui/pinch.js
cd nimbus/site && npx netlify-cli deploy --prod --no-build --dir .
```
