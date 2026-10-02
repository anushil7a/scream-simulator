local Config=require(game:GetService("ReplicatedStorage").Shared.Config)
local Rules={}
function Rules.CanCast(session,sound,now)
 return sound~=nil and sound.level<=session.data.level and now>=session.protectedUntil and now>=session.dodgingUntil and now>=session.nextCast and now>=(session.knockedUntil or 0)
end
function Rules.CanTarget(attackerPosition,targetPosition,targetProtectedUntil,now,radius)
 return Config.InArena(attackerPosition) and Config.InArena(targetPosition) and now>=targetProtectedUntil and (targetPosition-attackerPosition).Magnitude<=radius
end
function Rules.InBeam(origin,direction,target,length,width,targetRadius)
 local delta=target-origin;local along=delta:Dot(direction)
 if along<0 or along>length then return false end
 return (delta-direction*along).Magnitude<=width/2+(targetRadius or 0)
end
function Rules.VehicleSweep(previous,nextFrame,target,halfSize)
 local a=previous:PointToObjectSpace(target);local b=nextFrame:PointToObjectSpace(target)
 local delta=b-a;local enter,leave=0,1
 for _,axis in ipairs({"X","Y","Z"}) do
  local origin,speed,extent=a[axis],delta[axis],halfSize[axis]
  if math.abs(speed)<.00001 then if math.abs(origin)>extent then return false end
  else
   local near,far=(-extent-origin)/speed,(extent-origin)/speed
   if near>far then near,far=far,near end
   enter=math.max(enter,near);leave=math.min(leave,far);if enter>leave then return false end
  end
 end
 return true
end
return Rules
