local Marketplace=game:GetService("MarketplaceService")
local UIS=game:GetService("UserInputService")
local Catalog=require(game:GetService("ReplicatedStorage").Shared.ShopCatalog)
local Config=require(game:GetService("ReplicatedStorage").Shared.Config)
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
function Shop.Tick()
 for _,view in ipairs(priceViews) do updatePrice(view) end
 for _,timer in ipairs(timers) do
  local remaining=math.max(0,math.ceil(timer.ends-timer.serverNow-(os.clock()-timer.received)))
  local text=not timer.ready and "Boost status unavailable" or remaining>0 and string.format("ACTIVE · %02d:%02d remaining",math.floor(remaining/60),remaining%60) or "Not active"
  if timer.label.Text~=text then timer.label.Text=text end
 end
end
local function purchaseButton(item,parent,owned,data,ui,action,size,pos)
 local id=item.key=="Movement" and Config.MovementPassId or item.id
 local configured=type(id)=="number" and id==id and id>0 and id<math.huge and id%1==0
 local text=owned and "OWNED" or not configured and "COMING SOON" or "CHECKING PRICE…"
 local available=false;local revision=generation
 local b
 b=ui.button(parent,"Buy"..item.key,text,size,pos,function()
  if revision==generation and b and b.Parent and available then action:FireServer("ShopPurchase",item.key) end
 end,owned and Color3.fromRGB(32,75,73) or ink)
 b.TextSize=13;stroke(b,accent)
 -- Disabled configuration is an identity change, even if the same ID returns later.
 if not configured or prices[item.key] and prices[item.key].key~=item.kind..":"..id then prices[item.key]=nil end
 if owned or not configured then b.AutoButtonColor=false;return end
 local function apply(info,pending)
  if revision~=generation or not b.Parent then return end
  available=info~=nil and info.IsForSale==true and data.savingAvailable==true
  b.Text=available and ("R$ "..tostring(info.PriceInRobux)) or data.savingAvailable~=true and "TEST / UNAVAILABLE" or pending and "CHECKING PRICE." or "UNAVAILABLE"
  b.AutoButtonColor=available
 end
 -- Only the fixed catalog creates records; changing an ID invalidates old results.
 if Catalog.Get(item.key)~=item or type(id)~="number" or id~=id or id<=0 or id>=math.huge or id%1~=0 then apply(nil,false);return end
 local key=item.kind..":"..id;local record=prices[item.key]
 if not record or record.key~=key then record={itemKey=item.key,key=key};prices[item.key]=record end
 local view={record=record,id=id,kind=item.kind=="pass" and Enum.InfoType.GamePass or Enum.InfoType.Product,apply=apply}
 table.insert(priceViews,view);updatePrice(view)
end
function Shop.Render(data,ui,action)
 Shop.Clear()
 local narrow=ui.narrow
 local hero=ui.card(narrow and 300 or 260);hero.Name="SpectrumFeature"
 hero.BackgroundColor3=Color3.new(1,1,1)
 gradient(hero,{ColorSequenceKeypoint.new(0,Color3.fromRGB(30,49,76)),ColorSequenceKeypoint.new(1,Color3.fromRGB(39,24,61))},25)
 stroke(hero,accent)
 ui.label(hero,"01 / MAKE IT YOURS",UDim2.new(1,-32,0,20),UDim2.fromOffset(16,12),12,accent)
 local heading=ui.label(hero,"SPECTRUM",UDim2.new(1,-32,0,38),UDim2.fromOffset(16,35),30);heading.Font=Enum.Font.GothamBlack
 ui.label(hero,"One pass. Choose your beam hue.",UDim2.new(1,-32,0,38),UDim2.fromOffset(16,78),15)
 local beam=ui.frame(hero,"SpectrumBeam",UDim2.new(1,-48,0,12),UDim2.fromOffset(24,137),Color3.new(1,1,1))
 local keys={};for i=0,6 do table.insert(keys,ColorSequenceKeypoint.new(i/6,Color3.fromHSV(i/6,.8,1))) end
 gradient(beam,keys)
 ui.frame(beam,"HotCore",UDim2.new(1,0,0,3),UDim2.fromOffset(0,4),Color3.new(1,1,1))
 for i=1,4 do
  local ring=ui.frame(hero,"EnergyRing",UDim2.fromOffset(14,42),UDim2.new(i/5,-7,0,122),accent)
  ring.BackgroundTransparency=1;stroke(ring,Color3.fromHSV(i/5,.5,1),2)
 end
 ui.label(hero,"Unlock the hue picker. Yellow is the base color; saved colors are kept.",UDim2.new(1,-32,0,narrow and 42 or 30),UDim2.fromOffset(16,167),13,soft)
 purchaseButton(Catalog.Get("Spectrum"),hero,data.spectrumPass,data,ui,action,UDim2.new(1,-32,0,44),UDim2.fromOffset(16,narrow and 238 or 206))
 for index,key in ipairs({"XP","Coins"}) do
  local item=Catalog.Get(key);local tint=key=="XP" and violet or gold
  local c=ui.card(narrow and 244 or 210);c.Name="Boost"..key;stroke(c,tint)
  local badge=ui.frame(c,"Multiplier",UDim2.fromOffset(54,54),UDim2.fromOffset(16,16),ink)
  local badgeText=ui.label(badge,"2×",UDim2.fromScale(1,1),UDim2.new(),27,tint);badgeText.TextXAlignment=Enum.TextXAlignment.Center;badgeText.Font=Enum.Font.GothamBlack
  ui.label(c,"0"..(index+1).." / "..item.tag,UDim2.new(1,-100,0,20),UDim2.fromOffset(84,13),12,tint)
  ui.label(c,item.name,UDim2.new(1,-100,0,32),UDim2.fromOffset(84,34),narrow and 18 or 22)
  ui.label(c,item.description.." Starts automatically on confirmed delivery.",UDim2.new(1,-32,0,narrow and 56 or 40),UDim2.fromOffset(16,80),14,soft)
  local shop=data.shop or {};local inventory=shop.inventory or {};local ends=shop.ends or {}
  local status=ui.label(c,shop.ready==true and "Not active" or "Boost status unavailable",UDim2.new(1,-32,0,24),UDim2.fromOffset(16,narrow and 143 or 124),13,tint)
  table.insert(timers,{label=status,ready=shop.ready==true,ends=ends[item.boost] or 0,serverNow=shop.serverNow or os.time(),received=os.clock()})
  local y=narrow and 184 or 158
  local count=inventory[item.boost] or 0
  purchaseButton(item,c,false,data,ui,action,UDim2.new(count>0 and .5 or 1,count>0 and -22 or -32,0,44),UDim2.fromOffset(16,y))
  if count>0 then
   local revision=generation;local b
   b=ui.button(c,"Activate"..key,"USE SAVED ("..count..")",UDim2.new(.5,-22,0,44),UDim2.new(.5,6,0,y),function()
    if revision==generation and b and b.Parent and shop.ready then action:FireServer("ActivateBoost",item.boost) end
   end,ink);b.TextSize=13;b.TextColor3=tint;b.AutoButtonColor=shop.ready==true
  end
 end
 local movement=ui.card(narrow and 202 or 170);stroke(movement,accent)
 ui.label(movement,"04 / FREERUNNER",UDim2.new(1,-32,0,28),UDim2.fromOffset(16,12),20,accent)
 ui.label(movement,"Chain jumps and rolls through the safe city. Standard movement rules apply inside the PvP arena.",UDim2.new(1,-32,0,narrow and 70 or 48),UDim2.fromOffset(16,48),14,soft)
 purchaseButton(Catalog.Get("Movement"),movement,data.movementPass,data,ui,action,UDim2.new(1,-32,0,44),UDim2.fromOffset(16,narrow and 142 or 110))
 ui.info("New boosts activate automatically on confirmed delivery and stack time, not multiplier. Previously saved boosts remain usable.")
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
 local code=ui.label(c,"",UDim2.new(1,-32,0,24),UDim2.fromOffset(16,186),13,soft);code.Name="SelectedColor"
 local function update()
  code.Text="Selected color #"..color:ToHex():upper()
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
