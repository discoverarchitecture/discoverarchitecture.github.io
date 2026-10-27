const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const errs=[];
  const pg = await (await b.newContext({viewport:{width:1280,height:900}})).newPage();
  pg.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
  pg.on('console', m => { if (m.type()==='error' && !m.text().includes('zgo.at')) errs.push(m.text()); });
  const t = async (label, fn) => { try { await fn(); console.log('ok  ', label); } catch(e) { console.log('FAIL', label, e.message.split('\n')[0]); } };

  await pg.goto('http://localhost:8777/index.html', { waitUntil:'networkidle' });
  await t('buildings wall renders', async () => { if (await pg.$$eval('.t', e=>e.length) < 10) throw new Error('no tiles'); });
  await t('open a building', async () => { await pg.click('.t .open'); await pg.waitForTimeout(800); const n = await pg.textContent('#bName'); if (!n) throw new Error('no name'); await pg.keyboard.press('Escape'); });
  await t('switch to Books', async () => { await pg.click('#modeBooks'); await pg.waitForTimeout(1500); if (await pg.$$eval('.bt', e=>e.length) < 5 && await pg.$$eval('#table button', e=>e.length) < 5) throw new Error('no books'); });
  await t('switch to Documentaries', async () => { await pg.click('#modeFilms'); await pg.waitForTimeout(1200); if (await pg.$$eval('.ft', e=>e.length) < 10) throw new Error('no films'); });
  await t('genre filter narrows', async () => { await pg.click('.idea[data-shelf]'); await pg.waitForTimeout(600); const n = await pg.$$eval('.ft', e=>e.length); if (n===0 || n===46) throw new Error('did not narrow: '+n); });
  await t('search in films', async () => { await pg.click('.idea[aria-pressed="true"]'); await pg.waitForTimeout(400); await pg.fill('#q','gaudi'); await pg.waitForTimeout(700); const n=await pg.$$eval('.ft',e=>e.length); if (n<1||n>5) throw new Error('search gave '+n); await pg.fill('#q',''); await pg.waitForTimeout(500); });
  await t('back to Buildings', async () => { await pg.click('#modeBuildings'); await pg.waitForTimeout(900); if (await pg.$$eval('.t', e=>e.length) < 10) throw new Error('buildings gone'); });
  await t('deep link #documentaries', async () => { await pg.goto('http://localhost:8777/index.html#documentaries',{waitUntil:'networkidle'}); await pg.waitForTimeout(1500); if (await pg.getAttribute('#modeFilms','aria-pressed') !== 'true') throw new Error('not on films'); });
  await t('deep link #film:<id>', async () => { await pg.goto('http://localhost:8777/index.html#film:my-architect',{waitUntil:'networkidle'}); await pg.waitForTimeout(1800); const n=await pg.textContent('#bName'); if (!/Architect/i.test(n)) throw new Error('got '+n); });
  await t('deep link #book:<id> still works', async () => { await pg.goto('http://localhost:8777/index.html#book:form-space-and-order',{waitUntil:'networkidle'}); await pg.waitForTimeout(1800); const n=await pg.textContent('#bName'); if (!/Form/i.test(n)) throw new Error('got '+n); });
  await t('#filter still opens', async () => { await pg.goto('http://localhost:8777/index.html#filter',{waitUntil:'networkidle'}); await pg.waitForTimeout(900); if (await pg.getAttribute('#filters','hidden') !== null) throw new Error('filters closed'); });
  console.log(errs.length ? '\nCONSOLE ERRORS:\n'+[...new Set(errs)].join('\n') : '\nno console errors');
  await b.close();
})();
