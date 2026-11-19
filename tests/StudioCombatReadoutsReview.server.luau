-- Studio-only instrumentation appended to Bootstrap by build_sustained_review.py.
do
 assert(RunService:IsStudio() and game.PlaceId==0 and game.GameId==0 and localFixture,"Combat HUD evidence is local only")
 local storage=game:GetService("ServerStorage")
 local invoke=Instance.new("BindableFunction");invoke.Name="CombatReadoutsReview";invoke.Parent=storage
 local function participants()
  local ps=Players:GetPlayers();table.sort(ps,function(a,b)return a.UserId<b.UserId end)
  for _,p in ipairs(ps) do assert(sessions[p] and not sessions[p].canSave,"Temporary players required") end
  return ps
 end
 invoke.OnInvoke=function(mode)
  local ps=participants()
  local p=assert(ps[1]);local s=sessions[p];local c,r,h=parts(p)
  assert(c and r and h and h.Health>0 and not s.flight,"Living, grounded player required")
  if mode=="pair" then
   assert(#ps==2,"Start Studio Server & Clients 2")
   local _,other,oh=parts(ps[2]);assert(other and oh,"Second real Player must be loaded")
   local where=r.Position;local point=where+Vector3.new(0,0,-9)
   c:PivotTo(CFrame.lookAt(where,point))
   ps[2].Character:PivotTo(CFrame.lookAt(point,where))
   for i,player in ipairs(ps) do sessions[player].nextHeal=os.clock()+80 end
   h.Health=math.floor(h.MaxHealth*.69);oh.Health=math.floor(oh.MaxHealth*.37)
   print("COMBATUI_PAIR",p.Name,h.Health,h.MaxHealth,ps[2].Name,oh.Health,oh.MaxHealth)
   return true
  elseif mode=="heal" then
   local _,_,oh=parts(assert(ps[2]));assert(oh,"Second living Player required")
   oh.MaxHealth=160;oh.Health=160
   print("COMBATUI_HEAL",ps[2].Name,oh.Health,oh.MaxHealth)
   return true
  elseif mode=="wall" then
   assert(#ps==2,"Requires pair first")
   local _,other=parts(ps[2]);assert(other,"Second Player required")
   local wall=workspace:FindFirstChild("CombatUIReviewWall")
   if wall then wall:Destroy();return false end
   local mid=(r.Position+other.Position)*.5
   wall=Instance.new("Part");wall.Name="CombatUIReviewWall";wall.Anchored=true
   wall.Size=Vector3.new(18,18,1);wall.CFrame=CFrame.lookAt(mid,other.Position);wall.Parent=workspace
   return true
  elseif mode=="boss" then
   local b=assert(bosses and bosses.bosses[1])
   local target=b.center+Vector3.new(0,0,13)
   s.data.level=b.spec.level;s.protectedUntil=0;s.dodgingUntil=0;s.knockedUntil=0
   h.MaxHealth=Config.HealthForLevel(b.spec.level);h.Health=h.MaxHealth
   local point=target+Vector3.new(0,3,0)
   c:PivotTo(CFrame.lookAt(point,Vector3.new(b.center.X,point.Y,b.center.Z)))
   r.AssemblyLinearVelocity=Vector3.zero
   b.nextAttack=math.huge
   return b.spec.id,b.health,p.Name
  elseif mode=="damage" then
   -- Controlled call into real BossService and the private summary sender.
   -- This checks real server HP/replication/HUD, NOT aiming, power, or beam protocol.
   local b=bosses.bosses[1];local now=os.clock()
   local actual=bosses:Hit(b,p,73,now)
   assert(actual>0,"Run boss mode and stay in the arena")
   recordDamage(p,s,now,actual)
   print("COMBATUI_STAGED_DAMAGE",actual,b.health,b.spec.health,p.Name)
   return actual
  end
  error("Use pair, heal, wall, boss or damage")
 end
 print("COMBATUI_READY; guarded ServerStorage.CombatReadoutsReview")
end
