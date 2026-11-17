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
 'max=Vector3.new(1592,600,1592)', 'Voice.Stats(s.level,power,', 'Rules.Dps(stats)*dt',
 'or power<=0 then continue end', 'fx:FireClient(p,origin,endpoint,stats.power)']:
    assert fragment in server,fragment
for fragment in ['testUntil=os.clock()+4', 'if testUntil and (now>=testUntil or (player:GetAttribute("AcademyCharge") or -1)<0) then stopBeam() end',
 'Enum.KeyCode.Home', 'Enum.KeyCode.B', 'windowFocused=false;hover()',
 'if not h or h.Health<=0', 'Instance.new("ScrollingFrame")', 'if not testUntil and (input == heldInput',
 'Vector3.new(.08+.22*power, .08+.22*power, length)', 'toolsRemote:FireServer("FlyOff"); alive = false']:
    assert fragment in client,fragment
print('PASS 24 Academy server/client integration contracts (source checks only)')
start=client.index('local function stopBeam()');end=client.index('connect(holdButton.InputBegan',start)
fire=client.index('connect(fireTest.Activated,');fire_end=client.index('connect(flyButton.Activated,',fire)
tick=client.index(' local now = os.clock()\n flightInput(now)');tick_end=client.index(' if now - updateAt < .15 then return end',tick)
pre='''local n=0;local function check(v,m)assert(v,m);n+=1 end
local now=1;local os={clock=function()return now end};local held=false;local testUntil;local heldInput;local sentAt=-math.huge
local toolsPanel={Visible=true};local alive=true;local windowFocused=true;local attrs={AcademyBeamPercent=100,AcademyCharge=0};local health=100
local player={Character={FindFirstChildOfClass=function()return {Health=health}end},GetAttribute=function(_,k)return attrs[k]end}
local GuiService={MenuIsOpen=false};local focused=false;local UserInputService={GetFocusedTextBox=function()return focused end}
local holdButton={};local Color3={fromRGB=function()end};local function aimDirection()return "fresh aim"end
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
callbacks.fire();check(held and testUntil==5 and #sent==1,"one click arms one bounded test");check(not toolsPanel.Visible,"firing folds tools clear of reticle")
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
