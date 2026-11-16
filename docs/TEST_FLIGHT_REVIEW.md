# Local developer test flight

Reference decisions revisited: actual vault lightning movement reference/selected VFX safety guidance, `SIDEWAYS_DODGE_REVIEW.md`, and `DEVELOPER_TOOLS_REVIEW.md`. This is a separate original test-only movement feature, not borrowed demo combat logic. No runtime asset dependency or external credentials.

## Availability and isolation

Fly on/off appears in the existing Test Tools list only when Studio, PlaceId0, GameId0 and Workspace.LocalSustainedPrototype=true. Server `dev` independently checks current DeveloperAccess, the same local gates, and Commerce not busy. First authorized Fly uses existing sanitized baseline snapshot initialization. TestFlight itself also rejects missing authorization, nonlocal IDs, missing explicit bounds.localOnly and missing testBaseline. Current PrelaunchAllTesters does NOT expose Fly in published/shared preview.

No normal/live profile is mutated by flight. Temporary progress continues using the existing preserved-baseline save pathway. Turning flight off does not end the temporary test profile. Rejoin remains the way back to normal progress.

## Controls and cleanup

WASD moves relative to character heading, Space up and LeftCtrl down. Server accepts only three signed unit axis fields, normalizes diagonals, caps32stud/s and timestep.1, hovers after.3seconds without accepted input, and uses collision-respecting blockcasts. Horizontal map bounds retain8-stud margins; vertical range-4..220 supports coastal grounded roots without crossing rescue threshold-15. Starts reject anchored, seated, ragdolled, knocked or actively dodging characters.

Touch uses the existing joystick for horizontal movement plus44px FLY UP / FLY DOWN toggle buttons. Tapping the active vertical button stops ascent/descent; toggling the other switches direction. Text focus/menu opening sends zero axes; window focus loss clears vertical toggles. TestFlight status is server replicated. Physical phones/controllers and visual layout remain unverified.

The server anchors only the current character root, records its original CFrame, AutoRotate and network ownership, and returns/restores them on off. No BodyMover, constraint, attachment or physics helper instance is created. Death, character/root replacement, removal, authorization/local-guard loss, test-profile loss, departure and shutdown clean up. Client teardown requests an idempotent stop if active. Return-to-origin prevents using test flight to bypass traversal after switching off.

## Gameplay while flying

Existing attacks are canceled. Server rejects cast/dodge/sprint/talk/quest/commerce and other gameplay action verbs while flying; only Fly off, bounded flight input, idempotent stop, Sync and settings remain. PvP mode checks, bot/boss eligibility, existing trainer strikes, vehicle hits and direct quest prompt callbacks exclude flight. ActiveQuest/guide identity and quest progress remain; timed quest deadlines/start counters pause. An active soccer attempt is canceled (its independent callbacks must not award flight-assisted progress) without clearing quest identity. Restart that attempt after landing.

## Tests and native boundary

`tests/test_flight.py` executes the actual module with mocked character/physics, including local guards, missing baseline, malformed inputs, rate/diagonal/dt/bounds, stale input, obstruction, coastal start, unsafe starting posture and teardown cases. `developer_tools.py` executes the actual dev dispatcher to prove baseline-before-first-flight and preview rejection. `developer_tools_ui.py` executes the actual command list and button callback. `test_flight_input.py` executes the actual client controls with mocked WASD/vertical keys, touch toggles, focus/menu hover,10Hz cadence and teardown. Existing aggregate includes these checks.

Verified locally:39 module checks,101 developer dispatcher checks,63 test-panel checks and13 flight input checks; full26 pure/151 mocked aggregate and83 production scripts compile pass. All review builds also passed in the preceding26/150 run; the final additional suite only adds input tests. No native evidence claimed.

Native gate: first Fly click from coastal and academy ground; WASD and vertical controls; wall/ceiling collision; return-to-origin; respawn while active; deny published-like IDs; unavailable attack/quest prompts; verify saved baseline untouched. Synthetic tests do not establish Roblox networking, live saves, real devices or native physics.
