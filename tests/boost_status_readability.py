"""Actual Shop Render/Tick/Clear and Client UI constructors; modeled allocations, no native fit claim."""
from pathlib import Path
import argparse
import ast
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PATH = 'src/StarterPlayer/StarterPlayerScripts/ShopUI.luau'
BASE = '5622daa54424e639e7d3f671b2e453ff377b2cb6'

VIEW = r'''
 local Color3={};function Color3.new(r,g,b)return {R=r,G=g,B=b}end
 function Color3.fromRGB(r,g,b)return Color3.new(r/255,g/255,b/255)end
 function Color3.fromHSV(h,s,v)return {H=h,S=s,V=v}end
 local UDim={new=function(scale,offset)return {Scale=scale,Offset=offset}end}
 local UDim2={new=function(sx,ox,sy,oy)return {X={Scale=sx or 0,Offset=ox or 0},Y={Scale=sy or 0,Offset=oy or 0}}end}
 function UDim2.fromOffset(x,y)return UDim2.new(0,x,0,y)end;function UDim2.fromScale(x,y)return UDim2.new(x,0,y,0)end
 local Enum={InfoType={GamePass='pass',Product='product'},Font={GothamBlack=1,GothamBold=2,GothamMedium=3},TextXAlignment={Center=1,Left=2}}
 local ColorSequence={new=function(v)return v end};local ColorSequenceKeypoint={new=function(t,v)return {Time=t,Value=v}end}
 local function signal()
  local s={listeners={}};function s:Connect(fn)local c={Connected=true,fn=fn};function c:Disconnect()self.Connected=false end;table.insert(self.listeners,c);return c end
  function s:Fire()for _,c in ipairs(self.listeners)do if c.Connected then c.fn()end end end;return s
 end
 f.nodes={};f.cards={};f.actions={}
 local function node(class)local p={ClassName=class,Activated=signal()};table.insert(f.nodes,p);return p end
 local Instance={new=node}
'''

UI = r'''
 local clientDestroyed=false;local dark=Color3.fromRGB(8,14,28);local white=Color3.new(1,1,1);local panel=Color3.fromRGB(18,28,46)
 local content=node('Frame')
CLIENT_HELPERS
CLIENT_CARD
 local ui={card=function(h)local p=card(h);table.insert(f.cards,p);return p end,frame=frame,label=label}
 ui.button=function(...)local p=button(...);table.insert(f.buttons,p);return p end
 ui.info=function(text)f.info=text end
 local action={FireServer=function(_,verb,key)f.sent+=1;table.insert(f.actions,{verb,key})end}
 local function module()
'''

TAIL = r'''
 return {shop=Shop,stats=function()return {flight=priceInFlight,views=priceViews,timers=timers,records=prices}end}
 end
 local m=module();f.shop=m.shop;f.stats=m.stats
 function f.render(data,narrow)
  ui.narrow=narrow;content=node('Frame');f.nodes={content};f.cards={};f.buttons={};m.shop.Render(data,ui,action)
 end
 function f.finish(index,result)local ok,err=coroutine.resume(f.jobs[index].co,result);assert(ok,err);m.shop.Tick()end
 return f
end
'''

CHECKS = r'''
local function equal(a,b)
 if type(a)~='table' or type(b)~='table' then return a==b end
 for k,v in pairs(a)do if not equal(v,b[k])then return false end end
 for k in pairs(b)do if a[k]==nil then return false end end;return true
end
local function children(f,parent,omit)
 local t={};for _,p in ipairs(f.nodes)do if p.Parent==parent and p~=omit then table.insert(t,p)end end;return t
end
local function named(f,parent,name)for _,p in ipairs(f.nodes)do if p.Parent==parent and p.Name==name then return p end end end
local properties={'ClassName','Name','Size','Position','BackgroundColor3','BorderSizePixel','Text','TextSize','Font','TextColor3','TextXAlignment','TextWrapped','BackgroundTransparency','AutoButtonColor','Color','Transparency','Thickness','Rotation','CornerRadius','Active','Selectable','Interactable'}
local function graph(old,current,a,b,oldTimer,newTimer,boost)
 for _,key in ipairs(properties)do
  local exception=boost and ((a==oldTimer.label.Parent and key=='Size') or (a.Name=='Multiplier' and key=='BackgroundColor3') or (a.Parent and a.Parent.Name=='Multiplier' and key=='TextColor3') or (a.ClassName=='TextButton' and key=='Position'))
  if exception and key=='Size'then check(equal(a.Size.X,b.Size.X) and a.Size.Y.Scale==b.Size.Y.Scale,'Boost card width/scale changed')
  elseif exception and key=='Position'then check(equal(a.Position.X,b.Position.X) and a.Position.Y.Scale==b.Position.Y.Scale,'Boost button horizontal allocation changed')
  elseif not exception then check(equal(a[key],b[key]),'Protected UI property changed: '..tostring(a.Name)..' '..key)end
 end
 local aa=children(old,a,boost and oldTimer.label or nil);local bb=children(current,b,boost and newTimer.band or nil)
 check(#aa==#bb,'Unrelated UI nodes changed')
 for i,p in ipairs(aa)do graph(old,current,p,bb[i],oldTimer,newTimer,boost)end
end
local ink={R=9/255,G=14/255,B=28/255};local soft={R=160/255,G=178/255,B=208/255}
local green={R=112/255,G=230/255,B=174/255};local activeBand={R=18/255,G=42/255,B=40/255}
local function paint(f)
 for _,timer in ipairs(f.stats().timers)do
  local active=string.sub(timer.label.Text,1,6)=='ACTIVE'
  check(equal(timer.label.TextColor3,active and green or soft),'Status text paint does not match confirmed state')
  check(equal(timer.band.BackgroundColor3,active and activeBand or ink),'Status band paint does not match confirmed state')
  check(equal(timer.indicator.BackgroundColor3,active and green or soft),'Status indicator paint does not match confirmed state')
 end
end
local function trace(old,current)
 check(old.info==current.info,'Unrelated shop footer changed')
 check(old.sent==current.sent and equal(old.actions,current.actions),'Purchase/activation behavior diverged from baseline')
 check(#old.jobs==#current.jobs and old.stats().flight==current.stats().flight and #old.stats().views==#current.stats().views,'Price API/cache behavior changed')
 for i,job in ipairs(old.jobs)do check(job.args[2]==current.jobs[i].args[2] and job.args[3]==current.jobs[i].args[3],'Price API arguments changed')end
 check(equal(old.stats().records,current.stats().records),'Price record/cache state changed')
 check(#old.stats().timers==#current.stats().timers,'Timer ownership changed')
 for i,timer in ipairs(old.stats().timers)do
  local other=current.stats().timers[i]
  for _,key in ipairs({'ready','ends','serverNow','received'})do check(timer[key]==other[key],'Captured timer snapshot changed')end
  check(timer.label.Text==other.label.Text,'Timer text/arithmetic diverged from baseline')
 end
 for i,b in ipairs(old.buttons)do check(b.Text==current.buttons[i].Text and b.AutoButtonColor==current.buttons[i].AutoButtonColor,'Purchase/activation state changed')end
end
local function layout(f,narrow)
 for index,key in ipairs({'XP','Coins'})do
  local card=f.cards[index+1];local timer=f.stats().timers[index];local band=timer.band;local status=timer.label;local indicator=timer.indicator
  local tint=key=='XP' and {R=173/255,G=139/255,B=1} or {R=1,G=209/255,B=111/255}
  local badge=named(f,card,'Multiplier');local badgeText=children(f,badge)[2]
  check(equal(badge.BackgroundColor3,tint) and badgeText.Text=='2×' and equal(badgeText.TextColor3,ink),'Multiplier badge lost tint/ink identity')
  check(card.Size.Y.Offset==(narrow and 262 or 242),'Boost card height changed')
  check(band.Name=='BoostStatus' and band.Parent==card and band.Position.Y.Offset==(narrow and 148 or 128) and band.Size.Y.Offset==40,'Status band allocation changed')
  check(status.Name=='BoostStatusText' and status.Parent==band and status.TextSize==14 and status.Font==2 and status.TextWrapped,'Status label emphasis/wrapping changed')
  check(indicator.Name=='StateIndicator' and indicator.Parent==band and indicator.Position.X.Offset==8 and indicator.Size.X.Offset==3,'Status indicator allocation changed')
  for _,p in ipairs({band,indicator})do check(p.Active==false and p.Selectable==false and p.Interactable==false,'Passive status captured input')end
  local width=narrow and 300 or 660;local bandWidth=width-32;local labelWidth=bandWidth*status.Size.X.Scale+status.Size.X.Offset
  check(status.Position.X.Offset>=indicator.Position.X.Offset+indicator.Size.X.Offset+8 and status.Position.X.Offset+labelWidth<=bandWidth,'Status label overlaps indicator or band bounds')
  check(status.Size.Y.Scale==1 and status.Size.Y.Offset==0 and status.Position.Y.Offset==0,'Status label does not use full band height')
  for _,p in ipairs(children(f,card))do if p.ClassName=='TextButton'then
   check(p.Position.Y.Offset==(narrow and 202 or 182) and p.Size.Y.Offset==44 and p.Position.Y.Offset+p.Size.Y.Offset<=card.Size.Y.Offset-16,'Boost action lost 44px target or bottom clearance')
   check(p.Position.Y.Offset>=band.Position.Y.Offset+band.Size.Y.Offset+14,'Status and action overlap')
  end end
 end
end
for _,narrow in ipairs({false,true})do
 for _,ready in ipairs({false,true})do
  for _,saved in ipairs({false,true})do
   for _,saving in ipairs({false,true})do
    local data={savingAvailable=saving,shop={ready=ready,inventory={xp=saved and 3 or 0,coins=saved and 1 or 0},ends={xp=200,coins=100.001},serverNow=100}}
    local old=baseline();local current=fixture();old.render(data,narrow);current.render(data,narrow)
    trace(old,current);paint(current);layout(current,narrow)
    graph(old,current,old.cards[1],current.cards[1],nil,nil,false);graph(old,current,old.cards[4],current.cards[4],nil,nil,false)
    for i=1,2 do graph(old,current,old.cards[i+1],current.cards[i+1],old.stats().timers[i],current.stats().timers[i],true)end
    for _,now in ipairs({.001,.999,1,59.1,100,100.001})do old.now=now;current.now=now;old.shop.Tick();current.shop.Tick();trace(old,current);paint(current)end
    for _,f in ipairs({old,current})do for _,p in ipairs(f.buttons)do p.Activated:Fire()end end;trace(old,current)
    for index=1,4 do old.finish(index,{IsForSale=true,PriceInRobux=20+index});current.finish(index,{IsForSale=true,PriceInRobux=20+index})end;trace(old,current)
    for _,f in ipairs({old,current})do for _,p in ipairs(f.buttons)do p.Activated:Fire()end end;trace(old,current)
    for _,f in ipairs({old,current})do
     local stale=f.buttons;local timer=f.stats().timers[1];local text=timer.label.Text
     f.shop.Clear();check(#f.stats().timers==0 and #f.stats().views==0,'Clear retained status/price views')
     f.now+=100;f.shop.Tick();check(timer.label.Text==text,'Cleared status still ticks')
     local count=f.sent;for _,p in ipairs(stale)do p.Activated:Fire()end;check(f.sent==count,'Cleared callback still sends')
     f.render(data,narrow);for _,p in ipairs(stale)do p.Activated:Fire()end;check(f.sent==count,'Rerender admitted stale callback')
    end
    trace(old,current);paint(current)
   end
  end
 end
end
-- Resolve prices before their deadline so retained purchase callbacks are live.
for _,mode in ipairs({'clear','rerender','detach'})do
 local data={savingAvailable=true,shop={ready=true,inventory={xp=3,coins=1},ends={xp=200},serverNow=100}}
 local old=baseline();local current=fixture()
 for _,f in ipairs({old,current})do
  f.render(data,false);for i=1,4 do f.finish(i,{IsForSale=true,PriceInRobux=25})end
  local stale=f.buttons;for _,p in ipairs(stale)do p.Activated:Fire()end
  check(f.sent==6,'Confirmed available price/saved callback failed')
  if mode=='clear'then f.shop.Clear()elseif mode=='rerender'then f.render(data,false)else for _,p in ipairs(stale)do p.Parent=nil end end
  for _,p in ipairs(stale)do p.Activated:Fire()end;check(f.sent==6,'Stale available callback still sends after '..mode)
  f.render(data,false);for _,p in ipairs(f.buttons)do p.Activated:Fire()end;check(f.sent==12,'Fresh cached price/saved callback failed')
 end
 trace(old,current);paint(current)
end
local missing=fixture();missing.render({},true);paint(missing);for _,timer in ipairs(missing.stats().timers)do check(timer.label.Text=='Boost status unavailable','Missing ledger presented inactive/active')end
print('PASS',n,'boost state/layout/frozen9138743 graph/behavior assertions; actual constructors, mocked API/clock, no native glyph evidence')
'''


def build(source, baseline):
    tree = ast.parse((ROOT / 'tests/shop_price_requests.py').read_text(encoding='utf-8-sig'))
    head = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'setup' for t in n.targets))
    start = head.index(' local Color3=')
    head = head[:start] + VIEW + head[head.index(' local task=', start):]
    client = (ROOT / 'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text(encoding='utf-8-sig')
    helpers = client[client.index('local function frame(parent,'):client.index('-- Presentation only: no subscriptions,')]
    card = client[client.index('local function card(height)'):client.index('local function info(text,')]
    head = head[:head.index(' local ui={')] + UI.replace('CLIENT_HELPERS', helpers).replace('CLIENT_CARD', card)
    old = (head + baseline[:baseline.index('function Shop.ColorMixer(')] + TAIL).replace('local function fixture()', 'local function baseline()', 1)
    return old + head[head.index('local function fixture()'):] + source[:source.index('function Shop.ColorMixer(')] + TAIL + CHECKS


def run(source, baseline, expected=None):
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.luau', prefix='tmp_boost_status_', dir=ROOT / 'tests', delete=False) as f:
        path = Path(f.name)
        f.write(build(source, baseline))
    try:
        result = subprocess.run(['luau', str(path)], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=30)
    finally:
        path.unlink()
    output = result.stdout + result.stderr
    if expected:
        assert result.returncode and expected in output, output
        print('PASS control:', expected)
    else:
        assert result.returncode == 0, output
        print(output.strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--negative-controls', action='store_true')
    args = parser.parse_args()
    source = (ROOT / PATH).read_text(encoding='utf-8-sig')
    baseline = subprocess.check_output(['git', 'show', BASE + ':' + PATH], cwd=ROOT, text=True, encoding='utf-8')
    run(source, baseline)
    if args.negative_controls:
        cases = [
            ('timer.ready and remaining>0', 'timer.ready and remaining>=0', 'Status text paint does not match confirmed state'),
            ('timer.indicator.BackgroundColor3=active and Color3.fromRGB(112,230,174) or soft', 'timer.indicator.BackgroundColor3=soft', 'Status indicator paint does not match confirmed state'),
            ('timer.band.BackgroundColor3=active and Color3.fromRGB(18,42,40) or ink', 'timer.band.BackgroundColor3=ink', 'Status band paint does not match confirmed state'),
            ('UDim2.fromOffset(16,16),tint)', 'UDim2.fromOffset(16,16),ink)', 'Multiplier badge lost tint/ink identity'),
            ('narrow and 262 or 242', 'narrow and 244 or 210', 'Boost card height changed'),
            ('band.Interactable=false', 'band.Interactable=true', 'Passive status captured input'),
            ('narrow and 202 or 182', 'narrow and 184 or 158', 'Boost action lost 44px target or bottom clearance'),
            ('math.ceil(timer.ends-timer.serverNow-(os.clock()-timer.received))', 'math.floor(timer.ends-timer.serverNow-(os.clock()-timer.received))', 'Timer text/arithmetic diverged from baseline'),
            ('revision==generation and b and b.Parent and available', 'b and b.Parent and available', 'Stale available callback still sends after clear'),
            ('table.clear(timers);table.clear(priceViews)', 'table.clear(priceViews)', 'Clear retained status/price views'),
            ('One pass. Choose your beam hue.', 'Changed unrelated header', 'Protected UI property changed'),
        ]
        for old, new, expected in cases:
            assert source.count(old) == 1, old
            run(source.replace(old, new), baseline, expected)


if __name__ == '__main__':
    main()
