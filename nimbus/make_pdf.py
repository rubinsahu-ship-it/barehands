from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

OUT = "NIMBUS_PGDM_Project_Details.pdf"
TEAL, DARK, LIGHT = colors.HexColor("#5b4fd6"), colors.HexColor("#14142b"), colors.HexColor("#efedff")

H1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=DARK, spaceAfter=4)
H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13.5, leading=17, textColor=TEAL, spaceBefore=12, spaceAfter=5)
B = ParagraphStyle("b", fontName="Helvetica", fontSize=10, leading=14.2, textColor=DARK, spaceAfter=3)
SM = ParagraphStyle("sm", parent=B, fontSize=9, leading=12, textColor=colors.HexColor("#444444"))
BUL = ParagraphStyle("bul", parent=B, leftIndent=12, bulletIndent=0)
CELL = ParagraphStyle("cell", parent=B, fontSize=9.2, leading=12.5, spaceAfter=0)
CELLB = ParagraphStyle("cellb", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white)

def bullets(items):
    return [Paragraph(t, BUL, bulletText="•") for t in items]

def table(rows, widths, header=True):
    data = []
    for i, r in enumerate(rows):
        data.append([Paragraph(c, CELLB if (header and i == 0) else CELL) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8d4cf")),
          ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
          ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), TEAL)]
        st += [("BACKGROUND", (0, i), (-1, i), LIGHT) for i in range(2, len(rows), 2)]
    t.setStyle(TableStyle(st))
    return t

def footer(c, d):
    c.saveState()
    c.setFont("Helvetica", 8.5)
    c.setFillColor(colors.HexColor("#666666"))
    c.drawString(18 * mm, 10 * mm, "NIMBUS  |  PGDM Intelligence Interface  |  Project details for students")
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {d.page}")
    c.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                        title="NIMBUS PGDM Intelligence Interface - Project Details", author="RUBIN")
W = A4[0] - 36 * mm
s = []

s += [Paragraph("NIMBUS - PGDM Intelligence Interface", H1),
      Paragraph("A hands-free study assistant for PGDM students: control notes, framework images and study tools with your bare hands "
                "through a webcam, or by typing a command. Made by <b>RUBIN</b>.", B),
      Paragraph("Live app: <b>barehands.netlify.app</b> &nbsp;|&nbsp; Use Chrome, click WAKE NIMBUS, allow the camera", SM)]

s.append(Paragraph("1. Project name", H2))
s.append(Paragraph("<b>NIMBUS</b> (PGDM Intelligence Interface): a webcam-based assistant where notes, framework images, a timer, "
                   "a stopwatch and your day plan float on screen as glass cards. You pinch, throw and stretch them with your hands, "
                   "or type a command. No headset, controllers or gloves. Made by RUBIN for PGDM students.", B))

s.append(Paragraph("2. Benefits", H2))
s += bullets([
    "<b>Learn by handling ideas:</b> pull SWOT, Porter's Five Forces, BCG or Ansoff onto the board and arrange them side by side.",
    "<b>Ready-made PGDM content:</b> the exam calendar and weekly timetable, study notes and framework images (SWOT, BCG and more by typing).",
    "<b>Typed commands:</b> press Enter and type \"show SWOT\", \"explain BCG matrix\", \"compare SWOT and Porter\" or \"quiz me\"; the answer appears on screen.",
    "<b>NIMBUS Memory:</b> upload images, PDFs and notes from the Memory button (top right) or drop them anywhere. They open as cards from the ring's Memory circle, and stay saved on that laptop's browser.",
    "<b>Study tools:</b> a timer for presentations and group discussions and a stopwatch with laps (also typed: \"start a 5 minute timer\").",
    "<b>Morning briefing:</b> type \"all systems online\" and NIMBUS lays out your routine, today's calendar and a planned day, which you tick off by hand.",
    "<b>Always works:</b> if there is no camera or mic, the mouse and typed commands (press Enter) do everything.",
    "<b>Free and online:</b> runs in Chrome from one link, with no sign-up or API keys.",
])

s.append(Paragraph("3. How it works", H2))
s.append(table([
    ["Step", "What happens"],
    ["1. Wake", "A wake screen with the NIMBUS halo and a sound swell. Clicking WAKE NIMBUS starts the camera and hand tracking."],
    ["2. Camera", "The browser asks for webcam access. Video stays on your device; it is not uploaded."],
    ["3. Hand tracking", "Google MediaPipe finds 21 points on each hand in every frame, right in the browser."],
    ["4. Gestures", "Pinch (index and thumb, other fingers up) to grab, move to drag, "
                    "spread two hands to stretch, flick to throw. A quick pinch on the ring, a menu row or a card key presses it."],
    ["5. The ring and menu", "Tap the NIMBUS ring and three orbs bloom: <b>PGDM Notes</b>, <b>Frameworks</b> and <b>Tools</b>. Only one menu pane is open at a time."],
    ["6. Cards", "Pick a row and it opens as a glass card in a free spot. Cards you place stay put until you close them."],
    ["7. Commands and Memory", "Press Enter and type a command such as \"show SWOT\" or \"start a 5 minute timer\"; the reply appears on screen. "
                               "Files you upload to Memory are stored in the browser (IndexedDB) and open as glass cards."],
    ["8. Rendering", "three.js and CSS draw the glass cards, the HUD and effects over the live camera picture."],
], [32 * mm, W - 32 * mm]))
s.append(Spacer(1, 4))
s.append(Paragraph("<b>Where the content comes from.</b> Notes are plain markdown files in folders. Images are PNG files in a media folder. "
                   "A build script reads those folders and writes small JSON files (a folder list for each orb), which the page loads. "
                   "That is why the hosted version needs no server.", B))

s.append(Paragraph("4. Technology used", H2))
s.append(table([
    ["Tool / service", "What it does in this project"],
    ["HTML, CSS, JavaScript", "The whole board is one web page: layout, glass look, gestures, cards, the HUD and the tools."],
    ["IndexedDB", "Browser storage for NIMBUS Memory: uploads stay on the device, survive reloads and work offline."],
    ["Web Audio API", "The NIMBUS sound set (wake swell, glass clicks, bells, timer chime) is synthesised live in the browser; no audio files."],
    ["Google MediaPipe", "Hand tracking from the webcam (21 points per hand, in the image and in 3D), loaded from a CDN when the page opens."],
    ["three.js", "3D and glass rendering for cards, holograms and effects."],
    ["Python (standard library)", "A small local server (server.py) for running the board on your own computer."],
    ["Python + Pillow", "Generates the framework images (SWOT, Porter, BCG, Ansoff, 4Ps and more) and builds the static site."],
    ["Markdown", "Format for every study note, so notes are easy to write and edit."],
    ["Netlify", "Hosts the live app as a static site on a free URL; deployed with the Netlify command-line tool."],
    ["GitHub", "Code repository for the project."],
    ["Claude Code (Anthropic)", "AI coding assistant used to set up, adapt, brand and deploy the project."],
], [48 * mm, W - 48 * mm]))
s.append(Spacer(1, 6))
s.append(table([
    ["Item", "Details"],
    ["Code repository", "github.com/rubinsahu-ship-it/barehands"],
    ["Licence", "The hand-tracking board is open source (AGPL-3.0). Keep the LICENSE file if you reuse the code."],
    ["Live link", "https://barehands.netlify.app"],
    ["API keys", "None. Hand tracking, memory and hosting all run without API keys, accounts or paid services."],
    ["Run it on your computer", "Clone the repo, run <b>python3 server.py</b>, then open http://127.0.0.1:8794/stage.html in Chrome."],
], [38 * mm, W - 38 * mm]))

s.append(Paragraph("5. Time taken", H2))
s.append(Paragraph("About <b>4 days</b> of build time (21 to 24 November 2026): setting up the open-source hand-tracking board, hosting it on Netlify, "
                   "branding it as NIMBUS, writing the PGDM notes, generating the framework images, adding the boot screen, HUD, typed commands, Memory uploads, "
                   "quiz, timer, stopwatch, morning briefing, and testing and fixing glitches. Hand tracking runs on the open-source board; "
                   "everything NIMBUS adds was built on top of it.", B))
s.append(Paragraph("<i>Edit this to match your own timeline if you rebuild it.</i>", SM))

s.append(Paragraph("6. Write your own presentation script", H2))
s.append(Paragraph("Use the details above to build your own script. Do not copy anyone else's; use your own words and your own demo. "
                   "Fit it to your time slot using the template below.", B))
s.append(table([
    ["Time (adjust)", "Section", "Ideas to cover"],
    ["0:00 - 0:45", "Introduction", "Who you are, the problem (PGDM study is passive and scattered), and your one-line pitch. Click WAKE NIMBUS for the boot moment."],
    ["0:45 - 2:15", "Live demo: hands", "Tap the ring, open Frameworks, pull SWOT and BCG out and arrange them. Throw one, stretch one with two hands."],
    ["2:15 - 3:30", "Live demo: commands, tools, Memory", "Type \"all systems online\" and \"start a 5 minute timer\". Upload a file to Memory and pull it up by hand. Show how it helps in GDs and exam prep."],
    ["3:30 - 4:30", "How it works", "Camera, MediaPipe hand tracking, browser storage for Memory, three.js, hosted on Netlify. Keep it to three sentences."],
    ["4:30 - 5:00", "Close", "The benefit in one line, the live link, thanks."],
], [28 * mm, 38 * mm, W - 66 * mm]))
s.append(Spacer(1, 6))
s.append(Paragraph("<b>Before you present:</b>", B))
s += bullets([
    "Open the live link in Chrome ahead of time, click WAKE NIMBUS, and allow the camera. Good lighting and a plain background help the tracking.",
    "Upload the files you want to show to Memory before you present, on the laptop you'll present from.",
    "Practise each gesture once so the demo looks smooth.",
    "Have a backup: keep screenshots or a short screen recording in case the camera or internet fails.",
    "Rehearse with a timer and cut anything that runs over your slot.",
])

doc.build(s, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
