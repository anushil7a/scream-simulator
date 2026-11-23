-- Original compact-city interpretations of vault NPC-05/07/08/09.
-- Append-only resident slots: do not replace quest workers or training IDs.
local NPCs={}
local V=Vector3.new
local RGB=Color3.fromRGB
NPCs.Roster={
 {index=901,name="DJ Marina",role="Local",x=-90,z=190,lookX=-90,lookZ=200,concept="NPC-05",shirt={32,91,105},hair={64,211,217},kind="dj",action="Checking the boardwalk mix",lines={
  "Keep it comfortable. A quiet voice can still steer your beam; you do not need to shout.",
  "Eric plays in the west courtyard. Ask him about his crowd task before you head back to the stage.",
  "Watch the bottom-center meter follow your voice. Ease off to stop your attack and let it recharge."}},
 {index=902,name="Tinker Sparks",role="Vendor",x=70,z=-225,lookX=70,lookZ=-215,concept="NPC-07",shirt={81,104,62},hair={185,80,41},kind="tinker",action="Tuning portable speakers",lines={
  "A good rig fits your level, not just your wallet. Compare the gear here before you spend coins.",
  "Pau handles the cafe deliveries nearby. His tasks are a useful way to earn your next upgrade.",
  "Equipment helps your signal; it is not a reason to strain your voice. Start with a comfortable sound."}},
 {index=903,name="Lifeguard Kai",role="Local",x=-205,z=210,lookX=-205,lookZ=200,concept="NPC-08",shirt={232,101,75},hair={190,157,92},kind="lifeguard",action="Watching the waterfront",lines={
  "The promenade stays clear. Follow it east for the pier and Nick's hidden court.",
  "Look for the boardwalk runner near the lookout if you want a sprint task.",
  "If a fight gets too much, step away and reset. You can practice dodging with the arena coach first."}},
 {index=904,name="Archivist Lyra",role="Local",x=-290,z=65,lookX=-270,lookZ=65,concept="NPC-09",shirt={30,112,117},hair={163,184,202},kind="archivist",action="Cataloguing resonance notes",lines={
  "The training pads are north of here. Start with the lowest recommendation and learn the red strike warning.",
  "New beams unlock as you level. Check Beams when you reach each ten-level milestone.",
  "Open the full Map for all five boss rings and their required levels. Step into a ring and land a beam when you want to join."}},
}
local map10Directions={
 [901]="Want a music task? Open Quests and select Guide on the one you choose. The guide won't start on its own.",
 [902]="Ask Pau about cafe deliveries. Pick Guide on your active delivery to find the correct stop.",
 [903]="The coast leads down to the pier. Use the full Map to choose a destination if you're looking for a specific activity.",
 [904]="Start with the lowest recommended trainer. Open the full Map if you want to choose which training area to visit.",
}
function NPCs.AtHome(original,home)
 if not home then return original end
 local spec=table.clone(original)
 spec.x,spec.y,spec.z=home.x,home.y,home.z
 spec.lookX,spec.lookZ=home.lookX or home.x,home.lookZ or (home.z+1)
 spec.lines=table.clone(original.lines)
 spec.lines[1]=map10Directions[spec.index] or spec.lines[1]
 if spec.index==901 then
  spec.lines[2]="Eric has a crowd task. Look for him in the Quests panel when you're ready."
 end
 return spec
end
function NPCs.Job(spec)
 local rootHeight=(spec.y or 0)+3
 return {name=spec.name,role=spec.role,supporting=true,lines=spec.lines,stations={{position=V(spec.x,rootHeight,spec.z),lookAt=V(spec.lookX,rootHeight,spec.lookZ),action=spec.action}}}
end
function NPCs.Dress(bot,spec,accessory)
 local model=bot.model
 model:SetAttribute("SupportConcept",spec.concept)
 model:SetAttribute("VisualSource","Authored runtime costume; Blender look preview from same geometry")
 local torso=model:FindFirstChild("Torso");local head=model:FindFirstChild("Head")
 local color=RGB(table.unpack(spec.shirt));local hair=RGB(table.unpack(spec.hair))
 for _,name in ipairs({"Torso","Left Arm","Right Arm"}) do model:FindFirstChild(name).Color=color end
 -- Remove only generated cosmetic headwear/apron from these new residents.
 for _,item in ipairs(model:GetChildren()) do
  if item.Name=="Hair" or item.Name=="CurlyHair" or item.Name=="Cap" or item.Name=="CapBrim" or item.Name=="HeadphoneEar" or item.Name=="HeadphoneBand" or item.Name=="GlassesLens" or item.Name=="GlassesBridge" or item.Name=="VendorApron" or item.Name=="Jacket" then item:Destroy() end
 end
 local function add(target,name,size,offset,c)
  return accessory(model,target,name,V(table.unpack(size)),CFrame.new(table.unpack(offset)),c,Enum.Material.SmoothPlastic)
 end
 add(head,"SignatureHair",{2.12,.55,1.2},{0,.65,0},hair)
 local gold=RGB(220,177,80);local dark=RGB(35,43,56);local cyan=RGB(80,217,222)
 if spec.kind=="dj" then
  for _,x in ipairs({-1.1,1.1}) do add(head,"MarinaHeadphone",{.3,.7,.65},{x,0,0},cyan) end
  add(head,"MarinaHeadband",{2.3,.15,.45},{0,1,0},dark)
  add(torso,"SynthDeck",{2.6,.3,1.25},{0,-.7,-1.0},dark)
  for _,x in ipairs({-.8,.8}) do add(torso,"DeckPad",{.6,.1,.65},{x,-.5,-1},cyan) end
  for _,x in ipairs({-.68,.68}) do
   add(torso,"MarinaLapel",{.18,1.05,.12},{x,.28,-.58},cyan)
   add(torso,"MarinaPocket",{.48,.3,.14},{x,-.24,-.6},dark)
  end
  for _,name in ipairs({"Left Arm","Right Arm"}) do
   add(model:FindFirstChild(name),"MarinaCuff",{1.04,.2,1.04},{0,-.65,0},cyan)
  end
  add(torso,"DeckFader",{.15,.12,.38},{0,-.47,-1},gold)
  add(head,"SideBraid",{.3,1.15,.3},{.92,-.1,.52},hair)
 elseif spec.kind=="tinker" then
  for _,x in ipairs({-.48,.48}) do add(head,"SparksGoggle",{.7,.5,.22},{x,.42,-.63},gold) end
  for _,x in ipairs({-.66,.66}) do
   add(torso,"SpeakerPack",{.8,1.7,.6},{x,0,.8},dark)
   for _,y in ipairs({-.4,.4}) do add(torso,"PackCone",{.55,.55,.1},{x,y,1.15},gold) end
  end
  add(torso,"UtilityBelt",{2.15,.25,1.1},{0,-.8,0},gold)
  for _,x in ipairs({-.66,.66}) do
   add(torso,"HarnessWebbing",{.18,1.5,.12},{x,.12,-.56},RGB(119,82,51))
   add(torso,"HarnessBuckle",{.28,.27,.16},{x,.45,-.63},gold)
   add(torso,"ToolPouch",{.55,.6,.3},{x,-.72,-.69},RGB(104,67,43))
   add(head,"GoggleGlass",{.44,.3,.1},{x*.727,.42,-.78},dark)
  end
  add(torso,"BeltClasp",{.32,.3,.15},{0,-.8,-.63},dark)
 elseif spec.kind=="lifeguard" then
  add(torso,"RescueVest",{2.12,1.6,.2},{0,0,-.6},RGB(241,115,84))
  add(torso,"VestStripe",{2.14,.17,.23},{0,.35,-.62},RGB(246,229,178))
  add(torso,"RescueFloat",{.8,2.5,.5},{0,0,.85},RGB(241,115,84))
  for _,x in ipairs({-.48,.48}) do add(head,"KaiShades",{.7,.35,.15},{x,.07,-.6},dark) end
  for _,x in ipairs({-.7,.7}) do
   add(torso,"RescueStrap",{.16,1.48,.15},{x,.02,-.77},dark)
   add(torso,"RescueBuckle",{.32,.24,.1},{x,-.45,-.88},RGB(246,229,178))
  end
  add(torso,"VestZip",{.07,1.4,.08},{0,0,-.76},dark)
  add(torso,"Whistle",{.18,.3,.18},{.3,.15,-.85},gold)
  for _,name in ipairs({"Left Leg","Right Leg"}) do
   add(model:FindFirstChild(name),"BoardShortPanel",{1.02,.94,1.02},{0,.5,0},RGB(42,136,139))
  end
 else
  add(torso,"ArchivistMantle",{2.3,2,.2},{0,0,.65},color)
  add(torso,"MantleTrim",{2.35,.18,.25},{0,.85,.66},gold)
  add(model:FindFirstChild("Left Arm"),"ResonanceBook",{.9,1.1,.3},{0,-.7,-.65},gold)
  add(model:FindFirstChild("Left Arm"),"BookInlay",{.65,.8,.07},{0,-.7,-.84},cyan)
  for _,x in ipairs({-.82,.82}) do
   add(torso,"MantleBorder",{.12,1.8,.08},{x,-.05,.8},gold)
   add(torso,"ScholarStole",{.24,1.7,.16},{x,.02,-.6},gold)
  end
  for _,name in ipairs({"Left Leg","Right Leg"}) do
   local leg=model:FindFirstChild(name)
   add(leg,"SplitCoatTail",{.9,1.7,.14},{0,.1,.6},color)
   add(leg,"CoatHem",{.92,.12,.18},{0,-.72,.62},gold)
  end
  add(torso,"TuningClasp",{.3,.42,.2},{0,.63,-.63},gold)
  add(model:FindFirstChild("Left Arm"),"BookPages",{.82,.9,.08},{0,-.7,-.46},RGB(238,230,207))
 end
end
return NPCs
