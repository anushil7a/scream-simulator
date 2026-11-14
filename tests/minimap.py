"""Actual CityMap construction/projection/controller in mocks; no native layout claim."""
from pathlib import Path
import argparse,subprocess,tempfile,re
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');p.add_argument('--baseline',action='store_true');args=p.parse_args()
def read(path):return subprocess.check_output(['git','show','b5ba1aa:'+path],cwd=root,text=True,encoding='utf-8') if args.baseline else (root/path).read_text(encoding='utf-8')
source=read('src/StarterPlayer/StarterPlayerScripts/CityMap.luau')
source=source[source.index('local CityMap={}'):]
setup=r'''
local checks=0;local function check(ok,msg)assert(ok,msg);checks+=1 end
local function near(a,b)return math.abs(a-b)<.000001 end
local UDim2={fromScale=function(x,y)return {X={Scale=x,Offset=0},Y={Scale=y,Offset=0}}end,fromOffset=function(x,y)return {X={Scale=0,Offset=x},Y={Scale=0,Offset=y}}end}
local UDim={new=function(s,o)return {Scale=s,Offset=o}end}
local Vector2={new=function(x,y)return {X=x,Y=y}end}
local Color3={fromRGB=function(r,g,b)return {r,g,b}end}
local Enum={Font={GothamBold=1},AspectType={FitWithinMaxSize=1},TextYAlignment={Top=1}}
UDim2.new=function(sx,ox,sy,oy)return {X={Scale=sx or 0,Offset=ox or 0},Y={Scale=sy or 0,Offset=oy or 0}}end
local objects={};local Instance={new=function(class)local obj={ClassName=class};table.insert(objects,obj);return obj end}
local Config={ZoneMin={X=-480,Z=-360},ZoneMax={X=480,Z=360}}
local CityMap=(function()
'''
tests=r'''
end)()
check(type(CityMap.MiniLayout)=='function' and type(CityMap.MiniUpdate)=='function','Minimap API missing')
local function find(parent,name)for _,o in ipairs(objects)do if o.Parent==parent and o.Name==name then return o end end end
local full=CityMap.create({});local mini=CityMap.create({},true)
for i=1,8 do check(find(full.map,'Landmark'..i)~=nil,'Modal landmark missing');check(not find(mini.map,'Landmark'..i),'Compact landmark clutter')end
for _,name in ipairs({'Arena','Beach','Promenade','TimberPier','ArenaBoundary'})do
 local a,b=find(full.map,name),find(mini.map,name);check(a~=nil and b~=nil,'Compact map geometry missing')
 for _,axis in ipairs({'X','Y'})do check(near(a.Position[axis].Scale,b.Position[axis].Scale) and near(a.Size[axis].Scale,b.Size[axis].Scale),'Compact geometry differs from full map')end
end
check(not find(full.map,'North') and not find(mini.map,'North'),'Retired north decoration retained')
check(not CityMap.mapHelp:find('North is up',1,true),'Retired orientation instructions retained')
check(full.arrow and not mini.arrow,'Compact facing arrow retained')
check(CityMap.arenaPercent==40,'Arena fraction changed')
local r={Parent={},Position={X=0,Z=0},CFrame={LookVector={X=0,Z=-1}}}
for _,point in ipairs({{-720,-600,0,0},{720,600,1,1},{0,0,.5,.5},{9999,-9999,1,0},{-600,240,1/12,.7}})do
 r.Position={X=point[1],Z=point[2]};CityMap.update(full,r)
 check(full.dot.Visible and near(full.dot.Position.X.Scale,point[3]) and near(full.dot.Position.Y.Scale,point[4]),'World projection changed')
end
for _,heading in ipairs({{0,-1,0},{1,0,90},{0,1,180},{-1,0,-90}})do
 r.CFrame.LookVector={X=heading[1],Z=heading[2]};CityMap.update(full,r);check(near(math.abs(full.arrow.Rotation),math.abs(heading[3])),'Facing rotation changed')
end
CityMap.update(full,nil);check(not full.dot.Visible,'Missing modal root shown')
r.Parent=nil;CityMap.update(full,r);check(not full.dot.Visible,'Detached modal root shown');r.Parent={}
local calls=0;local real=CityMap.update;CityMap.update=function(...)calls+=1;return real(...)end
CityMap.MiniUpdate(mini,r,0,true);check(calls==1 and mini.dot.Visible,'First mini update delayed')
CityMap.MiniUpdate(mini,r,.01,true);CityMap.MiniUpdate(mini,r,.099,true);check(calls==1,'Minimap throttle missing')
CityMap.MiniUpdate(mini,r,.101,true);check(calls==2,'Minimap cadence too slow')
CityMap.MiniUpdate(mini,r,.102,false);check(not mini.dot.Visible,'Hidden minimap marker retained')
local before=calls;CityMap.MiniUpdate(mini,r,.103,true);check(calls==before+1 and mini.dot.Visible,'Minimap reshow delayed')
CityMap.MiniUpdate(mini,nil,.104,true);check(not mini.dot.Visible,'Missing mini root retained')
before=calls;CityMap.MiniUpdate(mini,r,.105,true);check(calls==before+1 and mini.dot.Visible,'Minimap rejoin delayed')
r.Parent=nil;CityMap.MiniUpdate(mini,r,.106,true);check(not mini.dot.Visible,'Detached mini root retained');r.Parent={}
before=calls;CityMap.MiniUpdate(mini,r,.107,true);check(calls==before+1 and mini.dot.Visible,'Reattached mini root delayed')
local replacement={Parent={},Position={X=720,Z=600},CFrame={LookVector={X=1,Z=0}}}
before=calls;CityMap.MiniUpdate(mini,replacement,.108,true);check(calls==before+1 and near(mini.dot.Position.X.Scale,1),'Replacement root throttled')
check(not full.dot.Visible,'Minimap changed modal visibility')
local allocated=#objects;for i=1,100 do CityMap.MiniUpdate(mini,replacement,1+i/60,true)end;check(#objects==allocated,'Minimap allocates each update')

for _,size in ipairs({{320,568},{360,640},{390,844},{430,844},{460,844},{844,390},{640,360},{820,600},{1280,720},{320,240},{1024,320}})do
 for _,touch in ipairs({false,true})do
  local layout=CityMap.MiniLayout({X=size[1],Y=size[2]},touch)
  check(layout.width>=44 and layout.width<=160 and layout.height>=44,'Minimap dimensions out of bounds')
  if layout.expanded then
   check(size[1]-layout.width-14>=264,'Minimap overlaps left HUD')
   check(size[2]>=360 and layout.width>=96,'Minimap expanded in cramped viewport')
   check(near((layout.width-16)/(layout.height-52),1.2),'Compact map aspect allocation incorrect')
   if touch then check(14+layout.height<=size[2]-203+.000001,'Minimap overlaps touch controls')end
  else check(layout.width<=90 and layout.height==44,'Collapsed MAP target incorrect')end
  if size[1]<=360 or size[2]<360 then check(not layout.expanded,'Small viewport did not collapse')end
 end
end
print('PASS '..checks..' actual CityMap construction/projection/controller assertions; mocked only')
'''
def run(code,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',encoding='utf-8',delete=False) as f:f.write(code);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],text=True,capture_output=True)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if expected:assert r.returncode and expected in out,out;print('PASS negative control:',expected)
 else:assert r.returncode==0,out;print(out.strip())
client=read('src/StarterPlayer/StarterPlayerScripts/Client.client.luau')
client_checks=''
if not args.baseline:
 a=client.index('local miniMapButton=');creation=client[a:client.index('local function card(',a)]
 a=client.index(' testButton.Size=');layout=client[a:client.index(' hud.Position=',a)]
 a=client.index(' local miniVisible=');visibility=client[a:client.index(' talkButton.Text=',a)]
 client_setup=r'''
local gui={};local activated;local opens={};local allocations=0
local testButton={};local tight=false;local data={devAccess=false}
local GuiService={MenuIsOpen=false};local modal={Visible=false};local micPanel={Visible=false};local conversationPanel={Visible=false}
local function toggleTab(tab)table.insert(opens,tab)end
local function button(parent,name,text,size,pos,fn)allocations+=1;activated=fn;return {Parent=parent,Name=name,Text=text,Size=size,Position=pos}end
local function frame(parent,name,size,pos)allocations+=1;return {Parent=parent,Name=name,Size=size,Position=pos}end
'''
 client_end=r'''
check(miniMapButton.Name=="MiniMap" and miniMapButton.Text=="MAP",'MAP launcher missing')
activated();check(#opens==1 and opens[1]=='Map','MAP launcher opens wrong tab')
local os={clock=function()return 10 end}
local root={Parent={},Position={X=0,Z=0},CFrame={LookVector={X=0,Z=-1}}}
local fixedAllocations=#objects
for _,vp in ipairs({{279,844},{280,844},{320,167},{320,168},{320,314},{320,315},{320,568},{390,844},{430,844},{460,844},{844,390},{820,600}})do
 for _,touch in ipairs({false,true})do
  local viewport={X=vp[1],Y=vp[2]}
__LAYOUT__
  check(miniMapButton.Position.X.Offset==-miniLayout.width-14 and miniMapButton.Position.Y.Offset==14,'MAP position changed')
  check(miniMapButton.Size.X.Offset==miniLayout.width and miniMapButton.Size.Y.Offset==miniLayout.height,'MAP size wiring changed')
  for _,access in ipairs({false,true,'truthy'})do
   data={devAccess=access}
__LAYOUT__
   for _,gameplayVisible in ipairs({false,true})do
    for _,windowFocused in ipairs({false,true})do
     for _,busy in ipairs({false,true})do
      local toast={Visible=busy}
__VISIBILITY__
      local expected=miniLayout.available and gameplayVisible and windowFocused
      check(miniMapButton.Visible==expected,'MAP visibility gate failed')
      check(miniMapView.dot.Visible==(expected and miniLayout.expanded),'MAP marker visibility gate failed')
      check(testButton.Visible==(access==true),'Test access display changed')
     end
    end
   end
  end
 end
end
check(#objects==fixedAllocations and allocations==2,'Client reallocates minimap per tick')
check(miniMapView~=full and miniMapView~=mini,'Minimap reused modal state')
print('PASS '..checks..' actual minimap module/client assertions; synthetic layout/input only')
'''
 tracker_size=re.search(r'local tracked=label\(gui,"",(UDim2.fromOffset\(\d+,\d+\))',client)[1]
 hud_size=re.search(r'local hud=frame\(gui,"CompactHUD",(UDim2.fromOffset\(\d+,\d+\))',client)[1]
 controls_size=re.search(r'local controls=frame\(gui,"Actions",(UDim2.fromOffset\(\d+,\d+\))',client)[1]
 positions='\n'.join(next(line for line in client.splitlines() if line.startswith(' '+key+'.Position=')) for key in ['tracked','hud','controls','talkButton'])+'\n'+next(line for line in client.splitlines() if line.startswith(' controls.Size='))+'\n'+next(line for line in client.splitlines() if line.startswith(' talkButton.Size='))
 nav=client[client.index(' local tight=viewport.X<380'):client.index(' testButton.Size=')]
 nav_origin=re.search(r'local top=frame\(gui,"Navigation",UDim2.fromOffset\(\d+,\d+\),(UDim2.fromOffset\(\d+,\d+\))',client)[1]
 notice_source=read('src/StarterPlayer/StarterPlayerScripts/NoticeLayout.luau')
 notice_view=read('src/StarterPlayer/StarterPlayerScripts/NoticeView.luau')
 height_expression=re.search(r'self.panelHeight=([^;]+);self.overflow',notice_view)[1].replace('self.textHeight','(textHeight+8)')
 toast_geometry="local layout=NoticeLayout.Get(viewport.X,viewport.Y,touch,miniLayout,testAccess,true)\nlocal notice={x=layout.x,y=layout.y,w=layout.width,h="+height_expression+"}\n"
 client_setup+='\nlocal NoticeLayout=(function()\n'+notice_source+'\nend)()\n'
 sweep=r'''
local function rectangle(o,viewport)
 local x=o.Position.X.Scale*viewport.X+o.Position.X.Offset;local y=o.Position.Y.Scale*viewport.Y+o.Position.Y.Offset
 return {x=x,y=y,w=o.Size.X.Offset,h=o.Size.Y.Offset}
end
local function overlaps(a,b)return a.x<b.x+b.w and b.x<a.x+a.w and a.y<b.y+b.h and b.y<a.y+a.h end
for width=320,1280 do
 for _,height in ipairs({167,168,240,261,314,315,320,360,390,568,640,844})do
  for _,touch in ipairs({false,true})do
   for _,testAccess in ipairs({false,true})do
   local data={devAccess=testAccess};local testButton={}
   local viewport={X=width,Y=height}
   local tracked={Size=__TRACKER__};local hud={Size=__HUD__};local controls={Size=__CONTROLS__};local talkButton={}
   local top={Position=__NAVORIGIN__};local shop={Position=UDim2.fromOffset(0,0)};local questsToggle={}
__NAV__
   for _,child in ipairs({shop,questsToggle})do child.Position.X.Offset+=top.Position.X.Offset;child.Position.Y.Offset+=top.Position.Y.Offset end
__LAYOUT__
__POSITIONS__
   local m=rectangle(miniMapButton,viewport)
   check(miniLayout.available==(width>=280 and height>=(touch and 315 or 168)),'Minimap availability boundary wrong')
   if miniLayout.available then
   check(not overlaps(m,rectangle(tracked,viewport)),'Minimap overlaps quest tracker')
   check(not overlaps(m,rectangle(hud,viewport)),'Minimap overlaps actual HUD')
   check(not overlaps(m,rectangle(shop,viewport)) and not overlaps(m,rectangle(questsToggle,viewport)),'Minimap overlaps interactive navigation')
   if touch then check(not overlaps(m,rectangle(controls,viewport)),'Minimap overlaps actual touch controls '..width..'x'..height)end
   check(not overlaps(m,rectangle(talkButton,viewport)),'Minimap overlaps Talk button')
   for _,textHeight in ipairs({18,30,60,10000})do
__TOAST__
    if layout.available then
     check(not overlaps(m,notice),'Minimap overlaps visible notice viewport')
     if testAccess then check(not overlaps(rectangle(testButton,viewport),notice),'Tools overlap visible notice viewport')end
     check(not overlaps(rectangle(shop,viewport),notice) and not overlaps(rectangle(questsToggle,viewport),notice),'Notice overlaps navigation')
     if touch then check(not overlaps(rectangle(controls,viewport),notice),'Notice overlaps touch controls')end
     local talk=rectangle(talkButton,viewport)
     if layout.moveTalk then talk.x=layout.talkX;talk.y=layout.talkY end
     check(not overlaps(talk,notice),'Notice overlaps resolved TALK')
     check(not overlaps(talk,m),'Resolved TALK overlaps MAP')
     if testAccess then check(not overlaps(talk,rectangle(testButton,viewport)),'Resolved TALK overlaps tools')end
     if layout.moveTalk then check(talk.y==14,'Resolved TALK enters native thumbstick area')end
    else
     -- Explicit retained-message fallback, not a passed visibility/layout case.
     local baseTalk=rectangle(talkButton,viewport)
     check(layout.width<120 or layout.height<44 or (touch and (width<312 or overlaps(baseTalk,{x=layout.x,y=layout.y,w=layout.width,h=layout.height}))), 'Notice unavailable without constrained layout')
    end
   end
   if testAccess then
    local t=rectangle(testButton,viewport)
    check(t.y>=m.y+m.h+8 and not overlaps(m,t),'Tools overlap minimap')
    check(not overlaps(t,rectangle(hud,viewport)),'Tools overlap HUD '..width..'x'..height..' touch='..tostring(touch))
    check(not overlaps(t,rectangle(tracked,viewport)),'Tools overlap quest tracker '..width..'x'..height..' touch='..tostring(touch))
    if touch then check(not overlaps(t,rectangle(controls,viewport)),'Tools overlap touch controls')end
    check(not overlaps(t,rectangle(talkButton,viewport)),'Tools overlap Talk button')
   end
   end
   end
  end
 end
end
'''
 sweep=sweep.replace('__TOAST__',toast_geometry).replace('__NAVORIGIN__',nav_origin).replace('__NAV__',nav).replace('__TRACKER__',tracker_size).replace('__HUD__',hud_size).replace('__CONTROLS__',controls_size).replace('__POSITIONS__',positions).replace('__LAYOUT__',layout)
 client_end=client_end.replace("print('PASS '..checks..' actual minimap",sweep+"print('PASS '..checks..' actual minimap")
 client_checks=client_setup+creation+client_end.replace('__LAYOUT__',layout).replace('__VISIBILITY__',visibility)
code=setup+source+tests+client_checks
if args.baseline:run(code,'Minimap API missing')
else:
 run(code)
 if args.negative_controls:
  cases=[(code.replace('compact and {} or landmarks','{}'),'Modal landmark missing'),(code.replace('compact and {} or landmarks','landmarks'),'Compact landmark clutter'),(code.replace('if view.lastRoot==root and view.nextUpdate and now<view.nextUpdate', 'if false and view.lastRoot==root and view.nextUpdate and now<view.nextUpdate'),'Minimap throttle missing'),(code.replace('view.dot.Visible=false;view.nextUpdate=nil','view.dot.Visible=true;view.nextUpdate=nil'),'Hidden minimap marker retained'),(code.replace('viewport.X-278','viewport.X-200'),'Minimap overlaps left HUD'),(code.replace('miniMapAvailable and gameplayVisible and windowFocused','miniMapAvailable and gameplayVisible and windowFocused and not toast.Visible'),'MAP visibility gate failed'),(code.replace('width=math.min(width,math.max(119,viewport.X-328))',''),'Minimap overlaps quest tracker'),(code.replace('view.lastRoot==root and view.nextUpdate','view.nextUpdate'),'Replacement root throttled'),(code.replace('miniMapAvailable and gameplayVisible','gameplayVisible'),'MAP visibility gate failed'),(code.replace('touch and 315 or 168','touch and 314 or 167',1),'Minimap availability boundary wrong'),(code.replace('touch and 315 or 168','touch and 261 or 168'),'Minimap overlaps Talk button')]
  cases.append((code.replace('width-map.width-22','width-14'),'Resolved TALK overlaps MAP'))
  cases.extend([(code.replace(" for i,v in ipairs(compact and {} or landmarks)"," box(map,'North',.04,.025,.25,.075,cream)\n for i,v in ipairs(compact and {} or landmarks)"),'Retired north decoration retained'),(code.replace("if not compact then arrow=text","if true then arrow=text"),'Compact facing arrow retained')])
  cases.extend([(code.replace('viewport.X<432 and -100 or -126','viewport.X<432 and -104 or -126'),'Tools overlap Talk button'),(code.replace('viewport.X<356 and miniLayout.height+74','viewport.X<0 and miniLayout.height+74'),'Tools overlap HUD')])
  for changed,message in cases:
   assert changed!=code,'Mutation did not match: '+message
   run(changed,message)

