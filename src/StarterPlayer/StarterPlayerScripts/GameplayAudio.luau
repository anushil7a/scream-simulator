local SoundService=game:GetService("SoundService")
local Content=game:GetService("ContentProvider")
local Settings=require(game:GetService("ReplicatedStorage").Shared.GameplayAudioConfig)
local Mix=require(script.Parent:WaitForChild("CueAudioMix"))
local Audio={}
function Audio.new()
 local destroyed=false;local ready={}
 local group=Instance.new("SoundGroup");group.Name="QuietGameplayEffects";group.Volume=Settings.GroupVolume;group.Parent=SoundService
 local eq=Instance.new("EqualizerSoundEffect");eq.LowGain=-3;eq.MidGain=-2;eq.HighGain=-3;eq.Parent=group
 local function create(kind,position)
  local asset=Settings.Asset(kind)
  if not asset or not ready[kind] then return nil end
  local parent=SoundService;local anchor
  if Settings.Cues[kind].Spatial then
   anchor=Instance.new("Part");anchor.Name="LocalGameplayAudio"
   anchor.Anchored=true;anchor.CanCollide=false;anchor.CanQuery=false;anchor.CanTouch=false
   anchor.CastShadow=false;anchor.Transparency=1;anchor.Size=Vector3.one;anchor.Position=position;anchor.Parent=workspace
   parent=anchor
  end
  local sound=Instance.new("Sound");sound.Name="Gameplay"..kind;sound.SoundId=asset
  sound.Looped=false;sound.Volume=0;sound.PlaybackSpeed=1;sound.PlayOnRemove=false
  sound.RollOffMode=Enum.RollOffMode.InverseTapered
  sound.RollOffMinDistance=Settings.NearDistance;sound.RollOffMaxDistance=Settings.Range
  sound.SoundGroup=group;sound.Parent=parent
  return {anchor=anchor,sound=sound}
 end
 local mix=Mix.new(Settings,create,function(handle,volume)
  handle.sound.Volume=volume
  if not handle.started and volume>0 then
   handle.started=true;handle.sound:Play()
  end
 end,
  function(handle)handle.sound:Stop();if handle.anchor then handle.anchor:Destroy() else handle.sound:Destroy() end end)
 local destroy=mix.Destroy
 function mix:Destroy()
  if self.destroyed then return end
  destroyed=true;destroy(self);group:Destroy()
 end
 -- Preload once per configured cue with bounded retries. No short-lived emitter
 -- is allocated until cached; slow/failed loads never stall gameplay or play late.
 for kind in pairs(Settings.Cues) do
  local cueKind=kind;local asset=Settings.Asset(kind)
  if asset then task.spawn(function()
   for attempt=1,3 do
    if destroyed then return end
    local loaded=false
    pcall(function()
     Content:PreloadAsync({asset},function(_,status)
      if status==Enum.AssetFetchStatus.Success then loaded=true end
     end)
    end)
    if destroyed then return end
    if loaded then ready[cueKind]=true;return end
    if attempt<3 then task.wait(attempt) end
   end
  end) end
 end
 return mix
end
return Audio
