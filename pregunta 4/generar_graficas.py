"""
Script para generar gráficas comparativas de rendimiento de parsers.
"""
import os
import json
import matplotlib.pyplot as plt
import numpy as np

RESULTS_JSON = os.path.join(os.path.dirname(__file__), 'resultados.json')

def generar_graficas():
    if not os.path.exists(RESULTS_JSON):
        print(f"Error: No existe el archivo {RESULTS_JSON}. Ejecuta primero medir_tiempos.py")
        return

    with open(RESULTS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    files = [item['file'].replace('docker-compose-', 'File ').replace('.yml', '') for item in data]
    parser_names = list(data[0]['results'].keys())

    # Styling settings
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig_color_bg = '#1a1a24'
    text_color = '#ffffff'
    grid_color = '#333344'
    colors = ['#00f2fe', '#4facfe', '#ff0844']

    # 1. Line Chart: Tiempo de Ejecución vs Complejidad del Archivo
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=fig_color_bg)
    ax.set_facecolor('#12121a')

    for idx, p_name in enumerate(parser_names):
        times = [item['results'][p_name]['mean_ms'] for item in data]
        ax.plot(files, times, marker='o', linewidth=2.5, label=p_name, color=colors[idx % len(colors)])

    ax.set_title('Experimento de Rendimiento: Tiempo de Ejecución vs Archivo Compose', color=text_color, fontsize=14, pad=15, fontweight='bold')
    ax.set_xlabel('Archivo Docker Compose (Complejidad Creciente)', color=text_color, fontsize=11, labelpad=10)
    ax.set_ylabel('Tiempo Promedio de Ejecución (ms)', color=text_color, fontsize=11, labelpad=10)
    ax.tick_params(colors=text_color, labelsize=10)
    ax.grid(True, linestyle='--', alpha=0.3, color=grid_color)
    ax.legend(facecolor='#222230', edgecolor='none', labelcolor=text_color, fontsize=10)
    plt.xticks(rotation=30)
    plt.tight_layout()

    out_line = os.path.join(os.path.dirname(__file__), 'grafica_rendimiento_lineas.png')
    plt.savefig(out_line, dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Grouped Bar Chart: Comparativa por Parser
    fig, ax = plt.subplots(figsize=(12, 6.5), facecolor=fig_color_bg)
    ax.set_facecolor('#12121a')

    x = np.arange(len(files))
    width = 0.25

    for idx, p_name in enumerate(parser_names):
        times = [item['results'][p_name]['mean_ms'] for item in data]
        ax.bar(x + (idx - 1) * width, times, width, label=p_name, color=colors[idx % len(colors)], alpha=0.9)

    ax.set_title('Comparativa de Tiempos Promedio por Parser (milisegundos)', color=text_color, fontsize=14, pad=15, fontweight='bold')
    ax.set_xlabel('Archivos Docker Compose Benchmark', color=text_color, fontsize=11, labelpad=10)
    ax.set_ylabel('Tiempo de Ejecución (ms)', color=text_color, fontsize=11, labelpad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(files, color=text_color, rotation=30)
    ax.tick_params(colors=text_color, labelsize=10)
    ax.grid(True, linestyle='--', alpha=0.3, color=grid_color)
    ax.legend(facecolor='#222230', edgecolor='none', labelcolor=text_color, fontsize=10)
    plt.tight_layout()

    out_bar = os.path.join(os.path.dirname(__file__), 'grafica_barras_comparativa.png')
    plt.savefig(out_bar, dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Throughput Bar Chart: Operaciones por segundo promedio
    fig, ax = plt.subplots(figsize=(9, 5.5), facecolor=fig_color_bg)
    ax.set_facecolor('#12121a')

    avg_ops = [np.mean([item['results'][p_name]['ops_per_sec'] for item in data]) for p_name in parser_names]
    bars = ax.bar(parser_names, avg_ops, color=colors, width=0.5, alpha=0.9)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:,.0f} ops/sec',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom', color=text_color, fontweight='bold', fontsize=11)

    ax.set_title('Rendimiento Global: Operaciones por Segundo Promedio (Throughput)', color=text_color, fontsize=14, pad=15, fontweight='bold')
    ax.set_ylabel('Parses por Segundo (ops/sec)', color=text_color, fontsize=11, labelpad=10)
    ax.tick_params(colors=text_color, labelsize=11)
    ax.grid(True, linestyle='--', alpha=0.3, color=grid_color)
    plt.tight_layout()

    out_ops = os.path.join(os.path.dirname(__file__), 'grafica_throughput.png')
    plt.savefig(out_ops, dpi=300, bbox_inches='tight')
    plt.close()

    print("[OK] Graficas generadas exitosamente:")
    print(f"    - {out_line}")
    print(f"    - {out_bar}")
    print(f"    - {out_ops}")

if __name__ == '__main__':
    generar_graficas()
