"""Actual entitlement module with coroutine ownership mocks; no Roblox calls."""
from pathlib import Path
import argparse,subprocess,tempfile
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');args=p.parse_args()
path='src/ServerScriptService/Entitlements.luau'
s=subprocess.check_output(['git','show','670948d:'+path],cwd=R,text=True,encoding='utf-8') if args.baseline else (R/path).read_text(encoding='utf-8')
setup=r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local function fixture(spectrumId,movementId,encoreId,afterimageId,cityGlowId,signalDeckId,cityCrestId)
 local handlers={};local function event(name)return {Connect=function(_,fn)handlers[name]=fn end}end
 local f={calls={},studio=false};local ids={Spectrum=spectrumId,Encore=encoreId,Afterimage=afterimageId,CityGlow=cityGlowId,SignalDeck=signalDeckId,CityCrest=cityCrestId}
 local config={MovementPassId=movementId,InArena=function(pos)return pos=='arena'end,Get=function(key)return {id=ids[key] or 0}end}
 local services={Players={PlayerRemoving=event('remove')},RunService={IsStudio=function()return f.studio end}}
 services.MarketplaceService={PromptGamePassPurchaseFinished=event('purchase'),UserOwnsGamePassAsync=function(_,id,pass)
  table.insert(f.calls,{id,pass});local result=coroutine.yield();if result=='error'then error('mock ownership unavailable')end;return result
 end}
 local game={ReplicatedStorage={Shared={Config={}}},GetService=function(_,name)return services[name]end}
 local require=function()return config end;local task={spawn=function(fn,player)local co=coroutine.create(fn);f.spawned=co;assert(coroutine.resume(co,player));return co end}
 local E=(function()
'''
checks=r'''
 end)();f.E=E;f.remove=handlers.remove;f.purchase=handlers.purchase
 function f.start(player)
  player.SetAttribute=player.SetAttribute or function(self,key,value) self[key]=value end
  player.GetAttribute=player.GetAttribute or function(self,key) return self[key] end
  local co=coroutine.create(E.Refresh);local ok,err=coroutine.resume(co,player);assert(ok,err);return co
 end
 function f.resume(co,value)local ok,err=coroutine.resume(co,value);assert(ok,err)end
 return f
end
-- First yielded pass: stale false and stale true cannot overwrite latest decision.
for _,latest in ipairs({true,false})do
 local f=fixture(11,22);local p={UserId=7,Parent={}}
 local old=f.start(p);local new=f.start(p);f.resume(new,latest);f.resume(new,latest)
 check(f.E.HasSpectrum(p)==latest and f.E.HasMovement(p)==latest,'Latest result missing')
 local calls=#f.calls;f.resume(old,not latest)
 check(f.E.HasSpectrum(p)==latest,'Stale first response overwrote spectrum')
 check(#f.calls==calls and coroutine.status(old)=='dead','Stale first response continued second API')
 check(f.E.HasMovement(p)==latest,'Stale first response changed movement')
end
-- Second yielded pass: same player, later refresh wins in both directions.
for _,latest in ipairs({true,false})do
 local f=fixture(11,22);local p={UserId=7,Parent={}}
 local old=f.start(p);f.resume(old,true)
 local new=f.start(p);f.resume(new,latest);f.resume(new,latest);f.resume(old,not latest)
 check(f.E.HasMovement(p)==latest,'Stale second response overwrote movement')
end
for _,stage in ipairs({1,2})do
 local f=fixture(11,22);local p={UserId=7,Parent={}};f.studio=true;f.E.SetStudioMovement(p,true)
 local old=f.start(p);if stage==2 then f.resume(old,true)end
 -- PlayerRemoving can fire while Parent is still present: identity must fence it.
 f.remove(p);local beforeQueued=#f.calls;local queued=f.start(p)
 check(#f.calls==beforeQueued and coroutine.status(queued)=='dead','Queued departure refresh began work')
 local replacement={UserId=7,Parent={}}
 local new=f.start(replacement);f.resume(new,true);f.resume(new,true);local calls=#f.calls
 f.resume(old,true)
 check(not f.E.HasSpectrum(p) and not f.E.HasMovement(p),'Departed cache repopulated')
 check(not f.E.HasStudioMovement(p),'Departure retained Studio override')
 check(f.E.HasSpectrum(replacement) and f.E.HasMovement(replacement),'Same-ID replacement affected')
 check(#f.calls==calls,'Departed first response continued API')
end
for _,pass in ipairs({11,22})do
 local f=fixture(11,22);local p={UserId=7,Parent={}}
 local join=f.start(p);local calls=#f.calls
 f.purchase(p,pass,false);f.purchase(p,999,true)
 check(#f.calls==calls and f.spawned==nil,'Cancelled/unrelated event queried ownership')
 check(not f.E.HasSpectrum(p) and not f.E.HasMovement(p),'Ignored event granted ownership')
 f.purchase(p,pass,true)
 check(f.spawned~=nil and #f.calls==calls+1,'Purchase callback did not refresh')
 f.resume(f.spawned,true);f.resume(f.spawned,true)
 check(f.E.HasSpectrum(p) and f.E.HasMovement(p),'Purchase refresh did not grant confirmed ownership')
 calls=#f.calls;f.resume(join,false)
 check(#f.calls==calls and f.E.HasSpectrum(p) and f.E.HasMovement(p),'Purchase callback failed to supersede join refresh')
 f.purchase(p,pass,false);f.purchase(p,999,true)
 check(#f.calls==calls and f.E.HasSpectrum(p) and f.E.HasMovement(p),'Ignored event changed confirmed ownership')
end
-- Clear previously confirmed paid caches even before Parent becomes nil.
do
 local f=fixture(11,22);local p={UserId=7,Parent={}}
 local co=f.start(p);f.resume(co,true);f.resume(co,true)
 check(f.E.HasMovement(p) and f.E.HasSpectrum(p),'Confirmed departure precondition missing')
 f.remove(p)
 check(p.Parent~=nil and not f.E.HasMovement(p),'Departure retained confirmed movement')
 check(not f.E.HasSpectrum(p),'Departure retained confirmed spectrum')
end
-- Successful prompt is only a refresh hint: no access pending, false or error.
for _,pass in ipairs({11,22})do
 for _,response in ipairs({false,'error'})do
  local f=fixture(11,22);local p={UserId=7,Parent={}}
  p.SetAttribute=function(self,key,value) self[key]=value end
  f.purchase(p,pass,true)
  check(f.spawned~=nil and not f.E.HasSpectrum(p) and not f.E.HasMovement(p),'Purchase event granted before ownership response')
  f.resume(f.spawned,response)
  check(not f.E.HasSpectrum(p) and not f.E.HasMovement(p),'Unconfirmed first response granted ownership')
  f.resume(f.spawned,response)
  check(not f.E.HasSpectrum(p) and not f.E.HasMovement(p),'False/error ownership granted fresh player')
 end
end
local f=fixture(11,22);local p={UserId=7,Parent={}}
local co=f.start(p);f.resume(co,true);f.resume(co,true)
co=f.start(p);f.resume(co,'error');f.resume(co,'error')
check(f.E.HasSpectrum(p) and f.E.HasMovement(p),'API errors cleared last-good values')
co=f.start(p);f.resume(co,false);f.resume(co,false)
check(not f.E.HasSpectrum(p) and not f.E.HasMovement(p),'Later legitimate revocation ignored')
local calls=#f.calls;p.Parent=nil;co=f.start(p)
check(#f.calls==calls and coroutine.status(co)=='dead','Detached player began ownership work')
f=fixture(0,0);p={UserId=7,Parent={}};co=f.start(p)
check(#f.calls==0 and coroutine.status(co)=='dead','Disabled IDs called API')
check(not f.E.HasSpectrum(p) and not f.E.HasMovement(p),'Disabled IDs granted access')
f.studio=true;check(f.E.SetStudioMovement(p,true) and f.E.HasMovement(p),'Studio override broken')
check(not f.E.CanUseMovement(p,'arena') and f.E.CanUseMovement(p,'safe'),'Arena rule changed')
f.studio=false;check(not f.E.HasMovement(p),'Studio override leaked live')
check(p.EncorePass==false and p.AfterimagePass==false and p.CityGlowPass==false and p.SignalDeckPass==false and p.CityCrestPass==false,'Disabled cosmetic attributes must be false')
f.purchase(p,0,true);check(f.spawned==nil,'Disabled pass event queried ownership')
for _,pass in ipairs({33,44})do
 f=fixture(0,0,33,44);p={UserId=7,Parent={}}
 local join=f.start(p)
 check(f.calls[1][2]==33,'Disabled movement blocked Encore ownership')
 f.purchase(p,pass,true)
 check(not f.E.HasEncore(p) and not f.E.HasAfterimage(p),'Cosmetic purchase callback granted ownership')
 f.resume(f.spawned,true)
 check(p.EncorePass==true and f.calls[#f.calls][2]==44,'Confirmed Encore missing or Afterimage unchecked')
 f.resume(f.spawned,true)
 check(p.AfterimagePass==true and f.E.HasEncore(p) and f.E.HasAfterimage(p),'Confirmed cosmetics missing')
 local calls=#f.calls;f.resume(join,false)
 check(#f.calls==calls and p.EncorePass==true,'Stale Encore refresh changed cosmetics')
 local old=f.start(p);f.resume(old,true)
 co=f.start(p);f.resume(co,'error');f.resume(co,'error')
 check(f.E.HasEncore(p) and f.E.HasAfterimage(p),'Cosmetic API errors cleared last-good values')
 f.resume(old,false)
 check(p.AfterimagePass==true,'Stale Afterimage refresh changed cosmetics')
 co=f.start(p);f.resume(co,false);f.resume(co,false)
 check(p.EncorePass==false and p.AfterimagePass==false,'Cosmetic revocation failed to clear attributes')
 co=f.start(p);f.remove(p);f.resume(co,true)
 check(p.EncorePass==false and not f.E.HasEncore(p) and not f.E.HasAfterimage(p),'Departure let a pending cosmetic confirm')
end
f=fixture(0,0,0,0,55);p={UserId=7,Parent={}}
local old=f.start(p)
f.purchase(p,55,true)
check(f.spawned and f.calls[#f.calls][2]==55 and not f.E.HasCityGlow(p),'Glow checkout must recheck ownership without granting it')
f.resume(f.spawned,true);f.resume(old,false)
check(f.E.HasCityGlow(p),'Stale refresh cleared confirmed glow')
co=f.start(p);f.resume(co,false)
check(not f.E.HasCityGlow(p),'Glow did not revoke after confirmed ownership loss')
for i,key in ipairs({'SignalDeck','CityCrest'})do
 local id=55+i
 local f=fixture(0,0,0,0,0,i==1 and id or 0,i==2 and id or 0)
 local p={UserId=7,Parent={}}
 local has=f.E['Has'..key]
 local join=f.start(p)
 f.purchase(p,id,false)
 check(f.spawned==nil and not has(p),'Cancelled theme purchase queried ownership')
 f.purchase(p,id,true)
 check(f.spawned and f.calls[#f.calls][2]==id and not has(p),'Theme checkout must recheck ownership without granting it')
 f.resume(f.spawned,true);f.resume(join,false)
 check(has(p) and p[key..'Pass']==true,'Theme ownership missing after confirmed response')
 local failed=f.start(p);f.resume(failed,'error')
 check(has(p),'Theme API error cleared confirmed ownership')
 local revoke=f.start(p);f.resume(revoke,false)
 check(not has(p) and p[key..'Pass']==false,'Theme did not revoke after confirmed ownership loss')
 local pending=f.start(p);f.remove(p);f.resume(pending,true)
 check(not has(p) and p[key..'Pass']==false,'Departure let a pending theme confirm')
end
print('PASS',n,'actual entitlement coroutine assertions; no live API, purchase or native replication')
'''
def run(source,error=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=R/'tests',encoding='utf-8',delete=False)as t:t.write(setup+source+checks);q=Path(t.name)
 try:r=subprocess.run(['luau',str(q)],capture_output=True,text=True)
 finally:q.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS expected failure:',error)
 else:print(out,end='');assert r.returncode==0
if args.baseline:run(s,'Stale first response overwrote spectrum')
else:
 run(s)
 if args.negative_controls:
  guard='if not current() then return false end'
  assert s.count(guard)==3
  run(s.replace(guard,'-- omitted first fence',1),'Stale first response overwrote spectrum')
  at=s.index(guard,s.index(guard)+len(guard));run(s[:at]+s[at:].replace(guard,'-- omitted second fence',1),'Stale second response overwrote movement')
  at=s.rindex(guard);run(s[:at]+s[at:].replace(guard,'-- omitted cosmetic fence',1),'Stale Encore refresh changed cosmetics')
  run(s.replace(' or id==Catalog.Get("CityGlow").id',''),'Glow checkout must recheck ownership without granting it')
  for key in ('SignalDeck', 'CityCrest'):
   run(s.replace(f' or id==Catalog.Get("{key}").id',''),'Theme checkout must recheck ownership without granting it')
  old='refreshIdentity[player]=nil;';assert s.count(old)==1;run(s.replace(old,''),'Departed cache repopulated')
  old='if not player.Parent or departed[player] then return false end';assert s.count(old)==1;run(s.replace(old,'if departed[player] then return false end'),'Detached player began ownership work')
  old='if success then owned[player]=result==true end';assert s.count(old)==1;run(s.replace(old,'if success and result then owned[player]=true end'),'Later legitimate revocation ignored')

  old='departed[player]=true;';assert s.count(old)==1;run(s.replace(old,''),'Queued departure refresh began work')

  old='and purchased then';assert s.count(old)==1;run(s.replace(old,'then'),'Cancelled/unrelated event queried ownership')
  old='owned[player]=nil;';assert s.count(old)==1;run(s.replace(old,''),'Departure retained confirmed movement')
  old='and purchased then task.spawn(Entitlements.Refresh,player)';assert s.count(old)==1
  run(s.replace(old,'and purchased then owned[player]=true;spectrum[player]=true;task.spawn(Entitlements.Refresh,player)'),'Purchase event granted before ownership response')
