local make=require('./DistrictCoast')
local specs={['03']={center={-420,8,-820},size={780,320}},['10']={center={-1150,12,-650},size={480,480}}}
for id,spec in pairs(specs) do
 local n=0;local names={};local b={}
 function b:part(name,p,s,c,solid,r,mat,tags)
  n+=1;assert(not names[name]);names[name]=true;assert(solid==true)
  for _,v in ipairs(s) do assert(v>0) end
  -- Conservative radius in XZ for tilted pieces, exact footprint for yaw-only pieces.
  r=r or {0,0,0};local yaw=math.rad(r[2]);local ex=math.abs(math.cos(yaw))*s[1]/2+math.abs(math.sin(yaw))*s[3]/2;local ez=math.abs(math.sin(yaw))*s[1]/2+math.abs(math.cos(yaw))*s[3]/2
  ex+=math.abs(math.sin(math.rad(r[3])))*s[2]/2;ez+=math.abs(math.sin(math.rad(r[1])))*s[2]/2
  local x,z=p[1]-spec.center[1],p[3]-spec.center[3]
  assert(math.abs(x)-ex>=22,name..' blocks vertical cross')
  assert(math.abs(z)-ez>=22,name..' blocks horizontal cross')
  assert(math.abs(x)+ex<=spec.size[1]/2-32,name..' perimeter X')
  assert(math.abs(z)+ez<=spec.size[2]/2-32,name..' perimeter Z')
 end
 function b:disk(name,x,y,z,r,h,c,solid,mat,tags) self:part(name,{x,y,z},{r*2,h,r*2},c,solid,nil,mat,tags) end
 make(b,id,spec);assert(n<=240);print('COAST_PASS',id,n)
end
