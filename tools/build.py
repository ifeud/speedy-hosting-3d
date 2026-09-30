from pathlib import Path
import base64, json, re, hashlib, html as html_lib
from PIL import Image, ImageOps, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'assets'
ART=ASSETS/'v4'
ART.mkdir(exist_ok=True)

def uri(path,mime):
    return f'data:{mime};base64,'+base64.b64encode(Path(path).read_bytes()).decode()

def webp(source,target,size=(1600,1000),quality=91):
    image=Image.open(source).convert('RGB')
    image.thumbnail(size,Image.Resampling.LANCZOS)
    image.save(target,'WEBP',quality=quality,method=6)

# Speedy's own transparent wordmark, not a Minecraft logo or font.
mark_path='M1 28H8L15 16H8ZM9 36H17L28 16H20ZM22 4H34L46 24L34 44H22L34 24Z'
mark=f'<svg class="brand-mark" viewBox="0 0 48 48" aria-hidden="true"><path fill="currentColor" d="{mark_path}"/></svg>'
font=TTFont(ASSETS/'archivo-black.woff2')
glyphs=font.getGlyphSet();cmap=font.getBestCmap();paths=[];x=0
for char in 'speedy':
    glyph=cmap[ord(char)];pen=SVGPathPen(glyphs);glyphs[glyph].draw(pen)
    paths.append(f'<path transform="translate({x} 0)" d="{pen.getCommands()}"/>')
    x+=font['hmtx'][glyph][0]-20
scale=.043
width=round(57+x*scale+4,2)
logo_content=f'<path fill="#92c763" d="{mark_path}" transform="translate(0 2)"/><g fill="#f4f7f0" transform="translate(57 37) scale({scale} -{scale})">'+''.join(paths)+'</g>'
logo=f'<svg class="brand-logo" viewBox="0 0 {width} 52" aria-hidden="true">{logo_content}</svg>'
standalone=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 52" width="620" height="151" role="img" aria-labelledby="logo-title"><title id="logo-title">Speedy Hosting transparent wordmark</title>{logo_content}</svg>'
(ROOT/'speedy-logo.svg').write_text(standalone)
(ROOT/'speedy-logo-dark.svg').write_text(standalone.replace('fill="#f4f7f0"','fill="#23371e"'))
(ASSETS/'speedy-mark.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><path fill="#92c763" d="{mark_path}"/></svg>')
favicon=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#92c763"/><path fill="#183b1c" d="{mark_path}" transform="translate(8 8)"/></svg>'
favicon_uri='data:image/svg+xml;base64,'+base64.b64encode(favicon.encode()).decode()
font_faces=''
for family,file,weight in [('Archivo Black','archivo-black','400'),('Noto Sans','noto-sans','100 900'),('IBM Plex Mono','ibm-plex-mono','400')]:
    font_faces+=f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};font-display:swap;src:url('{uri(ASSETS/(file+'.woff2'),'font/woff2')}') format('woff2')}}\n"

icons=['sparkle','copy','x','caret-down','cube','crosshair','game-controller','arrow-up-right','arrow-right','user-circle','list','play','check','lightning','shield-check','puzzle-piece','headset','magnifying-glass','sliders-horizontal','terminal-window','folder-simple','cloud-arrow-up','stop','arrows-clockwise','file-text','download-simple','cloud-check','plus','cpu','hard-drives','globe-hemisphere-west','info','check-circle','chat-circle-dots','users','rocket-launch','star','heart']
symbols=[]
for name in icons:
    source=(ASSETS/'icons/regular'/f'{name}.svg').read_text()
    body=re.search(r'<svg[^>]*>(.*?)</svg>',source,re.S).group(1)
    symbols.append(f'<symbol id="i-{name}" viewBox="0 0 256 256">{body}</symbol>')
sprite='<svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="position:absolute;width:0;height:0;overflow:hidden"><defs>'+''.join(symbols)+'</defs></svg>'

# Only newly generated original illustrations are used. No publisher images.
worlds={'minecraft':'builders-world','rust':'industrial-world','palworld':'companions-world','valheim':'nordic-world','terraria':'cavern-world','ark':'prehistoric-world'}
art_titles={'minecraft':'Riverside builders village','rust':'Coastal relay station','palworld':'Emerald waterfall valley','valheim':'Nordic fjord settlement','terraria':'Amber crystal cavern','ark':'Prehistoric river valley'}
manifest={'created':'2026-09-30','method':'Original AI-generated voxel environment illustrations','publisher_assets_used':False,'limitations':'Original generation and independent branding cannot guarantee legal clearance. Review resemblance, trademark context, operator details and applicable laws before commercial publication.','games':{}}
for game,world in worlds.items():
    source=ART/f'{world}.png'
    webp(source,ASSETS/f'{game}-card.webp',(900,550),quality=91)
    image=Image.open(source)
    manifest['games'][game]={'title':art_titles[game],'local_file':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'dimensions':list(image.size),'type':'original_ai_generated','not_game_screenshot':True}
manifest['hero']={'local_file':'assets/v4/hero-world.png','sha256':hashlib.sha256((ART/'hero-world.png').read_bytes()).hexdigest(),'type':'original_ai_generated'}
(ART/'artwork-manifest.json').write_text(json.dumps(manifest,indent=2))
webp(ART/'hero-world.png',ART/'hero-world.webp',(1600,1000),quality=91)
webp(ART/'builders-world.png',ART/'community-world.webp',(1100,700),quality=91)

# Original vector fallback for the authored real-time hardware sculpture.
fallback='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 430"><defs><linearGradient id="s" x2="1" y2="1"><stop stop-color="#53624a"/><stop offset="1" stop-color="#263621"/></linearGradient></defs><ellipse cx="317" cy="365" rx="205" ry="28" fill="#132112" opacity=".35"/><g stroke="#768b62" stroke-width="2" stroke-linejoin="round"><path d="M112 314L350 250L512 312L279 382Z" fill="#4a5c3e"/><path d="M112 314V333L279 402L512 331V312L279 382Z" fill="#2c4025"/><g fill="url(#s)"><path d="M147 230L341 176L480 226L286 288Z"/><path d="M147 230V296L286 348V288Z"/><path d="M286 288V348L480 288V226Z"/><path d="M158 163L352 109L491 159L297 221Z"/><path d="M158 163V227L297 279V221Z"/><path d="M297 221V279L491 219V159Z"/><path d="M169 96L363 42L502 92L308 154Z"/><path d="M169 96V160L308 212V154Z"/><path d="M308 154V212L502 152V92Z"/></g></g><g stroke="#bbd98c" stroke-width="5" opacity=".85"><path d="M184 110V147M196 114V151M208 119V155M220 123V159M232 128V164M244 132V168M256 137V173M268 141V177M280 146V182"/><path d="M173 178V214M185 182V218M197 187V222M209 191V226M221 196V231M233 200V235M245 205V240M257 209V244M269 214V249"/><path d="M162 245V280M174 249V285M186 254V289M198 258V293M210 263V298M222 267V302M234 272V307M246 276V311M258 281V316"/></g></svg>'''
(ART/'engine-fallback.svg').write_text(fallback)
engine_uri='data:image/svg+xml;base64,'+base64.b64encode(fallback.encode()).decode()

game_data=[('minecraft','Minecraft','Java, Bedrock, vanilla or your favorite modpack.',6,'survival sandbox','Full file access','mc java bedrock mods'),('rust','Rust','Build a base. Pick a fight. Bring a friend.',12,'survival','Full file access','pvp facepunch'),('palworld','Palworld','Good pals. Big adventures. One shared world.',12,'survival sandbox','Full file access','pals pocketpair'),('valheim','Valheim','A place for your next great Viking saga.',6,'survival','Full file access','viking coop iron gate'),('terraria','Terraria','Dig a little deeper. Make something unexpected.',6,'sandbox survival','Mod friendly','tmodloader relogic'),('ark','ARK: Survival Ascended','Tame the wild. Build something that lasts.',24,'survival','Full file access','dinosaurs ark wildcard')]
cards=[];credits=[]
for index,(game,name,description,price,categories,feature,keywords) in enumerate(game_data,1):
    record=manifest['games'][game]
    alt=html_lib.escape(f'Original voxel concept illustration: {record["title"]}. Not official game artwork.',quote=True)
    search=html_lib.escape(f'{name.lower()} {description.lower()} {keywords} {categories}',quote=True)
    cards.append(f'''<article class="game-card" data-game="{game}" data-categories="{categories}" data-search="{search}"><button class="game-cover" data-config="{game}" aria-label="Configure {html_lib.escape(name)} hosting"><img src="{uri(ASSETS/f'{game}-card.webp','image/webp')}" alt="{alt}" width="900" height="503" loading="lazy"><span class="game-cover-arrow"><svg class="icon" aria-hidden="true"><use href="#i-arrow-up-right"/></svg></span></button><div class="game-card-body"><div class="game-card-heading"><h3>{html_lib.escape(name)}</h3><span class="game-number" aria-hidden="true">0{index}</span></div><span class="game-type">{description}</span><div class="game-detail"><span><svg class="icon" aria-hidden="true"><use href="#i-folder-simple"/></svg>{feature}</span><span><svg class="icon" aria-hidden="true"><use href="#i-cloud-check"/></svg>Backups</span></div><div class="game-price-row"><span>From <strong>${price:.2f}</strong><small>/mo</small></span><button class="game-config" data-config="{game}" aria-label="Configure {html_lib.escape(name)}">Configure <svg class="icon" aria-hidden="true"><use href="#i-arrow-up-right"/></svg></button></div></div></article>''')
    credits.append(f'<article><h3>{record["title"]}</h3><p>Original AI-generated environment illustration created for Speedy Hosting. This is a concept illustration beside the supported game name, not a screenshot or publisher asset.</p></article>')

plans=[('Starter','A small squad. A world of possibilities.',4,6,'cube','Vanilla & light worlds',['Unlimited player slots','NVMe storage','Daily world backups','Full file access'],False),('Sidekick','For the people you play with every week.',8,12,'lightning','Room for mods & friends',['Unlimited player slots','NVMe storage','Daily world backups','One-click modpacks'],True),('Legend','For the big ideas and the whole crew.',16,24,'rocket-launch','Big worlds & heavy packs',['Unlimited player slots','NVMe storage','Daily world backups','One-click modpacks'],False)]
plan_html=[]
for name,description,ram,price,icon,tag,features,featured in plans:
    badge='<span class="plan-badge"><svg class="icon" aria-hidden="true"><use href="#i-star"/></svg>A LITTLE MORE ROOM</span>' if featured else ''
    benefits=''.join(f'<li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg>{feature}</li>' for feature in features)
    plan_html.append(f'<article class="plan-card{" featured" if featured else ""}" data-price="{price}"><div class="plan-topline"><span class="plan-icon"><svg class="icon" aria-hidden="true"><use href="#i-{icon}"/></svg></span>{badge}</div><h3>{name}</h3><p>{description}</p><div class="plan-price"><strong>${price:.2f}</strong><span>/ month</span></div><span class="plan-bill-note">Billed monthly. Example pricing.</span><div class="plan-ram"><strong>{ram} GB<span>RAM</span></strong><span>{tag}</span></div><ul>{benefits}</ul><button class="button{" button-ghost" if not featured else ""}" data-config="minecraft" data-ram="{ram}">Choose {name} <svg class="icon" aria-hidden="true"><use href="#i-arrow-up-right"/></svg></button></article>')

# Public-domain geography, not a game texture.
def project(lon,lat):return (lon+180)/360*700,(82-lat)/150*310
geography=json.loads((ASSETS/'world.geojson').read_text());map_paths=[]
for feature in geography['features']:
    if feature['properties'].get('ADM0_A3')=='ATA':continue
    polygons=feature['geometry']['coordinates']
    if feature['geometry']['type']=='Polygon':polygons=[polygons]
    for polygon in polygons:
        if not polygon[0]:continue
        points=[project(*point[:2]) for point in polygon[0]]
        map_paths.append('M'+'L'.join(f'{x:.1f},{y:.1f}' for x,y in points)+'Z')
map_svg='''<svg viewBox="0 0 700 310" role="group" aria-label="Example network map. Select a server region."><defs><pattern id="map-dots" width="4.4" height="4.4" patternUnits="userSpaceOnUse"><circle cx="2.2" cy="2.2" r=".8" fill="#668846" opacity=".55"/></pattern><pattern id="map-grid" width="70" height="62" patternUnits="userSpaceOnUse"><path d="M70 0H0V62" fill="none" stroke="#b0c696" stroke-width=".4" opacity=".4"/></pattern></defs><rect width="700" height="310" fill="url(#map-grid)"/><g fill="url(#map-dots)">'''+''.join(f'<path d="{path}"/>' for path in map_paths)+'</g><path class="map-route" d="M200 89Q385 -20 551 166"/><path class="map-route" d="M366 66Q488 65 551 166"/><path class="map-route" d="M200 89Q283 4 366 66"/>'
for region,lon,lat,label in [('ashburn',-77.487,39.044,'ASHBURN'),('frankfurt',8.682,50.11,'FRANKFURT'),('singapore',103.82,1.352,'SINGAPORE')]:
    x,y=project(lon,lat);active=region=='singapore'
    map_svg+=f'<g class="map-pin{" active" if active else ""}" transform="translate({x:.1f} {y:.1f})" data-map-region="{region}" role="button" tabindex="0" aria-label="Select {label.title()} example region" aria-pressed="{str(active).lower()}"><rect x="-25" y="-24" width="50" height="60" fill="transparent"/><circle class="pin-glow" r="22"/><circle class="pin-ring" r="13"/><circle class="pin-core" r="5.5"/><text y="34">{label}</text></g>'
map_svg+='</svg>'

# Social preview contains only our original imagery and open-license typography.
font.flavor=None;font.save(ART/'brand-title.ttf')
social=Image.open(ART/'hero-world.png').convert('RGB');social=ImageOps.fit(social,(1200,630))
overlay=Image.new('RGBA',(1200,630),(10,31,17,110));social=Image.alpha_composite(social.convert('RGBA'),overlay).convert('RGB')
draw=ImageDraw.Draw(social);font_path=str(ART/'brand-title.ttf')
draw.text((62,65),'SPEEDY HOSTING',font=ImageFont.truetype(font_path,29),fill='#c7e79a')
draw.text((57,202),'YOUR NEXT',font=ImageFont.truetype(font_path,73),fill='#ffffff')
draw.text((59,290),'WORLD AWAITS.',font=ImageFont.truetype(font_path,63),fill='#ffffff')
draw.text((62,475),'INDEPENDENT GAME SERVER HOSTING',font=ImageFont.truetype(font_path,16),fill='#d5e4bd')
social.save(ROOT/'social-preview.jpg',quality=93,optimize=True)

licenses='''ARTWORK AND SOFTWARE CREDITS
Seven original AI-generated environment illustrations created for this project. No publisher cover art, logos, proprietary fonts, game textures or intentional recognizable proprietary characters are used. Generation is not a guarantee of legal clearance; review before commercial publication. Local files and hashes are recorded in assets/v4/artwork-manifest.json.
Game names are descriptive references to supported software, not part of the Speedy brand. This is an independent frontend concept, not an official or endorsed service.
NOT AN OFFICIAL MINECRAFT SERVICE. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.
Original transparent cursor vectors and authored 3D hardware geometry included.
Minecraft.net was a broad web-design reference only. Its proprietary artwork, logo, font files, game UI textures, written copy and business claims are not reused.
Natural Earth geography: public domain.
Phosphor Icons: MIT License.
'''+(ASSETS/'icons/LICENSE').read_text()
for file in ['archivo-black','noto-sans','ibm-plex-mono']:
    path=ASSETS/f'{file}-OFL.txt'
    if path.exists():licenses+=f'\n{file} Font License:\n'+path.read_text()
licenses+='\nThree.js License:\n'+(ASSETS/'v2/three-LICENSE.txt').read_text()
licenses=licenses.replace('--',' ')
js=(ROOT/'tools/site.js').read_text().replace('@@LOGO_JSON@@',json.dumps(standalone))
replacements={'@@FAVICON@@':favicon_uri,'@@FONTS@@':font_faces,'@@CSS@@':(ROOT/'tools/site.css').read_text(),'@@LICENSES@@':licenses,'@@SPRITE@@':sprite,'@@LOGO@@':logo,'@@MARK@@':mark,'@@HERO_IMAGE@@':uri(ART/'hero-world.webp','image/webp'),'@@COMMUNITY_IMAGE@@':uri(ART/'community-world.webp','image/webp'),'@@ENGINE_IMAGE@@':engine_uri,'@@GAMECARDS@@':'\n'.join(cards),'@@ART_CREDITS@@':'\n'.join(credits),'@@PLANS@@':'\n'.join(plan_html),'@@MAP@@':map_svg,'@@JS@@':js,'@@SCENE@@':(ASSETS/'v2/scene.min.js').read_text()}
for name in ['arrow','hand','text','move']:replacements[f'@@CURSOR_{name.upper()}@@']=uri(ASSETS/f'cursors/{name}.png','image/png')
page=(ROOT/'tools/site.html').read_text()
for token,value in replacements.items():page=page.replace(token,value)
assert not re.search(r'@@[A-Z_]+@@',page),'Unreplaced template token'
(ROOT/'index.html').write_text(page)
public=ROOT/'public';public.mkdir(exist_ok=True);(public/'index.html').write_text(page)
for name in ['speedy-logo.svg','speedy-logo-dark.svg','social-preview.jpg']:(public/name).write_bytes((ROOT/name).read_bytes())
print(f'Built standalone index.html: {len(page.encode())/1024:.0f} KB. Original voxel artwork only; independent branding; open-license typography.')
