-- Run in a disposable local Play client. Synthetic movement, not physical input.
-- Temporarily overrides speed because voice setup otherwise locks movement.
assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio(),"Local Studio only")
local c=assert(game.Players.LocalPlayer.Character)
local h=c:FindFirstChildOfClass("Humanoid")
local root=c.HumanoidRootPart
local original=c:GetPivot();local speed=h.WalkSpeed
local rs=game:GetService("RunService")
local direction=Vector3.new(0,0,1)
local results={}
local ok,err=xpcall(function()
 c:PivotTo(CFrame.new(0,4,588))
 rs:BindToRenderStep("ShoreWalkReview",1000,function() h.WalkSpeed=16;h:Move(direction,false) end)
 task.wait(4)
 results.entry={z=root.Position.Z,y=root.Position.Y,state=h:GetState().Name}
 assert(root.Position.Z>630 and h:GetState()==Enum.HumanoidStateType.Swimming,"Shore entry blocked")
 direction=Vector3.new(0,0,-1)
 task.wait(5)
 results.exit={z=root.Position.Z,y=root.Position.Y,state=h:GetState().Name}
 assert(root.Position.Z<595 and root.Position.Y>3 and h:GetState()==Enum.HumanoidStateType.Running,"Could not walk back onto beach")
end,debug.traceback)
rs:UnbindFromRenderStep("ShoreWalkReview");h:Move(Vector3.zero);h.WalkSpeed=speed
c:PivotTo(original);root.AssemblyLinearVelocity=Vector3.zero
assert(ok,err)
return results
