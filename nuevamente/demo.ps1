Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

$baseUrl = "http://127.0.0.1:8000"
$fixtureFile = "backend/tests/fixtures/sample_contenedores.md"
$tmpIngest = "tmp_ingest.json"

Write-Host "=== [1/4] Smoke Test: Verificando estado del servidor ===" -ForegroundColor Cyan
$health = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
Write-Host "Respuesta /health: $($health | ConvertTo-Json -Compress)"

if (-not (Test-Path $fixtureFile)) {
    Write-Host "[ERROR] No se encontro el archivo $fixtureFile" -ForegroundColor Red
    exit 1
}

# Ruta absoluta nativa de Windows
$fullPath = (Get-Item $fixtureFile).FullName

Write-Host "`n=== [2/4] Ingesta: Subiendo $fixtureFile ===" -ForegroundColor Cyan
curl.exe -X POST "$baseUrl/ingest" -F "file=@$fullPath" -o $tmpIngest

if (-not (Test-Path $tmpIngest) -or (Get-Item $tmpIngest).Length -eq 0) {
    Write-Host "[ERROR] No se pudo realizar la peticion /ingest o la respuesta esta vacia." -ForegroundColor Red
    exit 1
}

$ingestJson = Get-Content -Path $tmpIngest -Raw -Encoding UTF8
Write-Host "Respuesta /ingest: $ingestJson"

$ingestObj = $ingestJson | ConvertFrom-Json
$docId = $ingestObj.document_id

if (-not $docId) {
    Write-Host "[ERROR] No se obtuvo document_id de /ingest" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] document_id obtenido: $docId" -ForegroundColor Green

Write-Host "`n=== [3/4] Adaptacion: Solicitando adaptacion asincrona ===" -ForegroundColor Cyan
$bodyJson = @{
    document_id = $docId
    perfil = "Principiante / Transición de Carrera"
    formato = "Guía Práctica Paso a Paso (Tutorial)"
    nicho = "Fintech"
} | ConvertTo-Json -Compress

$adaptObj = Invoke-RestMethod -Uri "$baseUrl/adapt" -Method Post `
    -ContentType "application/json" -Body $bodyJson
Write-Host "Respuesta /adapt: $($adaptObj | ConvertTo-Json -Compress)"

$jobId = $adaptObj.job_id

if (-not $jobId) {
    Write-Host "[ERROR] No se obtuvo job_id de /adapt" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] job_id obtenido: $jobId" -ForegroundColor Green

Write-Host "`n=== [4/4] Polling: Consultando estado hasta finalizar ===" -ForegroundColor Cyan
$status = "PROCESSING"
$attempts = 0
$maxAttempts = 20

while ($status -eq "PROCESSING" -or $status -eq "QUEUED") {
    if ($attempts -ge $maxAttempts) {
        Write-Host "[ERROR] Timeout: El job no finalizo a tiempo." -ForegroundColor Red
        exit 1
    }
    Start-Sleep -Seconds 3
    $attempts++
    $jobResp = Invoke-RestMethod -Uri "$baseUrl/adapt/$jobId" -Method Get
    $status = $jobResp.status
    Write-Host "Consulta #$attempts - Status actual: $status"
}

# Limpieza de archivos temporales
Remove-Item $tmpIngest -ErrorAction SilentlyContinue

Write-Host "`n=========================================================================" -ForegroundColor Yellow
Write-Host "RESULTADO FINAL DE LA ADAPTACION (status: $status):" -ForegroundColor Yellow
Write-Host "=========================================================================" -ForegroundColor Yellow
$jobResp | ConvertTo-Json -Depth 10

if ($status -eq "SUCCESS") {
    Write-Host "`n[EXITO] La adaptacion finalizo correctamente: status = SUCCESS" -ForegroundColor Green
} elseif ($status -eq "PARTIAL") {
    Write-Host "`n[AVISO] La adaptacion finalizo en modo parcial/mock." -ForegroundColor Yellow
} else {
    Write-Host "`n[ERROR] La adaptacion no finalizo correctamente: status = $status" -ForegroundColor Red
}