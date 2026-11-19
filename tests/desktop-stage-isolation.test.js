const assert = require('assert');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const repo = path.resolve(__dirname, '..');
const stage = path.join(repo, '.desktop-runtime');
const www = path.join(stage, 'www');
const stageScript = path.join(repo, 'scripts', 'stage-memories-desktop.js');
const sourcePackage = JSON.parse(fs.readFileSync(path.join(repo, 'package.json'), 'utf8'));

const runtimeFiles = [
  'index-embedded.html',
  'aetherwake.js',
  'p5.min.js',
  'embedded-fonts.css',
  'icon.svg',
  'icon.ico',
];
const forbiddenNames = new Set([
  'tests',
  'docs',
  '.github',
  'node_modules',
  'cache',
  'package-lock.json',
]);

let checks = 0;

function check(condition, message) {
  checks += 1;
  assert(condition, message);
}

function sortedEntries(directory) {
  return fs.readdirSync(directory).sort();
}

function assertRealDirectory(directory, label) {
  check(fs.existsSync(directory), `${label}: directory is missing`);
  const stat = fs.lstatSync(directory);
  check(stat.isDirectory() && !stat.isSymbolicLink(), `${label}: expected a real directory`);
}

function assertRegularFile(filePath, label) {
  check(fs.existsSync(filePath), `${label}: file is missing`);
  const stat = fs.lstatSync(filePath);
  check(stat.isFile() && !stat.isSymbolicLink(), `${label}: expected a regular non-symlink file`);
}

function hashFile(filePath) {
  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
}

function compareFile(sourcePath, stagedPath, label) {
  assertRegularFile(sourcePath, `${label}: source`);
  assertRegularFile(stagedPath, `${label}: staged`);
  const source = fs.readFileSync(sourcePath);
  const staged = fs.readFileSync(stagedPath);
  check(source.equals(staged), `${label}: staged bytes differ from source`);
  check(hashFile(sourcePath) === hashFile(stagedPath), `${label}: SHA-256 differs`);
}

function compareTree(sourceRoot, stagedRoot, label) {
  assertRealDirectory(sourceRoot, `${label}: source`);
  assertRealDirectory(stagedRoot, `${label}: staged`);

  const sourceEntries = sortedEntries(sourceRoot);
  const stagedEntries = sortedEntries(stagedRoot);
  check(
    JSON.stringify(sourceEntries) === JSON.stringify(stagedEntries),
    `${label}: entry set differs\nsource=${sourceEntries.join(',')}\nstaged=${stagedEntries.join(',')}`
  );

  for (const entry of sourceEntries) {
    const sourcePath = path.join(sourceRoot, entry);
    const stagedPath = path.join(stagedRoot, entry);
    const sourceStat = fs.lstatSync(sourcePath);
    const stagedStat = fs.lstatSync(stagedPath);
    check(sourceStat.isDirectory() === stagedStat.isDirectory(), `${label}/${entry}: type differs`);
    check(!sourceStat.isSymbolicLink() && !stagedStat.isSymbolicLink(), `${label}/${entry}: symlinks are not allowed`);

    if (sourceStat.isDirectory()) {
      compareTree(sourcePath, stagedPath, `${label}/${entry}`);
    } else {
      compareFile(sourcePath, stagedPath, `${label}/${entry}`);
    }
  }
}

function assertNoForbiddenContent(root) {
  for (const name of forbiddenNames) {
    check(!fs.existsSync(path.join(root, name)), `${root}: forbidden content present: ${name}`);
  }
}

function verifyStage() {
  assertRealDirectory(stage, 'desktop stage');
  assertRealDirectory(www, 'desktop www');

  const expectedRoot = ['package.json', 'www'];
  const actualRoot = sortedEntries(stage);
  check(
    JSON.stringify(actualRoot) === JSON.stringify(expectedRoot),
    `stage root entry set differs: ${actualRoot.join(',')}`
  );

  const expectedWww = [...runtimeFiles, 'modules'].sort();
  const actualWww = sortedEntries(www);
  check(
    JSON.stringify(actualWww) === JSON.stringify(expectedWww),
    `stage www entry set differs: ${actualWww.join(',')}`
  );

  assertNoForbiddenContent(stage);
  assertNoForbiddenContent(www);

  for (const file of runtimeFiles) {
    compareFile(path.join(repo, file), path.join(www, file), `www/${file}`);
  }
  compareTree(path.join(repo, 'modules'), path.join(www, 'modules'), 'www/modules');

  const stagedPackagePath = path.join(stage, 'package.json');
  assertRegularFile(stagedPackagePath, 'stage/package.json');
  const stagedPackage = JSON.parse(fs.readFileSync(stagedPackagePath, 'utf8'));
  check(stagedPackage.main === 'www/index-embedded.html', 'staged package main must be www/index-embedded.html');
  check(stagedPackage.main !== sourcePackage.main, 'staged package must not use the development root entrypoint');
  check(stagedPackage.version === sourcePackage.version, 'staged package version must match source package version');
}

const stageResult = spawnSync(process.execPath, [stageScript], {
  cwd: repo,
  encoding: 'utf8',
  stdio: 'inherit',
});
check(stageResult.status === 0, `stage script failed with exit code ${stageResult.status}`);

verifyStage();
const sourceAetherwake = path.join(repo, 'aetherwake.js');
const stagedAetherwake = path.join(www, 'aetherwake.js');
console.log(`SHA256_SOURCE_AETHERWAKE=${hashFile(sourceAetherwake)}`);
console.log(`SHA256_STAGED_AETHERWAKE=${hashFile(stagedAetherwake)}`);
console.log('POSITIVE_STAGE_ISOLATION=PASS');

// Disposable negative control: an injected development-only directory must fail,
// then be removed so the generated stage is restored exactly.
const negativeSentinel = path.join(www, 'tests');
try {
  fs.mkdirSync(negativeSentinel, { recursive: true });
  fs.writeFileSync(path.join(negativeSentinel, 'sentinel.txt'), 'negative-control\n', 'utf8');
  assert.throws(
    () => verifyStage(),
    /entry set differs|forbidden content present/,
    'synthetic development-only sentinel should invalidate the stage'
  );
  console.log('NEGATIVE_CONTROL=PASS (synthetic www/tests sentinel rejected)');
} finally {
  fs.rmSync(negativeSentinel, { recursive: true, force: true });
}

verifyStage();
console.log('NEGATIVE_CONTROL_CLEANUP=PASS');
console.log(`DESKTOP_STAGE_ISOLATION_CHECKS=${checks}`);
console.log('Aetherwake desktop stage isolation contract: PASS');
