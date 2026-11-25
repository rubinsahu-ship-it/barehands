# NIMBUS: PGDM Intelligence Interface

Made by RUBIN. Built on [barehands](https://github.com/jaredrhod/barehands) by Jared Rhodenizer (AGPL-3.0).

Live: https://barehands.netlify.app (Chrome, click **Wake Nimbus**, allow camera and microphone).

NIMBUS turns the barehands board into a study assistant for PGDM students: PGDM notes,
framework images, timer and stopwatch you control with your hands or typed commands, plus a
morning briefing ("Hey Nimbus, all systems online") with your routine, calendar and day plan.

## Folder

| Path | What it is |
|---|---|
| `build_site.py` | Builds the static site into `site/` from the repo's `stage.html` (patches it at build time; `stage.html` itself is not changed). Needs Python 3 + Pillow. |
| `ui/nimbus.js`, `ui/nimbus.css` | The NIMBUS layer (design, commands and cards only; hand tracking, pinch and gestures are the original barehands code, unchanged): wake screen, HUD, sound set, typed commands (Enter), NIMBUS Memory uploads (IndexedDB), briefing, routine / calendar / plan, quiz. |
| `site/` | The built site, as deployed to Netlify. |
| `make_pdf.py`, `NIMBUS_PGDM_Project_Details.pdf` | Project details PDF for students (needs reportlab). |

## Build, test, deploy

```bash
python3 nimbus/build_site.py
cd nimbus/site && npx netlify-cli deploy --prod --no-build --dir .
```
