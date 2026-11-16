-- Server-only four-way motion. Client supplies a bounded intent, never a vector or distance.
local M={}
function M.Direction(frame,move,intent)
 local right=Vector3.new(frame.RightVector.X,0,frame.RightVector.Z)
 right=right.Magnitude>.01 and right.Unit or Vector3.new(1,0,0)
 local forward=Vector3.new(right.Z,0,-right.X)
 local side,front=0,0
 if intent=="Left" or intent==-1 then side=-1
 elseif intent=="Right" or intent==1 then side=1
 elseif intent=="Forward" then front=1
 elseif intent=="Back" then front=-1
 else
  -- Unknown/malformed payload cannot supply movement magnitude or world vectors.
  local x,z=move:Dot(right),move:Dot(forward)
  if math.abs(z)>.1 and math.abs(z)>=math.abs(x) then front=z<0 and -1 or 1
  elseif math.abs(x)>.1 then side=x<0 and -1 or 1
  else side=1 end
 end
 return right*side+forward*front,side,front
end
function M.Step(world,frame,direction,distance,params,humanoid)
 -- Small substeps prevent skipping a narrow edge during a long server heartbeat.
 local position=frame.Position
 if distance<=.00001 then return position end
 local count=math.max(1,math.ceil(distance/.5))
 for _=1,count do
  local delta=direction*(distance/count)
  local ground=world:Raycast(position+Vector3.new(0,1,0),Vector3.new(0,-8,0),params)
  if not ground then return nil end
  local nextPoint=position+delta
  local ahead=world:Raycast(nextPoint+Vector3.new(0,1,0),Vector3.new(0,-8,0),params)
  local minNormal=math.cos(math.rad(math.min(humanoid.MaxSlopeAngle,45)))
  if not ahead or ahead.Normal.Y<minNormal then return nil end
  local rise=ahead.Position.Y-ground.Position.Y
  if math.abs(rise)>.65 then return nil end
  nextPoint+=Vector3.new(0,rise,0)
  if world:Blockcast(CFrame.new(position)*frame.Rotation,Vector3.new(2,2.5,2),nextPoint-position,params) then return nil end
  position=nextPoint
 end
 return position
end
return M
