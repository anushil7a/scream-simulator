-- Silent test beam. The caller supplies only isolated server-resolved target IDs.
-- Level/gear/origin come from the server; the only client choices are bounded power and aim.
local TestBeam={MaxDuration=4,Cooldown=5,InputTimeout=.5,MinPulseInterval=.1}
local RunService=game:GetService("RunService")
local Access=require(script.Parent.DeveloperAccess)
local function finite(n)return type(n)=="number" and n==n and math.abs(n)<math.huge end
function TestBeam.LocalFixture(localFixture)
 return localFixture==true and RunService:IsStudio() and game.GameId==0 and game.PlaceId==0 and workspace:GetAttribute("LocalSustainedPrototype")==true
end
function TestBeam.Available(authorized,localFixture)
 return authorized==true and (TestBeam.LocalFixture(localFixture)
  or Access.IsCityPreviewTools(game.CreatorType,game.CreatorId,RunService:IsStudio(),game.GameId,game.PlaceId))
end
function TestBeam.new(Combat,directionFor,Attack)
 local api={}
 local function request(arg,origin)
  if type(arg)~="table" then return nil end
  for k in pairs(arg) do if k~="power" and k~="aim" then return nil end end
  if not finite(arg.power) or arg.power%1~=0 or arg.power<0 or arg.power>100 then return nil end
  local direction=directionFor(origin,arg.aim)
  if not direction then return nil end
  return direction
 end
 local function context(p,s,authorized,localFixture,now)
  if not TestBeam.Available(authorized,localFixture) or not finite(now) or now<0 or s.flight or p.Parent==nil then return nil end
  local c=p.Character;local r=c and c:FindFirstChild("HumanoidRootPart");local h=c and c:FindFirstChildOfClass("Humanoid")
  if not c or not c.Parent or not r or r.Parent~=c or not r:IsA("BasePart") or not h or h.Parent~=c or h.Health<=0
   or r.Anchored or h.Sit or h.SeatPart or h.PlatformStand or now<(s.knockedUntil or 0) or now<(s.dodgingUntil or 0) then return nil end
  local origin=r.Position+Vector3.new(0,1,0);local head=c:FindFirstChild("Head")
  if head and head:IsA("BasePart") and (head.Position-r.Position).Magnitude<5 then origin=head.Position end
  return {character=c,root=r,humanoid=h,origin=origin}
 end
 function api.ValidateStart(p,s,authorized,localFixture,now,arg)
  local ctx=context(p,s,authorized,localFixture,now)
  if not ctx then return false,"Beam test needs an authorized test environment and a standing character." end
  if s.testBeam then return false,"Beam test is already active." end
  if now<(s.testBeamReadyAt or 0) then return false,"Beam test is cooling down." end
  if not request(arg,ctx.origin) then return false,"Invalid beam test input." end
  if arg.power==0 then return false,"0% power: no test beam." end
  return true,nil,ctx
 end
 function api.Start(p,s,authorized,localFixture,now,arg,gearMultiplier)
  local ok,reason,ctx=api.ValidateStart(p,s,authorized,localFixture,now,arg)
  if not ok then return false,reason end
  if type(s.testBaseline)~="table" then return false,"Start a temporary developer test session first." end
  local level=Combat.Level(s.data.level)
  local power=Combat.Stats(level,arg.power/100,false,false,gearMultiplier).power
  local protocol=Attack.New()
  -- The slider can show a harmless preview below the automatic damage gate.
  -- Keep the damage clock aligned with the visual cast, but supply no IDs
  -- while the actual (gear-adjusted) power is below the gate.
  if not Attack.Begin(protocol,now,1,Combat.Stats(level,1,false).maxDps,math.max(power,Attack.MinimumPower),true) then
   return false,"Invalid test beam damage budget."
  end
  s.testBeam={character=ctx.character,root=ctx.root,humanoid=ctx.humanoid,level=level,protocol=protocol,
   gearMultiplier=gearMultiplier,power=arg.power,effectivePower=power,aim=arg.aim,started=now,lastPulse=now,clock=now,lastVisual=-math.huge}
  return true
 end
 function api.Stop(s,now)
  local b=s.testBeam;if not b then return false end
  s.testBeam=nil
  if not finite(now) then now=b.clock end
  local ended=math.min(math.max(now,b.clock),b.started+TestBeam.MaxDuration,b.lastPulse+TestBeam.InputTimeout)
  s.testBeamReadyAt=math.max(s.testBeamReadyAt or 0,ended+TestBeam.Cooldown)
  return true
 end
 local function current(p,s,authorized,localFixture,now,finishing)
  local b=s.testBeam;if not b then return nil end
  local ctx=context(p,s,authorized,localFixture,now)
  if not ctx or type(s.testBaseline)~="table" or ctx.character~=b.character or ctx.root~=b.root or ctx.humanoid~=b.humanoid
   or now<b.clock or (not finishing and now>=b.started+TestBeam.MaxDuration) or now>=b.lastPulse+TestBeam.InputTimeout then return nil end
  return ctx
 end
 function api.Pulse(p,s,authorized,localFixture,now,arg)
  local b=s.testBeam;if not b then return false,false end
  local ctx=current(p,s,authorized,localFixture,now)
  if not ctx then return false,api.Stop(s,now) end
  -- Malformed/replayed packets cannot refresh the input deadline.
  if not request(arg,ctx.origin) then return false,false end
  if arg.power==0 then return false,api.Stop(s,now) end
  if now-b.lastPulse+1e-7<TestBeam.MinPulseInterval then return false,false end
  local power=Combat.Stats(b.level,arg.power/100,false,false,b.gearMultiplier).power
  if not Attack.Pulse(b.protocol,now,1,math.max(power,Attack.MinimumPower),true) then return false,api.Stop(s,now) end
  b.power=arg.power;b.effectivePower=power;b.aim=arg.aim;b.lastPulse=now;b.clock=now
  return true,false
 end
 function api.Step(p,s,authorized,localFixture,now,resolve)
  local b=s.testBeam;if not b then return nil,false end
  local ctx=current(p,s,authorized,localFixture,now,true)
  if not ctx then return nil,api.Stop(s,now) end
  b.clock=now
  local direction=directionFor(ctx.origin,b.aim)
  if not direction then return nil,api.Stop(s,now) end
  local stats=Combat.Stats(b.level,b.effectivePower,false)
  local ids,details
  if resolve and b.effectivePower>=Attack.MinimumPower and Attack.NeedsTargets(b.protocol,now) then
   ids,details=resolve(ctx,direction,stats,now)
  end
  local hits,ended=Attack.Step(b.protocol,now,true,ids)
  if ended then return nil,api.Stop(s,now),hits,details end
  if now-b.lastVisual+1e-7<TestBeam.MinPulseInterval then return nil,false,hits,details end
  b.lastVisual=now
  return {origin=ctx.origin,direction=direction,length=stats.range,width=stats.width,level=b.level,power=b.power},false,hits,details
 end
 return api
end
return TestBeam
