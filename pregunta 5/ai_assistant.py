"""
Módulo Asistente IA para UnegScript
Simulador de modelo inteligente para análisis y recomendación de errores sintácticos y léxicos.
"""

class AIAssistant:
    def __init__(self):
        self.logs = []

    def consult_unrecognized_token(self, token: str, valid_keywords: list) -> dict:
        """
        Simula la consulta a un modelo de IA cuando la similitud de Levenshtein es < 0.8
        """
        # Contextual intelligence rules
        if token.lower() in ['prn', 'prntf', 'write', 'echo', 'say']:
            suggestion = 'print'
            reason = f"El token '{token}' sugiere una intención de salida/impresión. La palabra clave oficial en UnegScript es 'print'."
            confidence = 0.92
        elif token.lower() in ['fi', 'iff', 'when']:
            suggestion = 'if'
            reason = f"El token '{token}' representa una estructura condicional. Usar 'if'."
            confidence = 0.89
        elif token.lower() in ['otherwise', 'els']:
            suggestion = 'else'
            reason = f"El token '{token}' representa la rama alternativa condicional. Usar 'else'."
            confidence = 0.90
        elif token.lower() in ['let', 'val', 'variable', 'set']:
            suggestion = 'var'
            reason = f"Intención de declaración de variable detectada para '{token}'. UnegScript utiliza 'var'."
            confidence = 0.88
        else:
            suggestion = token
            reason = f"Token '{token}' no coincide estrechamente con palabras clave conocidas. Identificado como variable/identificador."
            confidence = 0.60

        result = {
            'original_token': token,
            'suggested_fix': suggestion,
            'explanation': reason,
            'ai_confidence': confidence
        }
        self.logs.append(result)
        return result

    def generate_parser_suggestion(self, expected: str, found: str, line_code: str) -> dict:
        """
        Genera sugerencias inteligentes cuando el parser recursivo falla.
        """
        suggestion = f"Se esperaba '{expected}' pero se encontró '{found}'."
        fix = f"Modificar '{found}' por '{expected}' o verificar delimitadores ';' y '(' en la sentencia: `{line_code}`."

        result = {
            'error_type': 'SyntaxError',
            'expected': expected,
            'found': found,
            'explanation': suggestion,
            'suggested_repair': fix
        }
        self.logs.append(result)
        return result

    def log_error(self, message: str):
        self.logs.append({'error_type': 'GeneralError', 'message': message})
