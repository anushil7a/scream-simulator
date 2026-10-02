"""Run actual Profiles source with a deterministic yielding store, never Roblox data."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / "src/ServerScriptService/Profiles.luau").read_text()
preamble = r'''
local Lease=require("../src/ReplicatedStorage/Shared/ProfileLease")
local records={};local pauseNext=false;local failures=0
local store={}
function store:UpdateAsync(key,transform)
 if pauseNext then pauseNext=false;coroutine.yield("update") end
 if failures>0 then failures-=1;error("Injected store failure") end
 local result=transform(records[key]);if result~=nil then records[key]=result end;return result
end
local config={Progression={Normalize=function(l,x)return l or 1,x or 0 end},Quests={},Auras={Gold=true},GetSound=function()return {id="TinyAah",level=1} end}
local services={DataStoreService={GetDataStore=function()return store end},ReplicatedStorage={Shared={Config="Config",ProfileLease="Lease"}},RunService={IsStudio=function()return true end},HttpService={GenerateGUID=function()return "test-owner" end}}
local game={JobId="test-job",GetService=function(_,name)return services[name] end}
local task={wait=function()coroutine.yield("wait") end}
local warn=function()end
local require=function(token) if token=="Config" then return config elseif token=="Lease" then return Lease else error(token) end end
local function loadActualProfiles()
'''
checks = r'''
end
local Profiles=loadActualProfiles();local checks=0
local function check(v,msg)assert(v,msg);checks+=1 end
local function step(co)local ok,value=coroutine.resume(co);assert(ok,value);return value end
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
check(not retry[2] and records.Player_42.coins==99,"Failed leave admitted second writer")
-- A different failed load must release its acquisition lock for a later attempt.
failures=3
local bad=coroutine.create(function()Profiles.Load(44)end)
repeat step(bad) until coroutine.status(bad)=="dead"
local recovered={Profiles.Load(44)};check(recovered[2],"Failed load retained lock")
print("PASS "..checks.." actual Profiles concurrency checks (mock store)")
'''
with tempfile.NamedTemporaryFile(mode="w", suffix=".luau", prefix=".profile_race_", dir=root / "tests", delete=False) as f:
    path = Path(f.name)
    f.write(preamble + source + checks)
try:
    subprocess.run(["luau", str(path)], cwd=root, check=True)
finally:
    path.unlink()
