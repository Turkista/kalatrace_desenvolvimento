from datetime import datetime, timezone
from typing import Optional, Dict, Any


class Evidence:
    """
    Evidence = Unidade de sustentação epistemológica.

    Representa uma fonte ou observação
    que contribui para a avaliação de um IEC.

    Responsabilidade única:

    Registrar evidências.

    Não executa:
    - validação;
    - consenso;
    - inferência.
    """


    def __init__(
        self,
        id: str,
        source: str,
        evidence_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ):

        # =============================
        # IDENTIDADE
        # =============================

        self.id = id


        # =============================
        # ORIGEM
        # =============================

        self.source = source


        # =============================
        # CLASSIFICAÇÃO
        # =============================

        self.evidence_type = evidence_type


        # =============================
        # METADADOS
        # =============================

        self.metadata = metadata or {}


        # =============================
        # QUALIDADE E CONFIANÇA
        # =============================

        self.reliability = 0.5


        # =============================
        # CICLO DE VIDA
        # =============================

        self.created_at = datetime.now(
            timezone.utc
        )

        self.updated_at = self.created_at
    # =============================
    # CONFIABILIDADE DA EVIDÊNCIA
    # =============================

    def update_reliability(
        self,
        value: float
    ):
        """
        Atualiza a confiabilidade da evidência.

        Mantém valores entre:
        0.0 e 1.0
        """

        self.reliability = max(
            0.0,
            min(1.0, float(value))
        )

        self.updated_at = datetime.now(
            timezone.utc
        )



    def reinforce(
        self,
        delta: float = 0.1
    ):
        """
        Aumenta confiabilidade.

        Exemplo:

        - replicação confirmada;
        - estudo consistente;
        - múltiplas fontes.
        """

        self.update_reliability(
            self.reliability + delta
        )



    def weaken(
        self,
        delta: float = 0.1
    ):
        """
        Reduz confiabilidade.

        Exemplo:

        - baixa qualidade metodológica;
        - inconsistências;
        - contradições.
        """

        self.update_reliability(
            self.reliability - delta
        )


    # =============================
    # RELAÇÃO COM IEC
    # =============================

    def attach_to_iec(
        self,
        iec_id: str
    ):
        """
        Vincula esta evidência
        a uma unidade de conhecimento.

        A Evidence não altera o IEC.
        Apenas registra a relação.
        """

        self.iec_id = iec_id
    # =============================
    # HISTÓRICO
    # =============================

    def add_history(
        self,
        event: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Registra eventos relacionados à evolução
        desta evidência.
        """

        if not hasattr(self, "history"):
            self.history = []

        self.history.append({

            "timestamp": datetime.now(
                timezone.utc
            ),

            "event": event,

            "data": data or {}

        })

        self.updated_at = datetime.now(
            timezone.utc
        )


    # =============================
    # EXPORTAÇÃO
    # =============================

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a evidência para estrutura
        serializável.
        """

        return {

            "id": self.id,

            "source": self.source,

            "evidence_type": self.evidence_type,

            "metadata": self.metadata,

            "reliability": self.reliability,

            "iec_id": getattr(self, "iec_id", None),

            "history": getattr(self, "history", []),

            "created_at": self.created_at,

            "updated_at": self.updated_at

        }


    # =============================
    # REPRESENTAÇÃO
    # =============================

    def __repr__(self):

        return (

            f"Evidence("
            f"id={self.id}, "
            f"type={self.evidence_type}, "
            f"source={self.source}, "
            f"reliability={self.reliability:.2f}"
            f")"

        )


    def __eq__(self, other):

        if not isinstance(other, Evidence):
            return False

        return self.id == other.id


    def __hash__(self):

        return hash(self.id)