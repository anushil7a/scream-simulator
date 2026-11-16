-- Optional compact-city encounters. Positions audited against CompactLayout.
local Catalog={Entries={
 {id="metronome",name="Whispering Metronome",level=10,x=-325,z=-55,radius=18,health=320,windup=1.5,interval=4.5,radii={3,5},attack="Pendulum pulse",damage=12,coins=35,xp=100,color={45,210,200}},
 {id="golem",name="Decibel Golem",level=30,x=285,z=125,radius=18,health=580,windup=2,interval=6,radii={6,8},attack="Bass quake",damage=20,coins=65,xp=200,color={240,170,55}},
 {id="ignis",name="Pyro-Tenor Ignis",level=50,x=-180,z=-270,radius=18,health=960,windup=1.75,interval=5,radii={4,6,3},attack="Azure overture",damage=28,coins=80,xp=270,color={70,170,255}},
 {id="leviathan",name="Leviathan Sub-Bass",level=70,x=205,z=-265,radius=18,health=1280,windup=2.25,interval=5.75,radii={5,8,6},attack="Sonar surge",damage=36,coins=95,xp=340,color={65,220,180}},
 {id="conductor",name="Eclipse Conductor",level=95,x=135,z=260,radius=18,health=1900,windup=1.5,interval=4,radii={4,7},attack="Bell cascade",damage=45,coins=110,xp=420,color={175,100,245}},
},Respawn=90,RewardCooldown=300,ResetAfter=20,CreditExpiry=20,Windup=1.5,Interval=4.5}
return Catalog
