from typing import Dict, List, Any
from datetime import datetime, UTC

from contracts.evidence_contract import EvidenceContract


class EvidenceStore:
    """
    Armazena e gerencia evidências científicas
    do sistema KALATRACE.

    Cada evidência pode sustentar
    um ou mais IECs.

    Responsabilidades:
    - armazenar evidências;
    - conectar evidências com IECs;
    - recuperar evidências;
    - calcular força epistemológica;
    - preparar persistência futura.
    """


    def __init__(self):

        # ======================================================
        # ARMAZENAMENTO PRINCIPAL
        # evidence_id -> EvidenceContract
        # ======================================================

        self.evidences: Dict[
            str,
            EvidenceContract
        ] = {}


        # ======================================================
        # ÍNDICE REVERSO
        #
        # IEC -> conjunto de evidências
        #
        # Ex:
        #
        # IEC-001:
        #    EV-001
        #    EV-002
        #
        # ======================================================

        self.iec_index: Dict[
            str,
            set
        ] = {}


        # ======================================================
        # CONTROLE DE EVENTOS
        # ======================================================

        self.history: List[
            Dict[str, Any]
        ] = []



    # ==========================================================
    # REGISTRO INTERNO DE EVENTOS
    # ==========================================================

    def _register_event(
        self,
        event: str,
        details: Dict[str, Any]
    ):
        """
        Registra alterações importantes
        realizadas no EvidenceStore.
        """

        self.history.append(
            {
                "event": event,
                "details": details,
                "timestamp": datetime.now(UTC)
                .isoformat()
            }
        )
    # ==========================================================
    # 1. ADICIONAR EVIDÊNCIA
    # ==========================================================

    def add_evidence(
        self,
        evidence: EvidenceContract
    ):
        """
        Adiciona uma nova evidência ao sistema.

        A evidência precisa ser um
        EvidenceContract válido.
        """

        if not isinstance(
            evidence,
            EvidenceContract
        ):
            raise TypeError(
                "A evidência precisa ser um EvidenceContract"
            )


        # valida contrato antes de armazenar

        evidence.validate()


        evidence_id = evidence.evidence_id


        # evita sobrescrever silenciosamente

        if evidence_id in self.evidences:

            raise ValueError(
                f"Evidência {evidence_id} já existe"
            )


        self.evidences[
            evidence_id
        ] = evidence



        self._register_event(
            "evidence_added",
            {
                "evidence_id": evidence_id,
                "type": evidence.evidence_type,
                "confidence": evidence.confidence
            }
        )


        return evidence_id



    # ==========================================================
    # 2. CRIAR E ADICIONAR EVIDÊNCIA SIMPLIFICADA
    # ==========================================================

    def create_evidence(
        self,
        evidence_id: str,
        source: str,
        evidence_type: str,
        title: str,
        description: str,
        confidence: float = 0.0,
        metadata: Dict[str, Any] | None = None
    ):
        """
        Atalho para criação de evidência.

        Cria um EvidenceContract
        e registra no Store.
        """

        evidence = EvidenceContract(

            id=evidence_id,

            source=source,

            evidence_type=evidence_type,

            title=title,

            description=description,

            confidence=confidence,

            metadata=metadata or {}

        )


        self.add_evidence(
            evidence
        )


        return evidence



    # ==========================================================
    # 3. RECUPERAR EVIDÊNCIA POR ID
    # ==========================================================

    def get_evidence(
        self,
        evidence_id: str
    ):
        """
        Retorna uma evidência específica.
        """

        return self.evidences.get(
            evidence_id
        )
    # ==========================================================
    # 4. LIGAR EVIDÊNCIA A IEC
    # ==========================================================

    def link_to_iec(
        self,
        evidence_id: str,
        iec_id: str
    ):
        """
        Cria uma conexão entre uma evidência
        e uma IEC.

        Relação:
        
        Evidence -> IEC
        IEC -> Evidence
        """

        if evidence_id not in self.evidences:

            raise ValueError(
                f"Evidência {evidence_id} não existe"
            )


        evidence = self.evidences[
            evidence_id
        ]


        # adiciona vínculo na evidência

        if iec_id not in evidence.metadata.get(
            "linked_iec",
            []
        ):

            evidence.metadata.setdefault(
                "linked_iec",
                []
            ).append(
                iec_id
            )


        # cria índice reverso

        if iec_id not in self.iec_index:

            self.iec_index[
                iec_id
            ] = set()


        self.iec_index[
            iec_id
        ].add(
            evidence_id
        )


        self._register_event(
            "evidence_linked",
            {
                "evidence_id": evidence_id,
                "iec_id": iec_id
            }
        )



    # ==========================================================
    # 5. RECUPERAR EVIDÊNCIAS DE UMA IEC
    # ==========================================================

    def get_evidence_for_iec(
        self,
        iec_id: str
    ) -> List[EvidenceContract]:
        """
        Retorna todas as evidências
        relacionadas a uma IEC.
        """

        evidence_ids = self.iec_index.get(
            iec_id,
            set()
        )


        return [

            self.evidences[evidence_id]

            for evidence_id in evidence_ids

            if evidence_id in self.evidences

        ]



    # ==========================================================
    # 6. CALCULAR FORÇA EPISTEMOLÓGICA
    # ==========================================================

    def compute_evidence_strength(
        self,
        iec_id: str
    ) -> float:
        """
        Calcula a força média das evidências
        que sustentam uma IEC.

        Retorna valor entre 0 e 1.
        """

        evidences = self.get_evidence_for_iec(
            iec_id
        )


        if not evidences:

            return 0.0


        total = sum(
            evidence.confidence
            for evidence in evidences
        )


        return total / len(evidences)



    # ==========================================================
    # 7. ATUALIZAR CONFIANÇA DA EVIDÊNCIA
    # ==========================================================

    def update_evidence_confidence(
        self,
        evidence_id: str,
        confidence: float,
        reason: str
    ):
        """
        Atualiza a confiança epistemológica
        de uma evidência.
        """

        evidence = self.get_evidence(
            evidence_id
        )


        if evidence is None:

            raise ValueError(
                f"Evidência {evidence_id} não encontrada"
            )


        evidence.update_confidence(
            confidence,
            reason
        )


        self._register_event(
            "confidence_updated",
            {
                "evidence_id": evidence_id,
                "new_confidence": confidence,
                "reason": reason
            }
        )
    # ==========================================================
    # 8. REMOVER EVIDÊNCIA
    # ==========================================================

    def remove_evidence(
        self,
        evidence_id: str
    ):
        """
        Remove uma evidência e todos
        os seus relacionamentos.
        """

        if evidence_id not in self.evidences:

            return False


        evidence = self.evidences[
            evidence_id
        ]


        linked_iecs = evidence.metadata.get(
            "linked_iec",
            []
        )


        # remove dos índices reversos

        for iec_id in linked_iecs:

            if iec_id in self.iec_index:

                self.iec_index[
                    iec_id
                ].discard(
                    evidence_id
                )


                # remove IEC vazio

                if not self.iec_index[iec_id]:

                    del self.iec_index[iec_id]


        # remove evidência

        del self.evidences[
            evidence_id
        ]


        self._register_event(
            "evidence_removed",
            {
                "evidence_id": evidence_id
            }
        )


        return True



    # ==========================================================
    # 9. EXPORTAR ESTADO DO STORE
    # ==========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Exporta o estado atual do EvidenceStore.

        Preparado para:
        - JSON
        - banco de dados
        - persistência futura
        """

        return {

            "evidences": {

                evidence_id:
                evidence.to_dict()

                for evidence_id, evidence
                in self.evidences.items()

            },


            "iec_index": {

                iec_id:
                list(evidence_ids)

                for iec_id, evidence_ids
                in self.iec_index.items()

            },


            "history": self.history

        }



    # ==========================================================
    # 10. RESTAURAR ESTADO
    # ==========================================================

    def restore(self, state: Dict[str, Any]) -> None:
        """Reconstrói o store a partir de um snapshot persistido."""
        if not isinstance(state, dict):
            raise TypeError("O estado precisa ser um dicionário")

        self.evidences.clear()
        self.iec_index.clear()
        self.history.clear()

        for evidence_id, payload in state.get("evidences", {}).items():
            evidence = EvidenceContract.from_dict(payload)
            if evidence.evidence_id != evidence_id:
                raise ValueError(
                    f"Snapshot inconsistente para evidência {evidence_id}"
                )
            evidence.validate()
            self.evidences[evidence_id] = evidence

        for iec_id, evidence_ids in state.get("iec_index", {}).items():
            self.iec_index[iec_id] = set(evidence_ids)

        self.history.extend(state.get("history", []))

    @classmethod
    def from_dict(cls, state: Dict[str, Any]) -> "EvidenceStore":
        store = cls()
        store.restore(state)
        return store

    # ==========================================================
    # 11. EXPORTAR UMA EVIDÊNCIA
    # ==========================================================

    def export_evidence(self, evidence_id: str) -> Dict[str, Any]:
        evidence = self.get_evidence(evidence_id)
        if evidence is None:
            raise ValueError(f"Evidência {evidence_id} não encontrada")
        return evidence.to_dict()

    # ==========================================================
    # 12. ESTATÍSTICAS DO SISTEMA
    # ==========================================================

    def stats(self) -> Dict[str, Any]:
        """
        Retorna métricas básicas
        do armazenamento.
        """

        return {

            "total_evidences":
                len(self.evidences),


            "total_linked_iecs":
                len(self.iec_index),


            "events":
                len(self.history)

        }



    # ==========================================================
    # 13. LIMPAR MEMÓRIA
    # ==========================================================

    def clear(self):
        """
        Remove todos os dados armazenados.
        """

        self.evidences.clear()

        self.iec_index.clear()

        self.history.clear()



    # ==========================================================
    # 14. DEBUG
    # ==========================================================

    def __repr__(self):

        state = self.stats()

        return (

            f"EvidenceStore("
            f"evidences={state['total_evidences']}, "
            f"linked_iecs={state['total_linked_iecs']}, "
            f"events={state['events']}"
            f")"

        )