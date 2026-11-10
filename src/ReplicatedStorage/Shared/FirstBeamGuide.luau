-- Presentation only. Completion comes from a server-confirmed target hit.
local Guide = {}

function Guide.Text(data, armed, cooldown, active, touch)
    if data.activeQuest or (data.level or 1) > 1 or (data.achievements or {}).FirstBeam then
        return nil
    end
    if active then
        return "FIRST BEAM · 3/3\nKeep aiming at the practice target.\nGo quiet to stop."
    end
    if cooldown > 0 then
        return "FIRST BEAM · 2/3\nLet your voice rest during cooldown.\nAim at MIC PRACTICE beside spawn."
    end
    if not armed then
        local control = touch and "Tap ARM VOICE" or "Press E to arm your voice"
        return "FIRST BEAM · 1/3\n" .. control .. ".\nFind MIC PRACTICE beside spawn."
    end
    return "FIRST BEAM · 2/3\nAim at MIC PRACTICE beside spawn.\nGo quiet, then speak to fire."
end

return Guide
