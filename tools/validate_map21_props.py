"""Blender roundtrip validation: blender -b --python tools/validate_map21_props.py."""
import bpy,json,pathlib,hashlib
from mathutils import Vector
root=pathlib.Path(__file__).resolve().parents[1]/'assets/drafts/map21-props'
m=json.loads((root/'manifest.json').read_text())
for a in m['assets']:
 p=root/a['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.gltf(filepath=str(p));bpy.context.view_layer.update()
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];vs=[o.matrix_world@Vector(v) for o in obs for v in o.bound_box]
 lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
 assert len(obs)==a['mesh_objects']
 assert all(abs(hi[i]-lo[i]-a['dimensions_studs'][i])<.001 for i in range(3)),(a['name'],lo,hi)
 assert abs(lo[2])<.001
 tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in obs)
 assert tris==a['triangles'] and tris<4000
 assert all(o.data.materials for o in obs)
 print('ROUNDTRIP_OK',a['name'],tris)
print('ALL_FOUR_GLB_ROUNDTRIPS_PASS')
