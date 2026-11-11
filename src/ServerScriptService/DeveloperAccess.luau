local Access = {}

-- This is the account that owns the published Scream Simulator experience.
-- Studio is supplied by server RunService, never by a client argument.
-- The client only receives visibility; every test command is checked again here.
Access.OwnerUserId = 11499795799

function Access.IsAuthorized(player, creatorType, creatorId, isStudio)
    return player ~= nil and (isStudio == true or (player.UserId == Access.OwnerUserId
        and creatorType == Enum.CreatorType.User
        and creatorId == Access.OwnerUserId))
end

return Access
