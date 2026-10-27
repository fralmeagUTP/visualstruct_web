"""Bounded, private-session layout/keyboard probe for the stack pilot."""
from __future__ import annotations
import argparse, json, tempfile, threading, sys, time, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.config import Config
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--report", required=True); parser.add_argument("--verify", action="store_true"); parser.add_argument("--flow", action="store_true"); parser.add_argument("--reflow", action="store_true"); args=parser.parse_args()
    started=time.monotonic(); results=[]
    with tempfile.TemporaryDirectory(prefix="vs-stack-residual-") as cache:
        class PrivateConfig(Config):
            APP_ENV="testing"
            TESTING=True
            SECRET_KEY="isolated-layout-probe"
            SESSION_CACHE_DIR=cache
            SESSION_FILE_DIR=cache
        app=create_app(PrivateConfig); server=make_server("127.0.0.1",0,app)
        thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        try:
            with sync_playwright() as pw:
                browser=pw.chromium.launch(headless=True)
                for width,height in [(1366,768),(768,1024),(390,844)]+([(683,384)] if args.reflow else []):
                    context=browser.new_context(viewport={"width":width,"height":height}, reduced_motion="reduce")
                    page=context.new_page(); page.set_default_timeout(10000)
                    page.goto(f"http://127.0.0.1:{server.server_port}/sequential/stack",wait_until="networkidle")
                    measure=page.evaluate("""() => {
                      const ids=['operation-select','seq-sim-execute','seq-sim-play','seq-sim-step','visual-state','op-pseudocode'];
                      const rects=Object.fromEntries(ids.map(id=>{const e=document.getElementById(id),r=e.getBoundingClientRect();return [id,{top:r.top,bottom:r.bottom,left:r.left,right:r.right,visible:!!e.getClientRects().length}]}));
                      const tab=document.querySelector('[data-seq-tab="visual"]');
                      return {width:innerWidth,height:innerHeight,overflow:document.documentElement.scrollWidth>innerWidth+1,rects,tabRole:tab.getAttribute('role'),tabIndex:tab.tabIndex,tabBarVisible:!!tab.getClientRects().length};
                    }""")
                    if width<=800:
                        before=page.evaluate("JSON.stringify({state:document.querySelector('#visual-state').innerHTML,code:document.querySelector('#op-pseudocode').textContent,operation:document.querySelector('#operation-select').value})")
                        visual=page.locator('[data-seq-tab="visual"]'); visual.focus(); page.keyboard.press("ArrowRight")
                        measure['keyboardCodeSelected']=page.locator('[data-seq-tab="code"]').get_attribute('aria-selected')=='true'
                        measure['keyboardFocusCode']=page.evaluate("document.activeElement.dataset.seqTab==='code'")
                        measure['codeVisibleAfterKeyboard']=page.locator('#seq-code-region').is_visible()
                        measure['singleTabStop']=page.locator('[role="tab"][tabindex="0"]').count()==1
                        page.keyboard.press("Home")
                        measure['homeSelectsVisual']=visual.get_attribute('aria-selected')=='true'
                        page.keyboard.press("End")
                        measure['endSelectsCode']=page.locator('[data-seq-tab="code"]').get_attribute('aria-selected')=='true'
                        page.keyboard.press("ArrowLeft")
                        measure['leftSelectsVisual']=visual.get_attribute('aria-selected')=='true'
                        after=page.evaluate("JSON.stringify({state:document.querySelector('#visual-state').innerHTML,code:document.querySelector('#op-pseudocode').textContent,operation:document.querySelector('#operation-select').value})")
                        measure['contentUnchanged']=before==after
                        if args.verify:
                            assert measure['tabRole']=='tab'
                            assert all(measure[key] for key in ['keyboardCodeSelected','keyboardFocusCode','codeVisibleAfterKeyboard','singleTabStop','homeSelectsVisual','endSelectsCode','leftSelectsVisual','contentUnchanged'])
                    measure['primaryContrast']=page.evaluate("""() => {
                      const parse=s=>(s.match(/[0-9.]+/g)||[]).map(Number);
                      const luminance=c=>c.slice(0,3).map(x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4}).reduce((v,x,i)=>v+x*[.2126,.7152,.0722][i],0);
                      return ['operation-select','seq-sim-execute','seq-step-mode','op-pseudocode'].map(id=>{
                        const el=document.getElementById(id),style=getComputedStyle(el);let bgEl=el,bg;
                        while(bgEl){bg=parse(getComputedStyle(bgEl).backgroundColor);if(bg.length===3 || bg[3]>0)break;bgEl=bgEl.parentElement;}
                        const a=luminance(parse(style.color)),b=luminance(bg||[255,255,255]);
                        return {id,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
                      });
                    }""")
                    if args.verify:
                        assert not measure['overflow']
                        assert all(item['ratio']>=4.5 for item in measure['primaryContrast']),measure['primaryContrast']
                    if width>1100:
                        measure['initialFunctionVisible']=page.evaluate("""() => {const code=document.querySelector('#op-pseudocode'),index=document.querySelector('.seq-function-link.is-active')?.dataset.line,target=code.querySelector(`.code-line[data-line="${index}"]`);if(!target)return false;const a=code.getBoundingClientRect(),b=target.getBoundingClientRect();return b.top>=a.top && b.bottom<=a.bottom && scrollY===0;}""")
                        if args.verify: assert measure['initialFunctionVisible']
                    if width>1100 and args.verify:
                        assert all(measure['rects'][key]['visible'] and measure['rects'][key]['top']>=0 and measure['rects'][key]['bottom']<=height for key in ['operation-select','seq-sim-execute','visual-state','op-pseudocode']), measure
                    if width<=800:
                        page.evaluate("window.scrollTo(0, 1100)")
                        page.wait_for_timeout(100)
                        measure['sticky']=page.evaluate("""() => {const p=document.querySelector('.seq-prepare').getBoundingClientRect(),t=document.querySelector('.sequential-mobile-tabs').getBoundingClientRect(),b=document.querySelector('#seq-sim-execute').getBoundingClientRect();return {prepareTop:p.top,prepareBottom:p.bottom,tabTop:t.top,buttonTop:b.top,buttonBottom:b.bottom};}""")
                        if args.verify:
                            assert abs(measure['sticky']['prepareTop'])<=1
                            assert measure['sticky']['tabTop']>=measure['sticky']['prepareBottom']-1
                            assert measure['sticky']['buttonTop']>=0 and measure['sticky']['buttonBottom']<=height
                        page.evaluate("window.scrollTo(0, 0)")
                    page.screenshot(path=str(Path(args.report).with_name(f"{Path(args.report).stem}-{width}.png")),full_page=False)
                    if args.flow:
                        page.evaluate("window.scrollTo(0,0); const e=document.querySelector('#seq-predictions-enabled'); e.checked=false; e.dispatchEvent(new Event('change',{bubbles:true}));")
                        page.locator('#field-value').fill('7')
                        page.locator('#seq-step-mode').click()
                        with page.expect_response(lambda response: response.url.endswith('/sequential/stack/operate')) as pending:
                            page.locator('#seq-sim-execute').click()
                        response=pending.value.json(); assert response['success']
                        page.wait_for_function("/Paso: 0\/([1-9][0-9]*)/.test(document.querySelector('#seq-sim-counter').textContent)")
                        page.locator('#seq-sim-step').click()
                        page.locator('#seq-sim-prev').click()
                        assert re.search(r'Paso:\s*0/',page.locator('#seq-sim-counter').inner_text())
                        for _ in range(300):
                            match=re.search(r'Paso:\s*(\d+)\s*/\s*(\d+)',page.locator('#seq-sim-counter').inner_text())
                            assert match
                            if match[1]==match[2]:break
                            page.locator('#seq-sim-step').click()
                        else:raise AssertionError('Manual trace exceeded bounded frame count')
                        final=page.locator('#visual-state').inner_text()
                        page.locator('#seq-sim-prev').click(); page.locator('#seq-sim-step').click()
                        assert page.locator('#visual-state').inner_text()==final
                        page.locator('#seq-step-mode').click()
                        with page.expect_response(lambda response: response.url.endswith('/sequential/stack/operate')) as pending:
                            page.locator('#seq-sim-execute').click()
                        duplicate=pending.value.json(); assert duplicate['success']
                        page.locator('#operation-select').select_option('desapilar')
                        with page.expect_response(lambda response: response.url.endswith('/sequential/stack/operate')) as pending:
                            page.locator('#seq-sim-execute').click()
                        popped=pending.value.json(); assert popped['success']
                        before_panels=page.locator('#visual-state').inner_text()+page.locator('#seq-sim-counter').inner_text()
                        panel_toggle=page.locator('#seq-understand-title > button')
                        panel_toggle.click(); panel_toggle.click()
                        assert page.locator('#visual-state').inner_text()+page.locator('#seq-sim-counter').inner_text()==before_panels
                        measure['panelsPreserveVisualAndCursor']=True
                        measure['reducedMotionRequested']=page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
                        measure['operation_flow']={'apilar':True,'duplicate_apilar':True,'desapilar':True,'step_previous_repeat':True,'final_replay_same_visual_text':True,'play_pause':'not exposed by current approved pilot; no hidden control forced'}
                    results.append(measure); context.close()
                browser.close()
        finally:
            server.shutdown(); thread.join(timeout=5)
    report={"schema":"stack-residual-layout/v1","elapsed_seconds":time.monotonic()-started,"private_sessions":True,"viewports":results}
    target=Path(args.report); target.parent.mkdir(parents=True,exist_ok=True); target.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report))
if __name__=="__main__": main()
