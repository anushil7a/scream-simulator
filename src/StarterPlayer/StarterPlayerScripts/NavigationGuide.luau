-- Local, opt-in world guidance. Never drives characters, remotes, saves or combat.
-- Pathfinding may fail with streamed-out geometry: distance is still useful, but
-- no straight-line trail is fabricated. Static dots respect reduced-motion settings.
local PathfindingService=game:GetService("PathfindingService")
local Workspace=game:GetService("Workspace")
local Guide={}
Guide.__index=Guide
local MAX_DOTS,SPACING,RETRY,MAX_AGE=18,5,3,8
local REPATH_DRIFT,MAX_TARGET_DRIFT=3,8
local LOW_RAY,HIGH_RAY=Vector3.new(0,.5,0),Vector3.new(0,2.5,0)
local GROUND_RAY=Vector3.new(0,-9,0)
local ROUTE_COLOR,PVP_COLOR=Color3.fromRGB(213,186,122),Color3.fromRGB(255,140,139)
local BEARINGS={"N","NE","E","SE","S","SW","W","NW"}
local function validPosition(p)
 return typeof(p)=="Vector3" and p.X==p.X and p.Y==p.Y and p.Z==p.Z
  and math.abs(p.X)<1e7 and math.abs(p.Y)<1e7 and math.abs(p.Z)<1e7
end
function Guide.new(ownerGui,isPvP)
 local folder=Instance.new("Folder");folder.Name="LocalNavigationGuide";folder.Parent=Workspace
 local self=setmetatable({folder=folder,dots={},visibleDots=0,isPvP=isPvP,generation=0,busy=false,lastRequest=-math.huge,lastDraw=-math.huge,status="",destroyed=false},Guide)
 self.raycast=RaycastParams.new();self.raycast.FilterType=Enum.RaycastFilterType.Exclude
 self.raycast.RespectCanCollide=true
 for i=1,MAX_DOTS do
  local dot=Instance.new("Part");dot.Name="Route"..i;dot.Size=Vector3.new(.85,.12,.85)
  dot.Anchored=true;dot.CanCollide=false;dot.CanTouch=false;dot.CanQuery=false;dot.CastShadow=false
  dot.Material=Enum.Material.SmoothPlastic;dot.Color=ROUTE_COLOR;dot.Transparency=1;dot.Parent=folder
  self.dots[i]=dot
 end
 if ownerGui then self.ownerConnection=ownerGui.Destroying:Connect(function() self:Destroy() end) end
 return self
end
function Guide:_hide()
 for i=1,self.visibleDots do self.dots[i].Transparency=1 end
 self.visibleDots=0;self.pvpAhead=false
end
function Guide:HasPvPAhead() return self.pvpAhead==true end
function Guide:_dropPath()
 if self.blocked then self.blocked:Disconnect();self.blocked=nil end
 if self.path then self.path:Destroy();self.path=nil end
 self.points=nil;self.cursor=nil;self.pathGoal=nil
 self:_hide()
end
function Guide:Clear()
 if self.destroyed then return end
 self.generation+=1;self.target=nil;self.root=nil;self.distance=nil;self.status="";self.lastRequest=-math.huge
 self.filterCharacter=nil;self.raycast.FilterDescendantsInstances={self.folder}
 self:_dropPath()
end
function Guide:SetTarget(target,keepThrottle)
 if self.destroyed then return end
 local valid=type(target)=="table" and validPosition(target.position)
 local label=valid and type(target.label)=="string" and string.sub(target.label,1,100) or "Destination"
 if keepThrottle and valid and self.target and self.target.label==label then
  -- Keep a nearby, already validated path visible while Mar is moving.
  self.target.position=target.position
  if self.points and ((self.pathGoal-target.position).Magnitude>MAX_TARGET_DRIFT
   or (self.points[#self.points].Position-target.position).Magnitude>MAX_TARGET_DRIFT) then
   self:_dropPath();self.status="Finding route"
  end
  return
 end
 local lastRequest,root=self.lastRequest,self.root
 self:Clear()
 if not valid then return end
 if keepThrottle then self.lastRequest=lastRequest;self.root=root end
 self.target={position=target.position,label=label}
 self.status="Finding route"
end
function Guide:GetStatus()
 local bearing=nil
 if self.target and self.root and self.root.Parent then
  local delta=self.target.position-self.root.Position
  if delta.X*delta.X+delta.Z*delta.Z>1 then
   -- Roblox world north is -Z; direction is informational, not a traversable route.
   local angle=math.atan2(delta.X,-delta.Z)
   bearing=BEARINGS[(math.floor(angle/(math.pi/4)+.5)%8)+1]
  end
 end
 return self.status,self.distance,bearing
end
function Guide:_request(root,now)
 if self.busy or now-self.lastRequest<RETRY then return end
 if self.pathGoal and (self.pathGoal-self.target.position).Magnitude<REPATH_DRIFT then return end
 self.busy=true;self.lastRequest=now
 local generation=self.generation
 local start,destination=root.Position,self.target.position
 task.spawn(function()
  local path
  local ok,points=pcall(function()
   path=PathfindingService:CreatePath({AgentRadius=3,AgentHeight=6,AgentCanJump=false,WaypointSpacing=SPACING})
   path:ComputeAsync(start,destination)
   if path.Status~=Enum.PathStatus.Success then return nil end
   return path:GetWaypoints()
  end)
  self.busy=false
  if self.destroyed or self.generation~=generation or self.root~=root then
   if path then path:Destroy() end
   return
  end
  if not root.Parent or (root.Position-start).Magnitude>18
   or (self.target.position-destination).Magnitude>MAX_TARGET_DRIFT then
   if path then path:Destroy() end
   if not self.points then self.status="Finding route" end
   return
  end
  -- A successful path must actually reach the chosen destination.
  if not ok or not points or #points<2 or #points>1024 or (points[#points].Position-destination).Magnitude>8
   or (points[#points].Position-self.target.position).Magnitude>MAX_TARGET_DRIFT then
   if path then path:Destroy() end
   if not self.points then self.status="Route unavailable" end
   return
  end
  self:_dropPath();self.path=path;self.points=points;self.cursor=2;self.pathGoal=destination
  self.pathAt=self.lastStepAt or now;self.status="Follow the markers"
  self.blocked=path.Blocked:Connect(function(index)
   if not self.destroyed and self.path==path and index>=self.cursor then
    self:_dropPath();self.status="Finding route"
   end
  end)
 end)
end
local function groundAt(raycast,point,height)
 local hit=Workspace:Raycast(Vector3.new(point.X,height+3,point.Z),GROUND_RAY,raycast)
 return hit and hit.Normal.Y>=.6 and hit or nil
end
local function mildDescent(first,last)
 local delta=last-first
 local horizontal=math.sqrt(delta.X^2+delta.Z^2)
 return horizontal>.01 and delta.Y<=.05 and -delta.Y<=horizontal*.5+.05
end
local function floorClearance(raycast,from,point,lowHit,previousGround)
 -- A navmesh waypoint chord can dip into a walkable surface at a ramp lip.
 if not lowHit.Normal or lowHit.Normal.Y<.6 or Workspace:Raycast(from+HIGH_RAY,point-from,raycast) then return end
 local start=previousGround or groundAt(raycast,from,from.Y)
 if not start then return end
 local middle=groundAt(raycast,(from+point)*.5,start.Position.Y)
 local finish=groundAt(raycast,point,start.Position.Y)
 if not middle or not finish or not mildDescent(start.Position,middle.Position)
  or not mildDescent(middle.Position,finish.Position) then return end
 if lowHit.Instance~=start.Instance and lowHit.Instance~=middle.Instance and lowHit.Instance~=finish.Instance then return end
 local delta=finish.Position-start.Position
 if Workspace:Raycast(start.Position+LOW_RAY,delta,raycast)
  or Workspace:Raycast(start.Position+HIGH_RAY,delta,raycast) then return end
 return finish
end
function Guide:Step(root,now,visible)
 if self.destroyed or not self.target then return end
 if type(now)~="number" or now~=now or math.abs(now)==math.huge then return end
 -- Use the latest client clock when asynchronous computation completes, not its start.
 self.lastStepAt=now
 if root~=self.root then
  self.generation+=1;self.root=root;self:_dropPath();self.lastRequest=-math.huge
 end
 if not root or not root.Parent or not validPosition(root.Position) then
  self.distance=nil;self.status="Waiting for character";self:_hide();return
 end
 self.distance=(self.target.position-root.Position).Magnitude
 if not visible then self:_hide();return end
 if self.distance<=8 then self.status="Arrived";self:_hide();return end
 if self.points then
  local previous=self.points[math.max(1,self.cursor-1)].Position
  local segment=self.points[self.cursor].Position-previous
  local lengthSquared=segment:Dot(segment)
  local t=lengthSquared>0 and math.clamp((root.Position-previous):Dot(segment)/lengthSquared,0,1) or 0
  local offRoute=(root.Position-(previous+segment*t)).Magnitude>20
  if now-self.pathAt>MAX_AGE or offRoute then self:_dropPath() end
 end
 self:_request(root,now)
 if now-self.lastDraw<.15 then return end
 self.lastDraw=now;self:_hide()
 if not self.points then return end
 if self.filterCharacter~=root.Parent then
  self.filterCharacter=root.Parent
  self.raycast.FilterDescendantsInstances={self.folder,root.Parent}
 end
 local points=self.points
 -- Advance sequentially; never pick a nearby point across the wall of a U-turn.
 while self.cursor<#points do
  local delta=points[self.cursor].Position-root.Position
  -- Corner fidelity: don't skip a 5-stud waypoint just because it is nearby.
  if delta.X*delta.X+delta.Z*delta.Z>6.25 or math.abs(delta.Y)>6 then break end
  self.cursor+=1
 end
 local from=root.Position-HIGH_RAY
 local previousGround
 local index,count,distance=self.cursor,0,0
 while index<=#points and count<MAX_DOTS and distance<90 do
  local goal=points[index].Position
  local delta=goal-from;local length=delta.Magnitude
  if length<.1 then index+=1;continue end
  local step=math.min(SPACING,length)
  local point=from+delta.Unit*step
  -- Keep only the already checked prefix. Replan when the obstacle blocks the first step.
  local lowHit=Workspace:Raycast(from+LOW_RAY,point-from,self.raycast)
  local recovered=lowHit and floorClearance(self.raycast,from,point,lowHit,previousGround)
  if (lowHit and not recovered) or (not lowHit and Workspace:Raycast(from+HIGH_RAY,point-from,self.raycast)) then
   if count>0 then break end
   self:_dropPath();self.status="Finding route";return
  end
  local ground=recovered or groundAt(self.raycast,point,point.Y)
  if not ground then break end
  -- Ground rays ignore decorative paving, so place markers above its shallow inlays.
  count+=1;self.visibleDots=count
  local dot=self.dots[count]
  local pvp=self.isPvP and self.isPvP(ground.Position)==true
  self.pvpAhead=self.pvpAhead or pvp==true
  local color=pvp and PVP_COLOR or ROUTE_COLOR
  if dot.Color~=color then dot.Color=color end
  dot.Position=ground.Position+Vector3.new(0,.45,0);dot.Transparency=.22
  distance+=step;from=recovered and ground.Position or point;previousGround=ground
  if step>=length then index+=1 end
 end
 if count==0 then self.status="Route unavailable" else self.status="Follow the markers" end
end
function Guide:Destroy()
 if self.destroyed then return end
 self:Clear();self.destroyed=true
 if self.ownerConnection then self.ownerConnection:Disconnect();self.ownerConnection=nil end
 self.folder:Destroy()
end
return Guide
