from typing import Dict, Any, List
from datetime import datetime, UTC

from contracts.evidence_contract import EvidenceContract
from storage.evidence_store import EvidenceStore



class ScientificResearchEngine:
    """
    Scientific Research Engine (SRE)

    Motor responsável pela investigação científica
    ativa dentro do KALATRACE.

    Responsabilidades:

    - receber perguntas de pesquisa;
    - estruturar investigações;
    - analisar contexto;
    - registrar descobertas;
    - alimentar evolução do conhecimento.

    O SRE não substitui pesquisadores.
    Ele organiza e governa processos
    de investigação.

    Migrado de core/scientific_research_engine.py para
    engines/scientific_research/ (T1.3b, sessão de 03/08/2026).
    Nenhum consumidor de produção real usava o caminho antigo antes
    da migração (checado por busca exaustiva). Diferente da T1.3a: os
    outros arquivos vazios deste pacote (scopus_client.py,
    pubmed_client.py, crossref_client.py, semantic_scholar_client.py,
    search_pipeline.py, parser.py) não parecem ser um split desta
    classe -- parecem ser uma capacidade futura e separada (clientes
    de busca em bases externas de literatura científica), já que esta
    classe não faz nenhuma chamada externa hoje, só organiza e
    rastreia o processo de pesquisa internamente. Não presumido nem
    decidido aqui; a classe foi movida inteira, sem redesenho.

    ENGINE-007 -- resolvido em 09/08/2026: os 6 arquivos citados
    acima foram removidos (ver __init__.py deste pacote). Eram, de
    fato, capacidade futura -- mas equivalente ao que já havia sido
    implementado, com nomes mais completos, em acquisition/.
    """


    def __init__(
        self,
        evidence_store: EvidenceStore
    ):

        self.evidence_store = evidence_store


        # pesquisas em execução

        self.research_tasks: List[
            Dict[str, Any]
        ] = []


        # descobertas registradas

        self.discoveries: List[
            Dict[str, Any]
        ] = []


        # histórico operacional

        self.history: List[
            Dict[str, Any]
        ] = []



    # ==========================================================
    # REGISTRO INTERNO
    # ==========================================================

    def _register_event(
        self,
        event: str,
        details: Dict[str, Any]
    ):

        self.history.append(

            {
                "event":
                    event,

                "details":
                    details,

                "timestamp":
                    datetime.now(UTC)
                    .isoformat()
            }

        )
    # ==========================================================
    # 1. RECEBER TAREFA DE PESQUISA
    # ==========================================================

    def receive_research_task(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recebe uma tarefa criada pelo
        CuriosityEngine.

        A tarefa entra no ciclo
        de investigação científica.
        """


        if not isinstance(
            task,
            dict
        ):

            raise TypeError(
                "A tarefa precisa ser um dicionário"
            )



        research_plan = (
            self.create_research_plan(
                task
            )
        )


        self.research_tasks.append(
            research_plan
        )


        self._register_event(

            "research_task_received",

            {
                "task_id":
                    task.get(
                        "task_id"
                    ),

                "iec_id":
                    task.get(
                        "iec_id"
                    )

            }

        )


        return research_plan



    # ==========================================================
    # 2. CRIAR PLANO DE PESQUISA
    # ==========================================================

    def create_research_plan(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transforma uma pergunta de pesquisa
        em um plano investigativo.
        """


        plan = {

            "research_id":
                f"SR-{len(self.research_tasks)+1}",


            "task_id":
                task.get(
                    "task_id"
                ),


            "iec_id":
                task.get(
                    "iec_id"
                ),


            "research_question":
                task.get(
                    "questions",
                    []
                ),


            "objectives":
                self._define_objectives(
                    task
                ),


            "strategy":
                self._define_strategy(
                    task
                ),


            "status":
                "PLANNED",


            "created_at":
                datetime.now(UTC)
                .isoformat()

        }


        self._register_event(

            "research_plan_created",

            plan

        )


        return plan



    # ==========================================================
    # 3. DEFINIR OBJETIVOS
    # ==========================================================

    def _define_objectives(
        self,
        task: Dict[str, Any]
    ) -> List[str]:
        """
        Define objetivos científicos
        da investigação.
        """

        objectives = []


        questions = task.get(
            "questions",
            []
        )


        for question in questions:

            objectives.append(

                f"Investigar: {question}"

            )


        if not objectives:

            objectives.append(

                "Coletar evidências científicas "
                "relacionadas à IEC"

            )


        return objectives



    # ==========================================================
    # 4. DEFINIR ESTRATÉGIA
    # ==========================================================

    def _define_strategy(
        self,
        task: Dict[str, Any]
    ) -> str:
        """
        Define abordagem inicial
        de pesquisa.
        """

        priority = task.get(
            "priority",
            5
        )


        if priority == 1:

            return "URGENT_INVESTIGATION"


        if priority == 2:

            return "DEEP_LITERATURE_ANALYSIS"


        if priority == 3:

            return "TARGETED_RESEARCH"


        return "BACKGROUND_REVIEW"
    # ==========================================================
    # 5. EXECUTAR PLANO DE PESQUISA
    # ==========================================================

    def execute_research(
        self,
        research_id: str
    ) -> Dict[str, Any]:
        """
        Inicia um ciclo de investigação.

        Nesta primeira versão:
        - prepara a estrutura;
        - registra o ciclo;
        - aguarda integração futura
          com fontes científicas.
        """


        research = (
            self._find_research(
                research_id
            )
        )


        if research is None:

            raise ValueError(
                f"Pesquisa {research_id} não encontrada"
            )



        research["status"] = (
            "RESEARCHING"
        )


        research["started_at"] = (
            datetime.now(UTC)
            .isoformat()
        )



        self._register_event(

            "research_started",

            {
                "research_id":
                    research_id

            }

        )


        return research



    # ==========================================================
    # 6. LOCALIZAR PESQUISA
    # ==========================================================

    def _find_research(
        self,
        research_id: str
    ):
        """
        Localiza um plano de pesquisa.
        """

        for research in self.research_tasks:

            if (
                research["research_id"]
                == research_id
            ):

                return research


        return None



    # ==========================================================
    # 7. REGISTRAR DESCOBERTA
    # ==========================================================

    def register_discovery(
        self,
        research_id: str,
        discovery: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Registra um resultado encontrado
        durante uma investigação.

        A descoberta pode futuramente
        gerar uma nova EvidenceContract.
        """


        research = (
            self._find_research(
                research_id
            )
        )


        if research is None:

            raise ValueError(
                f"Pesquisa {research_id} não encontrada"
            )



        record = {

            "research_id":
                research_id,


            "iec_id":
                research["iec_id"],


            "discovery":
                discovery,


            "created_at":
                datetime.now(UTC)
                .isoformat()

        }



        self.discoveries.append(
            record
        )


        self._register_event(

            "discovery_registered",

            record

        )


        return record



    # ==========================================================
    # 8. ADICIONAR EVIDÊNCIA ENCONTRADA
    # ==========================================================

    def add_discovered_evidence(
        self,
        evidence: EvidenceContract
    ):
        """
        Adiciona uma evidência encontrada
        durante a pesquisa.

        Integração direta:

        SRE → EvidenceStore
        """


        if not isinstance(
            evidence,
            EvidenceContract
        ):

            raise TypeError(
                "Precisa ser um EvidenceContract"
            )



        evidence.validate()



        evidence_id = (
            self.evidence_store
            .add_evidence(
                evidence
            )
        )


        self._register_event(

            "evidence_added_from_research",

            {
                "evidence_id":
                    evidence_id

            }

        )


        return evidence_id
    # ==========================================================
    # 9. ANALISAR RELAÇÃO DA DESCOBERTA
    # ==========================================================

    def analyze_discovery_relation(
        self,
        discovery: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analisa como uma descoberta
        se relaciona com o conhecimento existente.

        Relações possíveis:

        - CONFIRMS
        - CONTRADICTS
        - EXPANDS
        - UNRELATED
        """


        relation = (
            self._determine_relation(
                discovery,
                context
            )
        )



        result = {

            "discovery":
                discovery,


            "context":
                context,


            "relation":
                relation,


            "analyzed_at":
                datetime.now(UTC)
                .isoformat()

        }



        self._register_event(

            "discovery_context_analyzed",

            result

        )


        return result



    # ==========================================================
    # 10. DETERMINAR RELAÇÃO
    # ==========================================================

    def _determine_relation(
        self,
        discovery: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Primeira versão heurística.

        Futuramente poderá usar:

        - modelos de linguagem;
        - ontologias;
        - grafos;
        - embeddings científicos.
        """


        if discovery.get(
            "supports"
        ):

            return "CONFIRMS"



        if discovery.get(
            "contradicts"
        ):

            return "CONTRADICTS"



        if discovery.get(
            "extends"
        ):

            return "EXPANDS"



        return "UNRELATED"



    # ==========================================================
    # 11. CONSTRUIR CONTEXTO CIENTÍFICO
    # ==========================================================

    def reconstruct_context(
        self,
        iec_id: str,
        discoveries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Reconstrói um contexto científico
        inicial de uma IEC.

        Agrupa descobertas por relação.
        """


        context = {

            "iec_id":
                iec_id,


            "confirmations":
                [],


            "contradictions":
                [],


            "extensions":
                [],


            "unrelated":
                []

        }



        for item in discoveries:


            relation = item.get(
                "relation"
            )


            if relation == "CONFIRMS":

                context[
                    "confirmations"
                ].append(item)



            elif relation == "CONTRADICTS":

                context[
                    "contradictions"
                ].append(item)



            elif relation == "EXPANDS":

                context[
                    "extensions"
                ].append(item)



            else:

                context[
                    "unrelated"
                ].append(item)



        self._register_event(

            "scientific_context_reconstructed",

            context

        )


        return context
    # ==========================================================
    # 12. FINALIZAR PESQUISA
    # ==========================================================

    def complete_research(
        self,
        research_id: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Finaliza um ciclo de pesquisa.

        Registra o resultado final
        da investigação.
        """


        research = (
            self._find_research(
                research_id
            )
        )


        if research is None:

            raise ValueError(
                f"Pesquisa {research_id} não encontrada"
            )



        research["status"] = (
            "COMPLETED"
        )


        research["result"] = (
            result
        )


        research["completed_at"] = (
            datetime.now(UTC)
            .isoformat()
        )



        self._register_event(

            "research_completed",

            {
                "research_id":
                    research_id,

                "result":
                    result

            }

        )


        return research



    # ==========================================================
    # 13. AVALIAR EVOLUÇÃO DA IEC
    # ==========================================================

    def evaluate_knowledge_evolution(
        self,
        iec_id: str
    ) -> Dict[str, Any]:
        """
        Avalia se uma IEC apresenta
        sinais de evolução do conhecimento.

        Estados possíveis:

        - STABLE
        - EXPANDING
        - QUESTIONED
        - NEEDS_REVIEW
        """


        related = [

            discovery

            for discovery
            in self.discoveries

            if discovery["iec_id"]
            == iec_id

        ]



        confirmations = 0

        contradictions = 0

        expansions = 0



        for item in related:


            relation = (
                item
                .get(
                    "relation"
                )
            )


            if relation == "CONFIRMS":

                confirmations += 1


            elif relation == "CONTRADICTS":

                contradictions += 1


            elif relation == "EXPANDS":

                expansions += 1



        if contradictions > confirmations:

            state = "QUESTIONED"



        elif confirmations > 0 and expansions > 0:

            state = "EXPANDING"



        elif confirmations > 0:

            state = "STABLE"



        else:

            state = "NEEDS_REVIEW"



        result = {

            "iec_id":
                iec_id,


            "confirmations":
                confirmations,


            "contradictions":
                contradictions,


            "expansions":
                expansions,


            "knowledge_state":
                state

        }



        self._register_event(

            "knowledge_evolution_evaluated",

            result

        )


        return result
    # ==========================================================
    # 14. LISTAR PESQUISAS
    # ==========================================================

    def get_researches(
        self
    ) -> List[Dict[str, Any]]:
        """
        Retorna todas as pesquisas
        registradas pelo SRE.
        """

        return self.research_tasks



    # ==========================================================
    # 15. BUSCAR DESCOBERTAS
    # ==========================================================

    def get_discoveries(
        self
    ) -> List[Dict[str, Any]]:
        """
        Retorna todas as descobertas
        geradas pelo motor.
        """

        return self.discoveries



    # ==========================================================
    # 16. EXPORTAR ESTADO DO SRE
    # ==========================================================

    def to_dict(
        self
    ) -> Dict[str, Any]:
        """
        Exporta o estado completo
        do ScientificResearchEngine.
        """

        return {

            "research_tasks":
                self.research_tasks,


            "discoveries":
                self.discoveries,


            "history":
                self.history

        }



    # ==========================================================
    # 17. ESTATÍSTICAS DO MOTOR
    # ==========================================================

    def stats(
        self
    ) -> Dict[str, Any]:
        """
        Retorna métricas internas.
        """

        return {

            "research_tasks":
                len(
                    self.research_tasks
                ),


            "discoveries":
                len(
                    self.discoveries
                ),


            "events":
                len(
                    self.history
                ),


            "engine":
                "ScientificResearchEngine",


            "status":
                "active"

        }



    # ==========================================================
    # 18. LIMPAR ESTADO
    # ==========================================================

    def clear(
        self
    ):
        """
        Limpa pesquisas,
        descobertas e histórico.
        """

        self.research_tasks.clear()

        self.discoveries.clear()

        self.history.clear()



    # ==========================================================
    # 19. HEALTH CHECK
    # ==========================================================

    def health_check(
        self
    ) -> Dict[str, Any]:
        """
        Verifica funcionamento
        do SRE.
        """

        return {

            "scientific_research_engine":
                "OK",


            "evidence_store_connected":
                self.evidence_store is not None,


            "active_research":
                len(
                    self.research_tasks
                )

        }



    # ==========================================================
    # 20. DEBUG
    # ==========================================================

    def __repr__(
        self
    ) -> str:

        state = self.stats()


        return (

            f"ScientificResearchEngine("
            f"researches={state['research_tasks']}, "
            f"discoveries={state['discoveries']}, "
            f"status={state['status']}"
            f")"

        )