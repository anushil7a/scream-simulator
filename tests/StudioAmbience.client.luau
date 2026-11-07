-- Append to Ambience in an unpublished Studio city. Native asset/settings
-- checks plus a synthetic performer; not human listening or real voice mixing.
task.spawn(function()
 assert(game.PlaceId==0 and Run:IsStudio())
 local checks=0;local latest;local oldVolume=.55
 local receiver=state.OnClientEvent:Connect(function(data) latest=data end)
 local actor=Instance.new("Model");actor.Name="AmbienceTestPerformer"
 local root=Instance.new("Part");root.Name="HumanoidRootPart";root.Anchored=true;root.CanCollide=false;root.Position=stage;root.Parent=actor
 local humanoid=Instance.new("Humanoid");humanoid.Parent=actor
 actor:SetAttribute("Role","Busker");actor.Parent=workspace;Collection:AddTag(actor,"CityResident")
 local function check(v,message) assert(v,message);checks+=1 end
 local function send(volume)
  remotes.Action:FireServer("SetSettings",{volume=volume});task.wait(.4)
 end
 local ok,err=xpcall(function()
  remotes.Action:FireServer("Sync");task.wait(3)
  check(latest and not latest.savingAvailable,"Temporary profile required")
  oldVolume=latest.settings.volume
  local sounds={}
  for _,v in folder:GetDescendants() do if v:IsA("Sound") then table.insert(sounds,v);assert(v.SoundGroup==group and v.Looped and v.RollOffMaxDistance<=230) end end
  check(#sounds==5,"Unexpected sound count or routing")
  game:GetService("ContentProvider"):PreloadAsync(sounds)
  for _,sound in sounds do assert(sound.IsLoaded and sound.TimeLength>0) end
  check(true,"Audio assets did not load")
  send(0);check(group.Volume==0,"City mute did not apply through server settings")
  send(.4);check(math.abs(group.Volume-.4)<.001,"City volume did not apply")
  actor:SetAttribute("Working",true);task.wait(1.6)
  check(guitar.Volume>.17 and guitar.Volume<=.201,"Performing busker did not fade in within cap")
  actor:SetAttribute("Working",false);task.wait(1.6)
  check(guitar.Volume<.03,"Stopped performer did not fade out")
  humanoid.Health=0;actor:SetAttribute("Working",true);task.wait(.6)
  check(guitar.Volume<.03,"Dead performer activated music")
 end,debug.traceback)
 actor:Destroy();send(oldVolume);receiver:Disconnect()
 workspace:SetAttribute("AmbienceResult",game:GetService("HttpService"):JSONEncode({passed=ok,checks=checks,error=not ok and tostring(err) or nil}))
end)
