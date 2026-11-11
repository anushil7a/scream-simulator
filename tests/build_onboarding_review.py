"""Disposable actual-client onboarding UI; synthetic mic, remotes and focus. No persistence.
Run in local Studio, join numbered ONBOARDING_CHUNK output, then Stop.
"""
from pathlib import Path
import json,subprocess,sys
root=Path(__file__).resolve().parents[1];out=root/'build'
subprocess.run([sys.executable,str(root/'tests/build_studio_harness.py')],cwd=root,check=True)
subprocess.run([sys.executable,str(root/'tests/build_ui_preview.py'),'390','844'],cwd=root,check=True)
def replace_once(text,old,new):
    assert text.count(old)==1,(old,text.count(old))
    return text.replace(old,new)
s=(out/'StudioUIPreview.luau').read_text()
assert s.count('\nlocal report={}')==1
s=s.split('\nlocal report={}')[0]
s=replace_once(s,'ready=true,power=.55,status="UI preview: simulated mic"','ready=false,power=0,status="UI preview: synthetic calibration readiness"')
s=replace_once(s,'local receiver\nlocal sample=','local receiver\nlocal fixtureVerbs={}\nlocal sample=')
s=replace_once(s,'level=100,xp=30,xpNext=1800','level=1,xp=0,xpNext=103')
s=replace_once(s,'activeQuest="garden",','')
s=replace_once(s,'FireServer=function(_,verb) if verb=="Sync"','FireServer=function(_,verb,arg) table.insert(fixtureVerbs,verb); if verb=="SustainedBegin" then p:SetAttribute("SustainedActive",true);p:SetAttribute("SustainedSequence",arg.sequence) elseif verb=="SustainedStop" then p:SetAttribute("SustainedActive",false) end; if verb=="Sync"')
s+='''
local Http=game:GetService("HttpService")
local rowSerial=0
local function observe(stage)
 local seen={};local clipped={}
 for _,obj in ipairs(gui:GetDescendants()) do
  if obj:IsA("TextLabel") or obj:IsA("TextButton") then
   local visible=obj.Visible;local parent=obj.Parent
   while parent and parent~=screen do if parent:IsA("GuiObject") and not parent.Visible then visible=false end;parent=parent.Parent end
   if visible and obj.Text~="" then table.insert(seen,obj.Text);if not obj.TextFits then table.insert(clipped,obj.Text) end end
  end
 end
 local all=table.concat(seen," | "):lower()
 local avoidsProfanity=all:find("avoid profanity",1,true)~=nil
 local moderation=all:find("roblox records and moderates voice",1,true)~=nil or all:find("roblox records voice for moderation",1,true)~=nil
 if stage=="setup" then
  assert(avoidsProfanity and moderation,"Setup voice safety disclosure missing")
  local found=0
  for _,obj in ipairs(micPanel:GetDescendants()) do
   if obj:IsA("TextLabel") and obj.Text:find("Avoid profanity",1,true) then
    found+=1
    -- Allocated label fit only, not scroll viewport visibility or human accessibility.
    assert(obj.TextFits,"Native setup voice safety text does not fit its allocated label")
   end
  end
  assert(found==1,"Setup voice safety label duplicated or missing")
 end
 if stage=="settings" then
  assert(avoidsProfanity and moderation and all:find("rating and settings",1,true) and all:find("volume, not words",1,true) and all:find("stopping attacks does not mute voice",1,true),"Settings voice safety distinctions missing")
  local found=0
  for _,obj in ipairs(content:GetDescendants()) do
   if obj:IsA("TextLabel") and obj.Text:find("VOICE SAFETY",1,true) then found+=1;assert(obj.TextFits,"Native voice safety text does not fit its allocated card") end
  end
  assert(found==1,"Settings voice safety card duplicated or missing")
 end
 local pos,size=castButton.AbsolutePosition,castButton.AbsoluteSize
 local hits=p.PlayerGui:GetGuiObjectsAtPosition(pos.X+size.X/2,pos.Y+size.Y/2)
 local top=hits[1];local reachable=top==castButton or top and top:IsDescendantOf(castButton)
 local report={stage=stage,avoidsProfanity=avoidsProfanity,robloxVoiceModeration=moderation,viewport=tostring(gui.AbsoluteSize),armed=sustainedControl.armed,normalSpeechWarning=all:find("normal speech",1,true)~=nil,voiceUnchanged=all:find("voice chat",1,true)~=nil or all:find("live voice",1,true)~=nil or all:find("does not mute voice",1,true)~=nil,button=castButton.Text,buttonSize=tostring(size),buttonPosition=tostring(pos),controlsVisible=controls.Visible,reachable=reachable==true,clipped=clipped,text=seen,verbs=table.clone(fixtureVerbs),micReady=mic.ready}
 rowSerial+=1
 local encoded=Http:JSONEncode(report);local chunks={};local start=1
 while start<=#encoded do
  local nextByte=utf8.offset(encoded,201,start) or (#encoded+1)
  table.insert(chunks,encoded:sub(start,nextByte-1));start=nextByte
 end
 for i,chunk in ipairs(chunks) do print("ONBOARDING_CHUNK "..rowSerial.." "..i.."/"..#chunks.." "..chunk) end
end
local fixtureCharacter=p.Character or p.CharacterAdded:Wait();fixtureCharacter:WaitForChild("Humanoid")
windowFocused=true;data.activeQuest=nil;data.achievements={};modal.Visible=false
for _,view in ipairs({{320,568,true},{390,844,true},{844,390,true},{1280,720,false}}) do
 gui.Size=UDim2.fromOffset(view[1],view[2]);fixtureTouch=view[3];mic.ready=false
 Run.RenderStepped:Wait();Run.RenderStepped:Wait();observe("setup")
end
gui.Size=UDim2.fromOffset(390,844);fixtureTouch=true;mic.ready=true;data.micReady=true;mic.power=0
Run.RenderStepped:Wait();task.wait(.5);observe("first-ready")
for _,view in ipairs({{320,568,true},{390,844,true},{844,390,true},{1280,720,false}}) do
 gui.Size=UDim2.fromOffset(view[1],view[2]);fixtureTouch=view[3];windowFocused=true;sustainedControl:SetArmed(true);mic.power=0
 notifications=modules.NotificationQueue.new();task.wait(.5);observe("on")
 mic.power=.8;task.wait(.3);observe("synthetic-active")
 toggleVoice();task.wait(.15);observe("off")
 selected="Settings";modal.Visible=true;render();Run.RenderStepped:Wait();Run.RenderStepped:Wait();observe("settings");modal.Visible=false
end
gui.Size=UDim2.fromOffset(390,844);fixtureTouch=true;windowFocused=true;mic.power=0;sustainedControl:SetArmed(true)
notifications=modules.NotificationQueue.new();task.wait(.5);observe("manual-ready")
castButton.Activated:Connect(function()task.defer(function()task.wait(.1);observe("manual-click")end)end)
UIS.InputBegan:Connect(function(input,processed) if not processed and input.KeyCode==Enum.KeyCode.E then task.defer(function()task.wait(.1);observe("manual-key")end) end end)
print("ONBOARDING_READY synthetic mic/remotes; no persistence")
-- Reuse the actual collection renderer for full-power stat/cooldown readability.
data.level=100;selected="Screams";modal.Visible=true
for _,view in ipairs({{390,844,true},{844,390,true},{1280,720,false}}) do
 gui.Size=UDim2.fromOffset(view[1],view[2]);fixtureTouch=view[3]
 Run.RenderStepped:Wait();render();Run.RenderStepped:Wait();Run.RenderStepped:Wait()
 local found,clipped=0,{}
 for _,obj in ipairs(content:GetDescendants()) do
  if obj:IsA("TextLabel") and (obj.Text:find("FULL-POWER LIMITS",1,true) or obj.Text:find("Sound styles change audio",1,true)) then
   found+=1;if not obj.TextFits then table.insert(clipped,obj.Text) end
  end
 end
 print("BEAM_READOUT_RESULT",Http:JSONEncode({viewport=tostring(gui.AbsoluteSize),found=found,clipped=clipped,cooldown=sustainedRules.Cooldown}))
 assert(found==2 and #clipped==0,"Beam summary is missing or clipped")
end
'''
(out/'OnboardingReview.client.luau').write_text(s)
subprocess.run(['luau-compile',str(out/'OnboardingReview.client.luau')],stdout=subprocess.DEVNULL,check=True)
project={'name':'OnboardingReview_DO_NOT_PUBLISH','tree':{'$className':'DataModel','ReplicatedStorage':{'$className':'ReplicatedStorage','Shared':{'$path':str(root/'src/ReplicatedStorage/Shared')}},'StarterPlayer':{'$className':'StarterPlayer','StarterPlayerScripts':{'$className':'StarterPlayerScripts','Review':{'$path':str(out/'OnboardingReview.client.luau')}}},'Workspace':{'$className':'Workspace','Floor':{'$className':'Part','$properties':{'Anchored':True,'Size':[400,1,400],'Position':[0,-5,0]}}}}}
(out/'OnboardingReview.project.json').write_text(json.dumps(project));subprocess.run(['rojo','build',str(out/'OnboardingReview.project.json'),'-o',str(out/'OnboardingReview.rbxl')],check=True)
