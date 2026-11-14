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
assert(Settings.StarterFallback.Name=="se_battle_90","Wrong starter fallback name")
assert(Settings.FallbackForLevel(1)=="se_battle_90" and Settings.FallbackForLevel(9)=="se_battle_90","Wrong starter fallback for level 1-9")
assert(Settings.FallbackForLevel(10)=="rbxassetid://112589551277234","FallbackForLevel(10) did not return level 10 asset")
assert(Settings.FallbackForLevel(15)==nil,"FallbackForLevel(15) should be nil")
print("PASS 12 exact owner audio mapping and unassigned-tier checks")
