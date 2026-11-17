-- Actual standalone route rules and unchanged shared gear/combat helpers; no Studio simulation.
local Rules=require("./AcademyRouteRules")
local Gear=require("../../src/ReplicatedStorage/Shared/GearCatalog")
local Voice=require("../../src/ReplicatedStorage/Shared/VoiceCombat")
local checks=0
local function check(value,message) assert(value,message);checks+=1 end

local p=Rules.New()
check(p.stage=="Train" and p.coins==0 and p.level==1,"fresh isolated state")
check(not Rules.Accept(p) and not Rules.Enter(p,true) and not Rules.RewardOnce(p,35),"cannot skip training")
check(Rules.Direction(0,0,-1),"valid direction")
for _,v in ipairs({{0,0,0},{1e8,0,0},{math.huge,0,0},{0/0,0,0},{"1",0,0}}) do
 check(not Rules.Direction(table.unpack(v)),"invalid direction rejected")
end
check(Rules.Input(p,true,1),"start")
check(not Rules.Input(p,true,1.001),"rate cap")
check(Rules.Active(p,1+Rules.InputExpiry-.05),"fresh hold")
check(not Rules.Active(p,1+Rules.InputExpiry+.05),"stale hold expires")
local expiry=p.nextCast
check(not Rules.Input(p,true,expiry+1),"must release after stale hold")
check(Rules.Input(p,false,expiry+1.01),"release not rate-capped")
check(Rules.Input(p,true,expiry+1.08),"rearm on release")
local cast=p.started
for i=1,39 do
 local t=cast+i/10
 check(Rules.Input(p,true,t),"held update")
 check(Rules.Active(p,t),"remains active below four seconds")
end
check(not Rules.Active(p,cast+4.01),"maximum hold enforced")
check(Rules.Input(p,false,cast+4.02),"release")
check(not Rules.Input(p,true,p.nextCast-.10),"cooldown enforced")
check(Rules.Input(p,true,p.nextCast+.01),"cooldown expires")
for _=1,12 do Rules.Train(p,Rules.Tick) end
check(p.stage=="Meet" and not Rules.Train(p,Rules.Tick),"training only once")
check(Rules.Accept(p) and p.stage=="Guide" and p.level==10,"preview level lift on acceptance")
check(not Rules.Accept(p) and not Rules.Enter(p,false),"can't skip ring")
check(Rules.Enter(p,true) and p.stage=="Fight","enter fixed ring")
check(not Rules.RewardOnce(Rules.New(),35),"fresh player not rewarded")
check(Rules.RewardOnce(p,35) and p.stage=="Gear" and p.coins==100,"one 100-coin session grant")
check(not Rules.RewardOnce(p,35),"no duplicate boss reward")
local item=Gear.Get("Megaphone")
check(item.price==100 and item.level==1,"real starter catalog")
check(Gear.Act(p,item.id,false) and Gear.Selected(p)==item and p.coins==0,"earned gear equipped")
check(not Gear.Act(p,item.id,false) and p.coins==0,"repeat buy never debits")
local stats=Voice.Stats(p.level,1,false,false,Gear.Multiplier(p))
check(stats.range==32.25 and stats.power==1 and stats.maxDps>15,"actual level-10 beam stats; max power stays capped")
for _,v in ipairs({-1,101,math.huge,0/0,"100",true,{}}) do
 check(Rules.BeamPower(v)==nil,"invalid percent rejected")
end
check(Rules.BeamPower(0)==0 and Rules.BeamPower(50)==.5,"normalized power")
check(Rules.BeamPower(100)==1 and Rules.BeamPower(101)==nil,"100 cap")
local lastRange,lastDps=0,0
for _,percent in ipairs({0,10,50,100}) do
 local st=Voice.Stats(10,Rules.BeamPower(percent),false,false,1)
 local dps=Rules.Dps(st)
 check(dps>=lastDps and st.range>=lastRange,"monotonic actual stats")
 check(percent==0 and dps==0 or percent>0 and dps==st.maxDps*(.45+.55*st.power),"actual sustained power curve")
 lastRange=st.range;lastDps=dps
end
local a=Rules.New()
check(a.stage=="Train" and a.coins==0 and not Gear.Owned(a,item.id),"second session independent")
print("PASS "..checks.." Academy stage/gear/hold assertions (actual Luau modules)")
