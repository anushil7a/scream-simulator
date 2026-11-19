-- Fixed ground shapes: identical math for warning geometry and authoritative damage.
-- No tracking, asynchronous damage, body collisions or client-reported targets.
local Patterns={}
local function disk(x,z,r) return {kind="disk",x=x,z=z,radius=r} end
local function bar(x,z,w,l,a) return {kind="bar",x=x,z=z,width=w,length=l,angle=a} end
function Patterns.Build(id,turn,x,z,radius,leash)
 local a=math.atan2(x,z);local shapes={};local name,style,push
 local melee=turn%2==0
 local function forward(distance,width,length)
  return bar(math.sin(a)*distance,math.cos(a)*distance,width,length,a)
 end
 -- All corners, even at worst orientation, fit outside a reserved patrol
 -- margin. Isolated review places may override radius independently of live.
 local room=math.max(1,(radius or 22)-(leash or 4)-.5)
 local function lane(offset,width,angle)
  local edge=math.abs(offset)+width/2
  local length=2*math.sqrt(math.max(0,room*room-edge*edge))
  return bar(math.cos(angle)*offset,-math.sin(angle)*offset,width,length,angle)
 end
 if id=="metronome" then
  if melee then
   name="Resonance kick · step back or aside";style="ResonanceKick";push=4
   shapes={forward(5.5,8,8)}
  else
   name="Pendulum sweep · step sideways";style="PendulumSweep"
   shapes={lane(0,5,a+((turn-1)/2%2)*math.pi/2)}
  end
 elseif id=="golem" then
  if melee then
   name="Woofer slam · leave the circle";style="WooferSlam";push=6.5
   shapes={disk(0,0,12)}
  else
   name="Fault-line quake · find a corner";style="FaultLine"
   shapes={lane(0,6,0),lane(0,6,math.pi/2)}
  end
 elseif id=="ignis" then
  if melee then
   name="Backdraft stomp · leave the circle";style="Backdraft";push=5
   shapes={disk(0,0,10)}
  else
   name="Organ flames · slip between lanes";style="OrganFlames"
   -- Train the center flame lane on the selected participant from the current
   -- patrol position. The flanking lanes leave fixed gaps for a sidestep.
   for i=-1,1 do table.insert(shapes,lane(i*8,3.5,a)) end
  end
 elseif id=="leviathan" then
  -- Stable encounter key; the visible captain replaces the former sea creature.
  if melee then
   name="Cutlass broadside · step back or aside";style="CutlassBroadside";push=5.5
   shapes={forward(8,24,5)}
  else
   name="Twin sirens · find the center gap";style="TwinSirens"
   -- Lead the fixed shoulder lane onto the chosen player, not the safe gap.
   -- At point-blank range the gap remains a legitimate escape route.
   local distance=math.sqrt(x*x+z*z)
   if distance>=8 then a-=math.asin(6/distance) end
   for _,side in ipairs({-1,1}) do table.insert(shapes,lane(side*6,4,a)) end
  end
 elseif id=="conductor" then
  if melee then
   name="Baton sweep · step back or aside";style="BatonSweep";push=6
   shapes={forward(7,15,7)}
  else
   name="Six-bell cascade · stand in a gap";style="BellCascade"
   for i=1,6 do local t=i*math.pi/3+((turn-1)/2%2)*math.pi/6;table.insert(shapes,disk(math.sin(t)*(room-4.5),math.cos(t)*(room-4.5),4.5)) end
  end
 end
 return {shapes=shapes,name=name,style=style,kind=melee and "Melee" or "Ranged",push=push,aimX=math.sin(a),aimZ=math.cos(a)}
end
function Patterns.Contains(shape,x,z)
 x-=shape.x;z-=shape.z
 if shape.kind=="disk" then return x*x+z*z<=shape.radius*shape.radius end
 local c,s=math.cos(shape.angle),math.sin(shape.angle)
 return math.abs(c*x-s*z)<=shape.width/2 and math.abs(s*x+c*z)<=shape.length/2
end
function Patterns.Hits(pattern,x,z)
 for _,shape in ipairs(pattern.shapes) do if Patterns.Contains(shape,x,z) then return true end end
 return false
end
return Patterns
