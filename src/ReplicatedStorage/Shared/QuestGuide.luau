-- Short current-step directions for the HUD; never grants progress or rewards.
local Guide={}
function Guide.Step(quest,progress,carrying,racing,soccerDetail)
 if not quest then return nil end
 if progress>=quest.goal then return "Complete · claim in Quests" end
 if quest.id=="nick" then return soccerDetail or "Return to Nick's coastal court" end
 if quest.id=="delivery" then return carrying and "Deliver to the boardwalk music stage" or "Pick up coffee at the west promenade" end
 if quest.id=="sprint" then return racing and "Run east along the promenade!" or "Start beside the lifeguard tower" end
 local directions={
  garden="Water flowerbeds in Rambla Gardens",
  beach="Collect bottles along the beach",
  crowd="Line up 3 residents in one beam",
  dodge="Dodge enemy beams in the arena",
  arena="KO an equal/higher-level arena player",
 }
 return directions[quest.id] or quest.description
end
return Guide
