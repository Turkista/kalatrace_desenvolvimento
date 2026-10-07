from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from contracts.iec_contract import IECContract
from graph.base.node import Node


class IEC(Node):
    """
    IEC (Informational Epistemic Cell)

    Unidade básica de conhecimento do KALATRACE.

    Um IEC representa uma afirmação, conceito ou
    observação científica passível de evolução
    epistemológica ao longo do tempo.

    O IEC NÃO executa:

    - inferência;
    - validação científica;
    - consenso;
    - descoberta;
    - busca bibliográfica.

    Essas responsabilidades pertencem aos
    Engines, Services e Managers.

    Herança de Node (roadmap de estabilização, T1.2b/c, decisão de
    06/08/2026): IEC agora herda de graph.base.node.Node, a classe
    genérica de nó do KALATRACE. Isso segue a arquitetura oficial
    (DOCUMENTO 72 — Domain Model & Engineering Contracts, "Especificação
    Definitiva para Implementação"): existe uma classe-base para todo
    objeto científico (lá chamada ScientificObject; graph.base.node.Node
    é seu equivalente técnico no código atual), da qual IEC é uma das
    entidades que herdam -- ao lado de Hypothesis, Evidence, Mechanism,
    Experiment, Discovery e outras, não como pai delas. O próprio
    docstring de Node já listava IEC como exemplo antes desta mudança.
    graph/knowledge/knowledge_node.py (KnowledgeNode, a outra opção
    cogitada) não aparece em nenhum documento oficial e não tem nenhum
    consumidor de produção -- não foi usada como base.
    """

    def __init__(
        self,
        id: str,
        content: str,
        domain: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        statement: Optional[str] = None
    ):

        # ==========================================
        # NODE (herança) -- identidade, tipo, label, properties
        # ==========================================
        # Node exige node_id, node_type e label não-vazios. `domain` já
        # era opcional aqui (podia ficar None); quando None, cai no
        # mesmo default que engines/base/base_engine.py::create_iec já
        # usava para node_type ("Conhecimento"), então nenhum consumidor
        # real passa a receber um valor novo/inesperado. `label` não
        # existia nesta classe -- como nada no projeto lê `.label` de um
        # IEC hoje, um valor derivado (metadata/title > statement >
        # content > id) preenche a exigência de Node sem mudar
        # comportamento visível.
        label = (
            (metadata or {}).get("title")
            or statement
            or content
            or id
        )

        super().__init__(
            node_id=id,
            node_type=domain or "Conhecimento",
            label=label,
            properties=metadata,
        )

        # ==========================================
        # CONTEÚDO
        # ==========================================

        self.content = content

        # Forma canônica da afirmação científica.
        self.statement = statement or content

        # domain já foi setado por Node.__init__ (via a property
        # node_type -> domain, mantida abaixo por compatibilidade).

        # ==========================================
        # EVIDÊNCIAS E RELAÇÕES
        # ==========================================

        # Objetos de evidência associados.
        self.sources: List[Any] = []

        # IDs das evidências registradas.
        self.evidence_ids: List[str] = []

        # Relações com outros IECs.
        self.related_iec_ids: List[str] = []

        # ==========================================
        # CAMADA EPISTEMOLÓGICA
        # ==========================================

        # Grau atual de confiança.
        self.confidence: float = 0.50

        # Estado epistemológico.
        self.status: str = "candidate"

        # Versão evolutiva.
        self.version: int = 1

        # ==========================================
        # HISTÓRICO
        # ==========================================

        self.history: List[Dict[str, Any]] = []

        # ==========================================
        # CICLO DE VIDA
        # ==========================================
        # Sobrescreve o created_at (string ISO) que Node.__init__ já
        # setou -- IEC sempre expôs created_at/updated_at como objetos
        # datetime, não string, e Repository/APIs/testes dependem disso.

        self.created_at = datetime.now(
            timezone.utc
        )

        self.updated_at = self.created_at

    # ==========================================
    # COMPATIBILIDADE (id -> node_id)
    # ==========================================
    # Mesmo padrão das duas properties acima. IEC sempre expôs a
    # identidade como `self.id` (usado em validate/get_state/to_dict/
    # to_contract/__repr__/__eq__/__hash__ e por todo o resto do
    # projeto). Node guarda a identidade como `self.node_id`. Em vez de
    # reescrever esses métodos, `id` vira um alias de `node_id`.
    @property
    def id(self) -> str:
        return self.node_id

    @id.setter
    def id(self, value: str):
        self.node_id = value

    # ==========================================
    # COMPATIBILIDADE (node_type -> domain)
    # ==========================================
    # Vários pontos do sistema (CoreEngine.create_iec, a API, os
    # scripts run.py/app.py) foram escritos contra um atributo
    # `node_type`, que nunca existiu nesta classe -- o campo real
    # equivalente é `domain`. Property adicionada em vez de alterar
    # esses call-sites: correção mínima e mais segura (mesmo padrão já
    # usado em contracts/evidence_contract.py para `evidence_id`).
    # Mantida após a herança de Node: Node.__init__ faz
    # `self.node_type = node_type`, e por essa property já existir na
    # classe, essa atribuição é redirecionada para `self.domain`
    # automaticamente -- sem precisar de nenhuma mudança aqui.
    @property
    def node_type(self) -> Optional[str]:
        return self.domain

    @node_type.setter
    def node_type(self, value: Optional[str]):
        self.domain = value

    # ==========================================
    # COMPATIBILIDADE (properties -> metadata)
    # ==========================================
    # Mesmo padrão da property node_type acima: Node.__init__ faz
    # `self.properties = ...`, e IEC já tinha seu próprio `metadata`
    # com o mesmo papel (bag de metadados livres). Em vez de manter os
    # dois em paralelo (arriscando divergência), esta property faz
    # `properties` ser um alias direto de `metadata` -- os métodos
    # herdados de Node (add_property/get_property/remove_property/
    # update_properties) passam a operar sobre o mesmo dict que todo o
    # resto do IEC já lia/escrevia como `self.metadata`.
    @property
    def properties(self) -> Dict[str, Any]:
        return self.metadata

    @properties.setter
    def properties(self, value: Optional[Dict[str, Any]]):
        self.metadata = dict(value) if value is not None else {}

    # ==========================================
    # FONTES E EVIDÊNCIAS
    # ==========================================

    def add_source(self, source: Any):
        """
        Adiciona uma fonte ao IEC.

        A fonte pode representar:

        - artigo científico;
        - experimento;
        - ensaio clínico;
        - revisão sistemática;
        - documento;
        - dataset;
        - qualquer objeto de evidência.

        O IEC apenas registra a associação.
        A validação pertence ao Evidence Engine.
        """

        self.sources.append(source)

        self._register_history(
            event="source_added",
            data={
                "source": source
            }
        )

        self._touch()


    def add_evidence(self, evidence_id: str):
        """
        Associa uma evidência ao IEC.

        Recebe apenas o identificador da evidência.
        O objeto completo permanecerá no EvidenceStore.
        """

        if evidence_id not in self.evidence_ids:

            self.evidence_ids.append(
                evidence_id
            )

            self._register_history(
                event="evidence_added",
                data={
                    "evidence_id": evidence_id
                }
            )

            self._touch()


    # ==========================================
    # RELAÇÕES COM OUTROS IECS
    # ==========================================

    def add_relation(self, iec_id: str):
        """
        Cria uma relação entre este IEC
        e outro IEC do Knowledge Graph.
        """

        if iec_id not in self.related_iec_ids:

            self.related_iec_ids.append(
                iec_id
            )

            self._register_history(
                event="relation_added",
                data={
                    "related_iec": iec_id
                }
            )

            self._touch()
    # ==========================================
    # CONFIANÇA EPISTEMOLÓGICA
    # ==========================================

    def set_confidence(self, value: float):
        """
        Define explicitamente o nível de confiança.

        Este método normalmente é utilizado pelo
        Confidence Engine após calcular o novo
        score epistemológico do IEC.
        """

        previous = self.confidence

        self.confidence = max(
            0.0,
            min(1.0, float(value))
        )

        self._register_history(
            event="confidence_set",
            data={
                "previous": previous,
                "new": self.confidence
            }
        )

        self._touch()


    def update_confidence(self, value: float):
        """
        Atualiza o nível de confiança.

        Mantido por compatibilidade com versões
        anteriores do KALATRACE.
        """

        self.set_confidence(value)


    def reinforce(self, delta: float = 0.05):
        """
        Reforça a confiança do IEC.

        Utilizado quando novas evidências
        fortalecem o conhecimento.
        """

        self.set_confidence(
            self.confidence + delta
        )


    def weaken(self, delta: float = 0.05):
        """
        Reduz a confiança do IEC.

        Utilizado quando surgem
        evidências conflitantes.
        """

        self.set_confidence(
            self.confidence - delta
        )


    # ==========================================
    # VALIDAÇÃO EPISTEMOLÓGICA
    # ==========================================

    def validate(self):
        """
        Valida a integridade estrutural do IEC.

        Não executa validação científica,
        apenas garante que o objeto está
        consistente.
        """

        if not self.id:
            raise ValueError(
                "IEC precisa possuir um ID."
            )

        if not self.content:
            raise ValueError(
                "IEC precisa possuir conteúdo."
            )

        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError(
                "Confidence deve estar entre 0 e 1."
            )

        return True


    # ==========================================
    # ESTADO EPISTEMOLÓGICO
    # ==========================================

    def update_status(self, status: str):
        """
        Atualiza o estado epistemológico
        do IEC.
        """

        previous = self.status

        self.status = status

        self._register_history(
            event="status_updated",
            data={
                "previous": previous,
                "new": status
            }
        )

        self._touch()
    # ==========================================
    # HISTÓRICO INTERNO
    # ==========================================

    def _register_history(
        self,
        event: str,
        data: Dict[str, Any]
    ):
        """
        Registra uma alteração no histórico do IEC.

        Cada evento representa uma mudança no
        ciclo de vida epistemológico da unidade
        de conhecimento.
        """

        self.history.append(
            {
                "timestamp": datetime.now(
                    timezone.utc
                ),
                "event": event,
                "data": data
            }
        )


    def _touch(self):
        """
        Atualiza o timestamp da última modificação.
        """

        self.updated_at = datetime.now(
            timezone.utc
        )


    # ==========================================
    # CONSULTA DE ESTADO
    # ==========================================

    def get_state(self) -> Dict[str, Any]:
        """
        Retorna um resumo do estado atual do IEC.

        Utilizado por:

        - KnowledgeGraph
        - Repository
        - Services
        - APIs
        - Dashboards
        """

        return {

            "id": self.id,

            "content": self.content,

            "statement": self.statement,

            "domain": self.domain,

            "confidence": self.confidence,

            "status": self.status,

            "version": self.version,

            "sources_count": len(self.sources),

            "evidence_count": len(
                self.evidence_ids
            ),

            "relations_count": len(
                self.related_iec_ids
            ),

            "created_at": self.created_at,

            "updated_at": self.updated_at,

            "metadata": self.metadata

        }
    # ==========================================
    # CONVERSÃO PARA CONTRATO
    # ==========================================

    def to_contract(self) -> IECContract:
        """
        Converte o IEC para seu contrato estrutural.

        O contrato representa uma visão padronizada
        da unidade epistemológica para utilização
        entre módulos do KALATRACE.

        Correção (roadmap de estabilização, ENGINE-006, sessão de
        07/08/2026): este método nunca tinha sido exercitado por
        nenhum consumidor de produção antes desta sessão -- ao
        ligar o Knowledge Evolution Engine ao ciclo real (run.py),
        ele quebrou imediatamente com TypeError, porque passava
        `id`, `domain` e `version` para IECContract, que não tem
        esses parâmetros (tem `iec_id` e `knowledge_type`; não tem
        `version` nem `related_iec_ids`). Corrigido para os nomes
        reais do contrato; `version` e `related_iec_ids`, que não
        têm campo correspondente em IECContract, são preservados
        dentro de `metadata` em vez de descartados silenciosamente.
        """

        contract = IECContract(

            iec_id=self.id,

            title=self.metadata.get(
                "title",
                self.id
            ),

            statement=self.statement,

            knowledge_type=self.domain,

            evidence_ids=list(
                self.evidence_ids
            ),

            confidence=self.confidence,

            status=self.status,

            metadata={
                **self.metadata,
                "version": self.version,
                "related_iec_ids": list(self.related_iec_ids),
            }
        )

        contract.validate()

        return contract


    @classmethod
    def from_contract(cls, contract: IECContract) -> "IEC":
        """
        Reconstrói um IEC de domínio a partir do contrato canônico.

        O contrato é uma representação de fronteira; esta operação
        reconstitui novamente a entidade rica do domínio sem executar
        qualquer lógica de validação, inferência ou evolução.
        """
        if not isinstance(contract, IECContract):
            raise TypeError("contract deve ser uma instância de IECContract")

        metadata = dict(contract.metadata or {})
        metadata.setdefault("title", contract.title)
        version = int(metadata.pop("version", 1))
        related_iec_ids = list(metadata.pop("related_iec_ids", []) or [])

        iec = cls(
            id=contract.iec_id,
            content=contract.statement,
            domain=contract.knowledge_type,
            metadata=metadata,
            statement=contract.statement,
        )
        iec.evidence_ids = list(contract.evidence_ids or [])
        iec.confidence = float(contract.confidence)
        iec.status = contract.status
        iec.version = version
        iec.related_iec_ids = related_iec_ids

        if contract.created_at:
            iec.created_at = datetime.fromisoformat(
                contract.created_at.replace("Z", "+00:00")
            )
        if contract.updated_at:
            iec.updated_at = datetime.fromisoformat(
                contract.updated_at.replace("Z", "+00:00")
            )

        return iec

    # ==========================================
    # REPRESENTAÇÃO
    # ==========================================

    def __repr__(self):
        return (

            "IEC("

            f"id='{self.id}', "

            f"status='{self.status}', "

            f"confidence={self.confidence:.2f}, "

            f"version={self.version}, "

            f"domain='{self.domain}'"

            ")"

        )
    # ==========================================
    # SERIALIZAÇÃO
    # ==========================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o IEC para um dicionário.

        Utilizado por:
        - Repository
        - APIs
        - Persistência
        - Snapshots
        """

        return {

            "id": self.id,

            "content": self.content,

            "statement": self.statement,

            "domain": self.domain,

            "metadata": dict(
                self.metadata
            ),

            "sources": list(
                self.sources
            ),

            "evidence_ids": list(
                self.evidence_ids
            ),

            "related_iec_ids": list(
                self.related_iec_ids
            ),

            "confidence": self.confidence,

            "status": self.status,

            "version": self.version,

            "history": list(
                self.history
            ),

            "created_at": self.created_at,

            "updated_at": self.updated_at

        }


    # ==========================================
    # RESTAURAÇÃO DE ESTADO
    # ==========================================

    def load_state(
        self,
        state: Dict[str, Any]
    ):
        """
        Restaura o estado de um IEC previamente
        persistido.

        Este método não cria um novo IEC.
        Apenas atualiza a instância atual.
        """

        self.content = state.get(
            "content",
            self.content
        )

        self.statement = state.get(
            "statement",
            self.statement
        )

        self.domain = state.get(
            "domain",
            self.domain
        )

        self.metadata = dict(
            state.get(
                "metadata",
                self.metadata
            )
        )

        self.sources = list(
            state.get(
                "sources",
                self.sources
            )
        )

        self.evidence_ids = list(
            state.get(
                "evidence_ids",
                self.evidence_ids
            )
        )

        self.related_iec_ids = list(
            state.get(
                "related_iec_ids",
                self.related_iec_ids
            )
        )

        self.confidence = float(
            state.get(
                "confidence",
                self.confidence
            )
        )

        self.status = state.get(
            "status",
            self.status
        )

        self.version = int(
            state.get(
                "version",
                self.version
            )
        )

        self.history = list(
            state.get(
                "history",
                self.history
            )
        )

        self.created_at = state.get(
            "created_at",
            self.created_at
        )

        self.updated_at = state.get(
            "updated_at",
            datetime.now(timezone.utc)
        )

        return self
    # ==========================================
    # COMPARAÇÃO E IDENTIDADE
    # ==========================================

    def __eq__(self, other):
        """
        Dois IECs são considerados iguais quando
        possuem o mesmo identificador.
        """

        if not isinstance(other, IEC):
            return False

        return self.id == other.id


    def __hash__(self):
        """
        Permite utilizar IECs em estruturas
        como set e dict.
        """

        return hash(self.id)