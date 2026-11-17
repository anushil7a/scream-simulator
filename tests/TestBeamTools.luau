-- Actual input controller with synthetic clocks/state. No native input/audio claim.
local Tools=require("../src/StarterPlayer/StarterPlayerScripts/TestBeamTools")
local n=0;local function check(ok,message) assert(ok,message);n+=1 end
local now=1;local allowed=true;local aim=true;local calls={}
local state={testBeamAvailable=true,testBeamActive=false,testBeamCooldown=0,testBeamPower=0}
local tool=Tools.new({now=function()return now end,state=function()return state end,allowed=function()return allowed end,
 aim=function(power) return aim and {power=power} or nil end,
 send=function(verb,payload)table.insert(calls,{verb,payload})end})
local function last()return calls[#calls]end
check(tool.power==50 and not tool.running,'Default is not idle50')
for _,p in ipairs({0,10,50,100})do tool:SetPower(p);check(tool.power==p,'Power selection failed')end
tool:SetPower(-99);check(tool.power==0,'Negative power');tool:SetPower(999);check(tool.power==100,'Excess power')
tool:SetPower(22.8);check(tool.power==23,'Power not rounded');tool:SetPower(0/0);tool:SetPower('100');check(tool.power==23,'Malformed power accepted')
tool:SetPower(0);tool:Toggle();check(#calls==0,'Zero fired')
tool:SetPower(50);allowed=false;tool:Toggle();check(#calls==0,'Disallowed fired');allowed=true
state.testBeamAvailable=false;tool:Toggle();check(#calls==0,'Unavailable fired');state.testBeamAvailable=true
state.testBeamCooldown=1;tool:Toggle();check(#calls==0,'Cooldown fired');state.testBeamCooldown=0
aim=false;tool:Toggle();check(#calls==0,'Missing camera fired');aim=true
tool:Toggle();check(tool.running and last()[1]=='TestBeamBegin' and last()[2].power==50 and last()[2].aim.power==.5,'Begin payload')
local count=#calls;tool:Tick();check(#calls==count,'Too fast pulse')
now+=.11;tool:Tick();check(last()[1]=='TestBeamPulse','Missing pulse while ack pending')
state.testBeamActive=true;tool:Tick();check(tool.acknowledged,'Ack ignored')
tool:SetPower(70);now+=.11;tool:Tick();check(last()[2].power==70,'Updated power not sent')
tool:SetPower(0);check(not tool.running and last()[1]=='TestBeamStop','Zero did not stop');count=#calls;tool:Tick();tool:Stop();check(#calls==count,'Repeated stop leaked')
state.testBeamActive=false;tool:SetPower(100);tool:Toggle();now+=.51;tool:Tick();check(not tool.running and last()[1]=='TestBeamStop','Unacknowledged timeout')
for _,interrupt in ipairs({'focus/menu/panel/flight','permission','server stop','four seconds','missing camera'})do
 allowed=true;state.testBeamAvailable=true;state.testBeamActive=false;aim=true
 tool:Toggle();state.testBeamActive=true;tool:Tick()
 if interrupt=='focus/menu/panel/flight' then allowed=false
 elseif interrupt=='permission' then state.testBeamAvailable=false
 elseif interrupt=='server stop' then state.testBeamActive=false
 elseif interrupt=='four seconds' then now+=4
 elseif interrupt=='missing camera' then aim=false;now+=.11 end
 tool:Tick();check(not tool.running and last()[1]=='TestBeamStop','Failed interruption: '..interrupt)
 count=#calls;now+=1;tool:Tick();check(#calls==count,'Automatically resumed: '..interrupt)
end
print('PASS '..n..' actual silent Test Beam input checks; synthetic clocks/state')
