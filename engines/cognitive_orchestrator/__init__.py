"""
KALATRACE Cognitive Orchestrator -- coordenação do ciclo científico

IMPLEMENTADOS (em uso):
- cognitive_orchestrator_engine.py -> CognitiveOrchestrator, fachada
  pública do pacote.
- workflow.py -> definição estática do ciclo cognitivo e dos
  estados oficiais (DOCUMENTO 26, Art. 5º/6º).
- coordinator.py -> CycleCoordinator, estado e histórico por ciclo
  (Art. 6º/9º).
- pipeline.py -> CyclePipeline, execução real dos passos contra os
  engines que já existem no projeto.

Implementado em 08/08/2026 (roadmap de estabilização), depois de
ManualAcquisition, KnowledgeEvolutionEngine, CuriosityEngine e
ScientificResearchEngine já existirem, mas serem ligados
manualmente dentro de run.py/app.py -- exatamente o problema que o
DOCUMENTO 26, Art. 7º, descreve ("os módulos não deverão depender
diretamente uns dos outros; toda comunicação ocorrerá por
intermédio do Cognitive Orchestrator").

Dois passos do ciclo oficial (Scientific Context Reconstruction,
Research Strategy Engine) ainda não têm módulo real no projeto --
o pipeline os registra como SKIPPED explicitamente a cada ciclo,
nunca os ignora silenciosamente. Ver workflow.py.

Ver também core/orchestrator/ e agents/__init__.py: dois outros
pacotes com nomes parecidos ("orchestrator"), mas sem nenhuma
especificação em documento oficial encontrado até agora -- não são
este módulo, e não foram usados como base dele.
"""
