# Script para probar los endpoints de proyecto-parque en PowerShell

$BASE_URL = "http://localhost:8000/api"

Write-Host "🚀 Iniciando pruebas de endpoints..." -ForegroundColor Green

# 1. Crear cliente
Write-Host "`n=== 1. Crear Cliente ===" -ForegroundColor Cyan
$clientData = @{
    first_name = "Carlos"
    last_name = "García"
    phone = "+54921111111"
    email = "carlos@example.com"
    debt_amount = "3000.00"
} | ConvertTo-Json

curl -X POST "$BASE_URL/clients/" `
  -H "Content-Type: application/json" `
  -d $clientData | ConvertFrom-Json | ConvertTo-Json

# 2. Listar clientes
Write-Host "`n=== 2. Listar Clientes ===" -ForegroundColor Cyan
curl "$BASE_URL/clients/" | ConvertFrom-Json | ConvertTo-Json

# 3. Crear lote
Write-Host "`n=== 3. Crear Lote de Llamadas ===" -ForegroundColor Cyan
$batchData = @{
    name = "Lote Prueba"
    description = "Prueba de sistema"
    total_clients = 1
} | ConvertTo-Json

curl -X POST "$BASE_URL/calls/batches/" `
  -H "Content-Type: application/json" `
  -d $batchData | ConvertFrom-Json | ConvertTo-Json

# 4. Crear llamada
Write-Host "`n=== 4. Crear Llamada ===" -ForegroundColor Cyan
$callData = @{
    batch = 1
    client = 1
    status = "pending"
} | ConvertTo-Json

curl -X POST "$BASE_URL/calls/" `
  -H "Content-Type: application/json" `
  -d $callData | ConvertFrom-Json | ConvertTo-Json

# 5. Listar llamadas pendientes
Write-Host "`n=== 5. Listar Llamadas Pendientes ===" -ForegroundColor Cyan
curl "$BASE_URL/calls/pending/" | ConvertFrom-Json | ConvertTo-Json

# 6. Iniciar lote
Write-Host "`n=== 6. Iniciar Lote ===" -ForegroundColor Cyan
curl -X POST "$BASE_URL/calls/batches/1/start/" | ConvertFrom-Json | ConvertTo-Json

# 7. Desactivar cliente
Write-Host "`n=== 7. Desactivar Cliente ===" -ForegroundColor Cyan
curl -X POST "$BASE_URL/clients/1/deactivate/" | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n✅ Pruebas completadas!" -ForegroundColor Green
