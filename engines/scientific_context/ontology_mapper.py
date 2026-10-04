"""
Ontology Mapper -- ainda não implementado.

Mapearia cada IEC para a Ontologia Científica do KALATRACE
(DOCUMENTO 29 -- Ontologia Científica -- e DOCUMENTO 30 --
Ontologia Epistemológica), permitindo respostas reais para a
Seção 15.4 do DOCUMENTO 23 ("Mecanismos Biológicos") em
context_builder.py, hoje explicitamente marcada como não
determinável.

Escopo (roadmap de estabilização, sessão de 08/08/2026): a
Ontologia Científica define categorias (Entidades Biológicas,
Clínicas, Processo Científico, Recursos Científicos),
relacionamentos com semântica própria (causa, inibe, ativa,
contradiz...) e restrições (quais relações são válidas entre quais
tipos) -- um sistema de tipos e regras por si só, não uma tarefa de
reorganização de código. Implementar isso exige decisão de escopo
do usuário sobre quais categorias/relações priorizar primeiro, não
uma escolha de engenharia isolada.
"""
