-- Fixed ground shapes: identical math for warning geometry and authoritative damage.
-- No tracking, asynchronous damage, body collisions or client-reported targets.
local Patterns={}
local function disk(x,z,r) return {kind="disk",x=x,z=z,radius=r} end
local function bar(x,z,w,l,a) return {kind="bar",x=x,z=z,width=w,length=l,angle=a} end
function Patterns.Build(id,turn,x,z)
 local a=math.atan2(x,z);local shapes={};local name
 if id=="metronome" then
  name="Pendulum beat · step sideways"
  shapes={bar(0,0,4,30,a+(turn%2==0 and math.pi/2 or 0))}
 elseif id=="golem" then
  if turn%2==1 then name="Woofer slam · move out";shapes={disk(0,0,10)}
  else name="Fault-line quake · find a corner";shapes={bar(0,0,5,30,0),bar(0,0,5,30,math.pi/2)} end
 elseif id=="ignis" then
  name="Organ flames · slip between lanes"
  local angle=(turn%2)*math.pi/2
  for i=-1,1 do
   local off=i*8;table.insert(shapes,bar(math.cos(angle)*off,-math.sin(angle)*off,3,26,angle))
  end
 elseif id=="leviathan" then
  -- Stable encounter key; the visible captain replaces the former sea creature.
  if turn%2==1 then
   name="Cutlass broadside · step back or aside"
   shapes={bar(math.sin(a)*8,math.cos(a)*8,24,5,a)}
  else
   name="Twin sirens · find the center gap"
   for _,side in ipairs({-1,1}) do
    table.insert(shapes,bar(math.cos(a)*side*6,-math.sin(a)*side*6,4,24,a))
   end
  end
 elseif id=="conductor" then
  name="Six-bell chord · stand in a gap"
  for i=1,6 do local t=i*math.pi/3+(turn%2)*math.pi/6;table.insert(shapes,disk(math.sin(t)*11,math.cos(t)*11,4)) end
 end
 return {shapes=shapes,name=name}
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
