"""
KALATRACE Scientific Research -- investigação científica interna

IMPLEMENTADO (em uso):
- scientific_research_engine.py -> ScientificResearchEngine. Organiza
  e rastreia o processo de pesquisa internamente (planos, tarefas,
  descobertas, reconstrução de contexto). Não faz nenhuma chamada
  externa hoje.

ENGINE-007 -- resolvido (roadmap de estabilização, sessão de
09/08/2026): os 6 arquivos placeholder que existiam aqui
(pubmed_client.py, scopus_client.py, crossref_client.py,
semantic_scholar_client.py, search_pipeline.py, parser.py) foram
removidos. Investigação registrada nas sessões de 03/08, 07/08 e
08/08/2026 já havia confirmado que eram nomes espelhados, 0 bytes,
sem nenhum import real no projeto -- e que o pacote correto para
essa camada (DOCUMENTO 23, Parte II, Seção 11, a Knowledge
Acquisition Layer: ScientificSearchEngine, LiteratureRetriever,
ArticleParser) já existia em acquisition/ (topo do projeto),
implementado de verdade em 09/08/2026 (pubmed_connector.py,
crossref_client.py, semantic_scholar.py, acquisition_pipeline.py,
doi_resolver.py, iec_builder.py). Manter os dois em paralelo teria
recriado a mesma armadilha de nomenclatura duplicada já vista antes
no projeto (ex. "KnowledgeNode", "Orquestrador Cognitivo") -- por
isso a remoção, em vez de manter como duplicata desatualizada.

Scopus continua fora de acquisition/ por exigir credencial paga
(decisão já registrada lá); não há client Scopus em nenhum lugar
do projeto hoje.
"""
