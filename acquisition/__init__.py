"""
KALATRACE Acquisition -- Knowledge Acquisition Layer

Camada de aquisição de conhecimento do KALATRACE (DOCUMENTO 23 --
Arquitetura de Aquisição, Contextualização e Construção do
Conhecimento Científico, Seção 11 "Os Novos Módulos da Camada de
Aquisição").

IMPLEMENTADO (em uso):
- manual_acquisition.py -> ManualAcquisition (Aquisição Experimental
  Manual, Seção 8.1). Sem dependência externa. Movido para cá em
  07/08/2026 -- havia sido criado por engano em
  engines/acquisition/ numa sessão anterior, sem checar que este
  pacote (mais completo e melhor nomeado) já existia.
- source_connector.py, api_client.py -> infraestrutura HTTP/auth
  compartilhada entre os clientes de fonte (SourceConnector, o
  contrato comum com search()/fetch_by_id() e o formato de
  registro normalizado; APIClient, o cliente HTTP com rate
  limiting e retry/backoff). Implementado em 09/08/2026.
- pubmed_connector.py, crossref_client.py, semantic_scholar.py ->
  os 3 clientes de fonte já nomeados no DOCUMENTO 23
  (PubMedConnector via E-utilities do NCBI, CrossrefClient via a
  REST API do CrossRef, SemanticScholarClient via a Academic Graph
  API). Cada um implementa search() (ScientificSearchEngine) e
  fetch_by_id() (LiteratureRetriever) contra SourceConnector.
  Implementado em 09/08/2026 -- mais completos que os nomes
  espelhados em engines/scientific_research/, que devem ser
  considerados a versão desatualizada desses mesmos arquivos e
  removidos (ver nota lá, ainda pendente).
- acquisition_pipeline.py -> AcquisitionPipeline, que orquestra o
  fluxo de aquisição automatizada ponta a ponta (equivalente ao
  trecho Aquisição -> Normalização do fluxo da Seção 10 do
  DOCUMENTO 23; a Construção de IECs continua fora daqui -- ver
  doi_resolver.py abaixo). Consome os 3 clientes de fonte acima
  (antes só usáveis isoladamente, nenhum ponto do projeto os
  chamava) e o DOIResolver. Implementado em 09/08/2026.
- doi_resolver.py -> DOIResolver, que resolve DOIs para
  identificar/desduplicar publicações entre as 3 fontes antes de
  criar IECs, aproveitando o `doi` já normalizado que cada cliente
  devolve em todo registro. Usado por AcquisitionPipeline.run(),
  mas também utilizável isoladamente contra qualquer lista de
  registros no formato canônico. Implementado em 09/08/2026.
- iec_builder.py -> IECBuilder, o módulo de Construção de IECs da
  Seção 11 citado como pendente em todos os arquivos acima até
  agora. Converte tanto ManualAcquisition.capture() quanto os
  registros de AcquisitionPipeline.run()["records"] em IECs de
  verdade, via engines.base.base_engine.CoreEngine.create_iec (o
  único construtor real de IEC do projeto), preservando
  rastreabilidade completa de origem em iec.metadata. Não escreve
  no grafo sozinho -- ver api/main.py, POST /acquisition/search-and-build
  e POST /acquisition/build-iecs, que já fazem essa composição
  completa (busca -> construção -> grafo -> inferência).
  Implementado em 09/08/2026.

PLACEHOLDERS (0 bytes, não implementados -- Aquisição Científica
Automatizada, Seção 8.2): exigem integração real com bases
externas, autenticação e limites de uso por fonte.

- document_loader.py, html_reader.py, pdf_reader.py, xml_reader.py
  -> ArticleParser (Seção 11) por formato de origem -- os 3
  clientes acima só cobrem metadados/resumo, não o texto completo.
  IECBuilder já funciona sem eles (constrói a partir de
  título+resumo); quando existirem, passam a alimentar um `content`
  mais completo para o mesmo IECBuilder, não um caminho paralelo.

Nota (roadmap de estabilização, sessão de 08/08/2026, ainda
pendente após a implementação de 09/08/2026 acima): os 6 arquivos
equivalentes em engines/scientific_research/ (pubmed_client.py,
scopus_client.py, crossref_client.py, semantic_scholar_client.py,
search_pipeline.py, parser.py, documentados como pendentes em
ENGINE-007) continuam sendo a duplicata desatualizada desta camada
e devem ser removidos, não mantidos em paralelo.
"""
