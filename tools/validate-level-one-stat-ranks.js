'use strict';

// Review-only Level 1 rank acceptance check. Does not modify game data or permit abilities.
// Usage: node tools/validate-level-one-stat-ranks.js path/to/candidate-stats.json
const fs = require('node:fs');
const contract = require('../data/design/level-one-rank-constraints.json');
const has = (obj, key) => Object.prototype.hasOwnProperty.call(obj, key);

function validate(candidate) {
  const errors = [];
  if (!candidate || typeof candidate !== 'object' || Array.isArray(candidate)) {
    return { valid: false, errors: ['CANDIDATE_OBJECT_REQUIRED'] };
  }

  // Demand all five protagonists and all three numeric metrics; fail closed.
  for (const id of contract.roster) {
    if (!has(candidate, id) || !candidate[id] ||
        typeof candidate[id] !== 'object' || Array.isArray(candidate[id])) {
      errors.push('MISSING_CHARACTER:' + id);
      continue;
    }
    for (const stat of Object.keys(contract.stats)) {
      const value = candidate[id][stat];
      if (!Number.isSafeInteger(value) || value < 0) {
        errors.push('INVALID_STAT:' + id + ':' + stat);
      }
    }
  }
  for (const id of Object.keys(candidate)) {
    if (!contract.roster.includes(id)) errors.push('UNEXPECTED_CHARACTER:' + id);
  }
  if (errors.length) return { valid: false, errors };

  for (const rule of contract.strict_rank_rules) {
    const { stat, direction, first, second } = rule;
    const highFirst = direction === 'descending';
    const before = (a, b) => highFirst ? a > b : a < b;
    if (!before(candidate[first][stat], candidate[second][stat])) {
      errors.push('RANK_ORDER:' + stat + ':' + first + ':' + second);
    }
    for (const id of contract.roster) {
      if (id === first || id === second) continue;
      if (!before(candidate[second][stat], candidate[id][stat])) {
        errors.push('RANK_REMAINDER:' + stat + ':' + second + ':' + id);
      }
    }
  }
  return { valid: errors.length === 0, errors };
}

module.exports = { validate, contract };

if (require.main === module) {
  const filename = process.argv[2];
  if (!filename) {
    process.stderr.write('Usage: node tools/validate-level-one-stat-ranks.js candidate.json\n');
    process.exitCode = 2;
  } else {
    try {
      const input = JSON.parse(fs.readFileSync(filename, 'utf8'));
      const result = validate(input);
      process.stdout.write(JSON.stringify(result, null, 2) + '\n');
      if (!result.valid) process.exitCode = 1;
    } catch (error) {
      process.stderr.write('INPUT_ERROR: ' + error.message + '\n');
      process.exitCode = 2;
    }
  }
}
