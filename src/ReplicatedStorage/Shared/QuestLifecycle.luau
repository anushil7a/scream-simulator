-- Reset an abandoned/switched attempt without discarding an earned, unclaimed reward.
local QuestLifecycle={}
function QuestLifecycle.Clear(session,getQuest)
 local id=session.activeQuest
 local definition=id and getQuest(id)
 local progress=id and session.data.quests[id]
 if definition and progress and not progress.claimed and progress.progress<definition.goal then progress.progress=0 end
 session.activeQuest=nil;session.questDeadline=nil;session.carrying=false;session.raceStart=nil;session.collected={}
end
return QuestLifecycle
