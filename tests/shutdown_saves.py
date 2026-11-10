"""Actual shutdown callback with a fake scheduler/save, not Roblox persistence."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=s.index('local function shutdown()');b=s.index('game:BindToClose(shutdown)',a)
setup='''
local now=0;local os={clock=function()return now end}
local sessions={};local departuresInFlight=0;local joinsInFlight=0;local closing=false
local closes,cancels=0,0
local function closeConversation()closes+=1 end
local function cancelSustained()cancels+=1 end
local VoiceCombat={Cancel=function()end}
local queue={};local waits=0;local hold=false;local departureDone
local task={spawn=function(fn)table.insert(queue,fn)end,wait=function(dt)
 now+=dt;waits+=1
 if not hold then local pending=queue;queue={};for _,fn in ipairs(pending)do fn() end end
 if departureDone and now>=departureDone then departuresInFlight=0 end
end}
local calls={};local warnings=0;local warn=function()warnings+=1 end
local Profiles={Save=function(id,data,release)
 assert(next(sessions)==nil,'Final save began before all gameplay sessions detached')
 table.insert(calls,{id=id,data=data,release=release})
 if id==2 then error('synthetic save failure') end
 if id==5 then return false,'retry' end
 return true
end}
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
shutdown();check(waits==0,'Empty shutdown waited')
local ordinary={coins=5};local baseline={coins=8}
sessions[{UserId=1}]={canSave=true,data=ordinary}
sessions[{UserId=2}]={canSave=true,data={coins=9999},testBaseline=baseline}
sessions[{UserId=3}]={canSave=false,data={}}
shutdown()
check(#calls==2,'Shutdown omitted legitimate save or saved temporary data')
for _,call in ipairs(calls)do
 check(call.release==true and call.data==(call.id==1 and ordinary or baseline),'Shutdown changed baseline/release')
end
check(warnings==1 and waits==1 and now<1,'Exception leaked pending shutdown counter')
check(closing and next(sessions)==nil and closes==3 and cancels==3,'Shutdown retained gameplay or attacks')
sessions[{UserId=5}]={canSave=true,data={}}
shutdown();check(warnings==2,'Returned save failure was silently ignored')
sessions={};departuresInFlight=1;departureDone=now+.5
shutdown();check(departuresInFlight==0 and now<2,'Shutdown skipped detached departure save')
departureDone=nil;departuresInFlight=1;local start=now
shutdown();check(now-start>=25 and now-start<25.2,'Detached save wait was unbounded')
departuresInFlight=0;joinsInFlight=1;start=now;shutdown()
check(now-start>=25 and now-start<25.2,'In-flight join wait was unbounded')
joinsInFlight=0;hold=true;sessions[{UserId=4}]={canSave=true,data={}}
start=now;shutdown()
check(now-start>=25 and now-start<25.2 and #queue==1,'Pending shutdown save wait was unbounded')
print('PASS '..checks..' actual shutdown checks with mocked scheduler/saves')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+s[a:b]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
