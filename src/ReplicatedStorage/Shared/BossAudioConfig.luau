-- Original sources: assets/audio/bosses. Empty original IDs require approved upload.
-- Bundled fallback files were inventoried in installed official Studio content/sounds.
-- Fallbacks are functional warning/impact cues, not bespoke organ/horn recordings.
local Settings={GroupVolume=.5,TotalVolume=.08,VoiceDuck=.25,Limit=4,Range=70,NearDistance=8,FadeOut=.06,Cues={}}
Settings.Themes={
 metronome={tell='volume_slider.ogg',impact='action_jump_land.mp3',tellSpeed=1.4,impactSpeed=1.25},
 golem={tell='action_get_up.mp3',impact='impact_explosion_03.mp3',tellSpeed=.65,impactSpeed=.55},
 ignis={tell='action_jump.mp3',impact='impact_explosion_03.mp3',tellSpeed=.8,impactSpeed=1.15},
 leviathan={tell='action_get_up.mp3',impact='impact_water.mp3',tellSpeed=.85,impactSpeed=1.1},
 conductor={tell='volume_slider.ogg',impact='volume_slider.ogg',tellSpeed=.8,impactSpeed=1.55},
}
for id,theme in pairs(Settings.Themes) do
 for _,stage in ipairs({'tell','impact'}) do
  for variant=1,2 do
   Settings.Cues[id..'_'..stage..'_'..variant]={AssetId='',Fallback='rbxasset://sounds/'..theme[stage],
    Speed=theme[stage..'Speed']*(variant==2 and 1.06 or 1),Cooldown=.25,Lifetime=stage=='tell' and 1.1 or 1.15,Spatial=true}
  end
 end
end
function Settings.Key(id,stage,serial)
 if not Settings.Themes[id] or (stage~='tell' and stage~='impact') or type(serial)~='number' or serial%1~=0 or serial<1 or serial>1e9 then return nil end
 return id..'_'..stage..'_'..(serial%2==0 and 2 or 1)
end
function Settings.Speed(key)
 local cue=Settings.Cues[key];if not cue then return 1 end
 if type(cue.AssetId)=='string' and cue.AssetId:match('^[1-9]%d*$') then return key:sub(-1)=='2' and 1.06 or 1 end
 return cue.Speed
end
function Settings.Asset(key)
 local cue=Settings.Cues[key];if not cue then return nil end
 if type(cue.AssetId)=='string' and cue.AssetId:match('^[1-9]%d*$') then return 'rbxassetid://'..cue.AssetId end
 return cue.Fallback
end
return Settings
