// Exercise rendered controls against the installed theme, including mobile use.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { chromium } = require('playwright');

const root = path.resolve(process.argv[2]);
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2' };
const server = http.createServer((request, response) => {
  const url = new URL(request.url, 'http://localhost');
  const file = path.resolve(root, '.' + decodeURIComponent(url.pathname));
  if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
    response.writeHead(404).end();
    return;
  }
  response.setHeader('Content-Type', types[path.extname(file)] || 'application/octet-stream');
  fs.createReadStream(file).pipe(response);
});

(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, colorScheme: 'dark' });
    await page.goto(`http://127.0.0.1:${server.address().port}/index.html`);
    const theme = () => page.locator('html').getAttribute('data-theme');
    const select = async mode => {
      await page.locator('.theme-switch-button').click();
      await page.locator(`.theme-change-button[data-mode="${mode}"]`).click();
    };
    assert.equal(await theme(), 'dark');
    assert.equal(await page.locator('.family-nav li').count(), 3);
    assert.equal(await page.locator('.family-current').count(), 1);
    assert.equal(await page.locator('.family-nav a').count(), 2);
    await select('light');
    assert.equal(await theme(), 'light');
    await page.reload();
    assert.equal(await theme(), 'light');
    await select('dark');
    assert.equal(await theme(), 'dark');
    await select('auto');
    await page.emulateMedia({ colorScheme: 'light' });
    await page.waitForFunction(() => document.documentElement.dataset.theme === 'light');
    await page.emulateMedia({ colorScheme: 'dark' });
    await page.waitForFunction(() => document.documentElement.dataset.theme === 'dark');
    // Native keyboard activation must work for the appearance menu too.
    await page.locator('.theme-switch-button').focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('.theme-change-button[data-mode="auto"]').isVisible(), true);
    await page.keyboard.press('Escape');
    for (const width of [390, 768]) {
      await page.setViewportSize({ width, height: 844 });
      await page.locator('.primary-toggle').click();
      assert.equal(await page.locator('#pst-primary-sidebar-modal').evaluate(dialog => dialog.open), true);
      assert.equal(await page.locator('.family-nav').isVisible(), true);
      await page.keyboard.press('Escape');
      await page.waitForFunction(() => !document.getElementById('pst-primary-sidebar-modal').open);
    }
    console.log('Passed: family navigation, theme modes/persistence/system changes, keyboard menu, mobile sidebar.');
  } finally {
    await browser.close();
    server.close();
  }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
