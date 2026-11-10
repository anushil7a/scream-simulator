local Style=require("../src/ReplicatedStorage/Shared/BeamStyle")
assert(Style.Tier(1)==0 and Style.Tier(9)==0 and Style.Tier(10)==1 and Style.Tier(100)==10)
assert(Style.Tier(0/0)==0 and Style.Tier(999)==10)
local previous=0
for level=1,100 do
 local s=Style.Detail(level,false,10)
 local parts=5+s.rings*10+s.strands*12+s.sparks
 assert(parts>=previous and parts<=77);previous=parts
 local reduced=Style.Detail(level,true,10)
 assert(reduced.rings==0 and reduced.strands==0 and reduced.sparks==0)
 local distant=Style.Detail(level,false,111)
 assert(distant.rings==0 and distant.strands==0 and distant.sparks==0)
end
print("PASS beam tier boundaries, bounded increasing detail, reduced and distant effects")
