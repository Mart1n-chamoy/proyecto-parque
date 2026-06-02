#!/bin/bash
# Script para probar los endpoints de proyecto-parque

BASE_URL="http://localhost:8000/api"

echo "🚀 Iniciando pruebas de endpoints..."

# 1. Crear cliente
echo -e "\n=== 1. Crear Cliente ===" 
curl -X POST $BASE_URL/clients/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Carlos",
    "last_name": "García",
    "phone": "+54921111111",
    "email": "carlos@example.com",
    "debt_amount": "3000.00"
  }'

# 2. Listar clientes
echo -e "\n\n=== 2. Listar Clientes ===" 
curl $BASE_URL/clients/

# 3. Crear lote
echo -e "\n\n=== 3. Crear Lote de Llamadas ===" 
curl -X POST $BASE_URL/calls/batches/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lote Prueba",
    "description": "Prueba de sistema",
    "total_clients": 1
  }'

# 4. Crear llamada
echo -e "\n\n=== 4. Crear Llamada ===" 
curl -X POST $BASE_URL/calls/ \
  -H "Content-Type: application/json" \
  -d '{
    "batch": 1,
    "client": 1,
    "status": "pending"
  }'

# 5. Listar llamadas pendientes
echo -e "\n\n=== 5. Listar Llamadas Pendientes ===" 
curl $BASE_URL/calls/pending/

# 6. Iniciar lote
echo -e "\n\n=== 6. Iniciar Lote ===" 
curl -X POST $BASE_URL/calls/batches/1/start/

# 7. Desactivar cliente
echo -e "\n\n=== 7. Desactivar Cliente ===" 
curl -X POST $BASE_URL/clients/1/deactivate/

echo -e "\n\n✅ Pruebas completadas!"
