local Settings=require("../src/ReplicatedStorage/Shared/AttackAudioConfig")
local expected={
 [10]="112589551277234",[20]="71125574109613",[30]="72820033812084",
 [40]="116444869617367",[50]="110531388862916",[60]="72657289722275",
 [70]="8899285496",[80]="102380291908556",[90]="80523108386394",[100]="79853512837585",
}
local count=0
for level,id in pairs(expected) do
 assert(Settings.AssetForLevel(level)=="rbxassetid://"..id,"Wrong owner-selected audio at tier "..level)
 count+=1
end
local actual=0;for _ in pairs(Settings.AssetsByLevel) do actual+=1 end
assert(count==10 and actual==10,"Missing or unexpected audio tier")
assert(Settings.AssetForLevel(1)==nil and Settings.AssetForLevel(15)==nil and Settings.AssetForLevel(nil)==nil,"Unassigned tier played an unrelated sound")
print("PASS 12 exact owner audio mapping and unassigned-tier checks")
