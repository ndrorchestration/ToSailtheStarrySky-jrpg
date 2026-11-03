const fs = require('fs');
const path = require('path');
const packageJson = require('../package.json');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(packageJson.main === 'index-embedded.html',
  'development manifest must retain the embedded HTML entry point');
assert(packageJson.window && packageJson.window.width === 1440,
  'desktop package window width must default to 1440');
assert(packageJson.window && packageJson.window.height === 960,
  'desktop package window height must default to 960');
assert(packageJson.window && packageJson.window.resizable === true,
  'desktop package window must remain resizable');
assert(packageJson.window.min_width === 960 && packageJson.window.min_height === 640,
  'desktop package minimum window must preserve the logical 960x640 game surface');
// This historical source contract must NOT force retention of a dangerous
// direct package:windows entrypoint or deprecated nw-builder dependency.
// Their presence is audit evidence, not a requirement for future code.
assert(packageJson.private === true,
  'historical npm desktop manifest must remain private');
const directPackageCommands = Object.keys(packageJson.scripts || {})
  .filter(name => /^package:windows(?:$|:)/.test(name));
if (directPackageCommands.length) {
  console.log('LEGACY_DIRECT_NPM_PACKAGE_COMMAND=UNGUARDED_SECURITY_HOLD: ' +
    directPackageCommands.join(', '));
}

const stageScript = fs.readFileSync(
  path.join(__dirname, '..', 'scripts', 'stage-memories-desktop.js'),
  'utf8'
);
assert(stageScript.includes("main: 'www/index-embedded.html'"),
  'production desktop manifest must use the RPG Maker MV-style www entrypoint');
assert(stageScript.includes("'icon.ico'"),
  'production desktop runtime must stage a Windows ICO asset');
assert(stageScript.includes('version: rootPackage.version'),
  'production desktop manifest must carry the project version for Windows metadata');
// Preserve the source stage icon without requiring the archived CLI to be callable.
assert(stageScript.includes("path.join(stage, 'package.json')"),
  'production desktop manifest must live at the launcher root');
assert(stageScript.includes("path.join(stage, 'www')"),
  'production game payload must live under www');
// Script-defined stage boundaries are tested above and in dedicated Python checks.

const workflow = fs.readFileSync(
  path.join(__dirname, '..', '.github', 'workflows', 'desktop-package.yml'),
  'utf8'
);

// The October security hold superseded the former live desktop publisher.
// Validate the *retired* workflow, not requirements for a forbidden release.
const activeWorkflow = workflow.split(/\r?\n/)
  .filter(line => !/^\s*#/.test(line)).join('\n');
assert(workflow.includes('# SECURITY HOLD'),
  'retired desktop workflow must retain its explicit security hold');
assert(workflow.includes('name: Legacy NW.js Windows release — BLOCKED'),
  'historical desktop publisher must remain explicitly disabled');
assert(/^\s*workflow_dispatch:\s*$/m.test(activeWorkflow),
  'manual workflow entrypoint must remain an explicit denial path');
assert(!/^\s*(?:push|tags):/m.test(activeWorkflow),
  'retired publisher must not have push/tag triggers');
assert(/permissions:\s*\n\s*contents:\s*read/.test(activeWorkflow) &&
       !/\bcontents:\s*write\b/.test(activeWorkflow),
  'retired publisher must not regain a writable repository token');
assert(/Refuse manual execution[\s\S]*?exit 1/.test(activeWorkflow),
  'manual legacy workflow invocation must fail closed');
assert(!/softprops\/action-gh-release|gh\s+release\s+create|npm\s+ci|npm\s+run\s+package:windows|makensis|Start-Process|choco\s+install\s+nsis/i.test(activeWorkflow),
  'retired publisher must contain no installer, build, or release actions');
assert(!/uses:\s*(?:actions\/checkout|actions\/setup-node)/i.test(activeWorkflow),
  'manual denial workflow must not execute setup actions');

const readme = fs.readFileSync(path.join(__dirname, '..', 'README.md'), 'utf8');
const desktopGuide = fs.readFileSync(
  path.join(__dirname, '..', 'docs', 'DESKTOP_BUILD.md'),
  'utf8'
);
const localReleaseScript = fs.readFileSync(
  path.join(__dirname, '..', 'scripts', 'build-windows-release.ps1'),
  'utf8'
);
// Historical artifact labels may be retained, but an archived document must
// explicitly forbid using its outdated installer/download instructions.
assert(desktopGuide.startsWith('# Aetherwake Windows desktop build — RETIRED / SECURITY HOLD'),
  'historical player build guide must start with the current security hold');
assert(desktopGuide.includes('security classification remains unresolved') &&
       desktopGuide.includes('MUST NOT be executed') &&
       desktopGuide.includes('Everything below this warning is'),
  'old download/build instructions must be clearly superseded');
assert(desktopGuide.includes('Aetherwake-Setup.exe'),
  'historical guide must retain its original installer provenance');
assert(!desktopGuide.includes('Aetherwake-OneClick.exe'),
  'historical guide must not advertise obsolete SFX installers');
assert(!readme.includes('Aetherwake-OneClick.exe'),
  'legacy README must not advertise obsolete SFX installers');
// The archived local builder must reject execution BEFORE npm, NSIS or a game.
// These are source string checks; this test does not run any installer.
const activeLocal = localReleaseScript.split(/\r?\n/)
  .filter(line => !/^\s*#/.test(line)).join('\n');
const holdAt = activeLocal.indexOf('throw "SECURITY_HOLD_293:');
const firstLegacyAction = activeLocal.search(/\b(?:npm ci|npm run package:windows|makensis|Start-Process)\b/i);
assert(/^\s*\$ErrorActionPreference\s*=\s*"Stop"\s*\nthrow "SECURITY_HOLD_293:/m.test(activeLocal) &&
       holdAt >= 0 && firstLegacyAction > holdAt,
  'historical local builder must refuse before package or installer execution');
assert(localReleaseScript.includes('Get-ChildItem -LiteralPath $dist -Filter "Aetherwake.exe" -File -Recurse'),
  'local Windows release fallback must locate direct or nested nw-builder output');
assert(localReleaseScript.includes('LOCAL_WINDOWS_RELEASE=PASS'),
  'local Windows release fallback must emit an explicit success marker');
assert(localReleaseScript.includes('Start-Process -FilePath $installer'),
  'local Windows release fallback must install-smoke the generated installer');
assert(localReleaseScript.includes('Start-Process -FilePath $installedExe'),
  'local Windows release fallback must launch-smoke the installed game');
assert(localReleaseScript.includes('AETHERWAKE_DESKTOP_SMOKE_MARKER'),
  'local Windows release fallback must require application-level render readiness');
assert(localReleaseScript.includes('DESKTOP_RENDER_READINESS=PASS'),
  'local Windows release fallback must verify a rendered first frame');

console.log('Aetherwake archived desktop source layout and security hold: PASS (no build)');

const runtimeSource = fs.readFileSync(path.join(__dirname, '..', 'tosailthestarrysky.js'), 'utf8');
assert(runtimeSource.includes('function writeDesktopSmokeMarkerOnce()'),
  'runtime must expose a guarded desktop readiness marker writer');
assert(runtimeSource.includes('window.__awRuntimeReady') &&
       runtimeSource.includes('window.__awFirstFrame'),
  'desktop readiness marker must be bound to runtime-ready and completed-first-frame signals');

const embeddedHtmlForCanvas = fs.readFileSync(path.join(__dirname, '..', 'index-embedded.html'), 'utf8');
const runtimeSourceForCanvas = fs.readFileSync(path.join(__dirname, '..', 'tosailthestarrysky.js'), 'utf8');
assert(runtimeSourceForCanvas.includes('createCanvas(960, 640)'),
  'logical game canvas must remain 960x640 to preserve authored layout coordinates');
assert(embeddedHtmlForCanvas.includes('width: min(100vw, calc(100vh * 1.5))'),
  'desktop presentation must scale the 3:2 canvas to the largest fitting window area');

const embeddedDesktopControls = fs.readFileSync(path.join(__dirname, '..', 'index-embedded.html'), 'utf8');
assert(embeddedDesktopControls.includes('win.toggleFullscreen()'),
  'desktop entrypoint must expose a native fullscreen toggle');
assert(embeddedDesktopControls.includes("event.altKey && event.key === 'Enter'"),
  'desktop entrypoint must support Alt+Enter fullscreen');
assert(embeddedDesktopControls.includes("event.key === 'F11'"),
  'desktop entrypoint must support F11 fullscreen');
assert(embeddedDesktopControls.includes('win.leaveFullscreen()'),
  'desktop entrypoint must support leaving fullscreen with Escape');
