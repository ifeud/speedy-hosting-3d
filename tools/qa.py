from pathlib import Path
from urllib.parse import urlparse
import json, hashlib, re
from PIL import Image
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent.parent
OUTPUT=ROOT/'.qa';OUTPUT.mkdir(exist_ok=True)
report={'checks':[], 'viewports':[], 'errors':[]}

def check(name, condition):
    assert condition, name
    report['checks'].append(name)

# Source-level verification, including the provenance of every game image.
markup=(ROOT/'index.html').read_text()
soup=BeautifulSoup(markup,'html.parser')
ids=[tag['id'] for tag in soup.select('[id]')]
check('Unique HTML IDs',len(ids)==len(set(ids)))
check('One semantic H1',len(soup.find_all('h1'))==1)
for use in soup.find_all('use'):
    href=use.get('href','');check(f'SVG reference {href}',href.startswith('#') and href[1:] in ids)
for script in soup.select('script[type="application/ld+json"]'):json.loads(script.string)
check('Six supported game cards',len(soup.select('.game-card'))==6)
check('All page images embedded',all(image.get('src','').startswith('data:') for image in soup.find_all('img')))
manifest=json.loads((ROOT/'assets/v4/artwork-manifest.json').read_text())
check('No publisher artwork is used',manifest['publisher_assets_used'] is False)
check('No publisher image hosts are embedded','steamstatic.com' not in markup and 'minecraft.net/content/dam' not in markup)
for game,asset in manifest['games'].items():
    check(f'{game}: original illustration record',asset['type']=='original_ai_generated' and asset['not_game_screenshot'] is True)
    digest=hashlib.sha256((ROOT/asset['local_file']).read_bytes()).hexdigest()
    check(f'{game}: original asset hash matches research record',digest==asset['sha256'])
for name in ['arrow','hand','text','move']:
    image=Image.open(ROOT/f'assets/cursors/{name}.png').convert('RGBA')
    check(f'{name} cursor is 24px and transparent',image.size==(24,24) and image.getchannel('A').getextrema()==(0,255))

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    errors=[];network=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.on('request',lambda request:network.append(request.url))
    page.goto('http://127.0.0.1:3000/',wait_until='networkidle')
    page.evaluate('document.fonts.ready')
    check('All six games visible initially',page.locator('.game-card:visible').count()==6)
    check('No floating hero cards or pills',page.locator('.hero .server-float,.hero .world-label,.hero .online-pill').count()==0)
    check('No double-hyphen punctuation in visible copy','--' not in page.locator('body').inner_text())
    check('Headline uses open-license Archivo Black','Archivo Black' in page.locator('h1').evaluate('e=>getComputedStyle(e).fontFamily'))
    check('Buttons use Noto Sans','Noto Sans' in page.locator('button').first.evaluate('e=>getComputedStyle(e).fontFamily'))
    check('Inputs use Noto Sans','Noto Sans' in page.locator('input').first.evaluate('e=>getComputedStyle(e).fontFamily'))
    check('Console uses IBM Plex Mono','IBM Plex Mono' in page.locator('.console-window').evaluate('e=>getComputedStyle(e).fontFamily'))
    check('Body arrow hotspot is correct','3 2, default' in page.locator('body').evaluate('e=>getComputedStyle(e).cursor'))
    check('Button hand hotspot is correct','10 3, pointer' in page.locator('button').first.evaluate('e=>getComputedStyle(e).cursor'))
    check('Input text cursor hotspot is correct','12 12, text' in page.locator('#hero-query').evaluate('e=>getComputedStyle(e).cursor'))

    page.locator('#hero-query').fill('Valheim');page.locator('#hero-search button').click()
    check('Hero search forwards to catalog',page.locator('.game-card:visible').count()==1 and page.locator('.game-card:visible').get_attribute('data-game')=='valheim')
    page.locator('#game-search').fill('mc')
    check('Minecraft alias search works',page.locator('.game-card:visible').count()==1)
    page.locator('#game-search').fill('not-a-real-game')
    check('Empty search has a useful recovery',page.locator('#empty-games').is_visible())
    page.locator('#reset-search').click()
    check('Search reset restores every game',page.locator('.game-card:visible').count()==6)
    page.locator('[data-filter="sandbox"]').click()
    check('Sandbox filter works',page.locator('.game-card:visible').count()==3)
    page.locator('[data-filter="all"]').click()
    page.locator('h2').first.click();page.keyboard.press('/')
    check('Keyboard search shortcut works',page.locator('#game-search').evaluate('e=>e===document.activeElement'))

    page.locator('[data-billing="yearly"]').click()
    check('Annual pricing computes correctly',page.locator('.plan-price strong').first.inner_text()=='$4.80')
    page.locator('.plan-card.featured [data-config]').click()
    check('Annual quote computes correctly',page.locator('#quote-price').inner_text()=='$115.20')
    page.locator('#config-billing').select_option('monthly')
    page.locator('#promo-code').fill('FIRST20');page.locator('#apply-promo').click()
    check('Monthly first-payment promo works',page.locator('#quote-price').inner_text()=='$9.60')
    page.locator('#config-game').select_option('ark')
    check('Game requirements enforce minimum RAM',page.locator('input[name="ram"][value="4"]').is_disabled() and page.locator('input[name="ram"][value="8"]').is_disabled())
    check('ARK example quote is consistent',page.locator('#quote-price').inner_text()=='$19.20')
    page.locator('#config-billing').select_option('yearly')
    check('Annual discount does not stack with promo',page.locator('#quote-price').inner_text()=='$230.40')
    page.locator('#config-form button[type="submit"]').click()
    check('Quote review renders',page.locator('#quote-result').is_visible())
    with page.expect_download() as event:page.locator('#download-quote').click()
    check('Local quote download works',event.value.suggested_filename=='speedy-example-quote.txt')
    page.locator('#config-dialog [data-close]').click()
    check('Modal closes cleanly',not page.locator('body').evaluate('e=>e.classList.contains("modal-open")'))

    page.locator('[data-region="frankfurt"]').click()
    check('Region picker updates text',page.locator('#location-name').inner_text()=='Frankfurt, Germany')
    check('No invented ping figure is displayed',page.locator('#location-ping').inner_text()=='Frankfurt')
    page.locator('#location-deploy').click()
    check('Region choice reaches configurator',page.locator('#config-region').input_value()=='frankfurt')
    page.locator('#config-dialog [data-close]').click()

    for _ in range(10):page.locator('#server-toggle').click()
    page.locator('#server-restart').click();page.wait_for_timeout(1400)
    check('Demo server controls recover after restart','Running' in page.locator('#panel-status').inner_text())
    page.locator('[data-panel="files"]').click()
    check('Files tab works',page.locator('#panel-files').is_visible())
    with page.expect_download() as event:page.locator('#download-properties').click()
    check('Sample config download works',event.value.suggested_filename=='server.properties')
    page.locator('[data-panel="backups"]').click();page.locator('#make-backup').click()
    check('Backup demonstration works','Manual adventure backup' in page.locator('#backup-list').inner_text())
    page.locator('[data-panel="console"]').click()

    page.locator('#engine-canvas').scroll_into_view_if_needed()
    page.wait_for_timeout(250)
    check('Real 3D hardware initializes',page.evaluate('Boolean(window.SpeedyScene)'))
    before=page.evaluate('window.SpeedyScene.scene.children[0].rotation.y')
    page.locator('#engine-canvas').focus();page.keyboard.press('ArrowRight');page.wait_for_timeout(300)
    check('3D hardware supports keyboard rotation',abs(page.evaluate('window.SpeedyScene.scene.children[0].rotation.y')-before)>.05)
    box=page.locator('#engine-canvas').bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2
    before=page.evaluate('window.SpeedyScene.scene.children[0].rotation.y')
    page.mouse.move(x,y);page.mouse.down()
    check('Drag cursor switches to grabbing','grabbing' in page.locator('#engine-canvas').evaluate('e=>getComputedStyle(e).cursor'))
    page.mouse.move(x+65,y,steps=5);page.mouse.up();page.wait_for_timeout(300)
    check('3D pointer rotation works',abs(page.evaluate('window.SpeedyScene.scene.children[0].rotation.y')-before)>.08)
    page.locator('#reset-engine').click()

    page.locator('#support-open').click()
    page.locator('#support-form [name="name"]').fill('Player One')
    page.locator('#support-form [name="email"]').fill('player@example.com')
    page.locator('#support-form [name="message"]').fill('Which game plan should I choose for my friends?')
    page.locator('#support-form [type="submit"]').click()
    check('Local support request preview works',page.locator('#support-result').is_visible())
    page.locator('#support-dialog [data-close]').click()
    page.locator('#catalog-support').click()
    check('Catalog support link is functional',page.locator('#support-dialog').is_visible())
    page.locator('#support-dialog [data-close]').click()
    page.locator('[data-policy="privacy"]').click()
    check('Privacy dialog works','privacy' in page.locator('#policy-title').inner_text().lower())
    page.locator('#policy-dialog [data-close]').click()
    page.locator('#client-open').click();page.locator('#try-panel').click()
    check('Client preview leads to panel',not page.locator('#client-dialog').is_visible())
    page.locator('#artwork-open').click()
    check('Every game illustration has a generation credit',page.locator('.artwork-sources article').count()==6)
    page.locator('#artwork-dialog [data-close]').click()
    with page.expect_download() as event:page.locator('#download-logo').click()
    check('Transparent logo download works',event.value.suggested_filename=='speedy-logo.svg')

    for width in [320,360,390,600,768,900,1024,1280,1440]:
        page.set_viewport_size({'width':width,'height':900})
        page.goto('http://127.0.0.1:3000/',wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        dims=page.evaluate('({page:document.body.scrollWidth,viewport:innerWidth})')
        check(f'No horizontal overflow at {width}px',dims['page']<=width)
        report['viewports'].append({'width':width,**dims})
        if width in [320,390]:
            count=page.locator('h1').evaluate('e=>{const r=document.createRange();r.selectNodeContents(e);return [...r.getClientRects()].filter(x=>x.width>0).length}')
            check(f'Hero headline retains two lines at {width}px',count==2)
            check(f'Mobile paragraph spacing is correct at {width}px','longer. Independent' in page.locator('.hero-content>p').inner_text())
        if width==390:
            page.locator('#mobile-toggle').click();check('Mobile navigation opens',page.locator('#main-nav').is_visible())
            page.locator('#games-menu-button').click();page.locator('#games-menu [data-config="palworld"]').click()
            check('Mobile game menu opens configuration',page.locator('#config-dialog').is_visible())
            page.locator('#config-dialog [data-close]').click()

    # Capture every lazy image before creating the actual full-page deliverables.
    for width,height,name in [(1440,1000,'desktop'),(390,844,'mobile')]:
        page.set_viewport_size({'width':width,'height':height})
        page.goto('http://127.0.0.1:3000/',wait_until='networkidle');page.evaluate('document.fonts.ready')
        for y in range(0,int(page.evaluate('document.body.scrollHeight')),800):
            page.evaluate('(y)=>window.scrollTo(0,y)',y);page.wait_for_timeout(45)
        page.evaluate('window.scrollTo(0,0)');page.wait_for_timeout(200)
        check(f'All original illustrations load for {name}',page.locator('.game-card img').evaluate_all('images=>images.every(i=>i.complete&&i.naturalWidth>0)'))
        page.screenshot(path=str(ROOT/f'speedy-{name}.png'),full_page=True,animations='disabled')
        page.screenshot(path=str(OUTPUT/f'final-{name}-top.png'),animations='disabled')

    external=[url for url in network if not url.startswith(('http://127.0.0.1:3000','data:','blob:'))]
    check('No external runtime asset requests',not external)
    check('No browser JavaScript errors',not errors)
    report['errors']=errors
    browser.close()

    mobile=p.chromium.launch(headless=True,args=['--no-sandbox'])
    context=mobile.new_context(**p.devices['iPhone 13'])
    touch=context.new_page();touch.goto('http://127.0.0.1:3000/',wait_until='networkidle')
    check('Touch devices retain native cursor behavior',not touch.locator('body').evaluate('e=>getComputedStyle(e).cursor').startswith('url('))
    mobile.close()

report['status']='passed'
(OUTPUT/'qa-report-v4.json').write_text(json.dumps(report,indent=2))
print(f'Passed {len(report["checks"])} checks across {len(report["viewports"])} viewport widths. Original-art verification, font, cursor, interaction, 3D and full-page screenshot tests complete.')
