"""Actual Commerce/BoostLedger lifecycle with fake store, players and coroutines.
Private cache observations are test-only instrumentation, not GC/native proof.
"""
from pathlib import Path
import argparse,subprocess,tempfile
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');a=p.parse_args()
path='src/ServerScriptService/Commerce.luau';source=(R/path).read_text()
setup=r'''
local Ledger=require('../src/ReplicatedStorage/Shared/BoostLedger')
local Catalog=require('../src/ReplicatedStorage/Shared/ShopCatalog');Catalog.Get('XP').id=101;Catalog.Get('Coins').id=102
local n=0;local function check(v,m)assert(v,m);n+=1 end
local function fixture(seed)
 local f={now=100,clock=100,raw=seed,calls=0,notices={},prompts=0,lost=0,fail=0,suspend=false,guid=0}
 f.player={UserId=7,Parent=true,eligible=true};f.current=f.player
 local function prompt()f.prompts+=1;if f.suspendPrompt then coroutine.yield('prompt')end;if f.promptFail then error('prompt failed')end end
 local market={PromptProductPurchase=prompt,PromptGamePassPurchase=prompt}
 local db={UpdateAsync=function(_,key,transform)
  f.calls+=1;assert(key=='Player_7');if f.suspend then coroutine.yield('store')end
  if f.fail>0 then f.fail-=1;error('precommit')end
  local result=transform(f.raw);if result then f.raw=result end
  if f.lost>0 then f.lost-=1;error('committed-response-lost')end
  return result
 end}
 local services={MarketplaceService=market,Players={GetPlayerByUserId=function()return f.current end,PlayerRemoving={Connect=function(_,fn)f.removing=fn end}},RunService={IsStudio=function()return false end},HttpService={GenerateGUID=function()f.guid+=1;return 'operation-'..f.guid end},DataStoreService={GetDataStore=function()return db end}}
 local Config={MovementPassId=0};local Entitlements={HasSpectrum=function()return false end,HasMovement=function()return false end}
 services.ReplicatedStorage={Shared={ShopCatalog=Catalog,BoostLedger=Ledger,Config=Config}}
 local game={GetService=function(_,name)return services[name]end};local script={Parent={Entitlements=Entitlements}}
 local require=function(v)return v end;local os={clock=function()return f.clock end,time=function()return f.now end}
 local Enum={ProductPurchaseDecision={NotProcessedYet='pending',PurchaseGranted='granted'}}
 local task={spawn=function(fn,...)fn(...)end,wait=function(seconds)f.clock+=seconds;f.now+=seconds;coroutine.yield('wait')end}
 local Commerce=(function()
'''
endsetup=r'''
end)()
Commerce.Start(function(player)return player.eligible end,function(player,message)table.insert(f.notices,{player=player,message=message})end)
f.api=Commerce
function f.resume(co,...)local ok,value=coroutine.resume(co,...);assert(ok,value);return value end
function f.start(fn)local co=coroutine.create(fn);local value=f.resume(co);return co,value end
function f.receipt(id)return market.ProcessReceipt({PlayerId=7,ProductId=101,PurchaseId=id})end
function f.remove(player)f.removing(player or f.player)end
function f.rejoin()local p={UserId=7,Parent=true,eligible=true};f.current=p;return p end
function f.noticeCount(player)local count=0;for _,v in ipairs(f.notices)do if v.player==player then count+=1 end end;return count end
return f
end
'''
checks=r'''
-- Successful writes started before removal remain durable/acknowledged, but no local resurrection.
for _,operation in ipairs({'receipt','load','activate'})do
 local f=fixture(Ledger.Normalize({inventory={xp=2,coins=0}}));local p=f.player
 if operation=='activate'then f.api.Load(p)end
 local notices=f.noticeCount(p);f.suspend=true
 local co,why=f.start(function()if operation=='receipt'then return f.receipt('r')elseif operation=='load'then return f.api.Load(p)else return f.api.Activate(p,'xp')end end)
 check(why=='store' and f.api.Busy(p),'Operation did not suspend with owned lock')
 f.remove(p);check(not f.api._Cache(p),'Removal did not clear cache');check(f.api.Busy(p),'Removal hid actual owner lock: '..operation)
 local result=f.resume(co)
 check(operation~='receipt' or result=='granted','Committed departed receipt not acknowledged')
 check(not f.api._Cache(p),'Departed result resurrected private cache: '..operation)
 check(f.noticeCount(p)==notices,'Departed result invoked notification: '..operation)
 local status=f.api.Status(p);check(not status.ready and status.ends.xp==0 and status.inventory.xp==0 and f.api.Multiplier(p,'xp')==1,'Departed public status exposed cache')
 p.Parent=nil;check(not f.api._Cache(p),'Detach resurrected cache')
 check(not f.api.Busy(p),'Completed operation retained lock')
end
-- Tombstone must reject newly queued public calls even if Parent/allowed remain true.
local f=fixture();local p=f.player;f.remove(p)
f.api.Load(p);f.api.Activate(p,'xp');f.api.Prompt(p,'XP');local result=f.receipt('new')
check(f.calls==0 and f.prompts==0 and #f.notices==0 and result=='pending','Departed admission started work or notification')
-- A departed lock waiter can exit without touching the active owner's lock.
f=fixture();p=f.player;f.suspend=true
local owner,why=f.start(function()return f.receipt('owner')end);check(why=='store','Owner not suspended')
local waiter,waitWhy=f.start(function()return f.receipt('waiter')end);check(waitWhy=='wait' and f.calls==1,'Waiter began duplicate write')
f.remove(p);local replacement=f.rejoin()
check(f.api.Busy(replacement),'Removal cleared another operation lock')
check(f.resume(waiter)=='pending' and f.calls==1,'Departed waiter kept polling or wrote')
check(f.api.Busy(replacement),'Departed waiter released owner lock')
check(f.resume(owner)=='granted' and not f.api.Busy(replacement),'Owner failed to finish durable receipt')
check(not f.api._Cache(p) and not f.api._Cache(replacement),'Old completion populated wrong cache')
f.suspend=false;f.api.Load(replacement)
check(f.api.Status(replacement).ready and f.api.Multiplier(replacement,'xp')==2,'Same-ID replacement did not recover durable result')
check(not f.api._Cache(p) and f.noticeCount(p)==0 and f.noticeCount(replacement)==1,'Replacement identity/cache/notices crossed')
local expiry=f.raw.ends.xp;check(f.receipt('owner')=='granted' and f.raw.ends.xp==expiry,'Same-ID duplicate receipt gifted duration')
-- Existing current waiter still receives its own operation after serial owner completion.
f=fixture();f.suspend=true
owner,why=f.start(function()return f.receipt('first')end);waiter,waitWhy=f.start(function()return f.receipt('second')end)
check(f.resume(owner)=='granted','Current owner failed');check(f.resume(waiter)=='store' and f.calls==2,'Current waiter failed to acquire released lock')
check(f.resume(waiter)=='granted' and f.raw.receipts.first and f.raw.receipts.second and f.raw.ends.xp==3700,'Current serialized receipts failed')
check(f.api.Status(f.player).ready and f.api._Cache(f.player),'Current completion missing cache')
-- Ambiguous committed replies preserve the in-flight operation; no retry double grant.
for _,lost in ipairs({1,3})do
 f=fixture();p=f.player;f.suspend=true;f.lost=lost
 owner,why=f.start(function()return f.receipt('ambiguous')end);f.remove(p)
 local value=f.resume(owner)
 while coroutine.status(owner)~='dead'do value=f.resume(owner)end
 check(value==(lost==1 and 'granted' or 'pending'),'Ambiguous departed decision changed')
 check(f.calls==(lost==1 and 2 or 3) and f.raw.receipts.ambiguous,'In-flight retries stopped or duplicated count')
 check(f.raw.ends.xp==1900,'Ambiguous receipt duplicated duration')
 check(not f.api._Cache(p) and f.noticeCount(p)==0,'Ambiguous departure leaked local state')
 local replacement=f.rejoin();f.suspend=false;check(f.receipt('ambiguous')=='granted' and f.raw.ends.xp==1900,'Replacement replay duplicated duration')
end
-- Precommit errors remain bounded, preserve inventory and release lock.
f=fixture();f.fail=3;local co=f.start(function()return f.receipt('failure')end)
local value;while coroutine.status(co)~='dead'do value=f.resume(co)end
check(value=='pending' and f.calls==3 and f.raw==nil and not f.api.Busy(f.player),'Precommit failure changed durable state/bound')
-- Admission after ordinary detach also fails without relying on PlayerRemoving delivery.
f=fixture();f.player.Parent=nil;f.api.Load(f.player);check(f.receipt('detached')=='pending' and f.calls==0,'Detached admission started write')
-- Failed departed activation preserves saved tokens and suppresses its error notice.
f=fixture(Ledger.Normalize({inventory={xp=2,coins=0}}));p=f.player;f.api.Load(p)
local before=f.noticeCount(p);f.suspend=true;f.fail=3
co,why=f.start(function()f.api.Activate(p,'xp')end);check(why=='store','Failed activation did not start')
f.remove(p);while coroutine.status(co)~='dead'do f.resume(co)end
check(f.calls==4 and f.raw.inventory.xp==2 and f.raw.ends.xp==0,'Failed activation consumed saved inventory')
check(f.noticeCount(p)==before and not f.api._Cache(p) and not f.api.Busy(p),'Failed departed activation leaked notice/cache/lock')
-- A yielded prompt failure after departure must not revive user notifications.
f=fixture();p=f.player;f.api.Load(p);local before=f.noticeCount(p);f.suspendPrompt=true;f.promptFail=true
co,why=f.start(function()f.api.Prompt(p,'XP')end);check(why=='prompt','Prompt fixture did not yield')
f.remove(p);f.resume(co);check(f.noticeCount(p)==before and not f.api._Cache(p),'Departed prompt failure notified')
-- Current disallowed waiter also exits without altering the owner's slot.
f=fixture();f.suspend=true;owner=f.start(function()return f.receipt('own')end);waiter=f.start(function()return f.receipt('wait')end)
f.player.eligible=false;check(f.resume(waiter)=='pending' and f.calls==1 and f.api.Busy(f.player),'Unavailable waiter wrote or released lock')
f.resume(owner)
print('PASS',n,'actual Commerce lifecycle assertions; coroutine/store/player mocks, not native GC')
'''
baselines={
'cache':r'''local f=fixture();f.suspend=true;local co=f.start(function()return f.receipt('r')end);f.remove();f.resume(co);assert(f.api._Cache(f.player) and f.noticeCount(f.player)==1);print('REPRO departed cache and changed callback recreated while Parent remains true')''',
'wait':r'''local f=fixture();f.suspend=true;local owner=f.start(function()return f.receipt('owner')end);local waiter=f.start(function()return f.receipt('waiter')end);f.remove();f.player.eligible=false;for i=1,100 do assert(f.resume(waiter)=='wait')end;assert(f.calls==1);print('REPRO100 departed lock polls with no new durable write')'''}
def run(s,error=None,body=checks):
 # Read-only membership observer catches retention even if public accessors hide it.
 assert s.count('return Commerce')==1
 s=s.replace('return Commerce','Commerce._Cache=function(player)return cache[player]~=nil end\nreturn Commerce')
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.commerce_lifecycle_',dir=R/'tests',encoding='utf-8',delete=False)as t:t.write(setup+s+endsetup+body);q=Path(t.name)
 try:r=subprocess.run(['luau',str(q)],capture_output=True,text=True,timeout=15)
 finally:q.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS negative control:',error)
 else:print(out,end='');assert r.returncode==0
if a.baseline:
 old=subprocess.check_output(['git','show','03efe28:'+path],cwd=R,text=True,encoding='utf-8')
 for body in baselines.values():run(old,body=body)
else:
 run(source)
 if a.negative_controls:
  mutations=[
   ('function Commerce.Busy(player) return locks[player.UserId]==true end','function Commerce.Busy(player) return live(player) and locks[player.UserId]==true end','Removal hid actual owner lock: receipt'),
   ('departed[player]=true;','', 'Departed result resurrected private cache: receipt'),
   ('if live(player) then cache[player]=Ledger.Normalize(result) end','if player.Parent then cache[player]=Ledger.Normalize(result) end','Departed result resurrected private cache: receipt'),
   ('if ok and live(player) then changed(player) end','if ok then changed(player) end','Departed result invoked notification: load'),
   ('if live(player) then changed(player,ok and','if true then changed(player,ok and','Departed result invoked notification: activate'),
   ('if live(player) then changed(player,"Boost purchase processed.','if true then changed(player,"Boost purchase processed.','Departed result invoked notification: receipt'),
   ('  if not live(player) or not allowed(player) then return false end\n  task.wait(.05)','  task.wait(.05)','Departed waiter kept polling or wrote'),
   ('  if not live(player) or not allowed(player) then return false end\n  task.wait(.05)','  if not live(player) or not allowed(player) then locks[id]=nil;return false end\n  task.wait(.05)','Departed waiter released owner lock'),
   ('departed[player]','departed[player.UserId]','Same-ID replacement did not recover durable result'),
   ('cache[player]=nil;promptAt[player]=nil','promptAt[player]=nil','Removal did not clear cache'),
   ('if not ok and live(player) then changed(player,','if not ok then changed(player,','Departed prompt failure notified'),
   ('function Commerce.Prompt(player,key)\n if not live(player) then return end','function Commerce.Prompt(player,key)','Departed admission started work or notification')]
  for old,new,error in mutations:
   assert old in source,old;run(source.replace(old,new),error)

