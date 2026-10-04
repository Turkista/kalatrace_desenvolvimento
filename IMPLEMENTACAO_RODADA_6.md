# KALATRACE v8 — Integração Frontend ↔ Backend

## Entregue
- Cliente autenticado único reutilizando `ktApi()`.
- Catálogo dinâmico baseado em `/openapi.json`.
- Filtro de endpoints no painel de integrações.
- Teste direto de endpoints GET sem parâmetros de caminho.
- Endpoints com parâmetros/corpo continuam exigindo ação explícita e usam o explorer existente.
- Bindings de dados reais para Control, Workspace, Projects, CMC, Agente Local, Grafo, Governança, Metacognição, Evidências e Módulos.
- Atualização sob demanda por tela.
- Nenhuma credencial privilegiada é enviada ao frontend.

## Regra de segurança
GETs podem ser consultados pelo painel. Operações de mutação (POST/PATCH/PUT/DELETE) não são disparadas automaticamente: permanecem associadas a ações explícitas da interface e à autorização do backend.

## Próxima etapa
Executar validação de integração em ambiente real com Supabase e Neo4j configurados, revisar contratos de resposta e completar telas de domínio para operações que exigem payloads/contexto.
