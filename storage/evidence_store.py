from typing import Dict, List, Any
from datetime import datetime, UTC

from contracts.evidence_contract import EvidenceContract
from contracts.evidence_relation import EvidenceRelation, EPISTEMIC_RELATIONS


class EvidenceStore:
    """
    Armazena e gerencia evidências científicas
    do sistema KALATRACE.

    Cada evidência pode sustentar, contradizer ou contextualizar
    um ou mais IECs.

    Responsabilidades:
    - armazenar evidências;
    - conectar evidências com IECs por relações epistemológicas;
    - recuperar evidências e relações;
    - calcular síntese de suporte e contradição;
    - preparar persistência futura.
    """

    def __init__(self):
        self.evidences: Dict[str, EvidenceContract] = {}
        self.iec_index: Dict[str, set] = {}

        # Relações epistemológicas pertencem ao vínculo Evidence -> IEC,
        # e não ao contrato da evidência isoladamente.
        self.relations: Dict[str, EvidenceRelation] = {}
        self.iec_relation_index: Dict[str, set] = {}

        self.history: List[Dict[str, Any]] = []

    def _register_event(
        self,
        event: str,
        details: Dict[str, Any]
    ):
        """Registra alterações importantes realizadas no EvidenceStore."""
        self.history.append(
            {
                "event": event,
                "details": details,
                "timestamp": datetime.now(UTC).isoformat()
            }
        )

    # ==========================================================
    # 1. ADICIONAR EVIDÊNCIA
    # ==========================================================

    def add_evidence(
        self,
        evidence: EvidenceContract
    ):
        """Adiciona uma nova evidência ao sistema."""
        if not isinstance(evidence, EvidenceContract):
            raise TypeError(
                "A evidência precisa ser um EvidenceContract"
            )

        evidence.validate()
        evidence_id = evidence.evidence_id

        if evidence_id in self.evidences:
            raise ValueError(
                f"Evidência {evidence_id} já existe"
            )

        self.evidences[evidence_id] = evidence

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
        """Atalho para criação de evidência."""
        evidence = EvidenceContract(
            id=evidence_id,
            source=source,
            evidence_type=evidence_type,
            title=title,
            description=description,
            confidence=confidence,
            metadata=metadata or {}
        )

        self.add_evidence(evidence)
        return evidence

    # ==========================================================
    # 3. RECUPERAR EVIDÊNCIA POR ID
    # ==========================================================

    def get_evidence(
        self,
        evidence_id: str
    ):
        """Retorna uma evidência específica."""
        return self.evidences.get(evidence_id)

    # ==========================================================
    # 4. LIGAR EVIDÊNCIA A IEC
    # ==========================================================

    def link_to_iec(
        self,
        evidence_id: str,
        iec_id: str,
        relation: str = "SUPPORTS",
        weight: float = 1.0,
        reason: str = "",
        metadata: Dict[str, Any] | None = None
    ):
        """
        Cria ou atualiza a relação epistemológica entre uma evidência e uma IEC.

        Por compatibilidade, chamadas antigas que informam apenas
        evidence_id e iec_id continuam significando SUPPORTS com peso 1.0.
        """
        if evidence_id not in self.evidences:
            raise ValueError(
                f"Evidência {evidence_id} não existe"
            )

        if relation not in EPISTEMIC_RELATIONS:
            raise ValueError(
                f"Relação epistemológica inválida: {relation}"
            )

        if not 0.0 <= weight <= 1.0:
            raise ValueError("weight deve estar entre 0 e 1")

        evidence = self.evidences[evidence_id]

        linked_iec = evidence.metadata.setdefault(
            "linked_iec",
            []
        )
        if iec_id not in linked_iec:
            linked_iec.append(iec_id)

        self.iec_index.setdefault(iec_id, set()).add(evidence_id)

        relation_id = f"{evidence_id}:{iec_id}:epistemic"
        epistemic_relation = EvidenceRelation(
            id=relation_id,
            evidence_id=evidence_id,
            iec_id=iec_id,
            relation=relation,
            weight=weight,
            reason=reason,
            metadata=metadata or {}
        )
        epistemic_relation.validate()

        self.relations[relation_id] = epistemic_relation
        self.iec_relation_index.setdefault(iec_id, set()).add(
            relation_id
        )

        self._register_event(
            "evidence_linked",
            {
                "evidence_id": evidence_id,
                "iec_id": iec_id,
                "relation": relation,
                "weight": weight,
                "reason": reason
            }
        )

        return epistemic_relation.to_dict()

    # ==========================================================
    # 5. RECUPERAR EVIDÊNCIAS DE UMA IEC
    # ==========================================================

    def get_evidence_for_iec(
        self,
        iec_id: str
    ) -> List[EvidenceContract]:
        """Retorna todas as evidências relacionadas a uma IEC."""
        evidence_ids = self.iec_index.get(iec_id, set())

        return [
            self.evidences[evidence_id]
            for evidence_id in evidence_ids
            if evidence_id in self.evidences
        ]

    # ==========================================================
    # 6. RECUPERAR RELAÇÕES EPISTEMOLÓGICAS
    # ==========================================================

    def get_relation(
        self,
        evidence_id: str,
        iec_id: str
    ) -> EvidenceRelation | None:
        """Retorna a relação epistemológica atual Evidence -> IEC."""
        return self.relations.get(
            f"{evidence_id}:{iec_id}:epistemic"
        )

    def get_relations_for_iec(
        self,
        iec_id: str
    ) -> List[EvidenceRelation]:
        """Retorna as relações epistemológicas de uma IEC."""
        relation_ids = self.iec_relation_index.get(iec_id, set())

        return [
            self.relations[relation_id]
            for relation_id in relation_ids
            if relation_id in self.relations
        ]

    # ==========================================================
    # 7. SÍNTESE EPISTEMOLÓGICA
    # ==========================================================

    def compute_epistemic_synthesis(
        self,
        iec_id: str
    ) -> Dict[str, Any]:
        """
        Calcula suporte e contradição separadamente.

        A confiança da evidência mede a confiança na evidência.
        O peso da relação mede o quanto aquela evidência participa
        da avaliação específica da IEC.

        Uma evidência CONTRADICTS não aumenta o suporte.
        Ela compõe uma dimensão independente de contradição.
        """
        relations = self.get_relations_for_iec(iec_id)

        supporting = [
            relation
            for relation in relations
            if relation.relation == "SUPPORTS"
        ]

        contradicting = [
            relation
            for relation in relations
            if relation.relation == "CONTRADICTS"
        ]

        neutral = [
            relation
            for relation in relations
            if relation.relation == "NEUTRAL"
        ]

        def weighted_score(
            items: List[EvidenceRelation]
        ) -> float:
            if not items:
                return 0.0

            total_weight = 0.0
            total_value = 0.0

            for relation in items:
                evidence = self.evidences.get(
                    relation.evidence_id
                )

                if evidence is None:
                    continue

                total_value += (
                    evidence.confidence *
                    relation.weight
                )
                total_weight += relation.weight

            return (
                total_value / total_weight
                if total_weight
                else 0.0
            )

        return {
            "iec_id": iec_id,
            "support_score": weighted_score(supporting),
            "contradiction_score": weighted_score(contradicting),
            "evidence_count": len(relations),
            "supporting_count": len(supporting),
            "contradicting_count": len(contradicting),
            "neutral_count": len(neutral),
            "relations": [
                relation.to_dict()
                for relation in relations
            ]
        }

    # ==========================================================
    # 8. COMPATIBILIDADE: FORÇA EPISTEMOLÓGICA
    # ==========================================================

    def compute_evidence_strength(
        self,
        iec_id: str
    ) -> float:
        """
        Retorna o suporte atual de uma IEC.

        Mantém o contrato anterior do sistema, mas agora usa
        somente relações SUPPORTS. Relações CONTRADICTS deixam
        de inflar silenciosamente a força de suporte.
        """
        synthesis = self.compute_epistemic_synthesis(iec_id)
        return synthesis["support_score"]

    # ==========================================================
    # 9. ATUALIZAR CONFIANÇA DA EVIDÊNCIA
    # ==========================================================

    def update_evidence_confidence(
        self,
        evidence_id: str,
        confidence: float,
        reason: str
    ):
        """Atualiza a confiança epistemológica de uma evidência."""
        evidence = self.get_evidence(evidence_id)

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
    # 10. REMOVER EVIDÊNCIA
    # ==========================================================

    def remove_evidence(
        self,
        evidence_id: str
    ):
        """Remove uma evidência e todos os seus relacionamentos."""
        if evidence_id not in self.evidences:
            return False

        evidence = self.evidences[evidence_id]

        linked_iecs = evidence.metadata.get(
            "linked_iec",
            []
        )

        for iec_id in linked_iecs:
            if iec_id in self.iec_index:
                self.iec_index[iec_id].discard(evidence_id)

                if not self.iec_index[iec_id]:
                    del self.iec_index[iec_id]

        relation_ids = [
            relation_id
            for relation_id, relation
            in self.relations.items()
            if relation.evidence_id == evidence_id
        ]

        for relation_id in relation_ids:
            relation = self.relations.pop(relation_id)

            if relation.iec_id in self.iec_relation_index:
                self.iec_relation_index[
                    relation.iec_id
                ].discard(relation_id)

                if not self.iec_relation_index[relation.iec_id]:
                    del self.iec_relation_index[relation.iec_id]

        del self.evidences[evidence_id]

        self._register_event(
            "evidence_removed",
            {
                "evidence_id": evidence_id
            }
        )

        return True

    # ==========================================================
    # 11. EXPORTAR ESTADO DO STORE
    # ==========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Exporta o estado atual do EvidenceStore."""
        return {
            "evidences": {
                evidence_id: evidence.to_dict()
                for evidence_id, evidence
                in self.evidences.items()
            },
            "iec_index": {
                iec_id: list(evidence_ids)
                for iec_id, evidence_ids
                in self.iec_index.items()
            },
            "relations": {
                relation_id: relation.to_dict()
                for relation_id, relation
                in self.relations.items()
            },
            "iec_relation_index": {
                iec_id: list(relation_ids)
                for iec_id, relation_ids
                in self.iec_relation_index.items()
            },
            "history": self.history
        }

    # ==========================================================
    # 12. HIDRATAR A PARTIR DA PERSISTÊNCIA
    # ==========================================================

    def hydrate_from_persistence(
        self,
        evidence_rows: List[Dict[str, Any]],
        link_rows: List[Dict[str, Any]],
    ) -> Dict[str, int]:
        """Reconstrói o estado runtime a partir das linhas persistidas.

        Supabase é a fonte durável. As relações SUPPORTS / CONTRADICTS /
        NEUTRAL são restauradas exatamente como persistidas; não são
        inferidas novamente durante a hidratação.
        """
        self.evidences.clear()
        self.iec_index.clear()
        self.relations.clear()
        self.iec_relation_index.clear()
        self.history.clear()

        for row in evidence_rows or []:
            payload = dict(row)
            payload["description"] = payload.get("description") or payload.get("content") or ""
            payload["title"] = payload.get("title") or payload.get("id") or "Evidence"
            payload["evidence_type"] = payload.get("evidence_type") or "unknown"
            payload["metadata"] = dict(payload.get("metadata") or {})

            evidence = EvidenceContract.from_dict(payload)
            evidence.validate()
            self.evidences[evidence.evidence_id] = evidence

        restored_links = 0
        for row in link_rows or []:
            evidence_id = row.get("evidence_id")
            iec_id = row.get("iec_id")
            if not evidence_id or not iec_id:
                continue
            if evidence_id not in self.evidences:
                continue

            relation = str(row.get("relation") or "SUPPORTS").upper()
            weight = float(row.get("weight", 1.0))
            reason = row.get("reason") or ""
            metadata = dict(row.get("metadata") or {})

            relation_id = f"{evidence_id}:{iec_id}:epistemic"
            epistemic_relation = EvidenceRelation(
                id=relation_id,
                evidence_id=str(evidence_id),
                iec_id=str(iec_id),
                relation=relation,
                weight=weight,
                reason=reason,
                created_at=row.get("created_at") or datetime.now(UTC).isoformat(),
                validated_at=row.get("validated_at"),
                metadata=metadata,
            )
            epistemic_relation.validate()

            self.relations[relation_id] = epistemic_relation
            self.iec_relation_index.setdefault(str(iec_id), set()).add(relation_id)
            self.iec_index.setdefault(str(iec_id), set()).add(str(evidence_id))

            evidence = self.evidences[str(evidence_id)]
            linked_iec = evidence.metadata.setdefault("linked_iec", [])
            if str(iec_id) not in linked_iec:
                linked_iec.append(str(iec_id))

            restored_links += 1

        self._register_event(
            "evidence_store_hydrated",
            {
                "evidences": len(self.evidences),
                "relations": restored_links,
            },
        )

        return {
            "evidences": len(self.evidences),
            "relations": restored_links,
        }

    # ==========================================================
    # 13. RESTAURAR ESTADO
    # ==========================================================

    def restore(
        self,
        state: Dict[str, Any]
    ) -> None:
        """Reconstrói o store a partir de um snapshot persistido."""
        if not isinstance(state, dict):
            raise TypeError(
                "O estado precisa ser um dicionário"
            )

        self.evidences.clear()
        self.iec_index.clear()
        self.relations.clear()
        self.iec_relation_index.clear()
        self.history.clear()

        for evidence_id, payload in state.get(
            "evidences",
            {}
        ).items():
            evidence = EvidenceContract.from_dict(
                payload
            )

            if evidence.evidence_id != evidence_id:
                raise ValueError(
                    f"Snapshot inconsistente para evidência {evidence_id}"
                )

            evidence.validate()
            self.evidences[evidence_id] = evidence

        for iec_id, evidence_ids in state.get(
            "iec_index",
            {}
        ).items():
            self.iec_index[iec_id] = set(
                evidence_ids
            )

        # Snapshots novos restauram relações explícitas.
        for relation_id, payload in state.get(
            "relations",
            {}
        ).items():
            relation = EvidenceRelation.from_dict(
                payload
            )

            if relation.relation_id != relation_id:
                raise ValueError(
                    f"Snapshot inconsistente para relação {relation_id}"
                )

            if relation.evidence_id not in self.evidences:
                continue

            self.relations[relation_id] = relation
            self.iec_relation_index.setdefault(
                relation.iec_id,
                set()
            ).add(relation_id)

        # Compatibilidade com snapshots antigos que só possuíam
        # iec_index: cada vínculo legado é tratado como SUPPORTS.
        for iec_id, evidence_ids in self.iec_index.items():
            for evidence_id in evidence_ids:
                relation_id = (
                    f"{evidence_id}:{iec_id}:epistemic"
                )

                if relation_id in self.relations:
                    continue

                if evidence_id not in self.evidences:
                    continue

                legacy_relation = EvidenceRelation(
                    id=relation_id,
                    evidence_id=evidence_id,
                    iec_id=iec_id,
                    relation="SUPPORTS",
                    weight=1.0,
                    reason="LEGACY_LINK",
                    metadata={
                        "migrated_from": "iec_index"
                    }
                )

                legacy_relation.validate()
                self.relations[relation_id] = legacy_relation
                self.iec_relation_index.setdefault(
                    iec_id,
                    set()
                ).add(relation_id)

        self.history.extend(
            state.get("history", [])
        )

    @classmethod
    def from_dict(
        cls,
        state: Dict[str, Any]
    ) -> "EvidenceStore":
        store = cls()
        store.restore(state)
        return store

    # ==========================================================
    # 14. EXPORTAR UMA EVIDÊNCIA
    # ==========================================================

    def export_evidence(
        self,
        evidence_id: str
    ) -> Dict[str, Any]:
        evidence = self.get_evidence(
            evidence_id
        )

        if evidence is None:
            raise ValueError(
                f"Evidência {evidence_id} não encontrada"
            )

        return evidence.to_dict()

    # ==========================================================
    # 15. ESTATÍSTICAS DO SISTEMA
    # ==========================================================

    def stats(self) -> Dict[str, Any]:
        """Retorna métricas básicas do armazenamento."""
        return {
            "total_evidences": len(
                self.evidences
            ),
            "total_linked_iecs": len(
                self.iec_index
            ),
            "total_epistemic_relations": len(
                self.relations
            ),
            "events": len(
                self.history
            )
        }

    # ==========================================================
    # 16. LIMPAR MEMÓRIA
    # ==========================================================

    def clear(self):
        """Remove todos os dados armazenados."""
        self.evidences.clear()
        self.iec_index.clear()
        self.relations.clear()
        self.iec_relation_index.clear()
        self.history.clear()

    # ==========================================================
    # 17. DEBUG
    # ==========================================================

    def __repr__(self):
        state = self.stats()

        return (
            f"EvidenceStore("
            f"evidences={state['total_evidences']}, "
            f"linked_iecs={state['total_linked_iecs']}, "
            f"relations={state['total_epistemic_relations']}, "
            f"events={state['events']}"
            f")"
        )