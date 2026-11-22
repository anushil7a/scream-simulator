-- This owner covers only this Client's resources; terminal cleanup is reentrant.
local clientConnections={}
local clientCleanups={}
local clientDestroyed=false
local function attemptClientCleanup(callback)
 local ok=pcall(callback)
 if not ok then warn("ScreamSimulator Client cleanup failed") end
end
local function retireClient()
 if clientDestroyed then return end
 clientDestroyed=true
 for _,connection in ipairs(clientConnections) do attemptClientCleanup(function() connection:Disconnect() end) end
 table.clear(clientConnections)
 for i=#clientCleanups,1,-1 do attemptClientCleanup(clientCleanups[i]) end
 table.clear(clientCleanups)
end
local function ownClient(cleanup)
 if clientDestroyed then attemptClientCleanup(cleanup) else table.insert(clientCleanups,cleanup) end
end
local function clientCheckpoint()
 if not clientDestroyed and not script:IsDescendantOf(game) then retireClient() end
 return not clientDestroyed
end
table.insert(clientConnections,script.Destroying:Connect(retireClient))
local function loadClientDependency(parent,name,direct)
 if not clientCheckpoint() then return end
 local dependency
 if direct then dependency=parent[name] else dependency=parent:WaitForChild(name) end
 if not clientCheckpoint() then return end
 local value=require(dependency)
 if not clientCheckpoint() then return end
 return value
end
if not clientCheckpoint() then return end
local CityMap=loadClientDependency(script.Parent,"CityMap");if not clientCheckpoint() then return end
local DodgeVisuals=loadClientDependency(script.Parent,"DodgeVisuals");if not clientCheckpoint() then return end
ownClient(function() DodgeVisuals.Destroy() end)
local Players=game:GetService("Players")
local RS=game:GetService("ReplicatedStorage")
local UIS=game:GetService("UserInputService")
local Run=game:GetService("RunService")
local Tween=game:GetService("TweenService")
local Debris=game:GetService("Debris")
local TextService=game:GetService("TextService")
local GuiService=game:GetService("GuiService")
local function connectClient(signal,callback)
 if clientDestroyed then return end
 local connection=signal:Connect(function(...)
  if not clientDestroyed then callback(...) end
 end)
 table.insert(clientConnections,connection)
 return connection
end
local originalTouchControls=GuiService.TouchControlsEnabled
local lastTouchControls
ownClient(function()
 if lastTouchControls~=nil and GuiService.TouchControlsEnabled==lastTouchControls then GuiService.TouchControlsEnabled=originalTouchControls end
end)
local p=Players.LocalPlayer
local originalCameraMode=p.CameraMode
local originalMinZoom,originalMaxZoom=p.CameraMinZoomDistance,p.CameraMaxZoomDistance
local lastCameraMode,lastMinZoom,lastMaxZoom
ownClient(function()
 if lastCameraMode~=nil and p.CameraMode==lastCameraMode then p.CameraMode=originalCameraMode end
 if lastMinZoom~=nil and p.CameraMinZoomDistance==lastMinZoom then p.CameraMinZoomDistance=originalMinZoom end
 if lastMaxZoom~=nil and p.CameraMaxZoomDistance==lastMaxZoom then p.CameraMaxZoomDistance=originalMaxZoom end
end)
-- Keep wheel/pinch zoom outside first person on desktop and touch.
local function applyThirdPerson()
 if clientDestroyed then return end
 lastMaxZoom=math.max(originalMaxZoom,6);p.CameraMaxZoomDistance=lastMaxZoom
 lastMinZoom=math.max(originalMinZoom,6);p.CameraMinZoomDistance=lastMinZoom
 lastCameraMode=Enum.CameraMode.Classic;p.CameraMode=lastCameraMode
end
applyThirdPerson()
connectClient(p.CharacterAdded,applyThirdPerson)
local shared=RS:WaitForChild("Shared");if not clientCheckpoint() then return end
local Config=loadClientDependency(shared,"Config");if not clientCheckpoint() then return end
local InteractionRules=loadClientDependency(RS.Shared,"InteractionRules");if not clientCheckpoint() then return end
local mic=loadClientDependency(script.Parent,"Microphone");if not clientCheckpoint() then return end
mic=mic.new()
ownClient(function() mic:Destroy() end);if not clientCheckpoint() then return end
local attackAudio=loadClientDependency(script.Parent,"AttackAudio");if not clientCheckpoint() then return end
attackAudio=attackAudio.new()
ownClient(function() attackAudio:Destroy() end);if not clientCheckpoint() then return end
local attackAudioSettings=loadClientDependency(RS.Shared,"AttackAudioConfig",true);if not clientCheckpoint() then return end
local gameplayAudio=loadClientDependency(script.Parent,"GameplayAudio");if not clientCheckpoint() then return end
gameplayAudio=gameplayAudio.new()
ownClient(function() gameplayAudio:Destroy() end);if not clientCheckpoint() then return end
local gameplayAudioSettings=loadClientDependency(RS.Shared,"GameplayAudioConfig",true);if not clientCheckpoint() then return end

connectClient(p.CharacterRemoving,function() gameplayAudio:Clear() end)
local function cueContext()
 local enabled=gameplayAudio.enabled==true
 local voice=not mic.ready or mic.power>.12 -- unknown microphone state uses the conservative duck
 local suppressed=mic.phase~=nil -- quiet/voice calibration; spectators without a mic can hear
 if gameplayAudio.bossEnabled~=enabled then gameplayAudio.bossEnabled=enabled;p:SetAttribute("BossAudioEnabled",enabled) end
 if gameplayAudio.bossVoice~=voice then gameplayAudio.bossVoice=voice;p:SetAttribute("BossAudioVoiceActive",voice) end
 if gameplayAudio.bossSuppressed~=suppressed then gameplayAudio.bossSuppressed=suppressed;p:SetAttribute("BossAudioSuppressed",suppressed) end
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


local ShopUI=loadClientDependency(script.Parent,"ShopUI");if not clientCheckpoint() then return end
local shopUsed=false
local function clearShop()
 if shopUsed then ShopUI.Clear() end
end
ownClient(clearShop)
local ScreamEffects=loadClientDependency(script.Parent,"ScreamEffects");if not clientCheckpoint() then return end
local screamEffectsUsed=false
ownClient(function() if screamEffectsUsed then ScreamEffects.Clear() end end)
local remotes=RS:WaitForChild("ScreamRemotes");if not clientCheckpoint() then return end
local action=remotes:WaitForChild("Action");if not clientCheckpoint() then return end
-- Required channels can replicate separately from the folder.
remotes:WaitForChild("State");if not clientCheckpoint() then return end
remotes:WaitForChild("Effect");if not clientCheckpoint() then return end
local playerGui=p:WaitForChild("PlayerGui");if not clientCheckpoint() then return end
local gui=Instance.new("ScreenGui");ownClient(function() gui:Destroy() end);if not clientCheckpoint() then return end
gui.Name="ScreamUI";gui.ResetOnSpawn=false;gui.ZIndexBehavior=Enum.ZIndexBehavior.Sibling;gui.Parent=playerGui
local dark=Color3.fromRGB(17,25,29);local panel=Color3.fromRGB(35,47,52);local gold=Color3.fromRGB(235,190,105);local white=Color3.fromRGB(246,241,226);local muted=Color3.fromRGB(177,192,193)
local data={level=1,xp=0,xpNext=Config.XPToNext(1),coins=0,health=100,sound="TinyAah",aura="Gold",quests={},settings={volume=.55,reducedShake=false}}
-- Match the aim GUI's viewport coordinates without moving the camera or covering HUD.
local beamFeedbackGui=Instance.new("ScreenGui");ownClient(function() beamFeedbackGui:Destroy() end);if not clientCheckpoint() then return end
beamFeedbackGui.Name="BeamFeedback";beamFeedbackGui.ResetOnSpawn=false
beamFeedbackGui.ScreenInsets=Enum.ScreenInsets.None;beamFeedbackGui.DisplayOrder=-1;beamFeedbackGui.ZIndexBehavior=Enum.ZIndexBehavior.Sibling;beamFeedbackGui.Parent=p.PlayerGui
local beamScreenFeedback=loadClientDependency(script.Parent,"BeamScreenFeedback");if not clientCheckpoint() then return end
beamScreenFeedback=beamScreenFeedback.new(beamFeedbackGui)
ownClient(function() beamScreenFeedback:Destroy() end);if not clientCheckpoint() then return end

connectClient(p.CharacterRemoving,function() beamScreenFeedback:Clear() end)
connectClient(UIS.WindowFocusReleased,function() beamScreenFeedback:Clear() end)
connectClient(GuiService.MenuOpened,function() beamScreenFeedback:Clear() end)
-- Fail quiet if the platform comfort preference cannot be read.
local platformReducedMotion=true
local function refreshScreenComfort()
 local ok,value=pcall(function() return GuiService.ReducedMotionEnabled end)
 platformReducedMotion=not ok or value==true
 if platformReducedMotion then beamScreenFeedback:Clear() end
end
refreshScreenComfort()
do
 local comfortOk,comfortSignal=pcall(function() return GuiService:GetPropertyChangedSignal("ReducedMotionEnabled") end)
 if comfortOk then connectClient(comfortSignal,refreshScreenComfort) end
end
local function frame(parent,name,size,pos,color)
 local f=Instance.new("Frame");f.Name=name;f.Size=size;f.Position=pos;f.BackgroundColor3=color or dark;f.BorderSizePixel=0;f.Parent=parent
 local c=Instance.new("UICorner");c.CornerRadius=UDim.new(0,10);c.Parent=f;return f
end
local function label(parent,text,size,pos,fontSize,color)
 local l=Instance.new("TextLabel");l.Size=size;l.Position=pos;l.BackgroundTransparency=1;l.Text=text;l.TextSize=fontSize or 15;l.Font=Enum.Font.GothamMedium;l.TextColor3=color or white;l.TextXAlignment=Enum.TextXAlignment.Left;l.TextWrapped=true;l.Parent=parent;return l
end
local function button(parent,name,text,size,pos,callback,color)
 local b=Instance.new("TextButton");b.Name=name;b.Size=size;b.Position=pos;b.BackgroundColor3=color or panel;b.TextColor3=white;b.Text=text;b.TextSize=14;b.Font=Enum.Font.GothamBold;b.AutoButtonColor=true;b.BorderSizePixel=0;b.Parent=parent
 local c=Instance.new("UICorner");c.CornerRadius=UDim.new(0,8);c.Parent=b;b.Activated:Connect(function(...) if not clientDestroyed then callback(...) end end);return b
end
-- Presentation only: no subscriptions, assets, input handlers or independent lifetime.
local academy={}
function academy.surface(object,accent)
 local stroke=Instance.new("UIStroke");stroke.Name="AcademyEdge";stroke.ApplyStrokeMode=Enum.ApplyStrokeMode.Border;stroke.Color=accent or Color3.fromRGB(89,110,114);stroke.Transparency=.45;stroke.Thickness=1;stroke.Parent=object
 local shade=Instance.new("UIGradient");shade.Name="AcademyDepth";shade.Color=ColorSequence.new(Color3.new(1,1,1),Color3.fromRGB(183,196,201));shade.Rotation=90;shade.Parent=object
end
function academy.mark(parent,kind,pos,size,color)
 local icon=Instance.new("Frame");icon.Name="AcademyIcon_"..kind;icon.BackgroundTransparency=1;icon.Position=pos;icon.Size=UDim2.fromOffset(size,size);icon.Active=false;icon.Selectable=false;icon.Interactable=false;icon.Parent=parent
 local function bar(x,y,w,h)
  local f=Instance.new("Frame");f.Name="Glyph";f.BorderSizePixel=0;f.BackgroundColor3=color;f.Position=UDim2.fromScale(x,y);f.Size=UDim2.fromScale(w,h);f.Active=false;f.Selectable=false;f.Interactable=false;f.Parent=icon
  local corner=Instance.new("UICorner");corner.CornerRadius=UDim.new(0,2);corner.Parent=f
 end
 if kind=="voice" then
  bar(.08,.36,.12,.28);bar(.30,.18,.12,.64);bar(.52,.06,.12,.88);bar(.74,.26,.12,.48)
 elseif kind=="health" then bar(.36,.1,.28,.8);bar(.1,.36,.8,.28)
 elseif kind=="progress" then bar(.10,.65,.18,.25);bar(.40,.4,.18,.5);bar(.70,.1,.18,.8)
 end
 return icon
end
-- Original, static menu glyphs. Labels remain the accessible action identity.
academy.tabIcons={}
function academy.tabIcon(parent,kind)
 local icon=Instance.new("Frame");icon.Name="MenuIcon_"..kind;icon.Size=UDim2.fromOffset(20,20)
 icon.ZIndex=parent.ZIndex+1;icon.BackgroundTransparency=1;icon.Visible=false;icon.Active=false;icon.Selectable=false;icon.Interactable=false;icon.Parent=parent
 local ink=Color3.fromRGB(28,36,64);local light=Color3.fromRGB(255,242,199)
 local warm=Color3.fromRGB(240,190,91);local cool=Color3.fromRGB(143,191,202)
 local function shape(name,x,y,w,h,color,rotation,round)
  local f=Instance.new("Frame");f.Name=name;f.Position=UDim2.fromOffset(x,y);f.Size=UDim2.fromOffset(w,h)
  f.ZIndex=icon.ZIndex;f.BorderSizePixel=0;f.BackgroundColor3=color;f.Rotation=rotation or 0
  f.Active=false;f.Selectable=false;f.Interactable=false;f.Parent=icon
  if round then local c=Instance.new("UICorner");c.CornerRadius=UDim.new(0,round);c.Parent=f end
  return f
 end
 if kind=="Shop" then
  shape("StackInk",2,8,16,10,ink,0,4);shape("StackShade",4,10,12,6,warm,0,3)
  shape("CoinInk",2,2,16,11,ink,0,5);shape("CoinFace",4,4,12,7,light,0,4);shape("CoinFacet",5,8,10,2,warm,0,1)
 elseif kind=="Screams" then
  shape("BeamInk",2,7,16,7,ink,-18,2);shape("BeamFace",3,8,14,4,warm,-18,1)
  shape("EmitterInk",2,5,6,11,ink,-18,2);shape("EmitterFace",3,6,3,8,cool,-18,1)
  shape("Core",7,8,10,2,light,-18,1)
 elseif kind=="Quests" then
  shape("PageInk",3,1,14,18,ink,0,3);shape("PageFace",5,3,10,14,light,0,2)
  shape("CheckShort",6,7,3,2,cool,40);shape("CheckLong",8,6,6,2,cool,-42)
  shape("LineOne",7,12,6,2,warm);shape("LineTwo",7,15,4,1,warm)
 elseif kind=="Style" then
  shape("BackInk",2,3,12,14,ink,-18,3);shape("BackFace",4,5,8,10,cool,-18,2)
  shape("FrontInk",6,3,12,14,ink,15,3);shape("FrontFace",8,5,8,10,warm,15,2);shape("Shine",9,6,5,2,light,15,1)
 elseif kind=="Map" then
  shape("MapInk",1,3,18,15,ink,0,2);shape("WestFold",3,5,4,10,light)
  shape("MiddleFold",7,4,6,12,cool);shape("EastFold",13,5,4,10,light)
  shape("Route",5,9,10,2,warm,-18);shape("Destination",13,7,3,3,ink,0,1)
 elseif kind=="Settings" then
  for i=0,2 do
   shape("Rail"..i,2,3+i*6,16,3,ink,0,1)
   local x=({5,11,7})[i+1]
   shape("KnobInk"..i,x,1+i*6,5,7,ink,0,2)
   shape("KnobFace"..i,x+1,2+i*6,3,4,i==1 and cool or light,0,1)
  end
 end
 local padding=Instance.new("UIPadding");padding.Name="MenuTextInset";padding.Parent=parent
 return icon,padding
end
function academy.layoutTab(button,icon,padding,width)
 local measured=TextService:GetTextSize(button.Text,button.TextSize,button.Font,Vector2.new(1000,1000)).X
 local total=20+6+math.ceil(measured)
 local fits=width>=total+16
 icon.Visible=fits
 padding.PaddingRight=UDim.new(0,fits and (width-total)/2 or 0)
 button.TextXAlignment=fits and Enum.TextXAlignment.Right or Enum.TextXAlignment.Center
 icon.Position=UDim2.new(0,(width-total)/2,0.5,-10)
end
local top=frame(gui,"Navigation",UDim2.fromOffset(250,40),UDim2.fromOffset(14,12));top.BackgroundTransparency=1
local modal=frame(gui,"Menu",UDim2.fromOffset(720,520),UDim2.fromScale(.5,.5));modal.AnchorPoint=Vector2.new(.5,0);modal.ZIndex=10;modal.Visible=false
do
 local menuEdge=Instance.new("UIStroke");menuEdge.Color=gold;menuEdge.Transparency=.5;menuEdge.Parent=modal
 modal.BackgroundColor3=Color3.new(1,1,1)
 local menuGlow=Instance.new("UIGradient");menuGlow.Color=ColorSequence.new(Color3.fromRGB(46,61,65),dark);menuGlow.Rotation=80;menuGlow.Parent=modal
 frame(modal,"SignalStripe",UDim2.new(1,-44,0,2),UDim2.fromOffset(22,8),gold)
end
local menuScale=Instance.new("UIScale");menuScale.Parent=modal
local title=label(modal,"BEAM COLLECTION",UDim2.new(1,-85,0,36),UDim2.fromOffset(22,15),23,gold)
local subtitle=label(modal,"Train for XP. Unlock a new beam style every ten levels.",UDim2.new(1,-44,0,25),UDim2.fromOffset(22,52),14,muted)
local renderedMenuKey,renderedTab
local renderRevision=0
local function closeMenu()
 modal.Visible=false
 academy.menuQuestFocus=nil
 if academy.refreshTestLauncher then academy.refreshTestLauncher() end
 clearShop()
 -- Retain the previous tab/scroll position, but rebuild its subscriptions on reopen.
 renderedMenuKey=nil;renderRevision+=1
end
button(modal,"Close","X",UDim2.fromOffset(44,44),UDim2.new(1,-56,0,10),function() closeMenu() end)
local content=Instance.new("ScrollingFrame");content.Name="Content";content.Size=UDim2.new(1,-40,1,-148);content.Position=UDim2.fromOffset(20,132);content.BackgroundTransparency=1;content.BorderSizePixel=0;content.ScrollBarThickness=4;content.AutomaticCanvasSize=Enum.AutomaticSize.Y;content.CanvasSize=UDim2.new();content.Parent=modal
do local list=Instance.new("UIListLayout");list.Padding=UDim.new(0,10);list.SortOrder=Enum.SortOrder.LayoutOrder;list.Parent=content end
local selected="Style";local render;local tabs={};local mapDot;local devPanel;local narrow=false;local lastLayoutWidth=0
local conversationPanel,showConversation,closeConversation
local observedMicInterruption=0
function academy.gearUpgrade(data)
 local highestOwned
 for index,item in ipairs(Config.Gear.Items) do
  if Config.Gear.Owned(data,item.id) then highestOwned=index end
 end
 return highestOwned and Config.Gear.Items[highestOwned+1]
end
local function toggleTab(name,resetScroll,focusQuest)
 local opening=not modal.Visible or selected~=name
 selected=name;if not opening then closeMenu();return end;modal.Visible=true
 academy.menuQuestFocus=name=="Quests" and focusQuest or nil
 if academy.hideMiniMapForMenu then academy.hideMiniMapForMenu() end
 if academy.refreshTestLauncher then academy.refreshTestLauncher() end
 if opening then
  if name=="Style" then
   -- Keep item positions stable across a purchase response while this tab is open.
   local nextUpgrade=academy.gearUpgrade(data)
   if nextUpgrade~=academy.nextGearUpgrade then resetScroll=true end
   academy.nextGearUpgrade=nextUpgrade
  end
  if resetScroll then renderedTab=nil;renderedMenuKey=nil end
  if name=="Shop" then action:FireServer("ShopRefresh") end
  if closeConversation then closeConversation() end
  if devPanel then devPanel.Visible=false end
  render()
 end
end
local function toggle()
 if modal.Visible then closeMenu() else toggleTab(selected) end
end
local shop=button(top,"ShopToggle","MENU [B]",UDim2.fromOffset(125,36),UDim2.fromOffset(0,0),toggle,gold);shop.TextColor3=dark
local questsToggle=button(top,"QuestsToggle","QUESTS",UDim2.fromOffset(95,36),UDim2.fromOffset(134,0),function() toggleTab("Quests",true) end)
questsToggle.Visible=false
academy.surface(shop);academy.surface(questsToggle)
local function questLauncherText()
 local count=0
 for _,quest in ipairs(Config.Quests)do
  local progress=data.quests and data.quests[quest.id]
  if progress and not progress.claimed and progress.progress>=quest.goal then count+=1 end
 end
 return count>0 and ("QUESTS "..count) or "QUESTS"
end
local hud=frame(gui,"CompactHUD",UDim2.fromOffset(242,94),UDim2.new(0,14,1,-108));hud.BackgroundTransparency=.04
academy.surface(hud,gold)
frame(hud,"EnergyAccent",UDim2.new(1,-24,0,1),UDim2.fromOffset(12,2),gold)
local levelBadge=frame(hud,"LevelBadge",UDim2.fromOffset(82,24),UDim2.fromOffset(12,8),gold)
levelBadge.Active=false;levelBadge.Selectable=false;levelBadge.Interactable=false
local stats=label(levelBadge,"LEVEL 1",UDim2.fromScale(1,1),UDim2.new(),12,dark)
stats.Name="LevelValue";stats.Font=Enum.Font.GothamBold;stats.TextXAlignment=Enum.TextXAlignment.Center;stats.TextWrapped=false
local coins=label(hud,"0 coins",UDim2.fromOffset(128,24),UDim2.fromOffset(102,8),13,white)
coins.Name="CoinValue";coins.Font=Enum.Font.GothamBold;coins.TextXAlignment=Enum.TextXAlignment.Right;coins.TextWrapped=false
coins.Active=false;coins.Selectable=false;coins.Interactable=false
academy.healthMark=academy.mark(hud,"health",UDim2.fromOffset(12,36),10,Color3.fromRGB(130,211,174))
local health=label(hud,"100 HP",UDim2.fromOffset(204,18),UDim2.fromOffset(26,32),14)
health.Name="HealthValue";health.Font=Enum.Font.GothamBold;health.TextWrapped=false
academy.incomingHit=label(hud,"BEAM HIT YOU",UDim2.fromOffset(116,18),UDim2.fromOffset(114,32),13,Color3.fromRGB(255,157,146))
academy.incomingHit.Name="IncomingBeamHit"
academy.incomingHit.Font=Enum.Font.GothamBold
academy.incomingHit.TextXAlignment=Enum.TextXAlignment.Right
academy.incomingHit.TextWrapped=false
academy.incomingHit.Visible=false
academy.incomingHit.Active=false;academy.incomingHit.Selectable=false;academy.incomingHit.Interactable=false
local hf=frame(frame(hud,"HealthTrack",UDim2.fromOffset(218,8),UDim2.fromOffset(12,51),panel),"Fill",UDim2.fromScale(1,1),UDim2.new(),Color3.fromRGB(105,224,158))
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
local xpText=label(hud,"0 / 103 XP",UDim2.new(1,-38,0,19),UDim2.fromOffset(26,61),12,muted)
xpText.TextScaled=true
do local xpScale=Instance.new("UITextSizeConstraint");xpScale.Name="XPTextScale";xpScale.MaxTextSize=12;xpScale.MinTextSize=9;xpScale.Parent=xpText end
local xf=frame(frame(hud,"XPTrack",UDim2.fromOffset(218,4),UDim2.fromOffset(12,82),panel),"Fill",UDim2.fromScale(0,1),UDim2.new(),gold)
academy.progressMark=academy.mark(hud,"progress",UDim2.fromOffset(12,64),10,gold)
function academy.layoutStatusCard(compact)
 hud.Size=UDim2.fromOffset(compact and 218 or 242,compact and 78 or 94)
 levelBadge.Size=UDim2.fromOffset(compact and 68 or 82,compact and 20 or 24)
 levelBadge.Position=UDim2.fromOffset(12,compact and 6 or 8)
 coins.Size=UDim2.fromOffset(compact and 120 or 128,compact and 20 or 24)
 coins.Position=UDim2.fromOffset(compact and 86 or 102,compact and 6 or 8)
 health.Size=UDim2.fromOffset(compact and 82 or 204,18)
 health.Position=UDim2.fromOffset(26,compact and 27 or 32)
 academy.healthMark.Position=UDim2.fromOffset(12,compact and 31 or 36)
 academy.incomingHit.Size=UDim2.fromOffset(compact and 94 or 116,18)
 academy.incomingHit.Position=UDim2.fromOffset(compact and 112 or 114,compact and 27 or 32)
 hf.Parent.Size=UDim2.new(1,-24,0,compact and 6 or 8)
 hf.Parent.Position=UDim2.fromOffset(12,compact and 46 or 51)
 xpText.Size=UDim2.new(1,-38,0,compact and 15 or 19)
 xpText.Position=UDim2.fromOffset(26,compact and 53 or 61)
 academy.progressMark.Position=UDim2.fromOffset(12,compact and 55 or 64)
 xf.Parent.Size=UDim2.new(1,-24,0,4)
 xf.Parent.Position=UDim2.fromOffset(12,compact and 70 or 82)
end
local zone=label(gui,"SAFE • PvP OFF",UDim2.fromOffset(240,28),UDim2.new(.5,-120,0,12),13);zone.Name="ZoneStatus";zone.TextXAlignment=Enum.TextXAlignment.Center
zone.BackgroundColor3=dark;zone.BackgroundTransparency=.08
do local corner=Instance.new("UICorner");corner.CornerRadius=UDim.new(0,8);corner.Parent=zone end
academy.surface(zone)
-- Immediate local zone cue only; server damage authorization remains independent.
function academy.refreshZone()
 local character=p.Character
 local root=character and character:FindFirstChild("HumanoidRootPart")
 local position=root and root.Position
 local enabled=position and Config.InArena(position)==true or false
 local garden=enabled and Config.InGardenPvp and Config.InGardenPvp(position)==true
 local bossHint=not enabled and position and p:GetAttribute("BossCombatHint")
 local strikeAt=not enabled and not bossHint and position and character:GetAttribute("TrainingStrikeAt")
 local trainingHint=false
 if type(strikeAt)=="number" and workspace:GetServerTimeNow()<strikeAt then
  local center=character:GetAttribute("TrainingStrikeCenter")
  local humanoid=character:FindFirstChildOfClass("Humanoid")
  if typeof(center)=="Vector3" and humanoid and humanoid.Health>0 then
   local x,z=position.X-center.X,position.Z-center.Z
   local radius=academy.TrainingRules.StrikeRadius
   trainingHint=x*x+z*z<=radius*radius
  end
 end
 local value=enabled and (garden and "GARDEN • PvP ON" or "ARENA • PvP ON") or bossHint or trainingHint and "MOVE OR DODGE" or "SAFE • PvP OFF"
 local layout=Config.ResonanceLayout
 if layout and position then
  if enabled then value="RESONANCE HALL • PvP ON"
  elseif layout.Contains(layout.Practice,position) then value="TRAINING LANDING • SAFE"
  elseif layout.Contains(layout.Hall,position) and layout.IsSafeApron(position) then value="TRAINING PORTAL • SAFE" end
 end
 if zone.Text~=value then
  zone.Text=value;zone.TextColor3=(enabled or trainingHint) and Color3.fromRGB(255,140,139) or bossHint and gold or white
 end
end
function academy.layoutZone(viewport,touch)
 if touch or viewport.X<820 then
  zone.Size=UDim2.fromOffset(math.min(190,math.max(120,viewport.X-140)),14)
  zone.Position=UDim2.fromOffset(14,49);zone.TextSize=11
 else
  zone.Size=UDim2.fromOffset(240,24);zone.Position=UDim2.new(.5,-120,0,12);zone.TextSize=13
 end
end

local tracked=label(gui,"",UDim2.fromOffset(290,50),UDim2.fromOffset(16,56),13);tracked.Name="QuestTracker";tracked.TextYAlignment=Enum.TextYAlignment.Top
tracked.BackgroundColor3=dark;tracked.BackgroundTransparency=.06
academy.surface(tracked)
do
 local trackerCorner=Instance.new("UICorner");trackerCorner.CornerRadius=UDim.new(0,8);trackerCorner.Parent=tracked
 local trackerPadding=Instance.new("UIPadding");trackerPadding.PaddingLeft=UDim.new(0,6);trackerPadding.PaddingRight=UDim.new(0,6);trackerPadding.PaddingTop=UDim.new(0,4);trackerPadding.PaddingBottom=UDim.new(0,4);trackerPadding.Parent=tracked
end
local toast=label(gui,"",UDim2.new(.7,0,0,48),UDim2.new(.15,0,.72,0),16,gold);toast.TextXAlignment=Enum.TextXAlignment.Center;toast.AnchorPoint=Vector2.new(.5,1);toast.Position=UDim2.fromScale(.5,.72)
toast.Name="Notification";toast.ZIndex=30;toast.BackgroundColor3=dark;toast.BackgroundTransparency=.08;toast.Visible=false
local saveNotice=label(gui,"",UDim2.fromOffset(250,28),UDim2.new(.5,-125,0,40),12,gold);saveNotice.TextXAlignment=Enum.TextXAlignment.Center
saveNotice.BackgroundColor3=dark;saveNotice.BackgroundTransparency=.08
do local corner=Instance.new("UICorner");corner.CornerRadius=UDim.new(0,8);corner.Parent=saveNotice end
academy.surface(saveNotice,gold)
local notifications=loadClientDependency(script.Parent,"NotificationQueue");if not clientCheckpoint() then return end
notifications=notifications.new();if not clientCheckpoint() then return end
local toastWidth=0
local NoticeLayout=loadClientDependency(script.Parent,"NoticeLayout");if not clientCheckpoint() then return end
local noticeView=loadClientDependency(script.Parent,"NoticeView");if not clientCheckpoint() then return end
noticeView=noticeView.new(gui,toast)
ownClient(function() noticeView:Destroy() end);if not clientCheckpoint() then return end

local function notify(t,urgent,key) notifications:Push(t,urgent,key) end
local nextCast=0;local sequence=0;local captureSource=nil
local sustainedControl,sustainedRules
local voiceAccessInterrupted=false
do
 local readout=loadClientDependency(script.Parent,"DamageReadout");if not clientCheckpoint() then return end
 academy.damageReadout=readout.new(gui,frame,label,academy.surface,gold,muted)
 ownClient(function() academy.damageReadout.root:Destroy() end)
 connectClient(p.CharacterRemoving,function() academy.damageReadout:Clear() end)
 local function bind(remote)
  if academy.damageReadout.available or remote.Name~="DamageSummary" or not remote:IsA("RemoteEvent") then return end
  academy.damageReadout.available=true
  connectClient(remote.OnClientEvent,function(phase,dps,total)
   academy.damageReadout:Receive(phase,dps,total,os.clock())
  end)
 end
 connectClient(remotes.ChildAdded,bind)
 local remote=remotes:FindFirstChild("DamageSummary");if remote then bind(remote) end
end
local windowFocused=true
local function cancelCapture()
 if sustainedControl then sustainedControl:Cancel();return end
 captureSource=nil;mic:Cancel();action:FireServer("CancelCast")
end
local function blocked()
 local character=p.Character
 local humanoid=character and character:FindFirstChildOfClass("Humanoid")
 if not humanoid or humanoid.Health<=0 or humanoid.PlatformStand then return true end
 local now=workspace:GetServerTimeNow()
 return GuiService.MenuIsOpen or UIS:GetFocusedTextBox()~=nil or (conversationPanel and conversationPanel.Visible) or modal.Visible or (devPanel and devPanel.Visible) or now<(p:GetAttribute("ProtectionEnds") or 0) or now<(p:GetAttribute("DodgeEnds") or 0) or now<(p:GetAttribute("KnockdownEnds") or 0)
end
local function beamBlocked()
 return not mic.ready or data.voiceEligible~=true or blocked()
end
local function screenFeedbackAllowed()
 return not clientDestroyed and windowFocused and sustainedControl~=nil and sustainedControl.armed
  and not data.settings.reducedShake and not platformReducedMotion and not beamBlocked()
end
local function beginCapture(source)
 if sustainedControl or captureSource or beamBlocked() or os.clock()<nextCast then return end
 if mic:Begin() then sequence+=1;captureSource=source;action:FireServer("BeginCast",sequence) end
end
local function usesCenterAim()
 local input=UIS.PreferredInput
 return input==Enum.PreferredInput.Touch or input==Enum.PreferredInput.Gamepad
end
local function aimRay()
 local camera=workspace.CurrentCamera
 if not camera or camera.ViewportSize.X<2 or camera.ViewportSize.Y<2 then return nil end
 local location=usesCenterAim() and camera.ViewportSize/2 or UIS:GetMouseLocation()
 local ray=camera:ViewportPointToRay(location.X,location.Y)
 local params=RaycastParams.new();params.FilterDescendantsInstances={p.Character};params.FilterType=Enum.RaycastFilterType.Exclude;params.RespectCanCollide=true
 return ray,workspace:Raycast(ray.Origin,ray.Direction*1000,params)
end
if remotes:GetAttribute("AutomaticVoice")==true then
 sustainedRules=loadClientDependency(RS.Shared,"SustainedAttack");if not clientCheckpoint() then return end
 local VoiceActivation=loadClientDependency(RS.Shared,"VoiceActivation");if not clientCheckpoint() then return end
 sustainedControl=loadClientDependency(script.Parent,"SustainedControls");if not clientCheckpoint() then return end
 sustainedControl=sustainedControl.new(VoiceActivation.new(),
  function(verb,arg) if verb=="SustainedStop" or not clientDestroyed then action:FireServer(verb,arg) end end,
  function()
   if not workspace.CurrentCamera then return nil end
   local ray,hit=aimRay()
   if not ray then return nil end
   return hit and hit.Position or ray.Origin+ray.Direction*1000
  end,function() notifications:Remove("voice") end)
 ownClient(function() sustainedControl:Destroy() end);if not clientCheckpoint() then return end
end
local function voiceEligibilityHint(compact)
 if data.voiceEligible==true then
  local input=mic.input
  if input and input.Parent and input.Muted then
   return compact and "MIC MUTED\nUnmute in Roblox" or "Beams stay OFF. Unmute in Roblox, then turn Beams on.",true
  end
  return nil
 end
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
  local hint,inputMuted=voiceEligibilityHint()
  if inputMuted then academy.muteNoticePending=true end
  notify(hint or "Beams stay OFF. Wait for live microphone input and gameplay to be ready, then turn them on.",true,inputMuted and "micMuted" or "voice");return
 end
 sustainedControl:SetArmed(not sustainedControl.armed)
 notify(sustainedControl.armed and "Beams ON. Normal speech can fire attacks. Go quiet, then speak. Turn OFF to talk freely; voice chat is unchanged."
  or "Beams OFF. Talk freely without attacking. Voice chat is unchanged.",false,"voice")
end
local function screamToggleLabel(armed,touch,status)
 return (armed and "BEAMS: ON" or "BEAMS: OFF").."\n"..(status or (touch and "Tap" or "[E]")..(armed and " to turn off" or " to turn on"))
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
 if not blocked() then
  local character=p.Character;local root=character and character:FindFirstChild("HumanoidRootPart")
  local humanoid=character and character:FindFirstChildOfClass("Humanoid")
  local intent="Right"
  -- Cardinal intent only. Forward wins exact diagonal ties; opposite keys cancel.
  local x=(UIS:IsKeyDown(Enum.KeyCode.D) and 1 or 0)-(UIS:IsKeyDown(Enum.KeyCode.A) and 1 or 0)
  local z=(UIS:IsKeyDown(Enum.KeyCode.W) and 1 or 0)-(UIS:IsKeyDown(Enum.KeyCode.S) and 1 or 0)
  if x==0 and z==0 and root and humanoid then
   x=humanoid.MoveDirection:Dot(root.CFrame.RightVector)
   z=humanoid.MoveDirection:Dot(root.CFrame.LookVector)
  end
  if math.abs(z)>.1 and math.abs(z)>=math.abs(x) then intent=z<0 and "Back" or "Forward"
  elseif math.abs(x)>.1 then intent=x<0 and "Left" or "Right" end
  action:FireServer("Dodge",intent)
 end
end
local controls=frame(gui,"Actions",UDim2.fromOffset(260,88),UDim2.new(1,-274,1,-102));controls.BackgroundTransparency=1
local castButton=button(controls,"Cast","BEAM  [E]",UDim2.fromOffset(260,44),UDim2.fromOffset(0,0),toggleVoice,gold);castButton.TextColor3=dark
castButton.TextWrapped=true;castButton.Selectable=true
academy.surface(castButton,gold)
do
 local mark=academy.mark(castButton,"voice",UDim2.fromOffset(15,12),20,muted)
 mark.Visible=sustainedControl~=nil
 if sustainedControl then
  castButton.TextColor3=white
  local edge=castButton.AcademyEdge
  local glyphs=mark:GetChildren()
  local faces={
   off={panel,muted},
   armed={Color3.fromRGB(62,48,30),gold},
   firing={Color3.fromRGB(22,60,49),Color3.fromRGB(104,222,157)},
   cooldown={Color3.fromRGB(38,49,60),Color3.fromRGB(158,191,207)},
  }
  local current
  function academy.setBeamFace(armed,firing,cooldown)
   local mode=not armed and "off" or firing and "firing" or cooldown and "cooldown" or "armed"
   if mode==current then return end
   current=mode
   local face,accent=table.unpack(faces[mode])
   castButton.BackgroundColor3=face;edge.Color=accent
   for _,bar in ipairs(glyphs) do bar.BackgroundColor3=accent end
  end
  academy.setBeamFace(false,false,false)
 end
end
local voiceTimeTrack=frame(castButton,"VoiceTimeTrack",UDim2.new(1,-60,0,3),UDim2.new(0,48,1,-6),dark)
voiceTimeTrack.Active=false;voiceTimeTrack.Interactable=false;voiceTimeTrack.Selectable=false
local voiceTimeFill=frame(voiceTimeTrack,"RemainingOrRecovery",UDim2.fromScale(0,1),UDim2.new(),muted)
voiceTimeFill.Active=false;voiceTimeFill.Interactable=false;voiceTimeFill.Selectable=false
voiceTimeTrack.Visible=false
castButton.InputBegan:Connect(function(input)
 if input.UserInputType==Enum.UserInputType.MouseButton1 or input.UserInputType==Enum.UserInputType.Touch then beginCapture(input) end
end)

academy.VoiceReactor=loadClientDependency(script.Parent,"VoiceReactor");if not clientCheckpoint() then return end
academy.reactor=academy.VoiceReactor.new(gui)
local meter=academy.reactor.root
local meterText=academy.reactor.text
local meterFill=academy.reactor.fill
if sustainedControl then
 local threshold=frame(academy.reactor.track,"VoiceStartThreshold",UDim2.fromOffset(2,7),UDim2.new(sustainedControl.gate.OnPower,0,.5,0),white)
 threshold.AnchorPoint=Vector2.new(.5,.5);threshold.ZIndex=meterFill.ZIndex+1
 threshold.Visible=false;academy.voiceThreshold=threshold
end
local aimGui=Instance.new("ScreenGui");aimGui.Name="ScreamAim";aimGui.ResetOnSpawn=false;aimGui.ScreenInsets=Enum.ScreenInsets.None;aimGui.Parent=p.PlayerGui
ownClient(function() aimGui:Destroy() end);if not clientCheckpoint() then return end
local reticle=label(aimGui,"+",UDim2.fromOffset(24,24),UDim2.new(.5,-12,.5,-12),22,white);reticle.Name="Crosshair";reticle.TextXAlignment=Enum.TextXAlignment.Center
local hitFeedback=loadClientDependency(script.Parent,"HitFeedback");if not clientCheckpoint() then return end
hitFeedback=hitFeedback.new();if not clientCheckpoint() then return end
local hitText=label(aimGui,"",UDim2.fromOffset(210,26),UDim2.new(.5,-105,.5,-48),16,gold);hitText.Name="ConfirmedDamage";hitText.TextXAlignment=Enum.TextXAlignment.Center;hitText.Visible=false
local aimInfo=label(gui,"",UDim2.fromOffset(290,48),UDim2.new(.5,-145,.5,25),14,gold);aimInfo.TextXAlignment=Enum.TextXAlignment.Center
aimInfo.Font=Enum.Font.GothamBold
aimInfo.TextStrokeColor3=dark;aimInfo.TextStrokeTransparency=.12
local reportedReady=nil;local readyReportAt=0
local dodgeButton=button(controls,"Dodge","DODGE  [Q]",UDim2.fromOffset(108,32),UDim2.fromOffset(0,52),dodge);academy.surface(dodgeButton)
function academy.trainingHeadAt(ray,distance)
 local picked
 for _,head in ipairs(game:GetService("CollectionService"):GetTagged("TrainingAimHead")) do
  local model=head.Parent
  if not model or model:GetAttribute("ResidentActive")==false then continue end
  local origin=head.CFrame:PointToObjectSpace(ray.Origin)
  local direction=head.CFrame:VectorToObjectSpace(ray.Direction)
  local half=head.Size/2
  local enter,leave=0,distance
  for _,axis in ipairs({"X","Y","Z"}) do
   local start,speed,extent=origin[axis],direction[axis],half[axis]
   if math.abs(speed)<.00001 then
    if math.abs(start)>extent then enter=math.huge;break end
   else
    local a,b=(-extent-start)/speed,(extent-start)/speed
    enter=math.max(enter,math.min(a,b));leave=math.min(leave,math.max(a,b))
    if enter>leave then break end
   end
  end
  if enter<=leave and enter<distance then picked=model;distance=enter end
 end
 return picked
end
local sprinting=false
local nextSprintSend=0
local function setSprint(requested)
 local character=p.Character;local humanoid=character and character:FindFirstChildOfClass("Humanoid")
 if requested and (not windowFocused or GuiService.MenuIsOpen or UIS:GetFocusedTextBox()~=nil
  or modal.Visible or (devPanel and devPanel.Visible) or (conversationPanel and conversationPanel.Visible)
  or not humanoid or humanoid.Health<=0 or humanoid.PlatformStand or humanoid.Sit or humanoid.SeatPart
  or workspace:GetServerTimeNow()<(p:GetAttribute("KnockdownEnds") or 0)) then requested=false end
 -- Reconcile a held request after a transient quota rejection; never retry OFF.
 local now=os.clock()
 if sprinting==requested and (not requested or now<nextSprintSend) then return end
 sprinting=requested;nextSprintSend=now+.5;action:FireServer("Sprint",requested)
end
local function previewAttackOrigin(root)
 local character=p.Character;local head=character and character:FindFirstChild("Head")
 if head and head:IsA("BasePart") and (head.Position-root.Position).Magnitude<5 then return head.Position end
 return root.Position+Vector3.new(0,1,0)
end
local function beamTargetRange(root,targetRoot,aimPoint,stats,pvp)
 local origin=previewAttackOrigin(root)
 local aim=aimPoint-origin
 local projection=aim.Magnitude>=.01 and (targetRoot.Position-origin):Dot(aim.Unit) or math.huge
 local rootDistance=pvp and (targetRoot.Position-root.Position).Magnitude or 0
 local far=projection<0 or projection>stats.maxRange or rootDistance>stats.maxRange+2
 local currentFar=projection>stats.range or rootDistance>stats.range+2
 return far,currentFar,origin
end
local function targetCovered(origin,targetRoot,targetModel,aimPoint)
 local delta=targetRoot.Position-origin
 local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Exclude
 params.FilterDescendantsInstances={p.Character,targetModel};params.RespectCanCollide=true
 if workspace:Raycast(origin,delta,params) then return true end
 local aim=aimPoint-origin
 if aim.Magnitude<.01 then return false end
 local direction=aim.Unit
 local projection=delta:Dot(direction)
 if projection<=0 then return false end
 -- The server ignores actors when shortening the actual beam, then checks sight to the root separately.
 local excluded=game:GetService("CollectionService"):GetTagged("CityResident")
 table.insert(excluded,targetModel)
 for _,player in ipairs(Players:GetPlayers()) do
  if player.Character then table.insert(excluded,player.Character) end
 end
 params.FilterDescendantsInstances=excluded
 local obstruction=workspace:Raycast(origin,direction*projection,params)
 return obstruction~=nil and obstruction.Distance<projection
end
local function playerTargetInfo(target,humanoid,inPvp,targetInPvp,far,now,currentFar,covered)
 if humanoid.Health<=0 then return nil,false end
 local protection=math.max(0,(target:GetAttribute("ProtectionEnds") or 0)-now)
 local rolling=now<(target:GetAttribute("DodgeEnds") or 0)
 local status=not inPvp and (targetInPvp and "YOU ARE OUTSIDE PvP" or "BOTH OUTSIDE PvP")
  or not targetInPvp and "TARGET OUTSIDE PvP"
  or protection>0 and string.format("PROTECTED · %.1fs",protection)
  or rolling and "DODGING" or far and "OUT OF MAX RANGE" or currentFar and "BEYOND CURRENT RANGE" or covered and "BEHIND COVER" or "ARENA OPPONENT"
 local level=target:GetAttribute("ScreamLevel")
 local name=target.DisplayName..(type(level)=="number" and string.format(" · LV %d",level) or "")
 return string.format("%s\n%s",name,status),
  inPvp and targetInPvp and protection<=0 and not rolling and not far and not currentFar and not covered
end
local function residentTargetInfo(model,humanoid,far,currentFar,covered,position)
 if model:GetAttribute("ResidentActive")==false then return nil,false end
 if not humanoid or humanoid.Health<=0 then return nil,false end
 local home=model:GetAttribute("TrainingHome")
 local outsidePad=typeof(home)=="Vector3" and (position-home).Magnitude>academy.TrainingRules.Radius
 local status=outsidePad and "MOVE TOWARD PAD CENTER" or far and "OUT OF MAX RANGE" or currentFar and "BEYOND CURRENT RANGE" or covered and "BEHIND COVER"
  or (model:GetAttribute("TrainingTier")~=nil and "TRAINING FIGHTER" or "CITY RESIDENT")
 return string.format("%s\n%s",model:GetAttribute("DisplayName") or model.Name,status),not outsidePad and not far and not currentFar and not covered
end
local sprintButton=button(controls,"Sprint","SPRINT [SHIFT]",UDim2.fromOffset(144,32),UDim2.fromOffset(116,52),function() setSprint(not sprinting) end);academy.surface(sprintButton)
do
 local track=frame(sprintButton,"StaminaTrack",UDim2.new(1,-18,0,3),UDim2.new(0,9,1,-6),dark)
 local fill=frame(track,"Stamina",UDim2.fromScale(1,1),UDim2.new(),Color3.fromRGB(130,211,174))
 track.Active=false;track.Interactable=false;track.Selectable=false
 fill.Active=false;fill.Interactable=false;fill.Selectable=false
 academy.staminaFill=fill
end
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
  or (devPanel and devPanel.Visible) or (conversationPanel and conversationPanel.Visible) then return end
 local target=talkTarget
 if not target or not target.Parent or target:GetAttribute("ResidentActive")==false
  or not InteractionRules.CanReachNpc(p.Character,target,13) then return end
 -- A rejected Talk request should not cancel the current beam.
 action:FireServer("Talk",target:GetAttribute("NpcId") or target.Name)
end
local talkButton=button(gui,"Talk","TALK [T]",UDim2.fromOffset(120,34),UDim2.new(.5,-60,1,-108),requestTalk);talkButton.Visible=false;academy.surface(talkButton,gold)
local localFlightTools=Run:IsStudio() and game.PlaceId==0 and game.GameId==0 and workspace:GetAttribute("LocalSustainedPrototype")==true
-- Display capability is server-produced, not client authorization. Nil fallback
-- exists only for unchanged disposable local UI startup fixtures.
function academy.testToolsAllowed()
 if clientDestroyed or data.devAccess~=true then return false end
 local capability=remotes:GetAttribute("TestToolsAvailable")
 if capability==nil then return localFlightTools end
 return capability==true and data.testBeamAvailable==true
end
devPanel=frame(gui,"TestPanel",UDim2.fromOffset(230,330),UDim2.new(1,-244,0,60));devPanel.Visible=false;devPanel.ZIndex=10;academy.surface(devPanel)
do
 local testContent=Instance.new("ScrollingFrame");testContent.Name="Commands";testContent.BackgroundTransparency=1;testContent.BorderSizePixel=0;testContent.ScrollBarThickness=4;testContent.Position=UDim2.fromOffset(8,76);testContent.Size=UDim2.new(1,-16,1,-84);testContent.CanvasSize=UDim2.fromOffset(0,235);testContent.Parent=devPanel
 label(devPanel,"TEST SESSION",UDim2.fromOffset(210,25),UDim2.fromOffset(10,8),17,gold)
 label(devPanel,"Temporary progress. Shared combat is isolated.",UDim2.fromOffset(210,38),UDim2.fromOffset(10,35),12,muted)
 do
  local testCommands={{"XP","+500 XP"},{"AddLevels","+10 levels"},{"Coins","+1,000 coins"},{"MaxLevel","Level "..Config.MaxLevel},{"LevelOne","Level 1"},{"Heal","Heal"},{"Hub","Safe hub"},{"Arena","Arena"},{"Beach","Beach"},{"ResetQuests","Reset quests"}}
  table.insert(testCommands,1,{"Fly","Fly on / off"})
  if Run:IsStudio() then table.insert(testCommands,{"ResetBots","Reset bots"});table.insert(testCommands,{"StudioMovement","Test movement"}) end
  academy.testCommandButtons={}
  for _,item in ipairs(testCommands) do
   local b=button(testContent,item[1],item[2],UDim2.new(.5,-6,0,44),UDim2.new(),function()
    if item[1]=="Fly" and not academy.testToolsAllowed() then return end
    action:FireServer("DevCommand",item[1])
   end)
   if item[1]=="Fly" then b.Visible=false end
   table.insert(academy.testCommandButtons,{button=b,id=item[1]})
  end
  function academy.layoutTestCommands(allowed)
   if academy.testerToolsVisible==allowed then return end
   academy.testerToolsVisible=allowed
   local index=0;local beamOffset=allowed and 164 or 0
   for _,entry in ipairs(academy.testCommandButtons) do
    local visible=entry.id~="Fly" or allowed
    entry.button.Visible=visible
    if visible then
     entry.button.Position=UDim2.new((index%2)*.5,0,0,beamOffset+math.floor(index/2)*47);index+=1
    end
   end
   testContent.CanvasSize=UDim2.fromOffset(0,beamOffset+math.ceil(index/2)*47)
  end
 end
 testContent.XP.Modal=true
 do
  local TestBeamTools=loadClientDependency(script.Parent,"TestBeamTools");if not clientCheckpoint() then return end
  -- ScreamAim has ScreenInsets.None: its center matches ViewportPointToRay,
  -- independent of the cursor sitting over a Test Tools button or the top inset.
  local testAim=label(aimGui,"+",UDim2.fromOffset(28,28),UDim2.new(.5,-14,.5,-14),26,gold)
  testAim.Name="TestBeamCrosshair";testAim.TextXAlignment=Enum.TextXAlignment.Center;testAim.Visible=false
  local testAimHint=label(aimGui,"TEST AIM",UDim2.fromOffset(100,20),UDim2.new(.5,-50,.5,18),11,gold)
  testAimHint.Name="TestBeamAimHint";testAimHint.TextXAlignment=Enum.TextXAlignment.Center;testAimHint.Visible=false
  local function testBeamAllowed()
   return academy.testToolsAllowed() and devPanel.Visible and data.devAccess==true and windowFocused
    and not GuiService.MenuIsOpen and not UIS:GetFocusedTextBox() and not modal.Visible
    and not (conversationPanel and conversationPanel.Visible) and p:GetAttribute("TestFlight")~=true
  end
  local testBeam=TestBeamTools.new({
   now=os.clock,state=function() return data end,allowed=testBeamAllowed,
   aim=function()
    local camera=workspace.CurrentCamera
    if not camera or camera.ViewportSize.X<2 or camera.ViewportSize.Y<2 then return nil end
    local ray=camera:ViewportPointToRay(camera.ViewportSize.X/2,camera.ViewportSize.Y/2)
    -- No microphone or UI-position raycast. The server excludes the
    -- character and clips this far-point intent against authoritative cover.
    return ray.Origin+ray.Direction*1000
   end,
   send=function(verb,payload) action:FireServer(verb,payload) end,
  })
  local previewControls={}
  local powerLabel=label(testContent,"BEAM TEST · Power 50%",UDim2.new(1,-4,0,22),UDim2.fromOffset(0,0),12,gold)
  powerLabel.Name="TestBeamPower";powerLabel.Visible=false;table.insert(previewControls,powerLabel)
  local explanation=label(testContent,"Silent visual preview · no damage",UDim2.new(1,-4,0,20),UDim2.fromOffset(0,22),10,muted)
  explanation.Visible=false;table.insert(previewControls,explanation)
  for i,item in ipairs({{"BeamZero","0%",0},{"BeamLess","-10%",-10},{"BeamMore","+10%",10},{"BeamFull","100%",100}}) do
   local b=button(testContent,item[1],item[2],UDim2.new(.25,-4,0,44),UDim2.new((i-1)*.25,0,0,44),function()
    if not academy.testToolsAllowed() then return end
    testBeam:SetPower((i==1 or i==4) and item[3] or testBeam.power+item[3])
   end);b.TextSize=12;b.Selectable=true;b.Visible=false;table.insert(previewControls,b)
  end
  local fire=button(testContent,"TestBeam","TEST BEAM",UDim2.new(1,-4,0,44),UDim2.fromOffset(0,92),function() if not academy.testToolsAllowed() then return end;cancelCapture();testBeam:Toggle() end)
  fire.Selectable=true;fire.Visible=false;table.insert(previewControls,fire)
  local status=label(testContent,"Aim at +, then click Test Beam.",UDim2.new(1,-4,0,22),UDim2.fromOffset(0,138),10,muted)
  status.Name="TestBeamStatus";status.Visible=false;table.insert(previewControls,status)
  function academy.refreshTesterTools()
   local allowed=academy.testToolsAllowed()
   academy.layoutTestCommands(allowed)
   for _,control in ipairs(previewControls) do if control.Visible~=allowed then control.Visible=allowed end end
   if not allowed then testBeam:Stop();testAim.Visible=false;testAimHint.Visible=false end
  end
  connectClient(remotes:GetAttributeChangedSignal("TestToolsAvailable"),academy.refreshTesterTools)
  academy.refreshTesterTools()
  connectClient(Run.Heartbeat,function()
   if not academy.testerToolsVisible then return end
   testBeam:Tick()
   testAim.Visible=testBeamAllowed() and (data.testBeamAvailable==true or testBeam.running)
   testAimHint.Visible=testAim.Visible
   local damaging=data.testBeamDamageAvailable==true
   local description=damaging and "Silent · damages other testers in PvP" or "Silent visual preview · no damage"
   if explanation.Text~=description then explanation.Text=description end
   powerLabel.Text=string.format("BEAM TEST · Power %d%%",testBeam.power)
   fire.Text=testBeam.running and "STOP TEST BEAM" or "TEST BEAM"
   status.Text=data.testBeamActive==true and string.format(damaging and "Active: %d%% · silent test damage" or "Active: %d%% · silent / visual only",data.testBeamPower or 0)
    or (data.testBeamCooldown or 0)>0 and string.format("Cooldown: %.1fs",data.testBeamCooldown)
    or p:GetAttribute("TestFlight")==true and "Turn Fly off to test the beam."
    or data.testBeamAvailable~=true and "Authorized test session required."
    or testBeam.power==0 and "0% · no beam. Increase power to test."
    or damaging and "Both players need a test session."
    or "Aim at +, then click Test Beam."
  end)
  connectClient(devPanel:GetPropertyChangedSignal("Visible"),function() if not devPanel.Visible then testBeam:Stop() end end)
  connectClient(UIS.WindowFocusReleased,function() testBeam:Stop() end)
  connectClient(GuiService.MenuOpened,function() testBeam:Stop() end)
  connectClient(p.CharacterRemoving,function() testBeam:Stop() end)
  ownClient(function() testBeam:Stop() end)
 end
end
local testButton=button(gui,"TestToggle","TEST TOOLS",UDim2.fromOffset(112,32),UDim2.new(1,-126,0,14),function() if not academy.canShowTestLauncher() then return end;devPanel.Visible=not devPanel.Visible;if devPanel.Visible then closeMenu() end end);testButton.Visible=false;testButton.ZIndex=11;academy.surface(testButton)
-- One visibility owner: replicated State and the frame loop must agree while menus are open.
-- Keep modal transitions synchronous so no launcher frame leaks before RenderStepped.
function academy.canShowTestLauncher()
 return not clientDestroyed and not academy.testLauncherBlocked and data.devAccess==true and not GuiService.MenuIsOpen and not modal.Visible and not (conversationPanel and conversationPanel.Visible)
end
function academy.refreshTestLauncher()
 testButton.Visible=academy.canShowTestLauncher()
end
-- Flight controls exist only as UI; server independently validates the local fixture.
local flightUp=false;local flightDown=false;local flightSentAt=0;local flightFocused=true
local flightStatus=label(gui,"",UDim2.fromOffset(360,28),UDim2.new(.5,-180,0,110),13,gold)
flightStatus.Name="FlightStatus";flightStatus.Visible=false
local upButton=button(gui,"FlightUp","FLY UP",UDim2.fromOffset(90,44),UDim2.new(1,-210,1,-190),function() if not academy.testToolsAllowed() then return end;flightUp=not flightUp;flightDown=false end)
local downButton=button(gui,"FlightDown","FLY DOWN",UDim2.fromOffset(90,44),UDim2.new(1,-110,1,-190),function() if not academy.testToolsAllowed() then return end;flightDown=not flightDown;flightUp=false end)
upButton.Visible=false;downButton.Visible=false
connectClient(UIS.WindowFocusReleased,function() flightFocused=false;flightUp=false;flightDown=false end)
connectClient(UIS.WindowFocused,function() flightFocused=true end)
connectClient(Run.Heartbeat,function()
 local active=p:GetAttribute("TestFlight")==true
 if active and not academy.testToolsAllowed() then
  if not academy.testerFlightStopSent then academy.testerFlightStopSent=true;action:FireServer("FlightStop") end
  active=false
 else academy.testerFlightStopSent=false end
 flightStatus.Visible=active;upButton.Visible=active and UIS.TouchEnabled;downButton.Visible=active and UIS.TouchEnabled
 if not active then flightUp=false;flightDown=false;return end
 flightStatus.Text="TEST FLIGHT · WASD · Space up / Ctrl down"
 upButton.Text=flightUp and "UP: STOP" or "FLY UP";downButton.Text=flightDown and "DOWN: STOP" or "FLY DOWN"
 local now=os.clock();if now-flightSentAt<.1 then return end;flightSentAt=now
 local x,z,y=0,0,0
 if flightFocused and not UIS:GetFocusedTextBox() and not GuiService.MenuIsOpen then
  x=(UIS:IsKeyDown(Enum.KeyCode.D) and 1 or 0)-(UIS:IsKeyDown(Enum.KeyCode.A) and 1 or 0)
  z=(UIS:IsKeyDown(Enum.KeyCode.W) and 1 or 0)-(UIS:IsKeyDown(Enum.KeyCode.S) and 1 or 0)
  y=((flightUp or UIS:IsKeyDown(Enum.KeyCode.Space)) and 1 or 0)-((flightDown or UIS:IsKeyDown(Enum.KeyCode.LeftControl)) and 1 or 0)
  if x==0 and z==0 then
   local c=p.Character;local h=c and c:FindFirstChildOfClass("Humanoid");local root=c and c:FindFirstChild("HumanoidRootPart")
   if h and root then
    local mx=h.MoveDirection:Dot(root.CFrame.RightVector);local mz=h.MoveDirection:Dot(root.CFrame.LookVector)
    x=math.abs(mx)>.2 and (mx>0 and 1 or -1) or 0;z=math.abs(mz)>.2 and (mz>0 and 1 or -1) or 0
   end
  end
 end
 action:FireServer("FlightInput",{x=x,y=y,z=z})
end)
ownClient(function() if p:GetAttribute("TestFlight")==true then action:FireServer("FlightStop") end end)
-- Everyone sees the same navigation; authorized test controls sit below it.
-- Keep a separate view: modal renders replace mapDot but never this HUD map.
local miniMapButton=button(gui,"MiniMap","MAP",UDim2.fromOffset(112,132),UDim2.new(1,-126,0,14),function() toggleTab("Map") end)
miniMapButton.TextSize=12;miniMapButton.TextYAlignment=Enum.TextYAlignment.Top;miniMapButton.Visible=false
do
 local miniMapPadding=Instance.new("UIPadding");miniMapPadding.PaddingTop=UDim.new(0,10);miniMapPadding.Parent=miniMapButton
end
local miniMapHolder=frame(miniMapButton,"MiniMapHolder",UDim2.new(1,-16,1,-42),UDim2.fromOffset(8,34));miniMapHolder.BackgroundTransparency=1
local miniMapView=CityMap.create(miniMapHolder,true)
local miniMapAvailable=false
-- Hide the HUD map before menu dispatch/render; keep normal restoration frame-owned.
function academy.hideMiniMapForMenu()
 miniMapButton.Visible=false
 CityMap.MiniUpdate(miniMapView,nil,os.clock(),false)
end
local function card(height)
 local c=frame(content,"Card",UDim2.new(1,-8,0,height),UDim2.new(),panel)
 local edge=Instance.new("UIStroke");edge.Color=Color3.fromRGB(64,91,125);edge.Transparency=.65;edge.Parent=c
 return c
end
local function info(text,height) local width=math.min(720,gui.AbsoluteSize.X-24)-76;local fit=TextService:GetTextSize(text,15,Enum.Font.GothamMedium,Vector2.new(width,10000)).Y+24;local c=card(math.max(height or 70,fit));label(c,text,UDim2.new(1,-28,1,-20),UDim2.fromOffset(14,10),15);return c end
ownClient(function() modal.Visible=false;renderedMenuKey=nil;renderRevision+=1 end)
-- Guidance is session-local and can only be selected by an explicit button.
academy.NavigationCatalog=loadClientDependency(shared,"NavigationCatalog");if not clientCheckpoint() then return end
academy.TrainingRules=loadClientDependency(shared,"TrainingRules");if not clientCheckpoint() then return end
academy.BossCatalog=loadClientDependency(shared,"BossCatalog");if not clientCheckpoint() then return end
academy.NavigationGuide=loadClientDependency(script.Parent,"NavigationGuide");if not clientCheckpoint() then return end
academy.guide=academy.NavigationGuide.new(gui)
ownClient(function() academy.guide:Destroy() end);if not clientCheckpoint() then return end
academy.guidePanel=frame(gui,"SelectedGuide",UDim2.fromOffset(290,62),UDim2.fromOffset(16,120));academy.guidePanel.Visible=false
academy.surface(academy.guidePanel)
academy.guideText=label(academy.guidePanel,"",UDim2.new(1,-86,1,-8),UDim2.fromOffset(6,4),12)
academy.clearGuide=function()
 academy.guideSelection=nil;academy.guideTarget=nil;academy.marPosition=nil;academy.guide:Clear();academy.guidePanel.Visible=false
 renderedMenuKey=nil
end
button(academy.guidePanel,"ClearGuide","CLEAR",UDim2.fromOffset(72,44),UDim2.new(1,-78,.5,-22),academy.clearGuide)
function academy.resolveGuide(kind,id)
 if kind~="mar" then return academy.NavigationCatalog.Resolve(kind,id,data) end
 local area=academy.NavigationCatalog.Resolve("place","gardens",data)
 if not area then return nil end
 local position=academy.marPosition
 return {position=position or area.position,label=position and "Mar Soler" or "Mar's work area"}
end
academy.refreshGuide=function()
 local selection=academy.guideSelection
 if not selection then return end
 local target=academy.resolveGuide(selection.kind,selection.id)
 if not target then academy.clearGuide();return end
 local previous=academy.guideTarget
 local moving=selection.kind=="mar" and previous~=nil
 if moving and previous.label==target.label and (previous.position-target.position).Magnitude<3 then return end
 if not previous or previous.position~=target.position or previous.label~=target.label then
  academy.guideTarget=target;academy.guide:SetTarget(target,moving)
 end
end
function academy.refreshMarGuide(playerRoot,residents)
 if not academy.guideSelection or academy.guideSelection.kind~="mar" then return end
 academy.marPosition=nil
 for _,resident in ipairs(residents) do
  if resident.Parent and resident:GetAttribute("DisplayName")=="Mar Soler" and resident:GetAttribute("ResidentActive")~=false then
   local root=resident:FindFirstChild("HumanoidRootPart")
   local humanoid=resident:FindFirstChildOfClass("Humanoid")
   if playerRoot and root and humanoid and humanoid.Health>0 and (root.Position-playerRoot.Position).Magnitude<=90 then
    academy.marPosition=root.Position;break
   end
  end
 end
 academy.refreshGuide()
end
function academy.refreshTrainingGuide(residents)
 local selection=academy.guideSelection
 academy.trainingGuideFighter=nil
 if not selection or selection.kind~="place" or selection.id~="training" then return end
 local tier=academy.TrainingRules.Recommended(data.level).id
 for _,resident in ipairs(residents) do
  if resident.Parent and resident:GetAttribute("TrainingTier")==tier then
   academy.trainingGuideFighter=resident
   return
  end
 end
end
academy.selectGuide=function(kind,id)
 if not academy.resolveGuide(kind,id) then return end
 if kind~="mar" then academy.marPosition=nil
 elseif not academy.guideSelection or academy.guideSelection.kind~="mar" then academy.guideTarget=nil end
 academy.guideSelection={kind=kind,id=id};academy.refreshGuide();renderedMenuKey=nil
end
function academy.canGuideTraining()
 return Config.CompactCity==true and not data.activeQuest and not academy.guideSelection
end
academy.trainingGuideButton=button(tracked,"GuideTraining","GUIDE",UDim2.fromOffset(78,44),UDim2.new(1,-78,.5,-22),function()
 if academy.trainingGuideButton.Visible and academy.canGuideTraining() then academy.selectGuide("place","training") end
end)
academy.trainingGuideButton.TextColor3=gold
academy.trainingGuideButton.Visible=false
academy.guideMenu=function()
 local c=card(110)
 label(c,academy.guideTarget and ("GUIDING: "..academy.guideTarget.label) or "Choose a guide below. Nothing is selected automatically.",UDim2.new(1,-28,0,48),UDim2.fromOffset(14,6),14,gold)
 button(c,"ClearGuide","CLEAR GUIDE",UDim2.fromOffset(140,44),UDim2.fromOffset(14,58),function() academy.clearGuide();render() end)
end
-- On landscape phones the left rail may have no room above touch controls.
function academy.trackerLayout(viewport,touch,defaultY)
 local w,h=viewport.X,viewport.Y
 local canShare=touch and w>h and h>=315 and h<346 and w-274>=314 and defaultY+50<=h-102
 if touch and h>=239 and h<346 and w>h and not canShare then
  -- Keep the Guide target out of the stock movement frame and clear of Jump.
  local left,right=math.ceil(w*.4)+8,w-103
  local width=math.min(290,right-left)
  if width>=196 then
   return math.floor((left+right-width)/2),math.max(defaultY,h-91),width,60,true,true
  end
 end
 if not touch and h>=defaultY+68 and defaultY+50>h-102 then
  local width=math.min(290,w-274-8-16)
  if width>=212 then return 16,defaultY,width,60,true end
 end
 return 16,defaultY,290,50,canShare
end
academy.guideLayout=function(viewport,touch,trackedY)
 local w,h=viewport.X,viewport.Y
 if w>=230 and trackedY+118<h-(touch and 260 or 120) then
  return 16,trackedY+56,math.min(290,w-32),62,false
 end
 local left,right=264,w-182 -- retain space for the HUD and widest minimap
 local width=math.min(244,right-left)
 if h>=346 and width>=194 then
  return math.floor((left+right-width)/2),48,width,48,true
 end
end
function academy.starterCoinAction(data)
 if Config.ResonanceLayout then return end
 if not academy.NavigationCatalog.Resolve("place","gardens",data) then return end
 local canGuide=false
 local unlocked
 for _,id in ipairs({"garden","beach"}) do
  local quest=Config.GetQuest(id)
  local progress=(data.quests or {})[id]
  if quest and not quest.retired and not (progress and progress.claimed) then
   local active=data.activeQuest==id
   if (active or (data.availableQuests or {})[id]) and (progress and progress.progress or 0)>=quest.goal then return "claim" end
   canGuide=true
   if not unlocked and (data.availableQuests or {})[id] then unlocked=id end
  end
 end
 local active=data.activeQuest
 if (active=="garden" or active=="beach") and academy.NavigationCatalog.Resolve("quest",active,data) then return "objective" end
 if canGuide and not active then
  if unlocked then return "quest",unlocked end
  return "guide"
 end
end
local function menuKey()
 local fields
 if selected=="Screams" then fields={level=data.level,sound=data.sound,amplifier=data.amplifierEquipped,megaphone=data.megaphoneEquipped}
 elseif selected=="Quests" then fields={quests=data.quests,active=data.activeQuest,available=data.availableQuests,navigation=data.questNavigation,challenges=data.combatChallenges,level=data.level}
 elseif selected=="Style" then
  local starterAction,starterQuest=academy.starterCoinAction(data)
  fields={gearOwned=data.gearOwned,gearEquipped=data.gearEquipped,level=data.level,coins=data.coins,aura=data.aura,custom=data.customColor,customEquipped=data.useCustomColor,pass=data.spectrumPass,owned=data.amplifierOwned,equipped=data.amplifierEquipped,megaphoneOwned=data.megaphoneOwned,megaphoneEquipped=data.megaphoneEquipped,starterAction=starterAction,starterQuest=starterQuest}
 elseif selected=="Shop" then fields={compactLandscape=ShopUI.CompactLandscape(gui.AbsoluteSize.X,gui.AbsoluteSize.Y),spectrum=data.spectrumPass,movement=data.movementPass,inventory=data.shop and data.shop.inventory,ends=data.shop and data.shop.ends,ready=data.shop and data.shop.ready,saving=data.savingAvailable}
 elseif selected=="Settings" then fields={settings=data.settings,micStatus=mic.status,micEligible=mic.eligible,micPending=mic.checkPending}
 elseif selected=="Map" then fields={level=data.level,height=Config.ResonanceLayout and content.AbsoluteWindowSize.Y or nil}
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
 -- Card callbacks belong to this visible render, not a later reopened panel.
 local makeButton=button
 local function button(parent,name,text,size,pos,callback,color)
  return makeButton(parent,name,text,size,pos,function(...)
   if clientDestroyed or not modal.Visible or revision~=renderRevision then return end
   return callback(...)
  end,color)
 end
 clearShop()
 mapDot=nil
 narrow=gui.AbsoluteSize.X-24<620
 for _,c in ipairs(content:GetChildren()) do if c:IsA("GuiObject") then c:Destroy() end end
 for name,b in pairs(tabs) do b.BackgroundColor3=name==selected and Color3.fromRGB(64,93,99) or panel end
 if selected=="Shop" then
  title.Text="THE AMPLIFIER";subtitle.Text="SIGNATURE COLORS / POWER YOUR PROGRESS"
  shopUsed=true;ShopUI.Render(data,{card=card,frame=frame,label=label,button=button,info=info,narrow=narrow,compactLandscape=ShopUI.CompactLandscape(gui.AbsoluteSize.X,gui.AbsoluteSize.Y)},action)
 elseif selected=="Screams" then
  title.Text="BEAM COLLECTION"
  local nextStyle
  for _,style in ipairs(Config.Sounds) do
   if style.level>data.level and (not nextStyle or style.level<nextStyle.level) then nextStyle=style end
  end
  local milestone=card(70)
  milestone.Name="BeamMilestone"
  local heading=sustainedRules and "BEAM SOUNDS" or "BEAM STYLES"
  if nextStyle then heading=sustainedRules and "NEXT SOUND" or "NEXT STYLE" end
  local detail=nextStyle and (nextStyle.name.." · Lv "..nextStyle.level) or "All unlocked"
  local gearWidth=narrow and 92 or 112
  local textInset=gearWidth+38
  label(milestone,heading,UDim2.new(1,-textInset,0,19),UDim2.fromOffset(14,8),12,gold)
  label(milestone,detail,UDim2.new(1,-textInset,0,34),UDim2.fromOffset(14,28),15)
  button(milestone,"OpenBeamGear","VIEW GEAR",UDim2.fromOffset(gearWidth,44),UDim2.new(1,-gearWidth-14,.5,-22),function() toggleTab("Style") end)
  local maximum=Config.VoiceCombat.Stats(data.level,1,data.amplifierEquipped,data.megaphoneEquipped,data.gearMultiplier)
  local combatSummary=sustainedRules and string.format("CURRENT BEAM · LEVEL %d\nFULL-POWER LIMITS: %.1f DPS · %.2f studs",data.level,maximum.maxDps,maximum.maxRange)
   or string.format("CURRENT BEAM · LEVEL %d\nFULL-POWER LIMITS: %d damage · %.2f studs",data.level,maximum.damage,maximum.maxRange)
  if nextStyle then
   local nextStats=Config.VoiceCombat.Stats(nextStyle.level,1,false)
   local forecast=sustainedRules and string.format("%.1f max DPS",nextStats.maxDps) or (nextStats.damage.." damage")
   combatSummary..=string.format("\nAT LEVEL %d: %d HP · %s",nextStyle.level,nextStats.health,forecast)
  end
  info(combatSummary,narrow and 112 or 82)
  info("Sound styles change audio, not damage or range. These limits use your current level for the next attack. Lower voice power and cover shorten reach. DPS requires full power and continuous contact.",narrow and 150 or 96)
  for _,s in ipairs(Config.Sounds) do
   local c=card(sustainedRules and (narrow and 108 or 64) or (narrow and 150 or 76));label(c,s.name.."  /  LEVEL "..s.level,UDim2.new(1,narrow and -28 or -156,0,(narrow or sustainedRules) and 44 or 26),UDim2.fromOffset(14,8),17,gold)
   if not sustainedRules then
   label(c,s.description,UDim2.new(1,narrow and -28 or -158,0,narrow and 40 or 25),UDim2.fromOffset(14,narrow and 54 or 36),13)
   end
   local unlocked=data.level>=s.level
   local b=button(c,s.id,data.sound==s.id and "EQUIPPED" or unlocked and "EQUIP" or "LEVEL "..s.level,UDim2.fromOffset(116,37),UDim2.new(1,-130,0,sustainedRules and (narrow and 60 or 14) or (narrow and 102 or 21)),function() if unlocked then action:FireServer("EquipSound",s.id) end end)
   if not unlocked then b.TextColor3=muted end
  end
 elseif selected=="Quests" and Config.ResonanceLayout then
  title.Text="RESONANCE HALL";subtitle.Text="Local PvP playtest"
  info("Fight in the Hall. The cyan apron is safe. Use the Training City portal to leave and the return portal to come back.",98)
 elseif selected=="Quests" then
  title.Text="QUESTS & COMBAT";subtitle.Text="Beam combat first. One active task."
  local current=Config.GetQuest(data.activeQuest)
  local function readyToClaim(quest)
   if not quest then return false end
   local available=quest==current or quest.retired==true or quest.menuAvailable==true or (data.availableQuests and data.availableQuests[quest.id])
   local progress=available and data.quests[quest.id]
   return progress and not progress.claimed and progress.progress>=quest.goal
  end
  local reward=readyToClaim(current) and current or nil
  if not reward then
   for _,quest in ipairs(Config.Quests) do
    if readyToClaim(quest) then reward=quest;break end
   end
  end
  if reward then
   local payout=data.level>=Config.MaxLevel and (reward.coins.." coins (base)")
    or string.format("%d coins · %d XP (base)",reward.coins,reward.xp)
   local textBounds=Vector2.new(math.max(1,math.min(720,gui.AbsoluteSize.X-24)-206),10000)
   local nameHeight=math.max(19,TextService:GetTextSize(reward.name,15,Enum.Font.GothamMedium,textBounds).Y+2)
   local payoutHeight=math.max(16,TextService:GetTextSize(payout,12,Enum.Font.GothamMedium,textBounds).Y+2)
   local c=card(math.max(60,nameHeight+payoutHeight+18))
   label(c,reward.name,UDim2.new(1,-158,0,nameHeight),UDim2.fromOffset(14,8),15,gold)
   label(c,payout,UDim2.new(1,-158,0,payoutHeight),UDim2.fromOffset(14,nameHeight+10),12,muted)
   local actionName=reward==current and not reward.retired and "ActiveQuestAction" or "ReadyQuestAction"
   button(c,actionName,"CLAIM",UDim2.fromOffset(116,44),UDim2.new(1,-130,0,1),function()
    action:FireServer("ClaimQuest",reward.id)
   end)
  end
  academy.guideMenu()
  local padLocation=Config.CompactCity and "north of Academy spawn" or "in the west courtyard"
  info("COURTYARD TRAINING · "..(data.training or "Rookie").." recommended\nThree sparring pads "..padLocation..". Hit a fighter to start. Move out of red strikes or dodge. No PvP on the pads; training fighters can knock you out.")
  for _,spec in ipairs(Config.Progression.Challenges) do
   local rewardText=data.level>=Config.MaxLevel and "MAX LEVEL · no XP awarded" or ("+"..Config.Progression.ChallengeXP(data.level).." XP on completion")
   info(spec.name.." · "..((data.combatChallenges or {})[spec.id] or 0).."/"..spec.goal.."\n"..rewardText.." · renews automatically",68)
  end
  info("Training: contribute at least 10% damage. You must be no more than 20 levels above the fighter's reward band (Rookie 1-24, Brawler 25-59, Elite 60-100). Each qualifying KO or assist counts once. Environment cover is static. PvP XP is shared by damage; weak and repeated opponents pay less.")
  if data.activeQuest and not (current and current.retired==true) and (not reward or current~=reward) then
   local c=card(96)
   label(c,"CURRENT: "..(current and current.name or data.activeQuest),UDim2.new(1,-28,0,38),UDim2.fromOffset(14,6),14,gold)
   button(c,"ActiveQuestAction","ABANDON",UDim2.fromOffset(116,38),UDim2.new(1,-130,0,50),function()
    action:FireServer("AbandonQuest")
   end)
  end
  local currentProgress=current and data.quests[current.id]
  local unfinished=current and not current.retired and not (currentProgress and (currentProgress.claimed or currentProgress.progress>=current.goal))
  local combatEvents={Crowd=true,Evade=true,Underdog=true,PracticeBeam=true,ArenaAssist=true}
  local questGroups={{title="BEAM COMBAT TASKS",combat=true},{title="OPTIONAL CITY ACTIVITIES",combat=false}}
  for _,group in ipairs(questGroups) do
   local headingShown=false
   for _,q in ipairs(Config.Quests) do
    if (combatEvents[q.event]==true)~=group.combat then continue end
    local v=data.quests[q.id] or {progress=0}
    if q.retired==true and (v.claimed or v.progress<q.goal) then continue end
    local available=q.retired==true or q.menuAvailable==true or (data.availableQuests and data.availableQuests[q.id])
    if q.hidden and not available then continue end
    if not headingShown then info(group.title,50);headingShown=true end
    local restarting=available and not v.claimed and v.progress>0 and v.progress<q.goal and data.activeQuest~=q.id
    local switching=unfinished and q~=current and available and not q.retired and not v.claimed and v.progress<q.goal
    local description=q.retired==true and "Earned reward available." or q.description
    if switching then description..="\n\nReplaces "..current.name..". Unfinished progress resets." end
    if restarting then description..="\n\nRestarting resets this unfinished progress." end
    if not available then description..="\n\nTo unlock: meet "..(q.giver or "a resident").." and use Talk." end
    local textWidth=math.min(720,gui.AbsoluteSize.X-24)-48-(narrow and 28 or 158)
    local nameHeight=math.max(26,TextService:GetTextSize(q.name,17,Enum.Font.GothamMedium,Vector2.new(textWidth,10000)).Y+4)
    local descriptionHeight=math.max(49,TextService:GetTextSize(description,13,Enum.Font.GothamMedium,Vector2.new(textWidth,10000)).Y+8)
    local descriptionY=12+nameHeight;local rewardY=descriptionY+descriptionHeight+5
    local actionY=narrow and rewardY+34 or 32
    local canGuide=academy.NavigationCatalog.Resolve("quest",q.id,data)~=nil
    local guideToMar=not available and (q.id=="garden" or q.id=="beach") and academy.NavigationCatalog.Resolve("place","gardens",data)~=nil
    local c=card(narrow and actionY+(canGuide and 100 or guideToMar and 54 or 48) or math.max(canGuide and 164 or 150,rewardY+35))
    if q.id==academy.menuQuestFocus then c.LayoutOrder=-1 end
    label(c,q.name,UDim2.new(1,narrow and -28 or -150,0,nameHeight),UDim2.fromOffset(14,8),17,gold)
    label(c,description,UDim2.new(1,narrow and -28 or -158,0,descriptionHeight),UDim2.fromOffset(14,descriptionY),13)
    label(c,v.progress.." / "..q.goal.."   •   +"..q.xp.." XP   •   +"..q.coins.." coins",UDim2.new(1,-28,0,30),UDim2.fromOffset(14,rewardY),12,muted)
    button(c,q.id,guideToMar and "GUIDE TO MAR" or not available and "MEET NPC" or v.claimed and "CLAIMED" or v.progress>=q.goal and "CLAIM" or data.activeQuest==q.id and "ACTIVE" or switching and "SWITCH" or restarting and "RESTART" or "ACCEPT",UDim2.fromOffset(116,switching and 44 or (guideToMar and 44 or 38)),UDim2.new(1,-130,0,actionY),function()
     if guideToMar then academy.selectGuide("mar","gardens");closeMenu();return end
     if available and not v.claimed and (v.progress>=q.goal or data.activeQuest~=q.id) then action:FireServer(v.progress>=q.goal and "ClaimQuest" or "AcceptQuest",q.id) end
    end)
    if canGuide then
     button(c,"Guide_"..q.id,"GUIDE",UDim2.fromOffset(116,44),UDim2.new(1,-130,0,actionY+46),function()
      academy.selectGuide("quest",q.id);closeMenu()
     end)
    end
   end
  end
 elseif selected=="Style" then
  title.Text="GEAR & BEAM COLOR";subtitle.Text=Config.ResonanceLayout and "Earn gear with coins from PvP." or "Earn gear with coins from training and quests."
  local selectedGear=Config.Gear.Selected(data)
  local compactGear=narrow and gui.AbsoluteSize.X>=500
  local function gearCard(item,starter)
   local owned=Config.Gear.Owned(data,item.id)
   local locked=data.level<item.level
   local remaining=owned and 0 or math.max(0,item.price-data.coins)
   local canAct=not locked and remaining==0
   local equipped=selectedGear and selectedGear.id==item.id
   local canBuy=canAct and not owned
   local coinAction=starter and not locked and remaining>0 and academy.starterCoinAction(data) or nil
   local shortfall="NEED "..remaining.." COINS"
   local stateText=locked and ("LEVEL "..item.level) or equipped and "UNEQUIP" or owned and "EQUIP"
    or coinAction=="claim" and ("VIEW REWARDS\n"..shortfall) or coinAction=="guide" and ("GUIDE TO MAR\n"..shortfall)
    or coinAction=="objective" and ("GUIDE QUEST\n"..shortfall)
    or coinAction=="quest" and ("VIEW QUEST\n"..shortfall)
    or remaining>0 and shortfall or ("BUY & EQUIP\n"..item.price.." COINS")
   local c=card(compactGear and 72 or narrow and 116 or 110)
   label(c,string.upper(item.name),UDim2.new(1,narrow and -168 or -28,0,compactGear and 20 or narrow and 44 or 28),UDim2.fromOffset(15,6),16,gold)
   local status=equipped and "Equipped · " or owned and "Owned · " or not canBuy and (item.price.." coins · ") or ""
   local detail=string.format("Level %d · +%d%% mic power\n%s%d coins in wallet",item.level,math.floor(item.bonus*100+.5),status,data.coins)
   if starter and not canAct then
    detail..=Config.ResonanceLayout and "\nEarn coins from PvP KOs" or coinAction=="claim" and "\nClaim coins in Quests" or coinAction=="guide" and "\nEarn coins with Mar's quests" or coinAction=="objective" and "\nFollow your current quest" or coinAction=="quest" and "\nOpen an unlocked quest" or "\nEarn coins from training or quests"
   end
   label(c,detail,UDim2.new(1,narrow and not compactGear and -28 or -170,0,compactGear and 42 or 48),UDim2.fromOffset(15,compactGear and 26 or narrow and 57 or 34),13)
   local control=button(c,item.id,stateText,UDim2.fromOffset(135,44),UDim2.new(1,-149,0,narrow and 6 or 50),function()
    if canAct then
     action:FireServer("Gear",{id=item.id,intent=canBuy and "buy" or equipped and "unequip" or "equip"});return
    end
    local currentAction,questId=academy.starterCoinAction(data)
    if coinAction and currentAction==coinAction then
     if coinAction=="claim" then toggleTab("Quests",true)
     elseif coinAction=="objective" then academy.selectGuide("quest",data.activeQuest);closeMenu()
     elseif coinAction=="quest" then toggleTab("Quests",true,questId)
     else academy.selectGuide("mar","gardens");closeMenu() end
    end
   end)
   control.Interactable=canAct or coinAction~=nil
   if not control.Interactable then control.TextColor3=muted end
  end
  local starter=Config.Gear.Get("Megaphone")
  local nextUpgrade=academy.nextGearUpgrade
  if nextUpgrade then gearCard(nextUpgrade,false) end
  if starter then gearCard(starter,true) end
  shopUsed=true;ShopUI.ColorMixer(data,{card=card,frame=frame,label=label,button=button},action)
  info("Earned-coin gear · one active bonus · normalized power capped at 100%. Buy once, then equip freely.",90)
  for _,item in ipairs(Config.Gear.Items) do
   if item~=starter and item~=nextUpgrade then gearCard(item,false) end
  end
  info("Movement pass: repeated jumps (24-stud height limit) and consecutive rolls only in safe areas. Arena cooldowns always apply."..(Config.MovementPassId==0 and " Purchase setup is not available yet." or ""),70)
  local base=card(76)
  label(base,"YELLOW BASE",UDim2.new(1,-158,0,48),UDim2.fromOffset(15,10),17,Config.Auras.Gold)
  button(base,"BaseColor",data.aura=="Gold" and not data.useCustomColor and "EQUIPPED" or "USE YELLOW",UDim2.fromOffset(126,44),UDim2.new(1,-140,0,16),function() action:FireServer("SetAura","Gold") end)
  if data.aura~="Gold" and not data.useCustomColor then
   info("Your saved "..data.aura.." color is still equipped. Choosing yellow replaces this legacy selection; the old free palette is no longer selectable.")
  end
 elseif selected=="Map" then
  title.Text=Config.ResonanceLayout and "RESONANCE HALL" or "CITY & COAST"
  subtitle.Text=Config.ResonanceLayout and "Hall and training landing" or "Red: PvP • Pale café path: safe."
  local trainingTarget=academy.NavigationCatalog.Resolve("place","training",data)
  if trainingTarget then
   local trainingCard=card(narrow and 106 or 70)
   label(trainingCard,trainingTarget.label,UDim2.new(1,narrow and -28 or -160,0,44),UDim2.fromOffset(14,8),14,gold)
   button(trainingCard,"GuidePlace_training","GUIDE",UDim2.fromOffset(116,44),UDim2.new(1,-130,0,narrow and 54 or 13),function() academy.selectGuide("place","training");closeMenu() end)
  end
  local height=Config.ResonanceLayout and math.clamp(content.AbsoluteWindowSize.Y-4,78,300) or 300
  local c=card(height)
  local holder=frame(c,"MapHolder",UDim2.new(1,-26,1,-26),UDim2.fromOffset(13,13));holder.BackgroundTransparency=1
  mapDot=CityMap.create(holder)
  CityMap.update(mapDot,p.Character and p.Character:FindFirstChild("HumanoidRootPart"))
  info(CityMap.mapHelp,64)
  info(CityMap.legend,CityMap.legendHeight)
  info(CityMap.activityHelp,86)
  if Config.CompactCity~=false then
  academy.guideMenu()
  info("OPTIONAL DESTINATIONS · A guide does not accept quests, start fights or teleport you. Boss entry requires the listed minimum level.",90)
  for _,boss in ipairs(academy.BossCatalog.Entries) do
   local c=card(narrow and 112 or 72)
   label(c,boss.name.." · MIN LEVEL "..boss.level,UDim2.new(1,narrow and -28 or -160,0,48),UDim2.fromOffset(14,6),14,gold)
   button(c,"GuideBoss_"..boss.id,"GUIDE",UDim2.fromOffset(116,44),UDim2.new(1,-130,0,narrow and 60 or 14),function() academy.selectGuide("boss",boss.id);closeMenu() end)
  end
  for _,place in ipairs(academy.NavigationCatalog.Places) do
   if place.id=="training" then continue end
   local c=card(70)
   label(c,place.label,UDim2.new(1,-160,0,50),UDim2.fromOffset(14,10),14)
   button(c,"GuidePlace_"..place.id,"GUIDE",UDim2.fromOffset(116,44),UDim2.new(1,-130,0,13),function() academy.selectGuide("place",place.id);closeMenu() end)
  end
  end
 else
  title.Text="SETTINGS & CONTROLS";subtitle.Text="Keep the action comfortable and easy to read."
  if academy.damageReadout.available then
   local recapCard=card(74);local recapToggle
   local function recapLabel() return "COMBAT STATS: "..(academy.damageReadout.enabled and "ON" or "OFF") end
   recapToggle=button(recapCard,"CombatStats",recapLabel(),UDim2.new(1,-24,0,44),UDim2.fromOffset(12,6),function()
    academy.damageReadout:SetEnabled(not academy.damageReadout.enabled);recapToggle.Text=recapLabel()
   end)
   local note=label(recapCard,"Live DPS and fight total · this session",UDim2.new(1,-24,0,20),UDim2.fromOffset(12,50),12,muted)
   note.TextXAlignment=Enum.TextXAlignment.Center
  end
  local touch=UIS.TouchEnabled
  local attackHelp
  if sustainedControl then
   attackHelp=string.format("Beams start OFF. BEAMS ON: normal speech can fire attacks. Aim, then speak; %.0fs max, %.0fs cooldown.\n%s toggles attacks. OFF lets you talk; voice chat is unchanged. Go quiet before each beam.",sustainedRules.MaxDuration,sustainedRules.Cooldown,touch and "Tap BEAMS" or "E / BEAMS")
  else attackHelp=touch and "Hold BEAM, speak into your mic, then release to fire toward the center of your view." or "Hold E / BEAM, speak into your mic, then release to fire toward your aim." end
  info(attackHelp,touch and 130 or 100)
  info("VOICE SAFETY\nAvoid profanity. Roblox's profanity rules depend on the game's rating and settings; harassment, threats and hate speech are not allowed. Rule violations may restrict voice or your account.\nRoblox records voice for moderation. The beam mechanic reads volume, not words. Stopping attacks does not mute voice. Use Roblox's mic control to mute, or Report Abuse for violations.",100)
  info(string.format("Third-person camera\n%s: dodge (W/A/S/D) · %.0fs arena cooldown\n%s: %.0fs moving sprint; %.0fs rest when empty. Refill starts after %.0fs without sprint.",touch and "DODGE" or "Q / DODGE",Config.DodgeCooldown,touch and "SPRINT" or "Shift / SPRINT",Config.SprintDuration,Config.SprintRecovery,Config.SprintRegenDelay),touch and 130 or 110)
  if Config.ResonanceLayout then
   info(touch and "Touch and hold the portal prompt to travel. Open MAP from MENU." or "F: hold to use a portal · M: map · B: toggle menu",touch and 80 or 54)
  else
   info(touch and "Tap TALK near a resident. Follow the on-screen quest prompts. Tap MENU to open the tabs or X to close them." or "T: talk · F: quest interactions · M: map · B: toggle menu",touch and 80 or 54)
  end
  info("MICROPHONE\n"..mic.status,60)
  if not mic.eligible and not mic.checkPending then
   local accessCard=card(64)
   button(accessCard,"RetryVoiceAccess","RETRY VOICE ACCESS",UDim2.new(1,-24,0,44),UDim2.fromOffset(12,10),function()
    if not mic.eligible and not mic.checkPending then mic:Check() end
   end)
  end
  local c=card(58);button(c,"Volume","CITY AUDIO: "..math.floor(data.settings.volume*100).."%",UDim2.new(1,-24,0,38),UDim2.fromOffset(12,10),function() action:FireServer("SetSettings",{volume=data.settings.volume>=.99 and 0 or math.min(1,data.settings.volume+.25)}) end)
  local audioCard=card(58);local audioButton
  local function audioLabel()return "BEAM SFX: "..attackAudio.level end
  audioButton=button(audioCard,"AttackAudio",audioLabel(),UDim2.new(1,-24,0,38),UDim2.fromOffset(12,10),function()
   attackAudio:SetLevel(attackAudio.level=="NORMAL" and "LOW" or attackAudio.level=="LOW" and "OFF" or "NORMAL");audioButton.Text=audioLabel()
  end)
  info("NORMAL boosts effects; LOW keeps the old mix; OFF mutes them. Starter beam has no SFX. Session only; mic and voice chat unchanged.",narrow and 100 or 68)
  local cueCard=card(58);local cueButton
  local function cueLabel()return "GAMEPLAY SFX: "..(not gameplayAudio.enabled and "OFF" or "LOW") end
  cueButton=button(cueCard,"GameplayAudio",cueLabel(),UDim2.new(1,-24,0,38),UDim2.fromOffset(12,10),function()
   gameplayAudio:SetEnabled(not gameplayAudio.enabled);cueContext();cueButton.Text=cueLabel()
  end)
  info("This also mutes boss warnings. Packaged boss fallbacks play only when available; custom hit/dodge/level cues still await upload.",72)
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
academy.menuTabs={"Style","Screams","Quests","Shop","Map","Settings"}
for i,name in ipairs(academy.menuTabs) do
 local tabText=name=="Style" and "GEAR" or name=="Screams" and "BEAMS" or name=="Quests" and Config.ResonanceLayout and "RULES" or name:upper()
 tabs[name]=button(modal,name,tabText,UDim2.fromOffset(126,34),UDim2.fromOffset(20+(i-1)*134,88),function()
  if clientDestroyed or not modal.Visible then return end
  if selected~=name then toggleTab(name) end
 end)
 local icon,padding=academy.tabIcon(tabs[name],name);academy.tabIcons[name]={icon=icon,padding=padding}
end
local conversationNPC,conversationUntil
local conversationRevision=0
conversationPanel=frame(gui,"Conversation",UDim2.fromOffset(460,300),UDim2.fromScale(.5,.5));conversationPanel.AnchorPoint=Vector2.new(.5,.5);conversationPanel.Visible=false;conversationPanel.ZIndex=10
academy.surface(conversationPanel,gold)
local conversationName=label(conversationPanel,"",UDim2.new(1,-80,0,36),UDim2.fromOffset(18,12),19,gold)
local conversationList=Instance.new("ScrollingFrame");conversationList.Size=UDim2.new(1,-36,1,-66);conversationList.Position=UDim2.fromOffset(18,54);conversationList.BackgroundTransparency=1;conversationList.BorderSizePixel=0;conversationList.ScrollBarThickness=4;conversationList.AutomaticCanvasSize=Enum.AutomaticSize.Y;conversationList.CanvasSize=UDim2.new();conversationList.Parent=conversationPanel
do local conversationLayout=Instance.new("UIListLayout");conversationLayout.Padding=UDim.new(0,10);conversationLayout.SortOrder=Enum.SortOrder.LayoutOrder;conversationLayout.Parent=conversationList end
closeConversation=function()
 conversationRevision+=1
 if conversationPanel.Visible then action:FireServer("EndConversation") end
 conversationPanel.Visible=false;conversationNPC=nil
 academy.testLauncherBlocked=false;academy.refreshTestLauncher()
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
 academy.testLauncherBlocked=true;if academy.hideMiniMapForMenu then academy.hideMiniMapForMenu() end;academy.refreshTestLauncher();cancelCapture();closeMenu();if devPanel then devPanel.Visible=false end
 if info.name=="Mar Soler" and academy.guideSelection and academy.guideSelection.kind=="mar" then academy.clearGuide() end
 conversationRevision+=1;local revision=conversationRevision
 conversationNPC=info.npc;conversationUntil=os.clock()+20;conversationName.Text=info.name
 for _,child in ipairs(conversationList:GetChildren()) do if child:IsA("GuiObject") then child:Destroy() end end
 local order=0
 local function words(text,color)
  order+=1;local l=label(conversationList,text,UDim2.new(1,-10,0,0),UDim2.new(),14,color);l.AutomaticSize=Enum.AutomaticSize.Y;l.LayoutOrder=order;return l
 end
 local line=words(info.line,white)
 local function choice(text,callback)
  order+=1;local b=button(conversationList,"Choice",text,UDim2.new(1,-10,0,48),UDim2.new(),function(...)
   if clientDestroyed or not conversationPanel.Visible or revision~=conversationRevision then return end
   return callback(...)
  end);b.TextWrapped=true;b.LayoutOrder=order;return b
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
  local spec=Config.GetQuest(q.id);local progress=data.quests[q.id]
  local restarting=not q.claimed and not q.complete and spec and progress and progress.progress>0 and progress.progress<spec.goal and data.activeQuest~=q.id
  words(q.description..(restarting and "\n\nRestarting resets this unfinished progress." or ""),muted)
  local b=choice(q.claimed and (q.name.." · completed") or ((q.complete and "Claim: " or restarting and "Restart: " or "Accept: ")..q.name),function()
   if not q.claimed then action:FireServer(q.complete and "ClaimQuest" or "AcceptQuest",q.id);closeConversation() end
  end)
  b.Active=not q.claimed;b.AutoButtonColor=not q.claimed
  if academy.NavigationCatalog.Resolve("quest",q.id,data) then
   choice("Guide me: "..q.name,function() academy.selectGuide("quest",q.id);closeConversation() end)
  end
 end
 if Config.CompactCity~=false then choice("Choose a boss or place to guide me to",function() toggleTab("Map") end) end
 choice("See you later",closeConversation)
 conversationList.CanvasPosition=Vector2.zero;conversationPanel.Visible=true
 academy.testLauncherBlocked=false;academy.refreshTestLauncher()
end
local function refreshQuestObject(object)
 if not object:IsA("BasePart") then return end
 local action=object:GetAttribute("QuestAction")
 if action~="Litter" and action~="Garden" then return end
 local collected=data.collected and data.collected[object.Name]==true
 if action=="Litter" then object.LocalTransparencyModifier=collected and 1 or 0 end
 local prompt=object:FindFirstChildOfClass("ProximityPrompt")
 if prompt then prompt.Enabled=not collected end
end
local function refreshQuestObjects()
 local world=workspace:FindFirstChild("ScreamSimulatorWorld")
 local objects=world and world:FindFirstChild("QuestObjects")
 if not objects then return end
 for _,object in objects:GetChildren() do refreshQuestObject(object) end
end
-- Reapply this player's collection state if a marker loads after its state packet.
connectClient(game:GetService("ProximityPromptService").PromptShown,function(prompt)
 local object=prompt.Parent
 if not object or not data.collected or data.collected[object.Name]~=true then return end
 local world=workspace:FindFirstChild("ScreamSimulatorWorld")
 local objects=world and world:FindFirstChild("QuestObjects")
 if objects and object.Parent==objects then refreshQuestObject(object) end
end)
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
local starterGear={}
connectClient(remotes.State.OnClientEvent,function(nextData)
 observeVoiceEligibility(nextData)
 cueContext();gameplayAudio:ObserveLevel(nextData.level,nextData.testSession,os.clock())
 data=nextData
 if academy.refreshTesterTools then academy.refreshTesterTools() end
 p:SetAttribute("BossReducedEffects",not data.settings or data.settings.reducedShake~=false)
 academy.refreshGuide() -- Update only a destination the player already chose.
 local unclaimed=0
 for _,quest in ipairs(Config.Quests) do
  local progress=data.quests[quest.id]
  if progress and not progress.claimed and progress.progress>=quest.goal then unclaimed+=1 end
 end
 questsToggle.Text=unclaimed>0 and ("QUESTS "..unclaimed) or "QUESTS"
 questsToggle.TextColor3=unclaimed>0 and gold or white
 refreshQuestObjects();stats.Text="LEVEL "..data.level;coins.Text=data.coins.." coins";refreshHealth()
 xpText.Text=progressLabel(gui.AbsoluteSize.X<820);xf.Size=UDim2.fromScale(data.level>=Config.MaxLevel and 1 or data.xp/data.xpNext,1)
 academy.refreshZone()
 academy.refreshTestLauncher()
 local q=Config.GetQuest(data.activeQuest);local v=q and data.quests[q.id]
 local trainingHint=Config.CompactCity==true and "" or " · west courtyard"
 local challengeHint=Config.CompactCity==true and "" or " · Quests for challenges"
 tracked.Text=q and (q.name.."\n"..(data.questStep or "").."\n"..(v and v.progress or 0).."/"..q.goal..(data.questTime>0 and "  •  "..data.questTime.."s left" or "")) or ("Train: "..(data.training or "Rookie")..trainingHint.."\nFighters "..((data.combatChallenges or {}).fighters or 0).."/3"..challengeHint)
 trackedQuestText=tracked.Text
 if data.savingAvailable==true and not data.savingDelayed then notifications:Remove("save") end
 local newMilestone=data.milestone and data.milestone~=lastMilestone
 if newMilestone then
  lastMilestone=data.milestone;notify(data.milestone)
 end
 if data.message and (not newMilestone or data.messageUrgent) then notify(data.message,data.messageUrgent,data.messageKey=="save" and "save" or nil) end
 if Config.CompactCity and not Config.ResonanceLayout then
  local item=Config.Gear.Get("Megaphone")
  local ready=item and not data.testSession and data.level>=item.level
   and data.coins>=item.price and not Config.Gear.Owned(data,item.id)
  if not ready then
   starterGear.pending=nil
   notifications:Remove("starterGear")
  elseif not starterGear.shown and starterGear.lastCoins and starterGear.lastCoins<item.price then
   starterGear.pending=item.name.." ready to buy · MENU → GEAR"
  end
  starterGear.lastCoins=not data.testSession and data.coins or nil
 end
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
connectClient(p.CharacterRemoving,function() academy.defenderCueUntil=nil;academy.attackCueUntil=nil;academy.incomingHit.Visible=false;hitFeedback:DiscardThrough(sustainedControl and sustainedControl.sequence or hitFeedback.sequence);setSprint(false);if sustainedControl then sustainedControl:SetArmed(false) end;cancelCapture();if closeConversation then closeConversation() end end)
connectClient(UIS.WindowFocused,function() windowFocused=true end)
local function suspendGameplay()
 if sustainedControl then sustainedControl:SetArmed(false) end
 setSprint(false);cancelCapture()
end
connectClient(UIS.WindowFocusReleased,function() windowFocused=false;suspendGameplay() end)
connectClient(GuiService.MenuOpened,suspendGameplay)
connectClient(p:GetAttributeChangedSignal("ProtectionEnds"),function() setSprint(false) end)
;(function()
local function fxPart(position,color,size)
 local f=Instance.new("Part");f.Anchored=true;f.CanCollide=false;f.CanTouch=false;f.CanQuery=false;f.Material=Enum.Material.Neon;f.Color=color;f.Size=size;f.Position=position;f.Transparency=.3;f.Parent=workspace;Debris:AddItem(f,1.1);return f
end
local BeamVisuals=loadClientDependency(script.Parent,"BeamVisuals");if not clientCheckpoint() then return end
local beamVisualsUsed=false
-- Registered before the manager so reverse cleanup destroys owned rigs first.
ownClient(function() if beamVisualsUsed then BeamVisuals.Clear() end end)
local function createOwnedBeam(...)
 if clientDestroyed then return end
 beamVisualsUsed=true;return BeamVisuals.Create(...)
end
local beamFrame=0
local sustainedBeams
if sustainedControl then
 sustainedBeams=loadClientDependency(script.Parent,"SustainedBeams");if not clientCheckpoint() then return end
 sustainedBeams=sustainedBeams.new(createOwnedBeam,BeamVisuals.Update,BeamVisuals.Destroy)
 ownClient(function() sustainedBeams:Destroy() end);if not clientCheckpoint() then return end
 connectClient(p.CharacterRemoving,function() sustainedBeams:Clear() end)
 connectClient(p.CharacterRemoving,function() attackAudio:Clear() end)
 connectClient(Players.PlayerRemoving,function(leaving) sustainedBeams:Remove(leaving.UserId);sustainedBeams:Remove("test:"..tostring(leaving.UserId)) end)
 connectClient(Players.PlayerRemoving,function(leaving) attackAudio:Remove(leaving.UserId) end)

end
connectClient(remotes.Effect.OnClientEvent,function(kind,pos,id,aura,direction,length,beamWidth,audioStyleId,attackLevel)
 -- The test packet deliberately returns before all attack/gameplay audio paths.
 if kind=="TestBeamEnd" then
  if sustainedBeams then sustainedBeams:Remove("test:"..tostring(id)) end
  return
 end
 if kind=="TestBeam" then
  if not academy.testToolsAllowed() or not sustainedBeams then return end
  local key="test:"..tostring(id)
  local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
  if not Players:GetPlayerByUserId(id) or not root or (root.Position-pos).Magnitude>180 or length<.05 then sustainedBeams:Remove(key);return end
  local color=typeof(aura)=="Color3" and aura or Config.Auras[aura] or Config.Auras.Gold
  sustainedBeams:Update(key,os.clock(),pos,direction,length,beamWidth,color,attackLevel or 1,data.settings.reducedShake)
  return
 end
 if kind=="SustainedDamageTaken" or kind=="BeamDodged" then
  local character=p.Character
  if pos and character and character:FindFirstChildOfClass("Humanoid")==pos then
   local dodged=kind=="BeamDodged"
   academy.incomingHit.Text=dodged and "BEAM DODGED" or "BEAM HIT YOU"
   academy.incomingHit.TextColor3=dodged and Color3.fromRGB(147,236,192) or Color3.fromRGB(255,157,146)
   academy.defenderCueUntil=os.clock()+1.4
  end
  return
 end
 if kind=="SustainedCover" or kind=="SustainedEvaded" or kind=="SustainedNoHit" then
  if type(id)=="number" and p:GetAttribute("SustainedActive")==true and id==p:GetAttribute("SustainedSequence") and id~=hitFeedback.sequence then
   academy.attackCueSequence=id;academy.attackCueUntil=os.clock()+.9
   academy.attackCueText=kind=="SustainedNoHit" and "NO HIT YET" or kind=="SustainedEvaded" and "OPPONENT DODGED" or "BEAM HIT COVER"
  end
  return
 end
 if kind=="SustainedHit" then
  if hitFeedback:Accept(id,aura,os.clock()) then
   playGameplayCue("Hit");beamScreenFeedback:Hit(os.clock(),screenFeedbackAllowed())
   if id==academy.attackCueSequence then academy.attackCueUntil=nil end
   if sustainedBeams and typeof(pos)=="Vector3" then
    local attack=sustainedControl and sustainedControl.attack
    local entry=sustainedBeams.entries[p.UserId];local now=os.clock()
    if attack and attack.acknowledged and attack.sequence==id and p:GetAttribute("SustainedActive")==true
     and p:GetAttribute("SustainedSequence")==id and entry and now<entry.expires and windowFocused and not beamBlocked() then
     BeamVisuals.Contact(entry.visual,pos,now,id)
    end
   end
  end
  return
 end
 if kind=="SustainedBeamEnd" then
  if id==p.UserId then
   -- End has no sequence payload. Consume the current local attempt, failing quiet
   -- if an old End overlaps a new attempt, rather than launch after a known stop.
   local ended=sustainedControl and sustainedControl.attack
   if ended then beamScreenFeedback:Begin(ended.sequence,os.clock(),nil,false) end
   beamScreenFeedback:Clear()
  end
  attackAudio:Stop(id,os.clock())
  if sustainedBeams then sustainedBeams:Remove(id) end
  return
 end
 if kind=="SustainedBeam" then
  if not sustainedBeams then return end
  local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
  local distance=root and (root.Position-pos).Magnitude
  if not Players:GetPlayerByUserId(id) or not distance or distance>180 or length<.05 then
   sustainedBeams:Remove(id);attackAudio:Remove(id);return
  end
  local color=typeof(aura)=="Color3" and aura or Config.Auras[aura] or Config.Auras.Gold
  sustainedBeams:Update(id,os.clock(),pos,direction,length,beamWidth,color,attackLevel or 1,data.settings.reducedShake)
  local style=distance<=attackAudioSettings.Range and type(audioStyleId)=="string" and Config.GetSound(audioStyleId)
  attackAudio:Pulse(id,os.clock(),pos,id==p.UserId,style and style.level,distance)
  return
 end
 local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart");if not root or (root.Position-pos).Magnitude>180 then return end
 if kind=="Break" then
  playGameplayCue("Break",pos)
  for i=1,6 do local chip=fxPart(pos,(typeof(id)=="Color3" and id or Config.Auras[id] or gold),Vector3.new(.5,.5,.5));Tween:Create(chip,TweenInfo.new(.45),{Position=pos+Vector3.new(math.cos(i)*3,2,math.sin(i)*3),Transparency=1}):Play() end;return
 end
 local chosenColor=kind=="Dodge" and id or aura
 local color=typeof(chosenColor)=="Color3" and chosenColor or Config.Auras[chosenColor] or gold
 if kind=="Dodge" then
  playGameplayCue("Dodge",pos)
  local actor=type(id)=="number" and Players:GetPlayerByUserId(id)
  if actor and actor.Character then DodgeVisuals.Play(actor.Character,data.settings.reducedShake or platformReducedMotion) end
  return
 end
 local s=Config.GetSound(id);if not s then return end
 -- Actual voice stays on Roblox proximity audio. Owner-selected SFX are separate.
 direction=direction or Vector3.new(0,0,-1);length=length or Config.VoiceCombat.Stats(data.level,1,false).range
 screamEffectsUsed=true;ScreamEffects.Render(s.effect,pos,direction,length,beamWidth or 4,color,data.settings.reducedShake,s.variant)
end)
local elapsed=0
local lastViewport,lastTouch,lastDevAccess
-- Visible modal buttons keep the pointer available while interacting with panels.
modal.Close.Modal=true;conversationPanel.Close.Modal=true
connectClient(Run.RenderStepped,function(dt)
 -- The optional gear hint yields to payouts and other notices already waiting.
 if starterGear.pending and not notifications.active then
  notify(starterGear.pending,false,"starterGear")
  starterGear.pending=nil;starterGear.shown=true
 end
 local notice=notifications:Step(0,false)
 if notice~=toast.Text then toast.Text=notice;toastWidth=0 end
 -- NoticeView owns full-text visibility and readable dwell.
 ShopUI.Tick()
 refreshHealth();academy.refreshZone()
 local viewport=gui.AbsoluteSize
 local touch=UIS.TouchEnabled
 local layoutChanged=viewport~=lastViewport or touch~=lastTouch or data.devAccess~=lastDevAccess
 if layoutChanged then lastViewport=viewport;lastTouch=touch;lastDevAccess=data.devAccess end
 if layoutChanged then conversationPanel.Size=UDim2.fromOffset(math.min(460,viewport.X-24),math.min(340,viewport.Y-36)) end
 refreshConversation()
 saveNotice.Text=saveStatus()
 saveNotice.Visible=saveNotice.Text~="" and not modal.Visible and viewport.X>=820
 local progress=progressLabel(viewport.X<820)
 if xpText.Text~=progress then xpText.Text=progress end
 -- Consume every observed input interruption before availability can recover.
 local micInterruption=mic.interruptionEpoch or 0
 if micInterruption~=observedMicInterruption then
  observedMicInterruption=micInterruption
  if sustainedControl then sustainedControl:SetArmed(false) end
  cancelCapture()
 end
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
  sustainedControl:ObserveAvailability(alive and mic.ready and data.voiceEligible==true,false)
  voiceCooldown=math.max(0,(p:GetAttribute("SustainedReadyAt") or 0)-workspace:GetServerTimeNow())
  voiceActive=p:GetAttribute("SustainedActive")==true
  sustainedControl:Step(dt,os.clock(),mic.power,alive and windowFocused and not beamBlocked(),
   data.micReady==true,voiceActive,p:GetAttribute("SustainedSequence"),voiceCooldown>0)
 end
 if captureSource and beamBlocked() then cancelCapture() end
 if captureSource and mic.captureStarted and os.clock()-mic.captureStarted>Config.VoiceCombat.CaptureExpiry then
  cancelCapture();notify("Capture expired. Hold attack again and use a fresh live voice input.",true,"capture")
 end
 if sprinting then setSprint(true) end
 local gameplayVisible=not GuiService.MenuIsOpen and not modal.Visible and not conversationPanel.Visible
 academy.guide:Step(p.Character and p.Character:FindFirstChild("HumanoidRootPart"),os.clock(),gameplayVisible and not devPanel.Visible)

 local showTouchControls=originalTouchControls and not GuiService.MenuIsOpen and not modal.Visible and not conversationPanel.Visible
 if GuiService.TouchControlsEnabled~=showTouchControls then lastTouchControls=showTouchControls;GuiService.TouchControlsEnabled=showTouchControls end
 local eligibilityHint,inputMuted=voiceEligibilityHint(true)
 if academy.muteNoticePending and not inputMuted then
  notifications:Remove("micMuted")
  academy.muteNoticePending=false
 end
 tracked.Text=trackedQuestText
 local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
 if os.clock()>=nextResidentUi then
  nextResidentUi=os.clock()+.1
  local residents=game:GetService("CollectionService"):GetTagged("CityResident")
  talkTarget=refreshResidentLabels(root,workspace.CurrentCamera,residents)
  academy.refreshMarGuide(root,residents)
  academy.refreshTrainingGuide(residents)
 end
 local confirmed=hitFeedback:Read(os.clock())
 local attackCue=alive and windowFocused and p:GetAttribute("SustainedActive")==true
  and p:GetAttribute("SustainedSequence")==academy.attackCueSequence and os.clock()<(academy.attackCueUntil or 0)
 hitText.Visible=gameplayVisible and (confirmed~=nil or attackCue)
 if confirmed then hitText.Text=string.format("%d DAMAGE",confirmed)
 elseif attackCue then hitText.Text=academy.attackCueText end
 if protectionRemaining>0 then academy.defenderCueUntil=nil end
 academy.incomingHit.Visible=gameplayVisible and windowFocused and alive and os.clock()<(academy.defenderCueUntil or 0)
 local showVoiceMeter=viewport.Y>=315 and not (not touch and viewport.X>=820 and talkTarget~=nil)
 local compactVoice=not showVoiceMeter
 meter.Visible=gameplayVisible and showVoiceMeter;reticle.Visible=usesCenterAim() and gameplayVisible
 local power=academy.VoiceReactor.Power(captureSource and mic:CapturePower() or mic.power)
 academy.reactor:Step(power,dt,data.settings.reducedShake or platformReducedMotion,mic.ready and (not sustainedControl or sustainedControl.armed))
 local beamStats=Config.VoiceCombat.Stats(data.level,power,data.amplifierEquipped,data.megaphoneEquipped,data.gearMultiplier)
 local range=beamStats.range
 local captureRemaining=mic.captureStarted and math.max(0,Config.VoiceCombat.MaxCapture-(os.clock()-mic.captureStarted)) or 0
 local captureHint=captureSource and (captureRemaining>0 and string.format("Speak now • %.1fs left",captureRemaining) or "Window ended • release to fire") or "Hold attack before speaking"
 if sustainedControl then
  captureHint=not alive and (compactVoice and "Respawning" or "Respawning • beams OFF")
   or not windowFocused and (compactVoice and "Attack paused" or "Window inactive • attack paused")
   or protectionRemaining>0 and string.format(compactVoice and "Protected %.1fs" or "Spawn protection • %.1fs",protectionRemaining)
   or (knocked or humanoid.PlatformStand) and (compactVoice and "Recovering" or "Recovering • attack unavailable")
   or rolling and (compactVoice and "Rolling" or "Rolling • attack cancelled")
   or UIS:GetFocusedTextBox()~=nil and (compactVoice and "Typing · paused" or "Typing • attack paused")
   or compactVoice and devPanel.Visible and "Close Test Tools"
   or (data.micReady~=true or compactVoice and not mic.ready) and (compactVoice and "Connecting mic" or "Connecting microphone…")
   or not sustainedControl.armed and (compactVoice and (touch and "Tap to turn on" or "[E] to turn on") or touch and "Beams OFF • tap to turn on" or "Beams OFF • E to turn on")
   or voiceCooldown>0 and string.format(sustainedControl.gate.needsQuiet and "Cooldown %.1fs · go quiet" or "Cooldown %.1fs",voiceCooldown)
   or sustainedControl.attack and (voiceActive and string.format(compactVoice and "Firing · %.1fs" or "Attacking • %.1fs left",math.max(0,(p:GetAttribute("SustainedEndsAt") or 0)-serverNow)) or "Starting attack…")
   or os.clock()<(sustainedControl.unconfirmedUntil or 0) and (compactVoice and "Go quiet, then retry" or "Not confirmed • quiet, then retry")
   or sustainedControl.gate.needsQuiet and "Go quiet"
   or sustainedControl.gate.onset>0 and (compactVoice and "Keep speaking" or "Voice detected • keep speaking")
   or "Aim and speak"
  meterFill.BackgroundColor3=voiceActive and Color3.fromRGB(104,222,157)
   or (not sustainedControl.armed or voiceCooldown>0 or sustainedControl.gate.needsQuiet or blocked()) and muted or gold
  academy.voiceThreshold.Visible=sustainedControl.armed and voiceCooldown<=0 and windowFocused
   and data.micReady==true and not inputMuted and not beamBlocked()
 end
 meterText.Text=inputMuted and eligibilityHint or academy.VoiceReactor.Status(
  string.format("%s %d%%\n%s",captureSource and "BEAM POWER" or "LIVE MIC",math.floor(power*100),captureHint),
  eligibilityHint,sustainedControl and not sustainedControl.armed,viewport.X,viewport.Y,touch)
 local shortLandscape=viewport.Y<300 and viewport.X>viewport.Y
 if layoutChanged then
 academy.layoutZone(viewport,touch)
 local short=viewport.Y<550
 menuScale.Scale=1
 local width=math.min(720,viewport.X-24)
 modal.Size=UDim2.fromOffset(width,math.min(620,viewport.Y-(shortLandscape and 16 or 76)))
 modal.Position=UDim2.new(.5,0,0,shortLandscape and 8 or 64)
 modal.Close.Position=UDim2.new(1,-56,0,shortLandscape and 0 or 10)
 title.Position=UDim2.fromOffset(22,shortLandscape and 4 or 15)
 title.TextSize=width<620 and 20 or 23
 subtitle.Visible=not short;subtitle.Size=UDim2.new(1,-44,0,width<620 and 42 or 25)
 local tabY=shortLandscape and 44 or short and 54 or width<620 and 102 or 88
 local columns=(width>=620 or shortLandscape and width>=500) and 6 or 3;local rows=6/columns
 local tabWidth=(width-40-(columns-1)*6)/columns
 for i,name in ipairs(academy.menuTabs) do
  local b=tabs[name];b.Size=UDim2.fromOffset(tabWidth,44);b.Position=UDim2.fromOffset(20+((i-1)%columns)*(tabWidth+6),tabY+math.floor((i-1)/columns)*50);b.TextSize=width<620 and 12 or 14
  local decoration=academy.tabIcons[name];academy.layoutTab(b,decoration.icon,decoration.padding,tabWidth)
 end
 content.Position=UDim2.fromOffset(20,tabY+rows*50+4);content.Size=UDim2.new(1,-40,1,-(tabY+rows*50+18))
 if width~=lastLayoutWidth or (selected=="Shop" and ShopUI.CompactLandscape(viewport.X,viewport.Y)~=academy.shopCompactLandscape) or (Config.ResonanceLayout and selected=="Map" and layoutChanged) then
  lastLayoutWidth=width
  academy.shopCompactLandscape=ShopUI.CompactLandscape(viewport.X,viewport.Y)
  if modal.Visible then render() end
 end
 -- Keep desktop controls compact; smaller displays retain readable button text.
 local tight=viewport.X<380
 shop.Size=UDim2.fromOffset(tight and 90 or 125,touch and 44 or 36);shop.Text=(tight or touch) and "MENU" or "MENU [B]"
 questsToggle.Size=UDim2.fromOffset(tight and 78 or 95,touch and 44 or 36);questsToggle.Position=UDim2.fromOffset(tight and 98 or 134,0)
 testButton.Size=UDim2.fromOffset(viewport.X<432 and 86 or 112,44)
 local miniLayout=CityMap.MiniLayout(viewport,touch,data.devAccess==true)
 miniMapButton.Size=UDim2.fromOffset(miniLayout.width,miniLayout.height);miniMapButton.Position=UDim2.new(1,-miniLayout.width-14,0,14)
 miniMapHolder.Visible=miniLayout.expanded;miniMapAvailable=miniLayout.available
 local testTop=miniLayout.available and 14+miniLayout.height+8 or (touch and math.clamp(viewport.Y-195-44,0,14) or 14)
 testButton.Position=UDim2.new(1,viewport.X<432 and -100 or -126,0,testTop)
 hud.Position=(touch or viewport.X<820) and UDim2.fromOffset(14,data.devAccess==true and viewport.X<356 and miniLayout.height+74 or 64) or UDim2.new(0,14,1,-108)
 academy.layoutStatusCard(touch and shortLandscape)
 controls.Position=UDim2.new(1,-274,1,touch and -195 or -102)
 talkButton.Size=UDim2.fromOffset(120,touch and 44 or 34)
 controls.Size=UDim2.fromOffset(260,touch and 96 or 88)
 local trackerY=(touch or viewport.X<820) and math.max(data.devAccess==true and viewport.X<356 and miniLayout.height+170 or 160,data.devAccess==true and viewport.X<406 and miniLayout.height+74 or 0) or 64
 local trackerX,trackerTop,trackerWidth,trackerHeight,canShare,centerTracker=academy.trackerLayout(viewport,touch,trackerY)
 academy.guideMayUseTracker=canShare==true
 tracked.Position=UDim2.fromOffset(trackerX,trackerTop)
 tracked.Size=UDim2.fromOffset(trackerWidth,trackerHeight)
 local meterWidth,meterHeight=academy.VoiceReactor.Layout(viewport.X,touch,viewport.Y)
 local slimMeter=centerTracker and viewport.Y>=315
 meter.RecentAmplitude.Visible=not slimMeter
 if slimMeter then
  -- Keep live power under the status card while the guide occupies the bottom center.
  meter.Size=UDim2.fromOffset(math.min(meterWidth,trackerX-22),56)
  meter.Position=UDim2.fromOffset(14,trackerY+4)
 else
  meter.Size=UDim2.fromOffset(meterWidth,meterHeight)
  meter.Position=UDim2.new(.5,-meterWidth/2,1,-meterHeight-((not touch and viewport.X<820) and 116 or 12))
 end
 dodgeButton.Size=UDim2.fromOffset(108,touch and 44 or 32)
 sprintButton.Size=UDim2.fromOffset(144,touch and 44 or 32)
 local testBottom=testTop+44
 local bottomReserve=(touch and 189 or 96)+14
 local belowHeight=viewport.Y-(testBottom+8)-bottomReserve
 local panelWidth=viewport.X<432 and 212 or 230
 if belowHeight>=240 then
  devPanel.Position=UDim2.new(1,viewport.X<432 and -226 or -244,0,testBottom+8)
  devPanel.Size=UDim2.fromOffset(panelWidth,math.min(330,belowHeight))
 else
  local rightColWidth=miniLayout.available and math.max(miniLayout.width,viewport.X<432 and 86 or 112) or (viewport.X<432 and 86 or 112)
  devPanel.Position=UDim2.fromOffset(math.max(8,viewport.X-(rightColWidth+22+panelWidth)),14)
  devPanel.Size=UDim2.fromOffset(panelWidth,math.min(330,math.max(120,viewport.Y-14-bottomReserve)))
 end
 end
 hud.Visible=gameplayVisible;controls.Visible=gameplayVisible
 -- Keep the fight readable without hiding a running quest deadline.
 local combatQuest=data.activeQuest=="arena" or data.activeQuest=="dodge" or data.activeQuest=="crowd" or data.activeQuest=="practice_beams" or data.activeQuest=="arena_assist"
 local showQuest=not data.inWarZone or combatQuest or (data.questTime or 0)>0
 local guideUsesTracker=false
 do
  local x,y,w,h,compact=academy.guideLayout(viewport,touch,tracked.Position.Y.Offset)
  if not x and academy.guideMayUseTracker and not data.activeQuest and showQuest then
   -- The selected route takes the idle objective's lane only while it needs it.
   x,y=tracked.Position.X.Offset,tracked.Position.Y.Offset
   w,h=tracked.Size.X.Offset,tracked.Size.Y.Offset
   guideUsesTracker=true
  end
  academy.guidePanel.Visible=x~=nil and gameplayVisible and not devPanel.Visible and academy.guideTarget~=nil
  if academy.guidePanel.Visible then
   academy.guidePanel.Position=UDim2.fromOffset(x,y);academy.guidePanel.Size=UDim2.fromOffset(w,h)
   local status,distance,bearing=academy.guide:GetStatus()
   local selection=academy.guideSelection
   local heading=compact and "" or academy.guideTarget.label.."\n"
   if status=="Arrived" and selection.kind=="place" and selection.id=="training" then
    local fighter=academy.trainingGuideFighter
    local ready=fighter and fighter.Parent and fighter:GetAttribute("ResidentActive")
    status=ready==false and "Fighter recovering" or ready==true and "Hit the fighter to spar" or "Sparring pad"
    distance=nil
    if guideUsesTracker then
     heading=""
     status..="\nFighters "..((data.combatChallenges or {}).fighters or 0).."/3"
    end
   end
   if status=="Arrived" and academy.guideTarget.minimumLevel then
    local minimumLevel=academy.guideTarget.minimumLevel
    if data.level<minimumLevel then
     status="Requires Lv "..minimumLevel
    else
     local world=workspace:FindFirstChild("ScreamSimulatorWorld")
     local encounters=world and world:FindFirstChild("BossEncounters")
     local boss=encounters and encounters:FindFirstChild(selection.id)
     local health=boss and boss:GetAttribute("BossHealth")
     local phase=boss and boss:GetAttribute("BossState")
     if health==0 or phase=="Defeated" then
      status="Boss defeated"
     elseif health and health>0 and phase then
      status="Hit boss to join"
     else
      status="Boss unavailable"
     end
    end
    distance=nil
   end
   if compact and status=="Route unavailable" then status="No route" end
   local suffix=distance and (" · "..math.floor(distance).." studs"..(bearing and (" "..bearing) or "")) or ""
   local text=heading..status..suffix
   if academy.guideText.Text~=text then academy.guideText.Text=text end
  end
 end
 tracked.Visible=gameplayVisible and tracked.Text~="" and showQuest and not Config.ResonanceLayout
  and not (guideUsesTracker and academy.guidePanel.Visible)
 zone.Visible=gameplayVisible
 academy.trainingGuideButton.Visible=tracked.Visible and not devPanel.Visible and academy.canGuideTraining()
 local now=workspace:GetServerTimeNow();local protected=math.max(0,(p:GetAttribute("ProtectionEnds") or 0)-now)
 if sustainedControl then
  -- Keep the next voice action on the toggle when the meter has no lane.
  local status
  if compactVoice or inputMuted or sustainedControl.armed and (voiceActive or voiceCooldown>0) then
   status=captureHint
   if inputMuted then
    status="Unmute in Roblox"
   elseif eligibilityHint then
    status=data.voiceStatus=="denied" and "Check voice settings"
     or data.voiceStatus=="unavailable" and "Voice check delayed" or "Checking voice"
   end
  end
  castButton.Text=screamToggleLabel(sustainedControl.armed,touch,status)
  castButton.TextSize=13
 else
  castButton.Text=protected>0 and "PROTECTED "..math.ceil(protected).."s" or os.clock()<nextCast and string.format("BEAM %.1fs",nextCast-os.clock()) or captureSource and (captureRemaining>0 and "SPEAK • RELEASE" or "RELEASE TO FIRE") or "HOLD BEAM [E]"
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
 if academy.setBeamFace then
  local armed=sustainedControl.armed and windowFocused and data.micReady==true and not beamBlocked()
  academy.setBeamFace(armed,voiceActive and sustainedControl.attack~=nil,voiceCooldown>0)
 else
  castButton.BackgroundColor3=protected>0 and muted or gold
 end
 local cd=math.max(0,(p:GetAttribute("DodgeReady") or 0)-now);dodgeButton.Text=cd>0 and string.format("DODGE %.1fs",cd) or (touch and "DODGE" or "DODGE [Q]")
 local rest=p:GetAttribute("SprintCooldown") or 0;local charge=p:GetAttribute("SprintCharge") or Config.SprintDuration
 sprintButton.Text=rest>0 and string.format("REST %.1fs",rest) or string.format("SPRINT %.1fs",charge)..(touch and "" or " [SHIFT]")
 academy.staminaFill.Size=UDim2.fromScale(math.clamp(charge/Config.SprintDuration,0,1),1)
 aimInfo.Visible=gameplayVisible
 if sustainedBeams then
  local now=os.clock();sustainedBeams:Expire(now)
  beamFrame+=dt
  if beamFrame>=1/30 then
   beamFrame%=1/30
   local camera=workspace.CurrentCamera
   if camera then
    local attack=sustainedControl.attack
    local contactAllowed=windowFocused and not beamBlocked() and attack and attack.acknowledged and p:GetAttribute("SustainedActive")==true and p:GetAttribute("SustainedSequence")==attack.sequence
    local viewer=camera.CFrame.Position
    local crowded=BeamVisuals.IsCrowded(sustainedBeams.entries,viewer)
    local ownTestKey="test:"..p.UserId
    for id,entry in pairs(sustainedBeams.entries) do
     local incoming=type(id)=="number" and id~=p.UserId
     BeamVisuals.Animate(entry.visual,now,viewer,data.settings.reducedShake,(contactAllowed and entry.visual.contactSequence==attack.sequence)==true,platformReducedMotion,crowded and id~=p.UserId and id~=ownTestKey,incoming)
    end
   end
  end
 end
 -- A current local acknowledgement, not visual-packet arrival order, owns launch feedback.
 local screenAttack=sustainedControl and sustainedControl.attack
 if screenAttack and screenAttack.acknowledged and p:GetAttribute("SustainedActive")==true and p:GetAttribute("SustainedSequence")==screenAttack.sequence then
  beamScreenFeedback:Begin(screenAttack.sequence,os.clock(),Config.Auras.Gold,screenFeedbackAllowed())
 end
 -- Pause queue time while covered, too small, interacting, or overflow remains unseen.
 local noticeLayout=NoticeLayout.Get(viewport.X,viewport.Y,touch,CityMap.MiniLayout(viewport,touch,data.devAccess==true),data.devAccess==true,talkTarget~=nil,
  hud.Visible and hud.AbsolutePosition-gui.AbsolutePosition,hud.AbsoluteSize,
  math.max(tracked.Visible and tracked.AbsolutePosition.Y+tracked.AbsoluteSize.Y or 0,
   academy.guidePanel.Visible and academy.guidePanel.AbsolutePosition.Y+academy.guidePanel.AbsoluteSize.Y or 0)-gui.AbsolutePosition.Y)
 if modal.Visible then noticeLayout=NoticeLayout.Modal(viewport.X,viewport.Y,shortLandscape) end
 local noticeVisible=(gameplayVisible or modal.Visible) and windowFocused and not GuiService.MenuIsOpen
 local noticeNow=os.clock()
 noticeView:Update(notice,noticeLayout,noticeVisible,noticeNow,viewport.X<820 and 14 or 16,notifications.active)
 local nextNotice=notifications:Step(dt,noticeView:CanAdvance())
 if nextNotice~=notice then notice=nextNotice;noticeView:Update(notice,noticeLayout,noticeVisible,noticeNow,viewport.X<820 and 14 or 16,notifications.active) end
 title.Visible=not (shortLandscape and modal.Visible and noticeView.visible)
 shop.Visible=not GuiService.MenuIsOpen and not (conversationPanel and conversationPanel.Visible)
  and not (modal.Visible and (noticeView.visible or shortLandscape))
 questsToggle.Text=notice~="" and not noticeLayout.available and gameplayVisible and windowFocused and "NOTICE" or questLauncherText()
 -- Keep navigation in MENU. A pending claim or inaccessible notice gets a shortcut.
 questsToggle.Visible=shop.Visible and not modal.Visible and questsToggle.Text~="QUESTS"
 talkButton.Visible=talkTarget~=nil and gameplayVisible
 if noticeView.visible and noticeLayout.moveTalk then
  talkButton.Position=UDim2.fromOffset(noticeLayout.talkX,noticeLayout.talkY)
 elseif noticeLayout.baseTalkX then
  talkButton.Position=UDim2.fromOffset(noticeLayout.baseTalkX,noticeLayout.baseTalkY)
 else
  talkButton.Position=UDim2.new(.5,-60,1,touch and -249 or -108)
 end
 for _,passive in ipairs({hud,tracked,zone,saveNotice,meter,academy.guidePanel})do
  if noticeView:Overlaps(passive,gui) or noticeView:Overlaps(passive,gui,talkButton) then passive.Visible=false end
 end
 if academy.damageReadout.phase then
  academy.damageReadout:Step(noticeNow,dt,gameplayVisible and windowFocused and alive and not devPanel.Visible,
   gui,hud,tracked,academy.guidePanel,miniMapButton,testButton,noticeView.root,talkButton,meter,controls,zone,saveNotice)
 end
 beamScreenFeedback:Step(os.clock(),screenFeedbackAllowed(),data.settings.reducedShake or platformReducedMotion)
 cueContext();gameplayAudio:Step(os.clock(),dt)
 -- Audio consumes frame dt; keep ducking/calibration/fades outside the slow HUD gate.
 attackAudio:Step(os.clock(),dt,mic.ready and mic.power>.12,mic.phase~=nil)
 elapsed+=dt;if elapsed<.15 then return end;elapsed=0
 aimInfo.Text=""
 if aimInfo.Visible then
  local ray,hit=aimRay();local object=hit and hit.Instance
  while object and object~=workspace and not object:GetAttribute("RequiredLevel")
   and not (object:IsA("Model") and (Players:GetPlayerFromCharacter(object) or object:GetAttribute("NpcId"))) do object=object.Parent end
  if ray and (not object or object==workspace) then object=academy.trainingHeadAt(ray,hit and hit.Distance or 1000) end
  local targetPlayer=object and object~=workspace and object:IsA("Model") and Players:GetPlayerFromCharacter(object)
  if targetPlayer and targetPlayer~=p then
   local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
   local targetRoot=object:FindFirstChild("HumanoidRootPart");local humanoid=object:FindFirstChildOfClass("Humanoid")
   if root and targetRoot and humanoid then
    local inPvp,targetInPvp=Config.InArena(root.Position),Config.InArena(targetRoot.Position)
    local canFight=inPvp and targetInPvp
    local far,currentFar,origin=beamTargetRange(root,targetRoot,hit.Position,beamStats,true)
    local text,available=playerTargetInfo(targetPlayer,humanoid,inPvp,targetInPvp,far,workspace:GetServerTimeNow(),currentFar,canFight and not far and not currentFar and targetCovered(origin,targetRoot,object,hit.Position))
    aimInfo.Text=text or "";aimInfo.TextColor3=available and gold or white
   end
  elseif object and object~=workspace and object:IsA("Model") and object:GetAttribute("NpcId") then
   local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
   local npcRoot=object:FindFirstChild("HumanoidRootPart")
   if root and npcRoot then
    local aimPoint=hit and hit.Position or ray.Origin+ray.Direction*1000
    local far,currentFar,origin=beamTargetRange(root,npcRoot,aimPoint,beamStats,false)
    local text,available=residentTargetInfo(object,object:FindFirstChildOfClass("Humanoid"),far,currentFar,not far and not currentFar and targetCovered(origin,npcRoot,object,aimPoint),root.Position)
    aimInfo.Text=text or "";aimInfo.TextColor3=available and gold or white
   end
  elseif object and object~=workspace and object:GetAttribute("RequiredLevel") then
   local required=object:GetAttribute("RequiredLevel");local hp=object:GetAttribute("ObjectHealth") or 0
   local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
   local rangeLimit=Config.VoiceCombat.Stats(data.level,1,data.amplifierEquipped,data.megaphoneEquipped,data.gearMultiplier).maxRange
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
 if mapDot then CityMap.update(mapDot,root) end
 local miniVisible=miniMapAvailable and gameplayVisible and windowFocused and not modal.Visible and not (conversationPanel and conversationPanel.Visible) and not academy.testLauncherBlocked
 miniMapButton.Visible=miniVisible
 academy.refreshTestLauncher()
 CityMap.MiniUpdate(miniMapView,root,os.clock(),miniVisible and miniMapHolder.Visible)
 talkButton.Text=touch and "TALK" or "TALK [T]"
 talkButton.Visible=talkTarget~=nil and gameplayVisible
end)
end)()
if not clientCheckpoint() then return end
action:FireServer("Sync")

-- JumpRequest supports the built-in keyboard, controller and touch jump controls.
connectClient(UIS.JumpRequest,function()
 local character=p.Character;local h=character and character:FindFirstChildOfClass("Humanoid")
 if h and h.FloorMaterial==Enum.Material.Air and data.movementPass and not data.inWarZone and not blocked() then action:FireServer("ExtraJump") end
end)
