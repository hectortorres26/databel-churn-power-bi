param(
 [Parameter(Mandatory=$true)][int]$Port,
 [Parameter(Mandatory=$true)][string]$DependencyPath,
 [string]$ProjectRoot=(Split-Path $PSScriptRoot -Parent)
)
$ErrorActionPreference='Stop'
foreach($assembly in @('core','tabular','adomdclient')) {
 [Reflection.Assembly]::LoadFrom((Join-Path $DependencyPath "microsoft.analysisservices.$assembly.dll")) | Out-Null
}
$server=New-Object Microsoft.AnalysisServices.Tabular.Server
$connection=$null
try {
 $server.Connect("localhost:$Port")
 $matches=@($server.Databases | Where-Object { $_.Model.Tables.Name -contains 'Databel - Data' })
 if($matches.Count -ne 1){throw 'No se identifico un unico modelo Databel; no se ejecutaron consultas.'}
 $database=$matches[0];$table=$database.Model.Tables.Find('Databel - Data')
 if(@($table.Partitions | Where-Object State -NE 'Ready').Count){throw 'Hay particiones sin cargar.'}
 $definitionPath=Join-Path $ProjectRoot 'powerbi/Databel/Model/database.json'
 $definition=Get-Content -Raw -Encoding UTF8 -LiteralPath $definitionPath | ConvertFrom-Json
 $expectedTable=$definition.model.tables | Where-Object name -EQ 'Databel - Data'
 foreach($measure in $expectedTable.measures){
  $live=$table.Measures.Find($measure.name)
  if(-not $live -or ($live.Expression.Trim() -ne $measure.expression.Trim())){throw "Medida distinta de la fuente: $($measure.name)"}
 }
 foreach($column in $expectedTable.columns){
  if(-not $table.Columns.Find($column.name)){throw "Columna ausente: $($column.name)"}
 }
 if($table.Columns.Find('Phone Number')){throw 'El modelo conserva el telefono.'}
 $expectedM=($expectedTable.partitions[0].source.expression -join "`n").Replace("`r",'').Trim()
 if($table.Partitions[0].Source.Expression.Replace("`r",'').Trim() -ne $expectedM){throw 'Power Query no coincide con la definicion del proyecto.'}
 $spec=Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $ProjectRoot 'output/pruebas_motor_esperadas.json') | ConvertFrom-Json
 $connection=New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$Port;Initial Catalog=$($database.ID)")
 $connection.Open()
 function Read-Query([string]$query) {
  $cmd=$connection.CreateCommand();$cmd.CommandTimeout=60;$cmd.CommandText=$query
  $rd=$cmd.ExecuteReader();$rows=@()
  try {while($rd.Read()){$item=[ordered]@{};for($i=0;$i -lt $rd.FieldCount;$i++){$v=$rd.GetValue($i);if($v -is [DBNull]){$v=$null};$item[$rd.GetName($i)]=$v};$rows+=[pscustomobject]$item}}
  finally{$rd.Close()}
  return ,$rows
 }
 function Equal-Value($expected,$actual) {
  if($null -eq $expected){return $null -eq $actual}
  if($null -eq $actual){return $false}
  return [Math]::Abs([double]$expected-[double]$actual) -lt 0.00000001
 }
 $filterResults=@();$visualResults=@();$failures=@()
 foreach($case in $spec.filter_cases) {
  $fields=@($case.expected.PSObject.Properties | ForEach-Object { '"'+$_.Name+'", ['+$_.Name+']' })
  $row='ROW('+($fields -join ', ')+')'
  $conditions=@($case.filters.PSObject.Properties | ForEach-Object { '''Databel - Data''['+$_.Name+'] = "'+$_.Value.Replace('"','""')+'"' })
  $query='EVALUATE '+$row
  if($conditions.Count){$query='EVALUATE CALCULATETABLE('+$row+', '+($conditions -join ', ')+')'}
  $rows=Read-Query $query;$actual=$rows[0];$ok=$true
  foreach($p in $case.expected.PSObject.Properties){if(-not (Equal-Value $p.Value $actual.PSObject.Properties[('['+$p.Name+']')].Value)){$ok=$false;$failures+=$case.name+': '+$p.Name}}
  $filterResults+=@{name=$case.name;filters=$case.filters;status=$(if($ok){'OK'}else{'ERROR'});values=$actual}
 }
 foreach($case in $spec.visual_cases) {
  $query='EVALUATE SUMMARIZECOLUMNS(''Databel - Data''['+$case.column+'], "Valor", ['+$case.measure+'])'
  $rows=Read-Query $query;$actual=@{}
  foreach($row in $rows){$props=@($row.PSObject.Properties);$actual[[string]$props[0].Value]=$props[1].Value}
  $ok=$actual.Count -eq $case.expected.Count
  foreach($expected in $case.expected){if(-not $actual.ContainsKey($expected.category) -or -not (Equal-Value $expected.value $actual[$expected.category])){$ok=$false}}
  if(-not $ok){$failures+=$case.name}
  $visualResults+=@{name=$case.name;column=$case.column;measure=$case.measure;categories=$actual.Count;status=$(if($ok){'OK'}else{'ERROR'})}
 }
 $sha=[Security.Cryptography.SHA256]::Create()
 $modelHash=([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes([IO.File]::ReadAllText($definitionPath).Replace("`r`n","`n"))))).Replace('-','').ToLower()
 $sha.Dispose()
 $result=[ordered]@{scope='Modelo propio cargado en Power BI Desktop; consultas de solo lectura';model_definition_sha256=$modelHash;hash_normalization='UTF-8 sin BOM, saltos LF';source_matches_loaded_model=$true;partitions_ready=$true;measures=$table.Measures.Count;filter_cases=$filterResults;visual_cases=$visualResults;failures=$failures;status=$(if($failures.Count){'ERROR'}else{'OK'});ui_validation='Pendiente: estas consultas no prueban clics, tooltips ni renderizado en Power BI.'}
 $result | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $ProjectRoot 'output/validacion_motor.json')
 @{status=$result.status;filters=$filterResults.Count;visuals=$visualResults.Count;failures=$failures} | ConvertTo-Json -Depth 4
 if($failures.Count){exit 1}
} finally {if($connection -and $connection.State -eq 'Open'){$connection.Close()};$server.Disconnect()}
