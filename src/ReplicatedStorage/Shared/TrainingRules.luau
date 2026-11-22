local Training={Radius=32,StrikeRadius=4,StrikeHeight=6,Windup=1.1,AttackInterval=4,ResetAfter=25,RoamRadius=18,RoamSpeed=7,RoamLeash=22}
Training.Tiers={
 {id="rookie",name="Rookie",level=1,maxLevel=24,health=80,damage=8,xp=48,x=-440,z=545},
 {id="brawler",name="Brawler",level=25,maxLevel=59,health=220,damage=18,xp=180,x=-320,z=545},
 {id="elite",name="Elite",level=60,maxLevel=100,health=420,damage=32,xp=420,x=-200,z=545},
}
function Training.RewardLevel(tier,level)
 return math.clamp(level,tier.level,tier.maxLevel)
end
function Training.Recommended(level)
 local tier=Training.Tiers[1]
 for _,candidate in ipairs(Training.Tiers) do if level>=candidate.level then tier=candidate end end
 return tier
end
-- A ground strike spans the painted circle and the volume just above it.
function Training.ContainsStrike(center,position)
 local x,y,z=position.X-center.X,position.Y-center.Y,position.Z-center.Z
 return y>=0 and y<=Training.StrikeHeight and x*x+z*z<=Training.StrikeRadius^2
end
function Training.Hits(center,position,protected,dodging)
 return not protected and not dodging and Training.ContainsStrike(center,position)
end
return Training
