#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para ejecutar tests y ver resultados"""
import subprocess
import sys
import os

os.chdir(r'C:\Users\Maxip\OneDrive\Documentos\Prepolitecinca\SeptimoSemestre\VerificacionYValidacionDeSoftware\Proyecto\immigration-crm\backend')

result = subprocess.run(
    ['python', '-m', 'behave',
     'features/solicitudes/agendamiento/agendamiento_entrevista.feature',
     '--no-capture', '--no-color'],
    capture_output=True,
    text=True,
    encoding='utf-8',
    errors='replace'
)

output = result.stdout + result.stderr

# Escribir a archivo
with open('test_results.txt', 'w', encoding='utf-8') as f:
    f.write(output)
    f.write(f"\n\nCodigo de salida: {result.returncode}\n")
    if result.returncode == 0:
        f.write("✅ TODOS LOS TESTS PASARON\n")
    else:
        f.write("❌ ALGUNOS TESTS FALLARON\n")

# Buscar y mostrar resumen
lines = output.split('\n')
summary_started = False
for line in lines:
    if 'Failing scenarios' in line or 'features passed' in line or 'scenarios passed' in line or 'steps passed' in line:
        summary_started = True
    if summary_started:
        print(line)

print(f"\nCodigo de salida: {result.returncode}")
if result.returncode == 0:
    print("TODOS LOS TESTS PASARON")
else:
    print("ALGUNOS TESTS FALLARON")

print("\nResultados completos guardados en test_results.txt")
