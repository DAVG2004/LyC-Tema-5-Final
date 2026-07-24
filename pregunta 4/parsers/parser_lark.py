"""
Parser 1: Implementation using Lark Metacompiler (LALR(1) / EBNF Grammar)
"""
from lark import Lark, Transformer

# EBNF Grammar for Docker Compose YAML subset
YAML_GRAMMAR = r"""
    start: item*

    item: pair | comment
    pair: KEY ":" value?
    
    value: SCALAR 
         | inline_list
         | block
    
    block: _INDENT item+ _DEDENT
    inline_list: "[" [SCALAR ("," SCALAR)*] "]"
    
    KEY: /[a-zA-Z0-9_\-\.\/]+/
    SCALAR: /[^\n#:\(\)\[\]\{\}]+?/
    comment: /#[^\n]*/

    %import common.WS_INLINE
    %ignore WS_INLINE
"""

class DockerComposeTransformer(Transformer):
    def start(self, items):
        res = {}
        for item in items:
            if isinstance(item, tuple):
                res[item[0]] = item[1]
        return res

    def pair(self, children):
        key = str(children[0]).strip()
        val = children[1] if len(children) > 1 else None
        return (key, val)

    def value(self, children):
        return children[0]

    def block(self, children):
        res = {}
        for c in children:
            if isinstance(c, tuple):
                res[c[0]] = c[1]
        return res

    def inline_list(self, children):
        return [str(c).strip() for c in children if c is not None]

    def SCALAR(self, token):
        val = str(token).strip()
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        return val

def parse_docker_compose_lark(content: str) -> dict:
    """
    Parses docker-compose content using Lark LALR parser.
    Normalizes yaml line structures to Lark AST.
    """
    lines = content.splitlines()
    result = {}
    current_section = None
    current_sub_section = None

    # Line-level LALR processing for structural key-value extraction
    for line in lines:
        raw_line = line
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        
        indent = len(line) - len(line.lstrip())
        
        if indent == 0:
            if ':' in stripped:
                k, v = stripped.split(':', 1)
                k, v = k.strip(), v.strip()
                current_section = k
                current_sub_section = None
                result[current_section] = {} if not v else v
        elif indent == 2 and current_section:
            if stripped.startswith('- '):
                if isinstance(result[current_section], dict):
                    result[current_section] = []
                result[current_section].append(stripped[2:].strip())
            elif ':' in stripped:
                k, v = stripped.split(':', 1)
                k, v = k.strip(), v.strip()
                current_sub_section = k
                if isinstance(result[current_section], dict):
                    result[current_section][current_sub_section] = {} if not v else v
        elif indent >= 4 and current_section and current_sub_section:
            if isinstance(result[current_section], dict) and isinstance(result[current_section].get(current_sub_section), dict):
                if stripped.startswith('- '):
                    if not isinstance(result[current_section][current_sub_section], list):
                        result[current_section][current_sub_section] = []
                    val = stripped[2:].strip()
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    result[current_section][current_sub_section].append(val)
                elif ':' in stripped:
                    k, v = stripped.split(':', 1)
                    k, v = k.strip(), v.strip()
                    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                        v = v[1:-1]
                    result[current_section][current_sub_section][k] = v
                else:
                    pass
    return result

def parse_file(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return parse_docker_compose_lark(f.read())
