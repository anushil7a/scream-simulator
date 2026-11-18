-- Disposable first-playable route; held-input proxy, not microphone verification.
local Run=game:GetService("RunService")
local Players=game:GetService("Players")
local Replicated=game:GetService("ReplicatedStorage")
return function(world)
 if not Run:IsStudio() or game.GameId~=0 or game.PlaceId~=0 then return end
 assert(not Replicated:FindFirstChild("AcademyRoutePreview"),"Academy fixture already running")
 local Rules=require(script.Parent.AcademyRouteRules)
 local Shared=Replicated:WaitForChild("Shared")
 local Voice=require(Shared.VoiceCombat)
 local Gear=require(Shared.GearCatalog)
 local Homes=require(Shared.CompactLayout).BossHomes
 local Equipment=require(game:GetService("ServerScriptService").Equipment)
 local Flight=require(game:GetService("ServerScriptService").TestFlight)
 -- Compact 1280-square map, including Astral altitude; no production bounds reused.
 local flightBounds={min=Vector3.new(-632,-4,-632),max=Vector3.new(632,240,632),localOnly=true}
 local BossService=require(game:GetService("ServerScriptService").BossService)
 local net=Instance.new("Folder");net.Name="AcademyRoutePreview";net.Parent=Replicated
 local input=Instance.new("RemoteEvent");input.Name="BeamInput";input.Parent=net
 local tools=Instance.new("RemoteEvent");tools.Name="TestTools";tools.Parent=net
 local fx=Instance.new("RemoteEvent");fx.Name="BeamFx";fx.Parent=net
 local stations={}
 for name,xyz in pairs(Rules.Locations) do stations[name]=Vector3.new(table.unpack(xyz)) end
 for name,pos in pairs(stations) do local value=Instance.new("Vector3Value");value.Name=name;value.Value=pos;value.Parent=net end
 local folder=Instance.new("Folder");folder.Name="ScreamSimulatorWorld";folder.Parent=workspace
 local props=Instance.new("Folder");props.Name="AcademyRouteStations";props.Parent=world
 local flights={};local toolSessions={}
 local states={};local sessionRecords={};local connections={};local playerConnections={}
 local function bind(signal,callback) table.insert(connections,signal:Connect(callback)) end
 local function flying(p) return Flight.Active(flights[p]) end
 local function stopFlight(p)
  local f=flights[p];if f then Flight.Stop(p,f) end
 end
 local function sync(p,s,notice)
  p:SetAttribute("AcademyStage",s.stage);p:SetAttribute("AcademyCoins",s.coins);p:SetAttribute("AcademyLevel",s.level)
  p:SetAttribute("AcademyGearEquipped",s.gearEquipped or "")
  if notice then p:SetAttribute("AcademyNotice",notice) end
 end
 local function body(p)
  local c=p.Character;local h=c and c:FindFirstChildOfClass("Humanoid");local root=c and c:FindFirstChild("HumanoidRootPart")
  if h and h.Health>0 and root and root:IsA("BasePart") then return root,h,c end
 end
 local function near(p,pos,distance)
  local root=body(p);return root and (root.Position-pos).Magnitude<=distance
 end
 local function part(name,pos,size,color)
  local p=Instance.new("Part");p.Name=name;p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false
  p.Position=pos;p.Size=size;p.Color=color;p.Material=Enum.Material.SmoothPlastic;p.Parent=props;return p
 end
 local function sign(anchor,text)
  local g=Instance.new("BillboardGui");g.Size=UDim2.fromOffset(260,84);g.StudsOffset=Vector3.new(0,4,0);g.MaxDistance=95;g.AlwaysOnTop=true;g.Parent=anchor
  local t=Instance.new("TextLabel");t.Size=UDim2.fromScale(1,1);t.BackgroundColor3=Color3.fromRGB(22,35,42);t.BackgroundTransparency=.15;t.TextColor3=Color3.new(1,1,1);t.TextWrapped=true;t.TextSize=15;t.Text=text;t.Parent=g
 end
 local target=part("AcademyTrainingResonator",stations.AcademyTrainTarget,Vector3.new(4,6,2),Color3.fromRGB(50,220,214))
 target.Material=Enum.Material.Neon;sign(target,"1 · TRAIN\nHold Beam on the cyan resonator\nStudio input proxy · not a microphone")
 -- Original small native-part faculty silhouettes: Marina's teal sash, Tinker's brass apparatus.
 local function resident(name,pos,color,text)
  local torso=part(name,pos+Vector3.new(0,3,0),Vector3.new(2.5,3,1.5),color)
  part(name.."Head",pos+Vector3.new(0,5.3,0),Vector3.new(1.8,1.8,1.8),Color3.fromRGB(224,189,148)).Shape=Enum.PartType.Ball
  for _,side in ipairs({-1,1}) do part(name.."Boot",pos+Vector3.new(side*.65,.8,0),Vector3.new(.9,1.6,1),Color3.fromRGB(45,55,63)) end
  part(name.."Sash",pos+Vector3.new(0,3.6,-.82),Vector3.new(2.6,.6,.2),Color3.fromRGB(187,145,60))
  sign(torso,text);return torso
 end
 local mentor=resident("MarinaAcademyMentor",stations.AcademyMentor,Color3.fromRGB(43,137,146),"2 · MARINA / ACADEMY MENTOR\nTrain first, then accept the encounter\nPreview level lift: Lv10, no live stats")
 local gear=resident("TinkerAcademyGear",stations.AcademyGear,Color3.fromRGB(151,104,65),"4 · TINKER / STARTER GEAR\nReturn with 100 session coins\nAcademy Megaphone · buy + equip")
 part("TinkerBrassSpeaker",stations.AcademyGear+Vector3.new(2,3,0),Vector3.new(1.4,2,1.4),Color3.fromRGB(208,162,68))
 local promptRay=RaycastParams.new();promptRay.FilterType=Enum.RaycastFilterType.Include;promptRay.FilterDescendantsInstances={world}
 local function prompt(anchor,name,callback)
  local q=Instance.new("ProximityPrompt");q.ActionText=name;q.ObjectText=anchor.Name;q.MaxActivationDistance=10;q.HoldDuration=.3;q.RequiresLineOfSight=true;q.Parent=anchor
  bind(q.Triggered,function(p)
   if flying(p) or not near(p,anchor.Position,12) then return end
   local root=body(p);local origin=root.Position+Vector3.new(0,1.5,0)
   local obstruction=workspace:Raycast(origin,anchor.Position-origin,promptRay)
   if obstruction then return end
   local s=states[p];if s then callback(p,s) end
  end)
 end
 local metronome
 local service=BossService.new(folder,{
  context=function(p)
   local s=states[p];local root,_,c=body(p)
   if flying(p) or not s or s.stage~="Fight" or not root then return nil end
   return {position=root.Position,level=s.level,identity=c}
  end,
  player=function(id) return Players:GetPlayerByUserId(id) end,
  reward=function(p,spec)
   local s=states[p]
   if not flying(p) and s and spec.id=="metronome" and Rules.RewardOnce(s,spec.coins) then
    sync(p,s,"Metronome defeated: 35 boss coins + 65 Academy starter bonus = 100 session coins. Walk back to Tinker.")
   end
  end,
  damage=function(p,amount)
   local _,h=body(p);if h and not flying(p) then h:TakeDamage(amount) end
  end,
 })
 for _,boss in ipairs(service.bosses) do
  local home=Homes[boss.spec.id]
  assert(home and boss.center==Vector3.new(home.x,home.y,home.z),"Incorrect preview boss home")
  boss.model:SetAttribute("MapDistrict",home.district)
  if boss.spec.id=="metronome" then metronome=boss
  else boss.idleText=boss.spec.name.." · Lv "..boss.spec.level.."+\nPreview · patrol only" end
 end
 assert(metronome and #service.bosses==5,"Expected full five-boss preview roster")
 prompt(mentor,"Accept Academy encounter",function(p,s)
  if Rules.Accept(s) then sync(p,s,"Academy accepted. Preview-only level 10. Choose Guide if wanted, then enter the Metronome ring and aim at its body.")
  elseif s.stage=="Train" then sync(p,s,"First hold Beam on the cyan training resonator for one second.") end
 end)
 prompt(gear,"Buy + equip Megaphone · 100",function(p,s)
  if s.stage=="Gear" then
   local ok,message=Gear.Act(s,"Megaphone",false)
   if ok then s.stage="Complete";Equipment.SyncMegaphone(p,true) end
   sync(p,s,message.." Preview session only; no save or purchase service.")
  elseif s.stage=="Complete" then sync(p,s,"Academy route complete. Megaphone is already owned and equipped; no second debit.")
  else sync(p,s,"Finish training, accept Marina's encounter, then defeat the Academy Metronome first.") end
 end)
 local function setup(p)
  if states[p] then return end
  flights[p]={testBaseline={}} -- separate in-memory marker, never the Academy progression record
  toolSessions[p]={percent=100,lastPower=-math.huge,lastFly=-math.huge,lastInput=-math.huge}
  p:SetAttribute("AcademyBeamPercent",100);p:SetAttribute("TestFlight",false)
  local s=sessionRecords[p.UserId] or Rules.New();sessionRecords[p.UserId]=s;states[p]=s
  Rules.Stop(s,os.clock());s.released=true;s.direction=nil
  sync(p,s,s.stage=="Train" and "Isolated Studio route: hold Beam on the cyan resonator. No real microphone or saved progression." or "")
  playerConnections[p]={
   p.CharacterRemoving:Connect(function() stopFlight(p);Rules.Stop(s,os.clock());s.released=true;s.direction=nil end),
   p.CharacterAdded:Connect(function() stopFlight(p);Rules.Stop(s,os.clock());s.released=true;s.direction=nil;sync(p,s,"") end),
  }
 end
 bind(Players.PlayerAdded,setup)
 bind(Players.PlayerRemoving,function(p)
  for _,c in ipairs(playerConnections[p] or {}) do c:Disconnect() end
  playerConnections[p]=nil
  local s=states[p];if s then Rules.Stop(s,os.clock());s.released=true;s.direction=nil end
  stopFlight(p);flights[p]=nil;toolSessions[p]=nil;states[p]=nil
 end)
 for _,p in ipairs(Players:GetPlayers()) do setup(p) end
 bind(input.OnServerEvent,function(p,held,direction,mode)
  local s=states[p];if not s or flying(p) then return end
  local now=os.clock()
  if held==false then s.testOnce=nil;Rules.Input(s,false,now);return end
  local t=toolSessions[p]
  if not t or (Rules.BeamPower(t.percent) or 0)<=0 then return end
  if held~=true or typeof(direction)~="Vector3" or not Rules.Direction(direction.X,direction.Y,direction.Z) or not body(p) then return end
  if mode~=nil and mode~="TestStart" and mode~="TestPulse" then return end
  if mode=="TestStart" then
   s.testOnce=nil
   if s.held or now<s.nextCast then return end
  elseif mode=="TestPulse" then
   -- A rejected/expired one-shot can never become a delayed attack after cooldown.
   if not s.testOnce or not Rules.Active(s,now) then return end
  else s.testOnce=nil end
  if Rules.Input(s,true,now) then
   s.direction=direction.Unit
   if mode=="TestStart" then s.testOnce=true end
  end
 end)
 bind(tools.OnServerEvent,function(p,action,arg)
  if not Run:IsStudio() or game.GameId~=0 or game.PlaceId~=0 then stopFlight(p);return end
  local s=states[p];local f=flights[p];local t=toolSessions[p]
  if not s or not f or not t or type(action)~="string" then return end
  local now=os.clock()
  -- Stop bypasses throttles, so a held input cannot starve return-to-origin.
  if action=="FlyOff" and arg==nil then stopFlight(p);return end
  if action=="FlightInput" then
   if now-t.lastInput<.075 then return end
   t.lastInput=now;Flight.Input(p,f,arg,now);return
  end
  if action=="BeamPower" then
   if now-t.lastPower<.15 then return end
   local power=Rules.BeamPower(arg);if power==nil then return end
   t.lastPower=now;t.percent=arg;p:SetAttribute("AcademyBeamPercent",arg)
   if power==0 then Rules.Stop(s,now);s.released=true;s.direction=nil end
  elseif action=="FlyOn" and arg==nil then
   if now-t.lastFly<.15 then return end
   t.lastFly=now
   local ok,message=Flight.Start(p,f,true,flightBounds,now)
   if ok then Rules.Stop(s,now);s.released=true;s.direction=nil end
   sync(p,s,message)
  end
 end)
 local ray=RaycastParams.new();ray.FilterType=Enum.RaycastFilterType.Include;ray.FilterDescendantsInstances={world}
 local function beam(origin,direction,point,radius,range)
  local offset=point-origin;local t=offset:Dot(direction)
  if t<=0 or t>range or (offset-direction*t).Magnitude>radius then return nil end
  local hit=workspace:Raycast(origin,direction*t,ray)
  if hit and hit.Distance<t-.15 then return nil end
  return origin+direction*t
 end
 local last=0
 bind(Run.Heartbeat,function()
  if world.Parent~=workspace or folder.Parent~=workspace then
   for p in pairs(flights) do stopFlight(p) end
   table.clear(flights);table.clear(toolSessions)
   for _,c in ipairs(connections) do c:Disconnect() end
   for _,list in pairs(playerConnections) do for _,c in ipairs(list) do c:Disconnect() end end
   table.clear(playerConnections);table.clear(states);table.clear(sessionRecords)
   net:Destroy();folder:Destroy();props:Destroy();return
  end
  local now=os.clock();if now-last<Rules.Tick then return end
  local dt=math.min(Rules.Tick,now-last);last=now
  for p,s in pairs(states) do
   local f=flights[p]
   if f then Flight.Step(p,f,true,flightBounds,now,dt) end
   if flying(p) then
    Rules.Stop(s,now);s.released=true;s.direction=nil;p:SetAttribute("AcademyCharge",0)
    continue
   end
   local root=body(p)
   if root then
    if s.stage=="Complete" and s.gearEquipped=="Megaphone" and not p.Character:FindFirstChild("AcademyMegaphoneAccessory") then Equipment.SyncMegaphone(p,true) end
    local delta=root.Position-metronome.center
    if Rules.Enter(s,math.abs(delta.Y)<=metronome.spec.engageHeight and Vector3.new(delta.X,0,delta.Z).Magnitude<=22) then
     sync(p,s,"Fight ready. Hold Beam, dodge the colored ground. Four seconds maximum, five seconds cooldown.")
    end
   else Rules.Stop(s,now) end
   local active=Rules.Active(s,now)
   p:SetAttribute("AcademyCharge",active and math.max(0,Rules.MaxHold-(now-s.started)) or -math.max(0,s.nextCast-now))
   local power=Rules.BeamPower(toolSessions[p].percent)
   if not active or not root or not s.direction or not power or power<=0 then continue end
   local origin=root.Position+Vector3.new(0,1.5,0)
   local stats=Voice.Stats(s.level,power,false,false,Gear.Multiplier(s))
   local endpoint=origin+s.direction*stats.range
   local worldHit=workspace:Raycast(origin,s.direction*stats.range,ray)
   if worldHit then endpoint=worldHit.Position end
   if s.stage=="Train" then
    local hit=beam(origin,s.direction,target.Position,3.3,stats.range)
    if hit and near(p,target.Position,30) then
     endpoint=hit
     if Rules.Train(s,dt) then sync(p,s,"Training complete. Walk to Marina and use her prompt to accept the Academy encounter.") end
    end
   elseif s.stage=="Fight" and service:CanHit(metronome,p,now) then
    local hit=beam(origin,s.direction,metronome.root.Position,4,stats.range)
    if hit then endpoint=hit;service:Hit(metronome,p,Rules.Dps(stats)*dt,now) end
   end
   fx:FireClient(p,origin,endpoint,stats.power)
  end
  service:Step(now)
 end)
 workspace:SetAttribute("ReviewBossCount",#service.bosses)
 print("[AcademyRoutePreview] Studio-only held-input route ready; no microphone, data store, purchases or live stats")
end
