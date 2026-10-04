"""
KALATRACE Consensus -- testes

FASE 5 (PROPOSTA), sessao de 09/08/2026: cobertura de
ConsensusEngine/ConsensusTracker (registro de classificacao de
consenso a partir de Paranomas Cientificos da SCR, deteccao de
mudanca de classificacao, panorama agregado).

Nao pretende ser cobertura completa -- objetivo e detectar
regressao obvia se algo for quebrado ao mexer no modulo (mesmo
padrao ja usado em tests/core/).
"""

from consensus.consensus_engine import ConsensusEngine


def make_panorama(consensus_state, divergent=None, convergent=None):
    return {
        "scientific_consensus": consensus_state,
        "divergent_evidence": divergent or [],
        "convergent_evidence": convergent or [],
    }


def test_record_panorama_sem_historico_anterior_nao_gera_shift():
    engine = ConsensusEngine()
    result = engine.record_panorama("IEC-1", make_panorama("INSUFICIENCIA_DE_EVIDENCIAS"))

    assert result["recorded"]["consensus_state"] == "INSUFICIENCIA_DE_EVIDENCIAS"
    assert result["paradigm_shift"] is None


def test_record_panorama_com_mudanca_gera_shift():
    engine = ConsensusEngine()
    engine.record_panorama("IEC-1", make_panorama("INSUFICIENCIA_DE_EVIDENCIAS"))
    result = engine.record_panorama("IEC-1", make_panorama("CONTROVERSIA", divergent=["EV-1"]))

    shift = result["paradigm_shift"]
    assert shift is not None
    assert shift["from_state"] == "INSUFICIENCIA_DE_EVIDENCIAS"
    assert shift["to_state"] == "CONTROVERSIA"


def test_record_panorama_sem_mudanca_nao_gera_shift():
    engine = ConsensusEngine()
    engine.record_panorama("IEC-1", make_panorama("APARENTA_CONSENSO"))
    result = engine.record_panorama("IEC-1", make_panorama("APARENTA_CONSENSO"))

    assert result["paradigm_shift"] is None


def test_assess_stability_sem_historico():
    engine = ConsensusEngine()
    stability = engine.assess_stability("IEC-INEXISTENTE")

    assert stability["status"] == "SEM_HISTORICO"


def test_assess_stability_em_mudanca():
    engine = ConsensusEngine()
    engine.record_panorama("IEC-1", make_panorama("INSUFICIENCIA_DE_EVIDENCIAS"))
    engine.record_panorama("IEC-1", make_panorama("CONTROVERSIA", divergent=["EV-1"]))

    stability = engine.assess_stability("IEC-1")
    assert stability["status"] == "EM_MUDANCA"
    assert stability["reconstructions"] == 2


def test_controversial_iecs_lista_apenas_classificacao_mais_recente():
    engine = ConsensusEngine()
    engine.record_panorama("IEC-1", make_panorama("CONTROVERSIA", divergent=["EV-1"]))
    engine.record_panorama("IEC-2", make_panorama("APARENTA_CONSENSO"))
    # IEC-1 deixa de ser controversa na reconstrucao seguinte
    engine.record_panorama("IEC-1", make_panorama("APARENTA_CONSENSO"))

    assert engine.controversial_iecs() == []


def test_consensus_landscape_agrega_distribuicao():
    engine = ConsensusEngine()
    engine.record_panorama("IEC-1", make_panorama("CONTROVERSIA", divergent=["EV-1"]))
    engine.record_panorama("IEC-2", make_panorama("APARENTA_CONSENSO"))
    engine.record_panorama("IEC-3", make_panorama("APARENTA_CONSENSO"))

    landscape = engine.consensus_landscape()
    assert landscape["tracked_iecs"] == 3
    assert landscape["distribution"] == {"CONTROVERSIA": 1, "APARENTA_CONSENSO": 2}
    assert landscape["controversial_count"] == 1


def test_not_determinable_sempre_presente():
    engine = ConsensusEngine()
    result = engine.record_panorama("IEC-1", make_panorama("APARENTA_CONSENSO"))

    assert "divergencia_entre_pesquisadores" in result["not_determinable"]
    assert "consenso_de_comite_cientifico" in result["not_determinable"]
