# =====================================================================  2. AXIS (Swiss minimal)
@face
def axis():
    F = Face("axis", "Axis")
    F.font("roboto_medium")
    F.color_cfg(TH, "Dial", [
        ("Light", ["#FFE4E4E2", "#FF151515", "#FFBDBDBA", "#FF8C8C8A"]),
        ("Dark", ["#FF161616", "#FFF2F2F2", "#FF3A3A3A", "#FF8A8A8A"]),
        ("Paper", ["#FFF4F0E8", "#FF222222", "#FFD6D0C4", "#FF948C7E"]),
        ("Steel", ["#FF2E3338", "#FFF0F2F4", "#FF4C535A", "#FF9AA3AC"]),
        ("Sage", ["#FFD5DBD0", "#FF1E2A22", "#FFB0BAAA", "#FF6E7B70"]),
    ])
    F.color_cfg("accent", "Accent", ACCENTS)
    F.list_cfg("index", "Index", ["Crosshair", "Cardinal", "Minute track", "None"])
    F.list_cfg("sec", "Seconds", ["Sweep", "Tick", "Off"])
    F.bool_cfg("date", "Date", True)

    bg, ink, ln, tx = (C(TH, i) for i in range(4))
    dial = draw(circle(225, bg),
                radial_fill(225, ["#00000000", "#00000000", "#14000000", "#38000000"], [0, 0.84, 0.94, 1]),
                circle(199, None, ln, 1.2))
    idx = [
        draw(line(225, 34, 225, 286, ln, 1.4, "BUTT"), line(225, 322, 225, 416, ln, 1.4, "BUTT"), line(34, 225, 416, 225, ln, 1.4, "BUTT")),
        draw(*[radial_line(160, 196, a, ink, 3.2, "BUTT") for a in range(0, 360, 90)],
             *[radial_line(186, 196, a, ln, 2, "BUTT") for a in range(0, 360, 30) if a % 90]),
        draw(*[radial_line(176 if a % 30 == 0 else 189, 197, a, ink if a % 30 == 0 else ln, 2.4 if a % 30 == 0 else 1.2, "BUTT")
               for a in range(0, 360, 6)]),
        "",
    ]
    date = bool_scene("date", text(150, 292, 150, 22, font("roboto_medium", 13, tx, "<Upper>" + DAYDATE + "</Upper>", 0.2)))
    h_, m_ = bar_hand(8, 108, tail=18), bar_hand(4.5, 176, tail=22)
    s_ = bar_hand(3, 158, tail=42, cap_r=6.5)
    ha, hb = hands_pair(F, "ax", [("HourHand", h_), ("MinuteHand", m_)], ink, "#FFD8D8D8")
    sn = F.img("ax_sec", s_[0])
    secs = [clock(hand("SecondHand", sn, *s_, tint=C("accent"), inner=SWEEP)),
            clock(hand("SecondHand", sn, *s_, tint=C("accent"))), ""]
    cap = draw(circle(3.2, bg))
    F.add(active(dial, list_scene("index", idx), date, clock(*ha), list_scene("sec", secs), cap),
          ambient(draw(*[radial_line(186, 197, a, "#FF5A5A5A", 2, "BUTT") for a in range(0, 360, 30)]), clock(*hb)))
    return F


