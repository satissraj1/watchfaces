# =====================================================================  3. HAZE (blurred hands)
def float_bar(width, r0, r1, blur):
    pad = int(blur * 3) + 2
    w = int(width) + 2 * pad
    w += w % 2
    h = int(r1) + pad
    im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([(w - width) / 2 * SS, (h - r1) * SS, (w + width) / 2 * SS, (h - r0) * SS], radius=width / 2 * SS, fill=(255, 255, 255, 255))
    im = im.resize((w, h), Image.LANCZOS)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return im, w / 2, h


@face
def haze():
    F = Face("haze", "Haze")
    # 0 bg, 1 hands, 2 rim, 3 shadow
    F.color_cfg(TH, "Mood", [
        ("Fog", ["#FFC9C8BF", "#FF3D3D3F", "#FFE4E2DA", "#33000000"]),
        ("Dusk", ["#FF2A2A2C", "#FFD8D8D2", "#FF3A3A3D", "#66000000"]),
        ("Sage", ["#FFB9C2B1", "#FF2F3A2E", "#FFD6DDCF", "#33000000"]),
        ("Blush", ["#FFE6D3CF", "#FF4A3A38", "#FFF3E7E4", "#2E000000"]),
        ("Night", ["#FF0E0F12", "#FFB8BCC8", "#FF1B1C21", "#80000000"]),
        ("Sand", ["#FFE2D6C1", "#FF3B3127", "#FFF0E7D8", "#2E000000"]),
    ])
    F.color_cfg("accent", "Dot", [("Rose", ["#FFE0525E"])] + ACCENTS[1:] + [("Ink", ["#FF222222"]), ("White", ["#FFF5F5F5"])])
    F.list_cfg("blur", "Focus", ["Soft", "Dreamy", "Sharp"])
    F.bool_cfg("sec", "Seconds dot", True)
    F.list_cfg("marks", "Markers", ["None", "Soft dots", "Soft bars"])
    bg, hc, rim, sh = (C(TH, i) for i in range(4))
    mk = F.img("hz_mark", float_bar(10, 0, 10, 2.2)[0])
    mb = F.img("hz_markbar", float_bar(9, 0, 26, 2.2)[0])

    def marks(res, size, r):
        w, h = size
        out = ""
        for a in range(0, 360, 90 if res == mk else 30):
            x, y = polar(r, a)
            out += (f'<PartImage x="{f(x - w / 2)}" y="{f(y - h / 2)}" width="{w}" height="{h}" angle="{a}" '
                    f'pivotX="0.5" pivotY="0.5" tintColor="{hc}" alpha="150"><Image resource="{res}"/></PartImage>')
        return out
    mark_xml = list_scene("marks", ["", marks(mk, F.images[mk].size, 196), marks(mb, F.images[mb].size, 190)])
    F.list_cfg("bezel", "Bezel", ["Full screen", "Rim"])
    dial = list_scene("bezel", [
        draw(circle(225, bg), radial_fill(225, ["#00000000", "#00000000", "#1E000000", "#48000000"], [0, 0.8, 0.94, 1])),
        draw(circle(225, rim), circle(211, bg),
             radial_fill(211, ["#00000000", "#00000000", "#22000000", "#55000000"], [0, 0.86, 0.96, 1]))])
    opts, amb = [], []
    for i, b in enumerate([7, 13, 1.2]):
        hi, mi = float_bar(34, 18, 118, b), float_bar(30, 18, 172, b)
        si = dot_hand(120, 24, blur=b * 0.45)
        hn, mn, sn = F.img(f"hz_h{i}", hi[0]), F.img(f"hz_m{i}", mi[0]), F.img(f"hz_s{i}", si[0])
        sec = bool_scene("sec", active(clock(hand("SecondHand", sn, *si, tint=C("accent"), inner=SWEEP))))
        opts.append(sec + active(clock(hand("HourHand", hn, *hi, tint=hc), hand("MinuteHand", mn, *mi, tint=hc))))
        amb.append(ambient(clock(hand("HourHand", hn, *hi, tint="#FF9A9A9A"), hand("MinuteHand", mn, *mi, tint="#FFBDBDBD"))))
    # seconds dot sits *under* the hands (like the reference)
    F.add(active(dial, mark_xml), list_scene("blur", [o + a for o, a in zip(opts, amb)]))
    return F


