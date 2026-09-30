from pathlib import Path
import cairosvg

root=Path(__file__).resolve().parent.parent
folder=root/'assets/cursors'
folder.mkdir(parents=True,exist_ok=True)
paths={
 'arrow': '<path d="M4 3L26 19L16.5 20.5L12.5 29Z" fill="#fff7ee" stroke="#101315" stroke-width="1.7" stroke-linejoin="round"/><path d="M6.7 7L21.7 18.1L15.1 19Z" fill="#a5cf7a"/>',
 'hand': '<path d="M11 17V6.5C11 3.3 16 3.3 16 6.5V13.5C16 11.2 20 11.3 20 14V15C20 12.7 24 13 24 15.5V17C24 14.7 28 15.4 28 18.2V23C28 26.5 25 29 21.5 29H15.3C12.6 29 11.1 27.9 9.6 25.5L4.7 19.1C3 16.5 6.3 14.1 8.2 16.2L11 19" fill="#fff7ee" stroke="#101315" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/><path d="M13 26.5H23.7V29H15.3Z" fill="#a5cf7a"/><path d="M16 14V20M20 16V21M24 18V22" stroke="#101315" stroke-width="1" stroke-linecap="round"/>',
 'text': '<path d="M10 4H22M16 4V28M10 28H22" fill="none" stroke="#101315" stroke-width="4" stroke-linecap="round"/><path d="M10 4H22M16 4V28M10 28H22" fill="none" stroke="#fff7ee" stroke-width="2" stroke-linecap="round"/><path d="M16 10V22" stroke="#a5cf7a" stroke-width="2.2"/>',
 'move': '<path d="M16 5V27M5 16H27" stroke="#101315" stroke-width="4" stroke-linecap="round"/><path d="M16 5V27M5 16H27" stroke="#fff7ee" stroke-width="1.8"/><path d="M16 2L11 8H21ZM16 30L11 24H21ZM2 16L8 11V21ZM30 16L24 11V21Z" fill="#a5cf7a" stroke="#101315" stroke-width="1" stroke-linejoin="round"/>'
}
for name,path in paths.items():
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">{path}</svg>'
 (folder/f'{name}.svg').write_text(svg)
 cairosvg.svg2png(bytestring=svg.encode(),write_to=str(folder/f'{name}.png'),output_width=24,output_height=24)
print('Created four original transparent SVG and PNG cursors.')
