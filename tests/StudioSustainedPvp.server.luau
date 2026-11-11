-- Append to Bootstrap only in a disposable PlaceId=0 Studio test.
-- Start Server & Clients with two players, then run
-- game.ServerStorage.RunSustainedPvp:Invoke()
-- in the SERVER command bar. Uses real avatars and synthetic voice input.
assert(sustainedEnabled and RunService:IsStudio() and game.PlaceId==0)
_G.RunSustainedPvp=function(negativeControl)
 assert(sustainedEnabled and game.PlaceId==0)
 assert(negativeControl==nil or negativeControl=="repeat-limit-disabled","Unknown negative control")
 local ps=Players:GetPlayers();assert(#ps>=2,"Need two local players")
 local p,t=ps[1],ps[2];local s,ts=assert(sessions[p]),assert(sessions[t]);assert(not s.canSave and not ts.canSave)
 local c,r,h=parts(p);local tc,tr,th=parts(t);assert(c and tc)
 local saved={}
 for _,q in ipairs({p,t}) do
  local ss=sessions[q];local cc,rr,hh=parts(q)
  saved[q]={data=ss.data,frame=cc:GetPivot(),anchor=rr.Anchored,health=hh.Health,max=hh.MaxHealth,
   mic=ss.micReady,protection=ss.protectedUntil,dodge=ss.dodgingUntil,knock=ss.knockedUntil,credit=ss.credit}
  ss.data=Profiles.Default();ss.micReady=true;ss.protectedUntil=0;ss.dodgingUntil=0;ss.knockedUntil=0;ss.credit={};rr.Anchored=true
 end
 local oldHistory=rewardHistory;rewardHistory={pairs={}}
 -- Mutate the same module table used by Bootstrap, not a Command Bar require
 -- whose execution context may have a different module cache.
 local oldRepeat=Credit.RepeatFactor;local repeatCalls=0
 if negativeControl then Credit.RepeatFactor=function() repeatCalls+=1;return 1 end end
 local n=0;local function check(v,msg) assert(v,msg);n+=1 end
 local ok,err=xpcall(function()
  c:PivotTo(CFrame.new(0,190,0));tc:PivotTo(CFrame.new(0,190,-12));th.Health=th.MaxHealth
  local function hit()
   s.sustained=sustained.New();local now=os.clock()
   check(sustained.Begin(s.sustained,now,{sequence=1,power=1,aim=tr.Position},sustainedContext(p,s,now)),"Begin rejected")
   stepSustained(p,s,now+.2);return now
  end
  local health=th.Health;ts.protectedUntil=os.clock()+5;hit();check(th.Health==health,"Protected target damaged")
  ts.protectedUntil=0;ts.dodgingUntil=os.clock()+5;hit();check(th.Health==health,"Rolling target damaged")
  ts.dodgingUntil=0;hit();check(th.Health==health-3,"Arena player not damaged")
  c:PivotTo(CFrame.new(0,210,0));tc:PivotTo(CFrame.new(0,210,-12));health=th.Health;hit();check(th.Health==health,"Safe area PvP damage")
  c:PivotTo(CFrame.new(0,190,0));tc:PivotTo(CFrame.new(0,190,-12));th.Health=1
  -- Seed the preceding actual-damage credit for this synthetic almost-KO.
  ts.credit={};recordCredit(ts.credit,p,th.MaxHealth-1,th.MaxHealth,os.clock())
  local coins=s.data.coins;local x=s.data.xp;hit()
  check(not Config.InArena(tr.Position) and th.Health>1,"KO did not eject/heal")
  check(ts.protectedUntil>os.clock() and s.data.coins==coins+20 and (s.data.level>1 or s.data.xp>x),"KO protection/reward failed")
  tc:PivotTo(CFrame.new(0,190,-12));ts.protectedUntil=0;th.Health=1
  -- A full eligible life of credit is required: one finishing damage point alone
  -- rounds XP to zero even if repeat-opponent suppression is completely broken.
  ts.credit={};recordCredit(ts.credit,p,th.MaxHealth-1,th.MaxHealth,os.clock())
  coins=s.data.coins;x=s.data.xp;local level=s.data.level;hit()
  check(not Config.InArena(tr.Position) and th.Health>1,"Repeat KO did not land")
  check(s.data.coins==coins and s.data.xp==x and s.data.level==level,"Repeat KO reward farm")
 end,debug.traceback)
 Credit.RepeatFactor=oldRepeat
 for _,q in ipairs({p,t}) do
  local ss=sessions[q];local v=saved[q];local cc,rr,hh=parts(q)
  ss.data=v.data;ss.micReady=v.mic;ss.protectedUntil=v.protection;ss.dodgingUntil=v.dodge;ss.knockedUntil=v.knock;ss.credit=v.credit
  ss.sustained=sustained.New();cc:PivotTo(v.frame);rr.Anchored=v.anchor;hh.MaxHealth=v.max;hh.Health=v.health
  q:SetAttribute("SustainedActive",false);q:SetAttribute("SustainedReadyAt",0)
 end
 rewardHistory=oldHistory
 print("NATIVE_PVP_RESULT",ok,n,err or "two local players; synthetic voice",negativeControl or "baseline","repeatCalls",repeatCalls)
 return ok,n,err
end
-- Command Bar globals may differ from the running script environment. Expose
-- an explicit server-only entry point in this disposable fixture instead.
local runner=Instance.new("BindableFunction")
runner.Name="RunSustainedPvp"
local running=false
runner.OnInvoke=function(negativeControl)
 assert(not running,"PvP fixture is already running")
 running=true
 local result=table.pack(pcall(_G.RunSustainedPvp,negativeControl))
 running=false
 if not result[1] then error(result[2]) end
 return table.unpack(result,2,result.n)
end
runner.Parent=game:GetService("ServerStorage")
print("NATIVE_PVP_READY", "game.ServerStorage.RunSustainedPvp:Invoke()")
