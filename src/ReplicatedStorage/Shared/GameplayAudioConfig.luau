-- Original gameplay cues. Fill AssetId only after approved Roblox upload and
-- destination-experience permission checks. Empty IDs intentionally stay silent.
local Config = {
 GroupVolume = .5,
 TotalVolume = .12, -- separate quiet budget; at most .06 after the group
 VoiceDuck = .35,
 Limit = 6,
 Range = 50,
 NearDistance = 5,
 FadeOut = .035,
 Cues = {
  Hit = {AssetId = "", Cooldown = .16, Lifetime = .20, Spatial = false},
  Dodge = {AssetId = "", Cooldown = .15, Lifetime = .40, Spatial = true},
  Break = {AssetId = "", Cooldown = .12, Lifetime = .55, Spatial = true},
  LevelUp = {AssetId = "", Cooldown = 1, Lifetime = .80, Spatial = false},
 },
}
function Config.Asset(kind)
 local cue=Config.Cues[kind]
 local id=cue and cue.AssetId
 return type(id)=="string" and id:match("^[1-9]%d*$") and "rbxassetid://"..id or nil
end
function Config.Ready()
 for kind in pairs(Config.Cues) do if Config.Asset(kind) then return true end end
 return false
end
return Config
