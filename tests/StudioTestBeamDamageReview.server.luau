-- Manual, guarded 0/0 fixture. No player-remoting hook or staged damage.
do
 assert(RunService:IsStudio() and game.PlaceId==0 and game.GameId==0 and localFixture,"Test Beam damage review is local only")
 local invoke=Instance.new("BindableFunction");invoke.Name="TestBeamDamageReview";invoke.Parent=game:GetService("ServerStorage")
 invoke.OnInvoke=function(mode)
  local list=Players:GetPlayers()
  assert(#list==2,"Start two Studio players first")
  table.sort(list,function(a,b)return a.UserId<b.UserId end)
  assert(mode=="stage" or mode=="read","Use stage or read")
  for i,p in ipairs(list) do
   local s=assert(sessions[p]);local c,r,h=parts(p)
   assert(c and r and h and not s.canSave and not s.flight,"Expected living local characters only")
   if mode=="stage" then
    local pos=Vector3.new(40,19, i==1 and 79 or 87)
    local direction=Vector3.new(0,0,i==1 and 1 or -1)
    assert(Config.InArena(pos),"Known lawn PvP staging site must still be active")
    c:PivotTo(CFrame.lookAt(pos,pos+direction))
    r.AssemblyLinearVelocity=Vector3.zero;h.Health=h.MaxHealth
    s.protectedUntil=0;s.dodgingUntil=0;s.knockedUntil=0;s.nextHeal=os.clock()+90
    p:SetAttribute("ProtectionEnds",0);p:SetAttribute("DodgeEnds",0);p:SetAttribute("KnockdownEnds",0)
   end
   print("TEST_BEAM_DAMAGE_REVIEW",mode,i,p.Name,h.Health,h.MaxHealth,s.testBaseline~=nil,s.data.coins,s.data.xp,s.testBeam~=nil,r.Position)
  end
  return list[1].Name,list[2].Name
 end
 print("TEST_BEAM_DAMAGE_READY; ServerStorage.TestBeamDamageReview stage/read; use real client clicks")
end
