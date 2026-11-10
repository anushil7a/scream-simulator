"""Real autosave/State/upgrade/receiver/queue path; synthetic stores/UI/time/coins."""
from pathlib import Path
import ast,subprocess,sys,tempfile
root=Path(__file__).resolve().parents[1]
client=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
server=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
# Reuse only the literal UI stubs, not the other suite's execution or checks.
tree=ast.parse((root/'tests/action_feedback.py').read_text())
setup=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='setup' for t in n.targets))
setup=setup.replace('local function notify(message,urgent)table.insert(notices,message);table.insert(urgentNotices,urgent==true)end',
 '''local notifications=require('../src/StarterPlayer/StarterPlayerScripts/NotificationQueue').new()
local function notify(message,urgent,key)notifications:Push(message,urgent,key)end''')
receiver=client[client.index('local lastMilestone'):client.index('connectClient(UIS.InputBegan')]
state=server[server.index('local function state('):server.index('Commerce.Start(')]
autosave=server[server.index('local function autosave('):server.index('task.spawn(function() while true do task.wait(60)')]
speaker=server[server.index('local function microSpeaker('):server.index('local function vendorPurchase(')]
extra='''
local Queue=require('../src/StarterPlayer/StarterPlayerScripts/NotificationQueue')
local sessions={[p]=s};p.Parent=true;p.UserId=7
function p:GetAttribute()return 10 end;function p:SetAttribute()end
s.data.level=10;s.data.xp=0;s.voice={nextCast=0};s.canSave=true;s.nextDodge=0;s.protectedUntil=0
Config.XPToNext=function()return 100 end;Config.GetDeliveryStop=function()end
Config.HealthForLevel=function()return 100 end
local function parts()end
local Soccer={Status=function()end};local QuestGuide={Step=function()end}
local Equipment={Sync=function()end};local TrainingRules={Recommended=function()return {name='Rookie'}end}
local Entitlements={HasSpectrum=function()return false end,HasMovement=function()return false end}
local Access={IsAuthorized=function()return false end};local game={}
Commerce.Status=function()return {} end
local latest;local stateRemote={FireClient=function(_,player,value)latest=value;receiver(value)end}
local saveMode='ownership';local Profiles={Save=function()return saveMode=='ok',saveMode end}
'''
checks='''
local checks=0;local function check(ok,msg)assert(ok,msg);checks+=1 end
local function frame()return notifications:Step(.1,true)end
local function hasSave()
 if notifications.active and notifications.active.key=='save' then return true end
 for _,e in ipairs(notifications.pending)do if e.key=='save' then return true end end
 return false
end
local saving='Saving is unavailable. Progress from here is temporary; rejoin before continuing progression.'
local delayed='Save delayed. Your progress is still in this server; saving will retry automatically.'
notify('Screams stay OFF. Finish mic setup or wait for gameplay to be ready, then turn them on.',true,'voice');frame()
autosave(p,s)
local seen={}
-- Coins change synthetically between actual insufficient-funds helper calls.
-- Eight distinct rejections plus normal rewards fill the pending queue in <1 second.
for i=1,8 do
 s.data.coins=i;microSpeaker(p,s,false);state(p,'Quest reward '..i)
 local text=frame();seen[text]=true
end
for _=1,1400 do seen[frame()]=true end
check(seen[saving],'Save warning evicted before any displayed frame')
-- Mixed sustained traffic cannot preempt or evict the active save warning.
notifications=Queue.new();s.canSave=true;s.saveDelayed=false;saveMode='transient';autosave(p,s)
check(latest.messageKey=='save' and latest.messageUrgent,'Autosave State lost save category')
for i=1,100 do
 s.data.coins=i%200;microSpeaker(p,s,false);state(p,'Reward '..i)
 notify('Screams OFF',false,'voice');notify('Setup denied',true,'voice')
 check(#notifications.pending<=Queue.Limit,'Mixed traffic exceeded queue bound')
 check(notifications:Step(0,true)==delayed,'Mixed traffic displaced save warning')
end
-- Repeated status snapshots do not extend dwell; escalation replaces one slot.
local remaining=notifications.active.remaining;state(p)
check(notifications.active.remaining==remaining,'Silent status restarted save dwell')
saveMode='ownership';autosave(p,s)
check(frame()==saving,'Permanent failure did not replace delayed warning')
local count=0;for _,e in ipairs(notifications.pending)do if e.key=='save' then count+=1 end end
check(count==0,'Obsolete delayed warning queued after permanent failure')
-- Explicit healthy snapshot retires stale save guidance without hiding rewards.
s.canSave=true;s.saveDelayed=true;saveMode='ok';autosave(p,s);state(p)
check(not hasSave(),'Healthy snapshot retained stale save warning')
notifications=Queue.new();notify('Reward');s.canSave=true;s.saveDelayed=false;saveMode='transient';autosave(p,s)
check(frame()==delayed,'Save warning failed to preempt routine notice')
saveMode='ok';autosave(p,s);state(p)
check(frame()=='Reward','Recovery discarded interrupted reward')
-- Exact duplicates while visible do not keep the warning alive forever.
notifications=Queue.new();notify(saving,true,'save')
for _=1,20 do frame()end
local left=notifications.active.remaining;notify(saving,true,'save')
check(notifications.active.remaining==left,'Duplicate save reset dwell')
for _=1,150 do frame()end
check(notifications.active==nil,'Save toast became permanently sticky')
print('PASS '..checks..' save notification integration assertions; synthetic store/UI/time/coin changes')
'''
payload=setup+receiver+extra+state+autosave+speaker+checks
def run(source,failure=None):
 with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',suffix='.luau',dir=root/'tests',delete=False) as f:
  path=Path(f.name);f.write(source)
 try:
  result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True,encoding='utf-8')
  if failure:
   assert result.returncode!=0 and failure in result.stderr,result.stdout+result.stderr
   print('PASS save notification negative control: '+failure)
  else:
   print(result.stdout,end='');assert result.returncode==0,result.stderr
 finally:path.unlink()
run(payload)
if '--negative-controls' in sys.argv:
 def mutate_queue(old,new,failure):
  queue=(root/'src/StarterPlayer/StarterPlayerScripts/NotificationQueue.luau').read_text()
  assert queue.count(old)==1,old
  require="require('../src/StarterPlayer/StarterPlayerScripts/NotificationQueue')"
  run(payload.replace(require,'(function()\n'+queue.replace(old,new)+'\nend)()'),failure)
 mutate_queue('key=="save" and 2 or urgent and 1 or 0','urgent and 1 or 0','Save warning evicted before any displayed frame')
 assert payload.count(',nil,true,"save")')==2
 run(payload.replace(',nil,true,"save")',',nil,true)'),'Save warning evicted before any displayed frame')
 needle='messageKey=messageKey=="save" and "save" or nil'
 assert payload.count(needle)==1
 run(payload.replace(needle,'messageKey=nil'),'Save warning evicted before any displayed frame')
 needle='data.messageKey=="save" and "save" or nil'
 assert payload.count(needle)==1
 run(payload.replace(needle,'nil'),'Save warning evicted before any displayed frame')
 needle='if data.savingAvailable==true and not data.savingDelayed then notifications:Remove("save") end'
 assert payload.count(needle)==1
 run(payload.replace(needle,''),'Healthy snapshot retained stale save warning')
 mutate_queue('if #self.pending>Queue.Limit then','if false then','Mixed traffic exceeded queue bound')
 mutate_queue('if key then self:Remove(key) end','if key and key~="save" then self:Remove(key) end','Permanent failure did not replace delayed warning')
