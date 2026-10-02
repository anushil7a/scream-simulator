-- Actual service supplied by the isolated server harness; fake players test state, not voice.
return function(Soccer)
 local made={};local actors={}
 local function actor(id)
  local c=Instance.new("Model");c.Name="SoccerAuditActor";c.Parent=workspace;table.insert(made,c)
  local root=Instance.new("Part");root.Name="HumanoidRootPart";root.Anchored=true;root.CanCollide=false;root.Position=Vector3.new(647,4,547);root.Parent=c
  local h=Instance.new("Humanoid");h.Parent=c
  local player={UserId=id,DisplayName="Audit "..id,Character=c};table.insert(actors,player);return player,root
 end
 local checks=0;local completed=0
 local function check(value) assert(value,"Soccer check "..(checks+1));checks+=1 end
 local p1,r1=actor(-901);local p2,r2=actor(-902)
 local ok,err=xpcall(function()
  Soccer.Start(p1,function() end,function() completed+=1 end)
  check(Soccer.Status(p1).phase=="Find" and not Soccer.Collect(p1,1))
  r2.Position=Vector3.new(590,4,460);check(not Soccer.Collect(p2,1))
  r1.Position=r2.Position;check(Soccer.Collect(p1,1) and not Soccer.Collect(p1,1))
  r1.Position=Vector3.new(552,4,563);check(Soccer.Collect(p1,2))
  Soccer.Start(p2,function() end,function() completed+=1 end)
  check(Soccer.Collect(p2,1) and Soccer.Status(p2).detail=="Find balls 1/3" and Soccer.Status(p1).detail=="Find balls 2/3")
  r1.Position=Vector3.new(683,4,482);check(Soccer.Collect(p1,3))
  check(Soccer.Status(p1).phase=="Dribble" and Soccer.Status(p1).remaining<=90 and Soccer.Status(p1).remaining>85)
  check(not Soccer.Collect(p1,3) and completed==0)
  Soccer.Cancel(p1);check(Soccer.Status(p1)==nil and workspace.ScreamSimulatorWorld:FindFirstChild("SoccerAttempt_-901")==nil)
  check(Soccer.Status(p2)~=nil)
  r2.Position=Vector3.zero;task.wait(.25)
  check(Soccer.Status(p2)==nil and workspace.ScreamSimulatorWorld:FindFirstChild("SoccerAttempt_-902")==nil)
 end,debug.traceback)
 for _,p in ipairs(actors) do Soccer.Cancel(p) end
 for _,c in ipairs(made) do c:Destroy() end
 assert(ok,err);return {passed=true,checks=checks,completed=completed}
end
