"""Actual client external-signal cleanup helper; mocked dispatch, not Roblox scheduling."""
from pathlib import Path
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
s = (root / 'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
helper = s[s.index('local clientConnections={}'):s.index('local originalTouchControls=')]
setup = '''
local cleanup
local script={Destroying={Connect=function(_,fn)cleanup=fn end}}
local listeners={}
local signal={Connect=function(_,fn)
 local connection={callback=fn,disconnects=0}
 function connection:Disconnect()self.disconnects+=1 end
 table.insert(listeners,connection);return connection
end}
'''
checks = '''
local checks=0
local function check(v,msg)assert(v,msg);checks+=1 end
local total=0
connectClient(signal,function(a,b)total+=a+b end)
connectClient(signal,function()total+=10 end)
listeners[1].callback(2,3);listeners[2].callback()
check(total==15,'Live callback arguments or dispatch changed')
cleanup()
check(listeners[1].disconnects==1 and listeners[2].disconnects==1,'Teardown did not disconnect every signal')
listeners[1].callback(2,3);listeners[2].callback()
check(total==15,'Queued callback ran after teardown')
cleanup()
check(listeners[1].disconnects==1,'Repeated cleanup disconnected twice')
check(connectClient(signal,function()error('late callback')end)==nil and #listeners==2,'Late setup retained a new listener')
check(#clientConnections==0,'Cleanup retained connection references')
print('PASS '..checks..' actual client connection checks with mocked signals')
'''
with tempfile.NamedTemporaryFile(mode='w', suffix='.luau', dir=root/'tests', delete=False) as f:
    path=Path(f.name);f.write(setup+helper+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
