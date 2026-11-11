"""Actual ShopUI price path with suspended API mocks; no live prices or native UI."""
from pathlib import Path
import argparse,subprocess,tempfile
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');a=p.parse_args()
path='src/StarterPlayer/StarterPlayerScripts/ShopUI.luau';s=subprocess.check_output(['git','show','15df683:'+path],cwd=R,text=True,encoding='utf-8') if a.baseline else (R/path).read_text();s=s[:s.index('function Shop.ColorMixer(')]
setup=r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local function fixture()
 local f={now=0,jobs={},buttons={},sent=0};local os={clock=function()return f.now end,time=function()return 100 end}
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
 ui.card=function()return {}end;ui.label=function(_,text)return {Text=text}end;ui.frame=function()return {}end;ui.info=function()end
 local action={FireServer=function()f.sent+=1 end}
 local function module()
'''
endsetup=r'''
 return {shop=Shop,button=purchaseButton,stats=function()return {flight=priceInFlight,views=priceViews,records=prices}end}
end
local m=module();f.shop=m.shop;f.stats=m.stats;f.items=Catalog.Items;f.config=Config
function f.draw(i,clear,allowed)if clear~=false then m.shop.Clear()end;m.button(Catalog.Items[i or 2],{},false,{savingAvailable=allowed~=false},ui,action,{},{});return f.buttons[#f.buttons]end
function f.render(narrow)ui.narrow=narrow;f.buttons={};m.shop.Render({savingAvailable=true,shop={ready=true,inventory={},ends={},serverNow=100}},ui,action)end
function f.finish(i,result)local ok,err=coroutine.resume(f.jobs[i].co,result);assert(ok,err);m.shop.Tick()end
return f
end
'''
checks=r'''
for _,narrow in ipairs({false,true})do
 local rendered=fixture();for i=1,120 do rendered.render(narrow)end
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
-- Fail closed on malformed price responses, retaining no prior available price.
for _,info in ipairs({{},true,{IsForSale=true},{IsForSale=true,PriceInRobux=-1},{IsForSale=true,PriceInRobux=0/0},{IsForSale=true,PriceInRobux=math.huge},{IsForSale=true,PriceInRobux=1.5},{IsForSale='true',PriceInRobux=1},{IsForSale=false}})do
 f=fixture();b=f.draw();f.finish(1,info);check(b.Text=='UNAVAILABLE','Malformed/not-for-sale price enabled');b.callback();check(f.sent==0,'Unconfirmed price prompted')
end
f=fixture();b=f.draw(2,true,false);f.finish(1,{IsForSale=true,PriceInRobux=10});b.callback();check(b.Text=='TEST / UNAVAILABLE' and f.sent==0,'Unsavable snapshot purchase enabled')
f=fixture();f.items[2].id=0;b=f.draw();check(#f.jobs==0 and b.Text=='COMING SOON','Disabled product queried')
print('PASS',n,'actual price-path assertions; coroutine API and GUI mocks only')
'''
def run(source,error=None,baseline=False):
 tail="local f=fixture();for i=1,120 do f.draw()end;assert(#f.jobs==120);print('REPRO120 rerenders create120 pending price calls')" if baseline else checks
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=R/'tests',encoding='utf-8',delete=False)as t:t.write(setup+source+endsetup+tail);q=Path(t.name)
 try:r=subprocess.run(['luau',str(q)],capture_output=True,text=True)
 finally:q.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS negative control:',error)
 else:print(out,end='');assert r.returncode==0
if a.baseline:run(s,baseline=True)
else:
 run(s)
 if a.negative_controls:
  mutations=[('if record.info and os.clock()<record.expires then view.apply(record.info,false);return end','-- omitted synchronous cache apply','Synchronous success displayed unavailable'),('not record.pending and now>=','now>=','Rerenders duplicated pending request'),('priceInFlight<PRICE_LIMIT','true','Hung slot abandoned/replaced'),('record.retryAt=now+PRICE_RETRY','record.retryAt=now','Error not unavailable'),('now<record.deadline and validPrice(info)','validPrice(info)','Timed-out response cached'),('table.clear(priceViews)','do end','Full Render did not bound four product views/calls'),('if prices[record.itemKey]~=record then return end','if false then return end','Obsolete ID record accepted result')]
  for old,new,error in mutations:
   assert s.count(old)==1,old;run(s.replace(old,new),error)

  worker=s[s.index('local function fetchPrice('):s.index('local function updatePrice(')]
  assert all(word not in worker for word in ['view.','apply(','button','data.']), 'Worker captures GUI context'
  print('PASS source contract: worker has no GUI/apply/snapshot reference; not a GC proof')
