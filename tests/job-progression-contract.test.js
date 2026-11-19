'use strict';
const assert = require('node:assert/strict');
const canon = require('../modules/character-canon.js');
const magic = require('../modules/character-magic-profile.js');
const jobs = require('../modules/job-progression.js');

const registry = Object.freeze({
  'test-primary': Object.freeze({
    id: 'test-primary', status: 'admitted', allowedSlots: ['primary']
  }),
  'test-support': Object.freeze({
    id: 'test-support', status: 'admitted', allowedSlots: ['primary', 'secondary']
  }),
  'test-other': Object.freeze({
    id: 'test-other', status: 'admitted', allowedSlots: ['primary']
  }),
  'test-unapproved': Object.freeze({
    id: 'test-unapproved', status: 'candidate', allowedSlots: ['primary', 'secondary']
  })
});
// Fixture-only IDs intentionally have no implication of canon approval.

const ender = jobs.createProfile('ender');
assert.equal(ender.nativeJob, 'Rift Scholar');
assert.equal(ender.primaryJobId, null);
assert.equal(ender.secondaryJobId, null);
assert.equal(ender.runtimeStatus, 'DESIGN_ONLY_NOT_RUNTIME_AUTHORIZED');
assert.equal(ender.schemaVersion, 1);
assert.deepEqual(ender.jobRanks, {});
assert(Object.isFrozen(ender));
assert(Object.isFrozen(ender.jobRanks));
assert.throws(() => { ender.nativeJob = 'Generic Mage'; }, TypeError);

for (const characterId of ['ender', 'lyra', 'ionia', 'reson', 'aepex']) {
  const profile = jobs.createProfile(characterId);
  assert.equal(profile.nativeJob, canon.get(characterId).nativeJob || null);
}
assert.throws(() => jobs.createProfile('not-a-protagonist'), /UNKNOWN_CHARACTER/);
assert.throws(() => jobs.validateProfile({ ...ender, nativeJob: null }), /NATIVE_IDENTITY_MISMATCH/);
assert.throws(() => jobs.validateProfile({ ...ender, runtimeStatus: 'LIVE' }), /UNSUPPORTED_PROFILE/);
assert.throws(() => jobs.validateProfile({ ...ender, jobRanks: { 'test-primary': 6 } }), /INVALID_RANK/);
assert.throws(() => jobs.validateProfile({ ...ender, jobRanks: { 'test-primary': 0 } }), /INVALID_RANK/);
assert.throws(() => jobs.validateProfile({ ...ender, primaryJobId: '__proto__' }), /INVALID_SLOT/);
assert.throws(() => jobs.validateProfile({ ...ender, primaryJobId: null, secondaryJobId: 'test-support' }), /SECONDARY_REQUIRES_PRIMARY/);
assert.throws(() => jobs.validateProfile({ ...ender, primaryJobId: 'test-support', secondaryJobId: 'test-support' }), /DUPLICATE_EQUIPPED_JOB/);
assert.throws(() => jobs.evaluateEquip(ender, { primaryJobId: 'test-primary' }, registry), /TWO_SLOT/);

assert.equal(jobs.evaluateEquip(ender, { primaryJobId: 'test-primary', secondaryJobId: null }, {}).eligible, false);
assert.equal(jobs.evaluateEquip(ender, { primaryJobId: 'test-unapproved', secondaryJobId: null }, registry).eligible, false);
assert.equal(jobs.evaluateEquip(ender, { primaryJobId: null, secondaryJobId: 'test-support' }, registry).eligible, false);
assert.equal(jobs.evaluateEquip(ender, { primaryJobId: 'test-primary', secondaryJobId: 'test-primary' }, registry).eligible, false);
assert.equal(jobs.evaluateEquip(ender, { primaryJobId: 'test-primary', secondaryJobId: 'test-other' }, registry).eligible, false);
assert.throws(() => jobs.equipJobs(ender, { primaryJobId: 'test-unapproved', secondaryJobId: null }, registry), /EQUIP_BLOCKED/);
assert.equal(jobs.evaluateEquip(ender, { primaryJobId: 'test-primary', secondaryJobId: 'test-support' }, registry).eligible, true);

const equipped = jobs.equipJobs(ender, {
  primaryJobId: 'test-primary', secondaryJobId: 'test-support'
}, registry);
assert.equal(equipped.nativeJob, 'Rift Scholar');
assert.equal(equipped.primaryJobId, 'test-primary');
assert.equal(equipped.secondaryJobId, 'test-support');
assert.equal(ender.primaryJobId, null);

const swapped = jobs.equipJobs(equipped, {
  primaryJobId: 'test-other', secondaryJobId: 'test-support'
}, registry);
assert.equal(swapped.nativeJob, 'Rift Scholar');
assert.equal(swapped.primaryJobId, 'test-other');

assert.equal(jobs.evaluateJobRank(equipped, 'test-primary', 1, registry).eligible, true);
assert.equal(jobs.evaluateJobRank(equipped, 'test-primary', 2, registry).eligible, false);
assert.equal(jobs.evaluateJobRank(equipped, 'test-unapproved', 1, registry).eligible, false);
const ranked = jobs.recordJobRank(equipped, 'test-primary', 1, registry);
assert.equal(ranked.jobRanks['test-primary'], 1);
const rankedSwapped = jobs.equipJobs(ranked, {
  primaryJobId: 'test-other', secondaryJobId: 'test-support'
}, registry);
assert.equal(rankedSwapped.jobRanks['test-primary'], 1);
assert.equal(rankedSwapped.nativeJob, 'Rift Scholar');
assert.throws(() => jobs.recordJobRank(ranked, 'test-primary', 3, registry), /RANK_BLOCKED/);

const native = { id: 'observation-test', kind: 'native', ownerCharacterId: 'ender', status: 'admitted' };
const jobSkill = { id: 'staff-test', kind: 'job', sourceJobId: 'test-primary', status: 'admitted' };
assert.equal(jobs.evaluateTechnique(ranked, native, ['observation-test'], registry).eligibleForFutureIntegration, true);
assert.equal(jobs.evaluateTechnique(ranked, native, [], registry).eligibleForFutureIntegration, false);
assert.equal(jobs.evaluateTechnique(ranked, { ...native, ownerCharacterId: 'lyra' }, ['observation-test'], registry).eligibleForFutureIntegration, false);
assert.equal(jobs.evaluateTechnique(ranked, jobSkill, ['staff-test'], registry).eligibleForFutureIntegration, true);
assert.equal(jobs.evaluateTechnique(rankedSwapped, jobSkill, ['staff-test'], registry).eligibleForFutureIntegration, false);
const transferable = { ...jobSkill, transferPolicy: 'explicit-cross-job', allowedPrimaryTargets: ['test-other'] };
assert.equal(jobs.evaluateTechnique(rankedSwapped, transferable, ['staff-test'], registry).eligibleForFutureIntegration, true);
assert.equal(jobs.evaluateTechnique(rankedSwapped, { ...jobSkill, transferPolicy: 'explicit-cross-job' }, ['staff-test'], registry).eligibleForFutureIntegration, false);
assert.equal(jobs.evaluateTechnique(rankedSwapped, { ...jobSkill, status: 'candidate' }, ['staff-test'], registry).eligibleForFutureIntegration, false);
assert.equal(jobs.evaluateTechnique(rankedSwapped, { id: 'aether-test', kind: 'magic', status: 'admitted' }, ['aether-test'], registry).eligibleForFutureIntegration, false);
assert.equal(jobs.evaluateTechnique(rankedSwapped, jobSkill, ['staff-test'], registry).executable, false);

// Domain/learned-spell state is not coupled to this design-only job projection.
const magicBefore = magic.createProfile('ender');
const magicAfter = magic.createProfile('ender');
assert.deepEqual(magicAfter, magicBefore);
assert.deepEqual(magicAfter.innateAffinities, ['aether', 'resonance', 'correspondence', 'lumen']);
assert.deepEqual(magicAfter.learnedSpells, []);
assert.deepEqual(magicAfter.mastery, { trees: {}, domains: {} });

console.log('job-progression contract: PASS (identity, equip gates, mastery, transfer, isolation)');
