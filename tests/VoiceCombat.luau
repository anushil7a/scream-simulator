local Rules=require('../src/ReplicatedStorage/Shared/VoiceCombat')
local Mic=require('../src/ReplicatedStorage/Shared/MicPower')
local count=0
local function check(condition,message) assert(condition,message);count+=1 end
local last=0
for l=1,300 do
 local stats=Rules.Stats(l,1,false)
 check(stats.maxRange>last,'every level must increase range');last=stats.maxRange
 check(stats.damage<=48 and stats.range<=110 and stats.health<=205,'balance caps')
 local previous=0
 for n=0,10 do local v=Rules.Stats(l,n/10,true);check(v.range>=previous and v.range<=stats.maxRange,'loudness/amplifier caps');previous=v.range end
end
check(Rules.Stats(300,1,false).maxRange==104.75,'level 300 range')
check(Rules.Stats(1,1,false).health==100,'level 1 health')
check(Rules.Stats(300,1,false).health==205,'level 300 health')
local s=Rules.New()
check(Rules.Begin(s,0,1,true),'begin')
Rules.Cancel(s) -- roll cancels a pending attack
check(not Rules.Release(s,.5,1,1,true),'roll cannot leak release')
check(Rules.Begin(s,1,2,true),'new capture')
check(not Rules.Release(s,1.3,2,1,false),'protected/rolling release rejected')
check(Rules.Begin(s,2,3,true),'new sequence')
check(Rules.Release(s,2.4,3,.8,true),'valid shot')
check(not Rules.Release(s,2.5,3,.8,true),'duplicate release')
check(not Rules.Begin(s,3,4,true),'cooldown begin')
check(not Rules.Begin(s,7,4,true),'replayed sequence')
check(Rules.Begin(s,7,5,true),'ready begin')
check(not Rules.Release(s,7.3,5,math.huge,true),'non-finite power')
check(Rules.Begin(s,8,6,true),'begin for excess power')
check(not Rules.Release(s,8.3,6,2,true),'excess power')
check(Rules.Begin(s,9,7,true),'begin silence')
check(not Rules.Release(s,9.3,7,0,true),'silence')
check(Rules.Begin(s,10,8,true),'begin expiry')
check(not Rules.Release(s,19,8,1,true),'stale capture')
local mic=Mic.new();local quiet={};local voice={}
for i=1,60 do quiet[i]=.003;voice[i]=.06 end
check(mic:Calibrate(quiet,voice),'calibration')
mic:BeginCapture()
for i=1,30 do mic:Capture(mic:Step(i==15 and 1 or .003,1/60)) end
check(mic:Release()==0,'isolated noise spike rejected')
mic:Reset();mic:BeginCapture()
for i=1,60 do mic:Capture(mic:Step(.06,1/60)) end
check(mic:Release()>.9,'sustained voice accepted')
check(mic:Release()==0,'samples consumed once')
for i=1,60 do mic:Step(.06,1/60) end
check(mic.smoothed>.9,'pre-capture live meter can be high')
mic:BeginCapture()
for i=1,20 do mic:Capture(mic:Step(.003,1/60)) end
check(mic:Release()==0,'speech before the button cannot leak into a silent attack')
mic:BeginCapture()
for i=1,30 do mic:Capture(mic:Step(.06,1/60)) end
check(mic:Release()>.8,'fresh speech after reset still fires')
check(not Mic.new():Calibrate(quiet,quiet),'no voice calibration rejected')
for _=1,6 do mic:Capture(.8) end
check(not mic:Calibrate(quiet,quiet),'failed recalibration rejected')
check(not mic.calibrated,'failed recalibration must invalidate previous success')
check(#mic.samples==0 and mic.smoothed==0,'failed recalibration clears stale capture')
check(mic:Calibrate(quiet,voice) and mic.calibrated,'successful retry restores calibration')
print('PASS '..count..' microphone/combat rule checks')
local Destruction=require('../src/ReplicatedStorage/Shared/DestructionRules')
for _,level in ipairs({1,25,26,50,51,75,76,99,100,101,300}) do
 for kind,spec in pairs(Destruction.Types) do
  local hp,_,reason=Destruction.Hit(kind,level,spec.health,18)
  check((level>=spec.level and hp==spec.health-18 and reason==nil) or (level<spec.level and hp==spec.health and reason=='level'),'destruction unlock boundary')
 end
end
local _,_,invalid=Destruction.Hit('Bench',300,50,100000)
check(invalid=='damage','destruction damage cap')
print('PASS '..count..' total combat/microphone/destruction rule checks')
