local G=require('../src/ReplicatedStorage/Shared/GearCatalog')
local V=require('../src/ReplicatedStorage/Shared/VoiceCombat')
local P=require('../src/ReplicatedStorage/Shared/Progression')
local T=require('../src/ReplicatedStorage/Shared/TrainingRules')
local function fresh(level,coins) return {level=level,coins=coins,gearOwned={}} end
local checks=0
local function check(v) checks+=1;assert(v,'gear check '..checks) end
for _,item in ipairs(G.Items) do
 local d=fresh(item.level,item.price)
 local ok=G.Act(d,item.id,false);check(ok and d.coins==0 and G.Owned(d,item.id))
 check(G.Selected(d).id==item.id)
 check(not G.Act(d,item.id,false) and d.coins==0)
 check(G.Act(d,item.id,true) and not G.Selected(d))
 check(G.Act(d,item.id,true) and G.Selected(d).id==item.id and d.coins==0)
 local copy=fresh(d.level,d.coins);copy.megaphoneOwned=d.megaphoneOwned;copy.amplifierOwned=d.amplifierOwned
 G.Sanitize(copy,d);check(G.Selected(copy).id==item.id)
 local poor=fresh(item.level,item.price-1);check(not G.Act(poor,item.id,false) and poor.coins==item.price-1 and not G.Owned(poor,item.id))
 if item.level>1 then local low=fresh(item.level-1,1e6);check(not G.Act(low,item.id,false) and low.coins==1e6) end
 for _,power in ipairs({0,.08,.4,.65,.8,1}) do
  local stats=V.Stats(item.level,power,true,true,G.Multiplier(d))
  check(stats.power<=1 and math.abs(stats.power-math.min(1,power*(1+item.bonus)))<1e-8)
  check(stats.maxDps==V.Stats(item.level,power,false).maxDps)
 end
end
local legacy={level=100,coins=12345,amplifierOwned=true,amplifierEquipped=true,megaphoneOwned=true,megaphoneEquipped=true}
G.Sanitize(legacy,legacy);check(G.Multiplier(legacy)==1.12 and legacy.coins==12345 and legacy.megaphoneOwned)
check(G.Act(legacy,'CelestialOrgan',false));check(not legacy.amplifierEquipped and not legacy.megaphoneEquipped)
check(legacy.amplifierOwned and legacy.megaphoneOwned)
local before=legacy.coins;check(not G.Act(legacy,'bad',false) and legacy.coins==before)
local corrupt=fresh(1,22);G.Sanitize(corrupt,{gearOwned={SonicCannon=true,evil=true},gearEquipped='SonicCannon'})
check(corrupt.gearOwned.SonicCannon and not corrupt.gearOwned.evil and G.Selected(corrupt)==nil)
-- Save rollback uses old confirmed snapshot, not a compensating refund or free ownership.
local confirmed=fresh(100,99999);local live=fresh(100,confirmed.coins)
check(G.Act(live,'MosaicMic',false));check(not G.Owned(confirmed,'MosaicMic') and confirmed.coins==99999)
G.Sanitize(live,confirmed);live.coins=confirmed.coins;check(not G.Owned(live,'MosaicMic') and live.coins==99999)
-- Deterministic solo KO-only economy; no quests/boosts. Actual trainer XP and 5 coin KO.
local level,xp,bank,seconds,kills=1,0,0,0,0
local bought={};local objectives={}
while not bought.CelestialOrgan do
 local tier=T.Recommended(level)
 local damage=V.Stats(level,1,false).maxDps*(.45+.55*.8)*4*.75
 seconds+=math.ceil(tier.health/damage)*9+8;kills+=1;bank+=5
 local reward=tier.xp+P.Advance(objectives,'fighters',level)
 level,xp=P.Normalize(level,xp+reward)
 for _,item in ipairs(G.Items) do
  if not bought[item.id] and level>=item.level and bank>=item.price then
   bank-=item.price;bought[item.id]=true
   print(string.format('GEAR PACING %s level=%d %.1fmin KOs=%d',item.id,level,seconds/60,kills))
  end
 end
 check(kills<10000)
end
print('GearProgression checks',checks)
-- Real adapter freezes server-selected bonus at begin; ignores forged remote bonus.
local A=require('../src/ReplicatedStorage/Shared/SustainedAttack')
local Adapter=require('../src/ServerScriptService/SustainedAttackAdapter')
local api=Adapter.new(A,V,function()return 1 end)
local c={character={},origin=0,level=90,gearMultiplier=1.32,amplifier=true,megaphone=true}
local s=api.New()
check(api.Begin(s,0,{sequence=1,aim=10,power=.55,gearMultiplier=100},c))
check(math.abs(s.protocol.active.power-.726)<1e-8)
c.gearMultiplier=1
check(api.Pulse(s,.1,{sequence=1,sample=1,aim=10,power=.55,gearMultiplier=100},c))
check(math.abs(s.protocol.active.power-.726)<1e-8)
api.Step(s,.2,c,function(_,_,stats)check(math.abs(stats.power-.726)<1e-8);return {},{},nil end)
print('PASS server bonus snapshot / forged bonus / no double amplification')
