"""
Parser Recursivo Descendente para UnegScript
Construye el Árbol de Sintaxis Abstracta (AST) e integra recuperación de errores con sugerencias de IA.
"""

class ASTNode:
    def __init__(self, type_: str, **kwargs):
        self.type = type_
        self.attributes = kwargs

    def to_dict(self):
        res = {'type': self.type}
        for k, v in self.attributes.items():
            if isinstance(v, ASTNode):
                res[k] = v.to_dict()
            elif isinstance(v, list):
                res[k] = [item.to_dict() if isinstance(item, ASTNode) else item for item in v]
            else:
                res[k] = v
        return res

class RecursiveDescentParser:
    def __init__(self, tokens, ai_assistant=None):
        self.tokens = tokens
        self.pos = 0
        self.ai_assistant = ai_assistant
        self.errors = []

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        tok = self.peek()
        if tok:
            self.pos += 1
        return tok

    def match(self, expected_type, expected_value=None):
        tok = self.peek()
        if not tok:
            return False
        if tok.type == expected_type and (expected_value is None or tok.value == expected_value):
            self.advance()
            return True
        return False

    def expect(self, expected_type, expected_value=None):
        tok = self.peek()
        if not tok:
            err = f"Fin de entrada inesperado, se esperaba {expected_type} {expected_value or ''}"
            self.errors.append(err)
            if self.ai_assistant:
                self.ai_assistant.generate_parser_suggestion(expected_value or expected_type, 'EOF', '')
            return None
        
        if tok.type == expected_type and (expected_value is None or tok.value == expected_value):
            return self.advance()
        else:
            err = f"Error sintáctico: se esperaba {expected_type} '{expected_value or ''}', se encontró '{tok.value}'"
            self.errors.append(err)
            if self.ai_assistant:
                self.ai_assistant.generate_parser_suggestion(expected_value or expected_type, tok.value, str(tok))
            return None

    def parse(self):
        statements = []
        while self.pos < len(self.tokens):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            else:
                self.advance() # error recovery skip
        return ASTNode('Program', body=statements)

    def parse_statement(self):
        tok = self.peek()
        if not tok:
            return None

        # 1. Print Statement
        if tok.type == 'KEYWORD' and tok.value == 'print':
            self.advance()
            has_paren = self.match('DELIMITER', '(')
            expr = self.parse_expression()
            if has_paren:
                self.match('DELIMITER', ')')
            self.match('DELIMITER', ';')
            return ASTNode('PrintStatement', expression=expr)

        # 2. If Statement
        elif tok.type == 'KEYWORD' and tok.value == 'if':
            self.advance()
            cond = self.parse_expression()
            then_branch = self.parse_statement()
            else_branch = None
            if self.peek() and self.peek().type == 'KEYWORD' and self.peek().value == 'else':
                self.advance()
                else_branch = self.parse_statement()
            return ASTNode('IfStatement', condition=cond, then_branch=then_branch, else_branch=else_branch)

        # 3. Var Declaration or Assignment
        elif tok.type == 'KEYWORD' and tok.value == 'var':
            self.advance()
            id_tok = self.expect('IDENTIFIER')
            var_name = id_tok.value if id_tok else 'unknown'
            self.expect('OPERATOR', '=')
            expr = self.parse_expression()
            self.match('DELIMITER', ';')
            return ASTNode('VarDeclaration', name=var_name, value=expr)

        # 4. Identifier Assignment or Expression Statement
        elif tok.type == 'IDENTIFIER':
            id_tok = self.advance()
            if self.peek() and self.peek().type == 'OPERATOR' and self.peek().value == '=':
                self.advance()
                expr = self.parse_expression()
                self.match('DELIMITER', ';')
                return ASTNode('Assignment', name=id_tok.value, value=expr)
            else:
                # Primary identifier in statement context
                self.match('DELIMITER', ';')
                return ASTNode('Identifier', name=id_tok.value)

        else:
            expr = self.parse_expression()
            self.match('DELIMITER', ';')
            return expr

    def parse_expression(self):
        left = self.parse_primary()
        tok = self.peek()
        if tok and tok.type == 'OPERATOR':
            op_tok = self.advance()
            right = self.parse_primary()
            return ASTNode('BinaryExpression', left=left, operator=op_tok.value, right=right)
        return left

    def parse_primary(self):
        tok = self.peek()
        if not tok:
            return ASTNode('Literal', value=None)

        if tok.type == 'NUMBER':
            self.advance()
            val = float(tok.value) if '.' in tok.value else int(tok.value)
            return ASTNode('Literal', value=val)
        elif tok.type == 'STRING':
            self.advance()
            return ASTNode('Literal', value=tok.value)
        elif tok.type == 'IDENTIFIER':
            self.advance()
            return ASTNode('Identifier', name=tok.value)
        elif tok.type == 'KEYWORD' and tok.value in ['true', 'false']:
            self.advance()
            return ASTNode('Literal', value=(tok.value == 'true'))
        else:
            self.advance()
            return ASTNode('Literal', value=tok.value)
