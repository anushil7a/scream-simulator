"""Actual boost-card/timer code with synthetic UI and clock; no native layout claim."""
from pathlib import Path
import argparse, ast, subprocess, tempfile
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
local timers={};local priceViews={};local Shop={};local generation=0
local UDim2={new=function(sx,ox,sy,oy)return {sx=sx,ox=ox,sy=sy,oy=oy}end,fromOffset=function(x,y)return {x=x,y=y}end,fromScale=function(x,y)return {sx=x,sy=y}end}
local Enum={TextXAlignment={Center=1},Font={GothamBlack=1}}
local violet,gold,ink,soft={},{},{},{}
local labels,buttons,buys,actions={},{},{},{}
local ui={card=function()return {}end,frame=function()return {}end}
ui.label=function(_,text)local label={Text=text};table.insert(labels,label);return label end
ui.button=function(_,name,text,size,pos,callback)local b={Text=text,Size=size,call=callback,Parent=true};buttons[name]=b;return b end
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

def full_code(module):
 tree=ast.parse((root/'tests/shop_price_requests.py').read_text())
 literals={n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str)}
 head=literals['setup'].replace('button=function(_,_,text,_,_,callback)','button=function(_,name,text,_,_,callback)').replace('local b={Text=text,Parent=true,callback=callback}','local b={Name=name,Text=text,Parent=true,callback=callback}')
 head=head.replace('local action={FireServer=function()f.sent+=1 end}', 'f.actions={};local action={FireServer=function(_,verb,kind)f.sent+=1;table.insert(f.actions,{verb,kind})end}')
 tail=literals['endsetup'].replace('return f\nend',r'''
function f.saved(ready,narrow)
 ui.narrow=narrow;f.buttons={};m.shop.Render({savingAvailable=true,shop={ready=ready,inventory={xp=3,coins=1},ends={},serverNow=100}},ui,action)
 local result={};for _,b in ipairs(f.buttons)do result[b.Name]=b end;return result
end
return f
end
''')
 body=r'''
for _,narrow in ipairs({false,true})do
 for _,kind in ipairs({'XP','Coins'})do
  for _,mode in ipairs({'clear','rerender','detach'})do
   local f=fixture();local buttons=f.saved(true,narrow);local old=buttons['Activate'..kind]
   old.callback();check(f.sent==1 and f.actions[1][1]=='ActivateBoost' and f.actions[1][2]==string.lower(kind),'Current saved boost callback failed')
   if mode=='clear'then f.shop.Clear()elseif mode=='rerender'then f.saved(true,narrow)else old.Parent=nil end
   for i=1,20 do old.callback()end
   check(f.sent==1,'Stale saved callback sent after '..mode..': '..kind)
   buttons=f.saved(true,narrow);buttons['Activate'..kind].callback();check(f.sent==2,'Reopened saved boost callback blocked')
   buttons=f.saved(false,narrow);buttons['Activate'..kind].callback();check(f.sent==2,'Unavailable current saved boost callback sent')
  end
 end
end
print('PASS',n,'full Shop.Render/Clear saved callback assertions; mocked UI/API')
'''
 return head+module[:module.index('function Shop.ColorMixer(')]+tail+body

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--negative-controls',action='store_true');parser.add_argument('--baseline',action='store_true');args=parser.parse_args()
 code=setup+render+'\n'+footer+'\n'+checks[:checks.index('for _,narrow')]+tick+checks[checks.index('for _,narrow'):]
 if args.baseline:
  old=subprocess.check_output(['git','show','1d88558:src/StarterPlayer/StarterPlayerScripts/ShopUI.luau'],cwd=root,text=True,encoding='utf-8');run(full_code(old),'Stale saved callback sent after clear: XP');run(full_code(old).replace("{'XP','Coins'}","{'Coins','XP'}"),'Stale saved callback sent after clear: Coins');raise SystemExit
 run(code)
 run(full_code(source))
 if args.negative_controls:
  run(code.replace('Starts automatically on confirmed delivery.','Starts automatically on confirmed delivery. Timer continues offline.'),'Shop mentions offline timer against owner wording')
  run(code.replace('ready=shop.ready==true','ready=true'),'Unknown boost status falsely reported inactive')
  run(code.replace('if count>0 then','if true then'),'New purchase still requires manual activation control')
  run(code.replace('and shop.ready then','and true then'),'Unavailable ledger submitted legacy activation')
  run(code.replace('or "Not active"','or "ACTIVE"'),'Active/inactive timer incorrect')

  for old,new,error in [('revision==generation and b and b.Parent and shop.ready','b and b.Parent and shop.ready','Stale saved callback sent after clear: XP'),('revision==generation and b and b.Parent and shop.ready','revision==generation and shop.ready','Stale saved callback sent after detach: XP')]:
   assert source.count(old)==1;run(full_code(source.replace(old,new)),error)
