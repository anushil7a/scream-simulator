-- Appended only to the guarded Resonance combat build. Uses real Studio players.
do
 assert(localFixture and sustainedEnabled and RunService:IsStudio() and game.PlaceId==0 and game.GameId==0)
 local fixture=Instance.new("BindableFunction")
 fixture.Name="ResonanceCombatReview"
 fixture.Parent=game:GetService("ServerStorage")
 local function at(x,z) return Vector3.new(x,3.8,z) end
 fixture.OnInvoke=function()
  local list=Players:GetPlayers()
  assert(#list==2,"Start a local Server & Clients test with two players")
  local a,b=list[1],list[2]
  local sa,sb=assert(sessions[a]),assert(sessions[b])
  local ac,ar,ah=parts(a)
  local bc,br,bh=parts(b)
  assert(ac and bc and not sa.canSave and not sb.canSave,"Two living temporary profiles required")
  assert(not sa.testBaseline and not sb.testBaseline and not sa.flight and not sb.flight,"Restart with standard local profiles")
  assert(#World.Bots==0 and not workspace.ScreamSimulatorWorld:FindFirstChild("BeachVolley"))
  assert(Config.InArena(at(69,55)) and not Config.InArena(at(0,55)) and not Config.InArena(at(0,240)))
  local before={}
  for _,p in ipairs(list) do
   local s=sessions[p]
   local c,r,h=parts(p)
   before[p]={frame=c:GetPivot(),anchored=r.Anchored,health=h.Health,max=h.MaxHealth,data=s.data,
    mic=s.micReady,protection=s.protectedUntil,dodge=s.dodgingUntil,heal=s.nextHeal,credit=s.credit,knock=s.knockedUntil}
   cancelSustained(p,s,os.clock())
   s.data=Profiles.Default();s.micReady=true;s.protectedUntil=0;s.dodgingUntil=0;s.knockedUntil=0
   s.nextHeal=os.clock()+60;s.credit={};r.Anchored=true;h.MaxHealth=100;h.Health=100
  end
  local cases={
   {"open flank",at(-18,-12),at(-18,12),3},
   {"mixing desk",at(0,-11),at(0,11),0},
   {"speaker cover",at(-53,-32),at(-53,-51),0},
   {"portal protects defender",at(0,44),at(0,55),0},
   {"portal protects from outgoing cast",at(0,55),at(0,44),0},
   {"dodge",at(18,-12),at(18,12),0,"dodge"},
   {"spawn protection",at(18,-12),at(18,12),0,"protected"},
   {"knockout to safe apron",at(18,-12),at(18,12),2,"ko"},
  }
  local results={}
  local ok,err=xpcall(function()
   for _,case in ipairs(cases) do
    local name,from,to,damage,mode=table.unpack(case)
    ac:PivotTo(CFrame.lookAt(from,to));bc:PivotTo(CFrame.lookAt(to,from))
    local now=os.clock()
    local initial=mode=="ko" and 2 or 100
    bh.Health=initial;sb.credit={};sb.nextBeamCueAt=nil
    sb.dodgingUntil=mode=="dodge" and now+1 or 0
    sb.protectedUntil=mode=="protected" and now+1 or 0
    sa.sustained=sustained.New()
    assert(sustained.Begin(sa.sustained,now,{sequence=1,power=1,aim=to},sustainedContext(a,sa,now)),"Cast rejected in "..name)
    stepSustained(a,sa,now+.2)
    if mode=="ko" then
     assert(not Config.InArena(br.Position) and (br.Position-World.SafeSpawn.Position).Magnitude<.5 and sb.protectedUntil>now,"KO missed the safe apron")
    else
     assert(initial-bh.Health==damage,name.." expected "..damage.." damage, received "..(initial-bh.Health))
    end
    cancelSustained(a,sa,now+.2)
    results[#results+1]=name
   end
  end,debug.traceback)
  for _,p in ipairs(list) do
   local s,c,r,h=sessions[p],parts(p)
   local saved=before[p]
   c:PivotTo(saved.frame);r.Anchored=saved.anchored;h.MaxHealth=saved.max;h.Health=saved.health
   s.data=saved.data;s.micReady=saved.mic;s.protectedUntil=saved.protection;s.dodgingUntil=saved.dodge
   s.nextHeal=saved.heal;s.credit=saved.credit;s.knockedUntil=saved.knock
   cancelSustained(p,s,os.clock());s.sustained=sustained.New();state(p)
  end
  assert(ok,err)
  return {passed=#results,cases=results}
 end
end
