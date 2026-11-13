-- Optional local aim assistance only. Server still decides every hit and reward.
-- No camera, input, task, connection, Instance allocation or remote ownership here.
local LockOn={}
LockOn.__index=LockOn
local function finite(n)return type(n)=="number" and n==n and math.abs(n)<math.huge end
local function vector(v)return typeof(v)=="Vector3" and finite(v.X) and finite(v.Y) and finite(v.Z) end
local function instance(v,class)return typeof(v)=="Instance" and v:IsA(class) end
function LockOn.new(options)
 return setmetatable({options=options,target=nil,destroyed=false},LockOn)
end
function LockOn:Clear() self.target=nil end
function LockOn:Destroy() self:Clear();self.destroyed=true end
function LockOn:_context(c)
 if self.destroyed or type(c)~="table" or c.allowed~=true or not instance(c.character,"Model")
  or not c.character:IsDescendantOf(self.options.world) or self.options.localPlayer.Character~=c.character
  or not vector(c.origin) or not vector(c.position) or not finite(c.range) or c.range<=0
  or not finite(c.now) or not instance(c.camera,"Camera") then return false end
 local h=c.character:FindFirstChildOfClass("Humanoid")
 return h~=nil and h.Health>0
end
function LockOn:_valid(model,c,prior)
 local o=self.options
 if not instance(model,"Model") or model==c.character or not model:IsDescendantOf(o.world) then return nil end
 local root=model:FindFirstChild("HumanoidRootPart");local humanoid=model:FindFirstChildOfClass("Humanoid")
 if not instance(root,"BasePart") or not instance(humanoid,"Humanoid") or not root:IsDescendantOf(model) or not humanoid:IsDescendantOf(model) or not finite(humanoid.Health) or humanoid.Health<=0 or not vector(root.Position) then return nil end
 if prior and (prior.root~=root or prior.humanoid~=humanoid or prior.character~=c.character) then return nil end
 local player=o.players:GetPlayerFromCharacter(model)
 if player then
  if player==o.localPlayer or player.Character~=model or not player.Parent
   or not o.inArena(c.position) or not o.inArena(root.Position) then return nil end
  for _,key in ipairs({"ProtectionEnds","DodgeEnds"}) do
   local untilTime=player:GetAttribute(key)
   if untilTime~=nil and (not finite(untilTime) or untilTime>c.now) then return nil end
  end
 else
  local tier=model:GetAttribute("TrainingTier")
  local home=type(tier)=="string" and o.trainingHomes[tier]
  if not vector(home) or not o.collection:HasTag(model,"CityResident") or model:GetAttribute("ResidentActive")==false
   or (c.position-home).Magnitude>o.trainingRadius then return nil end
 end
 if prior and prior.player~=player then return nil end
 -- Additional local restrictions are advisory; unreplicated session/test-mode checks remain server-only.
 if o.canSelect and o.canSelect(model,player,c)~=true then return nil end
 if (root.Position-c.position).Magnitude>c.range then return nil end
 local screen,visible=c.camera:WorldToViewportPoint(root.Position)
 local viewport=c.camera.ViewportSize
 if not visible or not vector(screen) or screen.Z<=0 or viewport.X<2 or viewport.Y<2
  or screen.X<0 or screen.Y<0 or screen.X>viewport.X or screen.Y>viewport.Y then return nil end
 local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Exclude
 params.FilterDescendantsInstances={c.character,model};params.RespectCanCollide=true
 for _,origin in ipairs({c.origin,c.camera.CFrame.Position}) do
  if not vector(origin) or o.world:Raycast(origin,root.Position-origin,params) then return nil end
 end
 return {model=model,root=root,humanoid=humanoid,player=player,character=c.character},screen
end
function LockOn:Toggle(c)
 if self.target then self:Clear();return nil end
 if not self:_context(c) then return nil end
 local best,score=nil,math.huge
 local function consider(model)
  local target,screen=self:_valid(model,c)
  if not target then return end
  local viewport=c.camera.ViewportSize
  local distance=((screen.X-viewport.X/2)^2+(screen.Y-viewport.Y/2)^2)^.5
  -- Deliberate center acquisition cone, not a world-wide nearest-enemy search.
  if distance<=math.min(viewport.X,viewport.Y)*.35 and distance<score then best=target;score=distance end
 end
 for _,player in ipairs(self.options.players:GetPlayers()) do consider(player.Character) end
 for _,model in ipairs(self.options.collection:GetTagged("CityResident")) do consider(model) end
 self.target=best
 return best and best.model or nil
end
function LockOn:Resolve(c)
 if not self.target then return nil end
 if not self:_context(c) then self:Clear();return nil end
 local target=self:_valid(self.target.model,c,self.target)
 if not target then self:Clear();return nil end
 return target.root.Position,target.model
end
return LockOn
