"""Build isolated actual-client quest layout fixture; synthetic mic/remotes, no saves."""
from pathlib import Path
import json,subprocess,sys
root=Path(__file__).resolve().parents[1];out=root/'build'
subprocess.run([sys.executable,str(root/'tests/build_ui_preview.py'),'390','844'],cwd=root,check=True)
s=(out/'StudioUIPreview.luau').read_text(encoding='utf-8')
assert s.count('\nlocal report={}')==1
s=s.split('\nlocal report={}')[0]
s+=r"""
local Http=game:GetService("HttpService")
local checks=0;local function check(ok,message)assert(ok,message);checks+=1 end
local results={}
mic.ready=true;data.level=1;data.xp=0;data.training="Rookie";data.activeQuest=nil;data.questTime=0
selected="Quests";modal.Visible=true
local ok,err=xpcall(function()
 for _,known in ipairs({false,true})do
  data.quests={};data.availableQuests={}
  if known then
   for _,q in ipairs(Config.Quests)do data.availableQuests[q.id]=true;data.quests[q.id]={progress=q.goal,claimed=q.id=="nick"}end
  end
  for _,view in ipairs({{390,844,true},{844,390,true},{1280,720,false}})do
   gui.Size=UDim2.fromOffset(view[1],view[2]);fixtureTouch=view[3]
   Run.RenderStepped:Wait();Run.RenderStepped:Wait();render();Run.RenderStepped:Wait();Run.RenderStepped:Wait()
   local clipped={};local byId={};local order={}
   for _,obj in ipairs(content:GetDescendants())do
    if (obj:IsA("TextLabel") or obj:IsA("TextButton")) and obj.Text~="" and not obj.TextFits then table.insert(clipped,obj.Text)end
    if obj:IsA("TextButton") and Config.GetQuest(obj.Name) then
     check(byId[obj.Name]==nil,"Duplicate quest card "..obj.Name);byId[obj.Name]=obj;table.insert(order,{id=obj.Name,y=obj.AbsolutePosition.Y})
    end
   end
   check(#clipped==0,"Quest text clipped")
   check(title.TextFits,"Quest title clipped");check(subtitle.TextFits,"Quest subtitle clipped")
   check((byId.nick~=nil)==known,"Hidden quest discovery mismatch")
   for _,id in ipairs({"garden","beach"})do
    local button=byId[id];check(button~=nil,"Soler card missing")
    local description=""
    for _,obj in ipairs(button.Parent:GetChildren())do if obj:IsA("TextLabel") and obj.Text:find(Config.GetQuest(id).description,1,true)then description=obj.Text end end
    check(description~="","Soler objective hidden")
    check(known or description:find("To unlock: meet",1,true)~=nil,"Locked giver instruction missing")
    check(button.Text==(known and "CLAIM" or "MEET NPC"),"Quest state action changed")
   end
   table.sort(order,function(a,b)return a.y<b.y end)
   check(order[1].id=="crowd" and order[2].id=="dodge" and order[3].id=="arena","Combat tasks not first")
   check(#order==(known and 8 or 7),"Wrong visible quest count")
   table.insert(results,{width=view[1],height=view[2],known=known,cards=#order,clipped=#clipped})
  end
 end
end,debug.traceback)
local report={passed=ok,checks=checks,cases=results,error=not ok and tostring(err) or nil,synthetic=true}
workspace:SetAttribute("QuestCardsReviewResult",Http:JSONEncode(report))
print("QUEST_CARDS_RESULT",Http:JSONEncode(report))
gui.Size=UDim2.fromOffset(1280,720);fixtureTouch=false;data.availableQuests={};data.quests={};selected="Quests";modal.Visible=true
Run.RenderStepped:Wait();render()
"""
(out/'QuestCardsReview.client.luau').write_text(s,encoding='utf-8')
subprocess.run(['luau-compile',str(out/'QuestCardsReview.client.luau')],stdout=subprocess.DEVNULL,check=True)
project={'name':'QuestCardsReview_DO_NOT_PUBLISH','tree':{'$className':'DataModel','ReplicatedStorage':{'$className':'ReplicatedStorage','Shared':{'$path':str(root/'src/ReplicatedStorage/Shared')}},'StarterPlayer':{'$className':'StarterPlayer','StarterPlayerScripts':{'$className':'StarterPlayerScripts','Review':{'$path':str(out/'QuestCardsReview.client.luau')}}},'Workspace':{'$className':'Workspace','Floor':{'$className':'Part','$properties':{'Anchored':True,'Size':[400,1,400],'Position':[0,-5,0]}}}}}
(out/'QuestCardsReview.project.json').write_text(json.dumps(project))
subprocess.run(['rojo','build',str(out/'QuestCardsReview.project.json'),'-o',str(out/'QuestCardsReview.rbxl')],check=True)
print('Built isolated QuestCardsReview; not executed by this command')
