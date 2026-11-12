"""Actual menu teardown/scroll callback with mocked GUI and scheduling."""
from pathlib import Path
import subprocess
import tempfile
import re
root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
a=s.index('local renderRevision=0');b=s.index('button(modal,"Close","X"',a)
owner=s[s.index('local clientConnections={}'):s.index('local function loadClientDependency(')]
cleanup_source=re.search(r'ownClient\(function\(\) gui:Destroy\(\) end\)',s).group(0)+'\n'+re.search(r'ownClient\(function\(\) modal.Visible=false;renderedMenuKey=nil;renderRevision\+=1 end\)',s).group(0)
shop=s[s.index('local shopUsed=false'):s.index('ownClient(clearShop)')]
x=s.index(' task.spawn(function()',s.index('-- Restore only after AutomaticCanvasSize'))
y=s.index('\nend\nfor i,name',x)
setup='''
local modal={Visible=true};local ShopUI={Clear=function()end};local renderedMenuKey
local cleanup;local script={Destroying={Connect=function(_,fn)cleanup=fn;return {Disconnect=function()end}end}}
local gui={Destroy=function(self)self.destroyed=true end}
local queue={};local task={spawn=function(fn)table.insert(queue,fn)end}
local Run={Heartbeat={Wait=function()end}}
local Vector2={new=function(x,y)return {X=x,Y=y}end}
local content={AbsoluteCanvasSize={Y=500},AbsoluteWindowSize={Y=200},CanvasPosition={Y=0}}
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
schedule(120);queue[1]();check(content.CanvasPosition.Y==120,'Normal scroll restoration failed')
schedule(900);queue[2]();check(content.CanvasPosition.Y==300,'Scroll exceeded canvas bound')
schedule(80);renderRevision+=1;queue[3]();check(content.CanvasPosition.Y==300,'Older render overwrote newer scroll')
schedule(20);cleanup();queue[4]()
check(gui.destroyed,'Client teardown retained main HUD')
check(content.CanvasPosition.Y==300,'Deferred scroll wrote after teardown')
print('PASS '..checks..' actual menu cleanup checks with mocked GUI/scheduling')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(setup+owner+shop+s[a:b]+cleanup_source+'\nlocal function schedule(y)\nlocal revision=renderRevision;local scroll={Y=y}\n'+s[x:y]+'\nend\n'+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
