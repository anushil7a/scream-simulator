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
 TotalVolume = .40, -- NORMAL budget shared across all active/fading sounds
 LowVolume = .24, -- original quiet mix; also the ceiling while local voice is detected
 LocalMultiplier = .7,
 VoiceDuck = .4,
 Limit = 4,
 Range = 70,
 NearDistance = 6,
 Timeout = .5,
 FadeIn = .12,
 FadeOut = .16,
 MaxLifetime = 4.5, -- independent cleanup if an end packet is lost
 StarterFallback = {
  Name = "se_battle_90",
  SourceFile = "vault/Audio/SFX/SciFi_Magic_Abilities/se_battle_90.ogg",
  AssetId = "",
  MinLevel = 1,
  MaxLevel = 9,
  Duration = 3.154,
 },
}
function Settings.AssetForLevel(level)
 if type(level)~="number" or level%1~=0 then return nil end
 local id=Settings.AssetsByLevel[level]
 if id~=nil then return "rbxassetid://"..id end
 local fb=Settings.StarterFallback
 if fb and level>=fb.MinLevel and level<=fb.MaxLevel and type(fb.AssetId)=="string" and fb.AssetId:match("^%d+$") then
  return "rbxassetid://"..fb.AssetId
 end
 return nil
end
function Settings.FallbackForLevel(level)
 if type(level)~="number" or level%1~=0 then return nil end
 local asset=Settings.AssetForLevel(level)
 if asset~=nil then return asset end
 local fb=Settings.StarterFallback
 if fb and level>=fb.MinLevel and level<=fb.MaxLevel then return fb.Name end
 return nil
end
return Settings
