-- Assign the privately uploaded original loop only after owner approval.
return {
 LoopAssetId = "", -- assets/audio/energy-beam-loop.wav; no upload performed yet.
 GroupVolume = .65,
 TotalVolume = .24, -- shared across ALL active/fading attack sounds, not per attacker
 LocalMultiplier = .7,
 VoiceDuck = .4,
 Limit = 4,
 Range = 70,
 NearDistance = 6,
 Timeout = .5,
 FadeIn = .12,
 FadeOut = .16,
 MaxLifetime = 4.5, -- independent cleanup if an end packet is lost
}
