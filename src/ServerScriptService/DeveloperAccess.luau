local Access = {}

-- This is the account that owns the published Scream Simulator experience.
-- Studio is supplied by server RunService, never by a client argument.
-- The client only receives visibility; every test command is checked again here.
Access.OwnerUserId = 11499795799
-- Temporary owner-approved tester access. Disable before any public release.
-- Server-owned only: City Preview place 90337242377543 / universe 10769005350.
-- Verified cloud-reopen evidence: tests/evidence/city-preview-version14-2026-11-06.json.
Access.PrelaunchAllTesters = true
Access.PrelaunchUniverseIds = {[10769005350] = true}

function Access.IsAuthorized(player, creatorType, creatorId, isStudio, universeId)
    return player ~= nil and (isStudio == true or (creatorType == Enum.CreatorType.User
        and creatorId == Access.OwnerUserId
        and (player.UserId == Access.OwnerUserId or (Access.PrelaunchAllTesters == true
            and type(universeId) == "number" and universeId > 0 and universeId < math.huge
            and universeId % 1 == 0 and Access.PrelaunchUniverseIds[universeId] == true))))
end

return Access
