# Local Studio QA | November 16

The reviewed compact-city candidate ran in Studio Play Solo with temporary
profiles. All five boss rings and four supporting residents were present. The
Style panel showed the earned-coin gear tiers; selecting and clearing a boss
guide did not change the current quest. Successful guide selection is not a
native breadcrumb, device, real-voice, multiplayer, or live-save acceptance test.

The disposable imported-mesh pilot verified these three models:
- Academy Megaphone: buying for 100 of 1,000 test coins left 900; four imported
  mesh parts mounted with four welds instead of the runtime fallback.
- Pyro-Tenor Ignis: corrected mesh bounds 6.60 × 9.80 × 2.30 studs.
- DJ Marina: corrected mesh bounds 4.00 × 5.575 × 2.225 studs; original R6 rig retained.

The original boss/NPC FBXs imported 100 times too large. The generators use
FBX_SCALE_UNITS so scene units are encoded in FBX metadata; the corrected Ignis
FBX was re-imported natively and measured 6.60 × 9.80 × 2.30 studs without a
post-import scale correction. Remaining model imports should be checked
individually. Separate local test templates, Roblox asset IDs and temporary
review places are not committed. No Roblox place was published.

Code QA covers route expiry and low obstacles, landscape guide visibility,
boss idle work, and quest-giver indexing. Old-profile-writer compatibility
remains a live release gate. Keep the reviewed development branch separate
from main and do not publish the disposable fixture.
