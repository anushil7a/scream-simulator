-- Shared, server-simulated beach activity. Hits arrive only after normal mic-cast
-- validation; this module never creates attacks, rewards, or client-owned physics.
local Run=game:GetService("RunService")
local Rules=require(script.Parent.CombatRules)
local Config=require(game:GetService("ReplicatedStorage").Shared.Config)
local compact=Config.CompactCity and Config.CityLayout.Volley
local Volley={}
local V=Vector3.new
local serve=compact and compact.serve or V(-50,4,489)
local boardPosition=compact and compact.board or V(-75,5,484)
local minimum=compact and compact.min or V(-70,0,479)
local maximum=compact and compact.max or V(-30,0,531)
local playerMinimum=compact and compact.playerMin or V(-77,0,472)
local playerMaximum=compact and compact.playerMax or V(-23,0,538)
local netZ=compact and compact.netZ or 505
local netMinX=compact and compact.netMinX or -70
local netMaxX=compact and compact.netMaxX or -30
local minimumCrossingHeight=compact and compact.minimumCrossingHeight or 10.2
local floorBallY=compact and compact.floorBallY or 2.1
local gameState
local function label(state,text)
 state.label.Text=text
 state.model:SetAttribute("Rally",state.rally)
 state.model:SetAttribute("BestRally",state.best)
 state.model:SetAttribute("Phase",state.phase)
end
local function reset(state)
 state.position=serve;state.velocity=V(0,0,0);state.phase="Ready";state.rally=0;state.crossed=false
 state.ball.Position=serve
 label(state,"MIC VOLLEY · BEST "..state.best.."\nAim a beam at the ball to serve\nTrade returns across the net")
end
local function fault(state,reason)
 state.phase="Resetting";state.resetAt=os.clock()+3;state.velocity=V(0,0,0)
 label(state,reason.." · RALLY "..state.rally.."\nBest "..state.best.." · next serve in 3s")
end
function Volley.Start(parent)
 if gameState then
  if gameState.connection then gameState.connection:Disconnect() end
  gameState.model:Destroy()
 end
 local model=Instance.new("Model");model.Name="BeachVolley";model.Parent=parent
 local ball=Instance.new("Part");ball.Name="VolleyBall";ball.Shape=Enum.PartType.Ball;ball.Size=V(2.2,2.2,2.2);ball.Color=Color3.fromRGB(250,205,84);ball.Material=Enum.Material.SmoothPlastic;ball.Anchored=true;ball.CanCollide=false;ball.CanTouch=false;ball.CanQuery=false;ball.Parent=model
 local board=Instance.new("Part");board.Name="CourtReadout";board.Size=V(.1,.1,.1);board.Position=boardPosition;board.Anchored=true;board.Transparency=1;board.CanCollide=false;board.CanTouch=false;board.CanQuery=false;board.Parent=model
 local gui=Instance.new("BillboardGui");gui.Size=UDim2.fromOffset(230,66);gui.MaxDistance=48;gui.AlwaysOnTop=false;gui.Parent=board
 local text=Instance.new("TextLabel");text.Size=UDim2.fromScale(1,1);text.BackgroundColor3=Color3.fromRGB(25,48,51);text.BackgroundTransparency=.12;text.TextColor3=Color3.fromRGB(255,239,205);text.TextSize=13;text.Font=Enum.Font.GothamMedium;text.TextWrapped=true;text.Parent=gui
 local corner=Instance.new("UICorner");corner.CornerRadius=UDim.new(0,8);corner.Parent=text
 local stroke=Instance.new("UIStroke");stroke.Name="ReadoutStroke";stroke.ApplyStrokeMode=Enum.ApplyStrokeMode.Border;stroke.Color=Color3.fromRGB(235,190,105);stroke.Thickness=1;stroke.Transparency=.4;stroke.Parent=text
 local state={model=model,ball=ball,label=text,best=0};gameState=state;reset(state)
 state.connection=Run.Heartbeat:Connect(function(dt)
  if not model.Parent then state.connection:Disconnect();return end
  if state.phase=="Resetting" then if os.clock()>=state.resetAt then reset(state) end;return end
  if state.phase~="Playing" then return end
  dt=math.min(dt,.1)
  local old=state.position
  local position=old+state.velocity*dt+V(0,-6*dt*dt,0)
  state.velocity+=V(0,-12*dt,0)
  local crossed=(old.Z<netZ and position.Z>=netZ) or (old.Z>netZ and position.Z<=netZ)
  if crossed then
   local alpha=(netZ-old.Z)/(position.Z-old.Z)
   local crossingX=old.X+(position.X-old.X)*alpha
   if crossingX<netMinX or crossingX>netMaxX then
    fault(state,"Out of bounds")
   elseif old.Y+(position.Y-old.Y)*alpha<minimumCrossingHeight then
    fault(state,"Net hit")
   elseif not state.crossed then
    state.crossed=true;state.rally+=1;state.best=math.max(state.best,state.rally)
    label(state,"MIC VOLLEY · RALLY "..state.rally.."\nReturn the ball with an aimed beam\nSofter shots are easier to control")
   end
  end
  if state.phase=="Playing" then
   if position.X<minimum.X or position.X>maximum.X or position.Z<minimum.Z or position.Z>maximum.Z then fault(state,"Out of bounds")
   elseif position.Y<=floorBallY then position=V(position.X,floorBallY,position.Z);fault(state,"Ball landed") end
  end
  state.position=position
  ball.CFrame=CFrame.new(position)*CFrame.Angles(os.clock()*2,0,os.clock())
 end)
 return model
end
function Volley.Hit(player,origin,direction,length,width,power)
 local state=gameState
 if not state or not state.model.Parent or state.phase=="Resetting" then return false end
 local character=player.Character
 local root=character and character:FindFirstChild("HumanoidRootPart")
 local humanoid=character and character:FindFirstChildOfClass("Humanoid")
 if not root or not humanoid or humanoid.Health<=0 or root.Position.X<playerMinimum.X or root.Position.X>playerMaximum.X
  or root.Position.Z<playerMinimum.Z or root.Position.Z>playerMaximum.Z or (root.Position-state.position).Magnitude>35 then return false end
 if not Rules.InBeam(origin,direction,state.position,length,width,1.1) then return false end
 local flat=V(direction.X,0,direction.Z)
 if flat.Magnitude<.05 then return false end
 state.velocity=flat.Unit*(9+math.clamp(power,0,1)*6)+V(0,22,0)
 state.phase="Playing";state.crossed=false
 label(state,"MIC VOLLEY · RALLY "..state.rally.."\nGet across the net for the return\nSofter shots are easier to control")
 return true
end
return Volley
