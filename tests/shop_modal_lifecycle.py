"""Actual modal callbacks/render-cache gate and ShopUI with mock GUI/API; no native claims."""
from pathlib import Path
import argparse,ast,re,subprocess,tempfile
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--deferred-baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');a=p.parse_args()
path='src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
client=subprocess.check_output(['git','show','0619103:'+path],cwd=R,text=True,encoding='utf-8') if a.baseline else (R/path).read_text()
if a.deferred_baseline:client=subprocess.check_output(['git','show','74c77638d3c859324d2a2213440b0899688551c1:'+path],cwd=R,text=True,encoding='utf-8')
shop=(R/'src/StarterPlayer/StarterPlayerScripts/ShopUI.luau').read_text();shop=shop[:shop.rindex('return Shop')]
def literal(name):
 tree=ast.parse((R/'tests/shop_price_requests.py').read_text(encoding='utf-8-sig'))
 return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name)and t.id==name for t in n.targets))
setup=literal('setup')
setup=setup.replace('local services={',"local function signal()return {Connect=function(_,fn)local c={callback=fn,connected=true};function c:Disconnect()self.connected=false end;return c end}end\n local services={")
setup=setup.replace('UserInputService={}', 'UserInputService={InputChanged=signal(),InputEnded=signal()}')
setup=setup.replace('local Config={MovementPassId=104}',"local baseColor={ToHSV=function()return .5 end,ToHex=function()return 'FFFF00'end};local Config={MovementPassId=104,MaxLevel=100,Auras={Gold=baseColor}}")
setup=setup.replace('fromHSV=function()return {}end','fromHSV=function()return baseColor end').replace('fromRGB=function()return {}end','fromRGB=function()return baseColor end')
setup=setup.replace('local UDim2=', 'local Vector2={new=function(x,y)return {X=x,Y=y}end,zero={X=0,Y=0}};local UDim2=')
setup=setup.replace('ui.frame=function()return {}end','ui.frame=function()return {InputBegan=signal()}end')
# Actual callbacks are extracted by their source boundaries, not rewritten test behavior.
def callbacks(c):
 x=re.search(r'button\(modal,"Close","X".*?function\(\)(.*?)end\)',c).group(1)
 toggle=c[c.index('local function toggleTab('):c.index('\nlocal shop=button(top,')]
 dev=re.search(r'local testButton=button.*?function\(\)(.*?)end\);testButton',c).group(1)
 recal='' # Calibration panel and its close route were intentionally retired.
 convo=c[c.index('showConversation=function(info)'):].splitlines()[1]
 state=(c[c.index('local renderedMenuKey,renderedTab'):c.index('button(modal,"Close","X"')] if 'local function closeMenu()' in c else c[c.index('local renderedMenuKey,renderedTab'):c.index('local function menuKey()')])
 if 'local function ownClient(' in c: state+=c[:c.index('local function menuKey()')].rstrip().splitlines()[-1]+'\n'
 elif 'local function closeMenu()' in c: state+=re.search(r'script.Destroying:Connect\(function\(\)[^\n]*gui:Destroy\(\) end\)',c).group(0)+'\n'
 key=c[c.index('local function menuKey()'):c.index('render=function()')]
 head=c[c.index('render=function()'):];head=head[:head.index(' if selected=="Shop" then')]
 tail=c[c.index(' -- Restore only after AutomaticCanvasSize'):c.index('\nfor i,name in ipairs({"Shop"')]
 return x,toggle,dev,recal,convo,state,key,head,tail

def assemble(c):
 x,toggle,dev,recal,convo,state,key,head,tail=callbacks(c)
 open_helper=c[c.index('openMicSetup=function()'):c.index('local talkTarget')] if 'openMicSetup=function()' in c else ''
 tailSetup=literal('endsetup').split('return f\nend')[0]
 tailSetup=tailSetup.replace('records=prices','records=prices,connections=connections')
 context=r'''
local ShopUI=m.shop;local selected='Shop';local render;local closeMenu;local clientDestroyed=false;local clientConnections={};local button=ui.button
local modal={Visible=false};local gui={AbsoluteSize={X=720},Destroy=function()f.destroyed=true end}
local content={CanvasPosition={X=0,Y=40},AbsoluteCanvasSize={Y=600},AbsoluteWindowSize={Y=200},GetChildren=function()return {}end}

-- Passive tab decoration is exercised by menu_icons.py; retain real tab callbacks here.
local academy={tabIcons={},tabIcon=function()return {},{} end}
local tabs={};local panel={};local title={};local subtitle={};local mapDot;local narrow=false
local devPanel={Visible=false};local data={level=1,xp=0,xpNext=100,savingAvailable=true,settings={},quests={},aura='Gold',shop={ready=true,inventory={},ends={},serverNow=100}}
local destroyed={};local script={Destroying={Connect=function(_,fn)table.insert(destroyed,fn);return {Disconnect=function()end}end}}
local Run={Heartbeat={Wait=function()coroutine.yield()end}}
local oldGet=game.GetService;function game:GetService(name)if name=='HttpService'then return {JSONEncode=function()return 'stable'end}end;return oldGet(self,name)end
local function cancelCapture()end;local function setSprint()end;local mic={Calibrate=function()end};local sustainedControl=nil
local function closeConversation()end
local openMicSetup;local micSetupOpen=false;local micPanel={Visible=false}
'''
 input_setup="local keyCallback;local textFocus;local UIS={InputBegan={},GetFocusedTextBox=function()return textFocus end};local GuiService={};Enum.KeyCode={B='B'};local function connectClient(_,fn)keyCallback=fn end\n"
 if 'local function clearShop()' in c:
  owner=c[c.index('local clientConnections={}'):c.index('local function loadClientDependency(')]
  owner+='\n'+c[c.index('local shopUsed=false'):c.index('local ScreamEffects=')]
  owner+='\nownClient(function() gui:Destroy() end)\n'
 else:
  owner=re.search(r'script.Destroying:Connect\(function\(\) ShopUI.Clear\(\) end\)',c).group(0)+'\n'+c[c.index('script.Destroying:Connect(function()'):c.index('local originalTouchControls=')]
 renderbody=" if selected=='Shop' then ShopUI.Render(data,ui,action) elseif selected=='Style' then ShopUI.ColorMixer(data,ui,action) end\n"
 if 'local function clearShop()' in c:
  for verb in ('Render','ColorMixer'):
   line=next(line for line in c.splitlines() if 'ShopUI.'+verb+'(' in line)
   prefix=line.split('ShopUI.'+verb+'(')[0].strip()
   renderbody=renderbody.replace('ShopUI.'+verb+'(',prefix+'ShopUI.'+verb+'(')
 finish=r'''
f.closeX=function() XCLOSE end
f.closeDev=function() DEVCLOSE end
f.closeRecalibrate=function() RECALCLOSE end
f.closeConversation=function() CONVOCLOSE end
f.keyB=function()keyCallback({KeyCode='B'},false)end
f.blockedKeys=function()keyCallback({KeyCode='B'},true);GuiService.MenuIsOpen=true;keyCallback({KeyCode='B'},false);GuiService.MenuIsOpen=false;textFocus={};keyCallback({KeyCode='B'},false);textFocus=nil end
f.toggle=toggle;f.tab=toggleTab;f.content=content;f.modal=modal
f.destroy=function()for _,fn in ipairs(destroyed)do fn()end end
f.activateTab=function(name)tabs[name].callback()end
f.selected=function()return selected end
f.tick=function()ShopUI.Tick()end
f.flushScroll=function()for _,job in ipairs(f.jobs)do if #job.args==0 and coroutine.status(job.co)=='suspended'then assert(coroutine.resume(job.co))end end end
f.priceJobs=function()local out={};for _,job in ipairs(f.jobs)do if #job.args>0 then table.insert(out,job)end end;return out end
f.reply=function(index,result)local job=f.priceJobs()[index];assert(coroutine.resume(job.co,result));ShopUI.Tick()end
return f
end
'''.replace('XCLOSE',x).replace('DEVCLOSE',dev).replace('RECALCLOSE',recal).replace('CONVOCLOSE',convo)
 return setup+shop+tailSetup+context+owner+'\n'+state+'\n'+open_helper+'\nmodal.Visible=true;(function() '+x+' end)();check(not modal.Visible,"Early X close failed")\n'+key+toggle+'\n'+head+renderbody+tail+'\n'+input_setup+c[c.index('connectClient(UIS.InputBegan,function(input,processed)'):c.index('connectClient(UIS.InputEnded,function(input)')]+'\n'+c[c.index('for i,name in ipairs({"Shop"'):c.index('\nlocal conversationNPC',c.index('for i,name in ipairs({"Shop"'))]+'\n'+finish
checks=r'''
for _,route in ipairs({'closeX','toggle','keyB','sameTab','closeDev','closeConversation','destroy'})do
 local f=fixture();f.tab('Shop');check(#f.stats().views==4,'Opening did not render Shop')
 f.blockedKeys();check(f.modal.Visible,'Processed/menu/typing B closed modal')
 local jobs=f.priceJobs();check(#jobs==4,'Opening price call count wrong')
 local oldY=f.content.CanvasPosition.Y
 if route=='sameTab'then f.tab('Shop')else f[route]()end
 check((route=='destroy' and f.destroyed or not f.modal.Visible) and #f.stats().views==0,'Close wiring retained views: '..route)
 f.content.CanvasPosition={X=0,Y=77};f.flushScroll();check(f.content.CanvasPosition.Y==77,'Pending scroll survived close: '..route)
 f.now=1;for i=1,4 do f.reply(i,'error')end
 f.now=30;for i=1,120 do f.tick()end;check(#f.priceJobs()==4,'Hidden modal retried price: '..route)
 if route~='destroy'then
  f.tab('Shop');check(f.modal.Visible and #f.stats().views==4,'Unchanged key reopen lost subscriptions: '..route)
  check(#f.priceJobs()==8,'Open modal did not recover retry: '..route)
  f.flushScroll();check(f.content.CanvasPosition.Y==77,'Same-tab reopen lost scroll: '..route)
 end
end
local f=fixture();f.tab('Shop');f.closeX();f.now=1;for i=1,4 do f.reply(i,{IsForSale=true,PriceInRobux=20})end
check(#f.stats().views==0,'Late completion reinstated closed views')
f.tab('Shop');check(#f.priceJobs()==4 and #f.stats().views==4,'Fresh cache reopen lost price views')
f.activateTab('Style');local old={};for _,c in ipairs(f.stats().connections)do table.insert(old,c)end
check(#old==3,'Actual Style subscriptions missing')
f.closeX();for _,c in ipairs(old)do check(not c.connected,'Close retained Style connection')end
f.tab('Style');check(#f.stats().connections==3,'Unchanged Style reopen did not reconnect')
f.destroy();check(#f.stats().connections==0 and #f.stats().views==0,'Destroy retained subscriptions')
for _,result in ipairs({'error','success'})do
 local f=fixture();f.tab('Shop');f.closeX()
 for _,name in ipairs({'Shop','Screams','Quests','Style','Map','Settings'})do
  f.activateTab(name)
  check(#f.stats().views==0 and #f.stats().connections==0 and f.selected()=='Shop','Hidden tab callback rebuilt subscriptions or changed selection: '..name)
 end
 f.now=1;for i=1,4 do f.reply(i,result=='error' and 'error' or {IsForSale=true,PriceInRobux=20})end
 f.now=30
 for _,name in ipairs({'Shop','Screams','Quests','Style','Map','Settings'})do f.activateTab(name);f.tick()end
 check(#f.priceJobs()==4 and #f.stats().views==0,'Deferred hidden tabs retried completed prices')
 f.tab('Shop');check(#f.stats().views==4,'Deferred callback broke unchanged reopen')
 for _,name in ipairs({'Screams','Quests','Style','Map','Settings','Shop'})do
  f.activateTab(name);check(f.selected()==name and f.modal.Visible,'Visible tab switch failed: '..name)
 end
 check(#f.stats().views==4,'Visible Shop switch missing views')
 f.closeX();f.destroy();f.modal.Visible=true;f.activateTab('Style')
 check(#f.stats().connections==0 and f.selected()=='Shop','Destroyed tab callback rebuilt subscriptions')
end
print('PASS',n,'actual modal callback/cache + Shop price/style lifecycle assertions; mocked UI/API')
'''
def run(c,error=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=R/'tests',encoding='utf-8',delete=False)as t:t.write(assemble(c)+checks);q=Path(t.name)
 try:r=subprocess.run(['luau',str(q)],capture_output=True,text=True)
 finally:q.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS expected failure:',error)
 else:print(out,end='');assert r.returncode==0
if a.deferred_baseline:run(client,'Hidden tab callback rebuilt subscriptions or changed selection: Shop')
elif a.baseline:run(client,'Close wiring retained views: closeX')
else:
 assert client.index('local function closeMenu()')<client.index('button(modal,"Close","X"'), 'Close registered before helper initialization'
 run(client)
 if a.negative_controls:
  mutants=[('if clientDestroyed or not modal.Visible then return end;selected=name;render()', 'selected=name;render()', 'Hidden tab callback rebuilt subscriptions or changed selection: Shop'),('if clientDestroyed or not modal.Visible then return end;selected=name;render()', 'if not modal.Visible then return end;selected=name;render()', 'Destroyed tab callback rebuilt subscriptions'),('elseif k==Enum.KeyCode.B then toggle()','elseif k==Enum.KeyCode.B then do end','Close wiring retained views: keyB'),(next(line for line in client.splitlines() if line.startswith('button(modal,"Close","X"')),next(line for line in client.splitlines() if line.startswith('button(modal,"Close","X"')).replace('closeMenu()','modal.Visible=false'),'Close wiring retained views: closeX'),('if modal.Visible then closeMenu() else','if modal.Visible then modal.Visible=false else','Close wiring retained views: toggle'),('if not opening then closeMenu();return end','if not opening then modal.Visible=false;return end','Close wiring retained views: sameTab'),('if devPanel.Visible then closeMenu() end','if devPanel.Visible then modal.Visible=false end','Close wiring retained views: closeDev'),('cancelCapture();closeMenu();if devPanel','cancelCapture();modal.Visible=false;if devPanel','Close wiring retained views: closeConversation'),('renderedMenuKey=nil;renderRevision+=1','renderRevision+=1','Unchanged key reopen lost subscriptions'),('renderedMenuKey=nil;renderRevision+=1','renderedMenuKey=nil','Pending scroll survived close'),('ownClient(function() modal.Visible=false;renderedMenuKey=nil;renderRevision+=1 end)','ownClient(function() modal.Visible=false;renderedMenuKey=nil end)','Pending scroll survived close: destroy')]
  for old,new,error in mutants:
   assert client.count(old)==(2 if old=="renderedMenuKey=nil;renderRevision+=1" else 1),old;run(client.replace(old,new,1),error)
