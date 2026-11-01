'use strict';
// Isolated design-contract tests: illustrative fixtures, NOT game balance numbers.
const assert = require('node:assert/strict');
const { validate, contract } = require('../tools/validate-level-one-stat-ranks.js');

assert.equal(contract.numeric_values_approved, false);
assert.equal(contract.gameplay_implementation_authorized, false);
assert.deepEqual(contract.strict_rank_rules.map(r => r.stat), ['mag','mp','hp']);

const sample = {
  ender: { hp: 100, mp: 120, mag: 30 },
  lyra:  { hp: 80,  mp: 100, mag: 25 },
  ionia: { hp: 125, mp: 60,  mag: 12 },
  reson: { hp: 140, mp: 50,  mag: 11 },
  aepex: { hp: 115, mp: 70,  mag: 15 },
};
assert.equal(validate(sample).valid, true);

function mutation(id, stat, value) {
  const next = structuredClone(sample);
  next[id][stat] = value;
  return validate(next);
}
assert.equal(mutation('ender', 'mag', 25).valid, false, 'MAG ties must reject');
assert.equal(mutation('lyra', 'mp', 60).valid, false, 'MP ties with remainder must reject');
assert.equal(mutation('ender', 'hp', 80).valid, false, 'HP tie with Lyra must reject');
assert.equal(mutation('aepex', 'hp', 99).valid, false, 'Aepex must exceed Ender HP');
assert.equal(mutation('ionia', 'mag', 26).valid, false, 'Ionia must not exceed Lyra MAG');
assert.equal(mutation('reson', 'mp', 101).valid, false, 'Reson must not exceed Lyra MP');
assert.equal(mutation('ender', 'hp', '100').valid, false, 'numeric strings forbidden');

const missing = structuredClone(sample); delete missing.lyra;
assert.equal(validate(missing).valid, false, 'missing protagonist must reject');
const extra = structuredClone(sample); extra.talen = { hp:99, mp:99, mag:99 };
assert.equal(validate(extra).valid, false, 'guest/child cannot silently enter roster');
assert.equal(validate(null).valid, false);
console.log('Level 1 creator rank constraints (design-only): PASS');
