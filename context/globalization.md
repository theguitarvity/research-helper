# 61. Global Installation / Cross-Platform Bootstrap

O `research-helper` deve poder ser instalado e utilizado globalmente, fora de um repositório específico.

O objetivo é permitir que o pesquisador execute:

```bash
research-helper
```

em qualquer laboratório, diretório ou projeto de pesquisa.

O suporte alvo deve incluir:

```text
Windows
Linux
macOS
Android
```

Android deve ser considerado principalmente através de ambientes compatíveis com terminal, como Termux ou equivalente.

---

## 61.1 Global CLI

A CLI deve possuir instalação global.

Exemplo esperado:

```bash
research-helper init
research-helper doctor
research-helper search "agentic software engineering"
research-helper paper import paper.pdf
```

O agente deve detectar automaticamente o workspace atual.

Prioridade de resolução:

```text
Current Directory
    ↓
Nearest Research Lab Root
    ↓
User Global Configuration
```

---

## 61.2 Installation Strategy

Evitar dependência obrigatória de Docker.

O caminho principal deve utilizar Python + `uv`, permitindo uma instalação semelhante a:

```bash
uv tool install research-helper
```

ou mecanismo equivalente suportado pelo ecossistema escolhido.

Também avaliar suporte para:

```bash
pipx install research-helper
```

como fallback.

A instalação deve resultar em um executável global:

```text
research-helper
```

---

## 61.3 Bootstrap Script

Criar bootstrap multiplataforma.

Estrutura sugerida:

```text
scripts/
├── bootstrap.py
├── bootstrap.ps1
├── bootstrap.sh
└── bootstrap-termux.sh
```

`bootstrap.py` deve concentrar o máximo possível de lógica multiplataforma.

Os scripts específicos de shell devem ser wrappers mínimos.

Princípio:

```text
bootstrap.ps1 ─┐
bootstrap.sh  ─┼──> bootstrap.py
Termux       ──┘
```

Evitar duplicação de lógica entre sistemas operacionais.

---

## 61.4 Universal Installer

Avaliar a criação de um instalador universal que possa ser utilizado diretamente a partir do repositório.

Fluxo conceitual:

### Linux / macOS

```bash
curl ... | sh
```

### Windows

```powershell
irm ... | iex
```

### Android / Termux

```bash
curl ... | bash
```

Entretanto, o projeto NÃO deve depender exclusivamente de execução remota de scripts.

Também documentar instalação manual e auditável.

---

## 61.5 Platform Detection

O bootstrap deve identificar:

```text
Operating System
Architecture
Shell
Python availability
uv availability
Git availability
LaTeX availability
Optional research tools
```

Arquiteturas mínimas a considerar:

```text
x86_64
arm64
```

---

## 61.6 Android / Termux

Android deve possuir suporte de primeira classe dentro das limitações da plataforma.

O alvo inicial deve ser:

```text
Android
   ↓
Termux
   ↓
Python
   ↓
uv / pip-compatible environment
   ↓
research-helper CLI
```

O Research Helper no Android deve conseguir executar ao menos:

- busca bibliográfica;
- gerenciamento de metadata;
- organização do laboratório;
- criação de manifests;
- Graphify baseado em arquivos;
- Obsidian Vault;
- geração de Markdown;
- handoffs;
- sincronização via Git;
- APIs científicas;
- tarefas leves de síntese quando um provider remoto estiver configurado.

Funcionalidades dependentes de ferramentas desktop devem ser marcadas explicitamente como opcionais ou indisponíveis.

Exemplo:

```text
CAPABILITY_AVAILABLE
CAPABILITY_DEGRADED
CAPABILITY_UNAVAILABLE
```

---

# 62. Platform Capability Matrix

Criar uma matriz mantida pelo projeto.

Exemplo:

| Capability | Windows | macOS | Linux | Android/Termux |
|---|---|---|---|---|
| Research CLI | Yes | Yes | Yes | Yes |
| Literature Search | Yes | Yes | Yes | Yes |
| Reference Resolution | Yes | Yes | Yes | Yes |
| Git Integration | Yes | Yes | Yes | Yes |
| Obsidian Vault Generation | Yes | Yes | Yes | Yes |
| Graphify | Yes | Yes | Yes | Yes |
| PDF Parsing | Yes | Yes | Yes | Partial/Yes |
| LaTeX Build | Yes | Yes | Yes | Optional |
| Local LLM | Optional | Optional | Optional | Limited |
| Multimodal Local Models | Optional | Optional | Optional | Limited |

Essa matriz deve ser validada automaticamente pelo `doctor`.

---

# 63. research-helper doctor

O comando:

```bash
research-helper doctor
```

deve detectar o ambiente atual.

Exemplo:

```text
Research Helper Doctor

Platform:
  OS: macOS
  Architecture: arm64
  Shell: zsh

Core:
  Python ............. OK
  uv ................. OK
  Git ................ OK

Research:
  PDF extractor ...... OK
  Graphify ........... OK
  Obsidian Vault ..... OK

Academic:
  LaTeX .............. MISSING
  BibTeX ............. MISSING

Agents:
  Claude Code ........ FOUND
  Codex .............. FOUND
  Gemini ............. NOT FOUND
  Copilot ............ FOUND

Status:
  CORE READY
```

O mesmo comando deve funcionar em Windows, Linux, macOS e Termux.

---

# 64. Global Configuration

Criar configuração de usuário global.

Usar convenções do sistema operacional.

Exemplos conceituais:

### Linux

```text
~/.config/research-helper/
```

### macOS

```text
~/Library/Application Support/research-helper/
```

ou diretório XDG quando apropriado.

### Windows

```text
%APPDATA%\research-helper\
```

### Android / Termux

```text
~/.config/research-helper/
```

Não espalhar configurações arbitrariamente pelo filesystem.

---

# 65. Global Agent Skills

A instalação global deve disponibilizar também as skills.

Exemplo conceitual:

```text
~/.research-helper/
├── agent/
│   ├── skills/
│   ├── schemas/
│   └── templates/
├── config/
├── cache/
└── state/
```

Entretanto, projetos locais podem sobrescrever ou estender essas skills.

Resolução:

```text
Project Skill
   ↓ overrides
User Skill
   ↓ overrides
Built-in Skill
```

Isso permite personalização sem modificar a instalação original.

---

# 66. Global Agent Installation

Criar comando:

```bash
research-helper agents install
```

responsável por instalar/adaptar as instruções do Research Helper nos agentes encontrados.

Exemplo:

```text
Detected:

Claude Code
Codex
GitHub Copilot
Gemini
```

O instalador deve criar apenas adapters.

Nunca duplicar o conteúdo completo das skills.

Exemplo:

```text
Claude adapter
     ↓
.agent canonical skills

Codex adapter
     ↓
.agent canonical skills

Gemini adapter
     ↓
.agent canonical skills
```

---

# 67. Workspace Bootstrap

Em qualquer diretório:

```bash
research-helper init
```

deve transformar o diretório atual em um Research Lab.

Exemplo:

```text
research-helper init
```

gera:

```text
.agent/
research/
library/
literature/
experiments/
papers/
graph/
vault/
logs/
research-helper.yaml
```

Também deve ser possível:

```bash
research-helper init ~/research/agentic-se
```

---

# 68. Portable Research Lab

Um laboratório deve permanecer portável entre sistemas operacionais.

Este cenário deve funcionar:

```text
macOS
  ↓ git push
Windows
  ↓ git pull
Linux
  ↓ continue research
Android
  ↓ review / search / annotate
```

Não persistir caminhos absolutos específicos de SO dentro do estado do projeto quando puder ser evitado.

Errado:

```text
C:\Users\Victor\research\paper.pdf
```

Preferir:

```text
library/papers/paper.pdf
```

---

# 69. Path Abstraction

Toda lógica deve utilizar APIs de path portáveis.

Em Python:

```text
pathlib
```

deve ser preferido.

Evitar concatenar manualmente:

```text
"/"
```

ou:

```text
"\\"
```

Toda serialização persistente deve preferir paths relativos ao workspace.

---

# 70. Shell Independence

O core não deve depender de:

```text
bash
zsh
PowerShell
cmd
```

Scripts shell devem apenas inicializar o runtime.

Lógica real:

```text
Python
```

ou outro runtime multiplataforma escolhido pelo Spec Master.

---

# 71. Update Mechanism

Criar:

```bash
research-helper self update
```

ou utilizar diretamente o mecanismo do package manager.

Exemplo preferencial:

```bash
uv tool upgrade research-helper
```

O Research Helper pode abstrair isso através de:

```bash
research-helper update
```

O comando deve detectar como o software foi instalado.

---

# 72. Versioning

Expor:

```bash
research-helper --version
```

E registrar versão nos artefatos relevantes.

Exemplo:

```yaml
generated_by:
  tool: research-helper
  version: 0.4.2
```

Isso é importante para reprodutibilidade científica.

---

# 73. Offline-first Behavior

Operações que não precisam de internet devem continuar funcionando offline.

Exemplo:

```text
Graph build
Vault sync
Experiment scaffolding
LaTeX scaffolding
Reference parsing
Local search
Handoff
Validation
```

Operações externas devem falhar de maneira controlada.

Exemplo:

```text
OFFLINE
Using cached OpenAlex result from 2026-08-25
```

---

# 74. Global Cache

O usuário pode possuir cache compartilhado global.

Exemplo:

```text
~/.cache/research-helper/
```

Isso evita baixar ou consultar repetidamente o mesmo paper entre projetos diferentes.

Exemplo:

```text
Project A
     ↓
DOI X
     ↓
Global Cache

Project B
     ↓
DOI X
     ↓
CACHE HIT
```

O laboratório deve manter sua própria provenance mesmo quando o artefato vier do cache global.

---

# 75. Content-addressable Storage

Avaliar armazenamento por hash para documentos globais.

Exemplo:

```text
cache/objects/
└── sha256/
    └── ab/
        └── abc123...
```

Projetos podem referenciar os objetos sem downloads duplicados.

Isso deve ser avaliado pelo Spec Master como otimização posterior e não bloquear o MVP.

---

# 76. Global Templates

Templates acadêmicos também devem poder ser instalados globalmente.

Exemplo:

```bash
research-helper template list

research-helper template install sbc

research-helper template update sbc
```

Projeto local pode piná-los.

Exemplo:

```yaml
venue:
  template: sbc
  version: 2026.1
```

Isso evita que uma atualização global altere silenciosamente um paper existente.

---

# 77. Bootstrap Acceptance Criteria

A implementação global estará correta quando os seguintes cenários passarem:

### Windows

```powershell
research-helper doctor
research-helper init research-test
```

### macOS

```bash
research-helper doctor
research-helper init research-test
```

### Linux

```bash
research-helper doctor
research-helper init research-test
```

### Android / Termux

```bash
research-helper doctor
research-helper init research-test
```

E o mesmo projeto criado em um sistema operacional deve poder ser aberto e continuado nos outros sem migração manual.

---

# 78. Design Principle

A distribuição deve seguir:

```text
One Core
   +
One CLI
   +
One Skill Repository
   +
Thin Platform Adapters
```

e NÃO:

```text
Windows implementation
macOS implementation
Linux implementation
Android implementation
```

O objetivo é minimizar divergência entre plataformas e garantir que qualquer correção realizada no core beneficie todas elas.

---

# 79. New Critical Requirement

A capacidade de globalização deve ser considerada parte do MVP arquitetural.

O Spec Master deve garantir desde o início que nenhuma decisão fundamental torne o Research Helper dependente de:

- um repositório específico;
- um sistema operacional;
- um shell específico;
- um modelo específico;
- um IDE específico;
- um provider específico;
- paths absolutos;
- Docker;
- histórico de chat.

O `research-helper` deve ser tratado como uma **ferramenta global de Research Engineering**, da mesma forma que ferramentas como `git`, `uv` ou `pytest` acompanham o desenvolvedor entre projetos.