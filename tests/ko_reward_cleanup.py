"""Actual KO eligibility/cleanup helper with synthetic clock and session entries."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
s=s[s.index('local function claimKoReward('):s.index('local function questProgress(')]
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
local s={koRewards={[1]=100,[2]=101,[3]=200}}
check(not claimKoReward(s,2,100),'Unexpired opponent paid')
check(s.koRewards[1]==nil and s.koRewards[2]==101 and s.koRewards[3]==200,'Cleanup removed live cooldown or retained expired one')
check(s.nextKoRewardCleanup==130,'Cleanup interval not set')
check(claimKoReward(s,2,101) and s.koRewards[2]==131,'Exact reward deadline rejected')
s.koRewards[4]=102;claimKoReward(s,5,110)
check(s.koRewards[4]==102,'Cleanup scanned before scheduled boundary')
check(not claimKoReward(s,5,130) and s.koRewards[5]==140,'Cleanup bypassed or extended repeat cooldown')
check(s.koRewards[4]==nil and s.koRewards[2]==131 and s.koRewards[3]==200,'Scheduled cleanup failed or removed unexpired entry')
for i=10,1009 do s.koRewards[i]=150 end
check(claimKoReward(s,6,160),'New opponent rejected during cleanup')
local count=0;for _ in pairs(s.koRewards)do count+=1 end
check(count==2 and s.koRewards[3]==200 and s.koRewards[6]==190,'Expired historical opponents retained')
print('PASS '..checks..' actual KO reward cleanup checks with synthetic time; no memory benchmark')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(s+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
