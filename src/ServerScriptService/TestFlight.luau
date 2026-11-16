-- Server-authoritative, explicitly activated developer-test flight only.
-- Bounds are {min=Vector3,max=Vector3,localOnly=true}; no client CFrame, velocity or speed is accepted.
local Flight={}
local RunService=game:GetService("RunService")
local function localOnly(bounds)
 return RunService:IsStudio() and game.GameId==0 and game.PlaceId==0 and type(bounds)=="table" and bounds.localOnly==true
end
local SPEED=32
local MAX_DT=.1
local INPUT_TIMEOUT=.3
local function finite(v)return type(v)=="number" and v==v and math.abs(v)<math.huge end
local function validBounds(bounds)
 if type(bounds)~="table" or typeof(bounds.min)~="Vector3" or typeof(bounds.max)~="Vector3" then return false end
 for _,axis in ipairs({"X","Y","Z"}) do
  if not finite(bounds.min[axis]) or not finite(bounds.max[axis]) or bounds.min[axis]>=bounds.max[axis] then return false end
 end
 return true
end
local function live(p,f)
 return p.Character==f.character and f.character.Parent~=nil and f.root.Parent==f.character
  and f.character:FindFirstChild("HumanoidRootPart")==f.root
  and f.humanoid.Parent==f.character and f.humanoid.Health>0
end
function Flight.Active(s)return type(s)=="table" and s.flight~=nil end
function Flight.Stop(p,s)
 local f=s.flight;if not f then return end
 s.flight=nil;p:SetAttribute("TestFlight",false) -- callbacks/duplicate stops cannot reuse the session
 if f.root.Parent then
  f.root.CFrame=f.origin
  f.root.AssemblyLinearVelocity=Vector3.zero;f.root.AssemblyAngularVelocity=Vector3.zero
  f.root.Anchored=f.anchored
  if not f.anchored then
   pcall(function()
    if f.networkAuto then f.root:SetNetworkOwnershipAuto() else f.root:SetNetworkOwner(f.networkOwner) end
   end)
  end
 end
 if f.humanoid.Parent then f.humanoid.AutoRotate=f.autoRotate end
end
function Flight.Start(p,s,authorized,bounds,now)
 if authorized~=true or not localOnly(bounds) or type(s.testBaseline)~="table" then return false,"Start a developer test session first." end
 if not finite(now) or not validBounds(bounds) then return false,"Invalid flight bounds or clock." end
 if Flight.Active(s) then return false,"Flight is already active." end
 local character=p.Character
 local root=character and character:FindFirstChild("HumanoidRootPart")
 local humanoid=character and character:FindFirstChildOfClass("Humanoid")
 if not character or not character.Parent or not root or not root:IsA("BasePart") or not humanoid or humanoid.Health<=0 then return false,"A living character is required." end
 if root.Anchored or humanoid.Sit or humanoid.SeatPart or humanoid.PlatformStand or now<(s.knockedUntil or 0) or now<(s.dodgingUntil or 0) then return false,"Wait until standing normally before flying." end
 local pos=root.Position
 if pos.X<bounds.min.X or pos.Y<bounds.min.Y or pos.Z<bounds.min.Z or pos.X>bounds.max.X or pos.Y>bounds.max.Y or pos.Z>bounds.max.Z then return false,"Character is outside flight bounds." end
 local auto,owner=true,nil
 pcall(function()auto=root:GetNetworkOwnershipAuto();owner=root:GetNetworkOwner()end)
 local f={character=character,root=root,humanoid=humanoid,origin=root.CFrame,anchored=root.Anchored,autoRotate=humanoid.AutoRotate,
  networkAuto=auto,networkOwner=owner,input=Vector3.zero,inputAt=now,clock=now}
 -- Anchored flight has no client physics ownership; restoring the original ownership is best-effort.
 if not root.Anchored then pcall(function()root:SetNetworkOwner(nil)end) end
 root.Anchored=true;humanoid.AutoRotate=false
 root.AssemblyLinearVelocity=Vector3.zero;root.AssemblyAngularVelocity=Vector3.zero
 s.flight=f;p:SetAttribute("TestFlight",true)
 return true,"Test flight enabled."
end
function Flight.Input(p,s,arg,now)
 local f=s.flight
 if not f or type(s.testBaseline)~="table" or not live(p,f) or not finite(now) or now<f.clock then return false end
 if type(arg)~="table" then return false end
 for k in pairs(arg) do if k~="x" and k~="y" and k~="z" then return false end end
 for _,key in ipairs({"x","y","z"}) do local v=arg[key];if v~=-1 and v~=0 and v~=1 then return false end end
 f.input=Vector3.new(arg.x,arg.y,arg.z);f.inputAt=now
 return true
end
function Flight.Step(p,s,authorized,bounds,now,dt)
 local f=s.flight;if not f then return false end
 if authorized~=true or not localOnly(bounds) or type(s.testBaseline)~="table" or not live(p,f) or not validBounds(bounds)
  or f.humanoid.Sit or f.humanoid.SeatPart or f.humanoid.PlatformStand or now<(s.knockedUntil or 0)
  or not finite(now) or now<f.clock or not finite(dt) or dt<0 then Flight.Stop(p,s);return false end
 f.clock=now
 local input=now-f.inputAt<=INPUT_TIMEOUT and f.input or Vector3.zero
 local forward=f.root.CFrame.LookVector;forward=Vector3.new(forward.X,0,forward.Z)
 if forward.Magnitude<.001 then forward=Vector3.new(0,0,-1) else forward=forward.Unit end
 local right=Vector3.new(-forward.Z,0,forward.X)
 -- z=1 is forward (W); movement is aligned with server character heading, not client camera.
 local direction=right*input.X+Vector3.new(0,input.Y,0)+forward*input.Z
 if direction.Magnitude>1 then direction=direction.Unit end
 local delta=direction*SPEED*math.min(dt,MAX_DT)
 if delta.Magnitude>.0001 then
  local pos=f.root.Position
  local goal=pos+delta
  goal=Vector3.new(math.clamp(goal.X,bounds.min.X,bounds.max.X),math.clamp(goal.Y,bounds.min.Y,bounds.max.Y),math.clamp(goal.Z,bounds.min.Z,bounds.max.Z))
  delta=goal-pos
  if delta.Magnitude>.0001 then
   local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Exclude;params.FilterDescendantsInstances={f.character};params.RespectCanCollide=true
   local hit=workspace:Blockcast(f.root.CFrame,Vector3.new(2,3,2),delta,params)
   if hit then delta=delta.Unit*math.max(0,math.min(delta.Magnitude,hit.Distance-.1)) end
   f.root.CFrame=f.root.CFrame+delta
  end
 end
 return true
end
return Flight
