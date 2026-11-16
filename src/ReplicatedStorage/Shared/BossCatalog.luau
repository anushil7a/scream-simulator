-- Optional encounters. Public range and shared visual/aim scale are authoritative.
local Catalog={Entries={
 {id="metronome",name="Whispering Metronome",level=10,x=-325,z=-55,radius=22,health=320,windup=1.5,interval=4.5,attack="Pendulum beat",damage=12,coins=35,xp=100,color={45,210,200}},
 {id="golem",name="Decibel Golem",level=30,x=285,z=125,radius=22,health=580,windup=2,interval=6,attack="Bass quake",damage=20,coins=65,xp=200,color={240,170,55}},
 {id="ignis",name="Pyro-Tenor Ignis",level=50,x=-180,z=-270,radius=22,health=960,windup=1.75,interval=5,attack="Azure overture",damage=28,coins=80,xp=270,color={70,170,255}},
 {id="leviathan",name="Seagull Siren Captain",level=70,x=205,z=-265,radius=22,health=1280,windup=2.25,interval=5.75,attack="Cutlass and siren",damage=36,coins=95,xp=340,color={230,195,105}},
 {id="conductor",name="Eclipse Conductor",level=95,x=135,z=260,radius=22,health=1900,windup=1.5,interval=4,attack="Bell cascade",damage=45,coins=110,xp=420,color={175,100,245}},
},Respawn=90,RewardCooldown=300,ResetAfter=20,CreditExpiry=20,Windup=1.5,Interval=4.5}
local Layout=require(script.Parent.CompactLayout)
for _,spec in ipairs(Catalog.Entries) do
 spec.moveLeash=4;spec.moveSpeed=2;spec.recovery=.6;spec.scale=1.4;spec.aimHeight=7;spec.engageHeight=12
 local home=Layout.BossHomes and Layout.BossHomes[spec.id]
 if home then spec.x=home.x;spec.y=home.y;spec.z=home.z end
end
return Catalog
