#!/usr/bin/env node
// Copyright remains with this project. Engine-free export; NEVER grants an executable ability.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const sourceRoot = path.resolve(__dirname, '../..');
const elemental = require(path.join(sourceRoot, 'modules/elemental-spell-trees.js'));
const nonElemental = require(path.join(sourceRoot, 'modules/non-elemental-spell-trees.js'));
const output = path.join(sourceRoot, 'unreal/DesignCatalog/ALL_MAGIC_SEEDS_DESIGN_ONLY.json');

function fail(reason) { throw new Error('MAGIC_CATALOG_EXPORT_REJECTED: ' + reason); }
function toManifest() {
  const seeds = [];
  const allIds = new Set();
  for (const [family, catalog, expectedTrees] of [
    ['elemental', elemental, 11],
    ['non-elemental', nonElemental, 15]
  ]) {
    if (!catalog || !catalog.runtimeStatus ||
        !catalog.runtimeStatus.includes('NOT_EXECUTABLE')) fail('source is not design-only: ' + family);
    const trees = Object.values(catalog.TREES);
    if (trees.length !== expectedTrees) fail('unexpected school count: ' + family);
    for (const tree of trees) {
      const school = family === 'elemental' ? tree.treeId : tree.domainId;
      if (!school || !tree.ranks) fail('missing school/ranks: ' + family);
      if (family === 'non-elemental' && (!tree.status || !tree.access)) {
        fail('lost domain provenance/status: ' + school);
      }
      for (let rank = 1; rank <= 5; ++rank) {
        const stage = tree.ranks[rank];
        if (!stage || !Array.isArray(stage.spells) || stage.spells.length !== 2) {
          fail('unexpected stage count: ' + school + ':' + rank);
        }
        for (const entry of stage.spells) {
          if (!entry.id || !entry.name || !Array.isArray(entry.roles) ||
              !entry.intent || allIds.has(entry.id)) {
            fail('invalid or duplicate spell: ' + String(entry.id));
          }
          allIds.add(entry.id);
          const requirements = (entry.requiresMastery || []).map(req => {
            const dependency = req.tree || req.domain;
            if (!dependency || !Number.isInteger(req.rank) ||
                req.rank < 1 || req.rank > 5) fail('invalid dependency: ' + entry.id);
            return { school: dependency, minimumRank: req.rank };
          });
          seeds.push({
            id: entry.id, name: entry.name, family, school, rank,
            stage: stage.label,
            status: family === 'non-elemental' ? tree.status : 'admitted-elemental-design',
            access: family === 'non-elemental' ? tree.access : 'registered-elemental-tree',
            roles: [...entry.roles],
            intent: entry.intent,
            requiresMastery: requirements,
            admission: 'DesignOnly', executable: false,
            // Absent = intentionally unauthored. Do NOT fill these with defaults.
            effect: null, targeting: null, resourceCost: null,
            vfxAsset: null, animationAsset: null
          });
        }
      }
    }
  }
  seeds.sort((a, b) => a.id.localeCompare(b.id, 'en'));
  if (seeds.length !== 260 ||
      seeds.filter(s => s.family === 'elemental').length !== 110 ||
      seeds.filter(s => s.family === 'non-elemental').length !== 150 ||
      seeds.some(s => s.executable !== false || s.admission !== 'DesignOnly')) {
    fail('count or executable-admission drift');
  }
  return {
    schema: 'tstss.unreal.magic-review-catalog.v1',
    generatedFrom: [
      'modules/elemental-spell-trees.js',
      'modules/non-elemental-spell-trees.js'
    ],
    // The Unreal row model has fewer prerequisites than some design seeds:
    // JSON is authoritative for source-side review, not an executable DataTable.
    sourceRuntime: 'DESIGN_ONLY',
    counts: { schools: 26, elemental: 110, nonElemental: 150, total: 260 },
    seeds
  };
}

function main() {
  const command = process.argv[2] || '--summary';
  if (!['--check', '--write', '--summary'].includes(command) || process.argv.length > 3) {
    fail('expected --check, --write or --summary');
  }
  const content = JSON.stringify(toManifest(), null, 2) + '\n';
  if (command === '--write') {
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, content, 'utf8');
    process.stdout.write('WROTE design-only 260-seed review catalog: ' + output + '\n');
  } else if (command === '--check') {
    if (!fs.existsSync(output) || fs.readFileSync(output, 'utf8') !== content) {
      fail('generated output missing or stale; run --write');
    }
    process.stdout.write('PASS: reproducible 260-seed design-only catalog; NOT native gameplay\n');
  } else {
    process.stdout.write('PASS: 260 distinct design-only seeds; no executable magic authorized\n');
  }
}
try { main(); } catch (error) { process.stderr.write(error.message + '\n'); process.exitCode = 1; }
