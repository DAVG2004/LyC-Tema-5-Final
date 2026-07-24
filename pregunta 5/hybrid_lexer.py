"""
Lexer Híbrido para UnegScript con Distancia de Levenshtein y Fallback a IA
"""
import re

KEYWORDS = ["print", "if", "else", "while", "var", "function", "return", "true", "false"]

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calcula la distancia de edición de Levenshtein entre dos cadenas."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                cost = 0
            else:
                cost = 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # Eliminación
                dp[i][j - 1] + 1,      # Inserción
                dp[i - 1][j - 1] + cost # Sustitución
            )
    return dp[m][n]

def calculate_similarity(s1: str, s2: str) -> float:
    """
    Calcula la similitud normalizada entre 0.0 y 1.0 basada en Levenshtein.
    Similitud = 1.0 - (distancia / max_longitud)
    """
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    dist = levenshtein_distance(s1, s2)
    return 1.0 - (dist / max_len)

class Token:
    def __init__(self, type_: str, value: str, line: int = 1, col: int = 1, auto_corrected: bool = False, original_value: str = None, confidence: float = 1.0):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col
        self.auto_corrected = auto_corrected
        self.original_value = original_value if original_value else value
        self.confidence = confidence

    def __repr__(self):
        if self.auto_corrected:
            return f"Token({self.type}, '{self.value}' [AutoCorregido de '{self.original_value}', sim={self.confidence:.2f}])"
        return f"Token({self.type}, '{self.value}')"

class HybridLexer:
    def __init__(self, ai_assistant=None):
        self.ai_assistant = ai_assistant
        self.known_variables = set()

    def tokenize(self, code: str):
        tokens = []
        corrections = []
        ai_consultations = []

        # Specification of Regex Patterns
        token_specification = [
            ('NUMBER',     r'\d+(\.\d+)?'),
            ('STRING',     r'"[^"]*"|\'[^\']*\''),
            ('OPERATOR',   r'==|!=|<=|>=|[=>\+\-\*/]'),
            ('DELIMITER',  r'[;(),{}]'),
            ('WORD',       r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('SKIP',       r'[ \t\n]+'),
            ('MISMATCH',   r'.'),
        ]
        tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)

        for mo in re.finditer(tok_regex, code):
            kind = mo.lastgroup
            val = mo.group()
            
            if kind == 'SKIP':
                continue
            elif kind == 'NUMBER':
                tokens.append(Token('NUMBER', val))
            elif kind == 'STRING':
                tokens.append(Token('STRING', val[1:-1]))
            elif kind == 'OPERATOR':
                tokens.append(Token('OPERATOR', val))
            elif kind == 'DELIMITER':
                tokens.append(Token('DELIMITER', val))
            elif kind == 'WORD':
                # 1. Exact Match with Keywords
                if val in KEYWORDS:
                    tokens.append(Token('KEYWORD', val))
                    if val == 'var':
                        pass # variable declaration token
                else:
                    # 2. Check Levenshtein Similarity with all Keywords
                    best_match = None
                    highest_sim = 0.0

                    for kw in KEYWORDS:
                        sim = calculate_similarity(val, kw)
                        if sim > highest_sim:
                            highest_sim = sim
                            best_match = kw

                    # Decision Threshold: sim >= 0.8 (or > 0.79 for float precision)
                    if highest_sim >= 0.79 and best_match:
                        # Auto-correction via Levenshtein
                        token = Token(
                            type_='KEYWORD',
                            value=best_match,
                            auto_corrected=True,
                            original_value=val,
                            confidence=highest_sim
                        )
                        tokens.append(token)
                        corrections.append({
                            'original': val,
                            'corrected': best_match,
                            'similarity': round(highest_sim, 2),
                            'method': 'Levenshtein Auto-Correction'
                        })
                    else:
                        # 3. If similarity < 0.8, check if it's a known or declared variable
                        if val in self.known_variables or len(val) == 1:
                            tokens.append(Token('IDENTIFIER', val))
                            self.known_variables.add(val)
                        else:
                            # 4. Trigger AI Assistant Consultation
                            ai_suggestion = None
                            if self.ai_assistant:
                                ai_suggestion = self.ai_assistant.consult_unrecognized_token(val, KEYWORDS)
                            
                            ai_consultations.append({
                                'token': val,
                                'best_similarity': round(highest_sim, 2),
                                'ai_suggestion': ai_suggestion
                            })

                            # Fallback: treat as identifier with AI warning
                            tokens.append(Token('IDENTIFIER', val, auto_corrected=False))
                            self.known_variables.add(val)

            elif kind == 'MISMATCH':
                # Unknown symbol error
                if self.ai_assistant:
                    self.ai_assistant.log_error(f"Símbolo no reconocido '{val}'")
                tokens.append(Token('UNKNOWN', val))

        return tokens, corrections, ai_consultations
