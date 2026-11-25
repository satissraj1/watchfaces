from wff import *

FACES = {}


def face(fn):
    FACES[fn.__name__] = fn
    return fn


TH = "theme"  # theme color config id; index meaning documented per face
DAYDATE = tpl("%s %s", "[DAY_OF_WEEK_S]", "[DAY]")


# =====================================================================  1. ORBIT
@face
def orbit():
    F = Face("orbit", "Orbit")
    F.font("roboto_light"); F.font("roboto_medium")
    # theme: 0 dial, 1 rings, 2 ticks, 3 text, 4 minute planet
    F.color_cfg(TH, "Dial", [
        ("Dark", ["#FF000000", "#FF262626", "#FFEDEDED", "#FF8A8A8A", "#FFF4F4F4"]),
        ("Light", ["#FFECE9E2", "#FFD0CBC1", "#FF2A2A2A", "#FF7A766E", "#FF1E1E1E"]),
        ("Midnight", ["#FF0F1A2B", "#FF23334B", "#FFE6ECF5", "#FF7F8EA6", "#FFF0F4FA"]),
        ("Clay", ["#FF2B211C", "#FF46372F", "#FFF1E4D6", "#FF9C8676", "#FFF6EBDD"]),
        ("Graphite", ["#FF181818", "#FF2E2E2E", "#FFE0E0E0", "#FF8A8A8A", "#FFFFFFFF"]),
    ])
    F.color_cfg("rim", "Rim", [
        ("Marigold", ["#FFE8A33A"]), ("Mustard", ["#FFD4AE3A"]), ("Teal", ["#FF2F8F8A"]),
        ("Coral", ["#FFE86A4F"]), ("Graphite", ["#FF3E3E3E"]), ("Cream", ["#FFE6DECF"]),
        ("Sky", ["#FF6FA8DC"]), ("Olive", ["#FF7D8A4A"]),
    ])
    # planets: 0 hour, 1 second (minute planet follows the dial theme)
    F.color_cfg("dots", "Planets", [
        ("Classic", ["#FFD7263D", "#FFE8A33A"]),
        ("Citrus", ["#FFFF7A00", "#FF9BE15D"]),
        ("Ocean", ["#FF3FA7D6", "#FF59CD90"]),
        ("Ruby", ["#FFE63946", "#FFA8DADC"]),
        ("Violet", ["#FF8E6CFF", "#FFFFC857"]),
        ("Mono", ["#FF9A9A9A", "#FF6A6A6A"]),
    ])
    F.list_cfg("bezel", "Bezel", ["Full screen", "Thin", "Thick"])
    F.list_cfg("ticks", "Markers", ["Twelve", "Four", "Sixty", "None"])
    F.list_cfg("layout", "Orbits", ["Hours inside", "Hours outside"])
    F.bool_cfg("sec", "Seconds planet", True)
    F.bool_cfg("date", "Date", True)

    rings = [58, 108, 158]

    def dial_for(rin):
        if rin >= 225:  # full-screen dial, no bezel
            return draw(circle(225, C(TH, 0)), radial_fill(225, ["#00000000", "#00000000", "#30000000"], [0, 0.9, 1]),
                        *[circle(r, None, C(TH, 1), 2) for r in rings])
        k = rin / 225
        return draw(circle(225, C("rim")),
                    radial_fill(225, ["#00000000", "#00000000", "#30FFFFFF", "#00FFFFFF", "#38000000"], [0, k - 0.005, k + 0.011, (k + 1) / 2, 1]),
                    circle(rin, C(TH, 0)),
                    radial_fill(rin, ["#00000000", "#00000000", "#38000000"], [0, 0.92, 1]),
                    circle(rin + 1, None, "#30000000", 3),
                    *[circle(r, None, C(TH, 1), 2) for r in rings])
    dial = list_scene("bezel", [dial_for(225), dial_for(214), dial_for(200)])

    def ticks(kind, col):
        if kind == 0:
            return draw(*[radial_line(178, 192, a, col, 4) for a in range(0, 360, 30)])
        if kind == 1:
            return draw(*[radial_line(176, 193, a, col, 5) for a in range(0, 360, 90)])
        if kind == 2:
            return draw(*[radial_line(185 if a % 30 else 177, 192, a, col, 4 if a % 30 == 0 else 1.6) for a in range(0, 360, 6)])
        return ""

    tick_xml = list_scene("ticks", [ticks(i, C(TH, 2)) for i in range(4)])

    date = bool_scene("date", text(175, 192, 100, 20, font("roboto_medium", 14, C(TH, 3), "<Upper>" + tpl("%s", "[DAY_OF_WEEK_S]") + "</Upper>", 0.15))
                      + text(175, 208, 100, 36, font("roboto_light", 30, C(TH, 2), tpl("%s", "[DAY]"))))

    def planets(order):  # order: radii for (hour, minute, second)
        rh, rm, rs = order
        hi = F.img(f"h{rh}", dot_hand(rh, 12)[0]); mi = F.img(f"m{rm}", dot_hand(rm, 15)[0]); si = F.img(f"s{rs}", dot_hand(rs, 9)[0])
        H_ = dot_hand(rh, 12); M_ = dot_hand(rm, 15); S_ = dot_hand(rs, 9)
        hands = [hand("HourHand", hi, H_[0], H_[1], H_[2], tint=C("dots", 0)),
                 hand("MinuteHand", mi, M_[0], M_[1], M_[2], tint=C(TH, 4))]
        sec = clock(hand("SecondHand", si, S_[0], S_[1], S_[2], tint=C("dots", 1), inner=SWEEP))
        return clock(*hands), sec

    lay = []
    for order in [(58, 108, 158), (158, 108, 58)]:
        hm, sec = planets(order)
        lay.append(hm + bool_scene("sec", active(sec)))

    F.add(active(dial, tick_xml, date),
          ambient(draw(*[circle(r, None, "#FF262626", 2) for r in rings]),
                  draw(*[radial_line(178, 192, a, "#FF6A6A6A", 3) for a in range(0, 360, 30)])),
          list_scene("layout", lay))
    return F


def two_clocks(hands_active, hands_ambient):
    return active(clock(*hands_active)) + ambient(clock(*hands_ambient))


def hands_pair(F, prefix, specs, tint_a, tint_b):
    """specs: list of (tag, (img,px,py)). Returns (active_hands, ambient_hands)."""
    a, b = [], []
    for tag, (im, px, py) in specs:
        n = F.img(f"{prefix}_{tag.lower()}", im)
        a.append(hand(tag, n, im, px, py, tint=tint_a))
        b.append(hand(tag, n, im, px, py, tint=tint_b))
    return a, b


ACCENTS = [("Red", ["#FFE53935"]), ("Orange", ["#FFFF6D00"]), ("Blue", ["#FF2979FF"]),
           ("Yellow", ["#FFFFC400"]), ("Green", ["#FF00C853"]), ("Pink", ["#FFFF4081"]),
           ("Violet", ["#FF7C4DFF"]), ("Cyan", ["#FF00B8D4"])]


# =====================================================================  4. TUNER (radio dial: fixed needle, scrolling scale)
@face
def tuner():
    F = Face("tuner", "Tuner")
    F.clock_type = "DIGITAL"
    IN, LT, DP = F.font("inter_text"), F.font("inter_light"), F.font("inter_display_bold")
    # 0 bg, 1 ink, 2 secondary text, 3 tick, 4 ghost digit
    F.color_cfg(TH, "Theme", [
        ("Light", ["#FFEAEAE8", "#FF141414", "#FF5C5C5C", "#FF9C9C9A", "#FFC9C9C7"]),
        ("Dark", ["#FF000000", "#FFF2F2F2", "#FFA6A6A6", "#FF5A5A5A", "#FF303030"]),
        ("Sand", ["#FFEDE6DA", "#FF1F1B16", "#FF6B604E", "#FFA89D8A", "#FFD2C8B6"]),
        ("Navy", ["#FF0C1626", "#FFEAF0FA", "#FF9AA9C2", "#FF4A5A76", "#FF26344C"]),
        ("Olive", ["#FF23271D", "#FFE9ECDD", "#FFABB296", "#FF616851", "#FF3A3F30"]),
    ])
    F.color_cfg("accent", "Needle", ACCENTS)
    F.list_cfg("hours", "Hours", ["12 hour", "24 hour"])
    F.list_cfg("scale", "Dial tracks", ["Seconds", "Minutes"])
    bg, ink, mu, tk, gh = (C(TH, i) for i in range(5))
    acc = C("accent")
    NY = 225          # needle y (fixed)
    ST = 7.0          # px per unit on the scale
    TX0, TX1 = 300, 334  # tick x span
    LO, HI = -32, 92  # rendered unit range (wraps 0..59)

    def scale(expr, col_t, col_l, label_every=10):
        ticks = draw(*[line(TX0, (v - LO) * ST, TX1, (v - LO) * ST, col_t, 1.6 if v % label_every else 2, "BUTT")
                       for v in range(LO, HI + 1, 2)], w=W, h=(HI - LO) * ST + 4)
        labels = "".join(text(342, (v - LO) * ST - 11, 34, 22, font(LT, 15, col_l, f"{v % 60:02d}"), align="START")
                         for v in range(LO, HI + 1) if v % label_every == 0)
        tr = f'<Transform target="y" value="{NY} - (({expr}) - ({LO})) * {ST}"/>'
        return group(ticks, labels, name="scale", x=0, y=0, w=W, h=int((HI - LO) * ST) + 4, extra=tr)

    exprs = ["[SECOND_MILLISECOND]", "[MINUTE] + [SECOND_MILLISECOND] / 60"]
    needle = draw(line(284, NY, TX1 + 1, NY, acc, 3.2, "BUTT"))

    def cond(expr, yes, no):
        return (f'<Condition><Expressions><Expression name="c"><![CDATA[{expr}]]></Expression></Expressions>'
                f'<Compare expression="c">{yes}</Compare><Default>{no}</Default></Condition>')

    # band selector next to the needle (FM | AM  ->  AM | PM)
    def band(on, off_):
        return text(366, NY - 12, 84, 24, font(LT, 15, on[1], on[0]), font(LT, 15, tk, " | "), font(LT, 15, off_[1], off_[0]), align="START")
    ampm = list_scene("hours", [cond("[AMPM_STATE] == 0", band(("AM", ink), ("PM", tk)), band(("AM", tk), ("PM", ink))),
                                text(366, NY - 12, 60, 24, font(LT, 15, mu, "24H"), align="START")])

    # big readout with ghost leading zero, like 098.3
    def readout(hsrc, cink, cghost, cdot):
        y, hgt, sz, ls = NY - 50, 100, 78, None  # negative tracking collides "1." and clips
        mm = font(DP, sz, cdot, ".", ls) + font(DP, sz, cink, tpl("%s", "[MINUTE_Z]"), ls)
        lead = text(50, y, 236, hgt, font(DP, sz, cghost, "0", ls), font(DP, sz, cink, tpl("%s", hsrc), ls), mm, align="START")
        full = text(50, y, 236, hgt, font(DP, sz, cink, tpl("%s", hsrc), ls), mm, align="START")
        return cond(f"{hsrc} < 10", lead, full)
    hsrcs = ["[HOUR_1_12]", "[HOUR_0_23]"]

    top = (text(130, 78, 170, 23, font(LT, 17, ink, tpl("%s", "[DAY_OF_WEEK_F]")), align="START")
           + text(130, 100, 170, 23, font(LT, 17, mu, tpl("%s %s", "[MONTH_F]", "[DAY]")), align="START"))

    def comp(slot, x, provider):
        w, h = 112, 34
        return (f'<ComplicationSlot slotId="{slot}" name="c{slot}" x="{x}" y="276" width="{w}" height="{h}" '
                f'supportedTypes="SHORT_TEXT EMPTY" isCustomizable="TRUE">'
                f'<DefaultProviderPolicy defaultSystemProvider="{provider}" defaultSystemProviderType="SHORT_TEXT"/>'
                f'<BoundingBox x="0" y="0" width="{w}" height="{h}"/>'
                f'<Complication type="SHORT_TEXT">'
                + draw(rrect(1, 4, 52, 26, 13, None, ink, 1.2), circle(2.4, acc, cx=41, cy=17), w=w, h=h)
                + f'<PartImage x="12" y="8" width="20" height="18" tintColor="{ink}"><Image resource="[COMPLICATION.MONOCHROMATIC_IMAGE]"/></PartImage>'
                + text(60, 3, 54, 28, font(LT, 17, ink, tpl("%s", "[COMPLICATION.TEXT]")), align="START")
                + '</Complication><Complication type="EMPTY"></Complication></ComplicationSlot>')

    chev = draw(line(214, 404, 225, 394, ink, 1.8), line(225, 394, 236, 404, ink, 1.8))
    F.add(active(draw(circle(225, bg)),
                 list_scene("scale", [scale(e, tk, mu) for e in exprs]), needle, ampm, top, chev,
                 list_scene("hours", [readout(h, ink, gh, ink) for h in hsrcs])),
          ambient(list_scene("hours", [readout(h, "#FFD0D0D0", "#FF333333", "#FFD0D0D0") for h in hsrcs]),
                  scale(exprs[1], "#FF2E2E2E", "#FF555555"), draw(line(284, NY, TX1 + 1, NY, "#FF8A8A8A", 2.4, "BUTT"))),
          comp(0, 50, "WATCH_BATTERY"), comp(1, 166, "STEP_COUNT"))
    return F


# =====================================================================  5. BAUHAUS (red hands, Braun-ish)
@face
def bauhaus():
    F = Face("bauhaus", "Bauhaus")
    MD = F.font("inter_display_medium")
    F.color_cfg(TH, "Dial", [
        ("White", ["#FFF3F3F1", "#FF1A1A1A", "#FFCFCFCC", "#FFDCDCD9"]),
        ("Dark", ["#FF000000", "#FFEEEEEE", "#FF5A5A5A", "#FF1E1E1E"]),
        ("Cream", ["#FFF1EBDD", "#FF2A2620", "#FFD9D0BE", "#FFE3DAC7"]),
        ("Slate", ["#FF3A4048", "#FFF4F5F7", "#FF555D67", "#FF2E333A"]),
        ("Silver", ["#FFDADCDF", "#FF16181B", "#FFB4B8BE", "#FFF2F3F4"]),
    ])
    F.color_cfg("accent", "Hands", [("Red", ["#FFD62828"]), ("Blue", ["#FF1E56C8"]), ("Orange", ["#FFF05A1A"]),
                                    ("Green", ["#FF1E8A4C"]), ("Ink", ["#FF1A1A1A"]), ("Bone", ["#FFEDEDED"]), ("Yellow", ["#FFF2B705"])])
    F.color_cfg("sc", "Seconds colour", [("Yellow", ["#FFF2C200"]), ("Red", ["#FFD62828"]), ("Ink", ["#FF1A1A1A"]), ("Bone", ["#FFEDEDED"])])
    F.list_cfg("index", "Index", ["Spokes", "Lines", "Numerals", "Minimal"])
    F.bool_cfg("sec", "Second hand", True)
    F.bool_cfg("date", "Date", False)
    bg, ink, ln, rim = (C(TH, i) for i in range(4))
    acc = C("accent")
    dial = draw(circle(225, bg), radial_fill(225, ["#00000000", "#00000000", "#12000000", "#2A000000"], [0, 0.88, 0.96, 1]))
    nums = ""
    for n in range(1, 13):
        x, y = polar(170, n * 30)
        nums += text(x - 28, y - 22, 56, 44, font(MD, 34, ink, str(n)))
    idx = [
        draw(*[radial_line(118, 210, a, ln, 2.2, "BUTT") for a in range(0, 360, 30) if a % 90],
             radial_line(148, 206, 90, ink, 5, "BUTT"), radial_line(148, 206, 270, ink, 5, "BUTT"),
             radial_line(150, 210, 0, ln, 2.2, "BUTT"))
        + text(185, 266, 80, 76, font(MD, 60, ink, "6")),
        draw(*[radial_line(122, 218, a, ink, 4, "BUTT") for a in range(0, 360, 90)]),
        draw(*[radial_line(194 if a % 30 == 0 else 204, 214, a, ink, 3.2 if a % 30 == 0 else 1.4, "BUTT") for a in range(0, 360, 6)]) + nums,
        draw(*[circle(6, ink, cx=polar(200, a)[0], cy=polar(200, a)[1]) for a in range(0, 360, 90)]),
    ]
    date = bool_scene("date", draw(rrect(288, 207, 50, 36, 6, None, ink, 1.6))
                      + text(288, 207, 50, 36, font(MD, 21, ink, tpl("%s", "[DAY]"))))
    h_, m_, s_ = bar_hand(10, 110, tail=16), bar_hand(7, 176, tail=20), bar_hand(2.6, 186, tail=36)
    ha, hb = hands_pair(F, "bh", [("HourHand", h_), ("MinuteHand", m_)], acc, "#FFBDBDBD")
    sn = F.img("bh_sec", s_[0])
    cap = draw(circle(13, bg), circle(12, None, acc, 4))
    sec = bool_scene("sec", clock(hand("SecondHand", sn, *s_, tint=C("sc"), inner=SWEEP)) + draw(circle(3, C("sc"))))
    F.add(active(dial, list_scene("index", idx), date, clock(*ha), cap, sec),
          ambient(draw(*[radial_line(190, 206, a, "#FF4A4A4A", 3, "BUTT") for a in range(0, 360, 90)]),
                  clock(*hb), draw(circle(10, "#FF000000"), circle(9, None, "#FFBDBDBD", 3))))
    return F


# =====================================================================  6. STACK (big stacked digits)
@face
def stack():
    F = Face("stack", "Stack")
    F.clock_type = "DIGITAL"
    fams = ["inter_display_bold", "inter_display_regular", "inter_display_light", "roboto_condensed_light"]
    for fm in fams + ["inter_text"]:
        F.font(fm)
    F.color_cfg(TH, "Theme", [
        ("Dark", ["#FF000000", "#FFF5F5F5", "#FFA3A3A3", "#FF2A2A2A"]),
        ("Light", ["#FFF2F2F0", "#FF111111", "#FF5E5E5E", "#FFD2D2D0"]),
        ("Graphite", ["#FF1C1D20", "#FFE6E7EA", "#FFA3A6AD", "#FF34363B"]),
        ("Ivory", ["#FFEFE8DA", "#FF2B2721", "#FF6E655A", "#FFD6CDBD"]),
        ("Forest", ["#FF0F1F18", "#FFE4EFE8", "#FF93AE9F", "#FF1E3329"]),
    ])
    F.color_cfg("accent", "Accent", ACCENTS)
    F.list_cfg("weight", "Typeface", ["Bold", "Regular", "Light", "Condensed"])
    F.list_cfg("hours", "Hours", ["12 hour", "24 hour"])
    F.list_cfg("tone", "Minutes tone", ["Same", "Dimmed", "Accent"])
    F.bool_cfg("ring", "Seconds ring", True)
    F.bool_cfg("week", "Week strip", True)
    bg, ink, mu, bz = (C(TH, i) for i in range(4))
    acc = C("accent")
    hrs = ["[HOUR_1_12_Z]", "[HOUR_0_23_Z]"]

    def digits(fam, hexpr, hc, mc):
        ls = None  # negative tracking makes the runtime clip the last glyph
        return (text(0, 44, 450, 164, font(fam, 150, hc, tpl("%s", hexpr), ls))
                + text(0, 186, 450, 164, font(fam, 150, mc, tpl("%s", "[MINUTE_Z]"), ls)))
    body = list_scene("weight", [
        list_scene("hours", [list_scene("tone", [digits(fm, h, ink, ink), digits(fm, h, ink, mu), digits(fm, h, ink, acc)]) for h in hrs])
        for fm in fams])
    wk = "SMTWTFS"
    SP = 24
    week = ("".join(text(225 + (i - 3) * SP - 12, 370, 24, 22, font("inter_text", 15, mu, wk[i])) for i in range(7))
            + draw(circle(3.2, acc, cx=5, cy=5), x=225 - 3 * SP - 5, y=394, w=10, h=10,
                   extra=f'<Transform target="x" value="{225 - 3 * SP - 5} + ([DAY_OF_WEEK] - 1) * {SP}"/>'))
    foot = text(115, 344, 220, 24, font("inter_text", 16, mu, "<Upper>" + tpl("%s %s", "[DAY]", "[MONTH_S]") + "</Upper>", 0.12))
    ring = draw(circle(216, None, bz, 6),
                arc(216, 0, 0, acc, 6, cap="BUTT", inner='<Transform target="endAngle" value="[SECOND_MILLISECOND] * 6"/>'))
    F.add(active(draw(circle(225, bg)), bool_scene("ring", ring), bool_scene("week", week), foot, body),
          ambient(list_scene("hours", [digits("inter_display_light", h, "#FFE0E0E0", "#FFA0A0A0") for h in hrs])))
    return F


# =====================================================================  7. MOOD (faces)
def blob_img(seed=0, size=410, r=178):
    im = Image.new("RGBA", (size * SS, size * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = []
    for k in range(720):
        t = 2 * math.pi * k / 720
        rr = r * (1 + 0.035 * math.sin(3 * t + 0.6) + 0.025 * math.cos(2 * t + 1.3) + 0.015 * math.sin(5 * t))
        pts.append(((size / 2 + rr * math.cos(t)) * SS, (size / 2 + rr * math.sin(t)) * SS))
    d.polygon(pts, fill=(255, 255, 255, 255))
    return im.resize((size, size), Image.LANCZOS)


@face
def mood():
    F = Face("mood", "Mood")
    # 0 backdrop, 1 face, 2 features, 3 hands, 4 cheeks
    F.color_cfg(TH, "Character", [
        ("Tangerine", ["#FFF3B13B", "#FFE5793B", "#FF3A2414", "#FFFFFFFF", "#55FF4F6D"]),
        ("Forest", ["#FFF3B13B", "#FF1F6B4A", "#FFF2F7F3", "#FFFFFFFF", "#55FF9AA2"]),
        ("Lagoon", ["#FFF3B13B", "#FF0F6E7A", "#FFF2F7F8", "#FFFFFFFF", "#55FF9AA2"]),
        ("Cloud", ["#FFE7E7E5", "#FFFFFFFF", "#FF2A2A2A", "#FFE04848", "#55FF7A8A"]),
        ("Charcoal", ["#FF000000", "#FF2E3236", "#FFEDEDED", "#FFFF5A4E", "#40FF8A9A"]),
        ("Dusk", ["#FF0E1A24", "#FF6E8FA6", "#FFF3F6F8", "#FFFFFFFF", "#55FFB3C1"]),
        ("Bubblegum", ["#FFFFE3EC", "#FFFF8FB1", "#FF3B1F2B", "#FFFFFFFF", "#66FF4F7F"]),
    ])
    F.list_cfg("shape", "Head", ["Blob", "Round", "Full screen"])
    F.list_cfg("eyes", "Eyes", ["Dots", "Happy", "Glasses", "Wink", "Surprised", "Sleepy"])
    F.bool_cfg("blush", "Blush", True)
    F.bool_cfg("nose", "Seconds nose", True)
    bk, fc, ft, hd, ck = (C(TH, i) for i in range(5))
    bl = F.img("md_blob", blob_img())
    shapes = [f'<PartImage x="20" y="20" width="410" height="410" tintColor="{fc}"><Image resource="{bl}"/></PartImage>',
              draw(circle(190, fc)), draw(circle(225, fc))]
    EX, EY, ER = 172, 172, 278
    e = lambda x, y, r: circle(r, ft, cx=x, cy=y)
    eyes = [
        draw(e(EX, EY, 10), e(ER, EY, 10)),
        draw(arc(15, 105, 255, ft, 5.5, cx=EX, cy=EY - 6), arc(15, 105, 255, ft, 5.5, cx=ER, cy=EY - 6)),
        draw(circle(27, None, ft, 4, cx=EX, cy=EY), circle(27, None, ft, 4, cx=ER, cy=EY),
             arc(14, 300, 420, ft, 4, cx=225, cy=EY + 4), e(EX, EY, 6), e(ER, EY, 6)),
        draw(e(EX, EY, 10), line(ER - 14, EY, ER + 14, EY, ft, 5)),
        draw(circle(13, None, ft, 3.5, cx=EX, cy=EY), circle(13, None, ft, 3.5, cx=ER, cy=EY), e(EX, EY, 4), e(ER, EY, 4)),
        draw(line(EX - 15, EY, EX + 15, EY, ft, 5), line(ER - 15, EY, ER + 15, EY, ft, 5)),
    ]
    blush = bool_scene("blush", draw(circle(20, ck, cx=140, cy=238), circle(20, ck, cx=310, cy=238)))
    OY = 48  # mouth pivot at (225, 273)
    h_, m_ = bar_hand(10, 54), bar_hand(8, 86)
    ha, hb = hands_pair(F, "md", [("HourHand", h_), ("MinuteHand", m_)], hd, "#FFDADADA")
    n_ = dot_hand(16, 5)
    nn = F.img("md_nose", n_[0])
    nose = bool_scene("nose", clock(hand("SecondHand", nn, *n_, tint=ft), y=OY))
    F.add(active(draw(circle(225, bk)), list_scene("shape", shapes), list_scene("eyes", eyes), blush,
                 clock(*ha, y=OY), draw(circle(7, hd, cy=225 + OY)), nose),
          ambient(list_scene("eyes", [o.replace(ft, "#FFBDBDBD") for o in eyes]), clock(*hb, y=OY)))
    return F


# =====================================================================  8. SCRIBBLE (wire loops)
def scribble_img(loops, seed):
    import random
    rnd = random.Random(seed)
    S = 450
    im = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for _ in range(loops):
        # one pen pass: 1.1-1.4 turns that never quite close, radius drifting as the hand moves
        r0, drift = rnd.uniform(184, 206), rnd.uniform(-14, 14)
        cx, cy = 225 + rnd.uniform(-7, 7), 225 + rnd.uniform(-7, 7)
        ph, a1, a2, a3 = rnd.uniform(0, 6.28), rnd.uniform(0.015, 0.04), rnd.uniform(0.01, 0.03), rnd.uniform(0.003, 0.01)
        turns, t0 = rnd.uniform(1.1, 1.4), rnd.uniform(0, 2 * math.pi)
        n = int(360 * turns)
        pts = []
        for k in range(n + 1):
            u = k / n
            t = t0 + 2 * math.pi * turns * u
            rr = (r0 + drift * u) * (1 + a1 * math.sin(2 * t + ph) + a2 * math.cos(3 * t + ph * 2) + a3 * math.sin(7 * t + ph))
            rr = min(rr, 221)
            pts.append(((cx + rr * math.cos(t)) * SS, (cy + rr * math.sin(t)) * SS))
        d.line(pts, fill=(255, 255, 255, rnd.randint(190, 245)), width=int(rnd.uniform(1.2, 2.3) * SS), joint="curve")
    # hand-drawn "12" at the top: thin wire strokes
    def wire(pts, w=2.0):
        d.line([(x * SS, y * SS) for x, y in pts], fill=(255, 255, 255, 255), width=int(w * SS), joint="curve")
    # (no numerals: the time is written below the knot)
    return im.resize((S, S), Image.LANCZOS)


def _pen(d, pts, w):
    d.line([(x * SS, y * SS) for x, y in pts], fill=(255, 255, 255, 255), width=max(1, int(w * SS)), joint="curve")


def scribble_hand(length, tail, spread, strokes, pen, seed):
    """Hand-drawn hand pointing up: pen goes up and back down in loose, overlapping passes. Returns (img, px, py)."""
    import random
    rnd = random.Random(seed)
    pad = int(spread * 1.6 + pen) + 4
    w = 2 * pad; w += w % 2
    h = int(length + tail) + 2 * pad
    im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    py = pad + length
    pts = []
    for s in range(strokes):
        up = s % 2 == 0
        ph, fr = rnd.uniform(0, 6.3), rnd.uniform(2.0, 3.4)
        amp = spread * rnd.uniform(0.7, 1.25)
        for k in range(41):
            t = k / 40 if up else 1 - k / 40
            y = (py + tail * rnd.uniform(0.85, 1.0)) + ((pad + rnd.uniform(0, 2)) - (py + tail)) * t
            x = w / 2 + amp * (1 - 0.55 * t) * math.sin(fr * math.pi * t + ph) + rnd.uniform(-0.4, 0.4)
            pts.append((x, y))
    _pen(d, pts, pen)
    return im.resize((w, h), Image.LANCZOS), w / 2, py


def knot_img(r, loops, seed, pen=1.7):
    """Small scribbled wire knot centred in a square image."""
    import random
    rnd = random.Random(seed)
    S = int(2 * r + 12); S += S % 2
    im = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    for _ in range(loops):
        rr = rnd.uniform(0.55, 1.0) * r
        cx, cy, ph = c + rnd.uniform(-2.5, 2.5), c + rnd.uniform(-2.5, 2.5), rnd.uniform(0, 6.3)
        pts = [(cx + rr * (1 + 0.08 * math.sin(3 * t + ph)) * math.cos(t), cy + rr * (1 + 0.08 * math.cos(2 * t + ph)) * math.sin(t))
               for t in [2 * math.pi * k / 90 * rnd.uniform(0.98, 1.02) for k in range(96)]]
        _pen(d, pts, pen)
    return im.resize((S, S), Image.LANCZOS)


def wobble_line_img(x0, y0, y1, seed, pen=1.6):
    import random
    rnd = random.Random(seed)
    im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(x0 + 1.4 * math.sin(k / 6.0 + 1) + rnd.uniform(-0.3, 0.3), y0 + (y1 - y0) * k / 40) for k in range(41)]
    _pen(d, pts, pen)
    return im.resize((W, H), Image.LANCZOS)


def sketch_orbit(radius, sweep, colors, seed, band=7.0, fade_tail=True, pen=(1.8, 2.8)):
    """Seconds as rounded sketching: a curved pencil trail ending at 12 o'clock (rotated by the runtime),
    several colours scribbling over each other, fading out toward the tail. Full-screen image, pivot = centre."""
    import random
    rnd = random.Random(seed)
    im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for ci, col in enumerate(colors):
        ph1, ph2 = rnd.uniform(0, 6.3), rnd.uniform(0, 6.3)
        curl_r = rnd.uniform(5.0, 6.5)
        curl_w = 2 * math.pi * max(40, sweep / 3.0) * rnd.uniform(0.97, 1.03)  # loop every ~3 degrees
        n, prev = int(max(1400, sweep * 9)), None
        for k in range(n + 1):
            u = k / n                      # 0 = tail, 1 = pencil tip
            ang = math.radians(sweep * u) if not fade_tail else math.radians(-sweep * (1 - u))
            rr = radius + band * 0.3 * math.sin(5 * math.pi * u + ph1) + band * 0.15 * math.sin(13 * math.pi * u + ph2)
            rr += curl_r * math.cos(curl_w * u + ci * 1.7)
            ang += curl_r * math.sin(curl_w * u + ci * 1.7) / radius
            x, y = CX + rr * math.sin(ang), CY - rr * math.cos(ang)
            if prev:
                fade = u ** 1.2 if fade_tail else 1.0
                a = int(rnd.randint(185, 255) * fade)
                if a > 6:
                    d.line([(prev[0] * SS, prev[1] * SS), (x * SS, y * SS)], fill=col[:3] + (a,),
                           width=max(1, int(rnd.uniform(*pen) * (0.6 + 0.4 * fade) * SS)))
            prev = (x, y)
    return im.resize((W, H), Image.LANCZOS), CX, CY


def wander_path(seed, start=(225, 46), n_way=4, r_lo=70, r_max=172, samples=480):
    """Calm closed walk from 12 around the screen and back to 12: few waypoints, ordered clockwise
    with jitter, so the pen drifts in wide gentle curves instead of hairpins. Returns list of points."""
    import random
    rnd = random.Random(seed)
    pts = [start]
    for k in range(n_way):
        a = -math.pi / 2 + (k + 1) * 2 * math.pi / (n_way + 1) + rnd.uniform(-0.35, 0.35)
        r = rnd.uniform(r_lo, r_max)
        pts.append((CX + r * math.cos(a), CY + r * math.sin(a)))
    pts.append(start)
    P = [pts[0]] + pts + [pts[-1]]
    out = []
    per = samples // (len(pts) - 1)
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            x = 0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(start)
    # hand tremor
    return [(x + 1.2 * math.sin(k * 0.21 + seed) , y + 1.2 * math.cos(k * 0.17 + seed * 2)) for k, (x, y) in enumerate(out)]


def wander_seconds(seed, color, pen=3.2, segs=240):
    """`segs` short vector pieces of equal arc length; piece i fades in over its own 60/segs-second slot,
    so the line grows continuously like a pen being drawn."""
    pts = wander_path(seed)
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + math.dist(a, b))
    total, out, j = L[-1], [], 0
    for i in range(segs):
        lo, hi = total * i / segs, total * (i + 1) / segs
        seg = []
        while j < len(pts) - 1 and L[j] <= hi:
            if L[j + 1] >= lo:
                seg.append(pts[j])
            j += 1
        seg.append(pts[min(j, len(pts) - 1)])
        j = max(0, j - 1)
        lines = [line(a[0], a[1], b[0], b[1], color, pen) for a, b in zip(seg, seg[1:])]
        slot = 60.0 / segs
        tr = f'<Transform target="alpha" value="clamp(([SECOND_MILLISECOND] - {i * slot:.3f}) * {255 / slot:.1f}, 0, 255)"/>'
        out.append(f'<PartDraw x="0" y="0" width="450" height="450" alpha="0">{tr}{"".join(lines)}</PartDraw>')
    return "".join(out)


def by_minute(options):
    """Pick option j when [MINUTE] % len(options) == j."""
    k = len(options)
    exprs = "".join(f'<Expression name="m{j}"><![CDATA[([MINUTE] % {k}) == {j}]]></Expression>' for j in range(k - 1))
    comps = "".join(f'<Compare expression="m{j}">{o}</Compare>' for j, o in enumerate(options[:-1]))
    return f'<Condition><Expressions>{exprs}</Expressions>{comps}<Default>{options[-1]}</Default></Condition>'


@face
def scribble():
    F = Face("scribble", "Scribble")
    F.color_cfg(TH, "Theme", [
        ("Paper", ["#FFF4F4F2", "#FF2A2A2A", "#FF8E9095", "#FFC0262D", "#FF2F5FE0"]),
        ("Dark", ["#FF000000", "#FFB4B4B4", "#FF3E4146", "#FFFF5A4E", "#FF4FC3F7"]),
        ("Kraft", ["#FFE8DCC6", "#FF3B2F24", "#FF9C8C76", "#FFB3261E", "#FF2F55C8"]),
        ("Blueprint", ["#FF16324F", "#FFE8F0F8", "#FF4F6E8E", "#FFFFD166", "#FFFF8A65"]),
        ("Chalk", ["#FF2C3A33", "#FFEDEFE8", "#FF56675D", "#FFFF8A65", "#FF7FE0C3"]),
    ])
    F.list_cfg("density", "Wire", ["Tangled", "Loose", "Single"])
    F.bool_cfg("thread", "Pendulum thread", True)
    F.bool_cfg("sec", "Second hand", True)
    F.color_cfg("skc", "Seconds ink", [("Blue", ["#FF2F6BFF"]), ("Cyan", ["#FF29B6F6"]), ("Coral", ["#FFFF7A59"]), ("Mint", ["#FF5BD6B0"]), ("Green", ["#FF2E9E5B"]), ("Violet", ["#FF8E5CF5"])])
    F.list_cfg("hours", "Hours", ["12 hour", "24 hour"])
    F.bool_cfg("tag", "Digital time", True)
    F.bool_cfg("date", "Day and date", True)
    HW = F.font("caveat_bold")
    bg, wr, dc, hc = (C(TH, i) for i in range(4))
    imgs = [F.img("sc_heavy", scribble_img(15, 7)), F.img("sc_light", scribble_img(8, 3)), F.img("sc_single", scribble_img(2, 5))]
    full = lambda n, tint: f'<PartImage x="0" y="0" width="450" height="450" tintColor="{tint}"><Image resource="{n}"/></PartImage>'
    wire = lambda tint: list_scene("density", [full(n, tint) for n in imgs])
    th = F.img("sc_thread", wobble_line_img(225, 16, 190, 4))
    thread = bool_scene("thread", full(th, wr))
    kn = F.img("sc_knot", knot_img(36, 7, 11, pen=2.1))
    ks = F.images[kn].size[0]
    knot = lambda tint: f'<PartImage x="{225 - ks // 2}" y="{225 - ks // 2}" width="{ks}" height="{ks}" tintColor="{tint}"><Image resource="{kn}"/></PartImage>'
    h_ = scribble_hand(88, 12, 5.2, 3, 3.0, 21)
    m_ = scribble_hand(134, 14, 4.4, 3, 2.6, 22)
    ha, hb = hands_pair(F, "sc", [("HourHand", h_), ("MinuteHand", m_)], hc, "#FFE0E0E0")
    # seconds: a pen draws one calm loop from 12 back to 12 each minute
    sec_xml = wander_seconds(303, C("skc"), segs=300)  # one calm path, redrawn every minute
    # hanging time tag: knot -> short thread -> scribbled tag with handwritten time
    TT, TW_, TH_ = 288, 220, 76
    def cond(expr, yes, no):
        return (f'<Condition><Expressions><Expression name="c"><![CDATA[{expr}]]></Expression></Expressions>'
                f'<Compare expression="c">{yes}</Compare><Default>{no}</Default></Condition>')
    def tline(ink, accent, h24):
        hm = font(HW, 54, ink, tpl("%s:%s", "[HOUR_0_23]" if h24 else "[HOUR_1_12]", "[MINUTE_Z]"))
        box = lambda extra: text(CX - TW_ / 2, TT + 12, TW_, 62, hm, extra)
        if h24:
            return box("")
        return cond("[AMPM_STATE] == 0", box(font(HW, 32, accent, " am")), box(font(HW, 32, accent, " pm")))
    dline = lambda ink: bool_scene("date",
        text(52, 203, 116, 44, font(HW, 36, ink, tpl("%s", "[DAY_OF_WEEK_S]")), align="CENTER")
        + text(282, 203, 116, 44, font(HW, 36, ink, tpl("%s %s", "[DAY]", "[MONTH_S]")), align="CENTER"))
    tag = lambda ink, accent: list_scene("hours", [tline(ink, accent, False), tline(ink, accent, True)]) + dline(ink)
    # text sits above the hands so time/day/date are never covered
    F.add(active(draw(circle(225, bg)), wire(wr), thread, knot(wr), clock(*ha),
                 bool_scene("sec", sec_xml), draw(circle(3.2, hc)),
                 bool_scene("tag", tag(wr, hc))),
          ambient(wire("#FF4A4A4A"), knot("#FF6A6A6A"), clock(*hb), bool_scene("tag", tag("#FF8A8A8A", "#FF8A8A8A"))))
    return F
