from pathlib import Path
import base64, json, re, io
import requests
from PIL import Image, ImageOps, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'assets'

def uri(path, mime):
    return f'data:{mime};base64,'+base64.b64encode(Path(path).read_bytes()).decode()

def optimize(source,target,size,quality=85,center=(.5,.5)):
    im=Image.open(source).convert('RGB')
    im=ImageOps.fit(im,size,method=Image.Resampling.LANCZOS,centering=center)
    im.save(target,format='WEBP',quality=quality,method=6)

# A custom speed mark, and true vector wordmark (no background, no font dependency).
markpath='M1 28H8L15 16H8ZM9 36H17L28 16H20ZM22 4H34L46 24L34 44H22L34 24Z'
mark=f'<svg class="brand-mark" viewBox="0 0 48 48" aria-hidden="true"><path fill="currentColor" d="{markpath}"/></svg>'
font=instantiateVariableFont(TTFont(ASSETS/'space-grotesk.woff2'),{'wght':700},inplace=False)
glyphs=font.getGlyphSet();cmap=font.getBestCmap();x=0;paths=[]
for char in 'speedy':
    glyph=cmap[ord(char)];pen=SVGPathPen(glyphs);glyphs[glyph].draw(pen)
    paths.append(f'<path transform="translate({x} 0)" d="{pen.getCommands()}"/>')
    x+=font['hmtx'][glyph][0]-38
scale=.049
width=round(57+x*scale+3,2)
logo_content=f'<path fill="#ff783f" d="{markpath}" transform="translate(0 2)"/><g fill="#f2f4f4" transform="translate(57 37) scale({scale} -{scale})">'+''.join(paths)+'</g>'
logo=f'<svg class="brand-logo" viewBox="0 0 {width} 52" aria-hidden="true">{logo_content}</svg>'
standalone=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 52" width="620" height="151" role="img" aria-labelledby="logo-title"><title id="logo-title">Speedy Hosting — transparent wordmark</title>{logo_content}</svg>'
(ROOT/'speedy-logo.svg').write_text(standalone)
(ASSETS/'speedy-mark.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><path fill="#ff783f" d="{markpath}"/></svg>')
favicon=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="15" fill="#ff783f"/><path fill="#0b1116" d="{markpath}" transform="translate(8 8)"/></svg>'
favicon_uri='data:image/svg+xml;base64,'+base64.b64encode(favicon.encode()).decode()

# Embedded variable fonts.
fonts=''
for name,file,minweight,maxweight in [('Manrope','manrope',200,800),('Space Grotesk','space-grotesk',300,700)]:
    fonts+=f"@font-face{{font-family:'{name}';font-style:normal;font-weight:{minweight} {maxweight};font-display:swap;src:url('{uri(ASSETS/(file+'.woff2'),'font/woff2')}') format('woff2')}}\n"

# Phosphor's actual vector icons, not a network-dependent icon font.
icons=['sparkle','copy','x','caret-down','cube','crosshair','game-controller','arrow-up-right','arrow-right','user-circle','list','play','check','lightning','shield-check','puzzle-piece','headset','magnifying-glass','sliders-horizontal','terminal-window','folder-simple','cloud-arrow-up','stop','arrows-clockwise','file-text','download-simple','cloud-check','plus','cpu','hard-drives','globe-hemisphere-west','info','check-circle','chat-circle-dots','users','rocket-launch','star','heart']
symbols=[]
for name in icons:
    source=(ASSETS/'icons/regular'/f'{name}.svg').read_text()
    body=re.search(r'<svg[^>]*>(.*?)</svg>',source,re.S).group(1)
    symbols.append(f'<symbol id="i-{name}" viewBox="0 0 256 256">{body}</symbol>')
source=(ASSETS/'icons/fill/lightning-fill.svg').read_text()
body=re.search(r'<svg[^>]*>(.*?)</svg>',source,re.S).group(1)
symbols.append(f'<symbol id="i-lightning-fill" viewBox="0 0 256 256">{body}</symbol>')
sprite='<svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="position:absolute;width:0;height:0;overflow:hidden"><defs>'+''.join(symbols)+'</defs></svg>'

# Original artwork, optimized once and embedded in the standalone page.
optimize(ASSETS/'v2/engine-art.png',ASSETS/'v2/engine-art.webp',(1000,746),quality=88)
engine_uri=uri(ASSETS/'v2/engine-art.webp','image/webp')
hero_uri=engine_uri
world_art={'minecraft':'block-world','rust':'survival-world','palworld':'fantasy-world','valheim':'nordic-world','terraria':'cavern-world','ark':'prehistoric-world'}
for name,art in world_art.items():
    optimize(ASSETS/f'v2/{art}.png',ASSETS/f'{name}-card.webp',(720,540),quality=87)

games=[
    ('minecraft','Minecraft','Java, Bedrock & endless possibilities',6,'survival sandbox','Community favorite','star',True),
    ('rust','Rust','Build. Raid. Survive. Repeat.',12,'survival','Survive together','crosshair',False),
    ('palworld','Palworld','A whole world of pals & possibilities',12,'survival sandbox','Better with friends','heart',False),
    ('valheim','Valheim','Your next great Viking adventure',6,'survival','Forge your saga','lightning',False),
    ('terraria','Terraria','Dig deeper. Build bigger. Go together.',6,'sandbox survival','Endless discovery','cube',False),
    ('ark','ARK: Survival Ascended','Tame the wild. Make it your world.',24,'survival','Go prehistoric','game-controller',False)
]
cards=[]
for i,(id,name,desc,price,categories,badge,icon,accent) in enumerate(games):
    alt=f'Original {name}-inspired world illustration for game server hosting'
    hidden=' hidden' if i>=4 else ''
    cards.append(f'''<article class="game-card" data-game="{id}" data-categories="{categories}" data-search="{name.lower()} {id} {desc.lower()} {categories}"{hidden}>
  <button class="game-cover" data-config="{id}" aria-label="Configure {name} hosting"><img src="{uri(ASSETS/f'{id}-card.webp','image/webp')}" alt="{alt}" width="720" height="540" loading="lazy"><span class="game-cover-arrow"><svg class="icon" aria-hidden="true"><use href="#i-arrow-up-right"/></svg></span></button>
  <div class="game-card-body"><h3>{name}</h3><span class="game-type">{desc}</span><div class="game-price-row"><span>From <strong>${price:.2f}</strong><small>/mo</small></span><button class="game-config" data-config="{id}" aria-label="Configure {name}"><span>Configure</span><svg class="icon" aria-hidden="true"><use href="#i-arrow-up-right"/></svg></button></div></div>
</article>''')

plans=[('Starter','Small squad. Big possibilities.',4,6,'cube','Vanilla & light worlds',['Unlimited player slots','NVMe storage','Daily world backups','Full file access'],False),('Sidekick','For your everyday adventures.',8,12,'lightning','Room for mods & friends',['Unlimited player slots','NVMe storage','Daily world backups','One-click modpacks'],True),('Legend','Go big. Bring everyone.',16,24,'rocket-launch','Big worlds & heavy packs',['Unlimited player slots','NVMe storage','Daily world backups','One-click modpacks'],False)]
plan_html=[]
for name,desc,ram,price,icon,tag,features,featured in plans:
    badge='<span class="plan-badge"><svg class="icon" aria-hidden="true"><use href="#i-star"/></svg>THE SWEET SPOT</span>' if featured else ''
    benefits=''.join(f'<li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg>{f}</li>' for f in features)
    plan_html.append(f'''<article class="plan-card{' featured' if featured else ''}" data-price="{price}"><div class="plan-topline"><span class="plan-icon"><svg class="icon" aria-hidden="true"><use href="#i-{icon}"/></svg></span>{badge}</div><h3>{name}</h3><p>{desc}</p><div class="plan-price"><strong>${price:.2f}</strong><span>/ month</span></div><span class="plan-bill-note">Billed monthly. Example pricing.</span><div class="plan-ram"><strong>{ram} GB<span>RAM</span></strong><span>{tag}</span></div><ul>{benefits}</ul><button class="button{' button-ghost' if not featured else ''}" data-config="minecraft" data-ram="{ram}">Choose {name} <svg class="icon" aria-hidden="true"><use href="#i-arrow-up-right"/></svg></button></article>''')

# A real vector world silhouette converted into a compact dotted map.
def project(lon,lat):return (lon+180)/360*700,(82-lat)/150*310
geo=json.loads((ASSETS/'world.geojson').read_text())
map_paths=[]
for f in geo['features']:
    if f['properties'].get('ADM0_A3')=='ATA':continue
    polygons=f['geometry']['coordinates']
    if f['geometry']['type']=='Polygon':polygons=[polygons]
    for polygon in polygons:
        ring=polygon[0]
        if not ring:continue
        points=[project(*p[:2]) for p in ring]
        path='M'+'L'.join(f'{x:.1f},{y:.1f}' for x,y in points)+'Z'
        map_paths.append(path)
map_svg='''<svg viewBox="0 0 700 310" role="group" aria-label="Example network map. Choose a server region."><defs><pattern id="map-dots" width="4.4" height="4.4" patternUnits="userSpaceOnUse"><circle cx="2.2" cy="2.2" r=".7" fill="#7b9ba8" opacity=".5"/></pattern><pattern id="map-grid" width="70" height="62" patternUnits="userSpaceOnUse"><path d="M70 0H0V62" fill="none" stroke="#28404b" stroke-width=".4" opacity=".4"/></pattern></defs><rect width="700" height="310" fill="url(#map-grid)"/><g fill="url(#map-dots)">'''
map_svg+=''.join(f'<path d="{p}"/>' for p in map_paths)+'</g>'
map_svg+='<path class="map-route" d="M200 89Q385 -20 551 166"/><path class="map-route" d="M366 66Q488 65 551 166"/><path class="map-route" d="M200 89Q283 4 366 66"/>'
for id,lon,lat,label in [('ashburn',-77.487,39.044,'ASHBURN'),('frankfurt',8.682,50.11,'FRANKFURT'),('singapore',103.82,1.352,'SINGAPORE')]:
    x,y=project(lon,lat);active=id=='singapore'
    map_svg+=f'<g class="map-pin{" active" if active else ""}" transform="translate({x:.1f} {y:.1f})" data-map-region="{id}" role="button" tabindex="0" aria-label="Select {label.title()} example region" aria-pressed="{str(active).lower()}"><rect x="-25" y="-24" width="50" height="58" fill="transparent"/><circle class="pin-glow" r="22"/><circle class="pin-ring" r="13"/><circle class="pin-core" r="5.5"/><text y="33">{label}</text></g>'
map_svg+='</svg>'

# Social-sharing previews must have a public URL; this optional publishing asset is not needed by the page.
social=Image.new('RGB',(1200,630),'#0b1116')
art=Image.open(ASSETS/'v2/engine-art.png').convert('RGB');art=ImageOps.fit(art,(800,630),centering=(.63,.5));social.paste(art,(400,0))
# A smooth dark fade behind the lettering.
pix=social.load()
for px in range(680):
    factor=max(0,(px-320)/360)
    for py in range(630):
        old=pix[px,py];pix[px,py]=tuple(round(a*factor+b*(1-factor)) for a,b in zip(old,(11,17,22)))
font.flavor=None;font.save(ASSETS/'space-bold.ttf')
textfont=ImageFont.truetype(str(ASSETS/'space-bold.ttf'),68)
smallfont=ImageFont.truetype(str(ASSETS/'space-bold.ttf'),22)
draw=ImageDraw.Draw(social)
draw.text((67,71),'speedy',font=ImageFont.truetype(str(ASSETS/'space-bold.ttf'),37),fill='#ff783f')
draw.text((65,190),'Your world.',font=textfont,fill='#f2f4f4')
draw.text((65,277),'At full speed.',font=textfont,fill='#ff783f')
draw.text((68,423),'LESS SETUP. MORE PLAY.',font=smallfont,fill='#a9bcc8')
social.save(ROOT/'social-preview.jpg',quality=91,optimize=True)

licenses='''ASSET CREDITS AND LICENSES
Seven original game-world and hardware illustrations: AI-generated for this design.
Cursor artwork: original transparent vector designs.
Game names belong to their respective publishers. This concept is unaffiliated with those publishers.
Map geography: Natural Earth, public domain (naturalearthdata.com).
Fonts: Space Grotesk by Florian Karsten; Manrope by Mikhail Sharanda. SIL Open Font License 1.1.
Phosphor Icons: https://phosphoricons.com — MIT License.
Copyright (c) 2020 Phosphor Icons.
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the Software), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
# Include the complete OFL when available.
for family,url in [('Space Grotesk','https://raw.githubusercontent.com/google/fonts/main/ofl/spacegrotesk/OFL.txt'),('Manrope','https://raw.githubusercontent.com/google/fonts/main/ofl/manrope/OFL.txt')]:
    saved=ASSETS/f'{family.lower().replace(" ","-")}-OFL.txt'
    if not saved.exists():
        try:
            response=requests.get(url,timeout=15);response.raise_for_status();saved.write_text(response.text)
        except Exception:pass
    if saved.exists():licenses+=f'\n{family} Font License:\n'+saved.read_text()
licenses=licenses.replace('--','—')
js=(ROOT/'tools/site.js').read_text().replace('@@LOGO_JSON@@',json.dumps(standalone))
replacements={'@@FAVICON@@':favicon_uri,'@@FONTS@@':fonts,'@@CSS@@':(ROOT/'tools/site.css').read_text()+'\n'+(ROOT/'tools/v2.css').read_text(),'@@LICENSES@@':licenses,'@@SPRITE@@':sprite,'@@LOGO@@':logo,'@@MARK@@':mark,'@@HERO@@':hero_uri,'@@GAMECARDS@@':'\n'.join(cards),'@@PLANS@@':'\n'.join(plan_html),'@@MAP@@':map_svg,'@@JS@@':js,'@@ENGINE_IMAGE@@':engine_uri,'@@SCENE@@':(ASSETS/'v2/scene.min.js').read_text()}
for name in ['arrow','hand','text','move']:
    replacements[f'@@CURSOR_{name.upper()}@@']=uri(ASSETS/f'cursors/{name}.png','image/png')
three_license=ROOT/'node_modules/three/LICENSE'
if three_license.exists():
    replacements['@@LICENSES@@']+='\nThree.js License:\n'+three_license.read_text()
html=(ROOT/'tools/site.html').read_text()
for token,value in replacements.items():html=html.replace(token,value)
assert not re.search(r'@@[A-Z_]+@@',html), 'Unreplaced template token'
(ROOT/'index.html').write_text(html)
public=ROOT/'public';public.mkdir(exist_ok=True)
(public/'index.html').write_text(html)
for name in ['speedy-logo.svg','social-preview.jpg']:
    (public/name).write_bytes((ROOT/name).read_bytes())
print(f'Built index.html: {len(html.encode())/1024:.0f} KB. Logo: {width} × 52. All visual assets inline.')
