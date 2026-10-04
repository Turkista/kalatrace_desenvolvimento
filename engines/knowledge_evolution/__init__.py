"""
KALATRACE Knowledge Evolution -- Evolução epistemológica das IECs

IMPLEMENTADOS (em uso):
- knowledge_evolution_engine.py -> KnowledgeEvolutionEngine, fachada
  pública do pacote.
- state_transition.py -> StateTransitionManager, estado/transições
  de cada IEC.
- evolution_analyzer.py -> EvolutionAnalyzer, avaliação de evolução
  via evidências + relatórios/diagnóstico.
- conflict_solver.py -> ConflictSolver, registro/classificação/
  resolução de conflitos epistemológicos (DOCUMENTO 3, Art. 73º-77º).
- evidence_merger.py -> EvidenceMerger, mesclagem de evidências de
  múltiplas IECs em uma síntese (DOCUMENTO 3, Art. 30º-IV).

Histórico (roadmap de estabilização, sessão de 07/08/2026): os dois
últimos foram implementados numa sessão posterior à primeira análise
do pacote -- naquele momento não havia nenhuma especificação de
regra de negócio disponível (só o princípio geral em DOCUMENTO 8),
então os dois arquivos ficaram vazios, documentados como placeholder.
O usuário trouxe o DOCUMENTO 3 (Manual Operacional do Sistema
MEDIKALAT + KALATRACE) numa sessão seguinte, com artigos formais
sobre classificação e resolução de conflito -- suficiente para
implementar com segurança. Ver o docstring de cada classe para o que
é regra oficial do documento e o que é interpretação desta
implementação (os limiares numéricos específicos, que o documento
não especifica em nível quantitativo).
"""
