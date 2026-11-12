"""Build-only full-warning native layout fixture. No execution/device claims."""
from pathlib import Path
import json, re, subprocess, sys
root=Path(__file__).resolve().parents[1];out=root/'build'
subprocess.run([sys.executable,str(root/'tests/build_ui_preview.py'),'390','844'],cwd=root,check=True)
source=(out/'StudioUIPreview.luau').read_text(encoding='utf-8')
source=source[:source.rindex('local report={}')] + r"""
local checks=0;local rows={}
local function check(ok,message)assert(ok,message);checks+=1 end
local function settle()for _=1,3 do Run.RenderStepped:Wait() end;task.wait(.2) end
local function overlaps(a,b)
 local x,y=a.AbsolutePosition,a.AbsoluteSize;local u,v=b.AbsolutePosition,b.AbsoluteSize
 return x.X<u.X+v.X and u.X<x.X+y.X and x.Y<u.Y+v.Y and u.Y<x.Y+y.Y
end
local warnings=__REAL_SAVE_WARNINGS__
mic.ready=true;windowFocused=true;micSetupOpen=false
for _,view in ipairs({{320,315,true},{640,360,true},{390,844,true},{844,390,true},{1024,720,false},{1280,720,false}})do
 gui.Size=UDim2.fromOffset(view[1],view[2]);fixtureTouch=view[3]
 for _,dev in ipairs({false,true})do
  data.devAccess=dev;modal.Visible=false;devPanel.Visible=false;conversationPanel.Visible=false;settle()
  for _,message in ipairs(warnings)do
   notifications=modules.NotificationQueue.new();notify(message,true,"save");settle()
   check(noticeView.root.Visible,"Full warning unavailable without nearby NPC")
   check(toast.Text==message,"Full message was replaced")
   check(toast.TextFits,"Full canvas clipped text")
   if fixtureTouch then check(noticeView.scroll.AbsoluteSize.Y>=44,"Native scroll touch target below44px")end
   for _,target in ipairs({miniMapButton,testButton,shop,questsToggle,castButton,dodgeButton,sprintButton,talkButton})do
    if target.Visible and (target.Parent~=controls or controls.Visible)then check(not overlaps(noticeView.root,target),"Notice overlaps actionable "..target.Name)end
   end
   local remaining=notifications.active.remaining
   if noticeView.overflow then
    task.wait(.3);check(notifications.active.remaining==remaining,"Unexposed full text lost dwell")
    noticeView.scroll.CanvasPosition=Vector2.new(0,noticeView.contentHeight-noticeView.visibleHeight)
    settle();check(noticeView.atBottom,"Programmatic native scrolling did not expose bottom")
    check(toast.AbsolutePosition.Y+toast.AbsoluteSize.Y<=noticeView.root.AbsolutePosition.Y+noticeView.root.AbsoluteSize.Y-16+1,"Last line hidden behind scroll cue")
   end
   windowFocused=false;settle();remaining=notifications.active.remaining;task.wait(.3)
   check(notifications.active.remaining==remaining,"Inactive window consumed notice")
   windowFocused=true;settle()
   table.insert(rows,{viewport=tostring(gui.AbsoluteSize),testTools=dev,text=message,overflow=noticeView.overflow,position=tostring(noticeView.root.AbsolutePosition),size=tostring(noticeView.root.AbsoluteSize),canvas=tostring(noticeView.scroll.CanvasSize),textFits=toast.TextFits})
   notifications:Remove("save");settle();check(not noticeView.root.Visible,"Recovered warning retained viewport")
  end
 end
end
-- Actual modal helper with a failed-purchase notice; no purchase request occurs.
gui.Size=UDim2.fromOffset(640,360);fixtureTouch=true;notifications=modules.NotificationQueue.new()
toggleTab("Shop");notify("Roblox could not open this purchase. Please try again.",true);settle()
check(modal.Visible and noticeView.root.Visible,"Shop error hidden by menu")
check(not overlaps(noticeView.root,modal.Close),"Shop error blocks Close")
for _,tab in pairs(tabs)do check(not overlaps(noticeView.root,tab),"Shop error blocks navigation tab")end
check(toast.TextFits,"Shop error full canvas clipped")
-- Same measured width/height, changed horizontal center must actually move.
gui.Size=UDim2.fromOffset(1024,720);fixtureTouch=false;settle();local before=noticeView.root.AbsolutePosition.X
gui.Size=UDim2.fromOffset(1280,720);settle();check(noticeView.root.AbsolutePosition.X>before,"Cached measurement froze native position")
closeMenu();notifications=modules.NotificationQueue.new();settle()
local Http=game:GetService("HttpService")
for index,row in ipairs(rows)do print("NOTICE_LAYOUT_ROW "..Http:JSONEncode({index=index,row=row}))end
print("NOTICE_LAYOUT_RESULT "..Http:JSONEncode({checks=checks,rows=#rows,limits="Synthetic viewport, state, mic and programmatic scroll/helper calls. No physical phone, thumbstick reachability, real saves or human reading claim. Nearby-NPC fallback requires separate mocked callback evidence."}))
"""
bootstrap=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text(encoding='utf-8-sig')
profile=(root/'src/ServerScriptService/Profiles.luau').read_text(encoding='utf-8-sig')
recovery=re.search(r'local RECOVERY_NOTICE="([^"]+)"',profile).group(1)
warnings=["Saving is unavailable. Progress from here is temporary; rejoin before continuing progression.","Save delayed. Your progress is still in this server; saving will retry automatically."]
assert all(text in bootstrap for text in warnings)
for suffix in (" Another session owns this profile; progress here is temporary. Rejoin shortly."," Saving is unavailable; progress here is temporary."):
 assert suffix.strip() in profile
 warnings.append(recovery+suffix)
assert [len(text)for text in warnings]==[93,85,142,114]
source=source.replace('__REAL_SAVE_WARNINGS__','{'+','.join(json.dumps(text)for text in warnings)+'}')
client=out/'NoticeLayoutReview.client.luau';client.write_text(source,encoding='utf-8')
subprocess.run(['luau-compile',str(client)],stdout=subprocess.DEVNULL,check=True)
project={'name':'NoticeLayoutReview_DO_NOT_PUBLISH','tree':{'$className':'DataModel','ReplicatedStorage':{'$className':'ReplicatedStorage','Shared':{'$path':str(root/'src/ReplicatedStorage/Shared')}},'StarterPlayer':{'$className':'StarterPlayer','StarterPlayerScripts':{'$className':'StarterPlayerScripts','Review':{'$path':str(client)}}},'Workspace':{'$className':'Workspace','Floor':{'$className':'Part','$properties':{'Anchored':True,'Size':[40,1,40],'Position':[0,-5,0]}}}}}
path=out/'NoticeLayoutReview.project.json';path.write_text(json.dumps(project))
subprocess.run(['rojo','build',str(path),'-o',str(out/'NoticeLayoutReview.rbxl')],check=True)
print('Built/compiled full-warning layout fixture only; native execution NOT performed.')
