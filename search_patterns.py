#!/usr/bin/env python3
"""
Script para buscar padrões regex em arquivos binários (como .so de apps Flutter/Android)
Uso: python3 search_patterns.py --file <arquivo_alvo> --json <arquivo_json>
"""

import sys
import json
import re
import subprocess
import argparse
import base64
from pathlib import Path
from typing import List, Dict, Union, Set, Tuple

# Cores ANSI
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

def print_error(msg: str):
    print(f"{Colors.RED}{msg}{Colors.NC}", file=sys.stderr)

def print_success(msg: str):
    print(f"{Colors.GREEN}{msg}{Colors.NC}")

def print_info(msg: str):
    print(f"{Colors.CYAN}{msg}{Colors.NC}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}{msg}{Colors.NC}")

def extract_strings(file_path: Path) -> List[str]:
    """Extrai strings legíveis de um arquivo binário usando o comando 'strings'"""
    try:
        result = subprocess.run(
            ['strings', str(file_path)],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print_error(f"Erro ao extrair strings: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print_error("Comando 'strings' não encontrado. Certifique-se de que está instalado.")
        sys.exit(1)

def is_base64(s: str) -> bool:
    """Verifica se uma string parece ser Base64"""
    if len(s) < 16:
        return False
    base64_pattern = re.compile('^[A-Za-z0-9+/]+={0,2}$')
    if not base64_pattern.match(s):
        return False
    if len(s) % 4 != 0:
        return False
    return True

def decode_base64(s: str) -> str:
    """Tenta decodificar uma string Base64"""
    try:
        decoded_bytes = base64.b64decode(s, validate=True)
        decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
        if decoded_str and any(c.isprintable() for c in decoded_str):
            return decoded_str
    except Exception:
        pass
    return ""

def expand_strings_with_base64(strings: List[str]) -> Tuple[List[str], Dict[str, str]]:
    """
    Expande a lista de strings decodificando Base64
    Retorna: (strings_expandidas, mapa_decodificado)
    """
    expanded = list(strings)
    decoded_map = {}
    
    print_info("Verificando e decodificando strings Base64...")
    count = 0
    
    for s in strings:
        if is_base64(s):
            decoded = decode_base64(s)
            if decoded and decoded != s:
                expanded.append(decoded)
                decoded_map[decoded] = s
                count += 1
    
    if count > 0:
        print_success(f"✓ {count} strings Base64 decodificadas com sucesso")
    else:
        print_info("Nenhuma string Base64 válida encontrada")
    
    print()
    return expanded, decoded_map

def load_patterns(json_path: Path) -> Dict[str, Union[str, List[str]]]:
    """Carrega os padrões regex do arquivo JSON"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print_error(f"Erro ao parsear JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro ao ler arquivo JSON: {e}")
        sys.exit(1)

def search_pattern(pattern: str, strings: List[str], decoded_map: Dict[str, str]) -> Set[Tuple[str, str, str]]:
    """
    Busca um padrão regex nas strings extraídas
    Retorna: Set de tuplas (match, fonte, contexto_completo)
    """
    matches = set()
    try:
        regex = re.compile(pattern, re.IGNORECASE)
        for string in strings:
            found = regex.findall(string)
            if found:
                source = decoded_map.get(string, None)
                source_label = f"base64: {source}" if source else "direto"
                context = string if source else ""
                
                for match in found:
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else ''.join(match)
                    if match:
                        matches.add((match, source_label, context))
    except re.error as e:
        print_error(f"  Erro no regex: {e}")
    
    return matches

def process_patterns(patterns: Dict[str, Union[str, List[str]]], strings: List[str], decoded_map: Dict[str, str], max_results: int):
    """Processa todos os padrões e exibe os resultados"""
    total_patterns = 0
    total_matches = 0
    
    for key, value in patterns.items():
        print(f"{Colors.CYAN}{'━' * 70}{Colors.NC}")
        print(f"{Colors.GREEN}Padrão: {Colors.YELLOW}{key}{Colors.NC}")
        
        if isinstance(value, list):
            print(f"{Colors.GREEN}Tipo: {Colors.NC}Array com {len(value)} padrões")
            print()
            
            for idx, pattern in enumerate(value, 1):
                print(f"  {Colors.BLUE}Regex {idx}:{Colors.NC} {pattern}")
                matches = search_pattern(pattern, strings, decoded_map)
                
                if matches:
                    count = len(matches)
                    total_matches += count
                    print(f"    {Colors.GREEN}✓ Encontrado(s) {count} resultado(s) único(s):{Colors.NC}")
                    print()
                    
                    sorted_matches = sorted(matches, key=lambda x: (x[0], x[1]))
                    
                    for i, (match, source, context) in enumerate(sorted_matches[:max_results], 1):
                        if source.startswith("base64:"):
                            print(f"      {Colors.BLUE}→{Colors.NC} {match}")
                            print(f"        {Colors.YELLOW}Decodificado:{Colors.NC} {context}")
                        else:
                            print(f"      {Colors.BLUE}→{Colors.NC} {match}")
                    
                    if count > max_results:
                        remaining = count - max_results
                        print(f"      {Colors.YELLOW}... e mais {remaining} resultado(s){Colors.NC}")
                else:
                    print(f"    {Colors.RED}✗ Nenhum resultado encontrado{Colors.NC}")
                print()
                
                total_patterns += 1
        else:
            print(f"{Colors.GREEN}Regex: {Colors.NC}{value}")
            print()
            
            matches = search_pattern(value, strings, decoded_map)
            
            if matches:
                count = len(matches)
                total_matches += count
                print(f"  {Colors.GREEN}✓ Encontrado(s) {count} resultado(s) único(s):{Colors.NC}")
                print()
                
                sorted_matches = sorted(matches, key=lambda x: (x[0], x[1]))
                
                for match, source, context in sorted_matches[:max_results]:
                    if source.startswith("base64:"):
                        print(f"    {Colors.BLUE}→{Colors.NC} {match}")
                        print(f"      {Colors.YELLOW}Decodificado:{Colors.NC} {context}")
                    else:
                        print(f"    {Colors.BLUE}→{Colors.NC} {match}")
                
                if count > max_results:
                    remaining = count - max_results
                    print(f"    {Colors.YELLOW}... e mais {remaining} resultado(s){Colors.NC}")
            else:
                print(f"  {Colors.RED}✗ Nenhum resultado encontrado{Colors.NC}")
            print()
            
            total_patterns += 1
    
    return total_patterns, total_matches

def parse_arguments():
    """Parse argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description='Busca padrões regex em arquivos binários (ex: libapp.so)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python3 search_patterns.py --file libapp.so --json regexes.json
  python3 search_patterns.py -f libapp.so -j regexes.json --max-results 50
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        required=True,
        help='Arquivo alvo para busca (ex: libapp.so)'
    )
    
    parser.add_argument(
        '--json', '-j',
        type=str,
        required=True,
        help='Arquivo JSON com padrões regex'
    )
    
    parser.add_argument(
        '--max-results', '-m',
        type=int,
        default=20,
        help='Número máximo de resultados por padrão (padrão: 20)'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Desabilita cores no output'
    )
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    if args.no_color:
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')
    
    target_file = Path(args.file)
    json_file = Path(args.json)
    
    if not target_file.exists():
        print_error(f"Erro: Arquivo alvo '{target_file}' não encontrado")
        sys.exit(1)
    
    if not json_file.exists():
        print_error(f"Erro: Arquivo JSON '{json_file}' não encontrado")
        sys.exit(1)
    
    print(f"{Colors.BLUE}{'═' * 70}{Colors.NC}")
    print(f"{Colors.BLUE}  Busca de Padrões Regex em Arquivo Binário{Colors.NC}")
    print(f"{Colors.BLUE}{'═' * 70}{Colors.NC}")
    print(f"Arquivo alvo: {Colors.YELLOW}{target_file}{Colors.NC}")
    print(f"Arquivo JSON: {Colors.YELLOW}{json_file}{Colors.NC}")
    print()
    
    print_info("Extraindo strings do arquivo binário...")
    strings = extract_strings(target_file)
    print_success(f"✓ {len(strings)} strings extraídas")
    print()
    
    expanded_strings, decoded_map = expand_strings_with_base64(strings)
    
    patterns = load_patterns(json_file)
    
    total_patterns, total_matches = process_patterns(patterns, expanded_strings, decoded_map, args.max_results)
    
    print(f"{Colors.BLUE}{'═' * 70}{Colors.NC}")
    print_success(f"Busca concluída!")
    print(f"Total de padrões processados: {total_patterns}")
    print(f"Total de matches encontrados: {total_matches}")
    print(f"{Colors.BLUE}{'═' * 70}{Colors.NC}")

if __name__ == "__main__":
    main()