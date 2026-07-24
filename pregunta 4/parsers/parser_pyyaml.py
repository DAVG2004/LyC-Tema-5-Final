"""
Parser 3: Low-Level Event/AST PyYAML Parser Implementation
"""
import yaml

def parse_docker_compose_pyyaml(content: str) -> dict:
    """
    Parses docker-compose content using PyYAML SafeLoader AST parser.
    """
    return yaml.safe_load(content)

def parse_file(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return parse_docker_compose_pyyaml(f.read())
