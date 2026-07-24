"""
Programa Principal: Asistente Híbrido UnegScript (Pregunta 5)
Procesa código con errores léxicos/sintácticos mediante Levenshtein + Asistente IA + Parser AST
"""
import json
import sys
from hybrid_lexer import HybridLexer, calculate_similarity
from ai_assistant import AIAssistant
from recursive_parser import RecursiveDescentParser

def print_banner():
    print("==========================================================================")
    print("         ASISTENTE HÍBRIDO UNEGSCRIPT (LEXER LEVENSHTEIN + PARSER IA)")
    print("==========================================================================")

def format_ast_tree(node, indent="", is_last=True):
    """Genera una representación visual tipo árbol ASCII del AST."""
    if not node:
        return ""
    
    node_type = node.get('type', 'Node')
    tree_str = f"{indent}{'+-- ' if is_last else '|-- '}[{node_type}]"
    
    details = []
    for k, v in node.items():
        if k != 'type' and not isinstance(v, (dict, list)):
            details.append(f"{k}={repr(v)}")
    if details:
        tree_str += f" ({', '.join(details)})"
    tree_str += "\n"

    new_indent = indent + ("    " if is_last else "|   ")
    
    children = []
    for k, v in node.items():
        if k != 'type':
            if isinstance(v, dict):
                children.append(v)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        children.append(item)
    
    for idx, child in enumerate(children):
        tree_str += format_ast_tree(child, new_indent, idx == len(children) - 1)
    
    return tree_str

def process_unegscript(code: str):
    print(f"\n[1] CODIGO DE ENTRADA CON ERRORES:")
    print(f"    > \"{code}\"\n")

    ai_assistant = AIAssistant()
    lexer = HybridLexer(ai_assistant=ai_assistant)

    # 1. Lexical Analysis
    tokens, corrections, ai_consultations = lexer.tokenize(code)

    print("--------------------------------------------------------------------------")
    print(" [2] RESULTADOS DEL LEXER HIBRIDO (DISTANCIA DE LEVENSHTEIN):")
    print("--------------------------------------------------------------------------")
    for t in tokens:
        print(f"  * {t}")

    if corrections:
        print("\n  [OK] CORRECCIONES AUTOMATICAS POR LEVENSHTEIN (Similitud >= 0.8):")
        for c in corrections:
            print(f"      - '{c['original']}' -> '{c['corrected']}' (Similitud Levenshtein: {c['similarity']:.2f})")

    if ai_consultations:
        print("\n  [AI] CONSULTAS AL MODULO DE IA (Similitud < 0.8):")
        for ai_item in ai_consultations:
            tok = ai_item['token']
            sugg = ai_item['ai_suggestion']
            print(f"      - Token dudoso '{tok}' (Similitud max: {ai_item['best_similarity']:.2f})")
            if sugg:
                print(f"        Sugerencia IA: '{sugg['suggested_fix']}' | Confianza: {sugg['ai_confidence']*100:.0f}%")
                print(f"        Explicacion: {sugg['explanation']}")

    # 2. Parsing & AST Generation
    print("\n--------------------------------------------------------------------------")
    print(" [3] CONSTRUCCION DEL ARBOL DE SINTAXIS ABSTRACTA (AST):")
    print("--------------------------------------------------------------------------")
    
    parser = RecursiveDescentParser(tokens, ai_assistant=ai_assistant)
    ast = parser.parse()
    ast_dict = ast.to_dict()

    print("\n  Estructura AST (JSON Formateado):")
    print(json.dumps(ast_dict, indent=2, ensure_ascii=True))

    print("\n  Representacion Grafica del Arbol Sintactico (AST):")
    print(format_ast_tree(ast_dict))

    # 3. AI Suggestions & Recovery Summary
    print("--------------------------------------------------------------------------")
    print(" [4] INFORME DE CORRECCIONES Y SUGERENCIAS DEL ASISTENTE IA:")
    print("--------------------------------------------------------------------------")
    print("  * Resumen del Procesamiento:")
    print(f"    - Total de Tokens Procesados: {len(tokens)}")
    print(f"    - Errores Lexicos Corregidos por Levenshtein: {len(corrections)}")
    print(f"    - Errores Sintacticos Detectados: {len(parser.errors)}")
    
    if corrections:
        print("\n  * Detalle de Reparaciones Aplicadas:")
        for idx, c in enumerate(corrections, 1):
            print(f"    {idx}. Error Typo en palabra clave: '{c['original']}'")
            print(f"       -> Corregido a: '{c['corrected']}'")
            print(f"       -> Metrica Levenshtein: 1 - (dist / max_len) = {c['similarity']:.2f} >= 0.80")

    print("\n==========================================================================")
    print("                      PROCESAMIENTO FINALIZADO CON ÉXITO")
    print("==========================================================================\n")

if __name__ == '__main__':
    print_banner()
    
    # Input target code specified in requirement
    test_code = 'pront x = 5; if x > 3 prnt(x) else prnt("no")'
    
    if len(sys.argv) > 1:
        test_code = " ".join(sys.argv[1:])
        
    process_unegscript(test_code)
