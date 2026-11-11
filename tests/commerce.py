"""Actual receipt handler; deterministic fake atomic store/time, never live purchases."""
from pathlib import Path
import argparse
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/Commerce.luau').read_text(encoding='utf-8')
setup=r"""
local Catalog=require('../src/ReplicatedStorage/Shared/ShopCatalog')
local Ledger=require('../src/ReplicatedStorage/Shared/BoostLedger')
Catalog.Get('XP').id=101;Catalog.Get('Coins').id=102
-- MUTATION_INSERT
local function fixture(seed)
 local f={raw=seed,now=100,clock=100,fail=false,lost=0,studio=false,eligible=true,notices=0,prompts=0,calls=0,guid=0}
 f.player={UserId=7,Parent=true};f.live=f.player
 local player=f.player
 local market={PromptProductPurchase=function()f.prompts+=1 end,PromptGamePassPurchase=function()f.prompts+=1 end}
 local db={UpdateAsync=function(_,key,transform)
  f.calls+=1;assert(key=='Player_7','Wrong player ledger')
  if f.fail then error('precommit unavailable') end
  -- Roblox may re-evaluate an UpdateAsync transform after another writer commits.
  local first=table.pack(transform(f.raw))
  assert(first.n==1,'UpdateAsync callback returned status as userIds')
  if f.conflict then local fn=f.conflict;f.conflict=nil;f.raw=fn(f.raw) end
  local result=transform(f.raw)
  if result then f.raw=result end
  if f.leave then f.leave=false;f.removing(player);player.Parent=false;f.live=nil end
  if f.lost>0 then f.lost-=1;error('committed response lost') end
  return result
 end}
 local services={MarketplaceService=market,Players={GetPlayerByUserId=function()return f.live end,PlayerRemoving={Connect=function(_,fn)f.removing=fn end}},RunService={IsStudio=function()return f.studio end},HttpService={GenerateGUID=function()f.guid+=1;return 'operation-'..f.guid end},DataStoreService={GetDataStore=function()return db end}}
 local Config={MovementPassId=0};local Entitlements={HasSpectrum=function()return false end,HasMovement=function()return false end}
 services.ReplicatedStorage={Shared={ShopCatalog=Catalog,BoostLedger=Ledger,Config=Config}}
 local game={GetService=function(_,name)return services[name]end}
 local script={Parent={Entitlements=Entitlements}}
 local require=function(module)return module end
 local os={time=function()return f.now end,clock=function()return f.clock end}
 local Enum={ProductPurchaseDecision={NotProcessedYet='pending',PurchaseGranted='granted'}}
 local task={wait=function(seconds)f.now+=seconds;f.clock+=seconds end,spawn=function(fn,...)fn(...)end}
 local Commerce=(function()
"""
tests=r"""
 end)()
 Commerce.Start(function()return f.eligible end,function(_,message,_,urgent)f.notices+=1;f.lastMessage=message;f.urgent=urgent end)
 f.commerce=Commerce
 f.deliver=function(id,product)return market.ProcessReceipt({PlayerId=7,ProductId=product or 101,PurchaseId=id})end
 f.load=function()f.clock+=20;Commerce.Load(player)end
 return f
end
local n=0;local function check(ok,msg)assert(ok,msg);n+=1 end
local f=fixture()
f.studio=true;check(f.deliver('r')=='pending' and f.raw==nil and f.calls==0,'Studio wrote purchase ledger')
f.studio=false;f.live=nil;check(f.deliver('r')=='pending' and f.calls==0,'Offline receipt consumed')
f.live=f.player;f.eligible=false;check(f.deliver('r')=='pending' and f.calls==0,'Ineligible receipt consumed')
f.eligible=true;f.fail=true
check(f.deliver('r')=='pending' and f.raw==nil,'Precommit failure acknowledged')
check(f.calls==3 and f.notices==0 and not f.commerce.Status(f.player).ready,'Precommit retries exposed success')
f=fixture();f.lost=1
check(f.deliver('r1')=='granted' and f.raw.ends.xp==1900 and f.raw.inventory.xp==0,'Single lost response extended activation')
check(f.commerce.Multiplier(f.player,'xp')==2 and f.commerce.Status(f.player).ready,'Confirmed receipt did not activate immediately')
check(f.calls==2 and f.raw.receipts.r1,'Lost response did not retry same receipt')
f.now=150;check(f.deliver('r1')=='granted' and f.raw.ends.xp==1900,'Duplicate receipt extended timer')
check(f.deliver('r2')=='granted' and f.raw.ends.xp==3700 and f.raw.inventory.xp==0,'Distinct receipt did not stack time once')
check(f.deliver('c1',102)=='granted' and f.raw.ends.coins==1950 and f.raw.ends.xp==3700,'Types changed each other')
f.now=1950;check(f.commerce.Multiplier(f.player,'coins')==1 and f.commerce.Multiplier(f.player,'xp')==2,'Independent expiry boundary failed')
f.now=3700;check(f.commerce.Multiplier(f.player,'xp')==1,'Expired boost still pays')
check(f.deliver('r1')=='granted' and f.raw.ends.xp==3700,'Expired replay restarted timer')
local oldExpiry=f.raw.ends.xp
f=fixture(f.raw);f.now=9000;f.load()
check(f.commerce.Multiplier(f.player,'xp')==1 and f.raw.ends.xp==oldExpiry,'Rejoin paused offline expiry')
check(f.deliver('r2')=='granted' and f.raw.ends.xp==oldExpiry,'Rejoin replay restarted timer')
check(f.deliver('r3')=='granted' and f.raw.ends.xp==10800,'New receipt after expiry did not start now')
-- Persistent ambiguity: durable effect exists but no local entitlement is inferred.
f=fixture(Ledger.GrantActive(nil,'old','xp',100));f.load();f.lost=3
check(f.deliver('ambiguous')=='pending' and f.raw.ends.xp==3700,'All-lost outcome was acknowledged or duplicated')
check(not f.commerce.Status(f.player).ready and f.commerce.Multiplier(f.player,'xp')==1,'Ambiguous failure retained an unconfirmed cache')
f.now=200;check(f.deliver('ambiguous')=='granted' and f.raw.ends.xp==3700,'Later confirmation extended committed time')
check(f.commerce.Multiplier(f.player,'xp')==2,'Later confirmation failed to restore durable entitlement')
f=fixture();f.lost=3;check(f.deliver('expired')=='pending','All-lost first receipt acknowledged')
f.now=2500;check(f.deliver('expired')=='granted' and f.raw.ends.xp==1900 and f.commerce.Multiplier(f.player,'xp')==1,'Delayed confirmation gifted fresh time')
-- Offline delivery defers until eligible; starts at first durable processing, not purchase UI.
f=fixture();f.live=nil;check(f.deliver('late')=='pending' and f.raw==nil,'Offline purchase started timer')
f.now=10000;f.live=f.player;check(f.deliver('late')=='granted' and f.raw.ends.xp==11800,'Delayed first delivery used stale purchase time')
-- Simulate a conflicting writer between callback evaluations.
f=fixture();f.conflict=function(raw)return Ledger.GrantActive(raw,'other','xp',100)end
check(f.deliver('self')=='granted' and f.raw.ends.xp==3700 and f.raw.receipts.other and f.raw.receipts.self,'Conflict lost a distinct receipt')
f=fixture();f.conflict=function(raw)return Ledger.GrantActive(raw,'same','xp',100)end
check(f.deliver('same')=='granted' and f.raw.ends.xp==1900,'Concurrent duplicate extended timer')
-- Leaving after durable commit must not repopulate the departed player's cache.
f=fixture();f.leave=true
check(f.deliver('leave')=='granted' and f.raw.ends.xp==1900,'Committed departure receipt was discarded')
check(not f.commerce.Status(f.player).ready and f.notices==0,'Departed player cache or notice recreated')
-- Existing unspent tokens and old receipts are preserved, not automatically consumed.
local legacy=Ledger.Grant(nil,'legacy','xp');legacy=Ledger.Grant(legacy,'legacy2','xp')
f=fixture(legacy);f.load()
check(f.deliver('legacy')=='granted' and f.raw.inventory.xp==2 and f.raw.ends.xp==0,'Historical receipt gifted automatic time')
check(f.deliver('new')=='granted' and f.raw.inventory.xp==2 and f.raw.ends.xp==1900,'New purchase consumed legacy inventory')
f.commerce.Activate(f.player,'xp')
check(f.raw.inventory.xp==1 and f.raw.ends.xp==3700,'Legacy manual activation missing')
f.commerce.Activate(f.player,'xp');check(f.raw.inventory.xp==1 and f.raw.ends.xp==3700,'Activation throttle failed')
f.commerce.Activate(f.player,'invalid');check(f.raw.ends.xp==3700,'Invalid manual type changed timer')
check(f.deliver('legacy2')=='granted' and f.raw.inventory.xp==1 and f.raw.ends.xp==3700,'Old receipt restored consumed inventory')
-- Fail-closed malformed/unknown receipt and configured-product ambiguity.
f=fixture();check(f.deliver(nil)=='pending' and f.raw==nil,'Missing purchase ID acknowledged')
check(f.deliver('')=='pending' and f.raw==nil,'Empty purchase ID acknowledged')
check(f.deliver('unknown',999)=='pending' and f.raw==nil,'Unknown product acknowledged')
Catalog.Get('Coins').id=101;check(f.deliver('ambiguousProduct')=='pending' and f.raw==nil,'Duplicate product IDs acknowledged');Catalog.Get('Coins').id=102
local full=Ledger.Normalize(nil);for i=1,Ledger.ReceiptLimit do full.receipts[tostring(i)]=true end
f=fixture(full);check(f.deliver('new')=='pending' and not f.raw.receipts.new,'Receipt capacity exceeded')
check(f.deliver('1')=='granted' and f.raw.ends.xp==0,'Old receipt forgotten at capacity')
f=fixture({ends={xp=Ledger.MaxExpiry}});check(f.deliver('overflow')=='pending' and not (f.raw.receipts and f.raw.receipts.overflow),'Expiry cap overflow acknowledged')
f.load();f.commerce.Prompt(f.player,'XP');check(f.prompts==0 and f.urgent==true,'Unfulfillable duration prompted purchase')
f=fixture({inventory={xp=1000000}});f.load();f.commerce.Prompt(f.player,'XP')
check(f.prompts==1,'Legacy inventory capacity blocked automatic purchase')
f.commerce.Prompt(f.player,'Spectrum');check(f.prompts==1 and f.urgent==true,'Unconfigured pass prompted')
print('PASS '..n..' actual commerce assertions with simulated atomic retries/time; no native or live services')
"""
def run(code, expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',encoding='utf-8',delete=False) as f:
  path=Path(f.name);f.write(code)
 try:
  r=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True,encoding='utf-8');out=r.stdout+r.stderr
  if expected:
   assert r.returncode and expected in out,out
   print('PASS negative control:',expected)
  else:
   print(out,end='');assert r.returncode==0,out
 finally:path.unlink()
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--negative-controls',action='store_true');args=parser.parse_args()
 code=setup+source+tests;run(code)
 if args.negative_controls:
  run(code.replace('Ledger.GrantActive(raw,receipt.PurchaseId,item.boost,os.time())','Ledger.Grant(raw,receipt.PurchaseId,item.boost)'),'Single lost response extended activation')
  mutation="local original=Ledger.GrantActive;Ledger.GrantActive=function(raw,id,kind,now)local d=Ledger.Normalize(raw);if id then d.receipts[id]=nil end;return original(d,id,kind,now)end"
  run(code.replace('-- MUTATION_INSERT',mutation),'Single lost response extended activation')
  run(code.replace('if not ok then return Enum.ProductPurchaseDecision.NotProcessedYet end','if false then return Enum.ProductPurchaseDecision.NotProcessedYet end'),'Precommit failure acknowledged')
  run(code.replace('elseif not success then cache[player]=nil end','elseif not success then end'),'Ambiguous failure retained an unconfirmed cache')
  run(code.replace('-- MUTATION_INSERT',"Ledger.Multiplier=function(d,kind,now)return d and d.ends and (d.ends[kind] or 0)>0 and 2 or 1 end"),'Independent expiry boundary failed')
