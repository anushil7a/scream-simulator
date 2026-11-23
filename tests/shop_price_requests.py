"""Actual ShopUI price path with suspended API mocks; no live prices or native UI."""
from pathlib import Path
import argparse,subprocess,tempfile
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--callback-baseline',action='store_true');p.add_argument('--disabled-baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');a=p.parse_args()
path='src/StarterPlayer/StarterPlayerScripts/ShopUI.luau';s=subprocess.check_output(['git','show','15df683:'+path],cwd=R,text=True,encoding='utf-8') if a.baseline else (R/path).read_text();s=subprocess.check_output(['git','show','0619103:'+path],cwd=R,text=True,encoding='utf-8') if a.disabled_baseline else s;s=subprocess.check_output(['git','show','74c7763:'+path],cwd=R,text=True,encoding='utf-8') if a.callback_baseline else s;s=s[:s.index('function Shop.ColorMixer(')]
setup=r'''
local HISTORICAL=HISTORICAL_FIXTURE
local n=0;local function check(v,m)assert(v,m);n+=1 end
local function fixture()
 local f={now=0,jobs={},buttons={},links={},sent=0,labels={},cards={}};local os={clock=function()return f.now end,time=function()return 100 end}
 local Catalog=require('../src/ReplicatedStorage/Shared/ShopCatalog')
 for i,item in ipairs(Catalog.Items) do item.id=i<=4 and 100+i or 0 end
 for _,item in ipairs(Catalog.Items)do item.tag='tag';item.name=item.key;item.description='description';item.boost=item.key=='XP' and 'xp' or 'coins'end
 local Config={MovementPassId=104}
 local Marketplace={GetProductInfoAsync=function(_,id,kind)if f.sync then return f.sync end;local result=coroutine.yield();if result=='error'then error('mock unavailable')end;return result end}
 local function children(nodes)
  function nodes:WaitForChild(key)return assert(self[key],key) end
  return nodes
 end
 local services={MarketplaceService=Marketplace,UserInputService={},ReplicatedStorage=children({Shared=children({ShopCatalog=Catalog,Config=Config})})}
 local game={GetService=function(_,name)return services[name]end};local require=function(v)return v end
 local Color3={fromRGB=function()return {}end,new=function()return {}end,fromHSV=function()return {}end};local UDim2={new=function(xs,x,ys,y)return {xs=xs,x=x,ys=ys,y=y}end,fromOffset=function(x,y)return {xs=0,x=x,ys=0,y=y}end,fromScale=function(xs,ys)return {xs=xs,x=0,ys=ys,y=0}end};local ColorSequence={new=function()return {}end};local ColorSequenceKeypoint={new=function()return {}end};local Instance={new=function()return {}end};local Enum={InfoType={GamePass='pass',Product='product'},Font={GothamBlack=1},TextXAlignment={Center=1}}
 local task={spawn=function(fn,...)
  local args={...};local co=coroutine.create(fn);table.insert(f.jobs,{co=co,args=args});assert(coroutine.resume(co,...))
 end}
 local ui={button=function(parent,name,text,size,pos,callback)local b={Name=name,Text=text,Parent=true,callback=callback,holder=parent,size=size,pos=pos};table.insert(name:sub(1,6)=='Browse' and f.links or f.buttons,b);return b end,jump=function(name)f.destination=name end}
 ui.card=function(height)local card={height=height};table.insert(f.cards,card);return card end;ui.label=function(_,text)f.labels[text]=true;return {Text=text}end;ui.frame=function()return {}end;ui.info=function()end
 local action={FireServer=function()f.sent+=1 end}
 local function module()
'''
endsetup=r'''
 return {shop=Shop,button=purchaseButton,stats=function()return {flight=priceInFlight,views=priceViews,records=prices}end}
end
local m=module();f.shop=m.shop;f.stats=m.stats;f.items=Catalog.Items;f.config=Config
function f.draw(i,clear,allowed,owned)if clear~=false then m.shop.Clear()end;m.button(Catalog.Items[i or 2],{},owned==true,{savingAvailable=allowed~=false},ui,action,{},{});return f.buttons[#f.buttons]end
function f.render(narrow,compact,data)
 ui.narrow=narrow;ui.compactLandscape=compact;ui.featureLayout=compact==true and "compact" or compact;f.buttons={};f.cards={};f.links={}
 m.shop.Render(data or {savingAvailable=true,shop={ready=true,inventory={},ends={},serverNow=100}},ui,action)
end
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
local visual=fixture()
if not HISTORICAL then
 check(visual.shop.FeatureLayout~=nil,'Short-landscape Spectrum layout missing')
 for _,xy in ipairs({{455,218,154,275},{567,241,113,495},{448,150,86,208}})do
  local mode=visual.shop.FeatureLayout(xy[1],xy[2])
  check(mode=='short','Short-landscape Spectrum layout missing')
  visual.render(true,mode)
  local feature=visual.cards[1];local buy=visual.buttons[1];local boosts=visual.links[1]
  check(buy.holder==feature and boosts.holder==feature and #visual.buttons==13,'Short hero changed offer or jump wiring')
  check(buy.pos.y+buy.size.y<=xy[3] and boosts.pos.y+boosts.size.y<=xy[3] and buy.size.y==44 and boosts.size.y==44,
   'Spectrum actions below short first fold')
  check(buy.pos.x+buy.size.xs*xy[4]+buy.size.x<=boosts.pos.xs*xy[4]+boosts.pos.x-6,
   'Spectrum actions overlap in the short pane')
 end
 local disabled=fixture();disabled.items[1].id=0;disabled.render(true,'short')
 local buy=disabled.buttons[1];check(buy.Text=='COMING SOON' and not buy.Interactable,'Short hero obscured disabled availability')
 buy.callback();check(disabled.sent==0,'Disabled Spectrum prompted checkout in short hero')
end

if visual.shop.CompactLandscape then
 check(not visual.shop.CompactLandscape(388,762) and not visual.shop.CompactLandscape(1024,720),'Portrait or desktop compact')
 for _,xy in ipairs({{644,316},{750,323},{644,326},{749,388},{749,330},{844,390}})do
  check(visual.shop.CompactLandscape(xy[1],xy[2]),'Supported landscape not compact')
  visual.render(false,true)
  local feature=visual.cards[1];local cta=visual.buttons[1]
  local scrollY=math.min(620,xy[2]-76)-(54+50+18)
  check(feature.height<=scrollY and cta.pos.y+cta.size.y<=feature.height and cta.size.y==44,'Spectrum action below first fold or shortened')
  check(cta.holder==feature and feature.Name=='SpectrumFeature' and #visual.buttons==13,'Hierarchy or action count changed')
 end
 check(not visual.shop.CompactLandscape(643,388) and not visual.shop.CompactLandscape(749,315) and not visual.shop.CompactLandscape(749,431),'Breakpoint leaked')
 visual.render(false,false);check(visual.cards[1].height==260 and visual.buttons[1].pos.y==206,'Desktop hero changed')
 visual.render(true,false);check(visual.cards[1].height==300 and visual.buttons[1].pos.y==238,'Portrait hero changed')
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
if not HISTORICAL then
 local f=fixture()
 f.config.MovementPassId=f.items[1].id
 local spectrum=f.draw(1)
 local movement=f.draw(4,false)
 check(#f.jobs==0 and spectrum.Text=='COMING SOON' and not spectrum.Interactable
  and movement.Text=='COMING SOON' and not movement.Interactable,'Conflicting pass obtained a price request')
 spectrum.callback();movement.callback();check(f.sent==0,'Conflicting pass fired a client checkout request')
 local product=f.draw(2,false);check(#f.jobs==1 and not product.Interactable,'Separate product checkout was affected by pass collision')
end
if visual.shop.CompactLandscape and visual.buttons[3].Name=="BuyEncore" then
 local f=fixture()
 f.render(false,false)
 local order={"BuySpectrum","BuyMovement","BuyEncore","BuyAfterimage","BuyCityGlow","BuySignalDeck","BuyCityCrest","BuyPulseFrame","BuyRouteLights","BuyHarborBadge","BuySprintRibbon","BuyXP","BuyCoins"}
 for i,name in ipairs(order)do check(f.buttons[i].Name==name and f.buttons[i].holder.LayoutOrder==i*10,'Permanent passes must appear before timed boosts')end
 check(#f.links==2 and f.links[1].size.y==44 and f.links[2].size.y==44,'Missing section shortcuts or touch target')
 check(f.links[1].holder.LayoutOrder==10 and f.links[2].holder.LayoutOrder==115,'Sections are out of order')
 f.links[1].callback();check(f.destination=='BoostsSection','First-fold shortcut did not open boost section')
 f.links[2].callback();check(f.destination=='SpectrumFeature','Passes shortcut did not return to featured pass')
 local oldShortcut=f.links[1];f.shop.Clear();oldShortcut.callback()
 check(f.destination=='SpectrumFeature','Closed shop shortcut still directs scroll')
 for i=3,11 do
  local b=f.buttons[i]
  check(b.Text=="COMING SOON" and not b.Interactable and b.size.y>=45,'Unconfigured pass needs a disabled state and full target')
  b.callback()
 end
 check(f.sent==0 and #f.jobs==4,'Unconfigured pass attempted price lookup or purchase')
 f.render(true,false,{encorePass=true,afterimagePass=true,cityGlowPass=true,signalDeckPass=true,cityCrestPass=true,pulseFramePass=true,routeLightsPass=true,harborBadgePass=true,sprintRibbonPass=true,savingAvailable=true})
 for i=3,11 do
  local b=f.buttons[i];check(b.Text=="OWNED" and not b.Interactable,'Owned cosmetic state was lost')
  b.callback()
 end
 check(f.sent==0,'Owned pass attempted purchase')
 f.render(true,false,{harborBadgePass=true,savingAvailable=true})
 check(f.buttons[10].Text=='OWNED' and f.buttons[11].Text=='COMING SOON','Harbor Badge ownership was conflated')
 f.render(true,false,{sprintRibbonPass=true,savingAvailable=true})
 check(f.buttons[10].Text=='COMING SOON' and f.buttons[11].Text=='OWNED','Sprint Ribbon ownership was conflated')
 f.render(true,false,{signalDeckPass=true,savingAvailable=true})
 check(f.buttons[6].Text=='OWNED' and f.buttons[7].Text=='COMING SOON','Ownership of the new passes must remain independent')
 f.render(true,false,{cityCrestPass=true,savingAvailable=true})
 check(f.buttons[6].Text=='COMING SOON' and f.buttons[7].Text=='OWNED','Ownership of the new passes must remain independent')
 f.render(false,false,{pulseFramePass=true,savingAvailable=true})
 check(f.buttons[8].Text=='OWNED' and f.buttons[9].Text=='COMING SOON','Pulse Frame and Route Lights ownership were conflated')
 f.render(false,false,{routeLightsPass=true,savingAvailable=true})
 check(f.buttons[8].Text=='COMING SOON' and f.buttons[9].Text=='OWNED','Pulse Frame entitlement did not clear independently')
 local parts={}
 local trim=f.shop.PulseFrame({},function(parent,name,size,pos)
  local part={Parent=parent,Name=name,Size=size,Position=pos};table.insert(parts,part);return part
 end)
 check(#parts==3 and parts[1]==trim and trim.Visible==false,'Pulse trim must start hidden and allocate two rails')
 for _,part in ipairs(parts) do
  check(part.Active==false and part.Interactable==false and part.Selectable==false,'Pulse trim captured beam input')
 end
 check(parts[2].Parent==trim and parts[3].Parent==trim,'Pulse rails must hide with their frame')
 f=fixture()
 for i=1,4 do f.items[i].id=0 end;f.config.MovementPassId=0;f.items[7].id=107
 f.render(false,false)
 check(#f.jobs==1 and f.jobs[1].args[2]==107 and f.jobs[1].args[3]=='pass','City Glow lookup did not use the configured pass price')
 f.finish(1,{IsForSale=true,PriceInRobux=47})
 local glow=f.buttons[5]
 check(glow.Text=='R$ 47' and glow.Interactable,'City Glow did not display its runtime price')
 glow.callback()
 check(f.sent==1,'Available City Glow did not request checkout')
 for offset,key in ipairs({'SignalDeck','CityCrest','PulseFrame','RouteLights','HarborBadge','SprintRibbon'}) do
  f=fixture()
  for i=1,4 do f.items[i].id=0 end
  f.config.MovementPassId=0;f.items[7+offset].id=107+offset
  f.render(false,false)
  check(#f.jobs==1 and f.jobs[1].args[2]==107+offset and f.jobs[1].args[3]=='pass','New pass looked up the wrong ID or information type')
  f.finish(1,{IsForSale=true,PriceInRobux=41+offset})
  local pass=f.buttons[5+offset]
  check(pass.Name=='Buy'..key and pass.Interactable and pass.Text=='R$ '..(41+offset),'New pass did not use the Roblox-returned price')
  pass.callback();check(f.sent==1,'Available new pass did not request checkout')
 end
 f=fixture();f.items[5].id=105;f.items[6].id=106
 f.render(false,false)
 check(#f.jobs==4 and f.buttons[3].Text~="R$ 79" and f.buttons[4].Text~="R$ 99",'Checkout displayed a suggested price or exceeded request limit')
 f.finish(3,{IsForSale=true,PriceInRobux=82})
 f.finish(4,{IsForSale=false})
 check(f.buttons[3].Text=="R$ 82" and f.buttons[3].Interactable,'Encore did not use the verified Marketplace price')
 check(f.buttons[4].Text=="UNAVAILABLE" and not f.buttons[4].Interactable,'Off-sale Afterimage was interactive')
 f.buttons[3].callback();f.buttons[4].callback();check(f.sent==1,'Pass availability did not gate the purchase action')
end
print('PASS',n,'actual price-path assertions; coroutine API and GUI mocks only')
'''
# Historical lifecycle repros retain their original UI copy and intended failure oracle.
if a.baseline or a.callback_baseline or a.disabled_baseline:
 checks='\n'.join(line for line in checks.split('\n') if not any(message in line for message in ('Spectrum concise copy missing','Repeated hue instruction retained','Hierarchy or action count changed','Supported landscape not compact')))

setup=setup.replace('HISTORICAL_FIXTURE',str(a.baseline or a.callback_baseline or a.disabled_baseline).lower())
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
  run(s.replace('"BoostsSection",violet)','"SpectrumFeature",violet)'), 'First-fold shortcut did not open boost section')
  run(s.replace('short and 36 or','short and 90 or'),'Spectrum actions below short first fold')
  run(s.replace('short and -108 or','short and -90 or'),'Spectrum actions overlap in the short pane')
  run(s.replace('if revision==generation then ui.jump(target) end','ui.jump(target)'),'Closed shop shortcut still directs scroll')
  run(s.replace('owned=data.harborBadgePass','owned=data.sprintRibbonPass'),'Harbor Badge ownership was conflated')
  run(s.replace('owned=data.signalDeckPass','owned=data.cityCrestPass'), 'Ownership of the new passes must remain independent')

  run(s.replace('height>=316','height>=326'),'Supported landscape not compact')
  run(s.replace('(#cosmeticOffers+2)*10+5','75'),'Sections are out of order')
  run(s.replace('owned=data.pulseFramePass','owned=data.routeLightsPass'),'Pulse Frame and Route Lights ownership were conflated')
  run(s.replace('rail.Interactable=false','rail.Interactable=true'),'Pulse trim captured beam input')

  run(s.replace('local id=Catalog.OfferId(item,Config.MovementPassId)\n local configured=id~=nil',
                'local id=item.key=="Movement" and Config.MovementPassId or item.id\n local configured=type(id)=="number" and id==id and id>0 and id<math.huge and id%1==0'),
      'Conflicting pass obtained a price request')
  worker=s[s.index('local function fetchPrice('):s.index('local function updatePrice(')]
  assert all(word not in worker for word in ['view.','apply(','button','data.']), 'Worker captures GUI context'
  print('PASS source contract: worker has no GUI/apply/snapshot reference; not a GC proof')
