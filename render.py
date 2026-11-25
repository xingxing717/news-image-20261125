#!/usr/bin/env python3
"""Draw the 25 November 2026 world-news front page (1024x1024 PNG).

Pure Pillow vector drawing. Deterministic: no clock, no randomness, no
network. Run twice -> byte-identical output.
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (18, 38, 66)
RED = (178, 38, 30)
BLUE = (29, 78, 137)
GOLD = (176, 132, 24)
GREY = (110, 110, 104)
LIGHT = (233, 228, 216)
WHITE = (255, 255, 255)
SEA = (16, 52, 86)
SKY = (8, 12, 30)

FD = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FDB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FDB if bold else FD, size)


def wrap(d, text, f, max_w):
    """Greedy word wrap returning a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text(d, xy, s, f, fill=INK):
    d.text(xy, s, font=f, fill=fill)


# ---------------------------------------------------------------- data
HEADLINES = [
    {
        "kicker": "TOP STORY  |  STRAIT OF HORMUZ",
        "title": "Two tankers hit mines\nand catch fire",
        "deck": "Iran says an LNG carrier and an oil tanker struck naval mines in the Strait of Hormuz and caught fire. Tehran says the ships used a route it had not authorised. [CL]",
        "art": "hormuz",
    },
    {
        "kicker": "SPACE  |  JIUQUAN, CHINA",
        "title": "Pakistan reaches orbit\naboard Shenzhou-24",
        "deck": "Shenzhou-24 docks at Tiangong 3.5 hours after launch. Muhammad Zeeshan Ali is the first Pakistani in orbit and the first foreigner aboard China's station. [C]",
        "art": "space",
    },
    {
        "kicker": "TRADE  |  WASHINGTON",
        "title": "US proposes tariffs\non 14 economies",
        "deck": "The US Trade Representative proposes new tariffs on 14 economies, including China, the EU and India, after a probe into excess industrial capacity. [C]",
        "art": "tariffs",
    },
]

# briefs: (region, [(text, tag)]) -- numbered 01..45 in order
REGIONS_LEFT = [
    ("MIDDLE EAST", [
        ("Houthis say they hit Ras Tanura refinery; Saudis say drones downed", "CL"),
        ("Israeli strike kills Hamas security chief in Gaza City", "C"),
        ("Knesset gives first nod to Oct 7 state inquiry", "C"),
        ("Reports: US weighs strikes on Iranian leaders", "R"),
        ("Libya vows reply after drone raid kills 2 officers", "C"),
        ("Iran flogs singer Parastoo Ahmadi 74 times", "C"),
    ]),
    ("EUROPE", [
        ("Poland plans no-fly zone on Ukraine border", "C"),
        ("Merz: Russia wants more than Ukraine", "C"),
        ("Spain heads to snap vote on Sunday", "C"),
        ("EU unveils EUR 50bn tech fund", "C"),
        ("UK energy cap to rise 26% in January", "C"),
        ("Poundland collapses; 11,000+ jobs at risk", "C"),
        ("Leak: at least 490,334 Russian soldiers dead", "R"),
    ]),
    ("NORTH AMERICA", [
        ("Huawei convicted of bank fraud, trade-secret theft", "C"),
        ("Tech stocks tumble; S&P -2.2%, Nasdaq down ~3%", "C"),
        ("Nvidia slides as Congress probes Huang return", "C"),
        ("US growth 4.3%; inflation 3.8% in October", "C"),
        ("Abrego Garcia leaves US for Spain", "C"),
        ("Army blows up 5 tons of lead azide in Iowa", "C"),
        ("CIA and spy chief's office breached", "R"),
    ]),
]

REGIONS_RIGHT = [
    ("ASIA-PACIFIC", [
        ("China investigates Shanghai chief Chen Jining", "C"),
        ("Solomons-Australia sign treaty barring foreign bases", "C"),
        ("Bangladesh garment wage up 36% after protests", "C"),
        ("N. Korea expels Swiss diplomat, shuts office", "C"),
        ("Hanoi restaurant gas blast kills 7", "C"),
        ("Japan unveils rover to hunt moon water", "C"),
    ]),
    ("AFRICA", [
        ("Sudan drone strikes kill 19 civilians", "C"),
        ("Ramaphosa wins court battle on Phala Phala", "C"),
        ("Nollywood star Pete Edochie dies at 79", "C"),
        ("Morocco to challenge ruling restoring Senegal as AFCON champions", "C"),
        ("Ebola in E. Congo grinds on; families cannot trace bodies", "C"),
        ("DR Congo plane missing; rebels claim shoot-down", "R"),
    ]),
    ("LATIN AMERICA", [
        ("Cartagena siege ends; all hostages freed", "C"),
        ("Argentina slips into technical recession", "C"),
        ("Venezuela puts public debt at $237.5bn", "C"),
        ("WHO: Cuban life expectancy fell to 74.4", "C"),
    ]),
    ("SCIENCE & CULTURE", [
        ("South Pole Telescope maps distant matter", "C"),
        ("Social dolphins live longer, Shark Bay study finds", "C"),
        ("Blight-resistant American chestnut created", "C"),
        ("Medieval armour found in 1495 shipwreck", "C"),
        ("Sooryavanshi, 15, smashes 204 off 53 balls", "C"),
        ("Real Madrid 5-1 PSV; Arsenal 1-1 Dortmund", "C"),
    ]),
]

TIMELINE = [
    ("00:18 UTC", "Shenzhou-24 launches"),
    ("03:56 UTC", "Shenzhou-24 docks"),
    ("09:42 GMT", "Ramaphosa wins case"),
    ("DAY", "Hormuz mines reported"),
    ("DAY", "US tariffs proposed"),
    ("CLOSE", "S&P -2.2%"),
]

NUMBERS = [
    ("2", "tankers hit by mines in Hormuz"),
    ("490,334", "Russian war dead in leaked data"),
    ("-2.2%", "S&P 500 on AI and tariff fears"),
    ("EUR 50bn", "EU tech fund unveiled"),
    ("17,000 taka", "new Bangladesh garment wage"),
    ("204 off 53", "Sooryavanshi, 15, List A record"),
]

DATECHECK = (
    "DATE CHECK - left out, not 25 November: Miss Universe crowned 24 Nov (San Juan)  |  "
    "Shuri Castle hall reopened 23 Nov  |  COP31 talks collapsed Sun 22 Nov  |  Dow's first close "
    "above 50,000 was Tue 24 Nov  |  Kenya-DR Congo restored ties 24 Nov  |  London Museum opens "
    "Sat 28 Nov - still to come.  Also: Iran later claimed four tankers hit; the IRGC's first count "
    "was two - we print two."
)

# simplified continent outlines (lon, lat), schematic only
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80), (-75, 73),
     (-65, 60), (-55, 52), (-60, 47), (-70, 44), (-75, 38), (-80, 32), (-81, 26),
     (-90, 21), (-97, 16), (-94, 15), (-105, 20), (-110, 24), (-117, 33), (-125, 40),
     (-124, 48), (-135, 58), (-155, 60), (-165, 60)],
    [(-80, 9), (-72, 12), (-62, 10), (-52, 5), (-50, 0), (-44, -3), (-35, -8),
     (-40, -20), (-48, -28), (-58, -35), (-65, -41), (-70, -50), (-73, -54),
     (-70, -30), (-72, -18), (-77, -12), (-81, -5), (-80, 0)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 11), (48, 2), (40, -10), (35, -18), (32, -26), (28, -33),
     (20, -35), (15, -27), (12, -18), (9, -1), (9, 4), (-8, 5), (-13, 8)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (32, 70),
     (40, 68), (45, 66), (40, 60), (35, 55), (30, 50), (28, 45), (23, 40),
     (19, 42), (12, 44), (8, 44), (3, 43), (-2, 37), (-6, 36)],
    [(30, 62), (40, 68), (60, 69), (75, 73), (90, 75), (110, 76), (130, 72),
     (160, 70), (178, 66), (170, 60), (162, 56), (158, 52), (142, 50), (140, 40),
     (135, 35), (130, 33), (127, 35), (122, 38), (120, 32), (115, 23), (109, 18),
     (105, 10), (100, 8), (98, 15), (95, 16), (90, 22), (86, 20), (80, 13),
     (76, 10), (72, 20), (66, 25), (60, 25), (55, 26), (50, 29), (48, 30),
     (44, 29), (40, 31), (36, 36), (30, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (132, -32),
     (136, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -23), (146, -19), (142, -11), (137, -12), (135, -15), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20)],
]
# (lon, lat) of stories marked on the map
MAP_DOTS = [
    (57, 26), (35, 31), (30, 50), (21, 52), (-4, 40), (13, 52),
    (100, 40), (121, 31), (90, 24), (160, -9), (28, -26), (15, -4),
    (-75, 10), (-58, -35), (-77, 39), (127, 39), (106, 21), (149, -35),
]
MAP_LABELS = [
    ("N. AMERICA", -100, 55), ("S. AMERICA", -60, -20), ("EUROPE", 15, 62),
    ("AFRICA", 18, 5), ("ASIA", 100, 62), ("OCEANIA", 140, -30),
]


def point_in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


# ---------------------------------------------------------------- art
def art_hormuz(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=SEA)
    d.ellipse([x0 + w - 52, y0 + 8, x0 + w - 22, y0 + 38], fill=(232, 190, 90))
    # sea lines
    for yy in (y0 + h - 26, y0 + h - 14):
        for xx in range(x0 + 6, x0 + w - 10, 26):
            d.line([xx, yy, xx + 14, yy], fill=(90, 140, 190), width=2)
    # tanker 1
    d.polygon([(x0 + 12, y0 + h - 34), (x0 + 130, y0 + h - 34),
               (x0 + 122, y0 + h - 18), (x0 + 20, y0 + h - 18)], fill=(40, 40, 44))
    d.rectangle([x0 + 96, y0 + h - 52, x0 + 122, y0 + h - 34], fill=(120, 30, 26))
    # tanker 2 (far)
    d.polygon([(x0 + 170, y0 + h - 30), (x0 + 300, y0 + h - 30),
               (x0 + 292, y0 + h - 16), (x0 + 178, y0 + h - 16)], fill=(52, 52, 56))
    # flames
    for fx, fh in ((52, 30), (72, 40), (92, 28), (228, 34), (252, 26)):
        d.polygon([(x0 + fx - 12, y0 + h - 34), (x0 + fx, y0 + h - 34 - fh),
                   (x0 + fx + 12, y0 + h - 34)], fill=(240, 120, 30))
        d.polygon([(x0 + fx - 6, y0 + h - 34), (x0 + fx, y0 + h - 34 - fh + 12),
                   (x0 + fx + 6, y0 + h - 34)], fill=(250, 200, 60))
    # smoke
    for sx, sy, sr in ((60, 22, 10), (80, 14, 12), (240, 18, 10), (258, 10, 11)):
        d.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr, y0 + sy + sr],
                  fill=(70, 70, 74))


def art_space(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=SKY)
    stars = [(18, 12), (52, 30), (90, 10), (140, 22), (180, 8), (220, 26),
             (260, 12), (300, 30), (36, 52), (120, 48), (200, 52), (280, 48),
             (70, 62), (160, 64), (240, 62)]
    for sx, sy in stars:
        d.ellipse([x0 + sx - 1, y0 + sy - 1, x0 + sx + 1, y0 + sy + 1], fill=WHITE)
    # earth arc, clipped inside the art box: shallow arc, top edge bulging up
    import math as _math
    _pts = []
    for _i in range(33):
        _t = _i / 32
        _pts.append((x0 + _t * w, y0 + h - 4 - 18 * _math.sin(_math.pi * _t)))
    _pts += [(x0 + w, y0 + h), (x0, y0 + h)]
    d.polygon(_pts, fill=(36, 96, 168))
    # station: core + panels
    cx, cy = x0 + w // 2, y0 + 34
    d.rectangle([cx - 52, cy - 5, cx + 52, cy + 5], fill=(200, 200, 205))
    d.rectangle([cx - 118, cy - 9, cx - 56, cy + 9], fill=(40, 90, 170))
    d.rectangle([cx + 56, cy - 9, cx + 118, cy + 9], fill=(40, 90, 170))
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(230, 230, 235))
    # rocket below station
    rx, ry = x0 + 52, y0 + 52
    d.polygon([(rx, ry - 16), (rx - 7, ry + 2), (rx + 7, ry + 2)], fill=(235, 235, 238))
    d.rectangle([rx - 7, ry + 2, rx + 7, ry + 16], fill=(235, 235, 238))
    d.polygon([(rx - 7, ry + 16), (rx - 13, ry + 24), (rx - 7, ry + 18)], fill=(178, 38, 30))
    d.polygon([(rx + 7, ry + 16), (rx + 13, ry + 24), (rx + 7, ry + 18)], fill=(178, 38, 30))
    d.polygon([(rx - 4, ry + 16), (rx, ry + 30), (rx + 4, ry + 16)], fill=(250, 180, 60))


def art_tariffs(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(238, 232, 218))
    d.line([x0 + 16, y0 + h - 22, x0 + w - 12, y0 + h - 22], fill=INK, width=2)
    bars = [("IND", 25, RED), ("CHN", 20, BLUE), ("EU", 15, GOLD)]
    bw, gap = 56, 30
    x = x0 + 34
    for label, pct, col in bars:
        bh = int(pct * 1.4)
        top = y0 + h - 22 - bh
        d.rectangle([x, top, x + bw, y0 + h - 22], fill=col)
        text(d, (x + 6, top + 4), f"{pct}%", font(11, True), fill=WHITE)
        text(d, (x + 8, y0 + h - 18), label, font(10, True), fill=INK)
        x += bw + gap
    # down arrow for markets, top right, clear of the bars and the kicker
    d.line([x0 + w - 62, y0 + 18, x0 + w - 30, y0 + 42], fill=RED, width=3)
    d.polygon([(x0 + w - 38, y0 + 42), (x0 + w - 24, y0 + 42), (x0 + w - 30, y0 + 52)],
              fill=RED)


ART = {"hormuz": art_hormuz, "space": art_space, "tariffs": art_tariffs}


# ---------------------------------------------------------------- page
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.rectangle([0, 0, W, 56], fill=NAVY)
    text(d, (16, 10), "THE WORLD IN ONE DAY", font(28, True), fill=WHITE)
    text(d, (16, 40), "WEDNESDAY 25 NOVEMBER 2026  |  45 verified stories  |  7 regions",
         font(11, True), fill=(200, 210, 225))
    text(d, (W - 16 - d.textlength("ALL DATED 25 NOV 2026", font=font(11, True)), 40),
         "ALL DATED 25 NOV 2026", font(11, True), (240, 200, 90))

    # ---- UTC timeline
    y = 56
    d.rectangle([0, y, W, y + 32], fill=LIGHT)
    d.line([16, y + 20, W - 16, y + 20], fill=GREY, width=1)
    n = len(TIMELINE)
    for i, (t, label) in enumerate(TIMELINE):
        cx = 40 + i * (W - 80) // (n - 1)
        d.ellipse([cx - 4, y + 16, cx + 4, y + 24], fill=RED)
        tw = d.textlength(t, font=font(9, True))
        text(d, (cx - tw / 2, y + 2), t, font(9, True), fill=NAVY)
        lw = d.textlength(label, font=font(9))
        text(d, (max(8, min(W - 8 - lw, cx - lw / 2)), y + 22), label, font(9))

    # ---- headlines
    hy, hh = 88, 162
    pw = (W - 32 - 2 * 12) // 3
    for i, hl in enumerate(HEADLINES):
        x0 = 16 + i * (pw + 12)
        d.rectangle([x0, hy, x0 + pw, hy + hh], outline=(180, 175, 162), width=1)
        d.rectangle([x0, hy, x0 + pw, hy + 22], fill=NAVY)
        text(d, (x0 + 8, hy + 5), hl["kicker"], font(10, True), fill=WHITE)
        ART[hl["art"]](d, x0 + 1, hy + 23, pw - 2, 62)
        ty = hy + 89
        for line in hl["title"].split("\n"):
            text(d, (x0 + 8, ty), line, font(15, True))
            ty += 18
        for line in wrap(d, hl["deck"], font(10), pw - 16):
            text(d, (x0 + 8, ty), line, font(10), fill=(60, 60, 58))
            ty += 13

    # ---- map + numbers row
    my, mh = 258, 134
    # map panel
    mx0, mw = 16, 300
    d.rectangle([mx0, my, mx0 + mw, my + mh], outline=(180, 175, 162), width=1)
    text(d, (mx0 + 8, my + 4), "WHERE IT HAPPENED", font(10, True), fill=NAVY)
    d.text((mx0 + 8, my + mh - 13), "Schematic map, not to scale. Red dots: story sites.",
           font=font(8), fill=GREY)
    map_x0, map_y0, map_w, map_h = mx0 + 8, my + 18, mw - 16, mh - 34
    for gy in range(map_y0, map_y0 + map_h, 4):
        for gx in range(map_x0, map_x0 + map_w, 4):
            lon = -180 + (gx - map_x0) / map_w * 360
            lat = 84 - (gy - map_y0) / map_h * 168
            if any(point_in_poly(lon, lat, c) for c in CONTINENTS):
                d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=(90, 100, 110))
    for lon, lat in MAP_DOTS:
        px = map_x0 + (lon + 180) / 360 * map_w
        py = map_y0 + (84 - lat) / 168 * map_h
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED, outline=WHITE)
    for label, lon, lat in MAP_LABELS:
        px = map_x0 + (lon + 180) / 360 * map_w
        py = map_y0 + (84 - lat) / 168 * map_h
        text(d, (px - 22, py - 12), label, font(7, True), fill=NAVY)

    # numbers panel
    nx0, nw = 328, W - 16 - 328
    d.rectangle([nx0, my, nx0 + nw, my + mh], outline=(180, 175, 162), width=1)
    text(d, (nx0 + 10, my + 4), "THE DAY IN NUMBERS", font(10, True), fill=NAVY)
    cw = (nw - 20) // 3
    for i, (big, small) in enumerate(NUMBERS):
        cx = nx0 + 10 + (i % 3) * cw
        cy = my + 24 + (i // 3) * 52
        text(d, (cx, cy), big, font(17, True), fill=RED)
        for j, line in enumerate(wrap(d, small, font(10), cw - 12)):
            text(d, (cx, cy + 20 + j * 12), line, font(10), fill=(60, 60, 58))

    # ---- region briefs
    by = 400
    num = 0

    def region_block(d, x0, w, y, title, items):
        nonlocal num
        text(d, (x0, y), title, font(11, True), fill=NAVY)
        d.line([x0, y + 15, x0 + w, y + 15], fill=NAVY, width=1)
        y += 21
        f_item, f_tag = font(11), font(9, True)
        for txt, tag in items:
            num += 1
            prefix = f"{num:02d}. "
            pw_ = d.textlength(prefix, font=f_item)
            avail = w - pw_ - 24
            lines = wrap(d, txt, f_item, avail)
            for j, line in enumerate(lines):
                if j == 0:
                    text(d, (x0, y), prefix, f_item, fill=RED)
                    text(d, (x0 + pw_, y), line, f_item)
                else:
                    text(d, (x0 + pw_, y), line, f_item)
                y += 13
            tw_ = d.textlength(tag, font=f_tag)
            d.rectangle([x0 + w - tw_ - 6, y - 13, x0 + w, y - 1],
                        outline=GREY, width=1)
            text(d, (x0 + w - tw_ - 3, y - 13), tag, f_tag, fill=GREY)
            y += 4
        return y

    y = by
    for title, items in REGIONS_LEFT:
        y = region_block(d, 16, 490, y, title, items)
        y += 6
    y = by
    for title, items in REGIONS_RIGHT:
        y = region_block(d, 518, 490, y, title, items)
        y += 6

    # ---- DATE CHECK
    dy = 922
    d.rectangle([16, dy, W - 16, dy + 62], outline=RED, width=2)
    d.rectangle([16, dy, W - 16, dy + 18], fill=RED)
    text(d, (24, dy + 3), "DATE CHECK", font(11, True), fill=WHITE)
    ty = dy + 22
    for line in wrap(d, DATECHECK, font(10), W - 48):
        text(d, (24, ty), line, font(10))
        ty += 13

    # ---- footer
    fy = 990
    text(d, (16, fy),
         "Sources: Reuters  |  AP  |  BBC  |  NYT  |  Al Jazeera  |  Xinhua  |  The Guardian",
         font(10), fill=GREY)
    text(d, (16, fy + 14),
         "C = confirmed   R = reported   CL = claim   |   Every story happened or was first "
         "reported on Wednesday 25 November 2026.  Image drawn in code; no photo used.",
         font(10), fill=GREY)

    img.save(OUT, format="PNG")
    return num


if __name__ == "__main__":
    n = main()
    data = open(OUT, "rb").read()
    print("stories_in_briefs:", n)
    print("bytes:", len(data))
    print("sha256:", hashlib.sha256(data).hexdigest())
