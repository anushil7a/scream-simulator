local CityMap=require(script.Parent:WaitForChild("CityMap"))
local Players=game:GetService("Players")
local RS=game:GetService("ReplicatedStorage")
local UIS=game:GetService("UserInputService")
local Run=game:GetService("RunService")
local Tween=game:GetService("TweenService")
local Debris=game:GetService("Debris")
local TextService=game:GetService("TextService")
local GuiService=game:GetService("GuiService")
-- External signals outlive the HUD; suppress queued callbacks during teardown too.
local clientConnections={}
local clientDestroyed=false
local function connectClient(signal,callback)
 if clientDestroyed then return end
 local connection=signal:Connect(function(...)
  if not clientDestroyed then callback(...) end
 end)
 table.insert(clientConnections,connection)
 return connection
end
script.Destroying:Connect(function()
 clientDestroyed=true
 for _,connection in ipairs(clientConnections) do connection:Disconnect() end
 table.clear(clientConnections)
end)
local originalTouchControls=GuiService.TouchControlsEnabled
script.Destroying:Connect(function() GuiService.TouchControlsEnabled=originalTouchControls end)
local p=Players.LocalPlayer
local originalCameraMode=p.CameraMode
local originalMinZoom,originalMaxZoom=p.CameraMinZoomDistance,p.CameraMaxZoomDistance
-- Keep wheel/pinch zoom outside first person on desktop and touch.
local function applyThirdPerson()
 p.CameraMaxZoomDistance=math.max(originalMaxZoom,6)
 p.CameraMinZoomDistance=math.max(originalMinZoom,6)
 p.CameraMode=Enum.CameraMode.Classic
end
applyThirdPerson()
connectClient(p.CharacterAdded,applyThirdPerson)
local Config=require(RS:WaitForChild("Shared"):WaitForChild("Config"))
local FirstBeamGuide=require(RS.Shared:WaitForChild("FirstBeamGuide"))
local InteractionRules=require(RS.Shared:WaitForChild("InteractionRules"))
local mic=require(script.Parent:WaitForChild("Microphone")).new()
local attackAudio=require(script.Parent:WaitForChild("AttackAudio")).new()
local attackAudioSettings=require(RS.Shared.AttackAudioConfig)
local gameplayAudio=require(script.Parent:WaitForChild("GameplayAudio")).new()
local gameplayAudioSettings=require(RS.Shared.GameplayAudioConfig)
script.Destroying:Connect(function() gameplayAudio:Destroy() end)
connectClient(p.CharacterRemoving,function() gameplayAudio:Clear() end)
local function cueContext()
 gameplayAudio:SetContext(mic.ready and mic.power>.12,mic.phase~=nil or not mic.ready)
end
local function playGameplayCue(kind,position)
 cueContext()
 if position then
  local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
  if not root or (root.Position-position).Magnitude>gameplayAudioSettings.Range then return end
 end
 gameplayAudio:Play(kind,os.clock(),position)
end
script.Destroying:Connect(function() attackAudio:Destroy() end)
script.Destroying:Connect(function() mic:Destroy() end)
local ShopUI=require(script.Parent:WaitForChild("ShopUI"))
script.Destroying:Connect(function() ShopUI.Clear() end)
local ScreamEffects=require(script.Parent:WaitForChild("ScreamEffects"))
script.Destroying:Connect(function() ScreamEffects.Clear() end)
local remotes=RS:WaitForChild("ScreamRemotes")
local action=remotes:WaitForChild("Action")
local gui=Instance.new("ScreenGui");gui.Name="ScreamUI";gui.ResetOnSpawn=false;gui.ZIndexBehavior=Enum.ZIndexBehavior.Sibling;gui.Parent=p:WaitForChild("PlayerGui")
local dark=Color3.fromRGB(10,16,31);local panel=Color3.fromRGB(23,34,55);local gold=Color3.fromRGB(80,226,255);local white=Color3.fromRGB(240,247,255);local muted=Color3.fromRGB(159,178,207)
local data={level=1,xp=0,xpNext=Config.XPToNext(1),coins=0,health=100,sound="TinyAah",aura="Gold",quests={},settings={volume=.55,reducedShake=false}}
local function frame(parent,name,size,pos,color)
 local f=Instance.new("Frame");f.Name=name;f.Size=size;f.Position=pos;f.BackgroundColor3=color or dark;f.BorderSizePixel=0;f.Parent=parent
 local c=Instance.new("UICorner");c.CornerRadius=UDim.new(0,10);c.Parent=f;return f
end
local function label(parent,text,size,pos,fontSize,color)
 local l=Instance.new("TextLabel");l.Size=size;l.Position=pos;l.BackgroundTransparency=1;l.Text=text;l.TextSize=fontSize or 15;l.Font=Enum.Font.GothamMedium;l.TextColor3=color or white;l.TextXAlignment=Enum.TextXAlignment.Left;l.TextWrapped=true;l.Parent=parent;return l
end
local function button(parent,name,text,size,pos,callback,color)
 local b=Instance.new("TextButton");b.Name=name;b.Size=size;b.Position=pos;b.BackgroundColor3=color or panel;b.TextColor3=white;b.Text=text;b.TextSize=14;b.Font=Enum.Font.GothamBold;b.AutoButtonColor=true;b.BorderSizePixel=0;b.Parent=parent
 local c=Instance.new("UICorner");c.CornerRadius=UDim.new(0,8);c.Parent=b;b.Activated:Connect(callback);return b
end
local top=frame(gui,"Navigation",UDim2.fromOffset(250,40),UDim2.fromOffset(14,12));top.BackgroundTransparency=1
local modal=frame(gui,"Menu",UDim2.fromOffset(720,520),UDim2.fromScale(.5,.5));modal.AnchorPoint=Vector2.new(.5,0);modal.ZIndex=10;modal.Visible=false
local menuEdge=Instance.new("UIStroke");menuEdge.Color=gold;menuEdge.Transparency=.5;menuEdge.Parent=modal
modal.BackgroundColor3=Color3.new(1,1,1)
local menuGlow=Instance.new("UIGradient");menuGlow.Color=ColorSequence.new(Color3.fromRGB(36,50,76),dark);menuGlow.Rotation=80;menuGlow.Parent=modal
local brandStripe=frame(modal,"SignalStripe",UDim2.new(1,-44,0,2),UDim2.fromOffset(22,8),gold)
local menuScale=Instance.new("UIScale");menuScale.Parent=modal
local title=label(modal,"BEAM COLLECTION",UDim2.new(1,-85,0,36),UDim2.fromOffset(22,15),23,gold)
local subtitle=label(modal,"Train for XP. Unlock a new beam style every ten levels.",UDim2.new(1,-44,0,25),UDim2.fromOffset(22,52),14,muted)
button(modal,"Close","X",UDim2.fromOffset(44,44),UDim2.new(1,-56,0,10),function() modal.Visible=false end)
local content=Instance.new("ScrollingFrame");content.Name="Content";content.Size=UDim2.new(1,-40,1,-148);content.Position=UDim2.fromOffset(20,132);content.BackgroundTransparency=1;content.BorderSizePixel=0;content.ScrollBarThickness=4;content.AutomaticCanvasSize=Enum.AutomaticSize.Y;content.CanvasSize=UDim2.new();content.Parent=modal
local list=Instance.new("UIListLayout");list.Padding=UDim.new(0,10);list.SortOrder=Enum.SortOrder.LayoutOrder;list.Parent=content
local selected="Shop";local render;local tabs={};local mapDot;local devPanel;local narrow=false;local lastLayoutWidth=0
local conversationPanel,showConversation,closeConversation
local function toggleTab(name)
 local opening=not modal.Visible or selected~=name
 selected=name;modal.Visible=opening
 if opening then
  if name=="Shop" then action:FireServer("ShopRefresh") end
  if closeConversation then closeConversation() end
  if devPanel then devPanel.Visible=false end
  render()
 end
end
local function toggle()
 if modal.Visible then modal.Visible=false else toggleTab(selected) end
end
local shop=button(top,"ShopToggle","SHOP  [B]",UDim2.fromOffset(125,36),UDim2.fromOffset(0,0),function() toggleTab("Shop") end,gold);shop.TextColor3=dark
local questsToggle=button(top,"QuestsToggle","QUESTS",UDim2.fromOffset(95,36),UDim2.fromOffset(134,0),function() toggleTab("Quests") end)
local hud=frame(gui,"CompactHUD",UDim2.fromOffset(242,94),UDim2.new(0,14,1,-108));hud.BackgroundTransparency=.08
frame(hud,"EnergyAccent",UDim2.new(1,-24,0,2),UDim2.fromOffset(12,2),gold)
local stats=label(hud,"LEVEL 1     •     0 coins",UDim2.new(1,-24,0,22),UDim2.fromOffset(12,7),14,gold)
local health=label(hud,"100 HP",UDim2.fromOffset(65,20),UDim2.fromOffset(12,31),12)
local hb=frame(hud,"HealthTrack",UDim2.fromOffset(142,6),UDim2.fromOffset(83,38),panel)
local hf=frame(hb,"Fill",UDim2.fromScale(1,1),UDim2.new(),Color3.fromRGB(105,224,158))
local displayedHealth,displayedMaximum
local function refreshHealth()
 local character=p.Character
 local humanoid=character and character:FindFirstChildOfClass("Humanoid")
 -- Keep the last observed value between characters; a generic server snapshot
 -- must not briefly show full health over a dead or missing character.
 if not humanoid and displayedHealth~=nil then return end
 local maximum=math.max(1,humanoid and humanoid.MaxHealth or data.maxHealth or 100)
 local current=math.clamp(humanoid and humanoid.Health or data.health or maximum,0,maximum)
 if current==displayedHealth and maximum==displayedMaximum then return end
 displayedHealth,displayedMaximum=current,maximum
 health.Text=string.format("%d/%d",math.ceil(current),math.ceil(maximum))
 hf.Size=UDim2.fromScale(current/maximum,1)
end
local xpText=label(hud,"0 / 103 XP",UDim2.new(1,-24,0,19),UDim2.fromOffset(12,52),12,muted)
local xb=frame(hud,"XPTrack",UDim2.fromOffset(218,4),UDim2.fromOffset(12,79),panel)
local xf=frame(xb,"Fill",UDim2.fromScale(0,1),UDim2.new(),gold)
local zone=label(gui,"SAFE CITY • PvP off",UDim2.fromOffset(240,28),UDim2.new(.5,-120,0,12),13);zone.TextXAlignment=Enum.TextXAlignment.Center
local tracked=label(gui,"",UDim2.fromOffset(290,50),UDim2.fromOffset(16,56),13);tracked.Name="QuestTracker";tracked.TextYAlignment=Enum.TextYAlignment.Top
tracked.BackgroundColor3=dark;tracked.BackgroundTransparency=.12
local trackerCorner=Instance.new("UICorner");trackerCorner.CornerRadius=UDim.new(0,8);trackerCorner.Parent=tracked
local trackerPadding=Instance.new("UIPadding");trackerPadding.PaddingLeft=UDim.new(0,6);trackerPadding.PaddingRight=UDim.new(0,6);trackerPadding.PaddingTop=UDim.new(0,4);trackerPadding.PaddingBottom=UDim.new(0,4);trackerPadding.Parent=tracked
local toast=label(gui,"",UDim2.new(.7,0,0,48),UDim2.new(.15,0,.72,0),16,gold);toast.TextXAlignment=Enum.TextXAlignment.Center;toast.AnchorPoint=Vector2.new(.5,1);toast.Position=UDim2.fromScale(.5,.72)
toast.Name="Notification";toast.ZIndex=30;toast.BackgroundColor3=dark;toast.BackgroundTransparency=.08;toast.Visible=false
local saveNotice=label(gui,"",UDim2.fromOffset(250,28),UDim2.new(.5,-125,0,40),12,gold);saveNotice.TextXAlignment=Enum.TextXAlignment.Center
local notifications=require(script.Parent:WaitForChild("NotificationQueue")).new()
local toastWidth=0
local function notify(t,urgent,key) notifications:Push(t,urgent,key) end
local nextCast=0;local sequence=0;local captureSource=nil
local sustainedControl,sustainedRules
local voiceAccessInterrupted=false
local windowFocused=true
local function cancelCapture()
 if sustainedControl then sustainedControl:Cancel();return end
 captureSource=nil;mic:Cancel();action:FireServer("CancelCast")
end
script.Destroying:Connect(function()
 p.CameraMode=originalCameraMode
 p.CameraMinZoomDistance=originalMinZoom;p.CameraMaxZoomDistance=originalMaxZoom
end)
local function blocked()
 local character=p.Character
 local humanoid=character and character:FindFirstChildOfClass("Humanoid")
 if not humanoid or humanoid.Health<=0 or humanoid.PlatformStand then return true end
 local now=workspace:GetServerTimeNow()
 return GuiService.MenuIsOpen or UIS:GetFocusedTextBox()~=nil or (conversationPanel and conversationPanel.Visible) or modal.Visible or (devPanel and devPanel.Visible) or not mic.ready or now<(p:GetAttribute("ProtectionEnds") or 0) or now<(p:GetAttribute("DodgeEnds") or 0) or now<(p:GetAttribute("KnockdownEnds") or 0)
end
local function beamBlocked()
 return data.voiceEligible~=true or blocked()
end
local function beginCapture(source)
 if sustainedControl or captureSource or beamBlocked() or os.clock()<nextCast then return end
 if mic:Begin() then sequence+=1;captureSource=source;action:FireServer("BeginCast",sequence) end
end
local function aimRay()
 local camera=workspace.CurrentCamera
 if not camera or camera.ViewportSize.X<2 or camera.ViewportSize.Y<2 then return nil end
 local location=UIS.TouchEnabled and camera.ViewportSize/2 or UIS:GetMouseLocation()
 local ray=camera:ViewportPointToRay(location.X,location.Y)
 local params=RaycastParams.new();params.FilterDescendantsInstances={p.Character};params.FilterType=Enum.RaycastFilterType.Exclude;params.RespectCanCollide=true
 return ray,workspace:Raycast(ray.Origin,ray.Direction*1000,params)
end
if remotes:GetAttribute("AutomaticVoice")==true then
 sustainedRules=require(RS.Shared:WaitForChild("SustainedAttack"))
 local VoiceActivation=require(RS.Shared:WaitForChild("VoiceActivation"))
 sustainedControl=require(script.Parent:WaitForChild("SustainedControls")).new(VoiceActivation.new(),
  function(verb,arg) action:FireServer(verb,arg) end,
  function()
   if not workspace.CurrentCamera then return nil end
   local ray,hit=aimRay()
   if not ray then return nil end
   return hit and hit.Position or ray.Origin+ray.Direction*1000
  end,function() notifications:Remove("voice") end)
 script.Destroying:Connect(function() sustainedControl:Destroy() end)
end
local function voiceEligibilityHint(compact)
 if data.voiceEligible==true then return nil end
 if data.voiceStatus=="denied" then
  return compact and "VOICE ACCESS REQUIRED\nCheck Roblox voice settings" or "Beams OFF: Roblox voice access is not enabled. Check Roblox voice settings; server checks repeat. Voice chat is unchanged."
 end
 if data.voiceStatus=="unavailable" then
  return compact and "VOICE CHECK DELAYED\nWaiting to retry" or "Beams OFF: Voice verification is delayed. The server retries when a check can run. Voice chat is unchanged."
 end
 return compact and "CHECKING ROBLOX VOICE\nBeams are OFF" or "Beams OFF: Checking Roblox voice access. Voice chat is unchanged."
end
-- Process every server transition, not only the last state visible next frame.
local function observeVoiceEligibility(nextData)
 if nextData.voiceEligible==true then return end
 if nextData.voiceStatus=="denied" or nextData.voiceStatus=="unavailable" then voiceAccessInterrupted=true end
 if sustainedControl then sustainedControl:SetArmed(false)
 elseif captureSource then cancelCapture() end
end
local function toggleVoice()
 if not sustainedControl then return end
 -- Pausing is always allowed; arming must be an available gameplay action.
 if not sustainedControl.armed and (not windowFocused or beamBlocked()) then
  notify(voiceEligibilityHint() or "Beams stay OFF. Finish mic setup or wait for gameplay to be ready, then turn them on.",true,"voice");return
 end
 sustainedControl:SetArmed(not sustainedControl.armed)
 notify(sustainedControl.armed and "Beams ON. Normal speech can fire attacks. Go quiet, then speak. Turn OFF to talk freely; voice chat is unchanged."
  or "Beams OFF. Talk freely without attacking. Voice chat is unchanged.",false,"voice")
end
local function screamToggleLabel(armed,touch)
 return (armed and "BEAMS: ON" or "BEAMS: OFF").."\n"..(touch and "Tap" or "[E]")..(armed and " to turn off" or " to turn on")
end
local function releaseCapture(source)
 if captureSource~=source then return end
 captureSource=nil
 if beamBlocked() then cancelCapture();return end
 local power,reason=mic:Release();if power<.08 then action:FireServer("CancelCast");notify(reason or "Use your voice while holding attack.",true,"capture");return end
 local ray,hit=aimRay()
 if not ray then action:FireServer("CancelCast");return end
 action:FireServer("Cast",{sequence=sequence,power=power,aim=hit and hit.Position or ray.Origin+ray.Direction*1000})
 nextCast=os.clock()+4
end
local function dodge()
 cancelCapture()
 if not blocked() then action:FireServer("Dodge") end
end
local controls=frame(gui,"Actions",UDim2.fromOffset(260,88),UDim2.new(1,-274,1,-102));controls.BackgroundTransparency=1
local castButton=button(controls,"Cast","BEAM  [E]",UDim2.fromOffset(144,44),UDim2.fromOffset(116,0),toggleVoice,gold);castButton.TextColor3=dark
castButton.TextWrapped=true;castButton.Selectable=true
local voiceTimeTrack=frame(castButton,"VoiceTimeTrack",UDim2.new(1,-12,0,3),UDim2.new(0,6,1,-6),panel)
local voiceTimeFill=frame(voiceTimeTrack,"RemainingOrRecovery",UDim2.fromScale(0,1),UDim2.new(),muted)
voiceTimeTrack.Visible=false
castButton.InputBegan:Connect(function(input)
 if input.UserInputType==Enum.UserInputType.MouseButton1 or input.UserInputType==Enum.UserInputType.Touch then beginCapture(input) end
end)
local micPanel=frame(gui,"MicSetup",UDim2.fromOffset(430,260),UDim2.fromScale(.5,.5));micPanel.AnchorPoint=Vector2.new(.5,.5);micPanel.ZIndex=20
local micTitle=label(micPanel,"YOUR VOICE. YOUR POWER.",UDim2.new(1,-36,0,35),UDim2.fromOffset(18,16),21,gold)
local micStatus=label(micPanel,"",UDim2.new(1,-36,0,90),UDim2.fromOffset(18,58),15)
label(micPanel,sustainedControl and "BEAMS ON: normal speech can attack. OFF does not mute voice. Avoid profanity. Roblox records and moderates voice." or "Roblox voice access required. Nearby players may hear you. Avoid profanity. Roblox records and moderates voice.",UDim2.new(1,-36,0,50),UDim2.fromOffset(18,146),12,muted)
button(micPanel,"Calibrate","CALIBRATE MIC",UDim2.fromOffset(188,36),UDim2.fromOffset(18,208),function() mic:Calibrate() end,gold).TextColor3=dark
button(micPanel,"Retry","CHECK ACCESS",UDim2.fromOffset(188,36),UDim2.fromOffset(224,208),function() mic:Check() end)
for _,v in ipairs(micPanel:GetDescendants()) do if v:IsA("GuiObject") then v.ZIndex=21 end end
local micScale=Instance.new("UIScale");micScale.Parent=micPanel
local meter=frame(gui,"MicPower",UDim2.fromOffset(230,62),UDim2.new(.5,-115,1,-74))
local meterText=label(meter,"LIVE MIC 0%\nHold attack before speaking",UDim2.new(1,-20,0,40),UDim2.fromOffset(10,3),12,gold)
local meterTrack=frame(meter,"Track",UDim2.new(1,-20,0,5),UDim2.fromOffset(10,49),panel)
local meterFill=frame(meterTrack,"Fill",UDim2.fromScale(0,1),UDim2.new(),gold)
if sustainedControl then
 local threshold=frame(meterTrack,"VoiceStartThreshold",UDim2.fromOffset(2,11),UDim2.new(sustainedControl.gate.OnPower,0,.5,0),white)
 threshold.AnchorPoint=Vector2.new(.5,.5);threshold.ZIndex=meterFill.ZIndex+1
end
local aimGui=Instance.new("ScreenGui");aimGui.Name="ScreamAim";aimGui.ResetOnSpawn=false;aimGui.ScreenInsets=Enum.ScreenInsets.None;aimGui.Parent=p.PlayerGui
script.Destroying:Connect(function() aimGui:Destroy() end)
local reticle=label(aimGui,"+",UDim2.fromOffset(24,24),UDim2.new(.5,-12,.5,-12),22,white);reticle.Name="Crosshair";reticle.TextXAlignment=Enum.TextXAlignment.Center
local hitFeedback=require(script.Parent:WaitForChild("HitFeedback")).new()
local hitText=label(aimGui,"",UDim2.fromOffset(210,26),UDim2.new(.5,-105,.5,-48),16,gold);hitText.Name="ConfirmedDamage";hitText.TextXAlignment=Enum.TextXAlignment.Center;hitText.Visible=false
local aimInfo=label(gui,"",UDim2.fromOffset(290,48),UDim2.new(.5,-145,.5,25),13,gold);aimInfo.TextXAlignment=Enum.TextXAlignment.Center
local reportedReady=nil;local readyReportAt=0
local dodgeButton=button(controls,"Dodge","DODGE  [Q]",UDim2.fromOffset(108,44),UDim2.fromOffset(0,0),dodge)
local sprinting=false
local function setSprint(requested)
 local character=p.Character;local humanoid=character and character:FindFirstChildOfClass("Humanoid")
 if requested and (not windowFocused or not mic.ready or GuiService.MenuIsOpen or UIS:GetFocusedTextBox()~=nil
  or modal.Visible or (devPanel and devPanel.Visible) or (conversationPanel and conversationPanel.Visible)
  or not humanoid or humanoid.Health<=0 or humanoid.PlatformStand or humanoid.Sit or humanoid.SeatPart
  or workspace:GetServerTimeNow()<(p:GetAttribute("KnockdownEnds") or 0)) then requested=false end
 if sprinting==requested then return end
 sprinting=requested;action:FireServer("Sprint",requested)
end
local function targetCovered(root,targetRoot,targetModel)
 local character=p.Character;local head=character and character:FindFirstChild("Head")
 local origin=root.Position+Vector3.new(0,1,0)
 if head and head:IsA("BasePart") and (head.Position-root.Position).Magnitude<5 then origin=head.Position end
 local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Exclude
 params.FilterDescendantsInstances={character,targetModel};params.RespectCanCollide=true
 return workspace:Raycast(origin,targetRoot.Position-origin,params)~=nil
end
local function playerTargetInfo(target,humanoid,canFight,far,now,currentFar,covered)
 if humanoid.Health<=0 then return nil,false end
 local protection=math.max(0,(target:GetAttribute("ProtectionEnds") or 0)-now)
 local rolling=now<(target:GetAttribute("DodgeEnds") or 0)
 local status=not canFight and "SAFE · PvP OFF"
  or protection>0 and string.format("PROTECTED · %.1fs",protection)
  or rolling and "DODGING" or far and "OUT OF MAX RANGE" or currentFar and "BEYOND CURRENT RANGE" or covered and "BEHIND COVER" or "ARENA OPPONENT"
 local level=target:GetAttribute("ScreamLevel")
 local name=target.DisplayName..(type(level)=="number" and string.format(" · LV %d",level) or "")
 return string.format("%s\n%d / %d HP\n%s",name,math.ceil(humanoid.Health),math.ceil(humanoid.MaxHealth),status),
  canFight and protection<=0 and not rolling and not far and not currentFar and not covered
end
local function residentTargetInfo(model,humanoid,far,currentFar,covered)
 if model:GetAttribute("ResidentActive")==false then return nil,false end
 if not humanoid or humanoid.Health<=0 then return nil,false end
 local status=far and "OUT OF MAX RANGE" or currentFar and "BEYOND CURRENT RANGE" or covered and "BEHIND COVER" or "TRAINING RESIDENT"
 return string.format("%s\n%d / %d HP\n%s",model:GetAttribute("DisplayName") or model.Name,
  math.ceil(humanoid.Health),math.ceil(humanoid.MaxHealth),status),not far and not currentFar and not covered
end
local sprintButton=button(controls,"Sprint","SPRINT [SHIFT]",UDim2.fromOffset(164,32),UDim2.fromOffset(96,52),function() setSprint(not sprinting) end)
local talkTarget
local nextResidentUi=0
local function refreshResidentLabels(root,camera,residents)
 local nearest,best=nil,13
 local speaker,speechDistance=nil,24
 local damaged,damageDistance=nil,18
 local visible={}
 for _,bot in ipairs(residents) do
  local r=bot:FindFirstChild("HumanoidRootPart");local head=bot:FindFirstChild("Head");local h=bot:FindFirstChildOfClass("Humanoid")
  if not head then continue end
  local nameplate=head:FindFirstChild("Nameplate");local speech=head:FindFirstChild("SpeechBubble")
  if nameplate then nameplate.Enabled=false end
  if speech then speech.Enabled=false end
  if not r or not root or not camera or not h or h.Health<=0 or bot:GetAttribute("ResidentActive")==false then continue end
  local distance=(r.Position-root.Position).Magnitude
  local _,onScreen=camera:WorldToViewportPoint(head.Position)
  if not onScreen then continue end
  visible[bot]={nameplate=nameplate,speech=speech}
  if distance<best and InteractionRules.CanReachNpc(root.Parent,bot,13) then nearest=bot;best=distance end
  if h.Health<h.MaxHealth and distance<damageDistance then damaged=bot;damageDistance=distance end
  local words=speech and speech:FindFirstChildOfClass("TextLabel")
  if words and words.Visible and distance<speechDistance then speaker=bot;speechDistance=distance end
 end
 -- A single interaction name, at most one additional hurt resident, and one
 -- speech bubble keep crowds readable. Occlusion still uses native billboards.
 for _,bot in pairs({nearest,damaged}) do local item=visible[bot];if item and item.nameplate then item.nameplate.Enabled=true end end
 if speaker and visible[speaker].speech then visible[speaker].speech.Enabled=true end
 return nearest
end
local function requestTalk()
 if not windowFocused or GuiService.MenuIsOpen or UIS:GetFocusedTextBox() or modal.Visible
  or (devPanel and devPanel.Visible) or (conversationPanel and conversationPanel.Visible) or not mic.ready then return end
 local target=talkTarget
 if not target or not target.Parent or target:GetAttribute("ResidentActive")==false
  or not InteractionRules.CanReachNpc(p.Character,target,13) then return end
 cancelCapture()
 action:FireServer("Talk",target:GetAttribute("NpcId") or target.Name)
end
local talkButton=button(gui,"Talk","TALK [T]",UDim2.fromOffset(120,34),UDim2.new(.5,-60,1,-108),requestTalk);talkButton.Visible=false
devPanel=frame(gui,"TestPanel",UDim2.fromOffset(230,330),UDim2.new(1,-244,0,60));devPanel.Visible=false;devPanel.ZIndex=10
local testContent=Instance.new("ScrollingFrame");testContent.Name="Commands";testContent.BackgroundTransparency=1;testContent.BorderSizePixel=0;testContent.ScrollBarThickness=4;testContent.Position=UDim2.fromOffset(8,76);testContent.Size=UDim2.new(1,-16,1,-84);testContent.CanvasSize=UDim2.fromOffset(0,235);testContent.Parent=devPanel
label(devPanel,"TEST SESSION",UDim2.fromOffset(210,25),UDim2.fromOffset(10,8),17,gold)
label(devPanel,"Temporary progress. Shared combat is isolated.",UDim2.fromOffset(210,38),UDim2.fromOffset(10,35),12,muted)
local testCommands={{"XP","+500 XP"},{"AddLevels","+10 levels"},{"Coins","+1,000 coins"},{"MaxLevel","Level "..Config.MaxLevel},{"LevelOne","Level 1"},{"Heal","Heal"},{"Hub","Safe hub"},{"Arena","Arena"},{"Beach","Beach"},{"ResetQuests","Reset quests"}}
if Run:IsStudio() then table.insert(testCommands,{"ResetBots","Reset bots"});table.insert(testCommands,{"StudioMovement","Test movement"}) end
testContent.CanvasSize=UDim2.fromOffset(0,math.ceil(#testCommands/2)*47)
for i,item in ipairs(testCommands) do
 button(testContent,item[1],item[2],UDim2.fromOffset(98,44),UDim2.fromOffset(((i-1)%2)*108,math.floor((i-1)/2)*47),function() action:FireServer("DevCommand",item[1]) end)
end
local testButton=button(gui,"TestToggle","TEST TOOLS",UDim2.fromOffset(112,32),UDim2.new(1,-126,0,14),function() devPanel.Visible=not devPanel.Visible;if devPanel.Visible then modal.Visible=false end end);testButton.Visible=false
-- Regular players use the former test-tools corner for a north-up map.
-- Keep a separate view: modal renders replace mapDot but never this HUD map.
local miniMapButton=button(gui,"MiniMap","MAP",UDim2.fromOffset(112,132),UDim2.new(1,-126,0,14),function() toggleTab("Map") end)
miniMapButton.TextSize=12;miniMapButton.TextYAlignment=Enum.TextYAlignment.Top;miniMapButton.Visible=false
local miniMapPadding=Instance.new("UIPadding");miniMapPadding.PaddingTop=UDim.new(0,10);miniMapPadding.Parent=miniMapButton
local miniMapHolder=frame(miniMapButton,"MiniMapHolder",UDim2.new(1,-16,1,-42),UDim2.fromOffset(8,34));miniMapHolder.BackgroundTransparency=1
local miniMapView=CityMap.create(miniMapHolder,true)
local miniMapAvailable=false
local function card(height)
 local c=frame(content,"Card",UDim2.new(1,-8,0,height),UDim2.new(),panel)
 local edge=Instance.new("UIStroke");edge.Color=Color3.fromRGB(64,91,125);edge.Transparency=.65;edge.Parent=c
 return c
end
local function info(text,height) local width=math.min(720,gui.AbsoluteSize.X-24)-76;local fit=TextService:GetTextSize(text,15,Enum.Font.GothamMedium,Vector2.new(width,10000)).Y+24;local c=card(math.max(height or 70,fit));label(c,text,UDim2.new(1,-28,1,-20),UDim2.fromOffset(14,10),15);return c end
local renderedMenuKey,renderedTab
local renderRevision=0
script.Destroying:Connect(function() renderRevision+=1;gui:Destroy() end)
local function menuKey()
 local fields
 if selected=="Screams" then fields={level=data.level,sound=data.sound,amplifier=data.amplifierEquipped}
 elseif selected=="Quests" then fields={quests=data.quests,active=data.activeQuest,available=data.availableQuests,challenges=data.combatChallenges,level=data.level}
 elseif selected=="Style" then fields={aura=data.aura,custom=data.customColor,customEquipped=data.useCustomColor,pass=data.spectrumPass,owned=data.amplifierOwned,equipped=data.amplifierEquipped}
 elseif selected=="Shop" then fields={spectrum=data.spectrumPass,movement=data.movementPass,inventory=data.shop and data.shop.inventory,ends=data.shop and data.shop.ends,ready=data.shop and data.shop.ready,saving=data.savingAvailable}
 elseif selected=="Settings" then fields={settings=data.settings}
 else fields={} end
 return selected..":"..gui.AbsoluteSize.X..":"..game:GetService("HttpService"):JSONEncode(fields)
end
render=function()
 if selected=="Screams" then
  subtitle.Text=data.level>=Config.MaxLevel and ("Level "..Config.MaxLevel.." • MAX LEVEL") or ("Level "..data.level.." • "..data.xp.." / "..data.xpNext.." XP")
 end
 local key=menuKey()
 if key==renderedMenuKey then return end
 local scroll=renderedTab==selected and content.CanvasPosition or Vector2.zero
 renderedMenuKey=key;renderedTab=selected;renderRevision+=1
 local revision=renderRevision
 ShopUI.Clear()
 mapDot=nil
 narrow=gui.AbsoluteSize.X-24<620
 for _,c in ipairs(content:GetChildren()) do if c:IsA("GuiObject") then c:Destroy() end end
 for name,b in pairs(tabs) do b.BackgroundColor3=name==selected and Color3.fromRGB(64,93,99) or panel end
 if selected=="Shop" then
  title.Text="THE AMPLIFIER";subtitle.Text="SIGNATURE COLORS / POWER YOUR PROGRESS"
  ShopUI.Render(data,{card=card,frame=frame,label=label,button=button,info=info,narrow=narrow},action)
 elseif selected=="Screams" then
  title.Text="BEAM COLLECTION"
  local nextStyle
  for _,style in ipairs(Config.Sounds) do
   if style.level>data.level and (not nextStyle or style.level<nextStyle.level) then nextStyle=style end
  end
  local progress=nextStyle and string.format("Next style: %s · level %d",nextStyle.name,nextStyle.level) or "All beam styles unlocked"
  local stats=Config.VoiceCombat.Stats(data.level,1,false)
  if nextStyle then
   local nextStats=Config.VoiceCombat.Stats(nextStyle.level,1,false)
   progress..=string.format("\nAt level %d: %d HP · %.1f max DPS",nextStyle.level,nextStats.health,nextStats.maxDps)
  end
  info(progress..string.format("\nNow: %d HP · %.1f max DPS\nTrain at the %s pad. Challenges are in Quests.",stats.health,stats.maxDps,data.training or "Rookie"))
  local maximum=Config.VoiceCombat.Stats(data.level,1,data.amplifierEquipped)
  local combatSummary=sustainedRules and string.format("CURRENT BEAM · LEVEL %d\nFULL-POWER LIMITS: %.1f DPS · %.2f studs",data.level,maximum.maxDps,maximum.maxRange)
   or string.format("CURRENT BEAM · LEVEL %d\nFULL-POWER LIMITS: %d damage · %.2f studs",data.level,maximum.damage,maximum.maxRange)
  info(combatSummary,narrow and 112 or 82)
  info("Sound styles change audio, not damage or range. These limits use your current level for the next attack. Lower voice power and cover shorten reach. DPS requires full power and continuous contact.",narrow and 150 or 96)
  for _,s in ipairs(Config.Sounds) do
   local c=card(narrow and 194 or 118);label(c,s.name.."  /  LEVEL "..s.level,UDim2.new(1,narrow and -28 or -156,0,narrow and 44 or 26),UDim2.fromOffset(14,8),17,gold)
   label(c,s.description,UDim2.new(1,narrow and -28 or -158,0,narrow and 40 or 25),UDim2.fromOffset(14,narrow and 54 or 36),13)
   label(c,"SOUND STYLE · uses your level's beam power",UDim2.new(1,-28,0,40),UDim2.fromOffset(14,narrow and 95 or 69),12,muted)
   local unlocked=data.level>=s.level
   local b=button(c,s.id,data.sound==s.id and "EQUIPPED" or unlocked and "EQUIP" or "LEVEL "..s.level,UDim2.fromOffset(116,37),UDim2.new(1,-130,0,narrow and 145 or 21),function() if unlocked then action:FireServer("EquipSound",s.id) end end)
   if not unlocked then b.TextColor3=muted end
  end
 elseif selected=="Quests" then
  title.Text="QUESTS & COMBAT";subtitle.Text="Beam combat first. One active task."
  info("COURTYARD TRAINING · "..(data.training or "Rookie").." recommended\nThree sparring pads in the west courtyard. Hit a fighter to start. Move out of red strikes or dodge. No PvP on the pads; training fighters can knock you out.")
  for _,spec in ipairs(Config.Progression.Challenges) do
   info(spec.name.." · "..((data.combatChallenges or {})[spec.id] or 0).."/"..spec.goal.."\n+"..Config.Progression.ChallengeXP(data.level).." XP on completion · renews automatically",68)
  end
  info("Training: contribute at least 10% damage. You must be no more than 20 levels above the fighter's reward band (Rookie 1-24, Brawler 25-59, Elite 60-100). Each qualifying KO or assist counts once. Environment cover is static. PvP XP is shared by damage; weak and repeated opponents pay less.")
  if data.activeQuest then
   local current=Config.GetQuest(data.activeQuest);local c=card(96)
   local progress=current and data.quests[current.id]
   local rewardReady=progress and not progress.claimed and progress.progress>=current.goal
   label(c,(rewardReady and "COMPLETE: " or "CURRENT: ")..(current and current.name or data.activeQuest),UDim2.new(1,-28,0,38),UDim2.fromOffset(14,6),14,gold)
   button(c,"ActiveQuestAction",rewardReady and "CLAIM" or "ABANDON",UDim2.fromOffset(116,38),UDim2.new(1,-130,0,50),function()
    if rewardReady then action:FireServer("ClaimQuest",current.id) else action:FireServer("AbandonQuest") end
   end)
  end
  local combatEvents={Crowd=true,Evade=true,Underdog=true,PracticeBeam=true,ArenaAssist=true}
  local questGroups={{title="BEAM COMBAT TASKS",combat=true},{title="OPTIONAL CITY ACTIVITIES",combat=false}}
  for _,group in ipairs(questGroups) do
   local headingShown=false
   for _,q in ipairs(Config.Quests) do
    if (combatEvents[q.event]==true)~=group.combat then continue end
    local available=q.menuAvailable==true or (data.availableQuests and data.availableQuests[q.id])
    if q.hidden and not available then continue end
    if not headingShown then info(group.title,50);headingShown=true end
    local v=data.quests[q.id] or {progress=0}
    local description=q.description
    if not available then description..="\n\nTo unlock: meet "..(q.giver or "a resident").." and use Talk." end
    local textWidth=math.min(720,gui.AbsoluteSize.X-24)-48-(narrow and 28 or 158)
    local nameHeight=math.max(26,TextService:GetTextSize(q.name,17,Enum.Font.GothamMedium,Vector2.new(textWidth,10000)).Y+4)
    local descriptionHeight=math.max(49,TextService:GetTextSize(description,13,Enum.Font.GothamMedium,Vector2.new(textWidth,10000)).Y+8)
    local descriptionY=12+nameHeight;local rewardY=descriptionY+descriptionHeight+5
    local actionY=narrow and rewardY+34 or 32
    local c=card(narrow and actionY+48 or math.max(150,rewardY+35))
    label(c,q.name,UDim2.new(1,narrow and -28 or -150,0,nameHeight),UDim2.fromOffset(14,8),17,gold)
    label(c,description,UDim2.new(1,narrow and -28 or -158,0,descriptionHeight),UDim2.fromOffset(14,descriptionY),13)
    label(c,v.progress.." / "..q.goal.."   •   +"..q.xp.." XP   •   +"..q.coins.." coins",UDim2.new(1,-28,0,30),UDim2.fromOffset(14,rewardY),12,muted)
    button(c,q.id,not available and "MEET NPC" or v.claimed and "CLAIMED" or v.progress>=q.goal and "CLAIM" or data.activeQuest==q.id and "TRACKING" or "ACCEPT",UDim2.fromOffset(116,38),UDim2.new(1,-130,0,actionY),function()
     if available and not v.claimed and (v.progress>=q.goal or data.activeQuest~=q.id) then action:FireServer(v.progress>=q.goal and "ClaimQuest" or "AcceptQuest",q.id) end
    end)
   end
  end
 elseif selected=="Style" then
  title.Text="YOUR SIGNATURE";subtitle.Text="Choose the color of your beam effects."
  ShopUI.ColorMixer(data,{card=card,frame=frame,label=label,button=button},action)
  local equipment=card(narrow and 142 or 90)
  label(equipment,"MICRO-SPEAKER",UDim2.new(1,-28,0,25),UDim2.fromOffset(15,10),17,gold)
  label(equipment,"+12% mic power · capped at 100%",UDim2.new(1,narrow and -28 or -170,0,35),UDim2.fromOffset(15,42),14)
  button(equipment,"MicroSpeaker",data.amplifierEquipped and "UNEQUIP" or data.amplifierOwned and "EQUIP" or tostring(Config.MicroSpeakerPrice).." COINS",UDim2.fromOffset(135,38),UDim2.new(1,-149,0,narrow and 90 or 24),function() action:FireServer("MicroSpeaker") end)
  info("Movement pass: repeated jumps (24-stud height limit) and consecutive rolls only in safe areas. Arena cooldowns always apply."..(Config.MovementPassId==0 and " Purchase setup is not available yet." or ""),70)
  local base=card(76)
  label(base,"YELLOW BASE",UDim2.new(1,-158,0,48),UDim2.fromOffset(15,10),17,Config.Auras.Gold)
  button(base,"BaseColor",data.aura=="Gold" and not data.useCustomColor and "EQUIPPED" or "USE YELLOW",UDim2.fromOffset(126,44),UDim2.new(1,-140,0,16),function() action:FireServer("SetAura","Gold") end)
  if data.aura~="Gold" and not data.useCustomColor then
   info("Your saved "..data.aura.." color is still equipped. Choosing yellow replaces this legacy selection; the old free palette is no longer selectable.")
  end
 elseif selected=="Map" then
  title.Text="CITY & COAST";subtitle.Text=string.format("Arena District: %d%% PvP. Rest of the map: %d%% safe.",CityMap.arenaPercent,100-CityMap.arenaPercent)
  local c=card(300)
  local holder=frame(c,"MapHolder",UDim2.new(1,-26,1,-26),UDim2.fromOffset(13,13));holder.BackgroundTransparency=1
  mapDot=CityMap.create(holder)
  CityMap.update(mapDot,p.Character and p.Character:FindFirstChild("HumanoidRootPart"))
  info(CityMap.mapHelp,64)
  info(CityMap.legend,CityMap.legendHeight)
  info(CityMap.activityHelp,86)
 else
  title.Text="SETTINGS & CONTROLS";subtitle.Text="Keep the action comfortable and easy to read."
  local touch=UIS.TouchEnabled
  local attackHelp
  if sustainedControl then
   attackHelp=string.format("BEAMS ON: normal speech can fire attacks. Aim, then speak; %.0fs max, %.0fs cooldown.\n%s toggles attacks. OFF lets you talk; voice chat is unchanged. Go quiet before each beam.",sustainedRules.MaxDuration,sustainedRules.Cooldown,touch and "Tap BEAMS" or "E / BEAMS")
  else attackHelp=touch and "Hold BEAM, speak into your mic, then release to fire toward the center of your view." or "Hold E / BEAM, speak into your mic, then release to fire toward your aim." end
  info(attackHelp,touch and 130 or 100)
  info("VOICE SAFETY\nAvoid profanity. Roblox's profanity rules depend on the game's rating and settings; harassment, threats and hate speech are not allowed. Rule violations may restrict voice or your account.\nRoblox records voice for moderation. The beam mechanic reads volume, not words. Stopping attacks does not mute voice. Use Roblox's mic control to mute, or Report Abuse for violations.",100)
  info(string.format("Third-person camera\n%s: roll · %.0fs arena cooldown\n%s: %.0fs moving sprint; %.0fs rest when empty. Refill starts after %.0fs without sprint.",touch and "DODGE" or "Q / DODGE",Config.DodgeCooldown,touch and "SPRINT" or "Shift / SPRINT",Config.SprintDuration,Config.SprintRecovery,Config.SprintRegenDelay),touch and 130 or 110)
  info(touch and "Tap TALK near a resident. Use the on-screen prompts for quest interactions. SHOP opens and closes the menu." or "T: talk · F: quest interactions · M: map · B: toggle menu",touch and 80 or 54)
  local micCard=card(58)
  button(micCard,"Recalibrate","RECALIBRATE MICROPHONE",UDim2.new(1,-24,0,38),UDim2.fromOffset(12,10),function()
   if sustainedControl then sustainedControl:SetArmed(false) end
   cancelCapture();setSprint(false);mic:Calibrate();modal.Visible=false
  end)
  info("Changed microphone or room noise? Recalibrate with a comfortable strong voice. "..(sustainedControl and "Beams stay OFF afterward; use BEAMS to turn attacks back on. Voice chat is unchanged." or "After calibration, hold BEAM and use a fresh live voice input."),80)
  local c=card(58);button(c,"Volume","CITY AUDIO: "..math.floor(data.settings.volume*100).."%",UDim2.new(1,-24,0,38),UDim2.fromOffset(12,10),function() action:FireServer("SetSettings",{volume=data.settings.volume>=.99 and 0 or math.min(1,data.settings.volume+.25)}) end)
  local audioCard=card(58);local audioButton
  local function audioLabel()return "BEAM SFX: "..attackAudio.level end
  audioButton=button(audioCard,"AttackAudio",audioLabel(),UDim2.new(1,-24,0,38),UDim2.fromOffset(12,10),function()
   attackAudio:SetLevel(attackAudio.level=="NORMAL" and "LOW" or attackAudio.level=="LOW" and "OFF" or "NORMAL");audioButton.Text=audioLabel()
  end)
  info("NORMAL boosts effects; LOW keeps the old mix; OFF mutes them. Starter beam has no SFX. Session only; mic and voice chat unchanged.",narrow and 100 or 68)
  local cueCard=card(58);local cueButton
  local function cueLabel()return not gameplayAudioSettings.Ready() and "GAMEPLAY SFX: PENDING UPLOAD" or "GAMEPLAY SFX: "..(gameplayAudio.enabled and "LOW" or "OFF") end
  cueButton=button(cueCard,"GameplayAudio",cueLabel(),UDim2.new(1,-24,0,38),UDim2.fromOffset(12,10),function()
   gameplayAudio:SetEnabled(not gameplayAudio.enabled);cueButton.Text=cueLabel()
  end)
  info("City audio controls surf and street music. Manage live voice with Roblox's microphone and listener controls.",54)
  local d=card(58);button(d,"ReducedFX","REDUCED EFFECTS: "..(data.settings.reducedShake and "ON" or "OFF"),UDim2.new(1,-24,0,38),UDim2.fromOffset(12,10),function() action:FireServer("SetSettings",{reducedShake=not data.settings.reducedShake}) end)
 end
 -- Restore only after AutomaticCanvasSize has measured the replacement cards.
 task.spawn(function()
  Run.Heartbeat:Wait()
  if revision~=renderRevision then return end
  content.CanvasPosition=Vector2.new(0,math.clamp(scroll.Y,0,math.max(0,content.AbsoluteCanvasSize.Y-content.AbsoluteWindowSize.Y)))
 end)
end
for i,name in ipairs({"Shop","Screams","Quests","Style","Map","Settings"}) do tabs[name]=button(modal,name,name=="Screams" and "BEAMS" or name:upper(),UDim2.fromOffset(126,34),UDim2.fromOffset(20+(i-1)*134,88),function() selected=name;render() end) end
local conversationNPC,conversationUntil
conversationPanel=frame(gui,"Conversation",UDim2.fromOffset(460,300),UDim2.fromScale(.5,.5));conversationPanel.AnchorPoint=Vector2.new(.5,.5);conversationPanel.Visible=false;conversationPanel.ZIndex=10
local conversationName=label(conversationPanel,"",UDim2.new(1,-80,0,36),UDim2.fromOffset(18,12),19,gold)
local conversationList=Instance.new("ScrollingFrame");conversationList.Size=UDim2.new(1,-36,1,-66);conversationList.Position=UDim2.fromOffset(18,54);conversationList.BackgroundTransparency=1;conversationList.BorderSizePixel=0;conversationList.ScrollBarThickness=4;conversationList.AutomaticCanvasSize=Enum.AutomaticSize.Y;conversationList.CanvasSize=UDim2.new();conversationList.Parent=conversationPanel
local conversationLayout=Instance.new("UIListLayout");conversationLayout.Padding=UDim.new(0,10);conversationLayout.SortOrder=Enum.SortOrder.LayoutOrder;conversationLayout.Parent=conversationList
closeConversation=function()
 if conversationPanel.Visible then action:FireServer("EndConversation") end
 conversationPanel.Visible=false;conversationNPC=nil
end
local function refreshConversation()
 if not conversationPanel.Visible then return end
 local character=p.Character
 local root=character and character:FindFirstChild("HumanoidRootPart")
 local humanoid=character and character:FindFirstChildOfClass("Humanoid")
 local npc=conversationNPC and conversationNPC.Parent and conversationNPC
 local npcRoot=npc and npc:FindFirstChild("HumanoidRootPart")
 local npcHumanoid=npc and npc:FindFirstChildOfClass("Humanoid")
 if modal.Visible or not root or not humanoid or humanoid.Health<=0 or humanoid.PlatformStand or not npcRoot or not npcHumanoid or npcHumanoid.Health<=0 or npcHumanoid.PlatformStand or npc:GetAttribute("ResidentActive")==false
  or (root.Position-npcRoot.Position).Magnitude>18 or os.clock()>=conversationUntil then closeConversation() end
end
button(conversationPanel,"Close","X",UDim2.fromOffset(38,34),UDim2.new(1,-50,0,12),closeConversation)
showConversation=function(info)
 cancelCapture();modal.Visible=false;if devPanel then devPanel.Visible=false end
 conversationNPC=info.npc;conversationUntil=os.clock()+20;conversationName.Text=info.name
 for _,child in ipairs(conversationList:GetChildren()) do if child:IsA("GuiObject") then child:Destroy() end end
 local order=0
 local function words(text,color)
  order+=1;local l=label(conversationList,text,UDim2.new(1,-10,0,0),UDim2.new(),14,color);l.AutomaticSize=Enum.AutomaticSize.Y;l.LayoutOrder=order;return l
 end
 local line=words(info.line,white)
 local function choice(text,callback)
  order+=1;local b=button(conversationList,"Choice",text,UDim2.new(1,-10,0,48),UDim2.new(),callback);b.TextWrapped=true;b.LayoutOrder=order;return b
 end
 choice("Tell me about this neighborhood",function() line.Text=info.hint end)
 for _,product in ipairs(info.products or {}) do
  words(product.description,muted)
  local b=choice(product.owned and (product.name.." · owned") or ("Buy "..product.name.." · "..product.price.." coins"),function()
   if not product.owned and conversationNPC then
    action:FireServer("VendorPurchase",{npc=conversationNPC:GetAttribute("NpcId"),product=product.id});closeConversation()
   end
  end)
  b.Active=not product.owned;b.AutoButtonColor=not product.owned
 end
 if data.activeQuest then words("Starting another task resets unfinished progress on your current task.",muted) end
 for _,q in ipairs(info.quests or {}) do
  words(q.description,muted)
  local b=choice(q.claimed and (q.name.." · completed") or ((q.complete and "Claim: " or "Accept: ")..q.name),function()
   if not q.claimed then action:FireServer(q.complete and "ClaimQuest" or "AcceptQuest",q.id);closeConversation() end
  end)
  b.Active=not q.claimed;b.AutoButtonColor=not q.claimed
 end
 choice("See you later",closeConversation)
 conversationList.CanvasPosition=Vector2.zero;conversationPanel.Visible=true
end
local function refreshQuestObjects()
 local world=workspace:FindFirstChild("ScreamSimulatorWorld")
 local objects=world and world:FindFirstChild("QuestObjects")
 if not objects then return end
 for _,object in objects:GetChildren() do
  if object:IsA("BasePart") and object:GetAttribute("QuestAction")=="Litter" then
   local hidden=data.collected and data.collected[object.Name]==true
   object.LocalTransparencyModifier=hidden and 1 or 0
   local prompt=object:FindFirstChildOfClass("ProximityPrompt")
   if prompt then prompt.Enabled=not hidden end
  end
 end
end
local function saveStatus()
 if data.testSession then return "TEST SESSION · progress is temporary" end
 if data.recoveryWarning then
  return (data.savingAvailable==false and "TEMPORARY · recovered save" or data.savingDelayed and "Save delayed · retrying" or "Recovered save").."\nRecent progress may be missing"
 end
 return data.savingDelayed and "Save delayed · retrying automatically" or data.savingAvailable==false and "Temporary progress · saving unavailable" or ""
end
local function progressLabel(compact)
 if compact then
  if data.recoveryWarning and not data.testSession then
   return (data.savingAvailable==false and "UNSAVED" or data.savingDelayed and "DELAYED" or "RECOVERED").." · progress may be missing"
  end
  if data.testSession or data.savingAvailable==false then return "TEMPORARY PROGRESS • not saved" end
  if data.savingDelayed then return "SAVE DELAYED • retrying" end
 end
 return data.level>=Config.MaxLevel and "MAX LEVEL" or data.xp.." / "..data.xpNext.." XP"
end
local trackedQuestText=""
local lastMilestone=nil
connectClient(remotes.State.OnClientEvent,function(nextData)
 observeVoiceEligibility(nextData)
 cueContext();gameplayAudio:ObserveLevel(nextData.level,nextData.testSession,os.clock())
 data=nextData
 local unclaimed=0
 for _,quest in ipairs(Config.Quests) do
  local progress=data.quests[quest.id]
  if progress and not progress.claimed and progress.progress>=quest.goal then unclaimed+=1 end
 end
 questsToggle.Text=unclaimed>0 and ("QUESTS "..unclaimed) or "QUESTS"
 questsToggle.TextColor3=unclaimed>0 and gold or white
 refreshQuestObjects();stats.Text="LEVEL "..data.level.."    •    "..data.coins.." coins";refreshHealth()
 xpText.Text=progressLabel(gui.AbsoluteSize.X<820);xf.Size=UDim2.fromScale(data.level>=Config.MaxLevel and 1 or data.xp/data.xpNext,1)
 zone.Text=data.inWarZone and "ARENA DISTRICT • PvP ON" or "SAFE CITY • PvP OFF";zone.TextColor3=data.inWarZone and Color3.fromRGB(255,140,139) or white
 testButton.Visible=data.devAccess==true
 local q=Config.GetQuest(data.activeQuest);local v=q and data.quests[q.id]
 tracked.Text=q and (q.name.."\n"..(data.questStep or "").."\n"..(v and v.progress or 0).."/"..q.goal..(data.questTime>0 and "  •  "..data.questTime.."s left" or "")) or ("Train: "..(data.training or "Rookie").." · west courtyard\nFighters "..((data.combatChallenges or {}).fighters or 0).."/3 · Quests for challenges")
 trackedQuestText=tracked.Text
 if data.savingAvailable==true and not data.savingDelayed then notifications:Remove("save") end
 local newMilestone=data.milestone and data.milestone~=lastMilestone
 if newMilestone then
  lastMilestone=data.milestone;notify(data.milestone)
 end
 if data.message and (not newMilestone or data.messageUrgent) then notify(data.message,data.messageUrgent,data.messageKey=="save" and "save" or nil) end
 if data.conversation then showConversation(data.conversation) end
 if modal.Visible then render() end
end)
connectClient(UIS.InputBegan,function(input,processed)
 if processed or GuiService.MenuIsOpen or UIS:GetFocusedTextBox() then return end
 local k=input.KeyCode
 if k==Enum.KeyCode.E then if sustainedControl then toggleVoice() else beginCapture("keyboard") end elseif k==Enum.KeyCode.Q then dodge() elseif k==Enum.KeyCode.B then toggle()
 elseif k==Enum.KeyCode.M then toggleTab("Map")
 elseif k==Enum.KeyCode.LeftShift then setSprint(true)
 elseif k==Enum.KeyCode.T then requestTalk() end
end)
connectClient(UIS.InputEnded,function(input)
 if input.KeyCode==Enum.KeyCode.E then releaseCapture("keyboard")
 elseif captureSource==input or (typeof(captureSource)=="Instance" and captureSource.UserInputType==Enum.UserInputType.MouseButton1 and input.UserInputType==Enum.UserInputType.MouseButton1) then releaseCapture(captureSource) end
 if input.KeyCode==Enum.KeyCode.LeftShift then setSprint(false) end
end)
connectClient(p.CharacterRemoving,function() hitFeedback:DiscardThrough(sustainedControl and sustainedControl.sequence or hitFeedback.sequence);setSprint(false);if sustainedControl then sustainedControl:SetArmed(false) end;cancelCapture();if closeConversation then closeConversation() end end)
connectClient(UIS.WindowFocused,function() windowFocused=true end)
local function suspendGameplay()
 if sustainedControl then sustainedControl:SetArmed(false) end
 setSprint(false);cancelCapture()
end
connectClient(UIS.WindowFocusReleased,function() windowFocused=false;suspendGameplay() end)
connectClient(GuiService.MenuOpened,suspendGameplay)
connectClient(p:GetAttributeChangedSignal("ProtectionEnds"),function() setSprint(false) end)
local function fxPart(position,color,size)
 local f=Instance.new("Part");f.Anchored=true;f.CanCollide=false;f.CanTouch=false;f.CanQuery=false;f.Material=Enum.Material.Neon;f.Color=color;f.Size=size;f.Position=position;f.Transparency=.3;f.Parent=workspace;Debris:AddItem(f,1.1);return f
end
local BeamVisuals=require(script.Parent:WaitForChild("BeamVisuals"))
script.Destroying:Connect(function() BeamVisuals.Clear() end)
local beamFrame=0
local sustainedBeams
if sustainedControl then
 sustainedBeams=require(script.Parent:WaitForChild("SustainedBeams")).new(BeamVisuals.Create,BeamVisuals.Update,BeamVisuals.Destroy)
 connectClient(p.CharacterRemoving,function() sustainedBeams:Clear() end)
 connectClient(p.CharacterRemoving,function() attackAudio:Clear() end)
 connectClient(Players.PlayerRemoving,function(leaving) sustainedBeams:Remove(leaving.UserId) end)
 connectClient(Players.PlayerRemoving,function(leaving) attackAudio:Remove(leaving.UserId) end)
 script.Destroying:Connect(function() sustainedBeams:Destroy() end)
end
connectClient(remotes.Effect.OnClientEvent,function(kind,pos,id,aura,direction,length,beamWidth,audioStyleId,attackLevel)
 if kind=="SustainedHit" then
  if hitFeedback:Accept(id,aura,os.clock()) then playGameplayCue("Hit") end
  return
 end
 if kind=="SustainedBeamEnd" then
  attackAudio:Stop(id,os.clock())
  if sustainedBeams then sustainedBeams:Remove(id) end
  return
 end
 if kind=="SustainedBeam" then
  if not sustainedBeams then return end
  local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
  if not Players:GetPlayerByUserId(id) or not root or (root.Position-pos).Magnitude>180 or length<.05 then
   sustainedBeams:Remove(id);attackAudio:Remove(id);return
  end
  sustainedBeams:Update(id,os.clock(),pos,direction,length,beamWidth,(typeof(aura)=="Color3" and aura or Config.Auras[aura] or gold),attackLevel or 1,data.settings.reducedShake)
  if (root.Position-pos).Magnitude<=attackAudioSettings.Range then
   local style=type(audioStyleId)=="string" and Config.GetSound(audioStyleId)
   attackAudio:Pulse(id,os.clock(),pos,id==p.UserId,style and style.level)
  else attackAudio:Remove(id) end
  return
 end
 local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart");if not root or (root.Position-pos).Magnitude>180 then return end
 if kind=="Break" then
  playGameplayCue("Break",pos)
  for i=1,6 do local chip=fxPart(pos,(typeof(id)=="Color3" and id or Config.Auras[id] or gold),Vector3.new(.5,.5,.5));Tween:Create(chip,TweenInfo.new(.45),{Position=pos+Vector3.new(math.cos(i)*3,2,math.sin(i)*3),Transparency=1}):Play() end;return
 end
 local chosenColor=kind=="Dodge" and id or aura
 local color=typeof(chosenColor)=="Color3" and chosenColor or Config.Auras[chosenColor] or gold
 if kind=="Dodge" then playGameplayCue("Dodge",pos);return end
 local s=Config.GetSound(id);if not s then return end
 -- Actual voice stays on Roblox proximity audio. Owner-selected SFX are separate.
 direction=direction or Vector3.new(0,0,-1);length=length or Config.VoiceCombat.Stats(data.level,1,false).range
 ScreamEffects.Render(s.effect,pos,direction,length,beamWidth or 4,color,data.settings.reducedShake,s.variant)
end)
local elapsed=0
local lastViewport,lastTouch
-- Visible modal buttons keep the pointer available while interacting with panels.
modal.Close.Modal=true;micPanel.Calibrate.Modal=true;conversationPanel.Close.Modal=true
testContent.XP.Modal=true
connectClient(Run.RenderStepped,function(dt)
 local notice=notifications:Step(dt,windowFocused and not GuiService.MenuIsOpen)
 if notice~=toast.Text then toast.Text=notice;toastWidth=0 end
 toast.Visible=notice~=""
 ShopUI.Tick()
 refreshHealth()
 local viewport=gui.AbsoluteSize
 local touch=UIS.TouchEnabled
 -- Keep the raised notification above the touch/keyboard action targets.
 toast.Position=UDim2.fromOffset(viewport.X*.5,math.min(viewport.Y*.72,viewport.Y-(touch and 203 or 110)))
 local layoutChanged=viewport~=lastViewport or touch~=lastTouch
 if layoutChanged then lastViewport=viewport;lastTouch=touch;toastWidth=0 end
 local notificationWidth=math.min(640,viewport.X-32)
 if notificationWidth~=toastWidth then
  toastWidth=notificationWidth;toast.TextSize=viewport.X<820 and 14 or 16
  local textHeight=TextService:GetTextSize(toast.Text,toast.TextSize,toast.Font,Vector2.new(notificationWidth,10000)).Y
  toast.Size=UDim2.fromOffset(notificationWidth,math.min(viewport.Y*.35,textHeight+12))
 end
 if layoutChanged then conversationPanel.Size=UDim2.fromOffset(math.min(460,viewport.X-24),math.min(340,viewport.Y-36)) end
 refreshConversation()
 saveNotice.Text=saveStatus()
 saveNotice.Visible=not modal.Visible and viewport.X>=820
 local progress=progressLabel(viewport.X<820)
 if xpText.Text~=progress then xpText.Text=progress end
 if layoutChanged then
 micScale.Scale=1
 local micWidth=math.min(430,viewport.X-24);local micNarrow=micWidth<400
 micPanel.Size=UDim2.fromOffset(micWidth,micNarrow and 320 or 260);micTitle.TextSize=micNarrow and 18 or 21
 local calibrate=micPanel.Calibrate;local retry=micPanel.Retry
 calibrate.Size=UDim2.fromOffset(micNarrow and micWidth-36 or 188,UIS.TouchEnabled and 44 or 36);retry.Size=calibrate.Size
 calibrate.Position=UDim2.fromOffset(18,micNarrow and 224 or 208);retry.Position=UDim2.fromOffset(micNarrow and 18 or 224,micNarrow and 270 or 208)
 end
 micPanel.Visible=not mic.ready and not modal.Visible and not devPanel.Visible
 local calibrationActive=mic.phase~=nil and mic.phaseStarted~=nil
 micStatus.Text=calibrationActive and string.format("%s\n%.1fs remaining",mic.status,math.max(0,2-(os.clock()-mic.phaseStarted))) or mic.status
 micPanel.Calibrate.Text=calibrationActive and "RESTART SETUP" or "CALIBRATE MIC"
 if reportedReady~=mic.ready or (data.micReady~=mic.ready and os.clock()>readyReportAt) then reportedReady=mic.ready;readyReportAt=os.clock()+1;action:FireServer("MicReady",mic.ready) end
 local serverNow=workspace:GetServerTimeNow()
 local protectionRemaining=math.max(0,(p:GetAttribute("ProtectionEnds") or 0)-serverNow)
 local rolling=serverNow<(p:GetAttribute("DodgeEnds") or 0)
 local knocked=serverNow<(p:GetAttribute("KnockdownEnds") or 0)
 local voiceCooldown,voiceActive
 local character=p.Character
 local humanoid=character and character:FindFirstChildOfClass("Humanoid")
 local alive=humanoid~=nil and humanoid.Health>0
 if sustainedControl then
  if data.voiceStatus=="denied" or data.voiceStatus=="unavailable" then voiceAccessInterrupted=true end
  sustainedControl:ObserveAvailability(alive and mic.ready and data.voiceEligible==true,windowFocused and not GuiService.MenuIsOpen and not voiceAccessInterrupted)
  voiceCooldown=math.max(0,(p:GetAttribute("SustainedReadyAt") or 0)-workspace:GetServerTimeNow())
  voiceActive=p:GetAttribute("SustainedActive")==true
  sustainedControl:Step(dt,os.clock(),mic.power,alive and windowFocused and not beamBlocked(),
   voiceCooldown<=0 and data.micReady==true,voiceActive,p:GetAttribute("SustainedSequence"))
 end
 if captureSource and beamBlocked() then cancelCapture() end
 if captureSource and mic.captureStarted and os.clock()-mic.captureStarted>Config.VoiceCombat.CaptureExpiry then
  cancelCapture();notify("Capture expired. Hold attack again and use a fresh live voice input.",true,"capture")
 end
 if sprinting then setSprint(true) end
 local gameplayVisible=mic.ready and not GuiService.MenuIsOpen and not modal.Visible and not devPanel.Visible and not conversationPanel.Visible
 local showTouchControls=originalTouchControls and not GuiService.MenuIsOpen and not modal.Visible and not devPanel.Visible and not conversationPanel.Visible and not micPanel.Visible
 if GuiService.TouchControlsEnabled~=showTouchControls then GuiService.TouchControlsEnabled=showTouchControls end
 local eligibilityHint=voiceEligibilityHint(true)
 local guide=sustainedControl and not eligibilityHint and FirstBeamGuide.Text(data,sustainedControl.armed,voiceCooldown or 0,voiceActive,touch)
 tracked.Text=guide or trackedQuestText
 local confirmed=hitFeedback:Read(os.clock())
 hitText.Visible=gameplayVisible and confirmed~=nil
 if confirmed then hitText.Text=string.format("%d DAMAGE",confirmed) end
 meter.Visible=gameplayVisible;reticle.Visible=UIS.TouchEnabled and gameplayVisible
 local power=captureSource and mic:CapturePower() or mic.power;meterFill.Size=UDim2.fromScale(power,1)
 local range=Config.VoiceCombat.Stats(data.level,power,data.amplifierEquipped).range
 local captureRemaining=mic.captureStarted and math.max(0,Config.VoiceCombat.MaxCapture-(os.clock()-mic.captureStarted)) or 0
 local captureHint=captureSource and (captureRemaining>0 and string.format("Speak now • %.1fs left",captureRemaining) or "Window ended • release to fire") or "Hold attack before speaking"
 if sustainedControl then
  captureHint=not alive and "Respawning • beams OFF"
   or not windowFocused and "Window inactive • attack paused"
   or protectionRemaining>0 and string.format("Spawn protection • %.1fs",protectionRemaining)
   or (knocked or humanoid.PlatformStand) and "Recovering • attack unavailable"
   or rolling and "Rolling • attack cancelled"
   or UIS:GetFocusedTextBox()~=nil and "Typing • attack paused"
   or data.micReady~=true and "Connecting microphone…"
   or not sustainedControl.armed and (touch and "Beams OFF • tap to turn on" or "Beams OFF • E to turn on")
   or voiceCooldown>0 and string.format("Cooldown • %.1fs",voiceCooldown)
   or sustainedControl.attack and (voiceActive and string.format("Attacking • %.1fs left",math.max(0,(p:GetAttribute("SustainedEndsAt") or 0)-serverNow)) or "Starting attack…")
   or os.clock()<(sustainedControl.unconfirmedUntil or 0) and "Not confirmed • quiet, then retry"
   or sustainedControl.gate.needsQuiet and "Armed • quiet before speaking"
   or sustainedControl.gate.onset>0 and "Voice detected • keep speaking"
   or "ON · normal speech can attack"
  meterFill.BackgroundColor3=voiceActive and Color3.fromRGB(104,222,157)
   or (not sustainedControl.armed or voiceCooldown>0 or blocked()) and muted or gold
 end
 meterText.Text=string.format("%s %d%% • up to %.0f studs\n%s",captureSource and "BEAM POWER" or "LIVE MIC",math.floor(power*100),range,captureHint)
 if eligibilityHint then
  meterText.Text=eligibilityHint
 elseif sustainedControl and not sustainedControl.armed then
  meterText.Text="BEAMS OFF · TALK FREELY\nVoice chat is unchanged"
 end
 if layoutChanged then
 local short=viewport.Y<550
 menuScale.Scale=1
 local width=math.min(720,viewport.X-24)
 modal.Size=UDim2.fromOffset(width,math.min(620,viewport.Y-76));modal.Position=UDim2.new(.5,0,0,64)
 devPanel.Size=UDim2.fromOffset(230,math.min(330,viewport.Y-76));devPanel.Position=UDim2.new(1,-244,0,64)
 title.TextSize=width<620 and 20 or 23
 subtitle.Visible=not short;subtitle.Size=UDim2.new(1,-44,0,width<620 and 42 or 25)
 local tabY=short and 54 or width<620 and 102 or 88
 local columns=width<620 and 3 or 6;local rows=math.ceil(6/columns)
 local tabWidth=(width-40-(columns-1)*6)/columns
 for i,name in ipairs({"Shop","Screams","Quests","Style","Map","Settings"}) do
  local b=tabs[name];b.Size=UDim2.fromOffset(tabWidth,44);b.Position=UDim2.fromOffset(20+((i-1)%columns)*(tabWidth+6),tabY+math.floor((i-1)/columns)*50);b.TextSize=width<620 and 12 or 14
 end
 content.Position=UDim2.fromOffset(20,tabY+rows*50+4);content.Size=UDim2.new(1,-40,1,-(tabY+rows*50+18))
 if width~=lastLayoutWidth then lastLayoutWidth=width;if modal.Visible then render() end end
 -- Keep desktop controls compact; smaller displays retain readable button text.
 local tight=viewport.X<380
 shop.Size=UDim2.fromOffset(tight and 90 or 125,touch and 44 or 36);shop.Text=(tight or touch) and "SHOP" or "SHOP [B]"
 questsToggle.Size=UDim2.fromOffset(tight and 78 or 95,touch and 44 or 36);questsToggle.Position=UDim2.fromOffset(tight and 98 or 134,0)
 testButton.Size=UDim2.fromOffset(tight and 90 or 112,touch and 44 or 32);testButton.Position=UDim2.new(1,tight and -104 or -126,0,14)
 local miniLayout=CityMap.MiniLayout(viewport,touch)
 miniMapButton.Size=UDim2.fromOffset(miniLayout.width,miniLayout.height);miniMapButton.Position=UDim2.new(1,-miniLayout.width-14,0,14)
 miniMapHolder.Visible=miniLayout.expanded;miniMapAvailable=miniLayout.available
 hud.Position=(touch or viewport.X<820) and UDim2.fromOffset(14,64) or UDim2.new(0,14,1,-108)
 controls.Position=UDim2.new(1,-274,1,touch and -195 or -102)
 talkButton.Position=UDim2.new(.5,-60,1,touch and -249 or -108)
 talkButton.Size=UDim2.fromOffset(120,touch and 44 or 34)
 controls.Size=UDim2.fromOffset(260,touch and 96 or 88)
 tracked.Position=UDim2.fromOffset(16,(touch or viewport.X<820) and 160 or 64)
 sprintButton.TextSize=touch and 12 or 14;sprintButton.Size=UDim2.fromOffset(164,touch and 44 or 32)
 end
 hud.Visible=gameplayVisible;controls.Visible=gameplayVisible
 -- Keep the fight readable without hiding a running quest deadline.
 local combatQuest=data.activeQuest=="arena" or data.activeQuest=="dodge" or data.activeQuest=="crowd" or data.activeQuest=="practice_beams" or data.activeQuest=="arena_assist"
 local showQuest=not data.inWarZone or combatQuest or (data.questTime or 0)>0
 tracked.Visible=gameplayVisible and tracked.Text~="" and showQuest;zone.Visible=viewport.X>740 and gameplayVisible
 local now=workspace:GetServerTimeNow();local protected=math.max(0,(p:GetAttribute("ProtectionEnds") or 0)-now)
 castButton.Text=protected>0 and "PROTECTED "..math.ceil(protected).."s" or os.clock()<nextCast and string.format("BEAM %.1fs",nextCast-os.clock()) or captureSource and (captureRemaining>0 and "SPEAK • RELEASE" or "RELEASE TO FIRE") or "HOLD BEAM [E]"
 if sustainedControl then
  -- Keep the toggle state visible even during protection/cooldown; those gates
  -- still control attacks, but never disguise an OFF choice as a mic mute.
  castButton.Text=screamToggleLabel(sustainedControl.armed,touch)
  castButton.TextSize=12
 end
 -- Keep attack duration/cooldown distinct from live microphone loudness.
 voiceTimeTrack.Visible=sustainedControl~=nil and alive and protected<=0 and (voiceActive or (voiceCooldown or 0)>0)
 if voiceTimeTrack.Visible then
  local fraction
  if voiceActive then
   fraction=math.max(0,(p:GetAttribute("SustainedEndsAt") or 0)-serverNow)/sustainedRules.MaxDuration
   voiceTimeFill.BackgroundColor3=Color3.fromRGB(104,222,157)
  else
   fraction=1-voiceCooldown/sustainedRules.Cooldown
   voiceTimeFill.BackgroundColor3=muted
  end
  voiceTimeFill.Size=UDim2.fromScale(math.clamp(fraction,0,1),1)
 end
 castButton.BackgroundColor3=(sustainedControl and not sustainedControl.armed or protected>0) and muted or gold
 local cd=math.max(0,(p:GetAttribute("DodgeReady") or 0)-now);dodgeButton.Text=cd>0 and string.format("DODGE %.1fs",cd) or (touch and "DODGE" or "DODGE [Q]")
 local rest=p:GetAttribute("SprintCooldown") or 0;sprintButton.Text=rest>0 and string.format("REST %.1fs",rest) or string.format("SPRINT %.1fs",p:GetAttribute("SprintCharge") or 10)..(touch and "" or " [SHIFT]")
 aimInfo.Visible=gameplayVisible
 if sustainedBeams then
  local now=os.clock();sustainedBeams:Expire(now)
  beamFrame+=dt
  if beamFrame>=1/30 then
   beamFrame=0
   local camera=workspace.CurrentCamera
   if camera then
    for _,entry in pairs(sustainedBeams.entries) do BeamVisuals.Animate(entry.visual,now,camera.CFrame.Position,data.settings.reducedShake) end
   end
  end
 end
 cueContext();gameplayAudio:Step(os.clock(),dt)
 -- Audio consumes frame dt; keep ducking/calibration/fades outside the slow HUD gate.
 attackAudio:Step(os.clock(),dt,mic.ready and mic.power>.12,mic.phase~=nil)
 elapsed+=dt;if elapsed<.15 then return end;elapsed=0
 aimInfo.Text=""
 if aimInfo.Visible then
  local _,hit=aimRay();local object=hit and hit.Instance
  while object and object~=workspace and not object:GetAttribute("RequiredLevel")
   and not (object:IsA("Model") and (Players:GetPlayerFromCharacter(object) or object:GetAttribute("NpcId"))) do object=object.Parent end
  local targetPlayer=object and object~=workspace and object:IsA("Model") and Players:GetPlayerFromCharacter(object)
  if targetPlayer and targetPlayer~=p then
   local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
   local targetRoot=object:FindFirstChild("HumanoidRootPart");local humanoid=object:FindFirstChildOfClass("Humanoid")
   if root and targetRoot and humanoid then
    local canFight=Config.InArena(root.Position) and Config.InArena(targetRoot.Position)
    local far=(targetRoot.Position-root.Position).Magnitude>Config.VoiceCombat.Stats(data.level,1,data.amplifierEquipped).maxRange+2
    local currentFar=(targetRoot.Position-root.Position).Magnitude>range+2
    local text,available=playerTargetInfo(targetPlayer,humanoid,canFight,far,workspace:GetServerTimeNow(),currentFar,canFight and not far and targetCovered(root,targetRoot,object))
    aimInfo.Text=text or "";aimInfo.TextColor3=available and gold or muted
   end
  elseif object and object~=workspace and object:IsA("Model") and object:GetAttribute("NpcId") then
   local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
   local npcRoot=object:FindFirstChild("HumanoidRootPart")
   if root and npcRoot then
    local distance=(npcRoot.Position-root.Position).Magnitude
    local far=distance>Config.VoiceCombat.Stats(data.level,1,data.amplifierEquipped).maxRange+2
    local text,available=residentTargetInfo(object,object:FindFirstChildOfClass("Humanoid"),far,distance>range+2,not far and targetCovered(root,npcRoot,object))
    aimInfo.Text=text or "";aimInfo.TextColor3=available and gold or muted
   end
  elseif object and object~=workspace and object:GetAttribute("RequiredLevel") then
   local required=object:GetAttribute("RequiredLevel");local hp=object:GetAttribute("ObjectHealth") or 0
   local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
   local rangeLimit=Config.VoiceCombat.Stats(data.level,1,data.amplifierEquipped).maxRange
   local far=root and (hit.Position-root.Position).Magnitude>rangeLimit+2
   local currentFar=root and (hit.Position-root.Position).Magnitude>range+2
   local kind=object:GetAttribute("ObjectName") or object:GetAttribute("DestructibleType") or object.Name
   aimInfo.Text=string.format("%s · LEVEL %d\n%s",kind,required,data.level<required and "LOCKED" or far and "OUT OF MAX RANGE" or currentFar and "BEYOND CURRENT RANGE" or string.format("%d / %d durability",hp,object:GetAttribute("ObjectMaxHealth") or hp))
   local repairSeconds=math.max(0,math.ceil((object:GetAttribute("RepairAt") or 0)-workspace:GetServerTimeNow()))
   if hp<(object:GetAttribute("ObjectMaxHealth") or hp) then
    if object:GetAttribute("RepairBlocked")==true then
     aimInfo.Text..="\nRepair waiting · clear the area"
    elseif repairSeconds>0 then
     aimInfo.Text..=string.format("\nRepair in %d:%02d",math.floor(repairSeconds/60),repairSeconds%60)
    end
   end
   aimInfo.TextColor3=(data.level<required or far or currentFar) and muted or gold
  end
 end
 local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
 if os.clock()>=nextResidentUi then
  nextResidentUi=os.clock()+.1
  talkTarget=refreshResidentLabels(root,workspace.CurrentCamera,game:GetService("CollectionService"):GetTagged("CityResident"))
 end
 if mapDot then CityMap.update(mapDot,root) end
 local miniVisible=miniMapAvailable and gameplayVisible and windowFocused and not toast.Visible and data.devAccess~=true
 miniMapButton.Visible=miniVisible
 CityMap.MiniUpdate(miniMapView,root,os.clock(),miniVisible and miniMapHolder.Visible)
 talkButton.Text=touch and "TALK" or "TALK [T]"
 talkButton.Visible=talkTarget~=nil and gameplayVisible
end)
action:FireServer("Sync")

-- JumpRequest supports the built-in keyboard, controller and touch jump controls.
connectClient(UIS.JumpRequest,function()
 local character=p.Character;local h=character and character:FindFirstChildOfClass("Humanoid")
 if h and h.FloorMaterial==Enum.Material.Air and data.movementPass and not data.inWarZone and not blocked() then action:FireServer("ExtraJump") end
end)
