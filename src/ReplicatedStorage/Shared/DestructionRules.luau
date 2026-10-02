local Rules={}
Rules.Types={
 Bench={level=1,health=50,repair=120},
 Bin={level=1,health=36,repair=120},
 SmallTree={level=26,health=110,repair=180},
 Bike={level=35,health=145,repair=180},
 HouseFacade={level=51,health=180,repair=300},
 ApartmentFacade={level=76,health=250,repair=300},
 TowerFacade={level=100,health=340,repair=300},
}
function Rules.Hit(kind,level,health,damage)
 local spec=Rules.Types[kind]
 if not spec or type(level)~='number' or level~=level or level<spec.level then return health,false,'level' end
 if type(damage)~='number' or damage~=damage or damage<=0 or damage>48 then return health,false,'damage' end
 if type(health)~='number' or health~=health or health<=0 or health>spec.health then return health,false,'health' end
 local nextHealth=math.max(0,health-damage)
 return nextHealth,nextHealth==0,nil
end
return Rules
