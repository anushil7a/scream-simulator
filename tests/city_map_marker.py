"""Actual map marker update with mocked GUI/vectors; no rendered layout evidence."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/CityMap.luau').read_text()
a=s.index('local function position(');b=s.index('local arenaStart',a)
c=s.index('function CityMap.update(');d=s.index('CityMap.legend=',c)
setup='''
local CityMap={}
local UDim2={fromScale=function(x,y)return {X={Scale=x},Y={Scale=y}}end}
local view={map={Parent=true},dot={},arrow={}}
local root={Parent=true,Position={X=0,Z=0},CFrame={LookVector={X=0,Z=-1}}}
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
'''
checks='''
CityMap.update(view,root)
check(view.dot.Visible and view.dot.Position.X.Scale==.5 and view.dot.Position.Y.Scale==.5,'Center projection failed')
check(view.arrow.Rotation==0,'North heading incorrect')
root.CFrame.LookVector={X=1,Z=0};CityMap.update(view,root)
check(view.arrow.Rotation==90,'East heading incorrect')
root.CFrame.LookVector={X=-1,Z=0};CityMap.update(view,root)
check(view.arrow.Rotation==-90,'West heading incorrect')
root.Position={X=1000,Z=-1000};CityMap.update(view,root)
check(view.dot.Position.X.Scale==1 and view.dot.Position.Y.Scale==0,'Outside-land projection escaped map bounds')
root.Parent=nil;CityMap.update(view,root)
check(not view.dot.Visible,'Detached old character retained player marker')
root.Parent=true;root.Position={X=-600,Z=240};CityMap.update(view,root)
check(view.dot.Visible and math.abs(view.dot.Position.X.Scale-1/12)<.0001 and view.dot.Position.Y.Scale==.7,'Respawn projection failed')
CityMap.update(view,nil);check(not view.dot.Visible,'Missing character retained marker')
view.map.Parent=nil;CityMap.update(view,root);check(not view.dot.Visible,'Removed map received updates')
print('PASS '..checks..' actual map marker checks with mocked GUI')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(setup+s[a:b]+s[c:d]+checks)
try: subprocess.run(['/opt/homebrew/bin/luau',str(path)],cwd=root,check=True)
finally: path.unlink()
