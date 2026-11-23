local Marketplace=game:GetService("MarketplaceService")
local UIS=game:GetService("UserInputService")
local Catalog=require(game:GetService("ReplicatedStorage"):WaitForChild("Shared"):WaitForChild("ShopCatalog"))
local Config=require(game:GetService("ReplicatedStorage"):WaitForChild("Shared"):WaitForChild("Config"))
local Shop={}
local connections,timers={},{}
local prices,priceViews={},{}
local priceInFlight=0
local PRICE_LIMIT=4
local PRICE_TIMEOUT=8
local PRICE_RETRY=10
local PRICE_TTL=60
local function validPrice(info)
 return type(info)=="table" and type(info.IsForSale)=="boolean"
  and (not info.IsForSale or type(info.PriceInRobux)=="number" and info.PriceInRobux==info.PriceInRobux
   and info.PriceInRobux>=0 and info.PriceInRobux<math.huge and info.PriceInRobux%1==0)
end
-- This yielding worker deliberately captures no GUI, callback or player snapshot.
local function fetchPrice(record,id,kind)
 local ok,info=pcall(Marketplace.GetProductInfoAsync,Marketplace,id,kind)
 priceInFlight-=1;record.pending=false
 local now=os.clock()
 if prices[record.itemKey]~=record then return end
 if ok and now<record.deadline and validPrice(info) then
  record.info={IsForSale=info.IsForSale,PriceInRobux=info.IsForSale and info.PriceInRobux or nil};record.expires=now+PRICE_TTL
 else record.info=nil;record.retryAt=now+PRICE_RETRY end
end
local function updatePrice(view)
 local record=view.record;local now=os.clock()
 if prices[record.itemKey]~=record then view.apply(nil,false);return end
 if record.info and now<record.expires then view.apply(record.info,false);return end
 record.info=nil
 if not record.pending and now>=(record.retryAt or 0) and priceInFlight<PRICE_LIMIT then
  record.pending=true;record.deadline=now+PRICE_TIMEOUT;priceInFlight+=1
  task.spawn(fetchPrice,record,view.id,view.kind)
 end
 if record.info and os.clock()<record.expires then view.apply(record.info,false);return end
 view.apply(nil,record.pending and now<record.deadline)
end
local generation=0
local accent=Color3.fromRGB(79,225,255)
local violet=Color3.fromRGB(173,139,255)
local gold=Color3.fromRGB(255,209,111)
local ink=Color3.fromRGB(9,14,28)
local soft=Color3.fromRGB(160,178,208)
local purchaseGreen=Color3.fromRGB(32,84,67)
function Shop.Clear()
 generation+=1
 for _,connection in ipairs(connections) do connection:Disconnect() end
 table.clear(connections);table.clear(timers);table.clear(priceViews)
end
local function stroke(parent,color,thickness)
 local edge=Instance.new("UIStroke");edge.Color=color;edge.Transparency=.65;edge.Thickness=thickness or 1;edge.Parent=parent
end
local function gradient(parent,colors,rotation)
 local g=Instance.new("UIGradient");g.Color=ColorSequence.new(colors);g.Rotation=rotation or 0;g.Parent=parent;return g
end
function Shop.PulseFrame(button,frame)
 local trim=frame(button,"PulseFrameTrim",UDim2.fromScale(1,1),UDim2.new(),ink)
 trim.BackgroundTransparency=1;trim.Visible=false
 trim.Active=false;trim.Interactable=false;trim.Selectable=false
 for _,side in ipairs({0,1}) do
  local rail=frame(trim,"PulseEdge",UDim2.new(0,2,1,-16),UDim2.new(side,side==0 and 5 or -7,0,8),violet)
  rail.Active=false;rail.Interactable=false;rail.Selectable=false
 end
 return trim
end
function Shop.SignalDeckSkin(card)
 card.BackgroundColor3=Color3.fromRGB(19,34,62)
 stroke(card,accent,2)
 local signal=Instance.new("Frame")
 signal.Name="SignalDeckTrim";signal.Size=UDim2.new(0,3,1,-20);signal.Position=UDim2.fromOffset(5,10)
 signal.BackgroundColor3=accent;signal.BorderSizePixel=0;signal.Interactable=false;signal.Active=false;signal.Parent=card
end
function Shop.CityCrestSkin(card,ui)
 card.BackgroundColor3=Color3.fromRGB(44,37,32);stroke(card,gold,2)
 local crest=ui.frame(card,"AcademyCrest",UDim2.fromOffset(12,12),UDim2.fromOffset(17,15),gold)
 crest.Rotation=45;crest.Interactable=false
 local name=ui.label(card,"ACADEMY CITY MAP",UDim2.new(1,-58,0,28),UDim2.fromOffset(38,7),12,gold)
 name.Font=Enum.Font.GothamBold
end
function Shop.Tick()
 for _,view in ipairs(priceViews) do updatePrice(view) end
 for _,timer in ipairs(timers) do
  local remaining=math.max(0,math.ceil(timer.ends-timer.serverNow-(os.clock()-timer.received)))
  local text=not timer.ready and "Boost status unavailable" or remaining>0 and string.format("ACTIVE · %02d:%02d remaining",math.floor(remaining/60),remaining%60) or "Not active"
  if timer.label.Text~=text then
   timer.label.Text=text
   local active=timer.ready and remaining>0
   timer.label.TextColor3=active and Color3.fromRGB(112,230,174) or soft
   timer.band.BackgroundColor3=active and Color3.fromRGB(18,42,40) or ink
   timer.indicator.BackgroundColor3=active and Color3.fromRGB(112,230,174) or soft
  end
 end
end
local function purchaseButton(item,parent,owned,data,ui,action,size,pos)
 local id=Catalog.OfferId(item,Config.MovementPassId)
 local configured=id~=nil
 local text=owned and "OWNED" or not configured and "COMING SOON" or "CHECKING PRICE…"
 local available=false;local revision=generation
 local b
 b=ui.button(parent,"Buy"..item.key,text,size,pos,function()
  if revision==generation and b and b.Parent and available then action:FireServer("ShopPurchase",item.key) end
 end,owned and Color3.fromRGB(32,75,73) or ink)
 b.TextSize=13;stroke(b,accent)
 if ui.featureLayout=="short" and item.key=="Spectrum" then b.TextWrapped=true end
 b.Interactable=false;b.Selectable=false
 -- Disabled configuration is an identity change, even if the same ID returns later.
 if not configured or prices[item.key] and prices[item.key].key~=item.kind..":"..id then prices[item.key]=nil end
 if owned or not configured then b.AutoButtonColor=false;return end
 local function apply(info,pending)
  if revision~=generation or not b.Parent then return end
  available=info~=nil and info.IsForSale==true and data.savingAvailable==true
  b.Text=available and ("R$ "..tostring(info.PriceInRobux)) or data.savingAvailable~=true and "TEST / UNAVAILABLE" or pending and "CHECKING PRICE." or "UNAVAILABLE"
  b.AutoButtonColor=available;b.Interactable=available;b.Selectable=available
  b.BackgroundColor3=available and purchaseGreen or ink
 end
 -- Only the fixed catalog creates records; changing an ID invalidates old results.
 local key=item.kind..":"..id;local record=prices[item.key]
 if not record or record.key~=key then record={itemKey=item.key,key=key};prices[item.key]=record end
 local view={record=record,id=id,kind=item.kind=="pass" and Enum.InfoType.GamePass or Enum.InfoType.Product,apply=apply}
 table.insert(priceViews,view);updatePrice(view)
end
function Shop.CompactLandscape(width,height)
 return width>=644 and height>=316 and height<=430
end
function Shop.FeatureLayout(width,height)
 if width>=448 and height>=150 and height<300 then return "short" end
 if Shop.CompactLandscape(width,height) then return "compact" end
end
function Shop.Render(data,ui,action)
 Shop.Clear()
 local narrow=ui.narrow
 local revision=generation
 local function shortcut(parent,name,text,size,position,target,tint)
  local button=ui.button(parent,name,text,size,position,function()
   if revision==generation then ui.jump(target) end
  end,ink)
  button.TextSize=12;button.TextColor3=tint;stroke(button,tint)
 end
 local compact=ui.featureLayout=="compact"
 local short=ui.featureLayout=="short"
 local function section(name,title,detail,tint,order,link,target)
  local c=ui.card(64);c.Name=name;c.LayoutOrder=order
  c.BackgroundColor3=Color3.fromRGB(18,29,48)
  local line=ui.frame(c,"SectionAccent",UDim2.fromOffset(3,28),UDim2.fromOffset(8,13),tint)
  line.Interactable=false
  local textWidth=target and -108 or -36
  local heading=ui.label(c,title,UDim2.new(1,textWidth,0,20),UDim2.fromOffset(20,7),14,tint)
  heading.Font=Enum.Font.GothamBlack
  ui.label(c,detail,UDim2.new(1,textWidth,0,32),UDim2.fromOffset(20,26),12,soft)
  if target then shortcut(c,"Browse"..target,link,UDim2.fromOffset(70,44),UDim2.new(1,-78,0,10),target,tint) end
 end
 local hero=ui.card((short or compact) and 112 or narrow and 300 or 260);hero.Name="SpectrumFeature";hero.LayoutOrder=10
 local textScale,textOffset=compact and .48 or 1,compact and -24 or -32
 local function heroLabel(text,height,y,size,color)
  return ui.label(hero,text,UDim2.new(textScale,textOffset,0,height),UDim2.fromOffset(16,y),size,color)
 end
 hero.BackgroundColor3=Color3.new(1,1,1)
 gradient(hero,{ColorSequenceKeypoint.new(0,Color3.fromRGB(30,49,76)),ColorSequenceKeypoint.new(1,Color3.fromRGB(39,24,61))},25)
 stroke(hero,accent)
 if short then
  local heading=heroLabel("SPECTRUM",26,5,20)
  heading.Font=Enum.Font.GothamBlack
  heroLabel("Choose your beam hue.",22,84,13,soft)
 else
  heroLabel("PERMANENT PASS · BEAM COLOR",20,compact and 8 or 12,12,accent)
  local heading=heroLabel("SPECTRUM",compact and 28 or 38,compact and 23 or 35,compact and 24 or 30);heading.Font=Enum.Font.GothamBlack
  heroLabel("One pass. Choose your beam hue.",compact and 16 or 38,compact and 50 or 78,compact and 12 or 15)
  local beam=ui.frame(hero,"SpectrumBeam",UDim2.new(compact and .52 or 1,compact and -38 or -48,0,12),compact and UDim2.new(.48,14,0,29) or UDim2.fromOffset(24,137),Color3.new(1,1,1))
  local keys={};for i=0,6 do table.insert(keys,ColorSequenceKeypoint.new(i/6,Color3.fromHSV(i/6,.8,1))) end
  gradient(beam,keys)
  ui.frame(beam,"HotCore",UDim2.new(1,0,0,3),UDim2.fromOffset(0,4),Color3.new(1,1,1))
  for i=1,4 do
   local ring=ui.frame(hero,"EnergyRing",UDim2.fromOffset(14,42),UDim2.new(compact and .48+.52*i/5 or i/5,-7,0,compact and 14 or 122),accent)
   ring.BackgroundTransparency=1;stroke(ring,Color3.fromHSV(i/5,.5,1),2)
  end
  if not compact then heroLabel("Yellow base. Saved colors are kept.",narrow and 42 or 30,167,13,soft) end
 end
 local actionY=short and 36 or compact and 68 or narrow and 238 or 206
 purchaseButton(Catalog.Get("Spectrum"),hero,data.spectrumPass,data,ui,action,
  UDim2.new(compact and .52 or 1,short and -108 or compact and -32 or -114,0,44),
  compact and UDim2.new(.48,16,0,actionY) or UDim2.fromOffset(16,actionY))
 shortcut(hero,"BrowseTimedBoosts","BOOSTS ↓",UDim2.fromOffset(short and 68 or 74,44),
  compact and UDim2.fromOffset(16,actionY) or UDim2.new(1,short and -84 or -90,0,actionY),"BoostsSection",violet)
 section("PassesSection","PERMANENT PERKS","Movement and cosmetics",accent,15)
 local movement=ui.card(narrow and 202 or 170);movement.Name="MovementFeature";movement.LayoutOrder=20
 movement.BackgroundColor3=Color3.new(1,1,1)
 gradient(movement,{ColorSequenceKeypoint.new(0,Color3.fromRGB(22,44,68)),ColorSequenceKeypoint.new(1,Color3.fromRGB(16,26,44))},25)
 stroke(movement,accent)
 ui.label(movement,"FREERUNNER",UDim2.new(1,-32,0,28),UDim2.fromOffset(16,12),20,accent)
 ui.label(movement,"Chain jumps and dodges through the safe city. Standard movement rules apply in PvP areas.",UDim2.new(1,-32,0,narrow and 70 or 48),UDim2.fromOffset(16,48),14,soft)
 purchaseButton(Catalog.Get("Movement"),movement,data.movementPass,data,ui,action,UDim2.new(1,-32,0,44),UDim2.fromOffset(16,narrow and 142 or 110))
 local cosmeticOffers={
  {key="Encore",owned=data.encorePass,tint=gold,preview="ENCORE"},
  {key="Afterimage",owned=data.afterimagePass,tint=violet,preview="›  ›  ›"},
  {key="CityGlow",owned=data.cityGlowPass,tint=gold,preview="GLOW"},
  {key="SignalDeck",owned=data.signalDeckPass,tint=accent,preview="BEAMS"},
  {key="CityCrest",owned=data.cityCrestPass,tint=gold,preview="MAP"},
  {key="PulseFrame",owned=data.pulseFramePass,tint=violet,preview="[ PULSE ]"},
  {key="RouteLights",owned=data.routeLightsPass,tint=accent,preview="●  ●  ●"},
  {key="HarborBadge",owned=data.harborBadgePass,tint=accent,preview="HARBOR"},
  {key="SprintRibbon",owned=data.sprintRibbonPass,tint=violet,preview="»  »  »"},
 }
 for index,pass in ipairs(cosmeticOffers) do
  local item=Catalog.Get(pass.key)
  local c=ui.card(narrow and 162 or 104);c.Name=pass.key.."Feature";c.LayoutOrder=(index+2)*10
  c.BackgroundColor3=Color3.new(1,1,1)
  gradient(c,{ColorSequenceKeypoint.new(0,Color3.fromRGB(28,43,75)),ColorSequenceKeypoint.new(1,Color3.fromRGB(44,27,65))},25)
  stroke(c,pass.tint)
  local trim=ui.frame(c,"CardTrim",UDim2.fromOffset(3,76),UDim2.fromOffset(6,12),pass.tint)
  trim.Active=false;trim.Interactable=false;trim.Selectable=false
  local name=ui.label(c,item.name,UDim2.new(1,-32,0,26),UDim2.fromOffset(16,10),18)
  name.Font=Enum.Font.GothamBlack
  local plate=ui.frame(c,"PerkPreview",UDim2.fromOffset(74,22),UDim2.new(1,-90,0,12),ink)
  plate.Visible=not narrow
  name.Size=UDim2.new(1,narrow and -32 or -112,0,26)
  stroke(plate,pass.tint)
  local preview=ui.label(plate,pass.preview,UDim2.fromScale(1,1),UDim2.new(),12,pass.tint)
  preview.TextXAlignment=Enum.TextXAlignment.Center;preview.Font=Enum.Font.GothamBold
  ui.label(c,item.description,UDim2.new(1,narrow and -32 or -178,0,narrow and 56 or 48),UDim2.fromOffset(16,42),14,soft)
  purchaseButton(item,c,pass.owned,data,ui,action,narrow and UDim2.new(1,-32,0,46) or UDim2.fromOffset(126,46),
   narrow and UDim2.fromOffset(16,106) or UDim2.new(1,-142,0,44))
 end
 section("BoostsSection","TIMED BOOSTS","30 min · Counts down offline",violet,(#cosmeticOffers+2)*10+5,"PASSES ↑","SpectrumFeature")
 for index,key in ipairs({"XP","Coins"}) do
  local item=Catalog.Get(key);local tint=key=="XP" and violet or gold
  local c=ui.card(narrow and 262 or 242);c.Name="Boost"..key;c.LayoutOrder=(index+2+#cosmeticOffers)*10;stroke(c,tint)
  local badge=ui.frame(c,"Multiplier",UDim2.fromOffset(54,54),UDim2.fromOffset(16,16),tint)
  local badgeText=ui.label(badge,"2×",UDim2.fromScale(1,1),UDim2.new(),27,ink);badgeText.TextXAlignment=Enum.TextXAlignment.Center;badgeText.Font=Enum.Font.GothamBlack
  ui.label(c,item.tag,UDim2.new(1,-100,0,20),UDim2.fromOffset(84,13),12,tint)
  ui.label(c,item.name,UDim2.new(1,-100,0,32),UDim2.fromOffset(84,34),narrow and 18 or 22)
  ui.label(c,item.description.." Starts automatically on confirmed delivery.",UDim2.new(1,-32,0,narrow and 56 or 40),UDim2.fromOffset(16,80),14,soft)
  local shop=data.shop or {};local inventory=shop.inventory or {};local ends=shop.ends or {}
  -- A passive status band separates the live countdown from purchase actions.
  local band=ui.frame(c,"BoostStatus",UDim2.new(1,-32,0,40),UDim2.fromOffset(16,narrow and 148 or 128),ink)
  band.Active=false;band.Selectable=false;band.Interactable=false
  local indicator=ui.frame(band,"StateIndicator",UDim2.fromOffset(3,18),UDim2.fromOffset(8,11),soft)
  indicator.Active=false;indicator.Selectable=false;indicator.Interactable=false
  local status=ui.label(band,shop.ready==true and "Not active" or "Boost status unavailable",UDim2.new(1,-32,1,0),UDim2.fromOffset(20,0),14,soft)
  status.Name="BoostStatusText";status.Font=Enum.Font.GothamBold
  table.insert(timers,{label=status,band=band,indicator=indicator,ready=shop.ready==true,ends=ends[item.boost] or 0,serverNow=shop.serverNow or os.time(),received=shop.receivedAt or os.clock()})
  local y=narrow and 202 or 182
  local count=inventory[item.boost] or 0
  purchaseButton(item,c,false,data,ui,action,UDim2.new(count>0 and .5 or 1,count>0 and -22 or -32,0,44),UDim2.fromOffset(16,y))
  if count>0 then
   local revision=generation;local b
   b=ui.button(c,"Activate"..key,"USE SAVED ("..count..")",UDim2.new(.5,-22,0,44),UDim2.new(.5,6,0,y),function()
    if revision==generation and b and b.Parent and shop.ready then action:FireServer("ActivateBoost",item.boost) end
   end,ink);b.TextSize=13;b.TextColor3=tint;b.AutoButtonColor=shop.ready==true
  end
 end
 local footer=ui.info("New boosts activate automatically on confirmed delivery and stack time, not multiplier. Previously saved boosts remain usable.")
 if footer then footer.LayoutOrder=(5+#cosmeticOffers)*10 end
 Shop.Tick()
end
function Shop.ColorMixer(data,ui,action)
 local revision=generation
 local c=ui.card(292);c.Name="ColorMixer";stroke(c,violet)
 ui.label(c,"SIGNATURE COLOR",UDim2.new(1,-32,0,28),UDim2.fromOffset(16,12),20,violet)
 ui.label(c,data.spectrumPass and "Choose a hue, then equip it. Saved shades stay unchanged until you move the hue control." or "Preview a hue. Spectrum is required to equip it; yellow is the base color.",UDim2.new(1,-32,0,60),UDim2.fromOffset(16,44),14,soft)
 -- Preserve a saved custom shade exactly until an explicit hue edit.
 local color=data.customColor and Color3.fromHex(data.customColor) or Config.Auras[data.aura] or Config.Auras.Gold
 local hue=color:ToHSV()
 ui.label(c,"HUE",UDim2.new(1,-32,0,20),UDim2.fromOffset(16,110),12,soft)
 local bar=ui.frame(c,"HUE",UDim2.new(1,-32,0,44),UDim2.fromOffset(16,134),Color3.new(1,1,1));bar.Active=true
 local colors={};for j=0,6 do table.insert(colors,ColorSequenceKeypoint.new(j/6,Color3.fromHSV(j/6,1,1))) end
 gradient(bar,colors)
 local knob=ui.frame(bar,"Thumb",UDim2.fromOffset(10,44),UDim2.new(),Color3.new(1,1,1));stroke(knob,ink)
 local swatch=ui.frame(c,"ColorSwatch",UDim2.fromOffset(24,24),UDim2.fromOffset(16,186),color)
 swatch.Active=false;swatch.Selectable=false;swatch.Interactable=false;stroke(swatch,ink)
 local code=ui.label(c,"",UDim2.new(1,-64,0,24),UDim2.fromOffset(48,186),13,soft);code.Name="SelectedColor"
 local function update()
  code.Text="Selected color #"..color:ToHex():upper()
  swatch.BackgroundColor3=color
  knob.Position=UDim2.new(hue,-10*hue,.5,-22)
 end
 local dragInput
 local function setHue(input)
  hue=math.clamp((input.Position.X-bar.AbsolutePosition.X)/math.max(1,bar.AbsoluteSize.X),0,1)
  color=Color3.fromHSV(hue,1,1);update()
 end
 table.insert(connections,bar.InputBegan:Connect(function(input)
  if revision~=generation or dragInput then return end
  if input.UserInputType==Enum.UserInputType.MouseButton1 or input.UserInputType==Enum.UserInputType.Touch then
   dragInput=input;setHue(input)
  end
 end))
 table.insert(connections,UIS.InputChanged:Connect(function(input)
  if revision==generation and dragInput and (input==dragInput or input.UserInputType==Enum.UserInputType.MouseMovement and dragInput.UserInputType==Enum.UserInputType.MouseButton1) then setHue(input) end
 end))
 table.insert(connections,UIS.InputEnded:Connect(function(input) if input==dragInput then dragInput=nil end end))
 local equip=ui.button(c,"EquipCustom",data.spectrumPass and "EQUIP COLOR" or "PASS REQUIRED",UDim2.new(1,-32,0,44),UDim2.fromOffset(16,232),function()
  if revision==generation and data.spectrumPass then action:FireServer("SetCustomColor",color:ToHex()) end
 end,ink);equip.TextSize=13;stroke(equip,violet)
 update()
end
return Shop
