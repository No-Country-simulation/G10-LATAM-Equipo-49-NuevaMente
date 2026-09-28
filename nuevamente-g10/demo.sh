#!/bin/bash
# Demo NuevaMente G10 - Fase 1
# Uso: chmod +x demo.sh && ./demo.sh

PAYLOAD='{"documento_titulo":"Introduccion a VCN en OCI","documento_contenido":"La Virtual Cloud Network (VCN) es una red privada y personalizable configurada en Oracle Cloud Infrastructure. Similar a una red de centro de datos tradicional, la VCN ofrece control total sobre su entorno de red, incluyendo subredes publicas y privadas, tablas de enrutamiento, Internet Gateways, NAT Gateways y Security Lists.","perfil_destinatario":"Principiante","formato_salida":"Flashcards","nicho_sector":"General","nivel_detalle":"Didactico"}'

echo "=== 1) SALUD DEL MOTOR ==="
curl -s http://localhost:8000/health | python3 -m json.tool

echo ""
echo "=== 2) ADAPTACION DIRECTA ==="
curl -s -X POST http://localhost:8000/adaptar -H "Content-Type: application/json" -d "$PAYLOAD" | python3 -m json.tool

echo ""
echo "=== 3) VIA ORQUESTADOR n8n ==="
curl -s -X POST http://localhost:5678/webhook/nuevamente-adaptar -H "Content-Type: application/json" -d "$PAYLOAD" | python3 -m json.tool
