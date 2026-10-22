async (page) => {
  await page.setViewportSize({width:1440,height:958});
  await page.goto('http://127.0.0.1:8766/indus-findings-2026-10-22.html');
  await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));});
  const checks=[];
  for(let i=0;i<24;i++){
    await page.evaluate(i=>window.showSlide(i),i);
    const check=await page.evaluate(()=>{
      const s=document.querySelector('.slide.active');
      const footer=s.querySelector('footer').getBoundingClientRect();
      const body=s.querySelector('.body');
      const children=[...body.querySelectorAll('p,figure,table,.wide-callout,.small-callout,.stat-banner,.status,.end-line')];
      const bottom=children.filter(e=>!e.closest('.cover-art')).map(e=>({text:e.textContent.slice(0,100),bottom:e.getBoundingClientRect().bottom}));
      const horizontal=[...s.querySelectorAll('*')].filter(e=>e.scrollWidth>e.clientWidth+3&&e.clientWidth>0&&!['IMG'].includes(e.tagName)).map(e=>({class:e.className,extra:e.scrollWidth-e.clientWidth}));
      return {slide: Number(s.id.split('-')[1]),footerTop:footer.top,footerCollisions:s.classList.contains('cover')?[]:bottom.filter(e=>e.bottom>footer.top-8),horizontal};
    });
    checks.push(check);
    await page.screenshot({path:`output/playwright/indus-deck/slide-${String(i+1).padStart(2,'0')}.png`});
  }
  await page.getByRole('button',{name:'Previous slide',exact:true}).click();
  const previous=await page.locator('#counter').innerText();
  await page.keyboard.press('Home');
  const home=await page.locator('#counter').innerText();
  await page.keyboard.press('ArrowRight');
  const arrow=await page.locator('#counter').innerText();
  await page.getByRole('button',{name:'Overview',exact:true}).click();
  await page.locator('#overview button[data-slide="8"]').click();
  const overview=await page.locator('#counter').innerText();
  await page.setViewportSize({width:390,height:844});
  const mobile=[];
  for(let i=0;i<24;i++){
    await page.evaluate(i=>window.showSlide(i),i);
    mobile.push(await page.evaluate(()=>({slide:document.querySelector('.slide.active').id,width:document.documentElement.scrollWidth,viewport:innerWidth})));
    if([0,4,10,17,19,23].includes(i))await page.screenshot({path:`output/playwright/indus-deck/mobile-${i+1}.png`,fullPage:true});
  }
  await page.setViewportSize({width:1440,height:958});
  await page.emulateMedia({media:'print'});
  const print=await page.evaluate(()=>({visible:[...document.querySelectorAll('.slide')].filter(e=>getComputedStyle(e).display!=='none').length,slides:[...document.querySelectorAll('.slide')].map(e=>({width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height}))}));
  await page.pdf({path:'output/playwright/indus-deck/print-check.pdf',printBackground:true,preferCSSPageSize:true});
  await page.emulateMedia({media:'screen'});
  await page.evaluate(()=>showSlide(0));
  return {checks,controls:{previous,home,arrow,overview},mobile,print};
}
