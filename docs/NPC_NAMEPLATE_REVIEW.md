# Clearer NPC nameplates, November 13

NPCs and trainers now use a dark navy, gold-edged identity plate with a separate, readable 14-pixel damaged-health row and proportional gold health bar. Full-health residents use the shorter identity-only panel. Existing names, trainer levels, RECOVERING state, exact health and reward/combat behavior remain.

This is the NPC/trainer portion of the requested name-tag upgrade, not new player overhead tags. The existing client scheduler still shows one nearby interaction name and at most one additional damaged resident, plus one speech bubble. It keeps its 13/18-stud name selection and 24-stud speech selection. Native billboard occlusion remains enabled; the ordinary server MaxDistance is 18 and the existing trainer override is 65.

Vault consultation: `05 UI and UX/Nametags and Overhead Bars - Cost and Visibility Rules`, targeted current guidance on occlusion, bounded visible labels and avoiding duplicate built-in displays. No imported asset, dependency, new loop or connection. The richer plate adds five GUI descendants per NPC (seven total); this is not a zero-cost or performance guarantee.

## Native correction and visual result

The first larger candidate overlapped its speech text in Studio. The final source shares the same world anchor between speech and nameplate and uses size-relative offset to maintain six logical pixels between their canvases. Speech helper, content and visibility gates remain; speech placement intentionally changes. A separate 14-pixel health row is easier to read than the initial 11-pixel candidate.

- [Before](images/npc-nameplates-2026-11-13/before.jpg) and [final after](images/npc-nameplates-2026-11-13/after.jpg): same source-controlled ordinary Custom camera at 12.806 studs player-to-trainer distance, within the existing 13-stud interaction range. Speech, identity and 132/220 HP are simultaneously readable. Actual text-fit values pass; one name and one speech selected.
- [Native occlusion](images/npc-nameplates-2026-11-13/occluded.jpg): both labels remain enabled but are hidden behind an opaque fixture wall. The wall is non-queryable, so this is not combat line-of-sight evidence. It was removed afterward.
- Final on-screen boundary probes keep a healthy name hidden at 13.1 studs, damaged name visible at 17.9 and hidden at 18.1. An earlier off-screen probe was invalid and is not counted as a game failure.
- Full/damaged/recovering/restored fixture records retain identity, health-row visibility, fill and immediate UpdateBot reset/anchor behavior. Native font allocation fits four sampled authored identities. These use simulated health records linked to native objects, not actual combat/KO or full NPC lifecycle proof.

## Verification and cleanup

Independent source review passed 137 focused assertions, four source contracts and eight negative controls; retained resident-label checks pass 6. Final local aggregate passes 240 commands: 25 pure/synthetic suites, 129 mocked suites, 64 production compiles and requested builds. All 326 input fingerprints and log hash were rechecked. Not CI.

Exact source was verified in a disposable PlaceId 0/GameId 0 game with temporary profiles before Play. Three asset-type warnings were present; their origin was not established. Play stopped, original edit World restored and Client unchanged; original local binary hash retained. Only the matching task-created Studio process closed; PC left on. No live DataStore, cloud save or publication.

[Machine-readable evidence](../tests/evidence/npc-nameplates-2026-11-13.json). Independent reviewer accepted the final damaged/speech view. Physical devices, OS text scaling, crowded scenes, actual combat and performance remain unverified. Player target readout is unchanged. Existing real-microphone/multiplayer and mixed-version quest-writer release gates remain open.
