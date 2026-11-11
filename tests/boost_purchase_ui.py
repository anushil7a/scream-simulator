"""Actual boost-card/timer code with synthetic UI and clock; no native layout claim."""
from pathlib import Path
import argparse, subprocess, tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/StarterPlayer/StarterPlayerScripts/ShopUI.luau').read_text(encoding='utf-8')
start=source.index(' for index,key in ipairs({"XP","Coins"}) do')
render=source[start:source.index(' local movement=',start)]
footer=next(line for line in source.splitlines() if line.startswith(' ui.info("New boosts activate'))
tick=source[source.index('function Shop.Tick()'):source.index('local function purchaseButton(')]
setup='''
local Catalog=require('../src/ReplicatedStorage/Shared/ShopCatalog')
local checks=0;local function check(ok,msg)assert(ok,msg);checks+=1 end
local clock=0;local os={clock=function()return clock end,time=function()return 100 end}
local timers={};local priceViews={};local Shop={}
local UDim2={new=function(sx,ox,sy,oy)return {sx=sx,ox=ox,sy=sy,oy=oy}end,fromOffset=function(x,y)return {x=x,y=y}end,fromScale=function(x,y)return {sx=x,sy=y}end}
local Enum={TextXAlignment={Center=1},Font={GothamBlack=1}}
local violet,gold,ink,soft={},{},{},{}
local labels,buttons,buys,actions={},{},{},{}
local ui={card=function()return {}end,frame=function()return {}end}
ui.label=function(_,text)local label={Text=text};table.insert(labels,label);return label end
ui.button=function(_,name,text,size,pos,callback)local b={Text=text,Size=size,call=callback};buttons[name]=b;return b end
ui.info=function(text)table.insert(labels,{Text=text})end
local action={FireServer=function(_,verb,kind)table.insert(actions,{verb,kind})end}
local function stroke()end
local function purchaseButton(item,_,_,_,_,_,size)buys[item.key]=size end
local function draw(data,narrow)
 timers={};labels={};buttons={};buys={};actions={};clock=0
'''
checks='''
end
for _,narrow in ipairs({false,true}) do
 draw({shop={ready=true,inventory={xp=0,coins=0},ends={xp=200,coins=0},serverNow=100}},narrow)
 check(not buttons.ActivateXP and not buttons.ActivateCoins,'New purchase still requires manual activation control')
 check(buys.XP.sx==1 and buys.Coins.sx==1,'No-inventory purchase button not full width')
 local text='';for _,l in ipairs(labels)do text..=l.Text end
 check(string.find(text,'Starts automatically on confirmed delivery.',1,true)~=nil,'Automatic delivery notice missing')
 check(not string.find(text,'offline',1,true),'Shop mentions offline timer against owner wording')
 check(not string.find(text,'Activate when ready',1,true),'Stale manual-activation wording')
 Shop.Tick();check(string.find(timers[1].label.Text,'01:40',1,true)~=nil and timers[2].label.Text=='Not active','Active/inactive timer incorrect')
 clock=100;Shop.Tick();check(timers[1].label.Text=='Not active','Expired boost still shown active')
 draw({shop={ready=false,inventory={},ends={},serverNow=100}},narrow)
 check(timers[1].label.Text=='Boost status unavailable','Unknown boost status initially reported inactive')
 Shop.Tick();check(timers[1].label.Text=='Boost status unavailable' and timers[2].label.Text=='Boost status unavailable','Unknown boost status falsely reported inactive')
 draw({shop={ready=false,inventory={xp=3,coins=0},ends={},serverNow=100}},narrow)
 check(buttons.ActivateXP and buttons.ActivateXP.Text=='USE SAVED (3)' and not buttons.ActivateCoins,'Legacy saved inventory unavailable or fake inventory shown')
 check(buys.XP.sx==.5 and buys.Coins.sx==1,'Legacy/new purchase layout allocation wrong')
 buttons.ActivateXP.call();check(#actions==0,'Unavailable ledger submitted legacy activation')
 draw({shop={ready=true,inventory={xp=3,coins=1},ends={},serverNow=100}},narrow)
 buttons.ActivateXP.call();buttons.ActivateCoins.call()
 check(#actions==2 and actions[1][1]=='ActivateBoost' and actions[1][2]=='xp' and actions[2][2]=='coins','Saved boosts no longer usable')
end
print('PASS '..checks..' actual boost UI/timer checks with synthetic layout and clock')
'''
def run(code,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',encoding='utf-8',delete=False) as f:
  path=Path(f.name);f.write(code)
 try:
  r=subprocess.run(['luau',str(path)],capture_output=True,text=True,encoding='utf-8');out=r.stdout+r.stderr
  if expected:
   assert r.returncode and expected in out,out
   print('PASS negative control:',expected)
  else:
   print(out,end='');assert r.returncode==0,out
 finally:path.unlink()
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--negative-controls',action='store_true');args=parser.parse_args()
 code=setup+render+'\n'+footer+'\n'+checks[:checks.index('for _,narrow')]+tick+checks[checks.index('for _,narrow'):]
 run(code)
 if args.negative_controls:
  run(code.replace('Starts automatically on confirmed delivery.','Starts automatically on confirmed delivery. Timer continues offline.'),'Shop mentions offline timer against owner wording')
  run(code.replace('ready=shop.ready==true','ready=true'),'Unknown boost status falsely reported inactive')
  run(code.replace('if count>0 then','if true then'),'New purchase still requires manual activation control')
  run(code.replace('if shop.ready then','if true then'),'Unavailable ledger submitted legacy activation')
  run(code.replace('or "Not active"','or "ACTIVE"'),'Active/inactive timer incorrect')
