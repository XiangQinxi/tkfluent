import cairosvg

svg_path = "C:\\Users\\Xiang\\Downloads\\Mode=Light, Style=Standard, State=Rest, Solid Card=False.svg"
png_path = '1.png'
cairosvg.svg2png(url=svg_path, write_to=png_path, dpi=600)