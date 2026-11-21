-- Appended only to a guarded local 0/0 build. Uses two real local Players and
-- one synchronous synthetic power tick through the actual server beam resolver.
do
 assert(RunService:IsStudio() and game.PlaceId==0 and game.GameId==0 and localFixture and sustainedEnabled,"Unpublished automatic-voice QA only")
 local invoke=Instance.new("BindableFunction");invoke.Name="CentralPvpReview";invoke.Parent=game:GetService("ServerStorage")
 local running=false
 invoke.OnInvoke=function(mode)
  assert(mode==nil or mode=="target-crossing" or mode=="attacker-crossing","Unrecognized local scenario")
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
    credit=s.credit,movement=s.premiumRoll,beamCue=s.nextBeamCueAt}
   cancelSustained(p,s,os.clock())
   s.data=Profiles.Default();s.micReady=true;s.protectedUntil=0;s.dodgingUntil=0;s.knockedUntil=0;s.credit={}
   s.nextHeal=os.clock()+60;s.premiumRoll=false;s.nextBeamCueAt=nil;r.Anchored=true;h.MaxHealth=100;h.Health=100
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
   if mode then
    local other=V(40,19,79);local edge=V(40,19,87);local path=V(40,19,103)
    local mover,root,opponent
    if mode=="target-crossing" then
     ac:PivotTo(CFrame.lookAt(other,edge));bc:PivotTo(CFrame.lookAt(edge,other))
     mover,root,opponent=bc,br,ar
    else
     ac:PivotTo(CFrame.lookAt(edge,other));bc:PivotTo(CFrame.lookAt(other,edge))
     mover,root,opponent=ac,ar,br
    end
    task.wait(.15)
    assert(root.Parent==mover and Config.InArena(ar.Position) and Config.InArena(br.Position),"Crossing start must be in Garden PvP")
    local live=sustained.New();local idle=sustained.New()
    sa.sustained=live
    local began=os.clock();local sample=0
    assert(sustained.Begin(sa.sustained,began,{sequence=1,power=1,aim=br.Position},sustainedContext(a,sa,began)),"Crossing cast rejected")
    local cast=sa.sustained.protocol.active
    local function tick()
     sample+=1;local now=began+sample*.21
     sa.sustained=live;sa.micReady=true
     assert(live.protocol.active==cast,"Crossing must keep the same cast")
     assert(sustained.Pulse(live,now,{sequence=1,sample=sample,power=1,aim=br.Position},sustainedContext(a,sa,now)),"Crossing pulse rejected")
     stepSustained(a,sa,now)
     -- The ordinary Heartbeat sees an idle resolver only while this fixture yields.
     -- No changes are made to the production resolver or network rules.
     sa.sustained=idle
    end
    tick()
    assert(bh.Health<100,"Initial damage")
    print("CENTRAL_PVP_CROSS",mode,"initial",bh.Health,workspace:GetServerTimeNow())
    task.wait(.25)
    mover:PivotTo(CFrame.lookAt(path,opponent.Position))
    local safeHealth=bh.Health
    for _=1,8 do
     tick()
     assert(bh.Health==safeHealth and not Config.InArena(root.Position),"Damage on safe paving")
     task.wait(.21)
    end
    print("CENTRAL_PVP_CROSS",mode,"safe",safeHealth,workspace:GetServerTimeNow())
    mover:PivotTo(CFrame.lookAt(edge,opponent.Position))
    tick()
    assert(bh.Health<safeHealth,"Damage did not resume")
    assert(Config.InArena(ar.Position) and Config.InArena(br.Position),"Returned damage outside Garden PvP")
    print("CENTRAL_PVP_CROSS",mode,"returned",bh.Health,workspace:GetServerTimeNow(),sample)
    task.wait(.3)
    sa.sustained=live
    cancelSustained(a,sa,began+sample*.21)
    passed=3
    return
   end
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
   s.nextHeal=v.heal;s.credit=v.credit;s.premiumRoll=v.movement;s.nextBeamCueAt=v.beamCue
   c:PivotTo(v.frame);r.Anchored=v.anchor;h.MaxHealth=v.max;h.Health=v.health
  end
  running=false
  print("CENTRAL_PVP_DONE",ok,passed,why or "two local clients; synthetic power, not live voice")
  return ok,passed,why
 end
 print("CENTRAL_PVP_READY; guarded ServerStorage.CentralPvpReview")
end
