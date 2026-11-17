"""Emit a schematic of owner coordinates, deliberately not a terrain render."""
import html
import json
import sys
from pathlib import Path

root=Path(__file__).resolve().parent
data=json.loads((root/"layout.json").read_text())
zones=data["districts"]
built="--built" in sys.argv
world_paths=json.loads((root/"overworld_links.json").read_text()) if built else {}
colors=dict(zip(zones,["#66d5c3","#51b5dd","#f3af6f","#a9d680","#efc377","#b795f9","#f97757","#d4a1fc","#6bdcab"]))
X=lambda x: 102+(x+1600)*.213
Z=lambda z: 156+(z+1600)*.213
escape=html.escape
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1190" height="900" viewBox="0 0 1190 900">',
'<rect width="1190" height="900" rx="30" fill="#0b1722"/>',
'<g font-family="DejaVu Sans, sans-serif">',
'<text x="56" y="58" font-size="15" fill="#71dbc7" letter-spacing="3">SCREAM SIMULATOR / WORLD PLAN</text>',
'<text x="53" y="113" font-size="48" fill="#eff8f9" font-weight="bold">MAP–10 v2.1</text>',
'<rect x="102" y="156" width="681.6" height="681.6" fill="#0e2533" stroke="#355667"/>']
for p in range(-1600,1601,400):
    svg.append(f'<path d="M {X(p)} {Z(-1600)} V {Z(1600)} M {X(-1600)} {Z(p)} H {X(1600)}" fill="none" stroke="#2b4351" stroke-width="1"/>')
for a,b in data["plannedZone09Links"]:
    x,y,z=zones[a]["center"];u,v,w=zones[b]["center"]
    route=world_paths.get(a+"-"+b) or [(x,y,z),(u,v,w)]
    coords=" ".join(f"{X(px)},{Z(pz)}" for px,_,pz in route)
    dash="" if built else 'stroke-dasharray="6 7"'
    svg.append(f'<polyline points="{coords}" stroke="#b0d1d2" stroke-width="3.5" {dash} fill="none" opacity=".65"/>')
for i,(key,s) in enumerate(zones.items()):
    x,y,z=s["center"];w,d=s["size"];c=colors[key]
    svg.append(f'<rect x="{X(x-w/2)}" y="{Z(z-d/2)}" width="{w*.213}" height="{d*.213}" fill="#172c3a" stroke="{c}" stroke-width="{4 if key=="05" else 1.7}" rx="5"/>')
    svg.append(f'<text x="{X(x)}" y="{Z(z)+7}" text-anchor="middle" fill="{c}" font-size="22" font-weight="bold">{key}</text>')
    p=224+i*56
    svg.append(f'<rect x="823" y="{p-17}" width="33" height="29" rx="5" fill="{c}"/>')
    svg.append(f'<text x="840" y="{p+4}" text-anchor="middle" fill="#10212c" font-size="14" font-weight="bold">{key}</text>')
    svg.append(f'<text x="870" y="{p}" fill="#f4f9fa" font-size="17" font-weight="bold">{escape(s["name"])}</text>')
    stage=" • PREVIEW" if key=="05" and not built else ""
    svg.append(f'<text x="870" y="{p+18}" fill="#94b1bf" font-size="13">Y {y} · Lv {s["level"][0]}–{s["level"][1]}{stage}</text>')
svg.extend([
'<text x="823" y="180" font-size="15" fill="#8be2d4" letter-spacing="1.6">DISTRICTS / ELEVATION</text>',
'<line x1="823" y1="757" x2="849" y2="757" stroke="#a8c5ce" stroke-dasharray="6 5" stroke-width="3"/>',
'<text x="862" y="762" fill="#d1e2e8" font-size="15">Zone 09 planned transit links</text>',
'<text x="823" y="803" fill="#98b3bf" font-size="15">3,200 × 3,200 studs · X / Z</text>',
'<text x="823" y="827" fill="#98b3bf" font-size="15">Schematic, not playable terrain</text>',
'</g></svg>'])
if built:
    svg=[line.replace('stroke-dasharray="6 5"','').replace('planned transit links','built transit links').replace('Schematic, not playable terrain','Standalone Studio review') for line in svg]
out=root.parents[1]/"build"/"map21"/("Overworld-Layout.svg" if built else "Master-Layout.svg")
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text("\n".join(svg))
