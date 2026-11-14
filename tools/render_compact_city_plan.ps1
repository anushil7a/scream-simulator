# Offline diagnostic plan from draft data, not a Roblox screenshot.
param([string]$Root = (Split-Path -Parent $PSScriptRoot))
Add-Type -AssemblyName System.Drawing
$layout = Get-Content -Raw -LiteralPath (Join-Path $Root 'prototypes/compact-city/layout.json') | ConvertFrom-Json
$bitmap = [System.Drawing.Bitmap]::new(1080,740)
$g = [System.Drawing.Graphics]::FromImage($bitmap)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$font = [System.Drawing.Font]::new('Arial',11)
$title = [System.Drawing.Font]::new('Arial',19,[System.Drawing.FontStyle]::Bold)
$ink = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(30,48,54))
$line = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(45,122,193),2)
$line.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash
try {
 $g.Clear([System.Drawing.Color]::FromArgb(248,246,239))
 $g.DrawString('COMPACT CITY / DRAFT 01',$title,$ink,20,16)
 $g.DrawString('720 x 600 studs | 75% less footprint | geometry only, NOT a gameplay build',$font,$ink,20,49)
 foreach($p in ($layout.parts | Sort-Object { $_.position[1] + $_.size[1]/2 })) {
  $brush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb([int]$p.color[0],[int]$p.color[1],[int]$p.color[2]))
  try {$g.FillRectangle($brush,[single](20+$p.position[0]+360-$p.size[0]/2),[single](88+$p.position[2]+300-$p.size[2]/2),[single]$p.size[0],[single]$p.size[2])} finally {$brush.Dispose()}
 }
 foreach($route in $layout.routes) {
  for($i=1;$i -lt $route.points.Count;$i++) {$g.DrawLine($line,[single](20+$route.points[$i-1][0]+360),[single](88+$route.points[$i-1][1]+300),[single](20+$route.points[$i][0]+360),[single](88+$route.points[$i][1]+300))}
 }
 $i=0
 foreach($a in $layout.anchors) {
  $i++;$x=[single](20+$a.position[0]+360);$y=[single](88+$a.position[2]+300)
  $g.FillEllipse([System.Drawing.Brushes]::White,$x-9,$y-9,18,18)
  $g.DrawString([string]$i,$font,$ink,$x-7,$y-8)
  $g.DrawString(($i.ToString()+'. '+$a.id),$font,$ink,762,(100+29*($i-1)))
 }
 $g.DrawString('NORTH is up. Blue = reserved routes.',$font,$ink,20,704)
 $g.DrawString('Native collision, visual quality, combat,',$font,$ink,762,620)
 $g.DrawString('quests and saves are NOT validated.',$font,$ink,762,642)
 $out=Join-Path $Root 'build/CompactCityPlan.png';$bitmap.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
 Write-Output $out
} finally {$line.Dispose();$ink.Dispose();$font.Dispose();$title.Dispose();$g.Dispose();$bitmap.Dispose()}
