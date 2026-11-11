"""Inline the actual engine-valued layout into Config fixture lexical mocks.
No replacement coordinates, fake catalog, service access or production mutation.
"""
def inline_compact_layout(config, root):
    needle='require(script.Parent:WaitForChild("CompactLayout"))'
    if needle not in config:
        return config  # Historical baseline predates the dependency.
    source=(root/'src/ReplicatedStorage/Shared/CompactLayout.luau').read_text(encoding='utf-8')
    assert config.count(needle)==1
    return config.replace(needle,'(function()\n'+source+'\nend)()')
