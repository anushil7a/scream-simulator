"""Run actual Profiles source with a deterministic yielding store, never Roblox data."""
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / "src/ServerScriptService/Profiles.luau").read_text()
preamble = r'''
local Lease=require("../src/ReplicatedStorage/Shared/ProfileLease")
local records={};local pauseNext=false;local failures=0
local store={};local writes=0
function store:UpdateAsync(key,transform)
 writes+=1
 if pauseNext then pauseNext=false;coroutine.yield("update") end
 if failures>0 then failures-=1;error("Injected store failure") end
 local result=transform(records[key]);if result~=nil then records[key]=result end;return result
end
local config={Gear=require("../src/ReplicatedStorage/Shared/GearCatalog"),Progression={Challenges={},Normalize=function(l,x)return l or 1,x or 0 end},Quests={},Auras={Gold=true},GetSound=function()return {id="TinyAah",level=1} end}
local studio=true
local requestedStore,serviceCalls=nil,0
local services={DataStoreService={GetDataStore=function(_,name)requestedStore=name;return store end},ReplicatedStorage={Shared={Config="Config",ProfileLease="Lease"}},RunService={IsStudio=function()return studio end},HttpService={GenerateGUID=function()return "test-owner" end}}
local game={JobId="test-job",GameId=0,PlaceId=0,GetService=function(_,name)
 if name=="DataStoreService" then serviceCalls+=1 end
 return services[name]
end}
local task={wait=function()coroutine.yield("wait") end}
local warn=function()end
local require=function(token) if token=="Config" then return config elseif token=="Lease" then return Lease else error(token) end end
local function loadActualProfiles()
'''
checks = r'''
end
local checks=0
local function check(v,msg)assert(v,msg);checks+=1 end
local function step(co)local ok,value=coroutine.resume(co);assert(ok,value);return value end
local offline=loadActualProfiles()
local temp,canSave,message=offline.Load(40)
check(serviceCalls==0 and requestedStore==nil and writes==0,"Unpublished Studio touched persistence")
check(temp.level==1 and temp.coins==0 and not canSave and message=="Saving is unavailable. This session uses temporary progress.","Offline join did not report temporary progress")
temp.coins=20
local saved,reason=offline.Save(40,temp,true)
local reloaded=offline.Load(40)
check(not saved and reason=="unavailable" and reloaded~=temp and reloaded.coins==0 and writes==0,"Offline load or save retained temporary progress")

game.GameId=101;game.PlaceId=102
local Profiles=loadActualProfiles()
local _,studioWritable=Profiles.Load(41)
check(serviceCalls==1 and requestedStore=="ScreamSimulator_Studio_v2" and studioWritable and writes==1,"Published Studio lost its existing store and lease path")

studio=false
local server=loadActualProfiles()
local _,serverWritable=server.Load(45)
check(serviceCalls==2 and requestedStore=="ScreamSimulator_v1" and serverWritable and writes==2,"Production lost its existing store and lease path")
local a,b
pauseNext=true
local first=coroutine.create(function() a={Profiles.Load(42)} end)
local second=coroutine.create(function() b={Profiles.Load(42)} end)
check(step(first)=="update","First acquisition did not reach store")
check(step(second)=="wait","Concurrent load bypassed acquisition lock")
step(first);step(second)
check(a[2]==true and b[2]==false,"Two writable profiles opened")
local loaded,saveOK
a[1].coins=42;pauseNext=true
local leaving=coroutine.create(function()saveOK=Profiles.Save(42,a[1],true)end)
local rejoin=coroutine.create(function()loaded={Profiles.Load(42)}end)
check(step(leaving)=="update","Leave save did not yield")
local staleOK
local queued=coroutine.create(function()staleOK=Profiles.Save(42,a[1])end)
check(step(queued)=="wait","Queued autosave did not wait")
check(step(rejoin)=="wait","Rejoin bypassed finishing save")
local other={Profiles.Load(43)};check(other[2]==true,"Unrelated user blocked")
step(leaving);step(rejoin)
check(saveOK and loaded[2] and loaded[1].coins==42,"Rejoin missed final save")
loaded[1].coins=99;check(Profiles.Save(42,loaded[1]),"New session could not save")
step(queued)
check(not staleOK and records.Player_42.coins==99,"Old queued save overwrote new session")
failures=3
local failed=coroutine.create(function()saveOK=Profiles.Save(42,loaded[1],true)end)
repeat step(failed) until coroutine.status(failed)=="dead"
check(not saveOK,"Injected failure unexpectedly saved")
local retry={Profiles.Load(42)}
check(retry[2] and retry[1].coins==99,"Bounded final-save recovery failed on rejoin")
check(not Profiles.Save(42,loaded[1],true),"Old profile handle admitted after recovered rejoin")
-- A different failed load must release its acquisition lock for a later attempt.
failures=3
local bad=coroutine.create(function()Profiles.Load(44)end)
repeat step(bad) until coroutine.status(bad)=="dead"
local recovered={Profiles.Load(44)};check(recovered[2],"Failed load retained lock")
print("PASS "..checks.." actual Profiles concurrency checks (mock store)")
'''
negative_control = "--negative-control" in sys.argv
if negative_control:
    guard = 'RunService:IsStudio() and game.GameId == 0 and game.PlaceId == 0'
    assert source.count(guard) == 1
    source = source.replace(guard, "false", 1)

with tempfile.NamedTemporaryFile(mode="w", suffix=".luau", prefix=".profile_race_", dir=root / "tests", delete=False) as f:
    path = Path(f.name)
    f.write(preamble + source + checks)
try:
    if negative_control:
        result = subprocess.run(["luau", str(path)], cwd=root, capture_output=True, text=True)
        assert result.returncode and "Unpublished Studio touched persistence" in result.stderr, result.stdout + result.stderr
        print("PASS negative control: bypassed guard reached the fake store")
    else:
        subprocess.run(["luau", str(path)], cwd=root, check=True)
finally:
    path.unlink()
