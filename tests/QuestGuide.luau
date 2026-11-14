local Guide=require('../src/ReplicatedStorage/Shared/QuestGuide')
local q={id='delivery',goal=1}
assert(Guide.Step(q,0,false,false,nil,'lifeguard lookout')=='Pick up coffee at the market')
for _,name in ipairs({'boardwalk music stage','lifeguard lookout','end of the timber pier'}) do
 assert(Guide.Step(q,0,true,false,nil,name)=='Deliver to the '..name)
 assert(Guide.Step(q,1,true,false,nil,name)=='Complete · claim in Quests')
end
assert(Guide.Step(q,0,true,false,nil)=='Deliver to the boardwalk music stage')
assert(Guide.Step(nil,0,false,false)==nil)
print('PASS 9 delivery guide checks')
