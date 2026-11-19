-- Appended only to a guarded local 0/0 build. Uses two real local Players and
-- one synchronous synthetic power tick through the actual server beam resolver.
do
 assert(RunService:IsStudio() and game.PlaceId==0 and game.GameId==0 and localFixture and sustainedEnabled,"Unpublished automatic-voice QA only")
 local invoke=Instance.new("BindableFunction");invoke.Name="CentralPvpReview";invoke.Parent=game:GetService("ServerStorage")
 local running=false
 invoke.OnInvoke=function()
  assert(not running,"Central PvP check already running")
  local list=Players:GetPlayers();assert(#list==2,"Two local Players required")
  local a,b=list[1],list[2];local sa,sb=assert(sessions[a]),assert(sessions[b])
  local ac,ar,ah=parts(a);local bc,br,bh=parts(b)
  assert(ac and bc and not sa.canSave and not sb.canSave and not sa.flight and not sb.flight,"Two living temporary players required")
  running=true
  local saved={}
  for _,p in ipairs(list) do
   local s=sessions[p];local c,r,h=parts(p)
   saved[p]={frame=c:GetPivot(),anchor=r.Anchored,health=h.Health,max=h.MaxHealth,data=s.data,
    mic=s.micReady,protection=s.protectedUntil,dodge=s.dodgingUntil,knock=s.knockedUntil,heal=s.nextHeal,
    credit=s.credit,movement=s.premiumRoll}
   cancelSustained(p,s,os.clock())
   s.data=Profiles.Default();s.micReady=true;s.protectedUntil=0;s.dodgingUntil=0;s.knockedUntil=0;s.credit={}
   s.nextHeal=os.clock()+60;s.premiumRoll=false;r.Anchored=true;h.MaxHealth=100;h.Health=100
  end
  local function V(x,y,z)return Vector3.new(x,y,z)end
  local cases={
   {"north-garden",V(40,19,79),V(40,19,87),true,true,true},
   {"south-garden",V(45,19,136),V(45,19,144),true,true,true},
   {"garden-to-safe-path",V(40,19,90),V(40,19,100),true,false,false},
   {"safe-path-to-garden",V(40,19,100),V(40,19,90),false,true,false},
   {"safe-path-both",V(40,19,103),V(40,19,111),false,false,false},
   {"upper-level",V(40,35,79),V(40,35,87),false,false,false},
   {"below-terrace",V(40,8,79),V(40,8,87),false,false,false},
   {"west-old-stadium",V(-330,3,116),V(-330,3,124),true,true,true},
  }
  local passed=0
  local ok,why=xpcall(function()
   for _,case in ipairs(cases) do
    local name,from,to,attackerIn,targetIn,canHit=table.unpack(case)
    ac:PivotTo(CFrame.lookAt(from,to));bc:PivotTo(CFrame.lookAt(to,from))
    local prior=100;bh.Health=prior;sb.credit={};sa.sustained=sustained.New()
    assert(Config.InArena(ar.Position)==attackerIn and Config.InArena(br.Position)==targetIn,"Zone mismatch for "..name)
    local now=os.clock()
    assert(sustained.Begin(sa.sustained,now,{sequence=1,power=1,aim=br.Position},sustainedContext(a,sa,now)),"Start rejected for "..name)
    stepSustained(a,sa,now+.2)
    local removed=prior-bh.Health
    assert(removed==(canHit and 3 or 0),name.." removed "..removed.." instead of "..(canHit and 3 or 0))
    cancelSustained(a,sa,now+.2)
    passed+=1;print("CENTRAL_PVP_CASE",name,attackerIn,targetIn,removed)
   end
  end,debug.traceback)
  for _,p in ipairs(list) do
   local s=sessions[p];local c,r,h=parts(p);local v=saved[p]
   cancelSustained(p,s,os.clock());clearDamageSummary(p,s)
   s.sustained=sustained.New();s.data=v.data;s.micReady=v.mic;s.protectedUntil=v.protection;s.dodgingUntil=v.dodge;s.knockedUntil=v.knock
   s.nextHeal=v.heal;s.credit=v.credit;s.premiumRoll=v.movement
   c:PivotTo(v.frame);r.Anchored=v.anchor;h.MaxHealth=v.max;h.Health=v.health
  end
  running=false
  print("CENTRAL_PVP_DONE",ok,passed,why or "two local clients; synthetic power, not live voice")
  return ok,passed,why
 end
 print("CENTRAL_PVP_READY; guarded ServerStorage.CentralPvpReview")
end
