import { chromium } from 'playwright';
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1200, height: 1000 } });
await p.goto('file:///Users/kilo/CLAUDE%20CODE%20PARENT/Writers%20Daily%20Practice/writers-routines/writing-routines-compared/index.html', { waitUntil: 'networkidle' });
await p.waitForTimeout(500);
await p.screenshot({ path: 'comparison.png' });
await b.close();
console.log('shot taken');
