-- Pure rules for this disposable Studio fixture. Never used by live profiles.
local Rules={MaxHold=4,Cooldown=5,InputExpiry=.65,Tick=.1,TrainSeconds=1,Reward=100,MaxBeamPercent=100}
Rules.Locations={AcademyTrainTarget={-304,25,240},AcademyMentor={-294,20,248},
 AcademyMetronomeEntry={-228,20,248},AcademyGear={-322,20,248}}
function Rules.New()
 return {stage="Train",coins=0,level=1,gearOwned={},trained=0,rewarded=false,held=false,
  released=true,nextCast=0,lastInput=-math.huge,lastPacket=-math.huge,started=0}
end
function Rules.Finite(n) return type(n)=="number" and n==n and math.abs(n)<math.huge end
-- Explicit test percentage cannot exceed the shared combat power cap.
function Rules.BeamPower(percent)
 if not Rules.Finite(percent) or percent<0 or percent>Rules.MaxBeamPercent then return nil end
 return math.clamp(percent/100,0,1)
end
function Rules.Dps(stats) return stats.power>0 and stats.maxDps*(.45+.55*stats.power) or 0 end
function Rules.Direction(x,y,z)
 if not Rules.Finite(x) or not Rules.Finite(y) or not Rules.Finite(z) then return false end
 local length=x*x+y*y+z*z
 return length>=.98 and length<=1.02
end
function Rules.Stop(s,now)
 if s.held then s.held=false;s.nextCast=now+Rules.Cooldown end
end
function Rules.Input(s,held,now)
 if type(held)~="boolean" or not Rules.Finite(now) then return false end
 -- Releases cannot be starved by the update rate limiter.
 if not held then Rules.Stop(s,now);s.released=true;return true end
 if now-s.lastPacket<.045 then return false end
 s.lastPacket=now
 if not s.held then
  if not s.released or now<s.nextCast then return false end
  s.held=true;s.released=false;s.started=now
 end
 s.lastInput=now;return true
end
function Rules.Active(s,now)
 if s.held and (now-s.started>=Rules.MaxHold or now-s.lastInput>Rules.InputExpiry) then Rules.Stop(s,now) end
 return s.held
end
function Rules.Train(s,dt)
 if s.stage~="Train" then return false end
 s.trained+=math.clamp(dt,0,Rules.Tick)
 if s.trained>=Rules.TrainSeconds then s.stage="Meet";return true end
 return false
end
function Rules.Accept(s)
 if s.stage~="Meet" then return false end
 s.level=10;s.stage="Guide";return true
end
function Rules.Enter(s,inRing)
 if s.stage=="Guide" and inRing then s.stage="Fight";return true end
 return false
end
function Rules.RewardOnce(s,bossCoins)
 if s.stage~="Fight" or s.rewarded then return false end
 s.rewarded=true;s.coins+=math.max(Rules.Reward,bossCoins);s.stage="Gear";return true
end
return Rules
