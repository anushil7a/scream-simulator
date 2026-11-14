"""Hash-checked portable renderer baseline; no Git object or network dependency."""
from pathlib import Path
import hashlib
import json


def contact_renderer():
    folder = Path(__file__).resolve().parent / 'fixtures/nov13-contact-baseline'
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    assert manifest['originCommit'] == 'b76c94fafd65be4cec85f1c5f2caa4355262e43b'
    assert manifest['originPath'] == 'src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau'
    assert manifest['file'] == 'BeamVisuals.luau'
    data = (folder / 'BeamVisuals.luau').read_bytes()
    assert len(data) == manifest['bytes'] == 9006
    assert hashlib.sha256(data).hexdigest() == manifest['sha256'] == '2b274f82ae70814f4c2347d49edc83c9888b6f08b9eb977449e532c14c90c290'
    return data
