from svgwrite import Drawing

dwg = Drawing("6.svg", (160, 32), fill="none")
dwg["xmlns"] = "http://www.w3.org/2000/svg"
dwg["xmlns:xlink"] = "http://www.w3.org/1999/xlink"

border = dwg.linearGradient(start=(12, 1), end=(12, 12 * 2 - 1), id="DButton.Border",
                                   gradientUnits="userSpaceOnUse")
border.add_stop_color(0.500208, outline, outline_opacity)
border.add_stop_color(0.954545, outline2, outline2_opacity)
dwg.defs.add(border)
stroke = f"url(#{border.get_id()})"

dwg.add(
    dwg.rect(
        (x1, (y2 - y1) / 2 - 3), (x2 - x1, (y2 - y1) / 2 + 3), rx=3,
        fill=fill
    )
)
print((x1, (y2 - y1) / 2 - 3), (x2 - x1, (y2 - y1) / 2 + 3))

x = x3
y = (y2 - y1) / 2

dwg.add(
    dwg.circle(
        (x, y), r1,
        fill=stroke, fill_opacity=1, fill_rule="evenodd"
    )
)
dwg.add(
    dwg.circle(
        (x, y), r1 - 1,
        fill=fill, fill_opacity=fill_opacity, fill_rule="nonzero"
    )
)
dwg.add(
    dwg.circle(
        (x, y), r2,
        fill=inner_fill, fill_opacity=inner_fill_opacity, fill_rule="nonzero"
    )
)

dwg.save()
