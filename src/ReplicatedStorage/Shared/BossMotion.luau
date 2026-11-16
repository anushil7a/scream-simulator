-- Deterministic bounded patrol; convex chord paths stay within the inner leash.
local Motion={}
function Motion.New() return {x=0,z=0,yaw=0,waypoint=0} end
function Motion.Step(m,spec,dt)
 dt=math.clamp(dt,0,.25)
 local angle=m.waypoint*math.pi/4
 local x,z=math.cos(angle)*spec.moveLeash,math.sin(angle)*spec.moveLeash
 local dx,dz=x-m.x,z-m.z;local distance=math.sqrt(dx*dx+dz*dz)
 if distance<.01 then m.waypoint=(m.waypoint+1)%8;return end
 local amount=math.min(distance,spec.moveSpeed*dt)
 m.x+=dx/distance*amount;m.z+=dz/distance*amount
 m.yaw=math.atan2(-dx,-dz)
end
return Motion
