# =====================================================================  4. TUNER (radio dial)
@face
def tuner():
    F = Face("tuner", "Tuner")
    F.clock_type = "DIGITAL"
    F.font("roboto_light"); F.font("roboto_medium"); F.font("roboto_regular")
    F.color_cfg(TH, "Theme", [
        ("Light", ["#FFE8E8E6", "#FF111111", "#FF5E5E5E", "#FFB4B4B2"]),
        ("Dark", ["#FF0E0E0E", "#FFF2F2F2", "#FFA3A3A3", "#FF3C3C3C"]),
        ("Sand", ["#FFEDE6DA", "#FF1F1B16", "#FF6B604E", "#FFC9BEAC"]),
        ("Navy", ["#FF0C1626", "#FFEAF0FA", "#FF97A6BF", "#FF2A3A54"]),
        ("Olive", ["#FF23271D", "#FFE9ECDD", "#FFA9B094", "#FF464C3B"]),
    ])
    F.color_cfg("accent", "Needle", ACCENTS)
    F.list_cfg("hours", "Hours", ["12 hour", "24 hour"])
    F.list_cfg("scale", "Dial tracks", ["Seconds", "Minutes"])
    bg, ink, mu, fa = (C(TH, i) for i in range(4))
    acc = C("accent")
    Y0, ST = 92, 4.4
    scale = draw(*[line(356 if i % 5 else 336, Y0 + i * ST, 370, Y0 + i * ST, mu if i % 5 == 0 else fa, 2 if i % 5 == 0 else 1.3, "BUTT")
                   for i in range(61)])
    labels = "".join(text(377, Y0 + i * ST - 9, 40, 18, font("roboto_medium", 13, mu, f"{i:02d}"), align="START") for i in range(0, 61, 10))
    head = (text(96, 86, 200, 20, font("roboto_medium", 14, mu, "<Upper>" + tpl("%s", "[TIMEZONE_ABB]") + "</Upper>", 0.18), align="START")
            + draw(line(70, 96, 88, 96, acc, 2.5, "BUTT"))
            + text(70, 108, 240, 24, font("roboto_medium", 17, ink, "<Upper>" + tpl("%s %s %s", "[DAY_OF_WEEK_S]", "[DAY]", "[MONTH_S]") + "</Upper>", 0.08), align="START"))

    def big(hexpr, cink, ccol):
        return text(58, 142, 270, 116, font("roboto_regular", 94, cink, tpl("%s", hexpr)), font("roboto_regular", 94, ccol, ":"),
                    font("roboto_regular", 94, cink, tpl("%s", "[MINUTE_Z]")), align="START")
    hrs = ["[HOUR_1_12_Z]", "[HOUR_0_23_Z]"]

    def needle(expr, col, label=True):
        t = f'<Transform target="y" value="{Y0 - 4} + ({expr}) * {ST}"/>'
        out = draw(line(326, 4, 372, 4, col, 3, "BUTT"), x=0, y=Y0 - 4, w=W, h=8, extra=t)
        if label:
            tt = f'<Transform target="y" value="{Y0 - 11} + ({expr}) * {ST}"/>'
            out += draw(rrect(0, 0, 32, 22, 6, col), x=373, y=Y0 - 11, w=32, h=22, extra=tt)
            out += text(373, Y0 - 11, 32, 22, font("roboto_medium", 14, bg, tpl("%s", "[SECOND_Z]" if "MINUTE" not in expr else "[MINUTE_Z]")), extra=tt)
        return out
    needles = [needle("[SECOND_MILLISECOND]", acc), needle("[MINUTE] + [SECOND] / 60", acc)]

    def comp(slot, x, provider):
        w, h = 112, 40
        return (f'<ComplicationSlot slotId="{slot}" name="c{slot}" x="{x}" y="292" width="{w}" height="{h}" '
                f'supportedTypes="SHORT_TEXT EMPTY" isCustomizable="TRUE">'
                f'<DefaultProviderPolicy defaultSystemProvider="{provider}" defaultSystemProviderType="SHORT_TEXT"/>'
                f'<BoundingBox x="0" y="0" width="{w}" height="{h}"/>'
                f'<Complication type="SHORT_TEXT">'
                + draw(rrect(1, 9, 46, 22, 11, None, mu, 1.4), w=w, h=h)
                + f'<PartImage x="14" y="11" width="20" height="18" tintColor="{mu}"><Image resource="[COMPLICATION.MONOCHROMATIC_IMAGE]"/></PartImage>'
                + text(54, 3, 62, 34, font("roboto_medium", 20, ink, tpl("%s", "[COMPLICATION.TEXT]")), align="START")
                + '</Complication><Complication type="EMPTY"></Complication></ComplicationSlot>')

    chev = draw(line(213, 404, 225, 394, ink, 2), line(225, 394, 237, 404, ink, 2))
    F.add(active(draw(circle(225, bg)), scale, labels, head, chev, list_scene("scale", needles)),
          active(list_scene("hours", [big(h, ink, mu) for h in hrs])),
          ambient(list_scene("hours", [big(h, "#FFCFCFCF", "#FF5A5A5A") for h in hrs]),
                  draw(*[line(356 if i % 5 else 340, Y0 + i * ST, 370, Y0 + i * ST, "#FF3A3A3A", 1.3, "BUTT") for i in range(0, 61, 5)]),
                  needle("[MINUTE]", "#FF9A9A9A", label=False)),
          comp(0, 60, "WATCH_BATTERY"), comp(1, 180, "STEP_COUNT"))
    return F


