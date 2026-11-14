local Style=require("../src/ReplicatedStorage/Shared/BeamStyle")
assert(Style.LaunchScale(-1,false)==.55)
assert(Style.LaunchScale(0,false)==.55)
assert(Style.LaunchScale(.06,false)>.55 and Style.LaunchScale(.06,false)<1)
assert(Style.LaunchScale(.12,false)==1 and Style.LaunchScale(100,false)==1)
assert(Style.LaunchScale(0,true)==1)
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
assert(Style.StyleForLevel(1).id=="starter" and Style.StyleForLevel(39).id=="starter")
assert(Style.StyleForLevel(40).id=="firebeam" and Style.StyleForLevel(79).id=="firebeam")
assert(Style.StyleForLevel(80).id=="hollow_purple" and Style.StyleForLevel(100).id=="hollow_purple")
assert(Style.Detail(1,false,15).style=="starter")
assert(Style.Detail(50,false,15).style=="firebeam" and Style.Detail(50,true,15).style=="firebeam")
assert(Style.Detail(90,false,15).style=="hollow_purple" and Style.Detail(90,false,150).style=="hollow_purple")
assert(Style.SpecialBeams.ChargingBeam.id=="charging_beam" and Style.SpecialBeams.ChargingBeam.status=="reserved")
print("PASS beam tier boundaries, bounded increasing detail, reduced and distant effects")
