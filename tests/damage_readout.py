"""Execute exact readout lifecycle placement against deterministic GuiObject doubles."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'src/StarterPlayer/StarterPlayerScripts/DamageReadout.luau').read_text()
fixture = r'''
local function V(x,y)
 return setmetatable({X=x,Y=y},{__sub=function(a,b)return V(a.X-b.X,a.Y-b.Y)end})
end
UDim2={fromOffset=V,new=function(a,b,c,d)return V(b or 0,d or 0)end}
Enum={Font={GothamBold="bold"}}
Instance={new=function()return {}end}
local View=(function()
'''
test = r'''
end)()
local function box(x,y,w,h,on)
 return {AbsolutePosition=V(x,y),AbsoluteSize=V(w,h),Visible=on~=false}
end
local gui=box(0,0,390,844)
local hud=box(14,64,242,94)
local tracked=box(16,160,290,50)
local guide=box(0,0,0,0,false)
local widget=View.new(gui,function() return {} end,function()return {}end,function()end)
local n=0
local function check(v)assert(v,debug.traceback());n+=1 end
local function step(now,available,...)
 widget:Step(now,.25,available,gui,hud,tracked,guide,...)
end
widget:Receive("active",20,60,0);step(.1,true);check(not widget.root.Visible)
widget:SetEnabled(true)
widget:Receive("active",0/0,7,1);widget:Receive("active",1,math.huge,1);check(widget.phase==nil)
widget:Receive("active",73/3,73,1);step(1.1,true)
check(widget.root.Visible and widget.root.Position.Y==218)
check(widget.value.Text=="24.3 DPS  /  73 TOTAL" and widget.header.Text=="BEAM DAMAGE")
step(1.2,false);check(not widget.root.Visible)
local notice=box(0,210,390,90)
step(1.3,true,notice);check(not widget.root.Visible)
local pane=box(0,95,390,190)
step(1.4,true,pane);check(not widget.root.Visible)
gui=box(0,0,844,390)
step(2,true,box(742,22,90,96),box(570,133,260,96))
check(widget.root.Visible and widget.root.Position.X==266 and widget.root.Position.Y==74)
-- Rotated phone safe area can be smaller and inset by camera/hardware zones.
gui=box(0,0,749,330);hud=box(14,64,242,94);tracked=box(16,160,290,50)
local launch,actions=box(623,66,112,44),box(475,135,260,96)
step(2.1,true,launch,actions,box(249.5,40,250,28))
check(widget.root.Visible and widget.root.Position.X==266 and widget.root.Position.Y==74)
guide=box(16,120,290,62)
step(2.11,true,launch,actions,box(314.5,81,120,44))
check(widget.root.Visible and widget.root.Position.X==442 and widget.root.Position.Y==74)
guide=box(0,0,0,0,false)
gui=box(0,0,1300,770);hud=box(14,662,242,94);tracked=box(16,64,290,50)
step(2.2,true);check(widget.root.Visible and widget.root.Position.X==14 and widget.root.Position.Y==610)
widget:Receive("recap",0,73,3)
check(widget.value.Text=="73 TOTAL DAMAGE" and widget.header.Text=="FIGHT RECAP")
for i=1,22 do step(3+i/4,i>10) end
check(widget.root.Visible and widget.phase=="recap")
for i=23,31 do step(3+i/4,true) end
check(not widget.root.Visible and widget.phase==nil)
widget:Receive("recap",0,19,11);step(24,false);check(widget.phase==nil)
widget:Receive("active",1,3,25);step(25,true);check(widget.root.Visible)
widget:Receive("clear",0,0,25);check(not widget.root.Visible)
widget:Receive("active",1,3,26);widget:SetEnabled(false);check(not widget.root.Visible and widget.phase==nil)
check(not widget.root.Active and not widget.root.Interactable and not widget.root.Selectable)
print("Damage readout: "..n.." layout/lifecycle checks")
'''
with tempfile.NamedTemporaryFile('w', suffix='.luau', dir=root/'tests', delete=False) as handle:
    handle.write(fixture + source + test)
    path = Path(handle.name)
try:
    subprocess.run(['luau', str(path)], check=True, cwd=root)
finally:
    path.unlink()
