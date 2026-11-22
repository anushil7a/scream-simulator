-- Authored geometry shared by the standalone draft and guarded combat preview.
local Layout={
 Hall={x=0,z=0,width=176,depth=152},
 Practice={x=0,z=248,width=72,depth=48},
 Combat={minX=-86,maxX=86,minZ=-74,maxZ=74,minY=0,maxY=16},
 Apron={halfWidth=11,startZ=50},
 Desk={x=0,z=0,width=28,depth=8},
 HallPortal={x=0,z=65},
 PracticePortal={x=0,z=265},
 Speakers={
  {x=53,z=42,width=16,height=12,depth=7},
  {x=27,z=24,width=13,height=10,depth=5},
 },
}
function Layout.Contains(deck,position)
 return math.abs(position.X-deck.x)<=deck.width/2 and math.abs(position.Z-deck.z)<=deck.depth/2
end
function Layout.IsSafeApron(position)
 return position.Z>=Layout.Apron.startZ and math.abs(position.X)<=Layout.Apron.halfWidth
end
return Layout
