-- Pure purchase transactions; receipt IDs are never evicted. Fail closed at cap.
local Ledger={Duration=1800,ReceiptLimit=8000}
local function integer(n,maximum)
 return type(n)=="number" and n==n and math.clamp(math.floor(n),0,maximum) or 0
end
function Ledger.Normalize(raw)
 raw=type(raw)=="table" and raw or {}
 local d={inventory={},ends={},receipts={},operations={}}
 for _,kind in ipairs({"xp","coins"}) do
  d.inventory[kind]=integer(type(raw.inventory)=="table" and raw.inventory[kind],1000000)
  d.ends[kind]=integer(type(raw.ends)=="table" and raw.ends[kind],100000000000)
 end
 for id,value in pairs(type(raw.receipts)=="table" and raw.receipts or {}) do
  if type(id)=="string" and #id<=128 and value==true then d.receipts[id]=true end
 end
 for id,expires in pairs(type(raw.operations)=="table" and raw.operations or {}) do
  if type(id)=="string" and #id<=128 and type(expires)=="number" then d.operations[id]=expires end
 end
 return d
end
function Ledger.Grant(raw,receipt,kind)
 local d=Ledger.Normalize(raw)
 if type(receipt)~="string" or #receipt==0 or #receipt>128 or d.inventory[kind]==nil then return nil,"invalid" end
 if d.receipts[receipt] then return d,"duplicate" end
 local count=0;for _ in pairs(d.receipts) do count+=1 end
 if count>=Ledger.ReceiptLimit or d.inventory[kind]>=1000000 then return nil,"capacity" end
 d.receipts[receipt]=true;d.inventory[kind]+=1
 return d,"granted"
end
function Ledger.Activate(raw,kind,operation,started,now)
 local d=Ledger.Normalize(raw)
 if d.inventory[kind]==nil or now-started>60 or now<started then return nil,"invalid" end
 if d.operations[operation] then return d,"duplicate" end
 for id,expires in pairs(d.operations) do if now>=expires then d.operations[id]=nil end end
 if d.inventory[kind]<1 then return nil,"empty" end
 d.inventory[kind]-=1;d.ends[kind]=math.max(now,d.ends[kind])+Ledger.Duration
 d.operations[operation]=now+120
 return d,"activated"
end
function Ledger.Multiplier(d,kind,now)
 return d and d.ends and type(d.ends[kind])=="number" and now<d.ends[kind] and 2 or 1
end
return Ledger
