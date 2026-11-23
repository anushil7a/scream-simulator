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
autosave=server[server.index('local function autosave('):server.index('local function stepAutosaves(now)')]
speaker=server[server.index('local function gearAction('):server.index('local function vendorPurchase(')]
progress=server[server.index('local function questProgress('):server.index('local function confirmBeamDodge(')]
claim_start=server.index(' elseif verb=="ClaimQuest" then')+len(' elseif verb=="ClaimQuest" then')
claim='\nlocal function claim(p,s,arg)\n'+server[claim_start:server.index(' elseif verb=="SetSettings"',claim_start)]+'\nend\n'

extra='''
local VoiceEligibility=require('../src/ServerScriptService/VoiceEligibility')
local StateSnapshot=require('../src/ServerScriptService/StateSnapshot')
local Queue=require('../src/StarterPlayer/StarterPlayerScripts/NotificationQueue')
local sessions={[p]=s};p.Parent=true;p.UserId=7
function p:GetAttribute()return 10 end;function p:SetAttribute()end
s.data.level=10;s.data.xp=0;s.voice={nextCast=0};s.canSave=true;s.nextDodge=0;s.protectedUntil=0
Config.XPToNext=function()return 100 end;Config.GetDeliveryStop=function()end
Config.HealthForLevel=function()return 100 end
local function parts()end
local Soccer={Status=function()end};local QuestGuide={Step=function()end}
local NavigationCatalog={QuestTargets=function()return {}end};local World={Bots={}}
local Equipment={SyncGear=function()end};local TrainingRules={Recommended=function()return {name='Rookie'}end}
local Entitlements={HasSpectrum=function()return false end,HasMovement=function()return false end,
 HasEncore=function()return true end,HasAfterimage=function()return false end,HasCityGlow=function()return true end,
 HasSignalDeck=function()return false end,HasCityCrest=function()return true end,
 HasPulseFrame=function()return true end,HasRouteLights=function()return false end,
 HasHarborBadge=function()return false end,HasSprintRibbon=function()return true end}
local Access={IsAuthorized=function()return false end};local game={}
local RunService={IsStudio=function()return false end}
Commerce.Status=function()return {} end
os.time=function()return 1000 end
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
notify('Beams stay OFF. Finish mic setup or wait for gameplay to be ready, then turn them on.',true,'voice');frame()
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
check(latest.encorePass==true and latest.afterimagePass==false and latest.cityGlowPass==true and latest.signalDeckPass==false and latest.cityCrestPass==true and latest.pulseFramePass==true and latest.routeLightsPass==false and latest.harborBadgePass==false and latest.sprintRibbonPass==true,'State lost cosmetic ownership booleans')
for i=1,100 do
 s.data.coins=i%200;microSpeaker(p,s,false);state(p,'Reward '..i)
 notify('Beams OFF',false,'voice');notify('Setup denied',true,'voice')
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
do
 local completion='Quest complete! Claim your reward in Quests.'
 local receipt='Quest reward · +100 XP · +40 coins · Garden'
 local beachReceipt='Quest reward · +100 XP · +40 coins · Beach'
 local gardenQuest=Config.GetQuest
 Config.GetQuest=function(id)
  if id=='beach' then return {id='beach',name='Beach',goal=6,xp=100,coins=40} end
  return gardenQuest(id)
 end
 local function prepare()
  notifications=Queue.new()
  s.canSave=true;s.saveDelayed=false;s.activeQuest='garden'
  s.data.quests={garden={progress=2,claimed=false}}
  s.data.achievements={}
 end
 prepare()
 questProgress(p,'Garden')
 check(frame()==completion,'Quest completion did not display')
 claim(p,s,'garden')
 check(frame()==receipt,'Claimed reward reminder remained visible instead of receipt')
 prepare()
 notify('Earlier action')
 notify('Level-up cue')
 questProgress(p,'Garden');claim(p,s,'garden')
 check(frame()==receipt,'Quest receipt waited behind routine notices')
 local seen={[receipt]=true}
 for _=1,150 do seen[frame()]=true end
 check(seen[receipt] and not seen[completion],'Claimed reward reminder came back from pending queue')
 prepare()
 s.data.quests.beach={progress=6,claimed=false}
 table.insert(Config.Quests,{id='beach',goal=6})
 questProgress(p,'Garden')
 claim(p,s,'garden')
 check(frame()==receipt and notifications.pending[1] and notifications.pending[1].text==completion,
  'Claiming one reward hid another earned reward reminder')
 local firstReceipt=notifications.active
 claim(p,s,'beach')
 check(notifications.active==firstReceipt and #notifications.pending==1
  and notifications.pending[1].text==beachReceipt and notifications.pending[1]~=firstReceipt,
  'Equal claim receipts merged or last reward did not retire the shared reminder')
 claim(p,s,'beach');claim(p,s,'garden')
 check(#notifications.pending==1,'Repeated claim produced another receipt')
 for _=1,55 do frame() end
 check(notifications.active and notifications.active.text==beachReceipt and notifications.active~=firstReceipt,
  'Second confirmed claim receipt received no dwell')
 prepare()
 questProgress(p,'Garden')
 claim(p,s,'garden')
 state(p,completion,nil,false,'questClaim')
 local seen={}
 for _=1,150 do seen[frame()]=true end
 check(seen[receipt] and not seen[completion],'Unclaimable snapshot resurrected quest guidance')
 prepare()
 s.canSave=false;s.saveDelayed=false
 state(p,saving,nil,true,'save')
 notify('Other urgent',true)
 questProgress(p,'Garden')
 claim(p,s,'garden')
 check(frame()==saving,'Quest receipt interrupted urgent save warning')
 local seen={}
 local order={}
 for _=1,180 do
  local text=frame();seen[text]=true
  if text~='' and order[#order]~=text then table.insert(order,text) end
 end
 check(seen[receipt] and not seen[completion],'Save warning masked stale quest notice until later')
 check(order[1]==saving and order[2]=='Other urgent' and order[3]==receipt,'Receipt moved ahead of a queued urgent warning')
end
do
 local packets={}
 stateRemote.FireClient=function(_,_,packet)table.insert(packets,packet)end
 local function periodic() state(p,nil,nil,nil,nil,true) end
 local shopClock=1000;local boosts={xp=1050}
 os.time=function()return shopClock end
 Commerce.Status=function()return {ends=boosts}end
 s.collected={};s.data.quests={garden={progress=0}};s.activeQuest='garden';s.questDeadline=os.clock()+30
 periodic();periodic();check(#packets==1,'Identical periodic State was transmitted')
 s.data.quests.garden.progress=1;periodic();check(#packets==2,'In-place quest progress was suppressed')
 s.data.quests.garden.progress=0;periodic();check(#packets==3,'Reverted quest progress was suppressed')
 s.questDeadline-=2;periodic();check(#packets==4 and packets[4].questTime<packets[3].questTime,'Changed quest countdown was suppressed')
 shopClock+=1;periodic();check(#packets==4,'A clock tick forced an idle State packet')
 boosts.xp=nil;periodic();check(#packets==5,'Nested field removal was suppressed')
 state(p);state(p);check(#packets==7,'Explicit State requests were suppressed')
 state(p,'Reward');state(p,'Reward');check(#packets==9 and packets[9].message=='Reward','Repeated explicit notices were suppressed')
 state(p,'Saving is unavailable.',nil,true,'save');check(#packets==10 and packets[10].messageUrgent and packets[10].messageKey=='save','Urgent notice was suppressed')
 state(p,nil,{hint='Resident reply'});check(#packets==11 and packets[11].conversation.hint=='Resident reply','Conversation was suppressed')
 periodic();periodic();check(#packets==12 and not packets[12].conversation,'Transient State clearing packet was suppressed')
 s.collected.Flowerbed228=true;periodic();periodic();check(#packets==13,'An unchanged collected marker kept sending State')
 s.collected={};periodic();periodic();check(#packets==14,'Collection reset was suppressed')
 check(packets[1].shop.serverNow==1000 and packets[5].shop.serverNow==1001,'Sent State lacked its current timer anchor')
 s.questDeadline=nil;periodic()
 s.voice.nextCast=now+4;s.nextDodge=now+4;s.protectedUntil=now+4
 periodic();check(#packets==15,'Attribute-backed cooldowns forced an idle State packet')
 s.testBeamReadyAt=now+3;periodic()
 check(#packets==16 and packets[16].testBeamCooldown==3,'Tool cooldown was suppressed')
 now+=1;periodic();check(#packets==17 and packets[17].testBeamCooldown==2,'Tool cooldown stopped updating')
 now+=2;periodic();periodic();check(#packets==18 and packets[18].testBeamCooldown==0,'Tool cooldown expiry was suppressed')
end
do
 local packet
 stateRemote.FireClient=function(_,_,value)packet=value end
 s.activeQuest=nil
 s.data.quests={garden={progress=3,claimed=false}}
 s.data.availableQuests={garden=true}
 state(p);check(packet.quests.garden.progress==3 and packet.availableQuests.garden,'City state lost visible quest progress')
 Config.ResonanceLayout={}
 state(p);check(next(packet.quests)==nil,'Hall state exposed City quest progress')
 check(next(packet.availableQuests)==nil,'Hall state exposed City quest discoveries')
 check(s.data.quests.garden.progress==3 and s.data.availableQuests.garden,'Hall state cleared the persisted quest data')
end
print('PASS '..checks..' save notification and State integration assertions; synthetic store/UI/time/coin changes')
'''
# Keep the client HUD label separate from the reused server coins helper.
payload=setup+'\ndo local coins={}\n'+receiver+'\nend\n'+extra+state+autosave+speaker+progress+claim+checks
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
assert 'if verb=="Sync" then state(p)' in server
assert server.count('state(p,nil,nil,nil,nil,true)')==1 and 'if tick%5==0 then state(p,nil,nil,nil,nil,true) end' in server
if '--negative-controls' in sys.argv:
 def mutate_queue(old,new,failure):
  queue=(root/'src/StarterPlayer/StarterPlayerScripts/NotificationQueue.luau').read_text()
  assert queue.count(old)==1,old
  require="require('../src/StarterPlayer/StarterPlayerScripts/NotificationQueue')"
  run(payload.replace(require,'(function()\n'+queue.replace(old,new)+'\nend)()'),failure)
 mutate_queue('key=="save" and 2 or urgent and 1 or receipt and .5 or 0','urgent and 1 or receipt and .5 or 0','Save warning evicted before any displayed frame')
 assert payload.count(',nil,true,"save")')==2
 run(payload.replace(',nil,true,"save")',',nil,true)'),'Save warning evicted before any displayed frame')
 needle='messageKey=(messageKey=="save" or messageKey=="questClaim" or messageKey=="questReceipt") and messageKey or nil'
 assert payload.count(needle)==1
 run(payload.replace(needle,'messageKey=nil'),'Save warning evicted before any displayed frame')
 needle='(key=="save" or key=="questClaim" or key=="questReceipt") and key or nil'
 assert payload.count(needle)==1
 run(payload.replace(needle,'nil'),'Save warning evicted before any displayed frame')
 needle='if data.savingAvailable==true and not data.savingDelayed then notifications:Remove("save") end'
 assert payload.count(needle)==1
 run(payload.replace(needle,''),'Healthy snapshot retained stale save warning')
 run(payload.replace('if unclaimed==0 then notifications:Remove("questClaim") end',''),'Claimed reward reminder came back from pending queue')
 run(payload.replace('if key~="questClaim" or unclaimed>0 then','if true then'),'Unclaimable snapshot resurrected quest guidance')
 mutate_queue('if #self.pending>Queue.Limit then','if false then','Mixed traffic exceeded queue bound')
 mutate_queue('if key then self:Remove(key) end','if key and key~="save" then self:Remove(key) end','Permanent failure did not replace delayed warning')
 mutate_queue('or receipt and .5 or 0','or 0','Quest receipt waited behind routine notices')
 run(payload.replace('.." coins · "..q.name','.." coins · Garden"'),'Equal claim receipts merged')
 mutate_queue('if not receipt then','if true then','Equal claim receipts merged')
 mutate_queue('or urgent and 1 or receipt and .5 or 0','or receipt and 1.5 or urgent and 1 or 0','Receipt moved ahead of a queued urgent warning')
 run(payload.replace('quests=not Config.ResonanceLayout and s.data.quests or {}','quests=s.data.quests'),'Hall state exposed City quest progress')
 run(payload.replace('availableQuests=not Config.ResonanceLayout and s.data.availableQuests or {}','availableQuests=s.data.availableQuests'),
     'Hall state exposed City quest discoveries')
 run(payload.replace('if changedOnly and StateSnapshot.Equal(packet,s.lastStatePacket) then return end',''), 'Identical periodic State was transmitted')
 run(payload.replace('local snapshot=StateSnapshot.Copy(packet)','local snapshot=StateSnapshot.Copy(packet);snapshot.quests=packet.quests'),'In-place quest progress was suppressed')
 run(payload.replace('if changedOnly and StateSnapshot.Equal','if StateSnapshot.Equal'),'Explicit State requests were suppressed')
 run(payload.replace('if changedOnly and StateSnapshot.Equal','if changedOnly and not next(s.collected) and StateSnapshot.Equal'),'An unchanged collected marker kept sending State')
 run(payload.replace('if changedOnly and StateSnapshot.Equal','packet.shop.serverNow=os.time()\n if changedOnly and StateSnapshot.Equal'),'A clock tick forced an idle State packet')
