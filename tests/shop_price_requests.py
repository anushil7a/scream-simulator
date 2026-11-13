"""Actual ShopUI price path with suspended API mocks; no live prices or native UI."""
from pathlib import Path
import argparse,subprocess,tempfile
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--callback-baseline',action='store_true');p.add_argument('--disabled-baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');a=p.parse_args()
path='src/StarterPlayer/StarterPlayerScripts/ShopUI.luau';s=subprocess.check_output(['git','show','15df683:'+path],cwd=R,text=True,encoding='utf-8') if a.baseline else (R/path).read_text();s=subprocess.check_output(['git','show','0619103:'+path],cwd=R,text=True,encoding='utf-8') if a.disabled_baseline else s;s=subprocess.check_output(['git','show','74c7763:'+path],cwd=R,text=True,encoding='utf-8') if a.callback_baseline else s;s=s[:s.index('function Shop.ColorMixer(')]
setup=r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local function fixture()
 local f={now=0,jobs={},buttons={},sent=0,labels={}};local os={clock=function()return f.now end,time=function()return 100 end}
 local Catalog={Items={}};for i,key in ipairs({'Spectrum','XP','Coins','Movement'})do table.insert(Catalog.Items,{key=key,id=100+i,kind=(i==1 or i==4) and 'pass' or 'product'})end
 function Catalog.Get(key)for _,v in ipairs(Catalog.Items)do if v.key==key then return v end end end
 for _,item in ipairs(Catalog.Items)do item.tag='tag';item.name=item.key;item.description='description';item.boost=item.key=='XP' and 'xp' or 'coins'end
 local Config={MovementPassId=104}
 local Marketplace={GetProductInfoAsync=function(_,id,kind)if f.sync then return f.sync end;local result=coroutine.yield();if result=='error'then error('mock unavailable')end;return result end}
 local services={MarketplaceService=Marketplace,UserInputService={},ReplicatedStorage={Shared={ShopCatalog=Catalog,Config=Config}}}
 local game={GetService=function(_,name)return services[name]end};local require=function(v)return v end
 local Color3={fromRGB=function()return {}end,new=function()return {}end,fromHSV=function()return {}end};local UDim2={new=function()return {}end,fromOffset=function()return {}end,fromScale=function()return {}end};local ColorSequence={new=function()return {}end};local ColorSequenceKeypoint={new=function()return {}end};local Instance={new=function()return {}end};local Enum={InfoType={GamePass='pass',Product='product'},Font={GothamBlack=1},TextXAlignment={Center=1}}
 local task={spawn=function(fn,...)
  local args={...};local co=coroutine.create(fn);table.insert(f.jobs,{co=co,args=args});assert(coroutine.resume(co,...))
 end}
 local ui={button=function(_,_,text,_,_,callback)local b={Text=text,Parent=true,callback=callback};table.insert(f.buttons,b);return b end}
 ui.card=function()return {}end;ui.label=function(_,text)f.labels[text]=true;return {Text=text}end;ui.frame=function()return {}end;ui.info=function()end
 local action={FireServer=function()f.sent+=1 end}
 local function module()
'''
endsetup=r'''
 return {shop=Shop,button=purchaseButton,stats=function()return {flight=priceInFlight,views=priceViews,records=prices}end}
end
local m=module();f.shop=m.shop;f.stats=m.stats;f.items=Catalog.Items;f.config=Config
function f.draw(i,clear,allowed,owned)if clear~=false then m.shop.Clear()end;m.button(Catalog.Items[i or 2],{},owned==true,{savingAvailable=allowed~=false},ui,action,{},{});return f.buttons[#f.buttons]end
function f.render(narrow)ui.narrow=narrow;f.buttons={};m.shop.Render({savingAvailable=true,shop={ready=true,inventory={},ends={},serverNow=100}},ui,action)end
function f.finish(i,result)local ok,err=coroutine.resume(f.jobs[i].co,result);assert(ok,err);m.shop.Tick()end
return f
end
'''
checks=r'''
for _,narrow in ipairs({false,true})do
 local rendered=fixture();for i=1,120 do rendered.render(narrow)end
 check(rendered.labels['Yellow base. Saved colors are kept.'] and rendered.labels['One pass. Choose your beam hue.'],'Spectrum concise copy missing')
 check(not rendered.labels['Unlock the hue picker. Yellow is the base color; saved colors are kept.'],'Repeated hue instruction retained')
 check(#rendered.jobs==4 and #rendered.stats().views==4,'Full Render did not bound four product views/calls')
 rendered.shop.Clear();check(#rendered.stats().views==0,'Full Render clear retained views')
end
local sync=fixture();sync.sync={IsForSale=true,PriceInRobux=15};local direct=sync.draw()
check(direct.Text=='R$ 15','Synchronous success displayed unavailable');check(sync.stats().flight==0,'Synchronous success retained slot')
local f=fixture();local old=f.draw()
for i=1,120 do f.draw()end
check(#f.jobs==1,'Rerenders duplicated pending request')
check(#f.stats().views==1,'Old GUI watchers retained')
check(f.jobs[1].args[1].apply==nil and f.jobs[1].args[1].button==nil,'Worker record retains UI')
f.now=1;f.finish(1,{IsForSale=true,PriceInRobux=25})
check(old.Text=='CHECKING PRICE.' and f.buttons[#f.buttons].Text=='R$ 25','Late result changed obsolete GUI or missed current view')
f.buttons[#f.buttons].callback();check(f.sent==1,'Confirmed price cannot prompt')
f.shop.Clear();check(#f.stats().views==0,'Clear retained price views');local b=f.draw();check(b.Text=='R$ 25' and #f.jobs==1,'Reopen discarded fresh cache')
f.now=61;b=f.draw();check(#f.jobs==2 and b.Text=='CHECKING PRICE.','Expired cache used or not refreshed');b.callback();check(f.sent==1,'Expired price permits prompt')
f.finish(2,'error');check(b.Text=='UNAVAILABLE','Error not unavailable')
f.now=70;for i=1,120 do f.draw()end;check(#f.jobs==2,'Error rerender storm retried early')
f.now=71;f.shop.Tick();check(#f.jobs==3,'Open-view retry did not resume');f.finish(3,{IsForSale=true,PriceInRobux=0});check(f.buttons[#f.buttons].Text=='R$ 0','Valid free price rejected')
-- All slots remain occupied by timed-out calls, even through closes and ID changes.
f=fixture();for i=1,4 do f.draw(i,i==1)end;check(#f.jobs==4 and f.stats().flight==4,'Multi-product capacity incorrect')
f.now=8;f.shop.Tick();for _,b in ipairs(f.buttons)do check(b.Text=='UNAVAILABLE','Hung call stayed checking past deadline')end
f.items[2].id=202;f.draw(2);for i=1,120 do f.shop.Tick()end;check(#f.jobs==4,'Hung slot abandoned/replaced')
f.now=9;f.finish(2,{IsForSale=true,PriceInRobux=99});check(#f.jobs==5 and f.stats().flight==4,'Returned stale slot did not free capacity')
check(f.buttons[#f.buttons].Text=='CHECKING PRICE.','Old ID result applied to new ID')
f.finish(5,{IsForSale=true,PriceInRobux=42});check(f.buttons[#f.buttons].Text=='R$ 42','New ID result failed')
f.finish(1,{IsForSale=true,PriceInRobux=99});check(f.stats().records.Spectrum.info==nil,'Timed-out response cached')
f.shop.Clear();check(#f.stats().views==0,'Hung teardown retains views')
-- ID roundtrip must not admit an obsolete record even before its deadline.
f=fixture();f.draw();local first=f.jobs[1].args[1];f.items[2].id=202;f.draw();f.items[2].id=102;f.draw()
f.finish(3,{IsForSale=true,PriceInRobux=30});f.finish(1,{IsForSale=true,PriceInRobux=90});f.finish(2,{IsForSale=true,PriceInRobux=80})
check(first.info==nil and f.buttons[#f.buttons].Text=='R$ 30','Obsolete ID record accepted result')
-- Disabled/malformed transitions invalidate even when the same ID returns.
for _,invalid in ipairs({0,-1,0/0,math.huge,1.5,'102',false})do
 f=fixture();f.draw();local first=f.jobs[1].args[1]
 f.items[2].id=invalid;b=f.draw();check(b.Text=='COMING SOON' and #f.jobs==1 and f.stats().flight==1,'Invalid config spawned or abandoned request')
 f.items[2].id=102;b=f.draw();check(#f.jobs==2,'Disabled ID roundtrip reused obsolete request')
 f.finish(1,{IsForSale=true,PriceInRobux=90});check(first.info==nil and b.Text=='CHECKING PRICE.','Disabled ID result accepted')
 f.finish(2,{IsForSale=true,PriceInRobux=30});check(b.Text=='R$ 30' and f.stats().flight==0,'Reenabled fresh request failed')
end
f=fixture();f.draw();f.finish(1,{IsForSale=true,PriceInRobux=90});f.items[2].id=0;f.draw();f.items[2].id=102;b=f.draw()
check(#f.jobs==2 and b.Text=='CHECKING PRICE.','Disabled ID retained cached price')
for _,changed in ipairs({0,202})do
 f=fixture();f.draw();f.items[2].id=changed;b=f.draw(2,true,true,true);check(b.Text=='OWNED' and #f.jobs==1,'Owned transition queried')
 f.items[2].id=102;b=f.draw();check(#f.jobs==2,'Owned changed configuration retained obsolete request')
 f.finish(1,{IsForSale=true,PriceInRobux=90});check(b.Text=='CHECKING PRICE.','Owned transition admitted stale response')
end
-- Invalidating all four records must not release their still-running calls.
f=fixture();for i=1,4 do f.draw(i,i==1)end
for i=1,4 do if i==4 then f.config.MovementPassId=0 else f.items[i].id=0 end;f.draw(i)end
for i=1,4 do if i==4 then f.config.MovementPassId=104 else f.items[i].id=100+i end;f.draw(i,i==1)end
check(#f.jobs==4 and f.stats().flight==4,'Disabled records freed occupied slots')
f.finish(1,{IsForSale=true,PriceInRobux=90});check(#f.jobs==5 and f.stats().flight==4,'Invalidated response did not release exactly one slot')
-- Directly invoked queued/retained callbacks, not a native event-delivery claim.
for _,mode in ipairs({'clear','rerender','detach'})do
 f=fixture();local priced=f.draw();f.finish(1,{IsForSale=true,PriceInRobux=25});priced.callback();check(f.sent==1,'Current priced callback did not send')
 local current
 if mode=='clear'then f.shop.Clear()elseif mode=='rerender'then current=f.draw()else priced.Parent=nil end
 for i=1,20 do priced.callback()end
 check(f.sent==1,'Obsolete priced callback sent after '..mode)
 if mode~='detach'then current=current or f.draw();current.callback();check(f.sent==2,'Current reopened callback failed')end
end
-- Fail closed on malformed price responses, retaining no prior available price.
for _,info in ipairs({{},true,{IsForSale=true},{IsForSale=true,PriceInRobux=-1},{IsForSale=true,PriceInRobux=0/0},{IsForSale=true,PriceInRobux=math.huge},{IsForSale=true,PriceInRobux=1.5},{IsForSale='true',PriceInRobux=1},{IsForSale=false}})do
 f=fixture();b=f.draw();f.finish(1,info);check(b.Text=='UNAVAILABLE','Malformed/not-for-sale price enabled');b.callback();check(f.sent==0,'Unconfirmed price prompted')
end
f=fixture();b=f.draw(2,true,false);f.finish(1,{IsForSale=true,PriceInRobux=10});b.callback();check(b.Text=='TEST / UNAVAILABLE' and f.sent==0,'Unsavable snapshot purchase enabled')
f=fixture();f.items[2].id=0;b=f.draw();check(#f.jobs==0 and b.Text=='COMING SOON','Disabled product queried')
print('PASS',n,'actual price-path assertions; coroutine API and GUI mocks only')
'''
# Historical lifecycle repros retain their original UI copy and intended failure oracle.
if a.baseline or a.callback_baseline or a.disabled_baseline:
 checks='\n'.join(line for line in checks.split('\n') if 'Spectrum concise copy missing' not in line and 'Repeated hue instruction retained' not in line)

def run(source,error=None,baseline=False):
 tail="local f=fixture();for i=1,120 do f.draw()end;assert(#f.jobs==120);print('REPRO120 rerenders create120 pending price calls')" if baseline else checks
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=R/'tests',encoding='utf-8',delete=False)as t:t.write(setup+source+endsetup+tail);q=Path(t.name)
 try:r=subprocess.run(['luau',str(q)],capture_output=True,text=True)
 finally:q.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS negative control:',error)
 else:print(out,end='');assert r.returncode==0
if a.callback_baseline:run(s,'Obsolete priced callback sent after clear')
elif a.disabled_baseline:run(s,'Disabled ID roundtrip reused obsolete request')
elif a.baseline:run(s,baseline=True)
else:
 run(s)
 if a.negative_controls:
  mutations=[('Yellow base. Saved colors are kept.','Unlock the hue picker. Yellow is the base color; saved colors are kept.','Spectrum concise copy missing'),('revision==generation and b and b.Parent and available','b and b.Parent and available','Obsolete priced callback sent after clear'),('revision==generation and b and b.Parent and available','revision==generation and available','Obsolete priced callback sent after detach'),(' or prices[item.key] and prices[item.key].key~=item.kind..":"..id','','Owned changed configuration retained obsolete request'),('if not configured or prices[item.key] and prices[item.key].key~=item.kind..":"..id then prices[item.key]=nil end' ,'-- omitted disabled invalidation','Disabled ID roundtrip reused obsolete request'),('if record.info and os.clock()<record.expires then view.apply(record.info,false);return end','-- omitted synchronous cache apply','Synchronous success displayed unavailable'),('not record.pending and now>=','now>=','Rerenders duplicated pending request'),('priceInFlight<PRICE_LIMIT','true','Hung slot abandoned/replaced'),('record.retryAt=now+PRICE_RETRY','record.retryAt=now','Error not unavailable'),('now<record.deadline and validPrice(info)','validPrice(info)','Timed-out response cached'),('table.clear(priceViews)','do end','Full Render did not bound four product views/calls'),('if prices[record.itemKey]~=record then return end','if false then return end','Obsolete ID record accepted result')]
  for old,new,error in mutations:
   assert s.count(old)==1,old;run(s.replace(old,new),error)

  worker=s[s.index('local function fetchPrice('):s.index('local function updatePrice(')]
  assert all(word not in worker for word in ['view.','apply(','button','data.']), 'Worker captures GUI context'
  print('PASS source contract: worker has no GUI/apply/snapshot reference; not a GC proof')
