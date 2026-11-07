-- Run in Edit after importing a repository-built city place, or after a cloud
-- reopen. Source hashes alone do not verify serialized service configuration.
local chat=game:GetService("TextChatService")
local voice=game:GetService("VoiceChatService")
assert(chat.ChatVersion==Enum.ChatVersion.TextChatService,"Legacy text chat is enabled")
assert(chat.CreateDefaultCommands and chat.CreateDefaultTextChannels,"Default chat commands/channels disabled")
assert(voice.UseAudioApi==Enum.AudioApiRollout.Enabled and voice.EnableDefaultVoice,"Live voice routing disabled")
assert(workspace.StreamingEnabled and workspace.StreamingTargetRadius==512,"City streaming configuration mismatch")
return {checks=4,placeId=game.PlaceId,version=game.PlaceVersion}
