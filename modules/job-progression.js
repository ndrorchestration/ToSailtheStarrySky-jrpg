/* Aetherwake — hybrid job/loadout design contract v0.1.
 * Non-executable: no combat, party, persistence, or equipment binding.
 * Identity, job proficiency, magic mastery and learned techniques remain distinct.
 */
(function (root, factory) {
  const canon = typeof module === 'object' && module.exports
    ? require('./character-canon.js')
    : root.AetherwakeCharacterCanon;
  const api = factory(canon);
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.AetherwakeJobProgression = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (canon) {
  'use strict';
  if (!canon || typeof canon.get !== 'function') {
    throw new Error('JOB_PROGRESSION_REQUIRES_CHARACTER_CANON');
  }

  const VERSION = '0.1.0';
  const STATUS = 'DESIGN_ONLY_NOT_RUNTIME_AUTHORIZED';
  const JOB_ID = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
  const own = (obj, key) => Object.prototype.hasOwnProperty.call(obj, key);

  function validId(id) {
    return typeof id === 'string' && JOB_ID.test(id) &&
      id !== 'constructor' && id !== 'prototype' && id !== '__proto__';
  }

  function nativeJobOf(characterId) {
    const character = typeof characterId === 'string' ? canon.get(characterId) : null;
    if (!character) throw new Error('JOB_PROGRESSION_UNKNOWN_CHARACTER:' + characterId);
    return character.nativeJob || null;
  }

  function normalizedProfile(input) {
    if (!input || typeof input !== 'object' || Array.isArray(input)) {
      throw new Error('JOB_PROGRESSION_PROFILE_REQUIRED');
    }
    const nativeJob = nativeJobOf(input.characterId);
    if (input.nativeJob !== nativeJob) {
      throw new Error('JOB_PROGRESSION_NATIVE_IDENTITY_MISMATCH');
    }
    for (const slot of ['primaryJobId', 'secondaryJobId']) {
      if (input[slot] !== null && !validId(input[slot])) {
        throw new Error('JOB_PROGRESSION_INVALID_SLOT:' + slot);
      }
    }
    if (input.secondaryJobId !== null && input.primaryJobId === null) {
      throw new Error('JOB_PROGRESSION_SECONDARY_REQUIRES_PRIMARY');
    }
    if (input.primaryJobId !== null && input.primaryJobId === input.secondaryJobId) {
      throw new Error('JOB_PROGRESSION_DUPLICATE_EQUIPPED_JOB');
    }
    if (!input.jobRanks || typeof input.jobRanks !== 'object' ||
        Array.isArray(input.jobRanks)) {
      throw new Error('JOB_PROGRESSION_RANKS_REQUIRED');
    }
    const jobRanks = {};
    for (const id of Object.keys(input.jobRanks)) {
      const rank = input.jobRanks[id];
      if (!validId(id) || !Number.isInteger(rank) || rank < 1 || rank > 5) {
        throw new Error('JOB_PROGRESSION_INVALID_RANK:' + id);
      }
      jobRanks[id] = rank;
    }
    return Object.freeze({
      schemaVersion: 1,
      characterId: input.characterId,
      nativeJob,
      primaryJobId: input.primaryJobId,
      secondaryJobId: input.secondaryJobId,
      jobRanks: Object.freeze(jobRanks),
      runtimeStatus: STATUS
    });
  }

  function createProfile(characterId) {
    return normalizedProfile({
      characterId, nativeJob: nativeJobOf(characterId),
      primaryJobId: null, secondaryJobId: null, jobRanks: {}
    });
  }

  function validateProfile(profile) {
    if (!profile || profile.schemaVersion !== 1 || profile.runtimeStatus !== STATUS) {
      throw new Error('JOB_PROGRESSION_UNSUPPORTED_PROFILE');
    }
    return normalizedProfile(profile);
  }

  function admittedJob(registry, jobId, slot) {
    if (!registry || typeof registry !== 'object' || Array.isArray(registry) ||
        !own(registry, jobId)) return false;
    const job = registry[jobId];
    return !!(job && job.id === jobId && job.status === 'admitted' &&
      Array.isArray(job.allowedSlots) && job.allowedSlots.includes(slot));
  }

  function evaluateEquip(profile, next, registry) {
    const current = validateProfile(profile);
    if (!next || typeof next !== 'object' ||
        !own(next, 'primaryJobId') || !own(next, 'secondaryJobId')) {
      throw new Error('JOB_PROGRESSION_EXPLICIT_TWO_SLOT_REQUEST_REQUIRED');
    }
    const reasons = [];
    for (const [slot, id] of [
      ['primary', next.primaryJobId],
      ['secondary', next.secondaryJobId]
    ]) {
      if (id !== null && !validId(id)) reasons.push('invalid_' + slot + '_job');
      else if (id !== null && !admittedJob(registry, id, slot)) {
        reasons.push(slot + '_job_not_admitted');
      }
    }
    if (next.secondaryJobId !== null && next.primaryJobId === null) {
      reasons.push('secondary_requires_primary');
    }
    if (next.primaryJobId !== null && next.primaryJobId === next.secondaryJobId) {
      reasons.push('same_job_in_both_slots');
    }
    return Object.freeze({
      eligible: reasons.length === 0,
      reasons: Object.freeze(reasons),
      retainedNativeJob: current.nativeJob,
      runtimeStatus: STATUS
    });
  }

  function equipJobs(profile, next, registry) {
    const current = validateProfile(profile);
    const result = evaluateEquip(current, next, registry);
    if (!result.eligible) {
      throw new Error('JOB_PROGRESSION_EQUIP_BLOCKED:' + result.reasons.join(','));
    }
    return normalizedProfile(Object.assign({}, current, {
      primaryJobId: next.primaryJobId,
      secondaryJobId: next.secondaryJobId
    }));
  }

  function evaluateJobRank(profile, jobId, rank, registry) {
    const current = validateProfile(profile);
    const reasons = [];
    if (!validId(jobId) || !admittedJob(registry, jobId, 'primary')) {
      reasons.push('job_not_admitted_for_training');
    }
    if (!Number.isInteger(rank) || rank < 1 || rank > 5) {
      reasons.push('invalid_rank');
    } else if (rank !== (current.jobRanks[jobId] || 0) + 1) {
      reasons.push('rank_must_advance_one');
    }
    return Object.freeze({
      eligible: reasons.length === 0,
      reasons: Object.freeze(reasons),
      runtimeStatus: STATUS
    });
  }

  function recordJobRank(profile, jobId, rank, registry) {
    const current = validateProfile(profile);
    const check = evaluateJobRank(current, jobId, rank, registry);
    if (!check.eligible) {
      throw new Error('JOB_PROGRESSION_RANK_BLOCKED:' + check.reasons.join(','));
    }
    return normalizedProfile(Object.assign({}, current, {
      jobRanks: Object.assign({}, current.jobRanks, { [jobId]: rank })
    }));
  }

  // Explicit transfer contract. Learned != executable: all outputs are
  // design-only, and magic/weapon systems must independently authorize use.
  function evaluateTechnique(profile, technique, learnedTechniqueIds, registry) {
    const current = validateProfile(profile);
    const reasons = [];
    if (!technique || typeof technique !== 'object' ||
        typeof technique.id !== 'string' || technique.status !== 'admitted') {
      reasons.push('technique_not_admitted');
    }
    if (!Array.isArray(learnedTechniqueIds) ||
        !technique || !learnedTechniqueIds.includes(technique.id)) {
      reasons.push('technique_not_learned');
    }
    if (technique && technique.kind === 'native') {
      if (technique.ownerCharacterId !== current.characterId) {
        reasons.push('different_native_owner');
      }
    } else if (technique && technique.kind === 'job') {
      const source = technique.sourceJobId;
      if (!validId(source) || !admittedJob(registry, source, 'primary')) {
        reasons.push('source_job_not_admitted');
      } else if (source !== current.primaryJobId && source !== current.secondaryJobId) {
        const target = current.primaryJobId;
        if (technique.transferPolicy !== 'explicit-cross-job' ||
            !Array.isArray(technique.allowedPrimaryTargets) ||
            target === null || !technique.allowedPrimaryTargets.includes(target)) {
          reasons.push('job_not_equipped_or_transfer_not_approved');
        }
      }
    } else {
      reasons.push('external_magic_weapon_or_party_gate_required');
    }
    return Object.freeze({
      eligibleForFutureIntegration: reasons.length === 0,
      executable: false,
      reasons: Object.freeze(reasons),
      runtimeStatus: STATUS
    });
  }

  return Object.freeze({
    VERSION, STATUS, createProfile, validateProfile, evaluateEquip,
    equipJobs, evaluateJobRank, recordJobRank, evaluateTechnique
  });
});
