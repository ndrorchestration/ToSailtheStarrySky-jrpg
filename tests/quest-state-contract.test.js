const assert = require('assert');
const defs = require('../modules/quest-defs.js');
const questState = require('../modules/quest-state.js');
const opening = require('../modules/first-wake-opening.js');
const adapter = require('../modules/first-wake-quest-adapter.js');

assert.strictEqual(defs.VERSION, '0.1.0');
assert.strictEqual(questState.VERSION, '0.1.0');
assert.strictEqual(adapter.VERSION, '0.1.0');
assert.strictEqual(questState.validateDefinitions(), true);

const snapshot = questState.create();
const openingState = opening.createState();

adapter.applyCurrentScene(snapshot, openingState);
assert.strictEqual(questState.getQuest(snapshot, 'QST-A1-001').state, 'OPENING');

while (opening.currentScene(openingState).id !== 'lyra_join') {
  opening.advance(openingState);
}
adapter.applyCurrentScene(snapshot, openingState);

assert.strictEqual(questState.getQuest(snapshot, 'QST-A1-001').state, 'WRONG_SONG_NOTICED');
assert(snapshot.discoveries['DSC-A1-001'], 'Wrong Song must create the bounded Act I observation');
assert.strictEqual(snapshot.evidence['LOR-A1-001'].status, 'OBSERVED');
assert(snapshot.evidence['LOR-A1-001'].doesNotEstablish.includes('AURORAL_ROUTE_AUTHORIZED'));

opening.advance(openingState);
assert.strictEqual(opening.currentScene(openingState).id, 'ionia_practical');
adapter.applyCurrentScene(snapshot, openingState);
assert.strictEqual(questState.getQuest(snapshot, 'QST-A1-001').state, 'PRACTICAL_RESPONSE');

while (opening.currentScene(openingState).id !== 'first_wake_card') {
  opening.advance(openingState);
}
adapter.applyCurrentScene(snapshot, openingState);
assert.strictEqual(questState.getQuest(snapshot, 'QST-A1-001').status, 'COMPLETE');
assert.strictEqual(questState.getQuest(snapshot, 'QST-A1-001').state, 'COMPLETE');

assert.strictEqual(snapshot.quests['QST-A1-002'], undefined,
  'optional Ionia corroboration must not be required for opening completion');
assert.strictEqual(snapshot.quests['QST-A1-003'], undefined,
  'optional preparation side quest must not be required for opening completion');

questState.setWorldState(snapshot, 'WS-A1-001', {
  safety_state: 'PROVISIONAL',
  route_discrepancy_observed: true
});
questState.setRouteState(snapshot, 'RTE-A1-001', 'DEGRADED');
const roundTrip = questState.hydrate(questState.serialize(snapshot));
assert.deepStrictEqual(roundTrip.worldStates['WS-A1-001'], snapshot.worldStates['WS-A1-001']);
assert.deepStrictEqual(roundTrip.discoveries['DSC-A1-001'], snapshot.discoveries['DSC-A1-001']);
assert.deepStrictEqual(roundTrip.evidence['LOR-A1-001'], snapshot.evidence['LOR-A1-001']);
assert.strictEqual(roundTrip.routes['RTE-A1-001'], 'DEGRADED');

assert.strictEqual(questState.hasRequiredAuroralCrew(['ender','lyra','ionia','reson']), false);
assert.strictEqual(questState.hasRequiredAuroralCrew(['ender','lyra','ionia','reson','aepex']), true);
assert.strictEqual(questState.hasRequiredAuroralCrew(['ender','lyra','ionia','reson','reson']), false);
assert.strictEqual(questState.canAuthorizeAuroral({
  partyIds: ['ender','lyra','ionia','reson','aepex']
}), false, 'full crew alone must not authorize Auroral traversal');
assert.strictEqual(questState.canAuthorizeAuroral({
  partyIds: ['ender','lyra','ionia','reson','aepex'],
  shipReady: true,
  navigationReady: true,
  couplingReady: true,
  polarApproachKnown: true
}), true);

const malformed = {
  QUESTS: {
    'Q-A': {
      id: 'Q-A',
      initialState: 'A',
      terminalState: 'DONE',
      hardPrerequisites: ['Q-B'],
      transitions: { A: ['DONE'], DONE: [] }
    },
    'Q-B': {
      id: 'Q-B',
      initialState: 'A',
      terminalState: 'DONE',
      hardPrerequisites: ['Q-A'],
      transitions: { A: ['DONE'], DONE: [] }
    }
  },
  DISCOVERIES: {},
  ROUTES: {},
  WORLD_STATES: {}
};
assert.throws(() => questState.validateDefinitions(malformed), /QUEST_DEF_HARD_CYCLE/);

const duplicate = {
  QUESTS: {
    'DUP': {
      id: 'DUP',
      initialState: 'A',
      terminalState: 'DONE',
      hardPrerequisites: [],
      transitions: { A: ['DONE'], DONE: [] }
    }
  },
  DISCOVERIES: {
    'DUP': { id: 'DUP' }
  },
  ROUTES: {},
  WORLD_STATES: {}
};
assert.throws(() => questState.validateDefinitions(duplicate), /QUEST_DEF_DUPLICATE_ID/);

assert.strictEqual(opening.SCENES.length, 10, 'adapter must not rewrite First Wake scene count');
assert.strictEqual(opening.SCENES[6].id, 'lyra_join', 'adapter must not move Lyra join');
assert.strictEqual(opening.SCENES[6].joinCharacterId, 'lyra');

console.log('Aetherwake quest state tranche 1 contract: PASS');
