from playwright.sync_api import sync_playwright
from pathlib import Path
import json
root=Path(__file__).resolve().parent.parent
(root/'.qa').mkdir(exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
 errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:requests.append(r.url))
 page.goto('http://127.0.0.1:3000',wait_until='networkidle')
 page.evaluate('document.fonts.ready')
 page.screenshot(path=str(root/'.qa/desktop-top.png'),animations='disabled')
 page.screenshot(path=str(root/'.qa/desktop-full.png'),full_page=True,animations='disabled')
 print('body height',page.evaluate('document.body.scrollHeight'))
 assert page.locator('.server-float,.world-label').count()==0
 assert '--' not in page.locator('body').inner_text()
 assert page.evaluate('getComputedStyle(document.body).cursor.startsWith("url(")')
 print('3D scene initialized:',page.evaluate('Boolean(window.SpeedyScene)'))
 print('initial games',page.locator('.game-card:visible').count())
 page.locator('[data-filter="survival"]').click();assert page.locator('.game-card:visible').count()==6
 page.locator('#game-search').fill('rust');assert page.locator('.game-card:visible').count()==1
 page.locator('#game-search').fill('not-a-game');assert page.locator('#empty-games').is_visible()
 page.locator('#reset-search').click();assert page.locator('.game-card:visible').count()==4
 page.locator('#show-all-games').click();assert page.locator('.game-card:visible').count()==6
 page.locator('#show-all-games').click();assert page.locator('.game-card:visible').count()==4
 page.locator('[data-billing="yearly"]').click();assert page.locator('.plan-price strong').first.inner_text()=='$4.80'
 page.locator('.plan-card.featured [data-config]').click()
 assert page.locator('#config-dialog').is_visible()
 assert page.locator('#quote-price').inner_text()=='$115.20'
 page.locator('#config-billing').select_option('monthly')
 page.locator('#promo-code').fill('FIRST20');page.locator('#apply-promo').click()
 assert page.locator('#quote-price').inner_text()=='$9.60'
 page.locator('#config-game').select_option('ark')
 assert page.locator('#quote-price').inner_text()=='$19.20'
 assert page.locator('input[name="ram"][value="4"]').is_disabled()
 page.screenshot(path=str(root/'.qa/configurator.png'),animations='disabled')
 page.locator('#config-form button[type="submit"]').click()
 assert page.locator('#quote-result').is_visible()
 with page.expect_download() as download:
  page.locator('#download-quote').click()
 print('quote download',download.value.suggested_filename)
 page.locator('#config-dialog [data-close]').click()
 page.locator('[data-region="frankfurt"]').click();assert page.locator('#location-name').inner_text()=='Frankfurt, Germany'
 for i in range(10):page.locator('#server-toggle').click()
 page.locator('#server-restart').click();page.wait_for_timeout(1500)
 assert 'Running' in page.locator('#panel-status').inner_text()
 page.locator('[data-panel="files"]').click();assert page.locator('#panel-files').is_visible()
 with page.expect_download() as download:
  page.locator('#download-properties').click()
 print('properties download',download.value.suggested_filename)
 page.locator('[data-panel="backups"]').click();page.locator('#make-backup').click()
 assert 'Manual adventure backup' in page.locator('#backup-list').inner_text()
 page.locator('#support-open').click()
 page.locator('#support-form [name="name"]').fill('Player One')
 page.locator('#support-form [name="email"]').fill('player@example.com')
 page.locator('#support-form [name="message"]').fill('Can you help me choose a game server?')
 page.locator('#support-form [type="submit"]').click();assert page.locator('#support-result').is_visible()
 page.locator('#support-dialog [data-close]').click()
 page.locator('[data-policy="privacy"]').click();assert page.locator('#policy-title').inner_text()=='Privacy, simply put.'
 page.locator('#policy-dialog [data-close]').click()
 page.locator('#client-open').click();page.locator('#try-panel').click();assert not page.locator('#client-dialog').is_visible()
 page.locator('[data-panel="console"]').click()
 with page.expect_download() as download:
  page.locator('#download-logo').click()
 print('logo download',download.value.suggested_filename)
 print('errors',errors)
 print('external requests',[r for r in requests if not r.startswith(('http://127.0.0.1:3000','data:','blob:'))])
 assert not errors
 for width in [320,360,390,600,768,1024,1440]:
  page.set_viewport_size({'width':width,'height':900})
  page.goto('http://127.0.0.1:3000',wait_until='networkidle')
  page.evaluate('document.fonts.ready')
  overflow=page.evaluate('({body:document.body.scrollWidth,window:innerWidth})')
  print('viewport',width,'overflow',overflow)
  assert overflow['body']<=width, 'Horizontal overflow'
  if width==390:
   page.screenshot(path=str(root/'.qa/mobile-top.png'),animations='disabled')
   page.screenshot(path=str(root/'.qa/mobile-full.png'),full_page=True,animations='disabled')
   page.locator('#mobile-toggle').click();assert page.locator('#main-nav').is_visible()
   page.locator('#games-menu-button').click();assert page.locator('#games-menu').is_visible()
   page.locator('#games-menu [data-config="palworld"]').click();assert page.locator('#config-dialog').is_visible()
   page.screenshot(path=str(root/'.qa/mobile-config.png'),animations='disabled')
   page.locator('#config-dialog [data-close]').click()
 print('All checks passed.')
 browser.close()
