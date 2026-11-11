"""Native UI-only save priority fixture; synthetic State packets, no server/store."""
from pathlib import Path
import json,subprocess,sys
root=Path(__file__).resolve().parents[1];out=root/'build'
subprocess.run([sys.executable,str(root/'tests/build_ui_preview.py'),'390','844'],cwd=root,check=True)
s=(out/'StudioUIPreview.luau').read_text().split('\nlocal report={}')[0]
control='--negative-control' in sys.argv
if control:
 needle='key=="save" and 2 or urgent and 1 or 0'
 assert s.count(needle)==1
 s=s.replace(needle,'urgent and 1 or 0')
s+='''
local character=p.Character or p.CharacterAdded:Wait();character:WaitForChild("Humanoid")
windowFocused=true;mic.power=0;mic.ready=true;modal.Visible=false
task.wait(.5);sustainedControl:SetArmed(false)
local Http=game:GetService("HttpService")
local delayed="Save delayed. Your progress is still in this server; saving will retry automatically."
local unavailable="Saving is unavailable. Progress from here is temporary; rejoin before continuing progression."
local function packet(text,urgent,key,available,late)
 local value=table.clone(sample);value.message=text;value.messageUrgent=urgent;value.messageKey=key
 value.savingAvailable=available;value.savingDelayed=late;value.recoveryWarning=false;receiver(value)
end
local function settle()Run.RenderStepped:Wait();Run.RenderStepped:Wait()end
local function sampleWarning(expected,seconds)
 local started=os.clock();local frames=0;local peak=0
 repeat
  assert(toast.Visible and toast.Text==expected,"Native save warning displaced")
  assert(toast.TextFits,"Native save warning clipped")
  assert(#notifications.pending<=8,"Native queue exceeded bound")
  peak=math.max(peak,#notifications.pending);frames+=1
  Run.RenderStepped:Wait()
 until os.clock()-started>=seconds
 return {frames=frames,seconds=os.clock()-started,peakPending=peak,text=expected}
end
local rows={}
for _,view in ipairs({{390,844,true},{844,390,true},{1280,720,false}}) do
 gui.Size=UDim2.fromOffset(view[1],view[2]);fixtureTouch=view[3];settle()
 notifications=modules.NotificationQueue.new()
 notify("Screams stay OFF. Finish mic setup or wait for gameplay to be ready, then turn them on.",true,"voice");settle()
 packet(delayed,true,"save",true,true)
 for i=1,20 do
  packet("Micro-speaker costs 250 coins. You need "..(250-i).." more.",true,nil,true,true)
  packet("Quest reward "..i,false,nil,true,true)
 end
 settle()
 local row={viewport=tostring(gui.AbsoluteSize),mixedMessages=40}
 row.delayed=sampleWarning(delayed,3.7)
 local remaining=notifications.active.remaining;packet(nil,false,nil,true,true)
 assert(notifications.active.remaining==remaining,"Snapshot restarted warning dwell")
 packet(unavailable,true,"save",false,false);settle()
 assert(notifications.active.key=="save","Replacement lost classification")
 for _,entry in ipairs(notifications.pending) do assert(entry.key~="save","Old save state survived replacement")end
 row.unavailable=sampleWarning(unavailable,3.9)
 -- Clear before natural expiry, so expiry cannot mask a missing clear hook.
 assert(notifications.active and notifications.active.key=="save" and notifications.active.remaining>0,"Clear test started after expiry")
 packet(nil,false,nil,true,false);settle()
 assert(toast.Text~=unavailable and toast.Text~=delayed,"Healthy state left stale rendered save warning")
 assert(not notifications.active or notifications.active.key~="save","Healthy state kept active save category")
 for _,entry in ipairs(notifications.pending) do assert(entry.key~="save","Healthy state kept pending save category")end
 -- Independent short phase proves interrupted reward resumes after early recovery.
 notifications=modules.NotificationQueue.new();notify("Quest reward retained")
 packet(delayed,true,"save",true,true);settle();assert(toast.Text==delayed,"Short warning not rendered")
 packet(nil,false,nil,true,false);settle();assert(toast.Text=="Quest reward retained","Recovery lost interrupted reward")
 row.healthyCleared=true;row.rewardResumed=true
 table.insert(rows,row);print("SAVE_NOTICE_NATIVE_ROW "..Http:JSONEncode(row))
end
print("SAVE_NOTICE_NATIVE_PASS "..Http:JSONEncode({rows=#rows,synthetic=true}))
'''
name='SaveNoticeControl' if control else 'SaveNoticeReview'
client=out/(name+'.client.luau');client.write_text(s)
subprocess.run(['luau-compile',str(client)],stdout=subprocess.DEVNULL,check=True)
project={'name':name+'_DO_NOT_PUBLISH','tree':{'$className':'DataModel','ReplicatedStorage':{'$className':'ReplicatedStorage','Shared':{'$path':str(root/'src/ReplicatedStorage/Shared')}},'StarterPlayer':{'$className':'StarterPlayer','StarterPlayerScripts':{'$className':'StarterPlayerScripts','Review':{'$path':str(client)}}},'Workspace':{'$className':'Workspace','Floor':{'$className':'Part','$properties':{'Anchored':True,'Size':[400,1,400],'Position':[0,-5,0]}}}}}
path=out/(name+'.project.json');path.write_text(json.dumps(project))
subprocess.run(['rojo','build',str(path),'-o',str(out/(name+'.rbxl'))],check=True)
