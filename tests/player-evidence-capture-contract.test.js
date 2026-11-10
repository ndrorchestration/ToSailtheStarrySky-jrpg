const assert = require('assert');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const scriptPath = path.join(ROOT, 'scripts', 'capture-player-evidence.js');
const packagePath = path.join(ROOT, 'package.json');
const smokeWorkflowPath = path.join(ROOT, '.github', 'workflows', 'smoke.yml');
const smokeProgramPath = path.join(ROOT, 'tests', 'smoke-playwright.js');
const developmentPath = path.join(ROOT, 'docs', 'DEVELOPMENT.md');

assert(fs.existsSync(scriptPath), 'player evidence capture script must exist');

const source = fs.readFileSync(scriptPath, 'utf8');
const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
const smokeWorkflow = fs.readFileSync(smokeWorkflowPath, 'utf8');
const smokeProgram = fs.readFileSync(smokeProgramPath, 'utf8');
const development = fs.readFileSync(developmentPath, 'utf8');

assert.strictEqual(
  pkg.scripts['capture:player-evidence'],
  'node scripts/capture-player-evidence.js',
  'package.json must expose the local player evidence capture command'
);

assert.strictEqual(
  pkg.scripts['test:player-evidence-capture'],
  'node tests/player-evidence-capture-contract.test.js',
  'package.json must expose the player evidence capture contract test'
);

assert.strictEqual(
  smokeWorkflow.split(/\r?\n/, 1)[0],
  'name: To Sail the Starry Sky smoke',
  'smoke workflow must display the canonical To Sail the Starry Sky project name'
);

// Only human-facing smoke log labels are rebranded. Keep historical
// environment/config and package identities until compatibility is tested.
assert(
  smokeProgram.includes("console.log('To Sail the Starry Sky smoke test: PASS');"),
  'smoke success log must display the current game title'
);
assert(
  smokeProgram.includes("console.error('To Sail the Starry Sky smoke test: FAIL');"),
  'smoke failure log must display the current game title'
);
assert(
  !smokeProgram.includes('Aetherwake smoke test:'),
  'smoke output must not mislabel current test runs as Aetherwake'
);
assert(
  smokeProgram.includes('process.env.AETHERWAKE_TEST_PORT'),
  'legacy test-port override must remain compatible'
);

assert(
  smokeWorkflow.includes('npm run test:player-evidence-capture'),
  'smoke workflow must guard the player evidence capture contract'
);

assert(
  development.includes('npm run capture:player-evidence'),
  'development guide must document the local player evidence capture command'
);

for (const required of [
  'AETHERWAKE_PLAYER_EVIDENCE=CAPTURED',
  'AETHERWAKE_PLAYER_EVIDENCE_DIR=',
  'humanAcceptance: \'PENDING\'',
  'visualAcceptance: \'PENDING\'',
  'gameplayCaptureInspected: false',
  'git rev-parse HEAD',
  'index-embedded.html',
  'arrival_horizon',
  'lyra_join',
  'Captain Ionia',
  'Aetherwake.exe',
]) {
  assert(source.includes(required), `capture script must include required authority marker: ${required}`);
}

for (const forbidden of [
  "keyboard.press('KeyN')",
  'VISUAL_ACCEPTANCE=PASS',
  'HUMAN_PLAYER_ACCEPTANCE=PASS',
  'visualApproval: true',
]) {
  assert(!source.includes(forbidden), `capture script must not contain unsafe shortcut/approval marker: ${forbidden}`);
}

console.log('PLAYER_EVIDENCE_CAPTURE_CONTRACT=PASS');
