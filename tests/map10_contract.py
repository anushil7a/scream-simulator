"""Stdlib-only active Map10 contract checks. Geometry/engine QA is separate."""
import json,re,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];layout=(R/'src/ReplicatedStorage/Shared/CompactLayout.luau').read_text();old=(R/'prototypes/preserved-compact-city/CompactLayout.luau').read_text();geometry=json.loads((R/'prototypes/map10/geometry.json').read_text());parts=geometry['parts'];checks=0
def check(v,m):
 global checks
 assert v,m;checks+=1
check('MapId="Map10"' in layout,'active identity');check('require(script.Parent.Map10Geometry)' not in layout,'inline harness compatibility')
ids=lambda s:set(re.findall(r'id="([^"]+)",action=',s))
check(ids(layout)==ids(old),'quest IDs preserved')
check(len(parts)<1000,'static budget');check(len({p['id'] for p in parts})==len(parts),'unique geometry IDs')
for n,a,b,w in geometry['routes']:
 check(w>=26,n+' width');check(abs(a[1]-b[1])/math.hypot(a[0]-b[0],a[2]-b[2])<=.2,n+' grade')
for token in ['AcademyPavilion','ArenaTier','MusicTier','BranchLava','FloatingShrine','Chain','FootballLawn','DockMain','CliffFacet']:
 check(any(p['id'].startswith(token) for p in parts),'reference motif '+token)
check('Layout.ZoneMax=V(-240,14,210)' in layout,'safe upper terrace outside PvP')
check('position=V(-220,2,420)' in layout and 'position=V(220,2,420)' in layout,'unchanged440stud timed sprint')
for name,offset in [('Soccer',(25,54.5)),('Volley',(100,90))]:
 l=next(x for x in layout.splitlines() if x.startswith('Layout.'+name+'='));o=next(x for x in old.splitlines() if x.startswith('Layout.'+name+'='));vs=lambda t:[tuple(map(float,v.split(','))) for v in re.findall(r'V\(([^)]+)\)',t)];new=vs(l);prev=vs(o)
 check(len(new)==len(prev),name+' vectors preserved')
 for a,b in zip(new,prev):check(abs(a[0]-b[0]-offset[0])<.001 and a[1]==b[1] and abs(a[2]-b[2]-offset[1])<.001,name+' rigid relocation')
for q in parts:check(all(math.isfinite(v) for v in q['position']+q['size']+q['rotation']) and min(q['size'])>0,q['id']+' finite')
world=(R/'src/ServerScriptService/World.luau').read_text();check('(training.y or 0)+3.2' in world,'trainer grounding');check('nil,nil,spot.y' in world,'seed elevation');check('SupportingNPCs.AtHome' in world,'support placement adapter')
nav=(R/'src/ReplicatedStorage/Shared/NavigationCatalog.luau').read_text();check('(boss.y or 0)+3' in nav and '(landmark.y or 0)+3' in nav,'elevated guides')
check('home=Layout.BossHomes' in (R/'src/ReplicatedStorage/Shared/BossCatalog.luau').read_text(),'boss bindings')
print('PASS',checks,'Map10 contract checks (no native claims)')
