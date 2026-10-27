import json
from pathlib import Path
from playwright.sync_api import sync_playwright
E=Path('openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-create-insert-baseline-low');B=E/'browser';B.mkdir(exist_ok=True)
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True);page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto('http://127.0.0.1:5051/hash/hash_table');page.wait_for_selector('#hash-operation-select')
    def run(op,values):
        page.select_option('#hash-operation-select',op)
        for k,v in values.items():page.fill('#hash-field-'+k,str(v))
        with page.expect_response(lambda r:'/hash/hash_table/operate' in r.url and r.request.method=='POST') as response:page.click('#hash-sim-play')
        return response.value.json()
    results=[run('create_table',{'capacity':3})]
    for key in (1,4,7,10):results.append(run('insert',{'key':key,'value':key*10}))
    mains=page.locator('.didactic-history-main').evaluate_all("els => els.map(el => Array.from(el.querySelectorAll('.code-line')).map(x => x.textContent).join('\\n') || el.textContent)");(B/'main-visible.c').write_text(mains[-1] if mains else '',encoding='utf-8');page.screenshot(path=str(B/'collision-load.png'),full_page=True)
    report={'responses':results,'page_errors':errors,'five_sections':page.locator('.hash-stage').count(),'main_dom_count':len(mains),'main_download_status':page.request.get('http://127.0.0.1:5051/help/source/hash_table/main').status,'console_text':page.locator('#hash-printf-console').inner_text()}
    page.reload();report['reload_main_dom_count']=page.locator('.didactic-history-main').count();(B/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');browser.close()
