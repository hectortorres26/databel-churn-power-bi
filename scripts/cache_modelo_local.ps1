param(
 [Parameter(Mandatory=$true)][int]$Port,
 [Parameter(Mandatory=$true)][string]$DependencyPath
)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
foreach($assembly in @('core','tabular')){[Reflection.Assembly]::LoadFrom((Join-Path $DependencyPath "microsoft.analysisservices.$assembly.dll")) | Out-Null}
$server=New-Object Microsoft.AnalysisServices.Tabular.Server
try {
 $server.Connect("localhost:$Port")
 $models=@($server.Databases | Where-Object {$_.Model.Tables.Name -contains 'Databel - Data'})
 if($models.Count -ne 1){throw 'No hay un único modelo Databel.'}
 $table=$models[0].Model.Tables.Find('Databel - Data')
 if($table.Measures.Count -ne 9 -or $table.Columns.Find('Phone Number')){throw 'El modelo no corresponde a la adaptación esperada.'}
 $dir=Join-Path $root 'powerbi/DatabelPresentacion/Databel.SemanticModel/.pbi'
 New-Item -ItemType Directory -Path $dir -Force | Out-Null
 $file=Join-Path $dir 'cache.abf'
 if(Test-Path -LiteralPath $file){throw 'Ya existe una caché; no se sobrescribe.'}
 $stream=[IO.File]::Create($file)
 try {$server.ImageSave($models[0].ID,$stream)}finally{$stream.Dispose()}
 Write-Output 'Cache local del modelo guardada. Excluida de Git.'
}finally{$server.Disconnect()}
