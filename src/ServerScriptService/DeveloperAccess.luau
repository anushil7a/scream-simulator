local Access = {}

-- This is the account that owns the published Scream Simulator experience.
-- The client only receives a visibility flag; every cheat is checked again on the server.
Access.PublicTestingEnabled = true
Access.OwnerUserId = 11499795799

function Access.IsAuthorized(player, creatorType, creatorId)
    return (Access.PublicTestingEnabled and player ~= nil) or (player ~= nil
        and player.UserId == Access.OwnerUserId
        and creatorType == Enum.CreatorType.User
        and creatorId == Access.OwnerUserId)
end

return Access
