/* ============================================================
   Aetherwake — First Wake Quest Adapter v0.1
   Maps established opening scenes into the tranche-1 quest state.
   Does not alter authored scene order or party joins.
   ============================================================ */

(function (root, factory) {
  'use strict';
  const opening = (typeof module === 'object' && module.exports)
    ? require('./first-wake-opening.js')
    : (root && root.AetherFirstWakeOpening);
  const questState = (typeof module === 'object' && module.exports)
    ? require('./quest-state.js')
    : (root && root.AetherQuestState);
  const api = factory(opening, questState);
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.AetherFirstWakeQuestAdapter = api;
})(typeof window !== 'undefined' ? window :
   (typeof globalThis !== 'undefined' ? globalThis : null), function (Opening, QuestState) {
  'use strict';

  if (!Opening) throw new Error('FIRST_WAKE_OPENING_REQUIRED');
  if (!QuestState) throw new Error('QUEST_STATE_REQUIRED');

  const VERSION = '0.1.0';

  function ensureMainQuest(snapshot) {
    if (!QuestState.getQuest(snapshot, 'QST-A1-001')) {
      QuestState.activate(snapshot, 'QST-A1-001');
    }
    return QuestState.getQuest(snapshot, 'QST-A1-001');
  }

  function applyScene(snapshot, sceneOrId) {
    const scene = typeof sceneOrId === 'string'
      ? Opening.SCENES.find(item => item.id === sceneOrId)
      : sceneOrId;
    if (!scene || !scene.id) throw new Error('FIRST_WAKE_ADAPTER_SCENE_REQUIRED');

    const main = ensureMainQuest(snapshot);

    if (scene.id === 'lyra_join') {
      if (main.state === 'OPENING') {
        QuestState.transition(snapshot, 'QST-A1-001', 'WRONG_SONG_NOTICED');
      }
      QuestState.discover(snapshot, 'DSC-A1-001', {
        source: 'ENDER_FIELD_OBSERVATION',
        observation: 'shield-frequency echo overlaps a displaced spatial relation',
        interpretationStatus: 'UNRESOLVED',
        doesNotEstablish: [
          'PORTAL_CONFIRMED',
          'AURORAL_ROUTE_AUTHORIZED',
          'GLOBAL_CAUSE_CONFIRMED'
        ]
      });
      QuestState.recordEvidence(snapshot, 'LOR-A1-001', {
        status: 'OBSERVED',
        sources: ['ENDER_FIELD_OBSERVATION'],
        confidence: 'LOW',
        supports: ['HYP-SPATIAL_RELATION_MISMATCH'],
        doesNotEstablish: [
          'PORTAL_CONFIRMED',
          'AURORAL_ROUTE_AUTHORIZED',
          'GLOBAL_CAUSE_CONFIRMED'
        ]
      });
    }

    if (scene.id === 'ionia_practical') {
      const current = QuestState.getQuest(snapshot, 'QST-A1-001');
      if (current.state === 'WRONG_SONG_NOTICED') {
        QuestState.transition(snapshot, 'QST-A1-001', 'PRACTICAL_RESPONSE');
      }
    }

    if (scene.id === 'first_wake_card') {
      const current = QuestState.getQuest(snapshot, 'QST-A1-001');
      if (current.state === 'PRACTICAL_RESPONSE') {
        QuestState.transition(snapshot, 'QST-A1-001', 'CHAPTER_CARD');
      }
      const ready = QuestState.getQuest(snapshot, 'QST-A1-001');
      if (ready.state === 'CHAPTER_CARD') {
        QuestState.complete(snapshot, 'QST-A1-001', 'OPENING_COMPLETE');
      }
    }

    return snapshot;
  }

  function applyCurrentScene(snapshot, openingState) {
    return applyScene(snapshot, Opening.currentScene(openingState));
  }

  return Object.freeze({
    VERSION,
    applyScene,
    applyCurrentScene
  });
});
