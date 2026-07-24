"""
Script para medir tiempos de ejecución de los 3 parsers de Docker Compose.
"""
import os
import glob
import time
import json
import csv
import numpy as np

from parsers.parser_lark import parse_file as parse_lark
from parsers.parser_recursivo import parse_file as parse_recursivo
from parsers.parser_pyyaml import parse_file as parse_pyyaml

DATASET_DIR = os.path.join(os.path.dirname(__file__), 'dataset')
ITERATIONS = 50

def run_benchmark():
    files = sorted(glob.glob(os.path.join(DATASET_DIR, 'docker-compose-*.yml')))
    if not files:
        print(f"Error: No se encontraron archivos en {DATASET_DIR}")
        return

    parsers = {
        'Lark LALR(1)': parse_lark,
        'Recursive Descent': parse_recursivo,
        'PyYAML AST': parse_pyyaml
    }

    results = []

    print("==========================================================================")
    print("      EXPERIMENTO DE RENDIMIENTO: COMPARATIVA DE PARSERS DOCKER COMPOSE")
    print(f"      Archivos analizados: {len(files)} | Iteraciones por archivo: {ITERATIONS}")
    print("==========================================================================")

    for file_path in files:
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        file_metrics = {
            'file': filename,
            'size_bytes': file_size,
            'results': {}
        }

        print(f"\n[+] Analizando {filename} ({file_size} bytes)...")

        for name, parse_fn in parsers.items():
            # Warm-up run
            _ = parse_fn(file_path)

            durations = []
            for _ in range(ITERATIONS):
                t0 = time.perf_counter()
                _ = parse_fn(file_path)
                t1 = time.perf_counter()
                durations.append((t1 - t0) * 1000.0) # milliseconds

            mean_ms = float(np.mean(durations))
            std_ms = float(np.std(durations))
            min_ms = float(np.min(durations))
            max_ms = float(np.max(durations))
            ops_per_sec = float(1000.0 / mean_ms) if mean_ms > 0 else 0

            file_metrics['results'][name] = {
                'mean_ms': round(mean_ms, 5),
                'std_ms': round(std_ms, 5),
                'min_ms': round(min_ms, 5),
                'max_ms': round(max_ms, 5),
                'ops_per_sec': round(ops_per_sec, 2)
            }

            print(f"  -> {name:20s}: Promedio={mean_ms:.4f} ms | StdDev={std_ms:.4f} ms | Ops/sec={ops_per_sec:.1f}")

        results.append(file_metrics)

    # Save to JSON
    json_path = os.path.join(os.path.dirname(__file__), 'resultados.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    # Save to CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'resultados.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Archivo', 'Tamano_Bytes', 'Parser', 'Promedio_ms', 'StdDev_ms', 'Min_ms', 'Max_ms', 'Ops_por_Sec'])
        for item in results:
            for p_name, p_data in item['results'].items():
                writer.writerow([
                    item['file'],
                    item['size_bytes'],
                    p_name,
                    p_data['mean_ms'],
                    p_data['std_ms'],
                    p_data['min_ms'],
                    p_data['max_ms'],
                    p_data['ops_per_sec']
                ])

    print("\n[OK] Medicion completada exitosamente.")
    print(f"    Resultados guardados en: {csv_path} y {json_path}")

if __name__ == '__main__':
    run_benchmark()
