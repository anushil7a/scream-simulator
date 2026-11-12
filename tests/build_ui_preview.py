"""Visual/layout-only fixture. No real microphone, combat or server remotes are exercised.
Run in a fresh disposable Studio Client session and Stop afterward to clean listeners.
"""
from pathlib import Path
import sys
import build_studio_harness
root=Path(__file__).resolve().parents[1]
width=int(sys.argv[1]) if len(sys.argv)>1 else 390
height=int(sys.argv[2]) if len(sys.argv)>2 else 844
def replace_once(source, original, replacement):
    count = source.count(original)
    if count != 1:
        raise RuntimeError(f'UI preview substitution expected once, found {count}: {original[:80]}')
    return source.replace(original, replacement, 1)

source=(root/'build/StudioClientHarness.luau').read_text()
source=replace_once(source,'mic=mic.new()', '''mic={Destroy=function() end,ready=true,power=.55,status="UI preview: simulated mic",Cancel=function() end,CancelCalibration=function(self) self.phase=nil;self.phaseStarted=nil end,Begin=function() return false end,Release=function() return 0 end,Check=function() end,Calibrate=function() end}''')
source=replace_once(source,'local remotes=RS:WaitForChild("ScreamRemotes");if not clientCheckpoint() then return end','''local receiver
local sample={level=100,xp=30,xpNext=1800,coins=1500,activeQuest="garden",health=450,maxHealth=450,sound="TinyAah",aura="Gold",quests={},availableQuests={},settings={volume=.55,reducedShake=false},micReady=true,voiceEligible=true,voiceStatus="eligible",devAccess=true,savingAvailable=true,protection=0,dodgeCooldown=0,castCooldown=0,questTime=90}
sample.shop={ready=true,inventory={xp=2,coins=1},ends={xp=os.time()+1800,coins=0},serverNow=os.time()}
for _,q in ipairs(Config.Quests) do sample.availableQuests[q.id]=true;sample.quests[q.id]={progress=0} end
local actionMock={FireServer=function(_,verb) if verb=="Sync" and receiver then receiver(sample) end end}
local remotes={GetAttribute=function(_,name) return name=="AutomaticVoice" and true or nil end,WaitForChild=function() return actionMock end,State={OnClientEvent={Connect=function(_,fn) receiver=fn;return {Disconnect=function() if receiver==fn then receiver=nil end end} end}},Effect={OnClientEvent={Connect=function() return {Disconnect=function() end} end}}}''')
original='local gui=Instance.new("ScreenGui");ownClient(function() gui:Destroy() end);if not clientCheckpoint() then return end\ngui.Name="ScreamUI";gui.ResetOnSpawn=false;gui.ZIndexBehavior=Enum.ZIndexBehavior.Sibling;gui.Parent=playerGui'
replacement=f'''local screen=Instance.new("ScreenGui");ownClient(function() screen:Destroy() end);if not clientCheckpoint() then return end
screen.Name="LayoutPreview";screen.ResetOnSpawn=false;screen.ZIndexBehavior=Enum.ZIndexBehavior.Sibling;screen.Parent=playerGui
local gui=Instance.new("Frame");ownClient(function() gui:Destroy() end);if not clientCheckpoint() then return end
gui.Name="ScreamUI";gui.Size=UDim2.fromOffset({width},{height});gui.Position=UDim2.fromOffset(10,10);gui.BackgroundTransparency=1;gui.Parent=screen'''
source=replace_once(source,original,replacement).replace('workspace.CurrentCamera.ViewportSize',f'Vector2.new({width},{height})').replace('UIS.TouchEnabled','fixtureTouch')
source='local fixtureTouch=true\n'+source
source+='''
local report={}
for _,view in ipairs({{390,844,true},{844,390,true},{1280,720,false}}) do
 gui.Size=UDim2.fromOffset(view[1],view[2]);fixtureTouch=view[3]
 Run.RenderStepped:Wait();Run.RenderStepped:Wait()
for _,tab in ipairs({"Shop","Screams","Quests","Style","Map","Settings"}) do
 selected=tab;modal.Visible=true;render();Run.RenderStepped:Wait();Run.RenderStepped:Wait()
 local clipped={};local undersized={};local overflow={}
 for _,obj in ipairs(modal:GetDescendants()) do
  if obj:IsA("GuiObject") and obj.Parent:IsA("GuiObject") and not obj.Parent:IsA("ScrollingFrame") then
   if obj.AbsolutePosition.X+obj.AbsoluteSize.X>obj.Parent.AbsolutePosition.X+obj.Parent.AbsoluteSize.X+1 then table.insert(overflow,obj.Name) end
  end
  if (obj:IsA("TextLabel") or obj:IsA("TextButton")) and obj.Visible and obj.Text~="" then
   if not obj.TextFits then table.insert(clipped,{text=obj.Text,size=tostring(obj.AbsoluteSize),bounds=tostring(obj.TextBounds)}) end
   if obj.TextSize<12 then table.insert(undersized,obj.Text) end
  end
 end
 table.insert(report,{viewport=tostring(gui.AbsoluteSize),tab=tab,clipped=clipped,undersized=undersized,horizontalOverflow=overflow,menuSize=tostring(modal.AbsoluteSize)})
end
modal.Visible=false
for _,armed in ipairs({false,true}) do
 sustainedControl:SetArmed(armed);Run.RenderStepped:Wait();Run.RenderStepped:Wait()
 local clipped={};if not castButton.TextFits then table.insert(clipped,castButton.Text) end
 local expected=armed and "BEAMS: ON" or "BEAMS: OFF"
 assert(string.find(castButton.Text,expected,1,true),"Toggle status missing")
 assert(castButton.AbsoluteSize.X>=44 and castButton.AbsoluteSize.Y>=44,"Toggle touch target too small")
 assert(castButton.Selectable and controls.Visible,"Toggle unavailable")
 table.insert(report,{viewport=tostring(gui.AbsoluteSize),tab=expected,clipped=clipped,size=tostring(castButton.AbsoluteSize),text=castButton.Text})
end
for _,status in ipairs({"temporary","recovered","delayed"}) do
 local writable=status~="temporary"
 data.recoveryWarning=true;data.savingAvailable=writable;data.savingDelayed=status=="delayed"
 Run.RenderStepped:Wait();Run.RenderStepped:Wait()
 local notice=view[1]<820 and xpText or saveNotice
 local clipped={};if not notice.TextFits then table.insert(clipped,notice.Text) end
 assert(string.find(notice.Text,"progress may be missing",1,true),"Persistent rollback warning missing")
 if status=="delayed" then assert(string.find(notice.Text,view[1]<820 and "DELAYED" or "Save delayed",1,true),"Recovery masked delayed save") end
 table.insert(report,{viewport=tostring(gui.AbsoluteSize),tab="Recovery: "..status,clipped=clipped,text=notice.Text,size=tostring(notice.AbsoluteSize)})
end
data.recoveryWarning=nil;data.savingAvailable=true;data.savingDelayed=false
end
gui.Size=UDim2.fromOffset(390,844);fixtureTouch=true;Run.RenderStepped:Wait()
modal.Visible=false
showConversation({npc=p.Character,name="Mar Soler",line="The neighborhood flowerbeds could use a little care. Can you lend a hand today?",hint="Visit the three raised flowerbeds in Rambla Gardens.",quests={Config.Quests[2],Config.Quests[3]}})
task.wait(.15)
local dialogueClipped={}
for _,obj in ipairs(conversationPanel:GetDescendants()) do if (obj:IsA("TextLabel") or obj:IsA("TextButton")) and not obj.TextFits then table.insert(dialogueClipped,obj.Text) end end
table.insert(report,{tab="Conversation",menuSize=tostring(conversationPanel.AbsoluteSize),clipped=dialogueClipped})
closeConversation()
modal.Visible=false;mic.ready=false;mic.status="Roblox voice access is required. Enable eligible voice access in your account and allow microphone permission.";task.wait(.15)
local clipped={}
for _,obj in ipairs(micPanel:GetDescendants()) do if (obj:IsA("TextLabel") or obj:IsA("TextButton")) and not obj.TextFits then table.insert(clipped,obj.Text) end end
table.insert(report,{tab="Mic setup",menuSize=tostring(micPanel.AbsoluteSize),clipped=clipped})
notify("Nick: I lost THREE balls. You have 120 seconds! Check the north beach loungers, east of the pier, and the path north of this court. Hold F nearby.")
task.wait(.15)
table.insert(report,{tab="Long notification",clipped=not toast.TextFits,size=tostring(toast.AbsoluteSize)})
return report
'''
(root/'build/StudioUIPreview.luau').write_text(source)
print('UI-only preview:',width,height)
