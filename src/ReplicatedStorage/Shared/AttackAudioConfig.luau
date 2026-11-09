-- Owner-selected Roblox audio, keyed by equipped scream unlock level.
local Settings = {
 AssetsByLevel = {
  [10] = "112589551277234", [20] = "71125574109613",
  [30] = "72820033812084", [40] = "116444869617367",
  [50] = "110531388862916", [60] = "72657289722275",
  [70] = "8899285496", [80] = "102380291908556",
  [90] = "80523108386394", [100] = "79853512837585",
 },
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
function Settings.AssetForLevel(level)
 local id=Settings.AssetsByLevel[level]
 return id and "rbxassetid://"..id or nil
end
return Settings
