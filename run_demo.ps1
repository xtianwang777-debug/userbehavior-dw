param([switch]$Demo)
$ErrorActionPreference='Stop'
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$Py=$env:PYSPARK_PYTHON
if(-not $Py){$Py=Join-Path $Root '.venv\Scripts\python.exe'}
if(-not (Test-Path $Py)){$Py=(Get-Command python -ErrorAction Stop).Source}
$Jre=Get-ChildItem (Join-Path $Root 'tools') -Directory -ErrorAction SilentlyContinue | Where-Object {$_.Name -like 'jdk-*' -or $_.Name -like 'jre-*'} | Select-Object -First 1
if(-not $env:JAVA_HOME -and $Jre){$env:JAVA_HOME=$Jre.FullName}
if(-not $env:JAVA_HOME){Write-Warning 'JAVA_HOME is not set; install Java 8/11/17 before running Spark.'} else {$env:PATH="$env:JAVA_HOME\bin;$env:PATH"}
$Hadoop=Join-Path $Root 'tools\hadoop'
if(Test-Path $Hadoop){$env:HADOOP_HOME=$Hadoop; $env:HADOOP_HOME_DIR=$Hadoop; $env:PATH="$Hadoop\bin;$env:PATH"}
$env:PYSPARK_PYTHON=$Py
$env:PYSPARK_DRIVER_PYTHON=$Py
function Run-Step([string]$script, [string[]]$args) {
  & $Py (Join-Path $Root $script) @args
  if($LASTEXITCODE -ne 0){ throw "step failed: $script" }
}
if($Demo -or -not (Test-Path (Join-Path $Root 'data\raw\UserBehavior.csv'))){
  Run-Step 'src\00_generate_demo.py' @('--rows','120000')
} else { Write-Output 'USE_EXISTING_RAW_DATA' }
Run-Step 'src\01_ods_load.py' @()
Run-Step 'src\02_dwd_clean.py' @()
Run-Step 'src\03_dws_agg.py' @('--shuffle','400')
Run-Step 'src\04_ads_metrics.py' @()
Run-Step 'src\05_cross_validate.py' @()
Run-Step 'src\07_validate.py' @()
Run-Step 'src\08_tuning_benchmark.py' @()
Run-Step 'src\06_charts.py' @()
Write-Output 'DEMO_PIPELINE_PASS'
