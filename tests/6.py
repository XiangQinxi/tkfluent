from svgwrite import Drawing

dwg = Drawing("6.svg", (160, 32), fill="none")
dwg["xmlns"] = "http://www.w3.org/2000/svg"
dwg["xmlns:xlink"] = "http://www.w3.org/1999/xlink"

clip1 = dwg.clipPath()

rect1 = dwg.rect((0, 0), ("160.000000", "32.000000"), fill="white", fill_opacity="0")
clip1.add(rect1)

linear_gradient = dwg.linearGradient(x1="80.000000", y1="0.000000", x2="80.000000", y2="30.000000",
                                     id="paint_linear_31_43213_0", gradientUnits="userSpaceOnUse")
linear_gradient.add_stop_color("0.939453", "#FFFFFF", "0.000000")
linear_gradient.add_stop_color("0.941406", "#FFFFFF", )

dwg.defs.add(clip1)
dwg.defs.add(linear_gradient)

rect2 = dwg.rect(("1.000000", "1.000000"), ("158.000000", "30.000000"), rx="3.000000", fill="#FFFFFF",
                 fill_opacity="1.000000")

group1 = dwg.g(clip_path=f"url(#{clip1.get_id()})")

rect3 = dwg.rect(("0.500000", "0.500000"), ("159.000000", "31.000000"), rx="3.000000", stroke="#000000",
                 stroke_opacity="0.057800", stroke_width="1.000000")

mask = dwg.mask(maskUnits="userSpaceOnUse", x="0.000000", y="0.000000", width="160.000000", height="30.000000")

rect4 = dwg.rect(("-1.000000", "-1.000000"), ("162.000000", "32.000000"), stroke=f"url(#{linear_gradient.get_id()})",
                 stroke_opacity="1.000000", stroke_width="2.000000")

mask.add(rect4)

group2 = dwg.g(mask=f"url(#{mask.get_id()})")

rect5 = dwg.rect(("1.000000", "1.000000"), ("158.000000", "30.000000"), rx="4.000000", stroke="#005FB8",
                 stroke_opacity="1.000000", stroke_width="2.000000")

group2.add(rect5)

group1.add(rect3)
group1.add(mask)
group1.add(group2)

dwg.add(rect2)
dwg.add(group1)

dwg.save()


def remove_namespace_prefix(element):
    if '}' in element.tag:
        element.tag = element.tag.split('}', 1)[1]  # 移除前缀
    for child in list(element):
        remove_namespace_prefix(child)


import xml.etree.ElementTree as ET
from xml.dom import minidom

tree = ET.parse("6.svg")
root = tree.getroot()

root.set('xmlns', "http://www.w3.org/2000/svg")
root.set('xmlns:xlink', "http://www.w3.org/1999/xlink")

remove_namespace_prefix(root)

# 保存修改后的 XML 文件
tree.write('6.svg')

# 读取和解析 XML 文件
with open('6.svg', 'r', encoding='utf-8') as file:
    xml_content = file.read()

# 解析 XML 内容
dom = minidom.parseString(xml_content)

# 获取格式化后的 XML 字符串
pretty_xml_as_string = dom.toprettyxml(indent='    ')

# 保存格式化后的 XML 文件
with open('6.svg', 'w', encoding='utf-8') as file:
    file.write(pretty_xml_as_string)

"""
<svg width="160.000000" height="32.000000" viewBox="0 0 160 32" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
	<desc>
			Created with Pixso.
	</desc>
	<defs>
		<clipPath id="clip31_43215">
			<rect id="Text Active Box / Text Active Box" width="160.000000" height="32.000000" fill="white" fill-opacity="0"/>
		</clipPath>
		<linearGradient x1="80.000000" y1="0.000000" x2="80.000000" y2="30.000000" id="paint_linear_31_43213_0" gradientUnits="userSpaceOnUse">
			<stop offset="0.939453" stop-color="#FFFFFF" stop-opacity="0.000000"/>
			<stop offset="0.941406" stop-color="#FFFFFF"/>
		</linearGradient>
	</defs>
	<rect id="Base" x="1.000000" y="1.000000" rx="3.000000" width="158.000000" height="30.000000" fill="#FFFFFF" fill-opacity="1.000000"/>

	<path id="Text" d="M16.23 12.03L19.06 12.03L19.06 10.99L12.26 10.99L12.26 12.03L15.08 12.03L15.08 20.79L16.23 20.79L16.23 12.03ZM35.63 20.88C35.81 20.84 36 20.79 36.19 20.71L35.92 19.86C35.83 19.9 35.73 19.93 35.6 19.96C35.47 20 35.34 20.01 35.2 20.01C34.92 20.01 34.7 19.92 34.55 19.75C34.41 19.57 34.34 19.28 34.34 18.88L34.34 14.75L36.11 14.75L36.11 13.79L34.34 13.79L34.34 11.72L33.22 12.08L33.22 13.79L32.02 13.79L32.02 14.75L33.22 14.75L33.22 19.01Q33.22 19.96 33.69 20.46C34.01 20.78 34.45 20.94 35 20.94C35.24 20.94 35.44 20.92 35.63 20.88ZM19.78 17.54L24.73 17.54L24.73 16.99Q24.73 15.41 23.97 14.52Q23.76 14.27 23.49 14.08Q22.83 13.63 21.85 13.63Q21.04 13.63 20.4 13.96Q19.91 14.21 19.51 14.66Q19.42 14.77 19.34 14.88Q18.62 15.87 18.63 17.38C18.63 18.51 18.93 19.38 19.52 20.01C20.11 20.64 20.94 20.96 22 20.96Q22.71 20.96 23.3 20.78C23.7 20.66 24.09 20.47 24.49 20.22L23.97 19.42Q23.51 19.73 23.03 19.87C22.71 19.96 22.4 20.01 22.08 20.01Q21.2 20.01 20.64 19.58Q20.51 19.49 20.4 19.37C20.01 18.94 19.8 18.33 19.78 17.54ZM29.19 17.33L31.55 13.79L30.31 13.79L28.89 16.18L28.56 16.73L28.53 16.73L28.38 16.46C28.34 16.37 28.29 16.28 28.24 16.18L26.88 13.79L25.58 13.79L27.86 17.36L25.48 20.79L26.77 20.79L28.17 18.52C28.26 18.37 28.34 18.24 28.39 18.15Q28.47 18.02 28.49 17.99L28.52 17.99C28.58 18.1 28.63 18.2 28.68 18.28C28.73 18.37 28.78 18.45 28.83 18.52L30.2 20.79L31.5 20.79L29.19 17.33ZM23.11 15.12C23.42 15.48 23.58 15.98 23.58 16.63L19.79 16.63Q19.91 15.75 20.4 15.21Q20.43 15.17 20.47 15.13C20.85 14.76 21.3 14.57 21.83 14.57C22.37 14.57 22.8 14.75 23.11 15.12Z" fill="#000000" fill-opacity="0.606300" fill-rule="evenodd"/>

	<g clip-path="url(#clip31_43215)">
		<rect id="Top &amp; Sides" x="0.500000" y="0.500000" rx="3.000000" width="159.000000" height="31.000000" stroke="#000000" stroke-opacity="0.057800" stroke-width="1.000000"/>
		<mask id="mask31_43213" mask-type="alpha" maskUnits="userSpaceOnUse" x="0.000000" y="0.000000" width="160.000000" height="30.000000">
			<rect id="Mask - do not change my corners" x="-1.000000" y="-1.000000" width="162.000000" height="32.000000" stroke="url(#paint_linear_31_43213_0)" stroke-opacity="1.000000" stroke-width="2.000000"/>
		</mask>
		<g mask="url(#mask31_43213)">
			<rect id="Bottom" x="1.000000" y="1.000000" rx="4.000000" width="158.000000" height="30.000000" stroke="#005FB8" stroke-opacity="1.000000" stroke-width="2.000000"/>
		</g>
	</g>
</svg>

"""
