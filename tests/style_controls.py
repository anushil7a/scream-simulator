"""Actual hue mixer and server color branches with synthetic inputs; no native UI/purchase claim."""
from config_fixture import inline_compact_layout
from pathlib import Path
import argparse,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');args=p.parse_args()
def read(path):
 return subprocess.check_output(['git','show','d4cf668:'+path],cwd=root,text=True,encoding='utf-8') if args.baseline else (root/path).read_text(encoding='utf-8')
shop=read('src/StarterPlayer/StarterPlayerScripts/ShopUI.luau')
server=read('src/ServerScriptService/Bootstrap.server.luau')
helpers=shop[shop.index('function Shop.Clear()'):shop.index('function Shop.Tick()')]
mixer=shop[shop.index('function Shop.ColorMixer('):shop.rindex('return Shop')]
a=server.index(' elseif verb=="SetCustomColor" then');branches=' if'+server[a+7:server.index(' elseif verb=="AcceptQuest" then',a)]+' end\n'
setup=r'''
local checks=0;local function check(ok,msg)assert(ok,msg);checks+=1 end
local C={};C.__index=C;local Color3={}
Color3.new=function(r,g,b)return setmetatable({R=r,G=g,B=b},C)end
Color3.fromRGB=function(r,g,b)return Color3.new(r/255,g/255,b/255)end
Color3.fromHex=function(s)s=s:gsub("#","");return Color3.fromRGB(tonumber(s:sub(1,2),16),tonumber(s:sub(3,4),16),tonumber(s:sub(5,6),16))end
function C:ToHex()return string.format("%02X%02X%02X",math.floor(self.R*255+.5),math.floor(self.G*255+.5),math.floor(self.B*255+.5))end
function C:ToHSV()
 local mx=math.max(self.R,self.G,self.B);local mn=math.min(self.R,self.G,self.B);local d=mx-mn;local h=0
 if d>0 then if mx==self.R then h=((self.G-self.B)/d)%6 elseif mx==self.G then h=(self.B-self.R)/d+2 else h=(self.R-self.G)/d+4 end;h/=6 end
 return h,mx==0 and 0 or d/mx,mx
end
Color3.fromHSV=function(h,s,v)
 h=(h%1)*6;local i=math.floor(h);local f=h-i;local p=v*(1-s);local q=v*(1-f*s);local t=v*(1-(1-f)*s)
 if i==0 then return Color3.new(v,t,p) elseif i==1 then return Color3.new(q,v,p) elseif i==2 then return Color3.new(p,v,t) elseif i==3 then return Color3.new(p,q,v) elseif i==4 then return Color3.new(t,p,v) else return Color3.new(v,p,q) end
end
local function signal()
 local s={items={}};function s:Connect(fn)local c={Connected=true,fn=fn};function c:Disconnect()self.Connected=false end;table.insert(self.items,c);return c end
 function s:Fire(...)for _,c in ipairs(self.items)do if c.Connected then c.fn(...)end end end;return s
end
local UIS={InputChanged=signal(),InputEnded=signal(),WindowFocusReleased=signal()}
local Enum={UserInputType={MouseButton1=1,Touch=2,MouseMovement=3,Keyboard=4},Font={GothamBold=1}}
local UDim2={new=function(sx,ox,sy,oy)return {X={Scale=sx or 0,Offset=ox or 0},Y={Scale=sy or 0,Offset=oy or 0}}end,fromOffset=function(x,y)return {X={Offset=x},Y={Offset=y}}end}
local ColorSequence={new=function(...)return {...}end};local ColorSequenceKeypoint={new=function(...)return {...}end}
local nodes,frames,buttons,actions,labels={},{},{},{},{}
local function node(class)local n={ClassName=class,InputBegan=signal(),FocusLost=signal(),AbsolutePosition={X=10},AbsoluteSize={X=100}};table.insert(nodes,n);return n end
local Instance={new=node};local ui={}
ui.card=function(h)local n=node('Frame');n.height=h;return n end
ui.frame=function(parent,name,size,pos,color)local n=node('Frame');n.Name=name;n.Size=size;n.Position=pos;n.Parent=parent;n.BackgroundColor3=color;frames[name]=n;return n end
ui.label=function(parent,text,size,pos)local n=node('TextLabel');n.Text=text;n.Size=size;n.Position=pos;n.Parent=parent;table.insert(labels,n);return n end
ui.button=function(parent,name,text,size,pos,fn)local n=node('TextButton');n.call=fn;n.Text=text;buttons[name]=n;return n end
local action={FireServer=function(_,verb,arg)table.insert(actions,{verb,arg})end}
local Shop={};local connections,timers={},{};local priceViews={};local generation=0
local accent=Color3.fromRGB(79,225,255);local violet,ink,soft=accent,accent,accent
local Config={Auras={Gold=Color3.fromHex('FFD16F'),Blue=Color3.fromHex('0000FF')}}
local Catalog=require('../src/ReplicatedStorage/Shared/ShopCatalog')
'''
tests=r'''
local function draw(pass,hex)
 Shop.Clear();nodes={};frames={};buttons={};actions={};labels={}
 local data={spectrumPass=pass,customColor=hex};Shop.ColorMixer(data,ui,action)
 check(data.customColor==hex,'Mixer mutated saved color');return data
end
local function input(kind,x)return {UserInputType=kind,Position={X=x}}end
local function equip()buttons.EquipCustom.call();return actions[#actions] and actions[#actions][2]end
local function full(hex)local _,s,v=Color3.fromHex(hex):ToHSV();return math.abs(s-1)<.00001 and math.abs(v-1)<.00001 end
for _,hex in ipairs({'123456','808080','000000','FFFFFF','a1b2c3'})do
 draw(true,hex)
 check(frames.HUE and not frames.SATURATION and not frames.BRIGHTNESS,'Extra color sliders remain')
 check(not frames.Preview and not frames.Core,'Color preview strip remains')
 check(frames.HUE.Size.Y.Offset==44,'Hue touch target is not 44px')
 for _,n in ipairs(nodes)do check(n.ClassName~='TextBox','Editable hex remains')end
 check(#actions==0,'Opening mixer submitted color')
 check(equip()==hex:upper(),'Opening mixer changed saved shade')
 draw(true,hex);check(equip()==hex:upper(),'Reopening mixer changed saved shade')
 local m=input(Enum.UserInputType.MouseButton1,35);frames.HUE.InputBegan:Fire(m)
 check(full(equip()),'Hue edit retained saturation or brightness')
 UIS.InputChanged:Fire(input(Enum.UserInputType.MouseMovement,60));check(equip()=='00FFFF','Mouse drag incorrect')
 UIS.InputEnded:Fire(m);UIS.InputChanged:Fire(input(Enum.UserInputType.MouseMovement,80));check(equip()=='00FFFF','Mouse drag continued after release')
 local t=input(Enum.UserInputType.Touch,10);frames.HUE.InputBegan:Fire(t)
 check(equip()=='FF0000','Touch start incorrect')
 frames.HUE.InputBegan:Fire(input(Enum.UserInputType.Touch,90));check(equip()=='FF0000','Second pointer hijacked drag')
 UIS.InputChanged:Fire(input(Enum.UserInputType.Touch,60));check(equip()=='FF0000','Unrelated touch hijacked drag')
 t.Position.X=60;UIS.InputChanged:Fire(t);check(equip()=='00FFFF','Touch drag incorrect')
 UIS.InputEnded:Fire(t);t.Position.X=80;UIS.InputChanged:Fire(t);check(equip()=='00FFFF','Touch continued after release')
 local x=input(Enum.UserInputType.MouseButton1,-90);frames.HUE.InputBegan:Fire(x);check(equip()=='FF0000','Lower hue clamp incorrect')
 UIS.InputChanged:Fire(input(Enum.UserInputType.MouseMovement,900));check(equip()=='FF0000','Upper hue clamp incorrect')
 local oldCount=#actions;local oldBar=frames.HUE;local staleEquip=buttons.EquipCustom.call
 Shop.Clear();staleEquip();check(#actions==oldCount,'Stale equip survived Clear')
 oldBar.InputBegan:Fire(input(Enum.UserInputType.MouseButton1,60));check(#actions==oldCount,'Stale input submitted color')
 for _,c in ipairs(oldBar.InputBegan.items)do check(not c.Connected,'Clear left bar connection')end
 for _,sig in ipairs({UIS.InputChanged,UIS.InputEnded,UIS.WindowFocusReleased})do for _,c in ipairs(sig.items)do check(not c.Connected,'Clear left global input connection')end end
 UIS.InputChanged:Fire(input(Enum.UserInputType.MouseMovement,60));check(equip()=='FF0000','Cleared mixer still handles drag')
end
draw(false,'123456');check(buttons.EquipCustom.Text=='PASS REQUIRED','Locked equip wording changed');buttons.EquipCustom.call();check(#actions==0,'Locked mixer submitted equip')
frames.HUE.InputBegan:Fire(input(Enum.UserInputType.Touch,60));buttons.EquipCustom.call();check(#actions==0,'Locked preview submitted equip')
draw(true,'123456');local stale=buttons.EquipCustom.call;local old=frames.HUE;local down=input(Enum.UserInputType.Touch,30);old.InputBegan:Fire(down)
draw(true,'654321');stale();down.Position.X=90;UIS.InputChanged:Fire(down);check(#actions==0 and equip()=='654321','Reopened mixer inherited stale drag')
draw(true,'123456');frames.HUE.InputBegan:Fire(input(Enum.UserInputType.Keyboard,60));check(equip()=='123456','Keyboard input edited hue')
'''
server_setup=r'''
local ShopCatalog=Catalog;local entitled=false
local Entitlements={HasSpectrum=function()return entitled end}
local Config={Auras={Gold=true,Blue=true,Red=true}};local p={};local s={data={aura='Blue',customColor='123456',useCustomColor=true}};local states=0
local function state()states+=1 end
local function apply(verb,arg)
'''
beam_color=server[server.index('local function beamColor('):server.index('local function state(')]
server_tests=r'''
end
for _,arg in ipairs({'Blue','Red','Unknown','',{},42})do
 apply('SetAura',arg);check(s.data.aura=='Blue' and s.data.useCustomColor==true and states==0,'Forged free aura accepted')
end
apply('SetAura','Gold');check(s.data.aura=='Gold' and not s.data.useCustomColor and s.data.customColor=='123456' and states==1,'Yellow base changed legacy custom data')
for _,pass in ipairs({false,true})do
 entitled=pass
 for _,arg in ipairs({'abcdef','#123456','bad','12345G',{},123})do
  local old=s.data.customColor;local n=states;local hex=Catalog.Hex(arg);apply('SetCustomColor',arg)
  if pass and hex then check(s.data.customColor==hex and s.data.useCustomColor and states==n+1,'Valid entitled color rejected')
  else check(s.data.customColor==old and states==n,'Invalid or unentitled custom color accepted')end
 end
end
s.data.aura='Blue';s.data.customColor='123456';s.data.useCustomColor=true
entitled=true;check(beamColor(p,s):ToHex()=='123456','Custom beam shade changed')
entitled=false;check(beamColor(p,s)=='Blue','Legacy beam aura lost without pass')
entitled=true;s.data.useCustomColor=false;check(beamColor(p,s)=='Blue','Legacy equipped aura changed')
print('PASS '..checks..' actual mixer/server branch checks; synthetic input only')
'''
def run(code,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',encoding='utf-8',delete=False)as f:f.write(code);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],text=True,capture_output=True)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if expected:assert r.returncode and expected in out,out;print('PASS negative control:',expected)
 else:assert r.returncode==0,out;print(out.strip())
code=setup+helpers+mixer+tests+server_setup+branches+server_tests.replace('s.data.aura=\'Blue\';s.data.customColor',beam_color+'s.data.aura=\'Blue\';s.data.customColor')
if args.baseline:run(code,'Extra color sliders remain')
else:
 run(code)
 if args.negative_controls:
  run(code.replace('revision==generation and data.spectrumPass then action:FireServer','revision==generation then action:FireServer'),'Locked mixer submitted equip')
  run(code.replace('hex and Entitlements.HasSpectrum(p)','hex'),'Invalid or unentitled custom color accepted')
  run(code.replace('arg=="Gold"','Config.Auras[arg]'),'Forged free aura accepted')
  run(code.replace('connection:Disconnect()','-- connection:Disconnect()\n'),'Clear left bar connection')
  run(code.replace('Color3.fromHSV(hue,1,1)','Color3.fromHSV(hue,.5,.5)'),'Hue edit retained saturation or brightness')
  run(code.replace('if revision==generation and data.spectrumPass then','if data.spectrumPass then'),'Stale equip survived Clear')
  run(code.replace('or dragInput then return end','then return end'),'Second pointer hijacked drag')

# Isolated real Profiles module, fake atomic store only.
profile_preamble="\nlocal Healing=require('../src/ReplicatedStorage/Shared/Healing')\nlocal Combat=require('../src/ReplicatedStorage/Shared/VoiceCombat')\nlocal Lease=require('../src/ReplicatedStorage/Shared/ProfileLease')\nlocal Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}\nlocal Color3={fromRGB=function(r,g,b)return {r,g,b}end}\nlocal Progression=(function()\n"
profile_after_progression="\nend)()\n-- MUTATION_INSERT\nlocal script={Parent={WaitForChild=function(_,name)return name end}}\nlocal config\nlocal require=function(name)\n if name=='Healing' then return Healing elseif name=='VoiceCombat' then return Combat elseif name=='Progression' then return Progression\n elseif name=='Config' then return config elseif name=='Lease' then return Lease end\n error('Unexpected dependency '..tostring(name))\nend\nlocal function loadConfig()\n"
profile_after_config="\nend\nconfig=loadConfig()\nlocal now,clock,guid=1000,100,0\nlocal os={time=function()return now end,clock=function()return clock end}\nlocal task={wait=function(t)now+=t;clock+=t end}\nlocal durable;local writes=0\nlocal store={UpdateAsync=function(_,key,transform)\n assert(key=='Player_7','Unexpected test key');writes+=1\n local result=transform(durable)\n if result~=nil then durable=result end\n return result\nend}\nlocal services={DataStoreService={GetDataStore=function(_,name)assert(name=='ScreamSimulator_v1','Wrong fake store');return store end},\n ReplicatedStorage={Shared={Config='Config',ProfileLease='Lease'}},RunService={IsStudio=function()return false end},\n HttpService={GenerateGUID=function()guid+=1;return 'retirement-'..guid end}}\nlocal game={JobId='retirement-fixture',GetService=function(_,name)return services[name]end}\nlocal warn=function()end\nlocal function loadProfiles()\n"
profile_checks=r"""
end
local P=loadProfiles();local count=0
local function ck(ok,msg)assert(ok,msg);count+=1 end
local function preserved(d)
 ck(d.aura=='Mint','Legacy aura discarded');ck(d.customColor=='123456' and d.useCustomColor==true,'Legacy custom shade discarded')
 ck(d.level==50 and d.xp==12 and d.coins==321 and d.sound=='TinyAah','Unrelated progression changed')
end
local seed={schemaVersion=4,level=50,xp=12,coins=321,sound='TinyAah',aura='Mint',customColor='123456',useCustomColor=true}
ck(config.Auras.Mint~=nil,'Legacy aura removed from catalog')
for i=1,4 do seed=P.Sanitize(seed);preserved(seed)end
durable=seed
local d,ok=P.Load(7);ck(ok,'Fake load failed');preserved(d)
ck(P.Save(7,d,false)==true,'Fake autosave failed');preserved(durable)
ck(P.Save(7,d,true)==true,'Fake release failed');preserved(durable)
local d2,ok2=P.Load(7);ck(ok2,'Fake rejoin failed');preserved(d2)
ck(P.Save(7,d2,true)==true,'Fake second release failed')
local restarted=loadProfiles();local d3,ok3=restarted.Load(7);ck(ok3,'Fake restart load failed');preserved(d3)
ck(restarted.Save(7,d3,true)==true,'Fake restart release failed')
print('PASS '..count..' actual Profiles legacy style checks with fake atomic persistence')
"""
if not args.baseline:
 profile_source=read('src/ServerScriptService/Profiles.luau')
 profile_code=profile_preamble+read('src/ReplicatedStorage/Shared/Progression.luau')+profile_after_progression+inline_compact_layout(read('src/ReplicatedStorage/Shared/Config.luau'),root)+profile_after_config+profile_source+profile_checks
 run(profile_code)
 if args.negative_controls:
  run(profile_code.replace('data.aura=raw.aura','data.aura="Gold"'),'Legacy aura discarded')
  run(profile_code.replace('data.customColor=raw.customColor:upper()','data.customColor="FFFFFF"'),'Legacy custom shade discarded')

if not args.baseline:
 client=read('src/StarterPlayer/StarterPlayerScripts/Client.client.luau')
 a=client.index(' elseif selected=="Style" then\n')
 style=client[client.index('\n',a)+1:client.index(' elseif selected=="Map" then',a)]
 style_setup=r"""
local title,subtitle={},{};local gold=accent;local infoTexts={};local narrow=false
local card,frame,label,button=ui.card,ui.frame,ui.label,ui.button
local function info(text)table.insert(infoTexts,text)end
local ShopUI={ColorMixer=function(data,ui,action)end}
Config.MicroSpeakerPrice=100;Config.MovementPassId=0
local function renderStyle(data)
 buttons={};actions={};labels={};infoTexts={}
"""
 style_checks=r"""
end
for _,small in ipairs({false,true})do
 narrow=small
 for _,aura in ipairs({'Gold','Blue'})do
  for _,custom in ipairs({false,true})do
   local d={aura=aura,useCustomColor=custom,customColor='123456'};renderStyle(d)
   local count=0;for _ in pairs(buttons)do count+=1 end
   check(count==2 and buttons.BaseColor and buttons.MicroSpeaker,'Free palette cards remain')
   check(buttons.BaseColor.Text==((aura=='Gold' and not custom) and 'EQUIPPED' or 'USE YELLOW'),'Base selection status incorrect')
   check(d.aura==aura and d.customColor=='123456' and d.useCustomColor==custom,'Style render mutated saved selection')
   local legacy=false;for _,text in ipairs(infoTexts)do if string.find(text,'Your saved',1,true)then legacy=true end end
   check(legacy==(aura~='Gold' and not custom),'Legacy current selection notice incorrect')
   buttons.BaseColor.call();check(#actions==1 and actions[1][1]=='SetAura' and actions[1][2]=='Gold','Base card selects wrong aura')
  end
 end
end
print('PASS '..checks..' actual Style renderer assertions; narrow/wide mocks only')
"""
 style_code=setup+style_setup+style+style_checks
 run(style_code)
 if args.negative_controls:
  run(style_code.replace('action:FireServer("SetAura","Gold")','action:FireServer("SetAura","Blue")'),'Base card selects wrong aura')
  run(style_code.replace('data.aura~="Gold" and not data.useCustomColor','false'),'Legacy current selection notice incorrect')
