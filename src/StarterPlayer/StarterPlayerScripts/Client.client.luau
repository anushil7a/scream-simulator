local Players=game:GetService("Players")
local RS=game:GetService("ReplicatedStorage")
local UIS=game:GetService("UserInputService")
local Run=game:GetService("RunService")
local Tween=game:GetService("TweenService")
local Debris=game:GetService("Debris")
local TextService=game:GetService("TextService")
local GuiService=game:GetService("GuiService")
local originalTouchControls=GuiService.TouchControlsEnabled
script.Destroying:Connect(function() GuiService.TouchControlsEnabled=originalTouchControls end)
local p=Players.LocalPlayer
local Config=require(RS:WaitForChild("Shared"):WaitForChild("Config"))
local InteractionRules=require(RS.Shared:WaitForChild("InteractionRules"))
local mic=require(script.Parent:WaitForChild("Microphone")).new()
local ScreamEffects=require(script.Parent:WaitForChild("ScreamEffects"))
local remotes=RS:WaitForChild("ScreamRemotes")
local action=remotes:WaitForChild("Action")
local gui=Instance.new("ScreenGui");gui.Name="ScreamUI";gui.ResetOnSpawn=false;gui.ZIndexBehavior=Enum.ZIndexBehavior.Sibling;gui.Parent=p:WaitForChild("PlayerGui")
local dark=Color3.fromRGB(19,32,40);local panel=Color3.fromRGB(29,47,55);local gold=Color3.fromRGB(255,205,111);local white=Color3.fromRGB(239,244,240);local muted=Color3.fromRGB(165,188,193)
local data={level=1,xp=0,xpNext=103,coins=0,health=100,sound="TinyAah",aura="Gold",quests={},settings={volume=.55,reducedShake=false}}
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
local menuScale=Instance.new("UIScale");menuScale.Parent=modal
local title=label(modal,"SCREAM COLLECTION",UDim2.new(1,-85,0,36),UDim2.fromOffset(22,15),23,gold)
local subtitle=label(modal,"Train for XP. Unlock a new scream every five levels.",UDim2.new(1,-44,0,25),UDim2.fromOffset(22,52),14,muted)
button(modal,"Close","X",UDim2.fromOffset(44,44),UDim2.new(1,-56,0,10),function() modal.Visible=false end)
local content=Instance.new("ScrollingFrame");content.Name="Content";content.Size=UDim2.new(1,-40,1,-148);content.Position=UDim2.fromOffset(20,132);content.BackgroundTransparency=1;content.BorderSizePixel=0;content.ScrollBarThickness=4;content.AutomaticCanvasSize=Enum.AutomaticSize.Y;content.CanvasSize=UDim2.new();content.Parent=modal
local list=Instance.new("UIListLayout");list.Padding=UDim.new(0,10);list.SortOrder=Enum.SortOrder.LayoutOrder;list.Parent=content
local selected="Screams";local render;local tabs={};local mapDot;local devPanel;local narrow=false;local lastLayoutWidth=0
local function toggle() modal.Visible=not modal.Visible;if modal.Visible then if devPanel then devPanel.Visible=false end;render() end end
local shop=button(top,"ShopToggle","SCREAMS  [B]",UDim2.fromOffset(125,36),UDim2.fromOffset(0,0),toggle,gold);shop.TextColor3=dark
local questsToggle=button(top,"QuestsToggle","QUESTS",UDim2.fromOffset(95,36),UDim2.fromOffset(134,0),function() if devPanel then devPanel.Visible=false end;selected="Quests";modal.Visible=not(modal.Visible and title.Text=="CITY QUESTS");render() end)
local hud=frame(gui,"CompactHUD",UDim2.fromOffset(242,94),UDim2.new(0,14,1,-108));hud.BackgroundTransparency=.08
local stats=label(hud,"LEVEL 1     •     0 coins",UDim2.new(1,-24,0,22),UDim2.fromOffset(12,7),14,gold)
local health=label(hud,"100 HP",UDim2.fromOffset(65,20),UDim2.fromOffset(12,31),12)
local hb=frame(hud,"HealthTrack",UDim2.fromOffset(142,6),UDim2.fromOffset(83,38),panel)
local hf=frame(hb,"Fill",UDim2.fromScale(1,1),UDim2.new(),Color3.fromRGB(105,224,158))
local xpText=label(hud,"0 / 103 XP",UDim2.new(1,-24,0,19),UDim2.fromOffset(12,52),12,muted)
local xb=frame(hud,"XPTrack",UDim2.fromOffset(218,4),UDim2.fromOffset(12,79),panel)
local xf=frame(xb,"Fill",UDim2.fromScale(0,1),UDim2.new(),gold)
local zone=label(gui,"SAFE CITY • PvP off",UDim2.fromOffset(240,28),UDim2.new(.5,-120,0,12),13);zone.TextXAlignment=Enum.TextXAlignment.Center
local tracked=label(gui,"",UDim2.fromOffset(290,50),UDim2.fromOffset(16,56),13);tracked.Name="QuestTracker";tracked.TextYAlignment=Enum.TextYAlignment.Top
tracked.BackgroundColor3=dark;tracked.BackgroundTransparency=.12
local trackerCorner=Instance.new("UICorner");trackerCorner.CornerRadius=UDim.new(0,8);trackerCorner.Parent=tracked
local trackerPadding=Instance.new("UIPadding");trackerPadding.PaddingLeft=UDim.new(0,6);trackerPadding.PaddingRight=UDim.new(0,6);trackerPadding.PaddingTop=UDim.new(0,4);trackerPadding.PaddingBottom=UDim.new(0,4);trackerPadding.Parent=tracked
local toast=label(gui,"",UDim2.new(.7,0,0,48),UDim2.new(.15,0,.72,0),16,gold);toast.TextXAlignment=Enum.TextXAlignment.Center;toast.AnchorPoint=Vector2.new(.5,1);toast.Position=UDim2.fromScale(.5,.72)
local saveNotice=label(gui,"",UDim2.fromOffset(250,28),UDim2.new(.5,-125,0,40),12,gold);saveNotice.TextXAlignment=Enum.TextXAlignment.Center
local toastUntil=0;local toastWidth=0
local function notify(t) toast.Text=t;toastUntil=os.clock()+math.clamp(#t/22,4,12);toastWidth=0 end
local conversationPanel,showConversation,closeConversation
local nextCast=0;local sequence=0;local captureSource=nil
local function cancelCapture()
 captureSource=nil;mic:Cancel();action:FireServer("CancelCast")
end
local function blocked()
 local now=workspace:GetServerTimeNow()
 return (conversationPanel and conversationPanel.Visible) or modal.Visible or (devPanel and devPanel.Visible) or not mic.ready or now<(p:GetAttribute("ProtectionEnds") or 0) or now<(p:GetAttribute("DodgeEnds") or 0) or now<(p:GetAttribute("KnockdownEnds") or 0)
end
local function beginCapture(source)
 if captureSource or blocked() or os.clock()<nextCast then return end
 if mic:Begin() then sequence+=1;captureSource=source;action:FireServer("BeginCast",sequence) end
end
local function aimRay()
 local camera=workspace.CurrentCamera
 local location=UIS.TouchEnabled and camera.ViewportSize/2 or UIS:GetMouseLocation()-game:GetService("GuiService"):GetGuiInset()
 local ray=camera:ViewportPointToRay(location.X,location.Y)
 local params=RaycastParams.new();params.FilterDescendantsInstances={p.Character};params.FilterType=Enum.RaycastFilterType.Exclude;params.RespectCanCollide=true
 return ray,workspace:Raycast(ray.Origin,ray.Direction*1000,params)
end
local function releaseCapture(source)
 if captureSource~=source then return end
 captureSource=nil
 if blocked() then cancelCapture();return end
 local power=mic:Release();if power<.08 then action:FireServer("CancelCast");notify("Use your voice while holding attack.");return end
 local ray,hit=aimRay()
 action:FireServer("Cast",{sequence=sequence,power=power,aim=hit and hit.Position or ray.Origin+ray.Direction*1000})
 nextCast=os.clock()+4
end
local function dodge()
 cancelCapture()
 if not blocked() then action:FireServer("Dodge") end
end
local controls=frame(gui,"Actions",UDim2.fromOffset(260,88),UDim2.new(1,-274,1,-102));controls.BackgroundTransparency=1
local castButton=button(controls,"Cast","SCREAM  [E]",UDim2.fromOffset(144,44),UDim2.fromOffset(116,0),function() end,gold);castButton.TextColor3=dark
castButton.InputBegan:Connect(function(input)
 if input.UserInputType==Enum.UserInputType.MouseButton1 or input.UserInputType==Enum.UserInputType.Touch then beginCapture(input) end
end)
local micPanel=frame(gui,"MicSetup",UDim2.fromOffset(430,260),UDim2.fromScale(.5,.5));micPanel.AnchorPoint=Vector2.new(.5,.5);micPanel.ZIndex=20
local micTitle=label(micPanel,"YOUR VOICE. YOUR POWER.",UDim2.new(1,-36,0,35),UDim2.fromOffset(18,16),21,gold)
local micStatus=label(micPanel,"",UDim2.new(1,-36,0,90),UDim2.fromOffset(18,58),15)
label(micPanel,"A microphone and Roblox voice access are required. Nearby players hear your live voice. No recordings are saved by this game.",UDim2.new(1,-36,0,50),UDim2.fromOffset(18,146),12,muted)
button(micPanel,"Calibrate","CALIBRATE MIC",UDim2.fromOffset(188,36),UDim2.fromOffset(18,208),function() mic:Calibrate() end,gold).TextColor3=dark
button(micPanel,"Retry","CHECK ACCESS",UDim2.fromOffset(188,36),UDim2.fromOffset(224,208),function() mic:Check() end)
for _,v in ipairs(micPanel:GetDescendants()) do if v:IsA("GuiObject") then v.ZIndex=21 end end
local micScale=Instance.new("UIScale");micScale.Parent=micPanel
local meter=frame(gui,"MicPower",UDim2.fromOffset(230,52),UDim2.new(.5,-115,1,-64))
local meterText=label(meter,"SCREAM POWER 0%",UDim2.new(1,-20,0,24),UDim2.fromOffset(10,4),12,gold)
local meterTrack=frame(meter,"Track",UDim2.new(1,-20,0,5),UDim2.fromOffset(10,36),panel)
local meterFill=frame(meterTrack,"Fill",UDim2.fromScale(0,1),UDim2.new(),gold)
local reticle=label(gui,"+",UDim2.fromOffset(24,24),UDim2.new(.5,-12,.5,-12),22,white);reticle.TextXAlignment=Enum.TextXAlignment.Center
local aimInfo=label(gui,"",UDim2.fromOffset(290,48),UDim2.new(.5,-145,.5,25),13,gold);aimInfo.TextXAlignment=Enum.TextXAlignment.Center
local reportedReady=nil;local readyReportAt=0
local dodgeButton=button(controls,"Dodge","DODGE  [Q]",UDim2.fromOffset(108,44),UDim2.fromOffset(0,0),dodge)
local sprinting=false
local sprintButton=button(controls,"Sprint","SPRINT [SHIFT]",UDim2.fromOffset(164,32),UDim2.fromOffset(96,52),function() sprinting=not sprinting;action:FireServer("Sprint",sprinting) end)
local talkTarget
local nextResidentUi=0
local function refreshResidentLabels(root,camera,residents)
 local nearest,best=nil,13
 local speaker,speechDistance=nil,24
 local damaged,damageDistance=nil,18
 local visible={}
 for _,bot in ipairs(residents) do
  local r=bot:FindFirstChild("HumanoidRootPart");local head=bot:FindFirstChild("Head");local h=bot:FindFirstChildOfClass("Humanoid")
  if not r or not head then continue end
  local nameplate=head:FindFirstChild("Nameplate");local speech=head:FindFirstChild("SpeechBubble")
  if nameplate then nameplate.Enabled=false end
  if speech then speech.Enabled=false end
  if not root or not h or h.Health<=0 then continue end
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
local talkButton=button(gui,"Talk","TALK [T]",UDim2.fromOffset(120,34),UDim2.new(.5,-60,1,-108),function() if talkTarget then action:FireServer("Talk",talkTarget:GetAttribute("NpcId") or talkTarget.Name) end end);talkButton.Visible=false
devPanel=frame(gui,"TestPanel",UDim2.fromOffset(230,330),UDim2.new(1,-244,0,60));devPanel.Visible=false;devPanel.ZIndex=10
local testContent=Instance.new("ScrollingFrame");testContent.Name="Commands";testContent.BackgroundTransparency=1;testContent.BorderSizePixel=0;testContent.ScrollBarThickness=4;testContent.Position=UDim2.fromOffset(8,76);testContent.Size=UDim2.new(1,-16,1,-84);testContent.CanvasSize=UDim2.fromOffset(0,235);testContent.Parent=devPanel
label(devPanel,"TEST SESSION",UDim2.fromOffset(210,25),UDim2.fromOffset(10,8),17,gold)
label(devPanel,"Test commands disable saving this session.",UDim2.fromOffset(210,38),UDim2.fromOffset(10,35),12,muted)
local testCommands={{"XP","+500 XP"},{"Coins","+1,000 coins"},{"MaxLevel","Level 300"},{"LevelOne","Level 1"},{"Heal","Heal"},{"Hub","Safe hub"},{"Arena","Arena"},{"Beach","Beach"},{"ResetQuests","Reset quests"},{"ResetBots","Reset bots"}}
if Run:IsStudio() then table.insert(testCommands,{"StudioMovement","Test movement"}) end
testContent.CanvasSize=UDim2.fromOffset(0,math.ceil(#testCommands/2)*47)
for i,item in ipairs(testCommands) do
 button(testContent,item[1],item[2],UDim2.fromOffset(98,44),UDim2.fromOffset(((i-1)%2)*108,math.floor((i-1)/2)*47),function() action:FireServer("DevCommand",item[1]) end)
end
local testButton=button(gui,"TestToggle","TEST TOOLS",UDim2.fromOffset(112,32),UDim2.new(1,-126,0,14),function() devPanel.Visible=not devPanel.Visible;if devPanel.Visible then modal.Visible=false end end);testButton.Visible=false
local function card(height) return frame(content,"Card",UDim2.new(1,-8,0,height),UDim2.new(),panel) end
local function info(text,height) local width=math.min(720,gui.AbsoluteSize.X-24)-76;local fit=TextService:GetTextSize(text,15,Enum.Font.GothamMedium,Vector2.new(width,10000)).Y+24;local c=card(math.max(height or 70,fit));label(c,text,UDim2.new(1,-28,1,-20),UDim2.fromOffset(14,10),15);return c end
local renderedMenuKey,renderedTab
local renderRevision=0
local function menuKey()
 local fields
 if selected=="Screams" then fields={level=data.level,sound=data.sound,amplifier=data.amplifierEquipped}
 elseif selected=="Quests" then fields={quests=data.quests,active=data.activeQuest,available=data.availableQuests}
 elseif selected=="Style" then fields={aura=data.aura,owned=data.amplifierOwned,equipped=data.amplifierEquipped}
 elseif selected=="Settings" then fields=data.settings
 else fields={} end
 return selected..":"..gui.AbsoluteSize.X..":"..game:GetService("HttpService"):JSONEncode(fields)
end
render=function()
 if selected=="Screams" then
  subtitle.Text="Level "..data.level.."  •  "..data.xp.." / "..data.xpNext.." XP  •  Styles change visuals • level and mic power set strength"
 end
 local key=menuKey()
 if key==renderedMenuKey then return end
 local scroll=renderedTab==selected and content.CanvasPosition or Vector2.zero
 renderedMenuKey=key;renderedTab=selected;renderRevision+=1
 local revision=renderRevision
 mapDot=nil
 narrow=gui.AbsoluteSize.X-24<620
 for _,c in ipairs(content:GetChildren()) do if c:IsA("GuiObject") then c:Destroy() end end
 for name,b in pairs(tabs) do b.BackgroundColor3=name==selected and Color3.fromRGB(64,93,99) or panel end
 if selected=="Screams" then
  title.Text="SCREAM COLLECTION"
  local maximum=Config.VoiceCombat.Stats(data.level,1,data.amplifierEquipped)
  for _,s in ipairs(Config.Sounds) do
   local c=card(narrow and 178 or 101);label(c,s.name.."  /  LEVEL "..s.level,UDim2.new(1,narrow and -28 or -156,0,narrow and 44 or 26),UDim2.fromOffset(14,8),17,gold)
   label(c,s.description,UDim2.new(1,narrow and -28 or -158,0,narrow and 40 or 25),UDim2.fromOffset(14,narrow and 54 or 36),13)
   label(c,string.format("UP TO %d DAMAGE / %.1f STUDS • 4s COOLDOWN",maximum.damage,maximum.maxRange),UDim2.new(1,-28,0,narrow and 30 or 23),UDim2.fromOffset(14,narrow and 95 or 69),12,muted)
   local unlocked=data.level>=s.level
   local b=button(c,s.id,data.sound==s.id and "EQUIPPED" or unlocked and "EQUIP" or "LEVEL "..s.level,UDim2.fromOffset(116,37),UDim2.new(1,-130,0,narrow and 132 or 21),function() if unlocked then action:FireServer("EquipSound",s.id) end end)
   if not unlocked then b.TextColor3=muted end
  end
 elseif selected=="Quests" then
  title.Text="CITY QUESTS";subtitle.Text="One active task. Switching or abandoning resets unfinished progress."
  if data.activeQuest then
   local current=Config.GetQuest(data.activeQuest);local c=card(96)
   label(c,"CURRENT: "..(current and current.name or data.activeQuest),UDim2.new(1,-28,0,38),UDim2.fromOffset(14,6),14,gold)
   button(c,"AbandonQuest","ABANDON",UDim2.fromOffset(116,38),UDim2.new(1,-130,0,50),function() action:FireServer("AbandonQuest") end)
  end
  for _,q in ipairs(Config.Quests) do
   local available=data.availableQuests and data.availableQuests[q.id]
   if q.hidden and not available then continue end
   local v=data.quests[q.id] or {progress=0}
   local description=available and q.description or "Meet "..(q.giver or "a resident").." and press T to talk."
   local textWidth=math.min(720,gui.AbsoluteSize.X-24)-48-(narrow and 28 or 158)
   local nameHeight=math.max(26,TextService:GetTextSize(q.name,17,Enum.Font.GothamMedium,Vector2.new(textWidth,10000)).Y+4)
   local descriptionHeight=math.max(49,TextService:GetTextSize(description,13,Enum.Font.GothamMedium,Vector2.new(textWidth,10000)).Y+8)
   local descriptionY=12+nameHeight;local rewardY=descriptionY+descriptionHeight+5
   local actionY=narrow and rewardY+34 or 32
   local c=card(narrow and actionY+48 or math.max(150,rewardY+35))
   label(c,q.name,UDim2.new(1,narrow and -28 or -150,0,nameHeight),UDim2.fromOffset(14,8),17,gold)
   label(c,description,UDim2.new(1,narrow and -28 or -158,0,descriptionHeight),UDim2.fromOffset(14,descriptionY),13)
   label(c,v.progress.." / "..q.goal.."   •   +"..q.xp.." XP   •   +"..q.coins.." coins",UDim2.new(1,-28,0,30),UDim2.fromOffset(14,rewardY),12,muted)
   button(c,q.id,not available and "MEET NPC" or v.claimed and "CLAIMED" or v.progress>=q.goal and "CLAIM" or data.activeQuest==q.id and (q.id=="nick" and "RESTART" or "TRACKING") or "ACCEPT",UDim2.fromOffset(116,38),UDim2.new(1,-130,0,actionY),function()
    if available and not v.claimed and (v.progress>=q.goal or data.activeQuest~=q.id or q.id=="nick") then action:FireServer(v.progress>=q.goal and "ClaimQuest" or "AcceptQuest",q.id) end
   end)
  end
 elseif selected=="Style" then
  title.Text="YOUR SIGNATURE";subtitle.Text="Choose the color of your scream effects."
  local equipment=card(narrow and 142 or 90)
  label(equipment,"MICRO-SPEAKER",UDim2.new(1,-28,0,25),UDim2.fromOffset(15,10),17,gold)
  label(equipment,"+12% mic power · capped at 100%",UDim2.new(1,narrow and -28 or -170,0,35),UDim2.fromOffset(15,42),14)
  button(equipment,"MicroSpeaker",data.amplifierEquipped and "UNEQUIP" or data.amplifierOwned and "EQUIP" or tostring(Config.MicroSpeakerPrice).." COINS",UDim2.fromOffset(135,38),UDim2.new(1,-149,0,narrow and 90 or 24),function() action:FireServer("MicroSpeaker") end)
  info("Movement pass: repeated jumps (24-stud height limit) and consecutive rolls only in safe areas. Arena cooldowns always apply."..(Config.MovementPassId==0 and " Purchase setup is not available yet." or ""),70)
  for name,color in pairs(Config.Auras) do
   local c=card(56);label(c,name,UDim2.new(1,-158,0,36),UDim2.fromOffset(15,10),17,color)
   button(c,name,data.aura==name and "EQUIPPED" or "USE COLOR",UDim2.fromOffset(126,36),UDim2.new(1,-140,0,10),function() action:FireServer("SetAura",name) end)
  end
 elseif selected=="Map" then
  title.Text="CITY & COAST";subtitle.Text="Arena District: 40% PvP. Outer neighborhoods and beach: 60% safe."
  local c=card(250)
  local map=frame(c,"Map",UDim2.new(1,-26,1,-26),UDim2.fromOffset(13,13),Color3.fromRGB(45,66,72))
  local function area(t,x,y,w,h,col) local f=frame(map,t,UDim2.fromScale(w,h),UDim2.fromScale(x,y),col);local l=label(f,t,UDim2.fromScale(1,1),UDim2.new(),13);l.TextXAlignment=Enum.TextXAlignment.Center;return f end
  area("SAFE NORTH",0,0,1,.2,Color3.fromRGB(50,93,82));area("SAFE\nWEST",0,.2,.166,.6,Color3.fromRGB(50,93,82));area("SAFE\nEAST",.833,.2,.167,.6,Color3.fromRGB(50,93,82))
  area("ARENA DISTRICT • PvP\n40% of playable land",.166,.2,.667,.6,Color3.fromRGB(136,65,70));area("BARCELONETA • SAFE BEACH",0,.8,1,.2,Color3.fromRGB(159,137,91))
  local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart");if root then local pos=root.Position;mapDot=area("●",math.clamp((pos.X+720)/1440,0,.94),math.clamp((pos.Z+600)/1200,0,.94),.06,.06,gold) end
  info("Gold dot: you. Spawn: Plaça del Sol, southwest. Beach: south. Coffee: west promenade café → music stage. Race: lifeguard start → east promenade finish. PvP ends at the marked district boundary.",86)
 else
  title.Text="SETTINGS & CONTROLS";subtitle.Text="Keep the action comfortable and easy to read."
  info("Hold E / SCREAM, use mic, release: fire toward aim\nQ / tap DODGE: roll with a 4-second cooldown\nShift / tap SPRINT: 10 seconds of sprint, then a 5-second rest\nT: talk to nearby residents • F: quest interactions • B: toggle menu",125)
  local c=card(58);button(c,"Volume","AUDIO: "..math.floor(data.settings.volume*100).."%",UDim2.new(1,-24,0,38),UDim2.fromOffset(12,10),function() action:FireServer("SetSettings",{volume=data.settings.volume>=.99 and 0 or math.min(1,data.settings.volume+.25)}) end)
  local d=card(58);button(d,"ReducedFX","REDUCED EFFECTS: "..(data.settings.reducedShake and "ON" or "OFF"),UDim2.new(1,-24,0,38),UDim2.fromOffset(12,10),function() action:FireServer("SetSettings",{reducedShake=not data.settings.reducedShake}) end)
 end
 -- Restore only after AutomaticCanvasSize has measured the replacement cards.
 task.spawn(function()
  Run.Heartbeat:Wait()
  if revision~=renderRevision then return end
  content.CanvasPosition=Vector2.new(0,math.clamp(scroll.Y,0,math.max(0,content.AbsoluteCanvasSize.Y-content.AbsoluteWindowSize.Y)))
 end)
end
for i,name in ipairs({"Screams","Quests","Style","Map","Settings"}) do tabs[name]=button(modal,name,name:upper(),UDim2.fromOffset(126,34),UDim2.fromOffset(20+(i-1)*134,88),function() selected=name;render() end) end
local conversationNPC,conversationUntil
conversationPanel=frame(gui,"Conversation",UDim2.fromOffset(460,300),UDim2.fromScale(.5,.5));conversationPanel.AnchorPoint=Vector2.new(.5,.5);conversationPanel.Visible=false;conversationPanel.ZIndex=10
local conversationName=label(conversationPanel,"",UDim2.new(1,-80,0,36),UDim2.fromOffset(18,12),19,gold)
local conversationList=Instance.new("ScrollingFrame");conversationList.Size=UDim2.new(1,-36,1,-66);conversationList.Position=UDim2.fromOffset(18,54);conversationList.BackgroundTransparency=1;conversationList.BorderSizePixel=0;conversationList.ScrollBarThickness=4;conversationList.AutomaticCanvasSize=Enum.AutomaticSize.Y;conversationList.CanvasSize=UDim2.new();conversationList.Parent=conversationPanel
local conversationLayout=Instance.new("UIListLayout");conversationLayout.Padding=UDim.new(0,10);conversationLayout.SortOrder=Enum.SortOrder.LayoutOrder;conversationLayout.Parent=conversationList
closeConversation=function()
 if conversationPanel.Visible then action:FireServer("EndConversation") end
 conversationPanel.Visible=false;conversationNPC=nil
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
remotes.State.OnClientEvent:Connect(function(nextData)
 data=nextData;refreshQuestObjects();stats.Text="LEVEL "..data.level.."    •    "..data.coins.." coins";health.Text=data.health.."/"..(data.maxHealth or 100);hf.Size=UDim2.fromScale(data.health/(data.maxHealth or 100),1)
 xpText.Text=data.level>=Config.MaxLevel and "MAX LEVEL" or data.xp.." / "..data.xpNext.." XP";xf.Size=UDim2.fromScale(data.level>=Config.MaxLevel and 1 or data.xp/data.xpNext,1)
 zone.Text=data.inWarZone and "ARENA DISTRICT • PvP ON" or "SAFE CITY • PvP OFF";zone.TextColor3=data.inWarZone and Color3.fromRGB(255,140,139) or white
 testButton.Visible=data.devAccess==true
 local q=Config.GetQuest(data.activeQuest);local v=q and data.quests[q.id]
 tracked.Text=q and (q.name.."\n"..(data.questStep or "").."\n"..(v and v.progress or 0).."/"..q.goal..(data.questTime>0 and "  •  "..data.questTime.."s left" or "")) or ""
 if data.message then notify(data.message) end
 if data.conversation then showConversation(data.conversation) end
 if modal.Visible then render() end
end)
UIS.InputBegan:Connect(function(input,processed)
 if processed then return end
 local k=input.KeyCode
 if k==Enum.KeyCode.E then beginCapture("keyboard") elseif k==Enum.KeyCode.Q then dodge() elseif k==Enum.KeyCode.B then toggle()
 elseif k==Enum.KeyCode.M then selected="Map";modal.Visible=not modal.Visible;render()
 elseif k==Enum.KeyCode.LeftShift then action:FireServer("Sprint",true)
 elseif k==Enum.KeyCode.T and talkTarget then action:FireServer("Talk",talkTarget:GetAttribute("NpcId") or talkTarget.Name) end
end)
UIS.InputEnded:Connect(function(input)
 if input.KeyCode==Enum.KeyCode.E then releaseCapture("keyboard")
 elseif captureSource==input or (typeof(captureSource)=="Instance" and captureSource.UserInputType==Enum.UserInputType.MouseButton1 and input.UserInputType==Enum.UserInputType.MouseButton1) then releaseCapture(captureSource) end
 if input.KeyCode==Enum.KeyCode.LeftShift then action:FireServer("Sprint",false) end
end)
p.CharacterRemoving:Connect(function() cancelCapture();if closeConversation then closeConversation() end end)
UIS.WindowFocusReleased:Connect(function() sprinting=false;cancelCapture();action:FireServer("Sprint",false) end)
local function fxPart(position,color,size)
 local f=Instance.new("Part");f.Anchored=true;f.CanCollide=false;f.CanTouch=false;f.CanQuery=false;f.Material=Enum.Material.Neon;f.Color=color;f.Size=size;f.Position=position;f.Transparency=.3;f.Parent=workspace;Debris:AddItem(f,1.1);return f
end
remotes.Effect.OnClientEvent:Connect(function(kind,pos,id,aura,direction,length,beamWidth)
 local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart");if root and (root.Position-pos).Magnitude>180 then return end
 if kind=="Break" then
  for i=1,6 do local chip=fxPart(pos,Config.Auras[id] or gold,Vector3.new(.5,.5,.5));Tween:Create(chip,TweenInfo.new(.45),{Position=pos+Vector3.new(math.cos(i)*3,2,math.sin(i)*3),Transparency=1}):Play() end;return
 end
 local color=Config.Auras[kind=="Dodge" and id or aura] or gold
 if kind=="Dodge" then local f=fxPart(pos,color,Vector3.new(2,3,2));Tween:Create(f,TweenInfo.new(.35),{Transparency=1,Size=Vector3.new(5,1,5)}):Play();return end
 local s=Config.GetSound(id);if not s then return end
 -- Actual voice is carried by Roblox proximity audio. Never play a recorded attack.
 direction=direction or Vector3.new(0,0,-1);length=length or Config.VoiceCombat.Stats(data.level,1,false).range
 ScreamEffects.Render(s.effect,pos,direction,length,beamWidth or 4,color,data.settings.reducedShake,s.variant)
end)
local elapsed=0
local lastViewport,lastTouch
Run.RenderStepped:Connect(function(dt)
 local viewport=gui.AbsoluteSize
 local touch=UIS.TouchEnabled
 local layoutChanged=viewport~=lastViewport or touch~=lastTouch
 if layoutChanged then lastViewport=viewport;lastTouch=touch;toastWidth=0 end
 local notificationWidth=math.min(640,viewport.X-32)
 if notificationWidth~=toastWidth then
  toastWidth=notificationWidth;toast.TextSize=viewport.X<820 and 14 or 16
  local textHeight=TextService:GetTextSize(toast.Text,toast.TextSize,toast.Font,Vector2.new(notificationWidth,10000)).Y
  toast.Size=UDim2.fromOffset(notificationWidth,math.min(viewport.Y*.35,textHeight+12))
 end
 if layoutChanged then conversationPanel.Size=UDim2.fromOffset(math.min(460,viewport.X-24),math.min(340,viewport.Y-36)) end
 if conversationPanel.Visible then
  local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
  local npcRoot=conversationNPC and conversationNPC.Parent and conversationNPC:FindFirstChild("HumanoidRootPart")
  if modal.Visible or not root or not npcRoot or (root.Position-npcRoot.Position).Magnitude>18 or os.clock()>conversationUntil then closeConversation() end
 end
 saveNotice.Text=data.testSession and "TEST SESSION · progress is temporary" or data.savingDelayed and "Save delayed · retrying automatically" or data.savingAvailable==false and "Temporary progress · saving unavailable" or ""
 saveNotice.Visible=not modal.Visible and viewport.X>=820
 if viewport.X<820 then
  if data.testSession or data.savingAvailable==false then xpText.Text="TEMPORARY PROGRESS • not saved"
  elseif data.savingDelayed then xpText.Text="SAVE DELAYED • retrying" end
 end
 if layoutChanged then
 micScale.Scale=1
 local micWidth=math.min(430,viewport.X-24);local micNarrow=micWidth<400
 micPanel.Size=UDim2.fromOffset(micWidth,micNarrow and 320 or 260);micTitle.TextSize=micNarrow and 18 or 21
 local calibrate=micPanel.Calibrate;local retry=micPanel.Retry
 calibrate.Size=UDim2.fromOffset(micNarrow and micWidth-36 or 188,UIS.TouchEnabled and 44 or 36);retry.Size=calibrate.Size
 calibrate.Position=UDim2.fromOffset(18,micNarrow and 224 or 208);retry.Position=UDim2.fromOffset(micNarrow and 18 or 224,micNarrow and 270 or 208)
 end
 micPanel.Visible=not mic.ready and not modal.Visible and not devPanel.Visible;micStatus.Text=mic.status
 if reportedReady~=mic.ready or (data.micReady~=mic.ready and os.clock()>readyReportAt) then reportedReady=mic.ready;readyReportAt=os.clock()+1;action:FireServer("MicReady",mic.ready) end
 if captureSource and blocked() then cancelCapture() end
 local gameplayVisible=mic.ready and not modal.Visible and not devPanel.Visible and not conversationPanel.Visible
 local showTouchControls=originalTouchControls and not modal.Visible and not devPanel.Visible and not conversationPanel.Visible and not micPanel.Visible
 if GuiService.TouchControlsEnabled~=showTouchControls then GuiService.TouchControlsEnabled=showTouchControls end
 meter.Visible=gameplayVisible;reticle.Visible=UIS.TouchEnabled and gameplayVisible
 local power=mic.power;meterFill.Size=UDim2.fromScale(power,1)
 local range=Config.VoiceCombat.Stats(data.level,power,data.amplifierEquipped).range
 meterText.Text=string.format("SCREAM POWER %d%% • %.0f studs",math.floor(power*100),range)
 if layoutChanged then
 local short=viewport.Y<550
 menuScale.Scale=1
 local width=math.min(720,viewport.X-24)
 modal.Size=UDim2.fromOffset(width,math.min(620,viewport.Y-76));modal.Position=UDim2.new(.5,0,0,64)
 devPanel.Size=UDim2.fromOffset(230,math.min(330,viewport.Y-76));devPanel.Position=UDim2.new(1,-244,0,64)
 title.TextSize=width<620 and 20 or 23
 subtitle.Visible=not short;subtitle.Size=UDim2.new(1,-44,0,width<620 and 42 or 25)
 local tabY=short and 54 or width<620 and 102 or 88
 local columns=width<360 and 3 or 5;local rows=math.ceil(5/columns)
 local tabWidth=(width-40-(columns-1)*6)/columns
 for i,name in ipairs({"Screams","Quests","Style","Map","Settings"}) do
  local b=tabs[name];b.Size=UDim2.fromOffset(tabWidth,44);b.Position=UDim2.fromOffset(20+((i-1)%columns)*(tabWidth+6),tabY+math.floor((i-1)/columns)*50);b.TextSize=width<620 and 12 or 14
 end
 content.Position=UDim2.fromOffset(20,tabY+rows*50+4);content.Size=UDim2.new(1,-40,1,-(tabY+rows*50+18))
 if width~=lastLayoutWidth then lastLayoutWidth=width;if modal.Visible then render() end end
 -- Keep desktop controls compact; smaller displays retain readable button text.
 local tight=viewport.X<380
 shop.Size=UDim2.fromOffset(tight and 90 or 125,touch and 44 or 36);shop.Text=tight and "SCREAMS" or "SCREAMS [B]"
 questsToggle.Size=UDim2.fromOffset(tight and 78 or 95,touch and 44 or 36);questsToggle.Position=UDim2.fromOffset(tight and 98 or 134,0)
 testButton.Size=UDim2.fromOffset(tight and 90 or 112,touch and 44 or 32);testButton.Position=UDim2.new(1,tight and -104 or -126,0,14)
 hud.Position=(touch or viewport.X<820) and UDim2.fromOffset(14,64) or UDim2.new(0,14,1,-108)
 controls.Position=UDim2.new(1,-274,1,touch and -195 or -102)
 talkButton.Position=UDim2.new(.5,-60,1,touch and -249 or -108)
 talkButton.Size=UDim2.fromOffset(120,touch and 44 or 34)
 controls.Size=UDim2.fromOffset(260,touch and 96 or 88)
 tracked.Position=UDim2.fromOffset(16,(touch or viewport.X<820) and 160 or 64)
 sprintButton.TextSize=touch and 12 or 14;sprintButton.Size=UDim2.fromOffset(164,touch and 44 or 32)
 end
 hud.Visible=gameplayVisible;controls.Visible=gameplayVisible
 tracked.Visible=gameplayVisible and tracked.Text~="";zone.Visible=viewport.X>740 and mic.ready
 local now=workspace:GetServerTimeNow();local protected=math.max(0,(p:GetAttribute("ProtectionEnds") or 0)-now)
 castButton.Text=protected>0 and "PROTECTED "..math.ceil(protected).."s" or os.clock()<nextCast and string.format("SCREAM %.1fs",nextCast-os.clock()) or captureSource and "RELEASE TO FIRE" or "HOLD SCREAM [E]"
 castButton.BackgroundColor3=protected>0 and muted or gold
 local cd=math.max(0,(p:GetAttribute("DodgeReady") or 0)-now);dodgeButton.Text=cd>0 and string.format("DODGE %.1fs",cd) or "DODGE [Q]"
 local rest=p:GetAttribute("SprintCooldown") or 0;sprintButton.Text=rest>0 and string.format("REST %.1fs",rest) or string.format("SPRINT %.1fs [SHIFT]",p:GetAttribute("SprintCharge") or 10)
 if os.clock()>toastUntil then toast.Text="" end
 aimInfo.Visible=gameplayVisible
 elapsed+=dt;if elapsed<.15 then return end;elapsed=0
 aimInfo.Text=""
 if aimInfo.Visible then
  local _,hit=aimRay();local object=hit and hit.Instance
  while object and object~=workspace and not object:GetAttribute("RequiredLevel") do object=object.Parent end
  if object and object~=workspace then
   local required=object:GetAttribute("RequiredLevel");local hp=object:GetAttribute("ObjectHealth") or 0
   local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
   local rangeLimit=Config.VoiceCombat.Stats(data.level,1,data.amplifierEquipped).maxRange
   local far=root and (hit.Position-root.Position).Magnitude>rangeLimit+2
   local kind=object:GetAttribute("ObjectName") or object:GetAttribute("DestructibleType") or object.Name
   aimInfo.Text=string.format("%s · LEVEL %d\n%s",kind,required,data.level<required and "LOCKED" or far and "OUT OF MAX RANGE" or string.format("%d / %d durability",hp,object:GetAttribute("ObjectMaxHealth") or hp))
   local repairSeconds=math.max(0,math.ceil((object:GetAttribute("RepairAt") or 0)-workspace:GetServerTimeNow()))
   if repairSeconds>0 and hp<(object:GetAttribute("ObjectMaxHealth") or hp) then
    aimInfo.Text..=string.format("\nRepair in %d:%02d",math.floor(repairSeconds/60),repairSeconds%60)
   end
   aimInfo.TextColor3=(data.level<required or far) and muted or gold
  end
 end
 local root=p.Character and p.Character:FindFirstChild("HumanoidRootPart")
 if os.clock()>=nextResidentUi then
  nextResidentUi=os.clock()+.1
  talkTarget=refreshResidentLabels(root,workspace.CurrentCamera,game:GetService("CollectionService"):GetTagged("CityResident"))
 end
 if root and mapDot and mapDot.Parent then mapDot.Position=UDim2.fromScale(math.clamp((root.Position.X+720)/1440,0,.94),math.clamp((root.Position.Z+600)/1200,0,.94)) end
 talkButton.Visible=talkTarget~=nil and mic.ready and not modal.Visible and not devPanel.Visible and not conversationPanel.Visible
end)
action:FireServer("Sync")

-- JumpRequest supports the built-in keyboard, controller and touch jump controls.
UIS.JumpRequest:Connect(function()
 local character=p.Character;local h=character and character:FindFirstChildOfClass("Humanoid")
 if h and h.FloorMaterial==Enum.Material.Air and data.movementPass and not data.inWarZone and not blocked() then action:FireServer("ExtraJump") end
end)
