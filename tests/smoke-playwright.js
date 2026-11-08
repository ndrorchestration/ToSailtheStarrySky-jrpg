const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const BASE = path.resolve(__dirname, '..');
const PORT = Number(process.env.AETHERWAKE_TEST_PORT || 8091);

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function createServer() {
  return http.createServer((req, res) => {
    const parsed = new URL(req.url, `http://127.0.0.1:${PORT}`);
    let requested = decodeURIComponent(parsed.pathname);
    if (requested === '/') requested = '/index-embedded.html';

    const relative = requested.replace(/^\/+/, '');
    const fullPath = path.resolve(BASE, relative);

    if (!fullPath.startsWith(BASE + path.sep) && fullPath !== BASE) {
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
      }[path.extname(fullPath).toLowerCase()] || 'application/octet-stream';

      res.writeHead(200, { 'Content-Type': mime });
      res.end(data);
    });
  });
}

(async () => {
  const server = createServer();
  await new Promise(resolve => server.listen(PORT, '127.0.0.1', resolve));

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 960, height: 640 } });
  const errors = [];

  page.on('pageerror', err => errors.push(`PAGE: ${err.message}\n${err.stack || ''}`));
  page.on('requestfailed', request => {
    errors.push(`REQUEST: ${request.url()} — ${request.failure()?.errorText || 'failed'}`);
  });
  page.on('response', response => {
    if (response.status() < 400) return;
    const url = response.url();
    // Generated TTS is intentionally optional; a missing clip must not fail
    // the otherwise valid gameplay smoke path.
    if (/\/tts\/[^/]+\/[^/]+\/\d+\.mp3(?:\?.*)?$/.test(url)) return;
    errors.push(`HTTP ${response.status()} ${url}`);
  });
  page.on('console', msg => {
    if (msg.type() === 'error' && !msg.text().includes('Failed to load resource')) {
      errors.push(`CONSOLE: ${msg.text()}`);
    }
  });

  try {
    const response = await page.goto(
      `http://127.0.0.1:${PORT}/index-embedded.html`,
      { waitUntil: 'domcontentloaded', timeout: 20000 }
    );
    assert(response && response.ok(), 'index-embedded.html did not load successfully');

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

    const debugOverlayState = await page.evaluate(() =>
      ['debug-overlay', 'aw-debug-overlay'].map(id => {
        const node = document.getElementById(id);
        return {
          id,
          display: node ? getComputedStyle(node).display : 'missing',
          debugEnabled: Boolean(window.__awDebugEnabled),
        };
      })
    );
    assert(debugOverlayState.every(entry => entry.debugEnabled === false),
      'normal launch unexpectedly enabled debug mode');
    assert(debugOverlayState.every(entry => entry.display === 'none'),
      'normal launch exposed a debug overlay');

    // One real Enter follows the production input path:
    // BOOT → MENU → OPENING. No custom companion creation is allowed.
    await page.keyboard.press('Enter');
    await page.waitForFunction(() =>
      window.gameState === 'opening' &&
      window._firstWakeOpeningState &&
      window.AetherFirstWakeOpening.currentScene(window._firstWakeOpeningState).sequence === 0
    , undefined, { timeout: 5000 });

    const openingBootstrap = await page.evaluate(() => ({
      sceneId: window.AetherFirstWakeOpening.currentScene(window._firstWakeOpeningState).id,
      activeIds: window.ACTIVE_PARTY.map(character => character.id),
      playable: window.ROSTER.map(character => Boolean(character.playable)),
      charCreatePhase: window._charcreate && window._charcreate.phase,
    }));
    assert(openingBootstrap.sceneId === 'arrival_horizon',
      'New Game did not begin at authored First Wake Sequence 00');
    assert(openingBootstrap.activeIds.join('|') === 'ender',
      'First Wake did not begin with Ender alone');
    assert(openingBootstrap.playable.join('|') === 'true|false|false|false|false',
      'opening bootstrap exposed unjoined protagonists');
    assert(openingBootstrap.charCreatePhase !== 'name',
      'normal New Game incorrectly entered custom companion creation');

    for (let i = 0; i < 6; i++) await page.keyboard.press('Enter');
    await page.waitForFunction(() =>
      window.gameState === 'opening' &&
      window.AetherFirstWakeOpening.currentScene(window._firstWakeOpeningState).sequence === 6
    , undefined, { timeout: 5000 });

    const beforeLyraJoin = await page.evaluate(() => ({
      sceneId: window.AetherFirstWakeOpening.currentScene(window._firstWakeOpeningState).id,
      activeIds: window.ACTIVE_PARTY.map(character => character.id),
      playable: window.ROSTER.map(character => Boolean(character.playable)),
    }));
    assert(beforeLyraJoin.sceneId === 'lyra_join',
      'First Wake did not reach the Lyra join scene');
    assert(beforeLyraJoin.activeIds.join('|') === 'ender',
      'Lyra joined before the authored Lyra join beat');

    await page.keyboard.press('Enter');
    await page.waitForFunction(() =>
      window.AetherFirstWakeOpening.currentScene(window._firstWakeOpeningState).sequence === 7 &&
      window.ACTIVE_PARTY.length === 2
    , undefined, { timeout: 5000 });

    const afterLyraJoin = await page.evaluate(() => ({
      activeIds: window.ACTIVE_PARTY.map(character => character.id),
      playable: window.ROSTER.map(character => Boolean(character.playable)),
      lyraRef: window.ACTIVE_PARTY[1] === window.ROSTER[1],
      ioniaActive: window.ACTIVE_PARTY.some(character => character.id === 'ionia'),
    }));
    assert(afterLyraJoin.activeIds.join('|') === 'ender|lyra',
      'Lyra did not join at the authored Sequence 06 boundary');
    assert(afterLyraJoin.playable.join('|') === 'true|true|false|false|false',
      'Lyra join widened protagonist availability beyond the authored boundary');
    assert(afterLyraJoin.lyraRef,
      'Lyra active-party entry is not the canonical roster record');
    assert(afterLyraJoin.ioniaActive === false,
      'Ionia joined before the authored departure decision');

    await page.keyboard.press('Enter');
    await page.keyboard.press('Enter');
    await page.keyboard.press('Enter');
    await page.waitForFunction(() =>
      window.gameState === 'world' &&
      window._world &&
      window._world.player
    , undefined, { timeout: 5000 });

    const worldBeforeCombat = await page.evaluate(() => ({
      name: window._world.player.name,
      className: window._world.player.class,
      level: window._world.player.level,
      xp: window._world.player.xp,
      openingComplete: window._firstWakeOpeningState.complete,
      activeIds: window.ACTIVE_PARTY.map(character => character.id),
    }));

    assert(worldBeforeCombat.name === 'Ender',
      'First Wake handoff lost authored Ender identity');
    assert(worldBeforeCombat.className === 'Rift Scholar',
      'First Wake handoff lost Ender Rift Scholar job');
    assert(worldBeforeCombat.openingComplete === true,
      'First Wake opening did not mark completion at chapter-card handoff');
    assert(worldBeforeCombat.activeIds.join('|') === 'ender|lyra',
      'chapter-card handoff did not preserve authored two-member party');

    // Exercise real input/overlay paths before combat: movement, proximity-gated
    // shop, ledger data, and first-contact dialogue.
    await page.evaluate(() => {
      const p = window._world.player;
      p.tileX = 16; p.tileY = 16; p.x = 16; p.y = 16; p.px = 16 * 16; p.py = 16 * 16;
    });
    await page.keyboard.press('d');
    await page.waitForFunction(() => window._world.player.tileX === 17);

    await page.keyboard.press('m');
    await page.waitForTimeout(200);
    assert((await page.evaluate(() => window.gameState)) === 'world',
      'shop must not open outside Repair Cafe proximity');

    await page.evaluate(() => {
      const p = window._world.player;
      p.tileX = 14; p.tileY = 22; p.x = 14; p.y = 22; p.px = 14 * 16; p.py = 22 * 16;
    });
    await page.keyboard.press('m');
    await page.waitForFunction(() => window.gameState === 'shop');
    const shopBefore = await page.evaluate(() => ({
      items: window.UI.shopItems.length,
      handler: typeof window.UI.shopBuyHandler,
      scrap: window._world.player.scrap,
      aether: window._world.player.aether,
    }));
    assert(shopBefore.items === 6, 'Repair Cafe did not populate its live item list');
    assert(shopBefore.handler === 'function', 'Repair Cafe purchase handler is missing');
    await page.keyboard.press('1');
    await page.waitForFunction(before => window._world.player.scrap < before,
      shopBefore.scrap);
    const shopAfter = await page.evaluate(() => ({
      scrap: window._world.player.scrap,
      aether: window._world.player.aether,
    }));
    assert(shopAfter.aether === shopBefore.aether + 1,
      'Repair Cafe aether purchase did not update numeric world state');
    await page.keyboard.press('Escape');
    await page.waitForFunction(() => window.gameState === 'world');

    await page.keyboard.press('l');
    await page.waitForFunction(() => window.gameState === 'ledger');
    assert(await page.evaluate(() => window._world.getLedger().length >= 2),
      'ledger overlay did not expose live entries');
    await page.keyboard.press('Escape');
    await page.waitForFunction(() => window.gameState === 'world');

    await page.evaluate(() => {
      const p = window._world.player;
      p.tileX = 7; p.tileY = 7; p.x = 7; p.y = 7; p.px = 7 * 16; p.py = 7 * 16;
    });
    await page.keyboard.press('e');
    await page.waitForFunction(() => window.gameState === 'dialogue');
    const firstDialogue = await page.evaluate(() => ({
      lines: window.UI.dialogueLines,
      lineIndex: window.UI.dialogueLineIndex,
    }));
    assert(firstDialogue.lines[0].includes('The Aureate Wake can fly'),
      'first NPC contact did not select Captain Ionia\'s authored intro dialogue');
    assert(firstDialogue.lineIndex === 0, 'dialogue did not start at line zero');
    await page.keyboard.press('e');
    await page.waitForFunction(() => window.UI.dialogueLineIndex === 1);
    await page.keyboard.press('Escape');
    await page.waitForFunction(() => window.gameState === 'world');

    const partyArchitecture = await page.evaluate(() => ({
      rosterLength: window.ROSTER && window.ROSTER.length,
      activeLength: window.ACTIVE_PARTY && window.ACTIVE_PARTY.length,
      rosterIds: window.ROSTER && window.ROSTER.map(character => character.id),
      activeIds: window.ACTIVE_PARTY && window.ACTIVE_PARTY.map(character => character.id),
      rosterRefs: window.ROSTER && window.ACTIVE_PARTY && [
        window.ACTIVE_PARTY[0] === window.ROSTER[0],
        window.ACTIVE_PARTY[1] === window.ROSTER[1],
      ],
      worldLeadRef: Boolean(window._world && window.ROSTER &&
        window._world.player === window.ROSTER[0]),
      legacyPartyAlias: window.party === window.ACTIVE_PARTY,
      runtimeImplemented: window.ROSTER &&
        window.ROSTER.map(character => Boolean(character.runtimeImplemented)),
      playable: window.ROSTER &&
        window.ROSTER.map(character => Boolean(character.playable)),
      statModelVersion: window.AetherJRPGStatModel && window.AetherJRPGStatModel.VERSION,
      productionStatModelVersion: window.AetherPartyState &&
        window.AetherPartyState.productionStatModelVersion,
      enderProductionSpirit: window.ROSTER && window.ROSTER[0] &&
        window.ROSTER[0].productionStats && window.ROSTER[0].productionStats.spirit,
      ioniaProductionPresence: window.ROSTER && window.ROSTER[2] &&
        window.ROSTER[2].productionStats && window.ROSTER[2].productionStats.presence,
      enderLegacySpirit: window.ROSTER && window.ROSTER[0] && window.ROSTER[0].spirit,
      ioniaLegacyPresence: window.ROSTER && window.ROSTER[2] && window.ROSTER[2].presence,
      derivedReady: Boolean(window.ROSTER && window.ROSTER.every(character =>
        character.productionDerivedStats &&
        Number.isFinite(character.productionDerivedStats.maxHp))),
    }));

    assert(partyArchitecture.rosterLength === 5, 'persistent roster does not contain five records');
    assert(partyArchitecture.activeLength === 2, 'chapter-card party does not contain Ender + Lyra');
    assert(partyArchitecture.rosterIds.join('|') === 'ender|lyra|ionia|reson|aepex',
      'persistent roster identity order is incorrect');
    assert(partyArchitecture.activeIds.join('|') === 'ender|lyra',
      'chapter-card active party references are incorrect');
    assert(partyArchitecture.rosterRefs.every(Boolean),
      'ACTIVE_PARTY members are not the canonical ROSTER references');
    assert(partyArchitecture.worldLeadRef,
      'WORLD player is not the canonical Ender roster record');
    assert(partyArchitecture.legacyPartyAlias,
      'legacy window.party alias is not canonical ACTIVE_PARTY');
    assert(partyArchitecture.runtimeImplemented.join('|') === 'true|false|false|false|false',
      'runtime implementation boundary for roster records is incorrect');
    assert(partyArchitecture.playable.join('|') === 'true|true|false|false|false',
      'story-playable boundary drifted after Lyra join');
    assert(partyArchitecture.statModelVersion === '0.1.0',
      'JRPG stat model is not loaded in the browser runtime');
    assert(partyArchitecture.productionStatModelVersion === '0.1.0',
      'party state is not bound to JRPG stat model v0.1.0');
    assert(partyArchitecture.enderProductionSpirit === 12,
      'Ender production Spirit 12 is not present in the live roster');
    assert(partyArchitecture.ioniaProductionPresence === 9,
      'Ionia production Presence 9 is not present in the live roster');
    assert(partyArchitecture.enderLegacySpirit === 1 &&
           partyArchitecture.ioniaLegacyPresence === 2,
      'production stat binding contaminated legacy compatibility fields');
    assert(partyArchitecture.derivedReady,
      'production derived stats are not initialized for all roster records');

    await page.keyboard.press('KeyC');
    await page.waitForFunction(() =>
      window.gameState === 'combat' &&
      window._combat &&
      window._combat.getState &&
      window._combat.getState().enemy
    , undefined, { timeout: 5000 });

    const combatStart = await page.evaluate(() => window._combat.getState());
    assert(combatStart.turn === 0, 'combat did not start at turn 0');
    assert(combatStart.player.productionStats &&
           combatStart.player.productionStats.spirit === 12,
      'combat state did not receive Ender production stats');
    const productionFormulaRuntime = await page.evaluate(() => ({
      policyModel: window.AetherCombatSystemPolicy &&
        window.AetherCombatSystemPolicy.TARGET.model,
      formulaVersion: window.AetherCombatFormula &&
        window.AetherCombatFormula.VERSION,
      commonsVersion: window.AetherCommonsLedger &&
        window.AetherCommonsLedger.VERSION,
      commonsOwner: window.AetherCommonsLedger &&
        window.AetherCommonsLedger.OWNER,
      aetherSealVersion: window.AetherSealContract &&
        window.AetherSealContract.VERSION,
      aetherSealOwner: window.AetherSealContract &&
        window.AetherSealContract.OWNER,
    }));
    assert(productionFormulaRuntime.policyModel === 'jrpg-stat-formula',
      'production combat policy is not loaded');
    assert(productionFormulaRuntime.formulaVersion === '1.1.0',
      'production formula engine is not loaded at expected version 1.1.0');
    assert(productionFormulaRuntime.commonsVersion === '0.1.0' &&
           productionFormulaRuntime.commonsOwner === 'ender',
      'Commons Ledger runtime contract is not loaded for Ender');
    assert(productionFormulaRuntime.aetherSealVersion === '0.1.0' &&
           productionFormulaRuntime.aetherSealOwner === 'ender',
      'Aether Seal runtime contract is not loaded for Ender');

    // Wind Ward remains visible in its stable slot but authority-blocked
    // regardless of legacy level state.
    await page.keyboard.press('6');
    const afterLockedAction = await page.evaluate(() => window._combat.getState());
    assert(afterLockedAction.turn === 0,
      'SSOT-blocked Wind Ward consumed a turn');
    assert(afterLockedAction.log.some(line =>
      line.includes('Action blocked by current SSOT') && line.includes('Wind Ward')),
      'Wind Ward SSOT rejection was not recorded');
    assert(afterLockedAction.eligibleActionIds.join('|') ===
      'staffStrike|uncoverTruth|sharedDream|mycelialLedger|hold',
      'level-1 eligible action set drifted');

    const affordabilityContract = await page.evaluate(() => {
      window._combat.init({
        vit: 13,
        scrap: 7,
        aether: { current: 0, max: 6 },
        heat: { current: 1, max: 3 },
        echoes: { current: 1, max: 3 },
        charges: 2,
        staffMax: 2,
        level: 1,
        xp: 0,
        xpToNext: 50,
        unlockedAbilities: ['uncoverTruth', 'sharedDream', 'mycelialLedger'],
      });
      window._combat.beginEncounter('skyPredator');
      const before = window._combat.getState();
      const result = window._combat.resolveTurn('uncoverTruth', null);
      const after = window._combat.getState();

      // Restore the normal world-backed combat session for the rest of smoke.
      if (typeof startCombat !== 'function') throw new Error('startCombat is unavailable');
      startCombat('skyPredator');

      return {
        result,
        beforeTurn: before.turn,
        afterTurn: after.turn,
        beforeEchoes: before.player.echoes.current,
        afterEchoes: after.player.echoes.current,
        beforeAether: before.player.aether.current,
        afterAether: after.player.aether.current,
        log: after.log,
      };
    });

    assert(affordabilityContract.result === false,
      'underfunded action was not rejected');
    assert(affordabilityContract.beforeTurn === 0 && affordabilityContract.afterTurn === 0,
      'underfunded action consumed a turn');
    assert(affordabilityContract.beforeEchoes === 1 && affordabilityContract.afterEchoes === 1,
      'underfunded action partially consumed echoes');
    assert(affordabilityContract.beforeAether === 0 && affordabilityContract.afterAether === 0,
      'underfunded action partially consumed aether');
    assert(affordabilityContract.log.some(line =>
      line.includes('Not enough resources') && line.includes('needs 2')),
      'underfunded action did not record the preflight rejection');

    const progressionReachability = await page.evaluate(() => {
      window._combat.init({
        vit: 13,
        scrap: 7,
        aether: { current: 4, max: 6 },
        heat: { current: 1, max: 3 },
        echoes: { current: 3, max: 3 },
        charges: 2,
        staffMax: 2,
        level: 2,
        xp: 74,
        xpToNext: 75,
        unlockedAbilities: ['uncoverTruth', 'sharedDream', 'mycelialLedger'],
      });
      const before = window._combat.getState();
      window._combat.awardXP(1);
      const after = window._combat.getState();

      if (typeof startCombat !== 'function') throw new Error('startCombat is unavailable');
      startCombat('skyPredator');

      return {
        beforeLevel: before.player.level,
        beforeXP: before.player.xp,
        afterLevel: after.player.level,
        afterXP: after.player.xp,
        afterXPToNext: after.player.xpToNext,
        unlockedAbilities: after.player.unlockedAbilities,
        eligibleActionIds: after.eligibleActionIds,
        usableActionIds: after.usableActionIds,
        log: after.log,
      };
    });

    assert(progressionReachability.beforeLevel === 2 &&
      progressionReachability.beforeXP === 74,
      'progression reachability fixture did not start at level-2 threshold');
    assert(progressionReachability.afterLevel === 3,
      'awardXP did not advance level 2 to level 3');
    assert(progressionReachability.afterXP === 0,
      'level-up did not consume the previous XP threshold');
    assert(progressionReachability.afterXPToNext === 112,
      'level-3 XP threshold drifted');
    assert(progressionReachability.unlockedAbilities.includes('windWard'),
      'level-3 progression did not unlock Wind Ward');
    assert(progressionReachability.eligibleActionIds.includes('windWard'),
      'legacy progression record did not retain Wind Ward unlock provenance');
    assert(!progressionReachability.usableActionIds.includes('windWard'),
      'SSOT-blocked Wind Ward became runtime-usable after legacy unlock');
    assert(progressionReachability.log.some(line =>
      line.includes('LEVEL 3: Wind Ward unlocked')),
      'level-3 unlock log is missing');

    const blockedResidueContract = await page.evaluate(() => {
      window._combat.init({
        vit: 13,
        scrap: 7,
        aether: { current: 4, max: 6 },
        heat: { current: 1, max: 3 },
        echoes: { current: 3, max: 3 },
        charges: 2,
        staffMax: 2,
        level: 3,
        xp: 0,
        xpToNext: 112,
        unlockedAbilities: [
          'uncoverTruth', 'sharedDream', 'mycelialLedger', 'windWard'
        ],
      });
      window._combat.beginEncounter('skyPredator');

      const before = window._combat.getState();
      const dreamResult = window._combat.resolveTurn('sharedDream', null);
      const afterDream = window._combat.getState();
      const wardResult = window._combat.resolveTurn('windWard', null);
      const afterWard = window._combat.getState();

      if (typeof startCombat !== 'function') throw new Error('startCombat is unavailable');
      startCombat('skyPredator');

      return {
        dreamResult,
        wardResult,
        beforeTurn: before.turn,
        afterDreamTurn: afterDream.turn,
        afterWardTurn: afterWard.turn,
        beforeResources: {
          echoes: before.player.echoes.current,
          aether: before.player.aether.current,
          heat: before.player.heat.current,
        },
        afterResources: {
          echoes: afterWard.player.echoes.current,
          aether: afterWard.player.aether.current,
          heat: afterWard.player.heat.current,
        },
        dreamEligibility: afterDream.actionUseEligibility.sharedDream,
        wardEligibility: afterWard.actionUseEligibility.windWard,
        secondaryAvailable: afterWard.secondaryAvailable,
        lastAbilityId: afterWard.lastAbilityId,
        log: afterWard.log.slice(),
      };
    });

    assert(blockedResidueContract.dreamResult === false &&
           blockedResidueContract.wardResult === false,
      'SSOT-blocked compatibility actions were executable');
    assert(blockedResidueContract.beforeTurn === 0 &&
           blockedResidueContract.afterDreamTurn === 0 &&
           blockedResidueContract.afterWardTurn === 0,
      'SSOT-blocked compatibility action consumed a turn');
    assert(JSON.stringify(blockedResidueContract.beforeResources) ===
           JSON.stringify(blockedResidueContract.afterResources),
      'SSOT-blocked compatibility action consumed resources or generated Heat');
    assert(blockedResidueContract.dreamEligibility.reason === 'ssot_blocked' &&
           blockedResidueContract.wardEligibility.reason === 'ssot_blocked',
      'blocked compatibility actions do not expose SSOT-blocked eligibility');
    assert(blockedResidueContract.secondaryAvailable === false &&
           blockedResidueContract.lastAbilityId === null,
      'blocked compatibility action mutated secondary-action state');
    assert(blockedResidueContract.log.filter(line =>
      line.includes('Action blocked by current SSOT')).length >= 2,
      'blocked compatibility actions did not log authority rejection');

    // Secondary input must be a safe no-op when no secondary is available.
    // This specifically guards against core reaching into AetherCombat's
    // private state.
    await page.keyboard.press('KeyS');
    const afterIdleSecondary = await page.evaluate(() => window._combat.getState());
    assert(afterIdleSecondary.turn === 0,
      'unavailable secondary action should not consume a turn');

    const enemyMetadataContract = await page.evaluate(() => {
      const ids = [
        'skyPredator',
        'corporateSalvager',
        'windShear',
        'aetherLeak',
        'engine_spirit',
        'child_prophet',
        'elder_farmer',
      ];
      const snapshots = ids.map(id => {
        window._combat.beginEncounter(id);
        const enemy = window._combat.getState().enemy;
        return {
          id,
          type: enemy && enemy.type,
          ability: enemy && enemy.ability,
          abilities: enemy && enemy.abilities,
          abilityDesc: enemy && enemy.abilityDesc,
          color: enemy && enemy.color,
          bodyShape: enemy && enemy.bodyShape,
          aetherDependent: enemy && enemy.aetherDependent,
        };
      });
      window._combat.beginEncounter('skyPredator');
      return snapshots;
    });

    assert(enemyMetadataContract.length === 7,
      'enemy metadata contract did not cover all current templates');
    for (const enemy of enemyMetadataContract) {
      assert(enemy.type === enemy.id,
        'enemy encounter lost type metadata for ' + enemy.id);
      assert(typeof enemy.ability === 'string' && enemy.ability.length > 0,
        'enemy encounter lost ability metadata for ' + enemy.id);
      assert(Array.isArray(enemy.abilities) &&
        enemy.abilities.length === 1 &&
        enemy.abilities[0] === enemy.ability,
        'enemy encounter ability list drifted for ' + enemy.id);
      assert(typeof enemy.abilityDesc === 'string' && enemy.abilityDesc.length > 0,
        'enemy encounter lost ability description for ' + enemy.id);
      assert(typeof enemy.color === 'string' && enemy.color.length > 0,
        'enemy encounter lost color metadata for ' + enemy.id);
      assert(typeof enemy.bodyShape === 'string' && enemy.bodyShape.length > 0,
        'enemy encounter lost body-shape metadata for ' + enemy.id);
    }
    const aetherLeakMetadata = enemyMetadataContract.find(enemy => enemy.id === 'aetherLeak');
    const engineSpiritMetadata = enemyMetadataContract.find(enemy => enemy.id === 'engine_spirit');
    assert(aetherLeakMetadata && aetherLeakMetadata.aetherDependent === true,
      'Aether Leak Wraith lost explicit Aether-dependence metadata');
    assert(engineSpiritMetadata && engineSpiritMetadata.aetherDependent == null,
      'Wakeheart Echo Aether dependence was inferred without authority');

    const effectContract = await page.evaluate(() => {
      const vocabulary = window.AetherEffectVocabulary;
      const actions = window._combat.getState().actions;
      return {
        version: vocabulary && vocabulary.VERSION,
        validCoverage: Boolean(vocabulary && vocabulary.assertActionCoverage(actions)),
        kinds: vocabulary && Object.values(vocabulary.EFFECT_KIND),
        profileIds: actions.map(action => action.effectProfile),
        uncoverImplemented: vocabulary
          ? vocabulary.ACTION_EFFECT_PROFILES.uncoverTruth.success
              .filter(effect => effect.runtimeStatus === vocabulary.RUNTIME_STATUS.IMPLEMENTED)
              .map(effect => effect.kind + ':' + effect.key)
          : [],
        mycelialImplemented: vocabulary
          ? vocabulary.ACTION_EFFECT_PROFILES.mycelialLedger.success
              .filter(effect => effect.runtimeStatus === vocabulary.RUNTIME_STATUS.IMPLEMENTED)
              .map(effect => effect.kind + ':' + effect.key)
          : [],
        mycelialCommonCount: vocabulary
          ? vocabulary.ACTION_EFFECT_PROFILES.mycelialLedger.common.length
          : -1,
        aetherSealImplemented: vocabulary
          ? vocabulary.ACTION_EFFECT_PROFILES.aetherSeal.success
              .filter(effect => effect.runtimeStatus === vocabulary.RUNTIME_STATUS.IMPLEMENTED)
              .map(effect => effect.kind + ':' + effect.key)
          : [],
      };
    });

    assert(effectContract.version === '0.1.0', 'effect vocabulary version is not loaded');
    assert(effectContract.validCoverage, 'current actions are not covered by effect profiles');
    assert(effectContract.kinds.join('|') ===
      'damage|restore|resource|modifier|status|reveal|movement',
      'effect vocabulary kinds drifted');
    assert(effectContract.profileIds.join('|') ===
      'staffStrike|uncoverTruth|sharedDream|mycelialLedger|hold|windWard|aetherSeal|rest',
      'combat action effect-profile bindings drifted');
    assert(effectContract.uncoverImplemented.includes('reveal:weakness'),
      'Uncover Truth weakness reveal is not marked implemented');
    assert(effectContract.uncoverImplemented.includes('modifier:nextDamageMultiplier'),
      'Uncover Truth analysis multiplier is not marked implemented');
    for (const key of ['relationships', 'dependencies', 'exchanges', 'obligations']) {
      assert(effectContract.mycelialImplemented.includes('reveal:' + key),
        'Mycelial Ledger read-only reveal is not implemented: ' + key);
    }
    assert(effectContract.mycelialCommonCount === 0,
      'Mycelial Ledger unexpectedly retains common resource/Heat mutations');
    assert(effectContract.aetherSealImplemented.includes('status:aether-suppressed'),
      'Aether Seal suppression status is not marked implemented');

    const registryContract = await page.evaluate(() => {
      const abilities = window.AetherAbilityDefs;
      const progression = window.AetherProgressionDefs;
      const actions = window._combat.getState().actions;
      return {
        abilityVersion: abilities && abilities.VERSION,
        progressionVersion: progression && progression.VERSION,
        validAbilities: Boolean(abilities && abilities.assertRuntimeActions(actions)),
        validProgression: Boolean(
          progression && progression.validateAgainstAbilityDefs(abilities)
        ),
        actionOrder: abilities && abilities.ACTION_ORDER.slice(),
        sharedDreamAuthority: abilities && abilities.DEFS.sharedDream && {
          authorityStatus: abilities.DEFS.sharedDream.authorityStatus,
          migrationStatus: abilities.DEFS.sharedDream.migrationStatus,
          canonicalOwner: abilities.DEFS.sharedDream.canonicalOwner,
          hasResolution: Boolean(abilities.DEFS.sharedDream.resolution),
        },
        mycelialLedgerAuthority: abilities && abilities.DEFS.mycelialLedger && {
          authorityStatus: abilities.DEFS.mycelialLedger.authorityStatus,
          migrationStatus: abilities.DEFS.mycelialLedger.migrationStatus,
          canonicalOwner: abilities.DEFS.mycelialLedger.canonicalOwner,
          hasResolution: Boolean(abilities.DEFS.mycelialLedger.resolution),
          resolutionModel: abilities.DEFS.mycelialLedger.resolution &&
            abilities.DEFS.mycelialLedger.resolution.model,
        },
        aetherSealAuthority: abilities && abilities.DEFS.aetherSeal && {
          authorityStatus: abilities.DEFS.aetherSeal.authorityStatus,
          migrationStatus: abilities.DEFS.aetherSeal.migrationStatus,
          canonicalOwner: abilities.DEFS.aetherSeal.canonicalOwner,
          hasResolution: Boolean(abilities.DEFS.aetherSeal.resolution),
          resolutionModel: abilities.DEFS.aetherSeal.resolution &&
            abilities.DEFS.aetherSeal.resolution.model,
        },
        windWardAuthority: abilities && abilities.DEFS.windWard && {
          authorityStatus: abilities.DEFS.windWard.authorityStatus,
          migrationStatus: abilities.DEFS.windWard.migrationStatus,
          canonicalOwner: abilities.DEFS.windWard.canonicalOwner,
          hasResolution: Boolean(abilities.DEFS.windWard.resolution),
        },
        levelUnlocks: progression && Object.fromEntries(
          Object.entries(progression.LEVEL_UNLOCKS)
            .map(([level, entries]) => [level, entries.map(entry => entry.abilityId)])
        ),
      };
    });

    assert(registryContract.abilityVersion === '0.3.0',
      'ability registry version is not loaded');
    assert(registryContract.progressionVersion === '0.2.0',
      'progression registry version is not loaded');
    assert(registryContract.sharedDreamAuthority &&
      registryContract.sharedDreamAuthority.authorityStatus === 'legacy-adaptation-residue' &&
      registryContract.sharedDreamAuthority.migrationStatus === 'blocked-by-current-ssot' &&
      registryContract.sharedDreamAuthority.canonicalOwner === null &&
      registryContract.sharedDreamAuthority.hasResolution === false,
      'Shared Dream SSOT migration guard drifted');
    assert(registryContract.mycelialLedgerAuthority &&
      registryContract.mycelialLedgerAuthority.authorityStatus === 'creator-aligned-exceptional-access' &&
      registryContract.mycelialLedgerAuthority.migrationStatus === 'live-readonly-v1' &&
      registryContract.mycelialLedgerAuthority.canonicalOwner === 'ender' &&
      registryContract.mycelialLedgerAuthority.hasResolution === true &&
      registryContract.mycelialLedgerAuthority.resolutionModel === 'commons-readonly',
      'Mycelial Ledger SSOT migration guard drifted');
    assert(registryContract.aetherSealAuthority &&
      registryContract.aetherSealAuthority.authorityStatus === 'creator-aligned-aether-ward' &&
      registryContract.aetherSealAuthority.migrationStatus === 'live-aether-seal-v1' &&
      registryContract.aetherSealAuthority.canonicalOwner === 'ender' &&
      registryContract.aetherSealAuthority.hasResolution === true &&
      registryContract.aetherSealAuthority.resolutionModel === 'aether-seal',
      'Aether Seal authority binding drifted');
    assert(registryContract.windWardAuthority &&
      registryContract.windWardAuthority.authorityStatus === 'legacy-adaptation-residue' &&
      registryContract.windWardAuthority.migrationStatus === 'blocked-pending-owner-and-domain' &&
      registryContract.windWardAuthority.canonicalOwner === null &&
      registryContract.windWardAuthority.hasResolution === false,
      'Wind Ward unresolved-authority guard drifted');
    assert(registryContract.validAbilities,
      'runtime actions drifted from canonical ability definitions');
    assert(registryContract.validProgression,
      'progression unlocks do not resolve against canonical ability definitions');
    assert(registryContract.actionOrder.join('|') ===
      'staffStrike|uncoverTruth|sharedDream|mycelialLedger|hold|windWard|aetherSeal|rest',
      'ability action order drifted');
    assert(JSON.stringify(registryContract.levelUnlocks) ===
      JSON.stringify({ 3: ['windWard'], 4: ['aetherSeal'], 5: ['rest'] }),
      'legacy progression unlock mapping drifted');

    const resolverContract = await page.evaluate(() => {
      const vocabulary = window.AetherEffectVocabulary;
      const resolver = window.AetherEffectResolver;
      const context = {
        player: {
          vit: 10,
          maxVit: 13,
          scrap: 7,
          aether: { current: 4, max: 6 },
          heat: { current: 1, max: 3 },
          echoes: { current: 3, max: 3 },
          staffCharges: 2,
          maxStaffCharges: 2,
        },
        enemy: { hp: 12, maxHp: 12 },
        staffChargeMax: 2,
      };

      const results = resolver.applyEffects([
        resolver.createDamageEffect(vocabulary.TARGET.ENEMY, 3, 'emp'),
        resolver.createDamageEffect(vocabulary.TARGET.SELF, 2),
        resolver.createRestoreEffect(vocabulary.TARGET.SELF, 1),
        resolver.createResourceDeltaEffect(vocabulary.RESOURCE.HEAT, 5),
        resolver.createResourceDeltaEffect(vocabulary.RESOURCE.AETHER, -2),
      ], context);

      return {
        version: resolver.VERSION,
        playerVit: context.player.vit,
        enemyHp: context.enemy.hp,
        heat: context.player.heat.current,
        aether: context.player.aether.current,
        applied: results.map(result => result.applied),
      };
    });

    assert(resolverContract.version === '0.1.0',
      'effect resolver version is not loaded');
    assert(resolverContract.playerVit === 9,
      'effect resolver damage/restoration sequence drifted');
    assert(resolverContract.enemyHp === 9,
      'effect resolver enemy damage drifted');
    assert(resolverContract.heat === 3,
      'effect resolver heat clamp drifted');
    assert(resolverContract.aether === 2,
      'effect resolver resource decrease drifted');
    assert(resolverContract.applied.every(Boolean),
      'effect resolver unexpectedly skipped an implemented effect');

    await page.keyboard.press('1');
    await page.waitForFunction(() =>
      window._combat && window._combat.getState().turn >= 1
    , undefined, { timeout: 5000 });

    await page.keyboard.press('2');
    await page.waitForFunction(() =>
      window._combat && window._combat.getState().turn >= 2
    , undefined, { timeout: 5000 });

    const combatAfterActions = await page.evaluate(() => window._combat.getState());
    assert(combatAfterActions.turn >= 2, 'combat actions did not resolve');
    assert(combatAfterActions.resolverMutations > 0,
      'live combat actions did not route ordinary mutations through the effect resolver');
    assert(combatAfterActions.log.some(line =>
      line.includes('[Turn 1]') && line.includes('Resonator Staff')),
      'turn 1 action text was not logged correctly');
    assert(combatAfterActions.log.some(line =>
      line.includes('[Turn 1]') &&
      line.includes('Resonator Staff') &&
      !line.includes('Roll:')),
      'Staff Strike still exposed legacy dice text after formula migration');
    assert(combatAfterActions.log.some(line =>
      line.includes('[Turn 2]') && line.includes('Uncover Truth')),
      'turn 2 action text was not logged correctly');

    // Deterministic state-transition check. We test real keyboard combat
    // actions above; direct finishCombat avoids making the smoke test depend on
    // random damage rolls reaching victory.
    await page.evaluate(() => {
      if (typeof finishCombat !== 'function') throw new Error('finishCombat is unavailable');
      finishCombat();
    });

    await page.waitForFunction(() => window.gameState === 'world', undefined, { timeout: 5000 });

    const worldAfterCombat = await page.evaluate(() => ({
      vit: window._world.player.vit,
      scrap: window._world.player.scrap,
      aether: window._world.player.aether,
      heat: window._world.player.heat,
      echoes: window._world.player.echoes,
      staffCharges: window._world.player.staffCharges,
      level: window._world.player.level,
      xp: window._world.player.xp,
    }));

    assert(worldAfterCombat.vit === combatAfterActions.player.vit,
      'combat vitality was not written back to WORLD');
    assert(worldAfterCombat.scrap === combatAfterActions.player.scrap,
      'combat scrap was not written back to WORLD');
    assert(worldAfterCombat.aether === combatAfterActions.player.aether.current,
      'combat aether was not written back to WORLD');
    assert(worldAfterCombat.heat === combatAfterActions.player.heat.current,
      'combat heat was not written back to WORLD');
    assert(worldAfterCombat.echoes === combatAfterActions.player.echoes.current,
      'combat echoes were not written back to WORLD');
    assert(worldAfterCombat.staffCharges === combatAfterActions.player.staffCharges,
      'combat staff charges were not written back to WORLD');

    const rosterAfterCombat = await page.evaluate(() => ({
      vit: window.ROSTER[0].vit,
      scrap: window.ROSTER[0].scrap,
      aether: window.ROSTER[0].aether,
      heat: window.ROSTER[0].heat,
      echoes: window.ROSTER[0].echoes,
      staffCharges: window.ROSTER[0].staffCharges,
      worldLeadRef: window._world.player === window.ROSTER[0],
      activeLeadRef: window.ACTIVE_PARTY[0] === window.ROSTER[0],
    }));

    assert(rosterAfterCombat.vit === worldAfterCombat.vit,
      'combat vitality did not persist to canonical ROSTER[0]');
    assert(rosterAfterCombat.scrap === worldAfterCombat.scrap,
      'combat scrap did not persist to canonical ROSTER[0]');
    assert(rosterAfterCombat.aether === worldAfterCombat.aether,
      'combat aether did not persist to canonical ROSTER[0]');
    assert(rosterAfterCombat.heat === worldAfterCombat.heat,
      'combat heat did not persist to canonical ROSTER[0]');
    assert(rosterAfterCombat.echoes === worldAfterCombat.echoes,
      'combat echoes did not persist to canonical ROSTER[0]');
    assert(rosterAfterCombat.staffCharges === worldAfterCombat.staffCharges,
      'combat staff charges did not persist to canonical ROSTER[0]');
    assert(rosterAfterCombat.worldLeadRef && rosterAfterCombat.activeLeadRef,
      'canonical lead reference split after combat');

    const dedicatedResourceContract = await page.evaluate(() => {
      const productionStats = window._world.player.productionStats;
      const productionDerivedStats = window._world.player.productionDerivedStats;
      window._combat.init({
        vit: 13,
        scrap: 7,
        aether: { current: 4, max: 6 },
        heat: { current: 1, max: 3 },
        echoes: { current: 3, max: 3 },
        charges: 0,
        staffMax: 2,
        level: 1,
        xp: 0,
        xpToNext: 50,
        unlockedAbilities: ['uncoverTruth','sharedDream','mycelialLedger'],
        productionStats,
        productionDerivedStats,
        productionStatModelVersion: '0.1.0',
      });
      window._combat.beginEncounter('skyPredator');
      const before = window._combat.getState();
      const result = window._combat.resolveTurn('staffStrike', null);
      const after = window._combat.getState();
      startCombat('skyPredator');
      return {
        result,
        beforeTurn: before.turn,
        afterTurn: after.turn,
        reason: after.actionUseEligibility.staffStrike.reason,
        log: after.log,
      };
    });
    assert(dedicatedResourceContract.result === false,
      'zero-charge Staff Strike was not rejected');
    assert(dedicatedResourceContract.beforeTurn === 0 &&
           dedicatedResourceContract.afterTurn === 0,
      'zero-charge Staff Strike consumed a turn');
    assert(dedicatedResourceContract.reason === 'insufficient_dedicated_resource',
      'zero-charge Staff Strike did not expose dedicated-resource rejection');

    const uncoverTruthContract = await page.evaluate(() => {
      const originalRandom = window.random;
      try {
        startCombat('skyPredator');
        const before = window._combat.getState();
        const result = window._combat.resolveTurn('uncoverTruth', null);
        const analyzed = window._combat.getState();
        const revealedWeakness = analyzed.enemy && analyzed.enemy.analysis &&
          analyzed.enemy.analysis.revealedWeakness;
        const chargesBeforeStrike = analyzed.enemy && analyzed.enemy.analysis &&
          analyzed.enemy.analysis.charges;
        const analysisLog = analyzed.log.slice();

        // Formula damage uses bounded injected RNG via p5 random. Keep values
        // deterministic enough to prove analysis consumption, not exact damage.
        window.random = function(min, max) {
          if (max !== undefined) return (min + max) / 2;
          if (min !== undefined) return min * 0.5;
          return 0.5;
        };
        window._combat.resolveTurn('staffStrike', null);
        const afterStrike = window._combat.getState();

        return {
          result,
          beforeTurn: before.turn,
          afterAnalysisTurn: analyzed.turn,
          revealedWeakness,
          chargesBeforeStrike,
          analysisCleared: !afterStrike.enemy.analysis,
          analysisLog,
          afterStrikeLog: afterStrike.log.slice(),
        };
      } finally {
        window.random = originalRandom;
        startCombat('skyPredator');
      }
    });

    assert(uncoverTruthContract.beforeTurn === 0 &&
           uncoverTruthContract.afterAnalysisTurn === 1,
      'Uncover Truth did not consume exactly one turn');
    assert(typeof uncoverTruthContract.revealedWeakness === 'string' &&
           uncoverTruthContract.revealedWeakness.length > 0,
      'Uncover Truth did not reveal the authored weakness');
    assert(uncoverTruthContract.chargesBeforeStrike === 1,
      'Uncover Truth did not establish a single-use analysis window');
    assert(uncoverTruthContract.analysisCleared === true,
      'analysis window was not consumed by the next damaging action');
    assert(uncoverTruthContract.analysisLog.some(line =>
      line.includes('Uncover Truth') &&
      line.includes('Target analyzed') &&
      !line.includes('Roll:')),
      'Uncover Truth still exposed legacy dice text or failed to log analysis');

    const commonsLedgerContract = await page.evaluate(() => {
      startCombat('skyPredator');
      const before = window._combat.getState();
      const beforeResources = {
        scrap: before.player.scrap,
        aether: before.player.aether.current,
        heat: before.player.heat.current,
      };
      const result = window._combat.resolveTurn('mycelialLedger', null);
      const after = window._combat.getState();
      return {
        result,
        beforeTurn: before.turn,
        afterTurn: after.turn,
        beforeResources,
        afterResources: {
          scrap: after.player.scrap,
          aether: after.player.aether.current,
          heat: after.player.heat.current,
        },
        ledger: after.commonsLedgerEntry,
        log: after.log.slice(),
      };
    });
    assert(commonsLedgerContract.result !== false,
      'Mycelial Ledger read-only action was rejected');
    assert(commonsLedgerContract.beforeTurn === 0 &&
           commonsLedgerContract.afterTurn === 1,
      'Mycelial Ledger did not consume exactly one turn');
    assert(JSON.stringify(commonsLedgerContract.beforeResources) ===
           JSON.stringify(commonsLedgerContract.afterResources),
      'Mycelial Ledger mutated scrap, aether, or Heat');
    assert(commonsLedgerContract.ledger &&
           commonsLedgerContract.ledger.owner === 'ender' &&
           commonsLedgerContract.ledger.accessMode === 'mycelial-commons' &&
           commonsLedgerContract.ledger.readOnly === true,
      'live Commons Ledger entry is missing or violates owner/access boundary');
    assert(Array.isArray(commonsLedgerContract.ledger.unknowns),
      'Commons Ledger did not preserve explicit unknowns');
    assert(commonsLedgerContract.log.some(line =>
      line.includes('Mycelial Ledger') && !line.includes('Roll:')),
      'Mycelial Ledger still exposes legacy dice text');

    const aetherSealLiveContract = await page.evaluate(() => {
      const originalRandom = window.random;
      try {
        window._combat.init({
          vit: 13,
          scrap: 7,
          aether: { current: 6, max: 6 },
          heat: { current: 0, max: 3 },
          echoes: { current: 3, max: 3 },
          charges: 2,
          staffMax: 2,
          level: 4,
          xp: 0,
          xpToNext: 168,
          unlockedAbilities: ['uncoverTruth','sharedDream','mycelialLedger','windWard','aetherSeal'],
          productionStats: window._world.player.productionStats,
          productionDerivedStats: window._world.player.productionDerivedStats,
          productionStatModelVersion: '0.1.0',
        });

        // Force enemy-turn hit branches so suppression must actually prevent drain.
        window.random = function(min, max) {
          if (max !== undefined) {
            if (min === 1 && max === 4) return 3;
            return (min + max) / 2;
          }
          if (min !== undefined) return min * 0.5;
          return 0.5;
        };

        window._combat.beginEncounter('aetherLeak');
        const beforeSeal = window._combat.getState();
        const sealResult = window._combat.resolveTurn('aetherSeal', null);
        const afterSeal = window._combat.getState();
        const aetherAfterSeal = afterSeal.player.aether.current;
        const suppressionAfterSeal = afterSeal.enemy.aetherSuppression;

        window._combat.resolveTurn('hold', null);
        const afterSecondSuppressedTurn = window._combat.getState();

        window._combat.init({
          vit: 13,
          scrap: 7,
          aether: { current: 6, max: 6 },
          heat: { current: 0, max: 3 },
          echoes: { current: 3, max: 3 },
          charges: 2,
          staffMax: 2,
          level: 4,
          xp: 0,
          xpToNext: 168,
          unlockedAbilities: ['uncoverTruth','sharedDream','mycelialLedger','windWard','aetherSeal'],
        });
        window._combat.beginEncounter('skyPredator');
        const beforeRejected = window._combat.getState();
        const rejectedResult = window._combat.resolveTurn('aetherSeal', null);
        const afterRejected = window._combat.getState();

        return {
          sealResult,
          beforeSealTurn: beforeSeal.turn,
          afterSealTurn: afterSeal.turn,
          aetherBeforeSeal: beforeSeal.player.aether.current,
          aetherAfterSeal,
          echoesBeforeSeal: beforeSeal.player.echoes.current,
          echoesAfterSeal: afterSeal.player.echoes.current,
          heatAfterSeal: afterSeal.player.heat.current,
          suppressionAfterSeal,
          aetherAfterSecondSuppressedTurn: afterSecondSuppressedTurn.player.aether.current,
          suppressionCleared: !afterSecondSuppressedTurn.enemy.aetherSuppression,
          sealLog: afterSeal.log.slice(),
          rejectedResult,
          rejectedBeforeTurn: beforeRejected.turn,
          rejectedAfterTurn: afterRejected.turn,
          rejectedBeforeEchoes: beforeRejected.player.echoes.current,
          rejectedAfterEchoes: afterRejected.player.echoes.current,
          rejectedBeforeAether: beforeRejected.player.aether.current,
          rejectedAfterAether: afterRejected.player.aether.current,
          rejectedLog: afterRejected.log.slice(),
        };
      } finally {
        window.random = originalRandom;
        startCombat('skyPredator');
      }
    });

    assert(aetherSealLiveContract.sealResult !== false,
      'Aether Seal was rejected on explicitly Aether-dependent target');
    assert(aetherSealLiveContract.beforeSealTurn === 0 &&
           aetherSealLiveContract.afterSealTurn === 1,
      'Aether Seal did not consume exactly one turn');
    assert(aetherSealLiveContract.echoesBeforeSeal === 3 &&
           aetherSealLiveContract.echoesAfterSeal === 0,
      'Aether Seal did not pay its existing three-point pooled resource cost');
    assert(aetherSealLiveContract.aetherBeforeSeal === 6 &&
           aetherSealLiveContract.aetherAfterSeal === 6 &&
           aetherSealLiveContract.aetherAfterSecondSuppressedTurn === 6,
      'Aether Seal failed to suppress Wraith Aether drain for two enemy turns');
    assert(aetherSealLiveContract.heatAfterSeal === 1,
      'Aether Seal did not preserve current Heat-generation policy');
    assert(aetherSealLiveContract.suppressionAfterSeal &&
           aetherSealLiveContract.suppressionAfterSeal.remainingTurns === 1,
      'Aether Seal suppression did not establish/decrement correctly');
    assert(aetherSealLiveContract.suppressionCleared === true,
      'Aether Seal suppression did not expire after two enemy turns');
    assert(aetherSealLiveContract.sealLog.some(line =>
      line.includes('Aether Seal') && !line.includes('Roll:')),
      'Aether Seal still exposes legacy dice text');

    assert(aetherSealLiveContract.rejectedResult === false,
      'Aether Seal did not fail closed on non-Aether-dependent target');
    assert(aetherSealLiveContract.rejectedBeforeTurn === 0 &&
           aetherSealLiveContract.rejectedAfterTurn === 0,
      'rejected Aether Seal consumed a turn');
    assert(aetherSealLiveContract.rejectedBeforeEchoes ===
           aetherSealLiveContract.rejectedAfterEchoes &&
           aetherSealLiveContract.rejectedBeforeAether ===
           aetherSealLiveContract.rejectedAfterAether,
      'rejected Aether Seal consumed resources');
    assert(aetherSealLiveContract.rejectedLog.some(line =>
      line.includes('Aether Seal cannot bind')),
      'rejected Aether Seal did not expose fail-closed reason');

    const flightBefore = await page.evaluate(() => {
      finishCombat();
      if (typeof enterAirNavigation !== 'function') {
        throw new Error('enterAirNavigation unavailable');
      }
      const entered = enterAirNavigation();
      return {
        entered,
        gameState: window.gameState,
        x: window._airNavigationState && window._airNavigationState.x,
        y: window._airNavigationState && window._airNavigationState.y,
        moored: window._airNavigationState && window._airNavigationState.mooredLandmarkId,
        altitude: window._airNavigationState && window._airNavigationState.altitude,
      };
    });
    assert(flightBefore.entered === true && flightBefore.gameState === 'airship',
      'open-sky flight state did not activate');
    assert(flightBefore.moored === 'wake-dock',
      'flight did not begin moored at Wake Dock');

    await page.keyboard.press('ArrowRight');
    const flightAfterMove = await page.evaluate(() => ({
      gameState: window.gameState,
      x: window._airNavigationState && window._airNavigationState.x,
      y: window._airNavigationState && window._airNavigationState.y,
      moored: window._airNavigationState && window._airNavigationState.mooredLandmarkId,
      weatherId: window._airNavigationState && window._airNavigationState.weatherId,
    }));
    assert(flightAfterMove.gameState === 'airship',
      'flight movement left the airship state unexpectedly');
    assert(flightAfterMove.moored === null,
      'first flight movement did not cast off from berth');
    assert(flightAfterMove.x > flightBefore.x,
      'flight movement did not advance sky position');

    if (errors.length) {
      throw new Error('browser errors:\n' + errors.join('\n'));
    }

    console.log('To Sail the Starry Sky smoke test: PASS');
    console.log(JSON.stringify({
      openingBootstrap,
      beforeLyraJoin,
      afterLyraJoin,
      partyArchitecture,
      enemyMetadataContract,
      affordabilityContract,
      progressionReachability,
      blockedResidueContract,
      effectContract,
      registryContract,
      resolverContract,
      worldBeforeCombat,
      combatTurns: combatAfterActions.turn,
      enemy: combatAfterActions.enemy && combatAfterActions.enemy.name,
      worldAfterCombat,
      flightBefore,
      flightAfterMove,
    }, null, 2));
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(err => {
  console.error('To Sail the Starry Sky smoke test: FAIL');
  console.error(err.stack || err.message || String(err));
  process.exit(1);
});
