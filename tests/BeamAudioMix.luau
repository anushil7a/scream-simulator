local Mix=require("../src/StarterPlayer/StarterPlayerScripts/BeamAudioMix")
local settings=require("../src/ReplicatedStorage/Shared/AttackAudioConfig")
local created,destroyed,checks=0,0,0
local handles={}
local function check(ok,message) assert(ok,message);checks+=1 end
local function new()
 return Mix.new(settings,function()
  created+=1;local h={};table.insert(handles,h);return h
 end,function(h,position,volume,pitch) h.position=position;h.volume=volume;h.pitch=pitch end,
 function(h) check(not h.destroyed,"Double destruction");h.destroyed=true;destroyed+=1 end)
end
local mix=new()
check(mix:Pulse(1,0,10,true),"Local attack did not allocate")
mix:Step(.1,.1,false);local first=handles[1]
check(first.volume>0 and first.volume<=settings.TotalVolume*settings.LocalMultiplier,"Local gain cap")
check(first.pitch==1,"Supplied recording pitch changed")
mix:Pulse(1,.2,20,true);mix:Step(.2,.1,false)
check(created==1 and first.position==20,"Pulse restarted sound or lost position")
for i=2,settings.Limit do check(mix:Pulse(i,.2,i,false),"Concurrent sound rejected early") end
check(not mix:Pulse(99,.2,99,false) and created==settings.Limit,"Unbounded simultaneous sound count")
mix:Step(.35,.15,false)
local total=0;for _,h in ipairs(handles) do total+=h.volume end
check(total<=settings.TotalVolume,"Overlaps multiplied mix volume")
mix:Step(.36,.01,false,true)
check(first.volume==0,"Calibration heard attack SFX")
mix:Step(.37,.01,false,false)
local before=first.volume;mix:Step(.4,.05,true)
check(first.volume<before,"Local speaking did not duck effects")
mix:Stop(1,.4);mix:Stop(1,.45);mix:Step(.48,.08,true)
check(first.pitch==1 and first.volume<before,"Release did not soften or altered pitch")
check(not mix:Pulse(1,.49,30,true),"Late pulse revived stopped sound")
mix:Step(.57,.09,true)
check(first.destroyed and mix.count==settings.Limit-1,"Release failed cleanup")
mix:Step(2,.1,false)
check(mix.count==0 and destroyed==created,"Missing end packet leaked sound")
check(mix:Pulse(2,3,0,false),"New attack after cleanup rejected")
mix:SetEnabled(false)
check(mix.count==0 and not mix:Pulse(3,3,0,false),"SFX mute retained/recreated sound")
mix:SetEnabled(true);check(mix:Pulse(3,4,0,false),"Reenable failed")
for i=1,24 do mix:Pulse(3,4+i*.2,0,false);mix:Step(4+i*.2,.2,false) end
check(mix.count==0,"Maximum lifetime did not bound continuous updates")
mix:Pulse(4,10,0,false);mix:Remove(4);mix:Remove(4)
check(mix.count==0,"Departure cleanup underflow")
mix:Pulse(5,11,0,false);mix:Clear();check(mix.count==0,"Respawn retained audio")
mix:Destroy();mix:Destroy();mix:SetEnabled(true)
check(not mix:Pulse(6,12,0,false),"Queued event recreated destroyed mixer")
local unavailable=Mix.new(settings,function()return nil end,function()error("Unexpected update")end,function()error("Unexpected destruction")end)
check(not unavailable:Pulse(1,0,0,true) and unavailable.count==0,"Unconfigured asset allocated an entry")
unavailable:Step(1,.1,true);unavailable:Destroy()
print("PASS "..checks.." attack audio mix checks; synthetic handles, no listening evidence")
