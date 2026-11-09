local SoundService=game:GetService("SoundService")
local Settings=require(game:GetService("ReplicatedStorage").Shared.AttackAudioConfig)
local Mix=require(script.Parent:WaitForChild("BeamAudioMix"))
local Audio={}
function Audio.new()
 local group=Instance.new("SoundGroup");group.Name="QuietAttackEffects";group.Volume=Settings.GroupVolume;group.Parent=SoundService
 local eq=Instance.new("EqualizerSoundEffect");eq.LowGain=-3;eq.MidGain=-3;eq.HighGain=-4;eq.Parent=group
 local function create(position,tier)
  local asset=Settings.AssetForLevel(tier)
  if not asset then return nil end -- starter tier has no owner-selected SFX
  local anchor=Instance.new("Part");anchor.Name="LocalAttackAudio"
  anchor.Anchored=true;anchor.CanCollide=false;anchor.CanQuery=false;anchor.CanTouch=false
  anchor.Transparency=1;anchor.Size=Vector3.one;anchor.Position=position;anchor.Parent=workspace
  local sound=Instance.new("Sound");sound.Name="EnergyBeam";sound.SoundId=asset
  sound.Looped=false;sound.Volume=0;sound.PlaybackSpeed=1;sound.PlayOnRemove=false
  sound.RollOffMode=Enum.RollOffMode.InverseTapered
  sound.RollOffMinDistance=Settings.NearDistance;sound.RollOffMaxDistance=Settings.Range
  sound.SoundGroup=group;sound.Parent=anchor;sound:Play()
  return {anchor=anchor,sound=sound}
 end
 local mix=Mix.new(Settings,create,function(handle,position,volume,pitch)
  handle.anchor.Position=position;handle.sound.Volume=volume;handle.sound.PlaybackSpeed=pitch
 end,function(handle) handle.sound:Stop();handle.anchor:Destroy() end)
 local destroy=mix.Destroy
 function mix:Destroy() destroy(self);group:Destroy() end
 return mix
end
return Audio
