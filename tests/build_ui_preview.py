"""Visual/layout-only fixture. No real microphone, combat or server remotes are exercised.
Run in a fresh disposable Studio Client session and Stop afterward to clean listeners.
"""
from pathlib import Path
import sys
import build_studio_harness
root=Path(__file__).resolve().parents[1]
width=int(sys.argv[1]) if len(sys.argv)>1 else 390
height=int(sys.argv[2]) if len(sys.argv)>2 else 844
source=(root/'build/StudioClientHarness.luau').read_text()
source=source.replace('local mic=modules.Microphone.new()', '''local mic={ready=true,power=.55,status="UI preview: simulated mic",Cancel=function() end,Begin=function() return false end,Release=function() return 0 end,Check=function() end,Calibrate=function() end}''')
source=source.replace('local remotes=RS:WaitForChild("ScreamRemotes")','''local receiver
local sample={level=100,xp=30,xpNext=1800,coins=1500,health=135,maxHealth=135,sound="TinyAah",aura="Gold",quests={},availableQuests={},settings={volume=.55,reducedShake=false},micReady=true,devAccess=true,savingAvailable=true,protection=0,dodgeCooldown=0,castCooldown=0,questTime=90}
for _,q in ipairs(Config.Quests) do sample.availableQuests[q.id]=true;sample.quests[q.id]={progress=0} end
local actionMock={FireServer=function(_,verb) if verb=="Sync" and receiver then receiver(sample) end end}
local remotes={WaitForChild=function() return actionMock end,State={OnClientEvent={Connect=function(_,fn) receiver=fn end}},Effect={OnClientEvent={Connect=function() end}}}''')
original='local gui=Instance.new("ScreenGui");gui.Name="ScreamUI";gui.ResetOnSpawn=false;gui.ZIndexBehavior=Enum.ZIndexBehavior.Sibling;gui.Parent=p:WaitForChild("PlayerGui")'
replacement=f'''local screen=Instance.new("ScreenGui");screen.Name="LayoutPreview";screen.ResetOnSpawn=false;screen.Parent=p:WaitForChild("PlayerGui")
local gui=Instance.new("Frame");gui.Name="ScreamUI";gui.Size=UDim2.fromOffset({width},{height});gui.Position=UDim2.fromOffset(10,10);gui.BackgroundTransparency=1;gui.Parent=screen'''
assert original in source
source=source.replace(original,replacement).replace('workspace.CurrentCamera.ViewportSize',f'Vector2.new({width},{height})').replace('UIS.TouchEnabled','true' if width<820 else 'false')
source+='''
local report={}
for _,tab in ipairs({"Screams","Quests","Style","Map","Settings"}) do
 selected=tab;modal.Visible=true;render();task.wait(.15)
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
 table.insert(report,{tab=tab,clipped=clipped,undersized=undersized,horizontalOverflow=overflow,menuSize=tostring(modal.AbsoluteSize)})
end
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
return report
'''
(root/'build/StudioUIPreview.luau').write_text(source)
print('UI-only preview:',width,height)
