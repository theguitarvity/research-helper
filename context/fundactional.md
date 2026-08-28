# Research Helper — Agentic Research Engineering Harness

## 1. Contexto

Este projeto deve criar um **Research Helper multimodal e model-agnostic** para apoiar atividades de pesquisa científica, experimentação, revisão bibliográfica e produção acadêmica.

O Research Helper deve funcionar conceitualmente como um **estagiário de pesquisa digital**, capaz de executar atividades operacionais e repetitivas de pesquisa, organizar evidências, preparar ambientes experimentais e manter memória persistente sobre o trabalho realizado.

O sistema NÃO deve depender de um único modelo ou fornecedor.

O mesmo workspace deve poder ser utilizado por:

- Claude Code;
- OpenAI Codex;
- GitHub Copilot;
- Gemini;
- outros agentes futuros.

O trabalho iniciado por um agente deve poder ser continuado por outro sem depender do histórico da conversa anterior.

O filesystem, os artefatos produzidos, manifests, logs, provenance, grafo de conhecimento e arquivos de handoff devem constituir a **fonte persistente de contexto do projeto**.

O princípio central é:

> Chat is ephemeral. Research artifacts are persistent.

E, operacionalmente:

> Script what is deterministic. Use agents for reasoning.

---

# 2. Objetivo

Construir um harness local de pesquisa científica capaz de:

1. descobrir literatura científica;
2. baixar e organizar papers;
3. extrair referências bibliográficas;
4. resolver referências para documentos reais;
5. verificar se referências existem e correspondem ao que foi citado;
6. baixar automaticamente papers referenciados quando legalmente disponíveis;
7. sintetizar referências;
8. avaliar a relação entre uma citação e o trabalho citado;
9. construir um grafo navegável da literatura;
10. preparar projetos acadêmicos em LaTeX;
11. preparar experimentos científicos;
12. organizar datasets, resultados, evidências e notebooks;
13. manter memória de pesquisa através de Obsidian + Graphify;
14. suportar documentos, imagens, tabelas, gráficos e outros artefatos multimodais;
15. permitir handoff entre diferentes agentes/modelos;
16. minimizar consumo de tokens utilizando automação determinística sempre que possível.

---

# 3. Persona do agente

Nome conceitual:

`research-helper`

O agente deve se comportar como um **Research Assistant / Research Engineering Intern**.

Ele NÃO deve substituir o pesquisador na tomada de decisões científicas.

Seu papel é:

- executar trabalho operacional;
- coletar evidências;
- organizar literatura;
- preparar material;
- estruturar experimentos;
- verificar informações;
- sintetizar conteúdo;
- manter rastreabilidade;
- levantar inconsistências;
- apresentar evidências para decisão humana.

O pesquisador continua sendo responsável pelas conclusões científicas.

---

# 4. Princípios arquiteturais

## 4.1 Script-first

Sempre que uma operação puder ser executada deterministicamente, ela deve preferencialmente ser implementada como script.

Exemplos:

- criação de diretórios;
- geração de manifests;
- download de arquivos;
- cálculo de hashes;
- extração de metadata;
- parsing de DOI;
- parsing de BibTeX;
- extração de referências;
- consulta a APIs científicas;
- normalização de referências;
- deduplicação;
- geração de arquivos Markdown;
- geração de projetos LaTeX;
- execução de experimentos;
- geração de índices;
- atualização do grafo;
- validação estrutural;
- criação de handoff.

O LLM deve orquestrar essas ferramentas em vez de reproduzir manualmente o trabalho.

---

# 5. Token Economy

Tokens devem ser tratados como recurso computacional.

Prioridade:

```text
CLI / Script
    ↓
Structured Data
    ↓
Local Cache
    ↓
Search / Retrieval
    ↓
LLM Reasoning
```

Evitar enviar documentos inteiros ao modelo quando uma operação determinística puder reduzir o contexto.

Exemplo:

```text
paper.pdf
   ↓
extract
   ↓
references.json
   ↓
resolve
   ↓
references-resolved.json
   ↓
filter unresolved/relevant
   ↓
LLM
```

Não:

```text
paper.pdf
   ↓
LLM lê tudo
   ↓
LLM tenta manualmente descobrir referências
```

---

# 6. Arquitetura Agent Skills

Criar uma camada canônica compartilhada.

Estrutura sugerida:

```text
.agent/
├── README.md
├── agents/
│   └── research-helper/
│       ├── README.md
│       ├── AGENT.md
│       └── workflows/
├── skills/
│   ├── literature-search/
│   ├── reference-harvester/
│   ├── citation-validator/
│   ├── paper-synthesizer/
│   ├── latex-scaffolder/
│   ├── experiment-scaffolder/
│   ├── graphify-research/
│   ├── research-memory/
│   ├── multimodal-analysis/
│   └── research-handoff/
├── scripts/
├── schemas/
├── templates/
└── adapters/
```

Criar adapters mínimos para os agentes disponíveis.

Exemplo conceitual:

```text
.claude/
.codex/
.github/
.gemini/
```

Esses diretórios NÃO devem duplicar as skills.

Devem apenas apontar/adaptar as instruções existentes em `.agent/`.

`.agent/` deve ser a **single source of truth**.

---

# 7. Skill — Literature Search

Criar:

`research-helper/literature-search`

Responsável por busca científica estruturada.

Entrada:

```yaml
query: "agentic software engineering"
date:
  from: 2024
  to: 2026
languages:
  - en
max_results: 100
sources:
  - semantic-scholar
  - crossref
  - openalex
```

Avaliar suporte também para fontes adicionais quando APIs, datasets ou mecanismos legais de consulta estiverem disponíveis.

O sistema deve conseguir pesquisar por:

- título;
- autor;
- palavras-chave;
- DOI;
- período;
- venue;
- ano;
- citações;
- referências;
- open access;
- tipo de publicação.

Resultados devem ser normalizados para um schema comum.

Exemplo:

```json
{
  "title": "...",
  "authors": [],
  "year": 2026,
  "doi": "...",
  "venue": "...",
  "abstract": "...",
  "url": "...",
  "pdf_url": "...",
  "open_access": true,
  "source": "openalex"
}
```

Implementar deduplicação preferencialmente por:

1. DOI;
2. normalized title;
3. authors + year.

---

# 8. Skill — Reference Harvester

Criar:

`research-helper/reference-harvester`

Objetivo:

Dado um paper:

```text
paper.pdf
```

produzir:

```text
references/
├── references.raw.json
├── references.normalized.json
├── references.resolved.json
├── references.bib
└── papers/
```

Pipeline:

```text
PDF
 ↓
Text / structured extraction
 ↓
Reference section detection
 ↓
Reference parsing
 ↓
DOI extraction
 ↓
Metadata resolution
 ↓
Deduplication
 ↓
Availability discovery
 ↓
Download
 ↓
Manifest
```

Cada referência deve possuir estado:

```text
DISCOVERED
RESOLVED
VERIFIED
DOWNLOADED
UNAVAILABLE
AMBIGUOUS
INVALID
```

---

# 9. Skill — Citation Validator

Criar:

`research-helper/citation-validator`

Essa skill é diferente de apenas verificar se o paper existe.

Ela deve avaliar três níveis.

## Level 1 — Existence

A referência existe?

Verificar:

- DOI;
- título;
- autores;
- ano;
- venue.

## Level 2 — Bibliographic Consistency

A referência apresentada pelo paper corresponde ao documento encontrado?

Exemplo:

```text
citation:
Smith et al., 2021

resolved:
Smith et al., 2020
```

Deve ser marcada como potencial inconsistência.

## Level 3 — Claim Support

Quando possível, analisar:

```text
claim no paper A
       ↓
citation B
       ↓
paper B
       ↓
evidence
```

E classificar:

```text
SUPPORTED
PARTIALLY_SUPPORTED
NOT_SUPPORTED
CONTRADICTED
UNCLEAR
```

Nunca tratar essa classificação como verdade absoluta.

Sempre armazenar evidência e justificativa.

---

# 10. Evidence-first Research

Toda conclusão produzida pelo agente deve possuir provenance.

Exemplo:

```yaml
claim_id: claim-001
claim: "..."
source:
  paper: paper-023
  pages:
    - 7
evidence: "..."
analysis: "..."
confidence: 0.82
agent: claude
timestamp: ...
```

Distinguir explicitamente:

```text
SOURCE FACT
AGENT INTERPRETATION
RESEARCHER DECISION
```

Nunca misturar esses conceitos.

---

# 11. Skill — Paper Synthesizer

Criar:

`research-helper/paper-synthesizer`

Produzir sínteses estruturadas.

Não produzir apenas "resumo do paper".

Schema mínimo:

```markdown
# Paper

## Metadata

## Research Problem

## Research Question

## Hypothesis

## Methodology

## Dataset

## Experiment

## Results

## Contributions

## Limitations

## Threats to Validity

## Related Work

## Important Claims

## Evidence

## Relevance to Current Research

## Questions Raised

## Researcher's Notes
```

Criar também síntese comparativa para múltiplos papers.

Exemplo:

```text
synthesis/
├── individual/
│   ├── paper-001.md
│   └── paper-002.md
├── comparison.md
├── disagreements.md
├── common-findings.md
└── research-gaps.md
```

---

# 12. Citation Graph

O sistema deve construir automaticamente relações:

```text
Paper A
 ├── cites → Paper B
 ├── cites → Paper C
 └── cites → Paper D

Paper B
 └── cites → Paper E
```

Isso deve alimentar o Graphify.

Permitir futuramente operações como:

```text
find seminal papers
find citation clusters
find common references
find highly connected papers
find isolated claims
find contradictory works
find recent descendants
```

---

# 13. Skill — Graphify Research

Criar:

`research-helper/graphify-research`

Objetivo:

Transformar o laboratório em um knowledge graph.

Tipos de nós:

```text
Paper
Author
Concept
Method
Dataset
Experiment
Claim
Evidence
Tool
Venue
ResearchQuestion
Hypothesis
Result
```

Relações possíveis:

```text
CITES
AUTHORED_BY
SUPPORTS
CONTRADICTS
USES
EXTENDS
IMPLEMENTS
EVALUATES
PRODUCES
MENTIONS
ANSWERS
TESTS
```

Exemplo:

```text
Paper
 ↓ PROPOSES
Method
 ↓ EVALUATED_WITH
Dataset
 ↓ PRODUCES
Result
```

---

# 14. Obsidian Integration

Gerar um vault compatível com Obsidian.

Estrutura sugerida:

```text
vault/
├── Papers/
├── Authors/
├── Concepts/
├── Claims/
├── Experiments/
├── Datasets/
├── Methods/
├── Questions/
├── Daily/
└── Maps/
```

Cada paper:

```markdown
---
type: paper
doi: ...
year: 2026
authors:
  - ...
status: reviewed
---

# Title

## Summary

...

## References

[[Paper B]]
[[Paper C]]

## Concepts

[[Harness Engineering]]
[[Agentic Software Engineering]]
```

O vault deve ser gerado/atualizado por scripts.

Não depender do LLM para criar links manualmente.

---

# 15. Research Memory

A memória do agente deve estar no workspace.

Criar algo equivalente a:

```text
research/
├── memory/
│   ├── current-context.md
│   ├── decisions.md
│   ├── hypotheses.md
│   ├── questions.md
│   ├── discoveries.md
│   └── research-log.md
```

`current-context.md` deve funcionar como um checkpoint compacto.

Um agente novo deve conseguir ler esse arquivo e compreender rapidamente:

- qual pesquisa está sendo realizada;
- qual problema está sendo investigado;
- quais hipóteses existem;
- quais papers são importantes;
- quais experimentos estão ativos;
- quais dúvidas permanecem;
- qual deve ser o próximo trabalho.

---

# 16. Omni Router / Cross-Agent Continuity

Esta é uma requirement fundamental.

O projeto deve suportar:

```text
Claude
   ↓
Codex
   ↓
Gemini
   ↓
Copilot
   ↓
Claude
```

sem perda relevante de estado.

O histórico do chat NÃO pode ser a memória primária.

Criar:

```text
.agent/state/
├── session.json
├── active-task.json
├── research-state.json
└── handoff.md
```

`handoff.md` deve conter, no mínimo:

```markdown
# Research Handoff

## Objective

## Current Task

## What Was Done

## Evidence Collected

## Files Changed

## Commands Executed

## Decisions

## Assumptions

## Open Questions

## Known Problems

## Suggested Next Steps

## Reproduction Commands
```

---

# 17. Machine-readable Handoff

Além de Markdown:

```text
handoff.json
```

Schema conceitual:

```json
{
  "session": "...",
  "previous_agent": "claude",
  "task": "...",
  "status": "...",
  "artifacts": [],
  "commands": [],
  "evidence": [],
  "decisions": [],
  "open_questions": [],
  "next_actions": []
}
```

Isso deve permitir que outro agente faça:

```text
research-helper resume
```

e recupere o contexto.

---

# 18. Multimodal Research

O agente deve ser preparado para analisar:

- PDF;
- Markdown;
- LaTeX;
- imagens;
- gráficos;
- diagramas;
- tabelas;
- slides;
- CSV;
- JSON;
- código;
- notebooks;
- vídeos/transcrições quando suporte existir.

Quando um modelo não possuir capacidade multimodal necessária, o sistema deve registrar a necessidade e permitir delegação/handoff para outro agente/modelo.

Exemplo:

```text
Codex
 ↓
detects figure requiring visual reasoning
 ↓
creates multimodal task
 ↓
Gemini / Claude
 ↓
analysis artifact
 ↓
Codex resumes
```

O resultado deve ser persistido como artefato, não apenas retornado pelo chat.

---

# 19. Skill — LaTeX Scaffolder

Criar:

`research-helper/latex-scaffolder`

Responsável por preparar projetos acadêmicos.

Exemplo:

```bash
research-helper paper init \
  --venue wop \
  --year 2026 \
  --name harness-engineering
```

Resultado:

```text
papers/harness-engineering/
├── main.tex
├── references.bib
├── sections/
│   ├── introduction.tex
│   ├── background.tex
│   ├── methodology.tex
│   ├── results.tex
│   ├── discussion.tex
│   └── conclusion.tex
├── figures/
├── tables/
├── assets/
├── Makefile
├── README.md
└── venue.json
```

Templates devem ser extensíveis.

Exemplos:

```text
templates/latex/
├── generic/
├── sbpc/
├── wop/
├── sbc/
├── ieee/
├── acm/
└── custom/
```

Templates oficiais devem preservar licenças e provenance.

Não inventar requisitos de formatação.

---

# 20. Venue Registry

Criar registry:

```text
venues/
├── sbpc.yaml
├── wop.yaml
├── ieee.yaml
└── acm.yaml
```

Exemplo:

```yaml
name: WOP
template_source: ...
template_version: ...
retrieved_at: ...
requirements:
  pages: ...
  language: ...
  anonymous_review: ...
```

Separar:

```text
verified requirements
```

de:

```text
agent assumptions
```

---

# 21. Skill — Experiment Scaffolder

Criar:

`research-helper/experiment-scaffolder`

Exemplo:

```bash
research-helper experiment init attention-cache
```

Resultado:

```text
experiments/attention-cache/
├── README.md
├── hypothesis.md
├── protocol.md
├── environment/
├── src/
├── scripts/
├── datasets/
├── raw/
├── results/
├── analysis/
├── figures/
├── logs/
└── manifest.yaml
```

---

# 22. Experiment Manifest

Cada experimento deve possuir:

```yaml
experiment:
  id: EXP-001
  title: ...
  created_at: ...
  status: planned

research_question: ...

hypothesis: ...

variables:
  independent: []
  dependent: []
  controlled: []

dataset: ...

environment: ...

reproduction:
  command: ...

outputs: []
```

O objetivo é maximizar reprodutibilidade.

---

# 23. Reproducibility

Sempre registrar quando aplicável:

- comando executado;
- parâmetros;
- commit;
- versão do dataset;
- versão das ferramentas;
- modelo utilizado;
- modelo version;
- prompt/template;
- seed;
- environment;
- timestamp;
- hashes de arquivos relevantes.

Experimentos envolvendo LLM devem registrar adicionalmente:

```text
provider
model
temperature
system prompt
input artifact
output artifact
```

quando essas informações estiverem disponíveis.

---

# 24. Research Laboratory

Estrutura inicial sugerida:

```text
research-lab/
├── README.md
├── CLAUDE.md
├── AGENTS.md
│
├── .agent/
│   ├── agents/
│   ├── skills/
│   ├── scripts/
│   ├── schemas/
│   ├── templates/
│   └── state/
│
├── library/
│   ├── papers/
│   ├── books/
│   ├── articles/
│   └── datasets/
│
├── literature/
│   ├── searches/
│   ├── references/
│   └── synthesis/
│
├── experiments/
│
├── papers/
│
├── graph/
│
├── vault/
│
├── research/
│   └── memory/
│
└── logs/
```

O Spec Master deve avaliar criticamente essa estrutura e propor mudanças quando houver justificativa arquitetural.

---

# 25. Paper Storage

Evitar nomes arbitrários.

Preferir identificadores estáveis.

Exemplo:

```text
library/papers/
└── 10.1145_1234567/
    ├── paper.pdf
    ├── metadata.json
    ├── references.json
    ├── summary.md
    ├── claims.json
    └── manifest.json
```

Quando DOI não existir:

```text
paper-{normalized-hash}/
```

---

# 26. Provenance

Todo documento adquirido deve possuir provenance.

Exemplo:

```json
{
  "source": "openalex",
  "original_url": "...",
  "doi": "...",
  "retrieved_at": "...",
  "sha256": "...",
  "license": "...",
  "open_access": true
}
```

Nunca perder a origem de um artefato científico.

---

# 27. Legal / Ethical Acquisition

Não implementar mecanismos de bypass de paywall.

Priorizar:

- Open Access;
- repositórios institucionais;
- preprints;
- versões autorizadas;
- APIs públicas;
- documentos fornecidos pelo pesquisador.

Quando não for possível baixar:

```text
METADATA_ONLY
```

ou:

```text
PAYWALLED
```

A referência continua registrada no grafo.

---

# 28. Caching

Toda operação externa deve considerar cache.

Exemplo:

```text
.cache/
├── crossref/
├── openalex/
├── semantic-scholar/
├── metadata/
└── extraction/
```

Queries idênticas não devem consumir APIs ou tokens repetidamente sem necessidade.

---

# 29. CLI

Avaliar criação de CLI unificada.

Nome provisório:

```text
research-helper
```

Exemplos:

```bash
research-helper search "harness engineering"

research-helper import paper.pdf

research-helper references extract paper.pdf

research-helper references resolve paper.pdf

research-helper references download paper.pdf

research-helper citations validate paper.pdf

research-helper summarize paper.pdf

research-helper graph build

research-helper vault sync

research-helper paper init --venue wop

research-helper experiment init semantic-cache

research-helper handoff create

research-helper resume
```

A CLI deve ser fina.

A lógica reutilizável deve viver em módulos/bibliotecas.

---

# 30. Structured Output

Scripts devem preferir saída estruturada.

Exemplo:

```bash
research-helper search ... --format json
```

em vez de output exclusivamente humano.

Permitir:

```text
JSON
JSONL
YAML
Markdown
```

conforme apropriado.

Isso reduz necessidade de parsing pelo LLM.

---

# 31. Human-readable + Machine-readable

Sempre que importante, manter ambos.

Exemplo:

```text
summary.md
summary.json

handoff.md
handoff.json

manifest.yaml

references.bib
references.json
```

Markdown serve ao pesquisador.

Dados estruturados servem aos agentes e automações.

---

# 32. Skill README Standard

Todas as skills devem possuir README padronizado.

Template:

```markdown
# Skill Name

## Purpose

## When to Use

## When NOT to Use

## Inputs

## Outputs

## Preconditions

## Workflow

## Scripts / Tools

## Deterministic Operations

## Agent Reasoning Responsibilities

## Token Economy

## Provenance

## Failure Modes

## Recovery

## Cross-Agent Handoff

## Examples

## Validation

## Definition of Done
```

O Spec Master deve reutilizar o padrão já utilizado pelas Agent Skills existentes no ecossistema quando encontrado no repositório.

Não criar convenção incompatível sem necessidade.

---

# 33. Research Task Model

Criar conceito de Research Task.

Exemplo:

```yaml
id: RT-001

type: literature-review

objective:
  Evaluate semantic caching techniques for RAG.

inputs: []

status: running

steps:
  - search-literature
  - download
  - extract-references
  - synthesize
  - graphify

artifacts: []

agent_history:
  - claude
  - codex
```

Isso deve ser independente do modelo.

---

# 34. Agent Boundary

O agente deve saber quando NÃO agir autonomamente.

Exigir confirmação humana para:

- conclusões científicas importantes;
- descarte de evidências;
- classificação definitiva de referências como fraudulentas;
- alteração substancial de hipóteses;
- submissão de papers;
- publicação;
- decisões éticas;
- aquisição não autorizada de conteúdo.

---

# 35. Verification

Nunca assumir que uma referência é verdadeira apenas porque aparece em outro paper.

Resolver utilizando fontes externas independentes quando possível.

Registrar:

```text
verification_sources
```

Uma referência potencialmente inexistente deve ser marcada:

```text
UNVERIFIED
```

antes de:

```text
SUSPECTED_INVALID
```

Nunca usar linguagem acusatória automaticamente.

---

# 36. Confidence

Resultados inferenciais devem poder carregar confidence.

Exemplo:

```json
{
  "classification": "PARTIALLY_SUPPORTED",
  "confidence": 0.73
}
```

Confidence não substitui evidência.

---

# 37. Research Lineage

Manter lineage:

```text
Research Question
      ↓
Literature Search
      ↓
Papers
      ↓
Claims
      ↓
Hypothesis
      ↓
Experiment
      ↓
Evidence
      ↓
Result
      ↓
Paper Section
```

O objetivo futuro é conseguir perguntar:

> De onde veio essa afirmação no nosso artigo?

e reconstruir a cadeia completa.

---

# 38. Search Manifest

Cada busca científica deve ser reprodutível.

Exemplo:

```text
literature/searches/2026-08-harness-engineering/
├── query.yaml
├── raw-results.json
├── normalized.json
├── selected.json
└── README.md
```

`query.yaml`:

```yaml
query: "harness engineering"
sources:
  - openalex
  - semantic-scholar

filters:
  year:
    min: 2024
    max: 2026

executed_at: ...
```

---

# 39. Multimodal Artifacts

Figuras importantes devem poder virar entidades.

Exemplo:

```text
paper.pdf
   ↓
Figure 3
   ↓
figure-003.png
   ↓
figure-003.json
   ↓
analysis.md
```

Registrar:

```text
paper
page
figure
caption
extraction_method
analysis_model
```

O mesmo princípio deve valer para tabelas.

---

# 40. Observability

Registrar atividades do harness.

Exemplo:

```text
logs/
├── research-helper.jsonl
├── agents.jsonl
├── tools.jsonl
└── errors.jsonl
```

Registrar quando possível:

```text
task
agent
tool
duration
cache_hit
tokens
status
artifacts
```

Não armazenar secrets.

---

# 41. Security

Nunca versionar:

```text
API keys
tokens
credentials
private datasets
restricted papers
personal data
```

Preparar:

```text
.env.example
.gitignore
```

e documentação de secrets.

---

# 42. Technology

O Spec Master deve avaliar a stack.

Preferência inicial:

```text
Python 3.12+
uv
Typer
Pydantic
PyYAML
httpx
pytest
```

Para PDF/document processing, avaliar ferramentas especializadas antes de construir parsers manualmente.

Para APIs científicas, priorizar APIs oficiais.

Para Graphify, avaliar compatibilidade com o projeto/ecossistema já existente antes de introduzir nova tecnologia.

Não introduzir banco vetorial, graph database ou infraestrutura distribuída apenas porque são tecnicamente interessantes.

Filesystem-first é aceitável e preferível no MVP.

---

# 43. Progressive Architecture

O MVP deve funcionar localmente.

Não iniciar com:

```text
Kubernetes
Kafka
microservices
distributed databases
```

sem necessidade comprovada.

Preferir inicialmente:

```text
Python modules
CLI
filesystem
SQLite when useful
Git
Obsidian
Graphify
```

A arquitetura deve permitir evolução posterior.

---

# 44. Git as Research Memory

Git deve ser parte do mecanismo de memória.

Commits podem representar checkpoints de pesquisa.

Exemplo:

```text
research(literature): add harness engineering survey

experiment(cache): record baseline results

paper(wop): draft methodology section
```

Handoffs devem incluir commit atual quando disponível.

---

# 45. Agent Session Bootstrap

Cada agente deve possuir um processo equivalente a:

```text
1. Read project instructions
2. Read Research Helper agent definition
3. Read current-context
4. Read active-task
5. Read latest handoff
6. Inspect relevant manifests
7. Continue work
```

Não exigir leitura integral de todo o laboratório.

Isso é essencial para economia de tokens.

---

# 46. Context Layering

Organizar contexto em camadas.

```text
L0 — Constitution
L1 — Research Project
L2 — Current Research Question
L3 — Active Task
L4 — Relevant Evidence
L5 — Raw Artifacts
```

O agente deve carregar apenas as camadas necessárias.

---

# 47. Context Budget

As skills devem documentar estratégias para limitar contexto.

Exemplo:

```text
do not load 50 PDFs
```

Preferir:

```text
metadata
   ↓
abstract
   ↓
structured summaries
   ↓
relevant passages
   ↓
full document only if required
```

---

# 48. Quality Gates

Criar validações automatizadas.

Exemplos:

```text
skill schemas valid
manifests valid
broken wiki links
duplicate DOI
missing provenance
missing hashes
invalid BibTeX
broken LaTeX
missing experiment metadata
invalid handoff
```

Criar comando conceitual:

```bash
research-helper doctor
```

e:

```bash
research-helper validate
```

---

# 49. Testing

Criar:

- unit tests;
- integration tests;
- fixtures;
- golden files quando apropriado.

Fixtures devem incluir:

```text
sample paper
sample references
sample metadata
sample experiment
sample vault
sample handoff
```

APIs externas devem possuir mocks para testes determinísticos.

---

# 50. Bootstrap

Criar scripts equivalentes a:

```text
scripts/bootstrap.*
scripts/doctor.*
scripts/validate.*
```

Considerar Windows, macOS e Linux.

Evitar dependência desnecessária de shell específico.

---

# 51. Documentation

README principal deve explicar:

```text
What is Research Helper?
Architecture
Installation
Quick Start
Research Workflow
Skills
CLI
Graphify
Obsidian
Experiments
LaTeX
Cross-Agent Workflow
Provenance
Reproducibility
Troubleshooting
```

---

# 52. Example End-to-End Workflow

O seguinte cenário deve ser possível:

```bash
research-helper import paper-a.pdf
```

Depois:

```bash
research-helper references extract paper-a
```

Resultado:

```text
47 references discovered
```

Depois:

```bash
research-helper references resolve paper-a
```

Resultado conceitual:

```text
42 verified
3 ambiguous
1 unavailable
1 unresolved
```

Depois:

```bash
research-helper references download paper-a
```

Baixa versões legalmente disponíveis.

Depois:

```bash
research-helper summarize --references paper-a
```

Depois:

```bash
research-helper citations validate paper-a
```

Depois:

```bash
research-helper graph build
research-helper vault sync
```

O pesquisador abre Obsidian e consegue navegar:

```text
Paper A
 ├── Paper B
 │    ├── Paper E
 │    └── Paper F
 ├── Paper C
 └── Paper D
```

com summaries, claims, concepts, evidências e relações.

---

# 53. Example Research Discovery Workflow

```bash
research-helper search \
  "LLM agent software engineering" \
  --from 2024 \
  --to 2026
```

O sistema:

```text
Search APIs
 ↓
Normalize
 ↓
Deduplicate
 ↓
Rank
 ↓
Persist search manifest
 ↓
Download OA papers
 ↓
Generate metadata
 ↓
Optional synthesis
 ↓
Graphify
 ↓
Obsidian
```

---

# 54. Example Paper Creation Workflow

```bash
research-helper paper init \
  --venue wop \
  --name graph-engineering
```

Depois:

```text
research-helper
```

pode conectar:

```text
research question
literature
experiments
evidence
```

às seções do paper.

O agente pode auxiliar a escrever, mas nunca deve fabricar referências.

Toda citação sugerida deve apontar para uma referência resolvida.

---

# 55. Anti-Hallucination Requirement

Esta requirement é crítica.

O Research Helper NÃO deve criar referências bibliográficas baseando-se apenas na memória do modelo.

Uma referência usada como evidência deve possuir registro resolvido.

Preferencialmente:

```text
DOI
OpenAlex ID
Semantic Scholar ID
arXiv ID
URL verificável
```

Quando não houver confirmação:

```text
UNVERIFIED
```

---

# 56. Definition of Done — MVP

O MVP estará pronto quando for possível demonstrar:

1. inicialização de um Research Lab;
2. importação de PDF;
3. extração das referências;
4. resolução automática de uma parte significativa delas;
5. identificação de referências ambíguas;
6. download de referências Open Access;
7. geração de metadata;
8. geração de resumo estruturado;
9. criação de citation graph;
10. geração/sincronização de Obsidian vault;
11. busca científica por tema e período;
12. criação de experimento;
13. criação de projeto LaTeX;
14. execução de `doctor`;
15. execução de `validate`;
16. criação de handoff;
17. retomada da mesma Research Task por outro agente;
18. ausência de dependência obrigatória do histórico do chat.

---

# 57. Spec Master Mission

O `/spec-master` deve iniciar realizando uma auditoria do repositório.

Antes de implementar:

1. identificar padrões existentes de `.agent`, `.claude`, `.codex`, Graphify e Agent Skills;
2. identificar scripts e utilitários que possam ser reutilizados;
3. identificar convenções de documentação existentes;
4. avaliar integrações atualmente suportadas por Claude Code, Codex, Copilot e Gemini;
5. identificar APIs científicas adequadas;
6. avaliar ferramentas open source para PDF/reference extraction antes de construir uma solução própria;
7. verificar os mecanismos existentes do projeto Graphify;
8. definir arquitetura filesystem-first;
9. propor schemas;
10. dividir implementação em Vertical Slices.

Produzir:

```text
app-features.md
project-goals.md
tech-stack.md
architecture.md
research-helper-roadmap.md
```

e ADRs para decisões arquiteturais importantes.

---

# 58. Vertical Slices sugeridos

O Spec Master deve validar/refinar esta ordem:

```text
VS001 — Research Lab Foundation
VS002 — Research Task + State
VS003 — Scientific Search
VS004 — Paper Import
VS005 — Reference Extraction
VS006 — Reference Resolution
VS007 — Open Access Acquisition
VS008 — Structured Paper Synthesis
VS009 — Citation Validation
VS010 — Graphify Integration
VS011 — Obsidian Research Memory
VS012 — Experiment Scaffolder
VS013 — LaTeX / Venue Scaffolder
VS014 — Multimodal Artifacts
VS015 — Cross-Agent Handoff
VS016 — Research Lineage
VS017 — Doctor / Validation / Observability
```

Cada slice deve ser demonstrável isoladamente.

---

# 59. Stop Condition

Nesta execução inicial, o Spec Master NÃO deve implementar todo o Research Helper.

A missão inicial é:

```text
AUDIT
 ↓
RESEARCH
 ↓
ARCHITECTURE
 ↓
SPECIFICATION
 ↓
ROADMAP
```

Parar antes da implementação funcional extensa.

Implementação só deve começar após termos:

- arquitetura definida;
- schemas principais;
- skills planejadas;
- integrações avaliadas;
- Vertical Slices;
- acceptance criteria;
- riscos;
- ADRs necessários.

---

# 60. Quality Bar

Este projeto deve ser tratado como infraestrutura científica.

As prioridades são:

```text
Reproducibility
Traceability
Evidence
Provenance
Interoperability
Automation
Token Efficiency
Model Independence
Researcher Control
```

O sucesso não é fazer o agente "parecer inteligente".

O sucesso é conseguir iniciar uma pesquisa hoje com Claude, continuar amanhã com Codex, delegar uma análise visual para Gemini, voltar para Copilot e, semanas depois, reconstruir exatamente:

- o que foi pesquisado;
- por que foi pesquisado;
- quais fontes foram utilizadas;
- quais referências foram verificadas;
- quais evidências sustentaram cada decisão;
- quais experimentos foram executados;
- como reproduzi-los;
- quem ou qual agente produziu cada análise;
- e qual é o próximo passo da pesquisa.

O **Research Helper deve funcionar como uma camada persistente de Research Engineering entre o pesquisador e qualquer modelo de IA.**