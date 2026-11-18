"""Execute actual Academy tools dispatcher with mocked sessions, not native Roblox proof."""
from pathlib import Path
import subprocess,tempfile,os
base=Path(__file__).resolve().parent
server=(base/'AcademyRoutePreview.luau').read_text()
client=(base/'AcademyRoutePreview.client.luau').read_text()
a=server.index(' bind(tools.OnServerEvent,');b=server.index(' local ray=RaycastParams.new();',a)
pre='''local checks=0;local function check(v,m) assert(v,m);checks+=1 end
local Rules=require("./AcademyRouteRules")
local now=1;local os={clock=function()return now end}
local studio=true;local Run={IsStudio=function()return studio end};local game={GameId=0,PlaceId=0}
local p={attrs={}};function p:SetAttribute(k,v)self.attrs[k]=v end
local stranger={};local states={[p]=Rules.New()};local flights={[p]={testBaseline={}}}
local toolSessions={[p]={percent=100,lastPower=-math.huge,lastFly=-math.huge,lastInput=-math.huge}}
local flightBounds={};local starts,stops,inputs=0,0,0
local Flight={Start=function(_,f,auth,bounds)check(auth and bounds==flightBounds and f.testBaseline,"authority");starts+=1;f.flight={};return true,"ok" end,
Input=function(_,f,arg)check(f==flights[p],"session");inputs+=1 end}
local function stopFlight(q)if flights[q]then flights[q].flight=nil;stops+=1 end end
local function sync()end
local callback;local tools={OnServerEvent=true};local function bind(_,fn)callback=fn end
'''
post='''
callback(stranger,"FlyOn");check(starts==0,"unknown player")
callback(p,"FlyOn",true);check(starts==0,"bad fly argument")
local s=states[p];s.held=true;s.direction={}
callback(p,"FlyOn");check(starts==1 and not s.held and s.direction==nil,"flight stops attack")
callback(p,"FlyOn");check(starts==1,"start rate cap")
callback(p,"FlyOff");check(stops==1 and not flights[p].flight,"off bypasses limit")
callback(p,"FlightInput",{x=0,y=0,z=0});callback(p,"FlightInput",{});check(inputs==1,"input rate limit")
now+=.1;callback(p,"FlightInput",{});check(inputs==2,"input cadence")
now+=1
for _,value in ipairs({-1,101,math.huge,0/0,"50",false,{}})do callback(p,"BeamPower",value)end
check(toolSessions[p].percent==100,"malformed power rejected")
callback(p,"BeamPower",25);check(toolSessions[p].percent==25 and p.attrs.AcademyBeamPercent==25,"power accepted")
callback(p,"FlyOn");check(starts==2,"power update cannot throttle Fly click");callback(p,"FlyOff")
callback(p,"BeamPower",100);check(toolSessions[p].percent==25,"power rate limit")
now+=1;s.held=true;s.direction={};callback(p,"BeamPower",0)
check(toolSessions[p].percent==0 and not s.held and s.released and not s.direction,"zero stops beam")
now+=1;callback(p,"BeamPower",100);check(toolSessions[p].percent==100,"100 accepted bounded")
for _,mode in ipairs({"studio","game","place"}) do
 studio=mode~="studio";game.GameId=mode=="game" and 1 or 0;game.PlaceId=mode=="place" and 1 or 0
 now+=1;callback(p,"FlyOn");callback(p,"BeamPower",50)
 check(starts==2 and toolSessions[p].percent==100,"local guard "..mode)
end
print("PASS "..checks.." actual Academy tools dispatcher checks (mocked)")
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=base,delete=False) as f:
    f.write(pre+server[a:b]+post);path=Path(f.name)
try:subprocess.run([os.environ.get('LUAU','luau'),str(path)],check=True)
finally:path.unlink()
# Integration contracts complement actual helper/dispatcher execution; not behavior proof.
for fragment in ['if flying(p) or not near(', 'if flying(p) or not s or s.stage~="Fight"',
 'if not flying(p) and s and spec.id=="metronome"', 'if h and not flying(p)',
 'if not s or flying(p) then return end', 'if flying(p) then',
 'stopFlight(p);flights[p]=nil;toolSessions[p]=nil', 'p.CharacterRemoving:Connect(function() stopFlight(p)',
 'max=Vector3.new(632,240,632)', 'Voice.Stats(s.level,power,', 'Rules.Dps(stats)*dt',
 'or power<=0 then continue end', 'fx:FireClient(p,origin,endpoint,stats.power)']:
    assert fragment in server,fragment
for fragment in ['testUntil=os.clock()+4', 'if testUntil and (now>=testUntil or (player:GetAttribute("AcademyCharge") or -1)<0) then stopBeam() end',
 'Enum.KeyCode.Home', 'Enum.KeyCode.B', 'windowFocused=false;hover()',
 'if not h or h.Health<=0', 'Instance.new("ScrollingFrame")', 'if ownsBeamInput(input) then stopBeam() end',
 'Vector3.new(.08+.22*power, .08+.22*power, length)', 'toolsRemote:FireServer("FlyOff"); alive = false']:
    assert fragment in client,fragment
print('PASS 24 Academy server/client integration contracts (source checks only)')
flight_start=client.index("local flightSent=")
flight_end=client.index("local function destinationForStage",flight_start)
pre='''
local active,focused,windowFocused=true,false,true
local keys={};local vertical=0
local GuiService={MenuIsOpen=false}
local Enum={
 KeyCode={W="W",A="A",S="S",D="D",Space="Space",LeftControl="Ctrl"},
 PreferredInput={Touch="touch"},ContextActionResult={Sink="sink",Pass="pass"},
 ContextActionPriority={High={Value=3000}},
}
local spaceAction
local ContextActionService={BindActionAtPriority=function(_,_,callback)spaceAction=callback end}
local UserInputService={
 TouchEnabled=true,PreferredInput="keyboard",
 IsKeyDown=function(_,key)return keys[key]==true end,
 GetFocusedTextBox=function()return focused end,
}
local Vector3={new=function(x,_,z)
 local v={X=x,Z=z,Magnitude=1};v.Unit=v;return v
end}
local h={MoveDirection={Dot=function(_,axis)return axis.X end}}
local root={CFrame={LookVector={X=0,Z=-1}}}
local player={
 GetAttribute=function()return active end,
 Character={FindFirstChildOfClass=function()return h end,FindFirstChild=function()return root end},
}
local input
local toolsRemote={FireServer=function(_,action,arg)assert(action=="FlightInput");input=arg end}
'''
post='''
keys.W=true;keys.Space=true;flightInput(1)
assert(input.x==0 and input.y==1 and input.z==1,"touch-enabled laptop keeps W and Space")
assert(spaceAction()=="sink","Space ascends without triggering normal jump")
keys={A=true,Space=false,Ctrl=true};flightInput(2)
assert(input.x==-1 and input.y==-1 and input.z==0,"touch-enabled laptop keeps A and Ctrl")
keys={};flightInput(3)
assert(input.x==0 and input.y==0 and input.z==0,"keyboard release ignores stale humanoid movement")
UserInputService.PreferredInput="touch";vertical=1;flightInput(4)
assert(input.x==1 and input.y==1 and input.z==0,"touch stick and lift still work")
focused=true;flightInput(5)
assert(input.x==0 and input.y==0 and input.z==0 and spaceAction()=="pass","text focus suppresses flight only")
active=false;focused=false;assert(spaceAction()=="pass","Space retains normal jump on ground")
print("PASS Academy keyboard, touch and Space flight input arbitration (mocked client)")
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=base,delete=False) as f:
    f.write(pre+client[flight_start:flight_end]+post);path=Path(f.name)
try:subprocess.run([os.environ.get('LUAU','luau'),str(path)],check=True)
finally:path.unlink()

heartbeat_start=server.index(' local last=0\n bind(Run.Heartbeat')
heartbeat_end=server.index('  for p,s in pairs(states) do',heartbeat_start)
pre='''
local now=0;local os={clock=function()return now end}
local Run={Heartbeat=true};local callback
local function bind(_,fn)callback=fn end
local workspace={};local world={Parent=workspace};local folder={Parent=workspace}
local flying={active=true};local idle={}
local flights={pilot=flying,grounded=idle};local flightBounds={}
local Rules={Tick=.1};local steps=0;local elapsed=0;local combatTicks=0
local Flight={
 Active=function(session)return session.active==true end,
 Step=function(player,session,authorized,bounds,time,dt)
  assert(player=="pilot" and session==flying and authorized and bounds==flightBounds and time==now)
  assert(dt==1/60,"flight receives frame dt rather than the combat interval")
  steps+=1;elapsed+=dt
 end,
}
'''
post='''
  combatTicks+=1
 end)
 for frame=1,30 do
  now=frame/60
  callback(1/60)
 end
 assert(steps==30 and math.abs(elapsed-.5)<1e-6,"active flight steps every heartbeat")
 assert(combatTicks>0 and combatTicks<steps,"combat stays throttled independently")
 flying.active=false;now=31/60;callback(1/60)
 assert(steps==30,"grounded avatars do not step flight")
 print("PASS Academy flight cadence independent of combat (mocked Heartbeat)")
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=base,delete=False) as f:
    f.write(pre+server[heartbeat_start:heartbeat_end]+post);path=Path(f.name)
try:subprocess.run([os.environ.get('LUAU','luau'),str(path)],check=True)
finally:path.unlink()

layout_start=client.index('local layoutWidth, layoutHeight, layoutTouch')
layout_end=client.index('local updateAt',layout_start)
pre='''
local writes=0
local function gui(props)
 return setmetatable({},{
  __index=props,
  __newindex=function(_,key,value) writes+=1;props[key]=value end,
 })
end
local Vector2={new=function(x,y)return {X=x,Y=y}end}
local UDim2={new=function(sx,x,sy,y)return {sx=sx,x=x,sy=sy,y=y}end}
UDim2.fromOffset=function(x,y)return UDim2.new(0,x,0,y)end
local panel=gui({})
local toolsPanel=gui({Position=UDim2.new(1,-12,0,92),AnchorPoint=Vector2.new(1,0)})
local toolsToggle=gui({Position=UDim2.new(1,-12,0,48),AnchorPoint=Vector2.new(1,0)})
local heading,objective,routeText,disclaimer=gui({}),gui({}),gui({}),gui({})
local guideButton=gui({Position=UDim2.new(0,5,1,-49)})
local clearButton,holdButton=gui({}),gui({})
'''
post='''
local function bounds(node,w,h)
 local size,pos,pivot=node.Size,node.Position,node.AnchorPoint or Vector2.new(0,0)
 local width,height=size.sx*w+size.x,size.sy*h+size.y
 local x,y=pos.sx*w+pos.x-pivot.X*width,pos.sy*h+pos.y-pivot.Y*height
 return {left=x,top=y,right=x+width,bottom=y+height}
end
local function intersects(a,b)
 return a.left<b.right and a.right>b.left and a.top<b.bottom and a.bottom>b.top
end
local cases={
 {320,568,true},{568,320,true},{480,320,true},{640,360,true},
 {768,1024,true},{1024,768,true},{510,500,false},{500,510,false},{600,550,false},{800,600,false},
 {800,600,true},{1920,1080,false},
}
for _,case in ipairs(cases) do
 local x,y,touch=table.unpack(case)
 local viewport=Vector2.new(x,y)
 local before=writes
 layoutHud(viewport,touch)
 assert(writes>before,"viewport or capability change must update layout")
 local course,tools,toggle=bounds(panel,x,y),bounds(toolsPanel,x,y),bounds(toolsToggle,x,y)
 local reticle={left=x/2-11,top=y/2-11,right=x/2+11,bottom=y/2+11}
 for _,rect in ipairs({course,tools,toggle}) do
  assert(rect.left>=0 and rect.top>=0 and rect.right<=x and rect.bottom<=y,"HUD inside viewport")
  assert(not intersects(rect,reticle),"HUD leaves center aim visible")
 end
 assert(not intersects(course,tools) and not intersects(course,toggle),"opened tools clear of course")
 local w,h=course.right-course.left,course.bottom-course.top
 local guide,clear,hold=bounds(guideButton,w,h),bounds(clearButton,w,h),bounds(holdButton,w,h)
 assert(guide.right<=clear.left and clear.right<=hold.left,"buttons have distinct hit areas")
 assert(clear.right-clear.left>=40 and hold.bottom<=h,"compact controls fit panel")
 before=writes
 layoutHud(Vector2.new(x,y),touch)
 assert(writes==before,"unchanged view must not write static GUI properties")
end
print("PASS "..#cases.." actual Academy HUD layout and unchanged-refresh checks (mocked geometry)")
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=base,delete=False) as f:
    f.write(pre+client[layout_start:layout_end]+post);path=Path(f.name)
try:subprocess.run([os.environ.get('LUAU','luau'),str(path)],check=True)
finally:path.unlink()

start=client.index('local function stopBeam()');end=client.index('connect(UserInputService.WindowFocusReleased',start)
fire=client.index('connect(fireTest.Activated,');fire_end=client.index('connect(flyButton.Activated,',fire)
tick=client.index(' local now = os.clock()\n flightInput(now)');tick_end=client.index(' if now - updateAt < .15 then return end',tick)
pre='''local n=0;local function check(v,m)assert(v,m);n+=1 end
local now=1;local os={clock=function()return now end};local held=false;local testUntil;local heldInput;local sentAt=-math.huge
local toolsPanel={Visible=true};local alive=true;local windowFocused=true;local attrs={AcademyBeamPercent=100,AcademyCharge=0};local health=100
local player={Character={FindFirstChildOfClass=function()return {Health=health}end},GetAttribute=function(_,k)return attrs[k]end}
local GuiService={MenuIsOpen=false};local focused=false
local panel={};local guiHits={}
local playerGui={GetGuiObjectsAtPosition=function()return guiHits end}
local UserInputService={GetFocusedTextBox=function()return focused end,InputBegan="begin",InputEnded="ended",InputChanged="changed"}
local Enum={UserInputType={MouseButton1="mouse",Touch="touch"},KeyCode={B="B",ButtonR2="R2"}}
local holdButton={InputBegan="button"};local Color3={fromRGB=function()end};local function aimDirection()return "fresh aim"end
local sent={};local inputRemote={FireServer=function(_,held,aim)table.insert(sent,{held,aim,now})end}
local fireTest={Activated="fire"};local callbacks={};local function connect(k,f)callbacks[k]=f end
local function flightInput()end
'''
post='''local function tick(t)now=t
'''+client[tick:tick_end]+'''end
attrs.AcademyCharge=nil;callbacks.fire();check(not held,"unknown readiness cannot queue")
attrs.AcademyCharge=-2;callbacks.fire();check(not held,"cooldown cannot queue")
attrs.AcademyCharge=2;callbacks.fire();check(not held,"existing beam cannot queue")
attrs.AcademyCharge=0
local keyboard={UserInputType="keyboard",KeyCode="B"}
local mouse={UserInputType="mouse",KeyCode="unknown",Position={X=200,Y=160}}
local trigger={UserInputType="gamepad1",KeyCode="R2",Position={Z=.05}}
callbacks.begin(keyboard,false)
check(held,"B starts manual beam")
callbacks.fire();check(held and not testUntil,"stale ready status cannot convert a manual hold to one-shot")
callbacks.ended(mouse);check(held,"mouse release leaves B held")
callbacks.changed(trigger);check(held,"trigger drift leaves B held")
callbacks.ended(keyboard);check(not held,"B release stops its beam")
callbacks.begin(mouse,true)
check(not held,"engine-consumed left mouse click does not fire")
callbacks.begin(mouse,false)
check(held,"unprocessed left click in world starts manual beam")
callbacks.ended({UserInputType="mouse",KeyCode="unknown"});check(not held,"mouse release stops its beam")
for _,blocker in ipairs({panel,toolsPanel,{Active=true},{IsA=function(_,class)return class=="GuiButton"end},
 {IsA=function(_,class)return class=="TextBox"end},{IsA=function(_,class)return class=="ScrollingFrame"end}}) do
 guiHits={blocker};callbacks.begin(mouse,false);check(not held,"HUD click does not fire")
end
guiHits={}
mouse.Position.Y=-1;callbacks.begin(mouse,false);check(not held,"top-bar click does not fire")
mouse.Position.Y=160
attrs.TestFlight=true;callbacks.begin(mouse,false);check(not held,"flight still blocks world mouse firing")
attrs.TestFlight=false
GuiService.MenuIsOpen=true;callbacks.begin(mouse,false);check(not held,"menu still blocks world mouse firing")
GuiService.MenuIsOpen=false
focused=true;callbacks.begin(mouse,false);check(not held,"text focus still blocks world mouse firing")
focused=false
windowFocused=false;callbacks.begin(mouse,false);check(not held,"unfocused viewport does not fire")
windowFocused=true;callbacks.begin(mouse,false);check(held,"fresh mouse press after focus starts beam")
callbacks.ended(mouse)
local touch={UserInputType="touch"}
callbacks.button(touch)
callbacks.ended({UserInputType="touch"});check(held,"other finger leaves firing touch held")
callbacks.ended(touch);check(not held,"firing touch release stops beam")
callbacks.begin(trigger,false)
callbacks.changed({UserInputType="gamepad2",KeyCode="R2",Position={Z=.05}})
check(held,"another gamepad leaves firing trigger held")
callbacks.changed({UserInputType="gamepad1",KeyCode="R2",Position={Z=.05}})
check(not held,"own trigger below threshold stops beam")
table.clear(sent)
callbacks.fire();check(held and testUntil==5 and #sent==1,"one click arms one bounded test");check(not toolsPanel.Visible,"firing folds tools clear of reticle")
callbacks.changed(trigger);check(held,"trigger drift leaves one-shot test running")
for i=1,30 do tick(1+i*.12)end
check(held and #sent>10 and sent[#sent][2]=="fresh aim","refreshes aim and hold pulses")
tick(5.01);check(not held and not testUntil and sent[#sent][1]==false,"test stops at four seconds")
local count=#sent;tick(10);check(#sent==count,"no recurring automatic fire")
callbacks.fire();callbacks.fire();check(not held and not testUntil,"second click explicitly stops")
for _,case in ipairs({"zero","fly","menu","focus","blur","death","cooldown"}) do
 attrs={AcademyBeamPercent=100,AcademyCharge=0};GuiService.MenuIsOpen=false;focused=false;windowFocused=true;health=100
 callbacks.fire();check(held,"setup "..case)
 if case=="zero"then attrs.AcademyBeamPercent=0 elseif case=="fly"then attrs.TestFlight=true elseif case=="menu"then GuiService.MenuIsOpen=true elseif case=="focus"then focused=true elseif case=="blur"then windowFocused=false elseif case=="death"then health=0 else attrs.AcademyCharge=-1 end
 tick(now+.13);check(not held and not testUntil,"interrupt "..case)
 callbacks.fire();check(not held,"cannot restart during "..case)
end
print("PASS "..n.." actual Academy one-shot/pulse/interruption checks (mocked client)")
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=base,delete=False) as f:
    f.write(pre+client[start:end]+client[fire:fire_end]+post);path=Path(f.name)
try:subprocess.run([os.environ.get('LUAU','luau'),str(path)],check=True)
finally:path.unlink()
a=server.index(' bind(input.OnServerEvent,');b=server.index(' bind(tools.OnServerEvent,',a)
pre='''local n=0;local function check(v,m)assert(v,m);n+=1 end
local Rules=require("./AcademyRouteRules")
local now=1;local os={clock=function()return now end};local p={};local states={[p]=Rules.New()}
local toolSessions={[p]={percent=100}}
local flight=false;local function flying()return flight end;local function body()return true end
local direction={X=0,Y=0,Z=-1};direction.Unit=direction
local typeof=function(v)return v==direction and "Vector3" or type(v)end
local callback;local input={OnServerEvent=true};local function bind(_,f)callback=f end
'''
post='''local s=states[p];s.nextCast=5
callback(p,true,direction,"TestStart");check(not s.held and not s.testOnce,"cooldown start rejected")
now=6;callback(p,true,direction,"TestPulse");check(not s.held,"rejected start never queues")
callback(p,true,direction,"TestStart");check(s.held and s.testOnce,"fresh test press")
now=6.12;callback(p,true,direction,"TestPulse");check(s.held and s.lastInput==now,"test pulse sustains")
now=10.01;callback(p,true,direction,"TestPulse");check(not s.held,"max hold ends test")
now=16;callback(p,true,direction,"TestPulse");check(not s.held,"expired test never queues")
callback(p,false);now+=.1;callback(p,true,direction,"TestStart");check(s.held,"fresh released press recovers")
callback(p,false);check(not s.testOnce and not s.held,"stop clears test marker")
now=30;callback(p,true,direction,"invalid");check(not s.held,"malformed mode rejected")
toolSessions[p].percent=0
for _,mode in ipairs({"TestStart","TestPulse","manual"})do
 callback(p,true,direction,mode=="manual" and nil or mode)
 check(not s.held and not s.testOnce,"zero rejects positive "..mode)
end
callback(p,false);check(s.released,"zero permits release")
toolSessions[p].percent=100;now+=1;callback(p,true,direction,"TestPulse");check(not s.held,"raising power cannot activate stale test")
flight=true;callback(p,true,direction,"TestStart");check(not s.held,"flight rejects test")
print("PASS "..n.." actual Academy Beam one-shot/server sequencing checks (mocked)")
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=base,delete=False) as f:
    f.write(pre+server[a:b]+post);path=Path(f.name)
try:subprocess.run([os.environ.get('LUAU','luau'),str(path)],check=True)
finally:path.unlink()
