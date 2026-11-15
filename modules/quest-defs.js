/* ============================================================
   Aetherwake — Declarative Quest Definitions v0.1
   Issue #265 tranche 1. Proposal-safe runtime contracts only.
   ============================================================ */

(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.AetherQuestDefs = api;
})(typeof window !== 'undefined' ? window :
   (typeof globalThis !== 'undefined' ? globalThis : null), function () {
  'use strict';

  const VERSION = '0.1.0';
  const SCHEMA_VERSION = 1;

  const AURORAL_REQUIRED_PARTY_IDS = Object.freeze([
    'ender', 'lyra', 'ionia', 'reson', 'aepex'
  ]);

  const QUESTS = Object.freeze({
    'QST-A1-001': Object.freeze({
      id: 'QST-A1-001',
      kind: 'main-wake',
      authority: 'IMPLEMENTATION_SEED',
      initialState: 'OPENING',
      terminalState: 'COMPLETE',
      optional: false,
      hardPrerequisites: Object.freeze([]),
      transitions: Object.freeze({
        OPENING: Object.freeze(['WRONG_SONG_NOTICED']),
        WRONG_SONG_NOTICED: Object.freeze(['PRACTICAL_RESPONSE']),
        PRACTICAL_RESPONSE: Object.freeze(['CHAPTER_CARD']),
        CHAPTER_CARD: Object.freeze(['COMPLETE']),
        COMPLETE: Object.freeze([])
      })
    }),
    'QST-A1-002': Object.freeze({
      id: 'QST-A1-002',
      kind: 'crew-corroboration',
      authority: 'PROPOSAL',
      initialState: 'AVAILABLE',
      terminalState: 'COMPLETE',
      optional: true,
      hardPrerequisites: Object.freeze(['DSC-A1-001']),
      transitions: Object.freeze({
        AVAILABLE: Object.freeze(['CHECKED', 'SKIPPED']),
        CHECKED: Object.freeze(['COMPLETE']),
        SKIPPED: Object.freeze(['COMPLETE']),
        COMPLETE: Object.freeze([])
      })
    }),
    'QST-A1-003': Object.freeze({
      id: 'QST-A1-003',
      kind: 'side-quest',
      authority: 'PROPOSAL',
      initialState: 'AVAILABLE',
      terminalState: 'COMPLETE',
      optional: true,
      hardPrerequisites: Object.freeze([]),
      transitions: Object.freeze({
        AVAILABLE: Object.freeze(['FULL_PREP', 'PARTIAL_PREP', 'MINIMAL_PREP', 'SKIPPED']),
        FULL_PREP: Object.freeze(['COMPLETE']),
        PARTIAL_PREP: Object.freeze(['COMPLETE']),
        MINIMAL_PREP: Object.freeze(['COMPLETE']),
        SKIPPED: Object.freeze(['COMPLETE']),
        COMPLETE: Object.freeze([])
      })
    })
  });

  const DISCOVERIES = Object.freeze({
    'DSC-A1-001': Object.freeze({
      id: 'DSC-A1-001',
      kind: 'observation',
      authority: 'IMPLEMENTATION_SEED',
      discoveryChannels: Object.freeze(['OBSERVED', 'CARTOGRAPHIC']),
      establishes: Object.freeze(['OBSERVATION_RECORDED']),
      doesNotEstablish: Object.freeze([
        'PORTAL_CONFIRMED',
        'AURORAL_ROUTE_AUTHORIZED',
        'GLOBAL_CAUSE_CONFIRMED'
      ])
    }),
    'SEC-A1-001': Object.freeze({
      id: 'SEC-A1-001',
      kind: 'secret-clue',
      authority: 'PROPOSAL',
      discoveryChannels: Object.freeze(['ENVIRONMENTAL', 'DEDUCTIVE']),
      establishes: Object.freeze(['SECRET_CLUE_RECORDED']),
      doesNotEstablish: Object.freeze([
        'AURORAL_ROUTE_AUTHORIZED',
        'GLOBAL_CAUSE_CONFIRMED'
      ])
    })
  });

  const ROUTES = Object.freeze({
    'RTE-A1-001': Object.freeze({
      id: 'RTE-A1-001',
      authority: 'ABSTRACT_MAPPING',
      allowedStates: Object.freeze([
        'OPEN_NORMAL',
        'DEGRADED',
        'EMERGENCY',
        'RESTRICTED_AFTER_EVENT',
        'RESTORED_OR_ADAPTED'
      ])
    })
  });

  const WORLD_STATES = Object.freeze({
    'WS-A1-001': Object.freeze({
      id: 'WS-A1-001',
      authority: 'PROPOSAL_STATE_CONTRACT'
    })
  });

  function allDefinitions() {
    return { QUESTS, DISCOVERIES, ROUTES, WORLD_STATES };
  }

  return Object.freeze({
    VERSION,
    SCHEMA_VERSION,
    AURORAL_REQUIRED_PARTY_IDS,
    QUESTS,
    DISCOVERIES,
    ROUTES,
    WORLD_STATES,
    allDefinitions
  });
});
