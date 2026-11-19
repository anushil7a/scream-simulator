-- A short server-positioned shove instead of an uncapped physics impulse.
-- Reuse the dodge ground/headroom/avatar sweep and stop at the first unsafe step.
local DodgeMotion=require(script.Parent.DodgeMotion)
local Knockback={}
function Knockback.Target(world,frame,boss,strike,params,humanoid,inWorld)
 local start=frame.Position
 local relative=start-boss.center
 local away=Vector3.new(relative.X-strike.x,0,relative.Z-strike.z)
 local direction=away.Magnitude>.01 and away.Unit or Vector3.new(strike.aimX,0,strike.aimZ)
 local radius=math.max(0,boss.spec.radius-1.5) -- avatar clearance at arena edge
 local position=start
 local count=math.ceil(math.min(strike.push,6.5)/.5)
 for _=1,count do
  local nextPoint=DodgeMotion.Step(world,CFrame.new(position)*frame.Rotation,direction,.5,params,humanoid)
  if not nextPoint then break end
  local d=nextPoint-boss.center
  if d.X*d.X+d.Z*d.Z>radius*radius or math.abs(d.Y)>boss.spec.engageHeight or not inWorld(nextPoint) then break end
  position=nextPoint
 end
 return position~=start and position or nil
end
return Knockback
