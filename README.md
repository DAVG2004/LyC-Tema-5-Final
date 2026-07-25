# Lenguajes y Compiladores - Tema 5 (Final)

Este repositorio contiene la entrega final del **Tema 5** para la materia **Lenguajes y Compiladores**. El proyecto está estructurado en dos partes principales de desarrollo y una carpeta de documentación oficial.

---

## 📂 Estructura del Proyecto

El repositorio está organizado de la siguiente manera:

*   **`pregunta 4/`**: Experimento y comparación de rendimiento de tres (3) parsers distintos para archivos de configuración Docker Compose.
*   **`pregunta 5/`**: Asistente Híbrido para el lenguaje **UnegScript**, combinando análisis léxico/sintáctico tradicional con correcciones basadas en Distancia de Levenshtein y un Asistente de Inteligencia Artificial para la recuperación de errores.
*   **`documentos/`**: Documentación oficial y material de apoyo de la entrega.
    *   `Informe_Analisis_Sintactico.pdf`: Reporte detallado del análisis sintáctico.
    *   `Diapositivas_Arbol_Sintaxis_Abstracta.pdf` y `.pptx`: Presentación sobre Árboles de Sintaxis Abstracta (AST), su importancia y aplicaciones.

---

## 🚀 Pregunta 4: Comparativa de Rendimiento de Parsers

Este módulo realiza un análisis comparativo de la velocidad y eficiencia de procesamiento de tres aproximaciones de parsing para archivos YAML de Docker Compose:

1.  **Lark LALR(1)**: Un parser generado mediante la biblioteca Lark utilizando gramática formal.
2.  **Recursive Descent (Descenso Recursivo Custom)**: Implementación propia a mano para recorrer la estructura sintáctica del archivo.
3.  **PyYAML AST**: Parser tradicional basado en el árbol construido por la biblioteca nativa de PyYAML.

### Características
*   Prueba los parsers con un dataset de archivos de prueba (`dataset/docker-compose-*.yml`).
*   Ejecuta múltiples iteraciones por archivo para obtener estadísticas de desviación estándar, mínimos, máximos y operaciones por segundo.
*   Exporta los datos recopilados en formatos `resultados.json` y `resultados.csv`.
*   Genera gráficas estadísticas en formato PNG (`grafica_barras_comparativa.png`, `grafica_rendimiento_lineas.png`, y `grafica_throughput.png`).

### Cómo ejecutar el experimento
```bash
python "pregunta 4/medir_tiempos.py"
```

---

## 🧠 Pregunta 5: Asistente Híbrido UnegScript

Una herramienta avanzada de análisis léxico y sintáctico para el lenguaje experimental **UnegScript**. Integra recuperación inteligente de errores de código combinando dos capas de análisis:

1.  **Lexer Híbrido (Distancia de Levenshtein + Asistente IA)**:
    *   Detecta tokens mal escritos (palabras clave con errores ortográficos).
    *   Si la similitud de Levenshtein es alta ($\ge 0.8$), corrige automáticamente el token (ej: `prnt` $\to$ `print`).
    *   Si la similitud es baja ($< 0.8$), consulta al módulo del Asistente de IA para sugerir correcciones contextuales y explicaciones detalladas.
2.  **Parser de Descenso Recursivo con Recuperación por IA**:
    *   Construye el **Árbol de Sintaxis Abstracta (AST)** a partir de los tokens corregidos.
    *   Si encuentra un error sintáctico, consulta a la IA para obtener recomendaciones específicas de recuperación de la estructura del código.

### Salida del Programa
*   Muestra los tokens originales y corregidos.
*   Imprime el AST generado en formato JSON estructurado.
*   Muestra una representación gráfica del AST en un árbol ASCII.
*   Presenta un reporte completo de sugerencias y correcciones realizadas.

### Cómo ejecutar el asistente
```bash
python "pregunta 5/main.py"
```

---

## 🛠️ Requisitos del Entorno

Para ejecutar los scripts de la pregunta 4 y 5, asegúrate de tener instalado Python 3 y las siguientes dependencias:

```bash
pip install numpy matplotlib lark-parser pyyaml
```
*(Nota: El asistente de IA simula las interacciones con un modelo de lenguaje integrado en la arquitectura del parser).*

---

## 👥 Autores / Integrantes
*   **Alexmary Ramírez** - [alexmaryram.2005@gmail.com](mailto:alexmaryram.2005@gmail.com)
*   **Daniel Vallenilla (DAVG2004)** - [vallenilladaniel1@gmail.com](mailto:vallenilladaniel1@gmail.com)
*   **Robert Castro**
*   **Endrys Flores**

