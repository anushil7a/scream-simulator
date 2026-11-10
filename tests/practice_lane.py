"""Authored practice-line distance versus actual level-one voice rules (synthetic geometry)."""
from pathlib import Path
import re
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
city=(root/'src/ServerScriptService/City.luau').read_text()
distance=float(re.search(r'"StandLine",V\(10,\.04,\.35\),V\(tx,\.96,tz\+(\d+)\)',city)[1])
code=f'''
local Combat=require("../src/ReplicatedStorage/Shared/VoiceCombat")
local Gate=require("../src/ReplicatedStorage/Shared/VoiceActivation")
local range=Combat.Stats(1,Gate.OnPower,false).range
assert({distance}<=range,"Practice stand is "..({distance}).." studs away but level-one onset beam reaches only "..range)
-- Reserve two studs for aim height/origin offset at the lower sustain threshold.
assert({distance}+2<=Combat.Stats(1,Gate.OffPower,false).range,"Practice lane lacks a lower-power aiming margin")
print("PASS practice line is inside level-one onset and sustained reach with aiming margin")
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(code)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
