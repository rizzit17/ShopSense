"""Optional browser integration check. Requires Playwright + installed Edge.
Start the API on :8000 and Vite on :5173 before running this script.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tmp/browser'; OUT.mkdir(parents=True,exist_ok=True)
BASE_URL=os.environ.get('SHOPSENSE_URL','http://127.0.0.1:5173/')
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, channel='msedge')
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    errors=[];warnings=[]
    page.on('pageerror',lambda err: errors.append(str(err)))
    page.on('console',lambda msg: warnings.append(msg.text) if msg.type in ['warning','error'] else None)
    page.goto(BASE_URL,wait_until='networkidle')
    page.get_by_role('heading',name='Every purchase tells a story.').wait_for()
    assert page.locator('.recharts-scatter-symbol').count()==4338
    card=page.get_by_role('button',name='Inspect High-Value Champions')
    card.focus();card.press('Enter');assert card.get_attribute('aria-pressed')=='true'
    assert page.get_by_text('Inspecting Tier 1: High Value').is_visible()
    page.get_by_role('button',name='Experiments',exact=True).click()
    assert page.get_by_role('cell',name='0.3373',exact=True).is_visible()
    page.get_by_role('button',name='RFM comparison',exact=True).click()
    assert page.get_by_text('Median Recency / days',exact=True).is_visible()
    page.get_by_role('button',name='Selection',exact=True).click()
    page.get_by_label('1. Days Since Last Purchase (Recency)').fill('5')
    page.get_by_label('2. Total Completed Orders (Frequency)').fill('15')
    page.get_by_label('3. Total Spending in GBP (£) (Monetary)').fill('5000')
    page.get_by_role('button',name='Discover My Segment').click()
    page.locator('#predictor').get_by_role('heading',name='High-Value Champions',exact=True).wait_for()
    page.get_by_role('button',name='Active Regular (18d, 2 orders, £480)').click()
    assert page.get_by_text('Ready to Infer Shopping Segment').is_visible()
    page.get_by_label('3. Total Spending in GBP (£) (Monetary)').fill('900000')
    page.get_by_role('button',name='Discover My Segment').click()
    page.get_by_text('Training Distribution Outlier Alert:',exact=True).wait_for()
    page.screenshot(path=str(OUT/'desktop.png'),full_page=True)
    page.evaluate('window.scrollTo(0,0)')
    page.wait_for_timeout(300)
    page.screenshot(path=str(OUT/'desktop-top.png'))
    for width in [390,768]:
        page.set_viewport_size({'width':width,'height':844})
        page.wait_for_timeout(350)
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), f'Overflow at {width}px'
        page.screenshot(path=str(OUT/f'responsive-{width}.png'),full_page=True)
    offline=browser.new_page(viewport={'width':390,'height':844})
    offline.route('**/api/**',lambda route:route.abort())
    offline.goto(BASE_URL)
    offline.get_by_role('heading',name='Analytics unavailable').wait_for()
    assert offline.get_by_role('button',name='Retry connection').is_visible()
    assert offline.locator('.recharts-wrapper').count()==0
    offline.screenshot(path=str(OUT/'unavailable.png'))
    browser.close()
    (OUT/'results.json').write_text(json.dumps({'page_errors':errors,'console_warnings_or_errors':warnings,'viewports':[1440,390,768],'pca_points':4338,'checks':'prediction, presets, outlier, segment selection, evaluation tabs, overflow, API unavailable'},indent=2))
    assert not errors, errors
    assert not warnings, warnings
    print(json.dumps({'page_errors':errors,'console_warnings_or_errors':warnings}))
