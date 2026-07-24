"""
Parser 2: Handwritten Recursive Descent Parser for Docker Compose YAML
"""
import re

class Token:
    def __init__(self, kind, value, indent=0):
        self.kind = kind
        self.value = value
        self.indent = indent

    def __repr__(self):
        return f"Token({self.kind}, {repr(self.value)}, indent={self.indent})"

class LexerRecursive:
    def __init__(self, text):
        self.lines = text.splitlines()

    def tokenize(self):
        tokens = []
        for line in self.lines:
            raw = line
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            indent = len(line) - len(line.lstrip())
            
            if stripped.startswith('- '):
                tokens.append(Token('LIST_ITEM', stripped[2:].strip(), indent))
            elif ':' in stripped:
                parts = stripped.split(':', 1)
                k = parts[0].strip()
                v = parts[1].strip()
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                tokens.append(Token('KEY_VALUE', (k, v), indent))
            else:
                tokens.append(Token('SCALAR', stripped, indent))
        return tokens

class RecursiveDescentYamlParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def parse(self):
        root = {}
        stack = [( -1, root )]

        while self.pos < len(self.tokens):
            tok = self.advance()
            if tok.kind == 'KEY_VALUE':
                k, v = tok.value
                # find parent in stack
                while stack and stack[-1][0] >= tok.indent:
                    stack.pop()
                parent = stack[-1][1]

                if v != "":
                    if isinstance(parent, dict):
                        parent[k] = v
                else:
                    new_dict = {}
                    if isinstance(parent, dict):
                        parent[k] = new_dict
                    stack.append((tok.indent, new_dict))

            elif tok.kind == 'LIST_ITEM':
                while stack and stack[-1][0] >= tok.indent:
                    stack.pop()
                parent_indent, parent_dict = stack[-1]
                
                # convert container or add to list
                if isinstance(parent_dict, dict):
                    # list attached to last added key in parent
                    pass
                val = tok.value
                if isinstance(parent_dict, list):
                    parent_dict.append(val)
                elif isinstance(parent_dict, dict):
                    if parent_dict:
                        last_key = list(parent_dict.keys())[-1]
                        if not isinstance(parent_dict[last_key], list):
                            parent_dict[last_key] = []
                        parent_dict[last_key].append(val)
        return root

def parse_docker_compose_recursivo(content: str) -> dict:
    lexer = LexerRecursive(content)
    tokens = lexer.tokenize()
    parser = RecursiveDescentYamlParser(tokens)
    return parser.parse()

def parse_file(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return parse_docker_compose_recursivo(f.read())
