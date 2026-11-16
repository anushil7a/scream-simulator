local SoundService=game:GetService("SoundService")
local Content=game:GetService("ContentProvider")
local Settings=require(game:GetService("ReplicatedStorage").Shared.BossAudioConfig)
local Mix=require(script.Parent:WaitForChild("CueAudioMix"))
local Audio={}
function Audio.new()
 local destroyed=false;local ready={}
 local group=Instance.new("SoundGroup");group.Name="QuietBossAttacks";group.Volume=Settings.GroupVolume;group.Parent=SoundService
 local eq=Instance.new("EqualizerSoundEffect");eq.LowGain=-3;eq.MidGain=-2;eq.HighGain=-3;eq.Parent=group
 local function create(kind,position)
  local asset=Settings.Asset(kind)
  if not asset or not ready[kind] then return nil end
  local parent=SoundService;local anchor
  if Settings.Cues[kind].Spatial then
   anchor=Instance.new("Part");anchor.Name="LocalBossAudio"
   anchor.Anchored=true;anchor.CanCollide=false;anchor.CanQuery=false;anchor.CanTouch=false
   anchor.CastShadow=false;anchor.Transparency=1;anchor.Size=Vector3.one;anchor.Position=position;anchor.Parent=workspace
   parent=anchor
  end
  local sound=Instance.new("Sound");sound.Name="Boss"..kind;sound.SoundId=asset
  sound.Looped=false;sound.Volume=0;sound.PlaybackSpeed=Settings.Speed(kind);sound.PlayOnRemove=false
  sound.RollOffMode=Enum.RollOffMode.InverseTapered
  sound.RollOffMinDistance=Settings.NearDistance;sound.RollOffMaxDistance=Settings.Range
  sound.SoundGroup=group;sound.Parent=parent
  return {anchor=anchor,sound=sound,kind=kind}
 end
 local mix=Mix.new(Settings,create,function(handle,volume)
  handle.sound.Volume=volume
  if not handle.started and volume>0 then
   handle.started=true;handle.sound:Play()
  end
 end,
  function(handle)handle.sound:Stop();if handle.anchor then handle.anchor:Destroy() else handle.sound:Destroy() end end)
 local basePlay=mix.Play
 function mix:Play(kind,now,position)
  local cue=Settings.Cues[kind]
  if not self.destroyed and self.enabled and not self.suppressed and ready[kind] and cue and position
   and type(now)=="number" and now==now and math.abs(now)<math.huge
   and (not self.lastPlayed[kind] or now-self.lastPlayed[kind]>=cue.Cooldown)
   and kind:find("_tell_",1,true) and #self.entries>=Settings.Limit then
   -- Preserve warning intelligibility: replace one decorative impact, never another tell.
   for i,entry in ipairs(self.entries)do
    if entry.handle.kind:find("_impact_",1,true) then self.destroy(entry.handle);table.remove(self.entries,i);break end
   end
  end
  return basePlay(self,kind,now,position)
 end
 function mix:CancelTell(id,all)
  for i=#self.entries,1,-1 do
   local entry=self.entries[i]
   local prefix=id..(all and "_" or "_tell_")
   if entry.handle.kind:sub(1,#prefix)==prefix then self.destroy(entry.handle);table.remove(self.entries,i) end
  end
 end
 local destroy=mix.Destroy
 function mix:Destroy()
  if self.destroyed then return end
  destroyed=true;destroy(self);group:Destroy()
 end
 -- Preload once per configured cue with bounded retries. No short-lived emitter
 -- is allocated until cached; slow/failed loads never stall gameplay or play late.
 local assets={}
 for kind in pairs(Settings.Cues)do
  local asset=Settings.Asset(kind)
  if asset then assets[asset]=assets[asset] or {};table.insert(assets[asset],kind) end
 end
 for asset,kinds in pairs(assets)do task.spawn(function()
  for attempt=1,3 do
   if destroyed then return end
   local loaded=false
   pcall(function() Content:PreloadAsync({asset},function(_,status)if status==Enum.AssetFetchStatus.Success then loaded=true end end)end)
   if destroyed then return end
   if loaded then for _,kind in ipairs(kinds)do ready[kind]=true end;return end
   if attempt<3 then task.wait(attempt)end
  end
 end)end
 return mix
end
return Audio
