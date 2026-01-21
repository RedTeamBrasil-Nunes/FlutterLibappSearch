# 🔍 Regex Pattern Scanner

Script Python para busca de padrões regex em arquivos binários (como `.so` de apps Flutter/Android), com suporte automático para detecção e decodificação de strings Base64.

## 📋 Características

- ✅ Extrai strings de arquivos binários
- ✅ Detecta e decodifica automaticamente strings Base64
- ✅ Suporta múltiplos padrões regex via arquivo JSON
- ✅ Suporta arrays de regex para um mesmo padrão
- ✅ Busca case-insensitive
- ✅ Remove duplicatas automaticamente
- ✅ Output colorido e organizado
- ✅ Mostra contexto completo de strings decodificadas

## 🚀 Requisitos

### Sistema
- **Python 3.6+** (geralmente pré-instalado no macOS)
- **Comando `strings`** (pré-instalado no macOS/Linux)

### Dependências Python
Nenhuma! O script usa apenas bibliotecas padrão do Python.

## 📦 Instalação

```bash
# Clone o repositório
git clone <seu-repositorio>
cd <nome-do-projeto>

# Torne o script executável (opcional)
chmod +x search_patterns.py
```

## 🎯 Uso

### Sintaxe Básica

```bash
python3 search_patterns.py --file <arquivo_alvo> --json <arquivo_json>
```

### Exemplos

```bash
# Forma básica
python3 search_patterns.py --file libapp.so --json regexes.json

# Forma curta com aliases
python3 search_patterns.py -f libapp.so -j regexes.json

# Limitando número de resultados
python3 search_patterns.py -f libapp.so -j regexes.json --max-results 50

# Sem cores (útil para logs)
python3 search_patterns.py -f libapp.so -j regexes.json --no-color

# Ver ajuda
python3 search_patterns.py --help
```

## 📝 Formato do Arquivo JSON

O arquivo JSON deve conter pares chave-valor onde:
- **Chave**: Nome descritivo do padrão
- **Valor**: Regex (string) ou array de regex

### Exemplo de JSON

```json
{
  "Firebase": "[a-z0-9.-]+\\.firebaseio\\.com",
  "AWS_API_Key": "AKIA[0-9A-Z]{16}",
  "Amazon_AWS_S3_Bucket": [
    "//s3-[a-z0-9-]+\\.amazonaws\\.com/[a-z0-9._-]+",
    "//s3\\.amazonaws\\.com/[a-z0-9._-]+",
    "[a-z0-9.-]+\\.s3\\.amazonaws\\.com"
  ],
  "Google_API_Key": "AIza[0-9A-Za-z\\-_]{35}",
  "IP_Address": "(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
}
```

### JSON de Exemplo Completo

Você pode usar o arquivo de regex do projeto [apkleaks](https://github.com/dwisiswant0/apkleaks/blob/master/config/regexes.json) como referência.

## 🎨 Output

O script exibe resultados organizados e coloridos:

```
═══════════════════════════════════════════════════════════
  Busca de Padrões Regex em Arquivo Binário
═══════════════════════════════════════════════════════════
Arquivo alvo: libapp.so
Arquivo JSON: regexes.json

Extraindo strings do arquivo binário...
✓ 45230 strings extraídas

Verificando e decodificando strings Base64...
✓ 128 strings Base64 decodificadas com sucesso

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Padrão: Firebase
Regex: [a-z0-9.-]+\.firebaseio\.com

  ✓ Encontrado(s) 2 resultado(s) único(s):

    → myapp.firebaseio.com
    
    → secret-api.firebaseio.com
      Decodificado: {"url":"https://secret-api.firebaseio.com","key":"abc123"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Padrão: Google_API_Key
Regex: AIza[0-9A-Za-z\-_]{35}

  ✓ Encontrado(s) 1 resultado(s) único(s):

    → AIzaSyDxVxBvXxBvXxBvXxBvXxBvXxBvXxBvXxB

═══════════════════════════════════════════════════════════
Busca concluída!
Total de padrões processados: 52
Total de matches encontrados: 87
═══════════════════════════════════════════════════════════
```

## 🔧 Argumentos

| Argumento | Alias | Obrigatório | Descrição |
|-----------|-------|-------------|-----------|
| `--file` | `-f` | ✅ | Arquivo alvo para busca (ex: libapp.so) |
| `--json` | `-j` | ✅ | Arquivo JSON com padrões regex |
| `--max-results` | `-m` | ❌ | Número máximo de resultados por padrão (padrão: 20) |
| `--no-color` | - | ❌ | Desabilita cores no output |
| `--help` | `-h` | ❌ | Exibe ajuda |

## 🎯 Casos de Uso

- 🔐 **Análise de segurança**: Encontrar secrets, tokens e credenciais em binários
- 📱 **Engenharia reversa de apps**: Extrair URLs, APIs e configurações de apps Flutter/Android
- 🔍 **Auditoria de código**: Verificar vazamento de informações sensíveis
- 🛡️ **Pen testing**: Identificar pontos de ataque e configurações expostas

## 🧪 Detecção de Base64

O script detecta automaticamente strings Base64 válidas usando os seguintes critérios:

- Comprimento mínimo de 16 caracteres
- Comprimento múltiplo de 4
- Contém apenas caracteres válidos: `A-Z`, `a-z`, `0-9`, `+`, `/`, `=`
- Decodificação resulta em texto UTF-8 legível

Quando uma string Base64 é encontrada:
1. É decodificada automaticamente
2. A busca é feita no conteúdo decodificado
3. O contexto completo decodificado é exibido no resultado

## 🙏 Créditos

Inspirado no projeto [apkleaks](https://github.com/dwisiswant0/apkleaks) por dwisiswant0.
