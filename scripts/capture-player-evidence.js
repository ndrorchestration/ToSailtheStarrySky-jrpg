const { chromium } = require('playwright');
const childProcess = require('child_process');
const fs = require('fs');
const http = require('http');
const path = require('path');
const { URL } = require('url');

const ROOT = path.resolve(__dirname, '..');
const PORT = Number(process.env.AETHERWAKE_PLAYER_EVIDENCE_PORT || 8092);
const VIEWPORT = { width: 960, height: 640 };

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function gitValue(command, fallback) {
  try {
    return childProcess.execSync(command, { cwd: ROOT, encoding: 'utf8' }).trim();
  } catch (_err) {
    return fallback;
  }
}

function createServer() {
  return http.createServer((req, res) => {
    const parsed = new URL(req.url, `http://127.0.0.1:${PORT}`);
    let requested = decodeURIComponent(parsed.pathname);
    if (requested === '/') requested = '/index-embedded.html';
    const relative = requested.replace(/^\/+/, '');
    const fullPath = path.resolve(ROOT, relative);

    if (!fullPath.startsWith(ROOT + path.sep) && fullPath !== ROOT) {
      res.writeHead(403);
      res.end('Forbidden');
      return;
    }

    fs.readFile(fullPath, (err, data) => {
      if (err) {
        res.writeHead(404);
        res.end('Not found');
        return;
      }
      const mime = {
        '.html': 'text/html; charset=utf-8',
        '.js': 'application/javascript; charset=utf-8',
        '.css': 'text/css; charset=utf-8',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.mp3': 'audio/mpeg',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
      }[path.extname(fullPath).toLowerCase()] || 'application/octet-stream';
      res.writeHead(200, { 'Content-Type': mime });
      res.end(data);
    });
  });
}

function prepareEvidenceDir() {
  const commit = gitValue('git rev-parse HEAD', 'unknown');
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outputRoot = process.env.AETHERWAKE_PLAYER_EVIDENCE_DIR ||
    path.join(ROOT, 'evidence', 'player-acceptance', `${commit.slice(0, 12)}-${timestamp}`);
  fs.mkdirSync(outputRoot, { recursive: true });
  return { commit, outputRoot };
}

async function waitForRuntime(page) {
  await page.waitForSelector('canvas', { timeout: 15000 });
  await page.waitForFunction(() =>
    window._firstWakeOpeningState &&
    window.AetherFirstWakeOpening &&
    window._combat &&
    window._world &&
    document.querySelector('canvas') &&
    document.querySelector('canvas').width === 960 &&
    document.querySelector('canvas').height === 640
  , undefined, { timeout: 15000 });
}

async function capture(page, outputRoot, captures, id, description) {
  const fileName = `${String(captures.length).padStart(2, '0')}-${id}.png`;
  const filePath = path.join(outputRoot, fileName);
  await page.screenshot({ path: filePath, fullPage: false });
  captures.push({ id, description, file: fileName });
}

async function pressEnter(page, count = 1) {
  for (let i = 0; i < count; i++) {
    await page.keyboard.press('Enter');
    await page.waitForTimeout(120);
  }
}

(async () => {
  const { commit, outputRoot } = prepareEvidenceDir();
  const captures = [];
  const browserErrors = [];
  const verification = {
    repository: 'ndrorchestration/ToSailtheStarrySky-jrpg',
    sourceCommit: commit,
    capturedAt: new Date().toISOString(),
    viewport: VIEWPORT,
    entrypoint: 'index-embedded.html',
    desktopExecutable: 'Aetherwake.exe',
    humanAcceptance: 'PENDING',
    visualAcceptance: 'PENDING',
    gameplayCaptureInspected: false,
    authorityBoundary: 'evidence bundle only; does not establish visual approval or player acceptance',
    captures,
    browserErrors,
  };

  const server = createServer();
  await new Promise(resolve => server.listen(PORT, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: VIEWPORT });

  page.on('pageerror', err => browserErrors.push(`PAGE: ${err.message}`));
  page.on('requestfailed', request => {
    browserErrors.push(`REQUEST: ${request.url()} — ${request.failure()?.errorText || 'failed'}`);
  });
  page.on('response', response => {
    if (response.status() < 400) return;
    const url = response.url();
    if (/\/tts\/[^/]+\/[^/]+\/\d+\.mp3(?:\?.*)?$/.test(url)) return;
    browserErrors.push(`HTTP ${response.status()} ${url}`);
  });
  page.on('console', msg => {
    if (msg.type() === 'error' && !msg.text().includes('Failed to load resource')) {
      browserErrors.push(`CONSOLE: ${msg.text()}`);
    }
  });

  try {
    const response = await page.goto(`http://127.0.0.1:${PORT}/index-embedded.html`, {
      waitUntil: 'domcontentloaded',
      timeout: 20000,
    });
    assert(response && response.ok(), 'index-embedded.html did not load successfully');
    await waitForRuntime(page);
    await capture(page, outputRoot, captures, 'title-ready', 'boot/title/menu canvas before starting First Wake');

    await page.keyboard.press('Enter');
    await page.waitForFunction(() =>
      window.gameState === 'opening' &&
      window.AetherFirstWakeOpening.currentScene(window._firstWakeOpeningState).id === 'arrival_horizon'
    , undefined, { timeout: 5000 });

    await capture(page, outputRoot, captures, 'arrival-horizon', 'First Wake arrival_horizon opening beat');

    await pressEnter(page, 6);
    await page.waitForFunction(() =>
      window.gameState === 'opening' &&
      window.AetherFirstWakeOpening.currentScene(window._firstWakeOpeningState).id === 'lyra_join'
    , undefined, { timeout: 5000 });
    await capture(page, outputRoot, captures, 'lyra-join', 'Lyra join beat before active-party mutation');

    await page.keyboard.press('Enter');
    await page.waitForFunction(() =>
      window.AetherFirstWakeOpening.currentScene(window._firstWakeOpeningState).sequence === 7 &&
      window.ACTIVE_PARTY.map(character => character.id).join('|') === 'ender|lyra'
    , undefined, { timeout: 5000 });
    await capture(page, outputRoot, captures, 'ender-lyra-party', 'post-join First Wake party boundary');

    await pressEnter(page, 3);
    await page.waitForFunction(() => window.gameState === 'world' && window._world && window._world.player,
      undefined, { timeout: 5000 });
    await capture(page, outputRoot, captures, 'world-handoff', 'world handoff after authored First Wake opening');

    await page.evaluate(() => {
      const p = window._world.player;
      p.tileX = 7; p.tileY = 7; p.x = 7; p.y = 7; p.px = 7 * 16; p.py = 7 * 16;
    });

    await page.keyboard.press('KeyE');
    await page.waitForFunction(() => window.gameState === 'dialogue', undefined, { timeout: 5000 });
    const dialogueState = await page.evaluate(() => ({
      npc: window.UI.dialogueNPC && window.UI.dialogueNPC.name,
      firstLine: Array.isArray(window.UI.dialogueLines) ? window.UI.dialogueLines[0] : window.UI.dialogueText,
    }));
    assert(String(dialogueState.npc).includes('Captain Ionia'), 'Captain Ionia dialogue was not opened');
    await capture(page, outputRoot, captures, 'captain-ionia-dialogue', 'Captain Ionia authored first-contact dialogue');

    await page.keyboard.press('Escape');
    await page.waitForFunction(() => window.gameState === 'world', undefined, { timeout: 5000 });
    await page.keyboard.press('KeyC');
    await page.waitForFunction(() => window.gameState === 'combat' && window._combat && window._combat.getState().enemy,
      undefined, { timeout: 5000 });
    await capture(page, outputRoot, captures, 'combat-entry', 'representative combat entry frame for human review');

    verification.runtimeChecks = {
      arrivalScene: 'arrival_horizon',
      joinScene: 'lyra_join',
      ioniaDialogueNpc: dialogueState.npc,
      captureCount: captures.length,
    };
    verification.status = 'CAPTURED_PENDING_HUMAN_REVIEW';
    console.log('AETHERWAKE_PLAYER_EVIDENCE=CAPTURED');
    console.log(`AETHERWAKE_PLAYER_EVIDENCE_DIR=${outputRoot}`);
  } catch (err) {
    verification.status = 'FAILED';
    verification.failure = String(err && err.stack || err);
    throw err;
  } finally {
    fs.writeFileSync(path.join(outputRoot, 'manifest.json'), `${JSON.stringify(verification, null, 2)}\n`);
    await browser.close();
    server.close();
  }
})().catch(err => {
  console.error(err && err.stack || err);
  process.exit(1);
});
