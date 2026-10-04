local Lifecycle=require('../src/ReplicatedStorage/Shared/QuestLifecycle')
local function definition(id) if id=='garden' then return {goal=3} end end
local function session(progress,claimed)
 return {activeQuest='garden',data={quests={garden={progress=progress,claimed=claimed}}},questDeadline=123,carrying=true,raceStart=100,collected={bed1=true}}
end
local a=session(1,false);Lifecycle.Clear(a,definition)
assert(a.data.quests.garden.progress==0 and not a.activeQuest and not a.questDeadline and not a.carrying and not a.raceStart and next(a.collected)==nil)
local b=session(3,false);Lifecycle.Clear(b,definition);assert(b.data.quests.garden.progress==3 and not b.data.quests.garden.claimed)
local c=session(3,true);Lifecycle.Clear(c,definition);assert(c.data.quests.garden.claimed and c.data.quests.garden.progress==3)
Lifecycle.Clear(a,definition);assert(a.data.quests.garden.progress==0)
local d=session(1,false);d.activeQuest='removed';Lifecycle.Clear(d,definition);assert(d.data.quests.garden.progress==1 and d.activeQuest==nil)
print('PASS 5 quest lifecycle scenarios')
