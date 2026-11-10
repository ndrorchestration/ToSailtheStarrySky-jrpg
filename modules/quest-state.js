/* ============================================================
   Aetherwake — Quest State Service v0.1
   Schema-versioned, fail-closed state for issue #265 tranche 1.
   ============================================================ */

(function (root, factory) {
  'use strict';
  const defs = (typeof module === 'object' && module.exports)
    ? require('./quest-defs.js')
    : (root && root.AetherQuestDefs);
  const api = factory(defs);
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.AetherQuestState = api;
})(typeof window !== 'undefined' ? window :
   (typeof globalThis !== 'undefined' ? globalThis : null), function (Defs) {
  'use strict';

  if (!Defs) throw new Error('QUEST_DEFS_REQUIRED');

  const VERSION = '0.1.0';

  function clone(value) {
    return value === undefined ? undefined : JSON.parse(JSON.stringify(value));
  }

  function create() {
    return {
      schemaVersion: Defs.SCHEMA_VERSION,
      quests: {},
      discoveries: {},
      worldStates: {},
      routes: {},
      evidence: {},
      secretChains: {}
    };
  }

  function getQuest(snapshot, id) {
    requireSnapshot(snapshot);
    return snapshot.quests[id] || null;
  }

  function requirementSatisfied(snapshot, id, context) {
    if (snapshot.quests[id] && snapshot.quests[id].status === 'COMPLETE') return true;
    if (snapshot.discoveries[id]) return true;
    if (Object.prototype.hasOwnProperty.call(snapshot.worldStates, id)) return true;
    const satisfied = context && Array.isArray(context.satisfiedIds) ? context.satisfiedIds : [];
    return satisfied.includes(id);
  }

  function canActivate(snapshot, id, context) {
    requireSnapshot(snapshot);
    const def = Defs.QUESTS[id];
    if (!def || snapshot.quests[id]) return false;
    return def.hardPrerequisites.every(req => requirementSatisfied(snapshot, req, context));
  }

  function activate(snapshot, id, context) {
    if (!canActivate(snapshot, id, context)) {
      throw new Error('QUEST_ACTIVATION_NOT_AUTHORIZED:' + id);
    }
    const def = Defs.QUESTS[id];
    snapshot.quests[id] = {
      status: 'ACTIVE',
      state: def.initialState,
      resolution: null
    };
    return snapshot.quests[id];
  }

  function transition(snapshot, id, targetState) {
    requireSnapshot(snapshot);
    const def = Defs.QUESTS[id];
    const current = snapshot.quests[id];
    if (!def || !current || current.status !== 'ACTIVE') {
      throw new Error('QUEST_TRANSITION_NOT_AUTHORIZED:' + id);
    }
    const allowed = def.transitions[current.state] || [];
    if (!allowed.includes(targetState)) {
      throw new Error('QUEST_TRANSITION_INVALID:' + id + ':' + current.state + '->' + targetState);
    }
    current.state = targetState;
    if (targetState === def.terminalState) current.status = 'COMPLETE';
    return current;
  }

  function complete(snapshot, id, resolution) {
    requireSnapshot(snapshot);
    const def = Defs.QUESTS[id];
    const current = snapshot.quests[id];
    if (!def || !current || current.status !== 'ACTIVE') {
      throw new Error('QUEST_COMPLETION_NOT_AUTHORIZED:' + id);
    }
    const allowed = def.transitions[current.state] || [];
    if (!allowed.includes(def.terminalState)) {
      throw new Error('QUEST_COMPLETION_INVALID:' + id + ':' + current.state);
    }
    current.state = def.terminalState;
    current.status = 'COMPLETE';
    current.resolution = resolution || null;
    return current;
  }

  function discover(snapshot, id, evidence) {
    requireSnapshot(snapshot);
    const def = Defs.DISCOVERIES[id];
    if (!def) throw new Error('DISCOVERY_UNKNOWN:' + id);
    if (!snapshot.discoveries[id]) {
      snapshot.discoveries[id] = {
        status: 'OBSERVED',
        evidence: []
      };
    }
    if (evidence !== undefined) snapshot.discoveries[id].evidence.push(clone(evidence));
    return snapshot.discoveries[id];
  }

  function recordEvidence(snapshot, id, record) {
    requireSnapshot(snapshot);
    if (!id) throw new Error('EVIDENCE_ID_REQUIRED');
    if (!record || typeof record !== 'object') throw new Error('EVIDENCE_RECORD_REQUIRED:' + id);
    snapshot.evidence[id] = clone(record);
    return snapshot.evidence[id];
  }

  function setWorldState(snapshot, id, value) {
    requireSnapshot(snapshot);
    if (!Defs.WORLD_STATES[id]) throw new Error('WORLD_STATE_UNKNOWN:' + id);
    snapshot.worldStates[id] = clone(value);
    return snapshot.worldStates[id];
  }

  function getWorldState(snapshot, id) {
    requireSnapshot(snapshot);
    return Object.prototype.hasOwnProperty.call(snapshot.worldStates, id)
      ? snapshot.worldStates[id]
      : null;
  }

  function setRouteState(snapshot, id, value) {
    requireSnapshot(snapshot);
    const def = Defs.ROUTES[id];
    if (!def) throw new Error('ROUTE_STATE_UNKNOWN:' + id);
    if (!def.allowedStates.includes(value)) {
      throw new Error('ROUTE_STATE_INVALID:' + id + ':' + value);
    }
    snapshot.routes[id] = value;
    return snapshot.routes[id];
  }

  function getRouteState(snapshot, id) {
    requireSnapshot(snapshot);
    return Object.prototype.hasOwnProperty.call(snapshot.routes, id)
      ? snapshot.routes[id]
      : null;
  }

  function hasRequiredAuroralCrew(partyIds) {
    if (!Array.isArray(partyIds)) return false;
    const unique = new Set(partyIds);
    return Defs.AURORAL_REQUIRED_PARTY_IDS.every(id => unique.has(id));
  }

  function canAuthorizeAuroral(context) {
    if (!context || typeof context !== 'object') return false;
    return hasRequiredAuroralCrew(context.partyIds) &&
      context.shipReady === true &&
      context.navigationReady === true &&
      context.couplingReady === true &&
      context.polarApproachKnown === true;
  }

  function serialize(snapshot) {
    validateSnapshot(snapshot);
    return JSON.stringify(snapshot);
  }

  function hydrate(serialized) {
    const snapshot = typeof serialized === 'string' ? JSON.parse(serialized) : clone(serialized);
    validateSnapshot(snapshot);
    return snapshot;
  }

  function requireSnapshot(snapshot) {
    if (!snapshot || typeof snapshot !== 'object') throw new Error('QUEST_SNAPSHOT_REQUIRED');
    if (snapshot.schemaVersion !== Defs.SCHEMA_VERSION) {
      throw new Error('QUEST_SNAPSHOT_SCHEMA_UNSUPPORTED:' + snapshot.schemaVersion);
    }
  }

  function validateSnapshot(snapshot) {
    requireSnapshot(snapshot);
    for (const id of Object.keys(snapshot.quests || {})) {
      if (!Defs.QUESTS[id]) throw new Error('QUEST_SNAPSHOT_UNKNOWN_QUEST:' + id);
      const entry = snapshot.quests[id];
      const def = Defs.QUESTS[id];
      if (!entry || !def.transitions[entry.state]) {
        throw new Error('QUEST_SNAPSHOT_INVALID_STATE:' + id);
      }
      if (!['ACTIVE', 'COMPLETE'].includes(entry.status)) {
        throw new Error('QUEST_SNAPSHOT_INVALID_STATUS:' + id);
      }
      if (entry.status === 'COMPLETE' && entry.state !== def.terminalState) {
        throw new Error('QUEST_SNAPSHOT_COMPLETE_STATE_MISMATCH:' + id);
      }
    }
    for (const id of Object.keys(snapshot.discoveries || {})) {
      if (!Defs.DISCOVERIES[id]) throw new Error('QUEST_SNAPSHOT_UNKNOWN_DISCOVERY:' + id);
    }
    for (const id of Object.keys(snapshot.worldStates || {})) {
      if (!Defs.WORLD_STATES[id]) throw new Error('QUEST_SNAPSHOT_UNKNOWN_WORLD_STATE:' + id);
    }
    for (const [id, value] of Object.entries(snapshot.routes || {})) {
      const def = Defs.ROUTES[id];
      if (!def) throw new Error('QUEST_SNAPSHOT_UNKNOWN_ROUTE:' + id);
      if (!def.allowedStates.includes(value)) {
        throw new Error('QUEST_SNAPSHOT_INVALID_ROUTE_STATE:' + id + ':' + value);
      }
    }
    return true;
  }

  function validateDefinitions(defsOverride) {
    const d = defsOverride || Defs;
    const groups = [
      d.QUESTS || {},
      d.DISCOVERIES || {},
      d.ROUTES || {},
      d.WORLD_STATES || {}
    ];
    const seen = new Set();
    for (const group of groups) {
      for (const [key, def] of Object.entries(group)) {
        if (!def || def.id !== key) throw new Error('QUEST_DEF_ID_MISMATCH:' + key);
        if (seen.has(key)) throw new Error('QUEST_DEF_DUPLICATE_ID:' + key);
        seen.add(key);
      }
    }

    for (const [id, quest] of Object.entries(d.QUESTS || {})) {
      if (!quest.transitions || !quest.transitions[quest.initialState] || !quest.transitions[quest.terminalState]) {
        throw new Error('QUEST_DEF_TRANSITIONS_INVALID:' + id);
      }
      for (const req of quest.hardPrerequisites || []) {
        if (!seen.has(req)) throw new Error('QUEST_DEF_UNKNOWN_PREREQUISITE:' + id + ':' + req);
      }
      for (const [from, targets] of Object.entries(quest.transitions)) {
        if (!Array.isArray(targets)) throw new Error('QUEST_DEF_TARGETS_INVALID:' + id + ':' + from);
        for (const target of targets) {
          if (!Object.prototype.hasOwnProperty.call(quest.transitions, target)) {
            throw new Error('QUEST_DEF_UNKNOWN_STATE:' + id + ':' + target);
          }
        }
      }
    }

    const questGraph = {};
    for (const [id, quest] of Object.entries(d.QUESTS || {})) {
      questGraph[id] = (quest.hardPrerequisites || []).filter(req => (d.QUESTS || {})[req]);
    }
    const visiting = new Set();
    const visited = new Set();
    function visit(id) {
      if (visiting.has(id)) throw new Error('QUEST_DEF_HARD_CYCLE:' + id);
      if (visited.has(id)) return;
      visiting.add(id);
      for (const next of questGraph[id] || []) visit(next);
      visiting.delete(id);
      visited.add(id);
    }
    for (const id of Object.keys(questGraph)) visit(id);

    return true;
  }

  validateDefinitions();

  return Object.freeze({
    VERSION,
    create,
    getQuest,
    canActivate,
    activate,
    transition,
    complete,
    discover,
    recordEvidence,
    setWorldState,
    getWorldState,
    setRouteState,
    getRouteState,
    hasRequiredAuroralCrew,
    canAuthorizeAuroral,
    serialize,
    hydrate,
    validateSnapshot,
    validateDefinitions
  });
});
