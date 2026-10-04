"""PARSI — Pattern and Semantic Representation & Interpretation engine.

PARSI is intentionally deterministic in this first implementation. It converts
raw submissions into a structured semantic representation that downstream
modules can consume. It does not validate scientific claims, assign truth,
or mutate the Knowledge Graph.
"""

from __future__ import annotations

import re
import unicodedata
import uuid
from collections import Counter
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from parsi.models import PARSIResult, SemanticContext, SemanticEntity, SemanticRelation


class PARSIEngine:
    """First cognitive interpretation stage of KALATRACE."""

    VERSION = "1.0.0"

    _INTENT_PATTERNS = (
        ("question", re.compile(r"\?|\b(qual|quais|como|por que|porque|quando|onde|what|which|how|why|when|where)\b", re.I)),
        ("hypothesis", re.compile(r"\b(hip[oó]tese|hipoteticamente|pode|poderia|might|may|could|hypothesis|suggests?)\b", re.I)),
        ("experiment", re.compile(r"\b(experimento|ensaio|teste|protocolo|experiment|trial|assay|protocol|test)\b", re.I)),
        ("evidence", re.compile(r"\b(evid[eê]ncia|estudo|artigo|revis[aã]o|evidence|study|paper|review|dataset)\b", re.I)),
        ("definition", re.compile(r"\b(é|significa|define|defini[cç][aã]o|means|defined as|definition)\b", re.I)),
    )

    _MODALITY_PATTERNS = (
        ("uncertain", re.compile(r"\b(pode|talvez|possivelmente|provavelmente|might|may|possibly|likely|could)\b", re.I)),
        ("assertive", re.compile(r"\b(demonstra|comprova|estabelece|is|shows|demonstrates|proves|establishes)\b", re.I)),
    )

    _NEGATION_PATTERN = re.compile(r"\b(n[aã]o|sem|nunca|not|without|never)\b", re.I)
    _TEMPORAL_PATTERN = re.compile(
        r"\b(?:em|no|na|during|in|since|after|before)\s+(?:19|20)\d{2}\b|\b(?:19|20)\d{2}\b|\b(?:recentemente|recently|atualmente|currently|historicamente|historically)\b",
        re.I,
    )
    _SOURCE_PATTERN = re.compile(
        r"\b(pubmed|doi|journal|journal of|artigo|estudo|review|revis[aã]o|ensaio cl[ií]nico|clinical trial|dataset|guideline|diretriz)\b",
        re.I,
    )

    _RELATION_CUES: Sequence[tuple[str, str, re.Pattern[str]]] = (
        ("causal", "causa", re.compile(r"\b(causa|causes?|leads? to|resulta em|results? in|provoca)\b", re.I)),
        ("positive", "aumenta", re.compile(r"\b(aumenta|increase|increases|elevates?|ativa|activates?|stimula|stimulates?)\b", re.I)),
        ("negative", "reduz", re.compile(r"\b(reduz|reduces?|decreases?|diminui|inibe|inhibits?|suppresses?)\b", re.I)),
        ("association", "associado", re.compile(r"\b(associado|associada|associates?|associated with|relacionado|related to|correlates?)\b", re.I)),
        ("comparison", "comparado", re.compile(r"\b(comparado|compared|versus|vs\.)\b", re.I)),
    )

    _STOPWORDS = {
        "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da", "dos", "das",
        "e", "ou", "em", "no", "na", "nos", "nas", "por", "para", "com", "sem", "sobre", "entre",
        "que", "se", "é", "são", "ser", "foi", "tem", "têm", "como", "mais", "menos", "muito", "muita",
        "the", "a", "an", "of", "and", "or", "in", "on", "for", "with", "without", "to", "from", "that",
        "this", "these", "those", "is", "are", "be", "was", "were", "has", "have", "than", "as", "by",
    }

    def __init__(self) -> None:
        self.interpretations: Dict[str, PARSIResult] = {}

    def interpret(self, raw_input: Any, *, source: str = "unknown", metadata: Mapping[str, Any] | None = None) -> PARSIResult:
        """Interpret a raw textual submission into a structured result."""
        raw_text = self._coerce_text(raw_input)
        normalized = self.normalize(raw_text)
        if not normalized:
            raise ValueError("PARSI requires non-empty textual input.")

        sentences = self._split_sentences(normalized)
        intent = self._detect_intent(normalized)
        modality = self._detect_modality(normalized)
        polarity = "negative" if self._NEGATION_PATTERN.search(normalized) else "positive"
        language = self._detect_language(normalized)
        entities = self._extract_entities(normalized)
        relations = self._extract_relations(normalized, entities)
        context = SemanticContext(
            language=language,
            modality=modality,
            polarity=polarity,
            temporal_markers=self._unique(self._TEMPORAL_PATTERN.findall(normalized)),
            domain_hints=self._domain_hints(normalized),
            source_hints=self._unique(m.group(0) for m in self._SOURCE_PATTERN.finditer(normalized)),
        )

        confidence = self._interpretation_confidence(
            normalized=normalized,
            entities=entities,
            relations=relations,
            sentences=sentences,
            intent=intent,
        )
        warnings = self._warnings(normalized, entities, relations, context, intent)
        interpretation_id = f"PARSI-{uuid.uuid4().hex[:12].upper()}"
        result = PARSIResult(
            interpretation_id=interpretation_id,
            raw_text=raw_text,
            normalized_text=normalized,
            intent=intent,
            summary=self._build_summary(normalized, intent),
            entities=entities,
            relations=relations,
            context=context,
            interpretation_confidence=confidence,
            warnings=warnings,
            provenance={
                "module": "PARSI",
                "version": self.VERSION,
                "source": source,
                "metadata": dict(metadata or {}),
                "scientific_truth_evaluation": "not_performed",
            },
        )
        self.interpretations[interpretation_id] = result
        return result

    def normalize(self, text: str) -> str:
        """Normalize whitespace and Unicode without changing meaning."""
        text = unicodedata.normalize("NFKC", text).strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def get(self, interpretation_id: str) -> PARSIResult | None:
        return self.interpretations.get(interpretation_id)

    def stats(self) -> Dict[str, Any]:
        intents = Counter(result.intent for result in self.interpretations.values())
        return {
            "version": self.VERSION,
            "interpretations": len(self.interpretations),
            "intents": dict(intents),
        }

    @staticmethod
    def _coerce_text(raw_input: Any) -> str:
        if isinstance(raw_input, str):
            return raw_input
        if isinstance(raw_input, Mapping):
            for key in ("statement", "text", "content", "query", "description"):
                value = raw_input.get(key)
                if isinstance(value, str):
                    return value
        raise TypeError("PARSI input must be a string or mapping containing textual content.")

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        return [item.strip() for item in re.split(r"(?<=[.!?])\s+", text) if item.strip()]

    @classmethod
    def _detect_intent(cls, text: str) -> str:
        for intent, pattern in cls._INTENT_PATTERNS:
            if pattern.search(text):
                return intent
        return "observation"

    @classmethod
    def _detect_modality(cls, text: str) -> str:
        for modality, pattern in cls._MODALITY_PATTERNS:
            if pattern.search(text):
                return modality
        return "neutral"

    @staticmethod
    def _detect_language(text: str) -> str:
        pt = len(re.findall(r"\b(de|da|do|que|não|uma|um|para|com|reduz|aumenta|estimula)\b", text, re.I))
        en = len(re.findall(r"\b(the|of|that|not|a|an|for|with|reduces?|increases?|stimulates?)\b", text, re.I))
        if pt > en:
            return "pt"
        if en > pt:
            return "en"
        return "unknown"

    @classmethod
    def _extract_entities(cls, text: str) -> List[SemanticEntity]:
        candidates: List[str] = []
        candidates.extend(re.findall(r"[\"“]([^\"”]+)[\"”]", text))
        candidates.extend(re.findall(r"\b[A-ZÀ-Ý][\wÀ-ÿ-]*(?:\s+[A-ZÀ-Ý][\wÀ-ÿ-]*){0,2}\b", text))

        tokens = re.findall(r"[\wÀ-ÿ-]{4,}", text.lower())
        counts = Counter(token for token in tokens if token not in cls._STOPWORDS and not token.isdigit())
        candidates.extend(token for token, _ in counts.most_common(8))

        seen: set[str] = set()
        entities: List[SemanticEntity] = []
        for candidate in candidates:
            normalized = cls._normalize_entity(candidate)
            if not normalized or normalized in seen or normalized in cls._STOPWORDS:
                continue
            seen.add(normalized)
            score = 0.8 if len(candidate.split()) > 1 else 0.55
            entities.append(SemanticEntity(candidate.strip(), normalized, "concept", score))
            if len(entities) >= 12:
                break
        return entities

    @staticmethod
    def _normalize_entity(value: str) -> str:
        value = unicodedata.normalize("NFKD", value)
        value = "".join(ch for ch in value if not unicodedata.combining(ch))
        return re.sub(r"\s+", " ", value).strip().lower()

    @classmethod
    def _extract_relations(cls, text: str, entities: Sequence[SemanticEntity]) -> List[SemanticRelation]:
        if len(entities) < 2:
            return []
        relations: List[SemanticRelation] = []
        for relation_type, label, pattern in cls._RELATION_CUES:
            match = pattern.search(text)
            if not match:
                continue
            before = text[:match.start()]
            after = text[match.end():]
            source = cls._nearest_entity(before, entities, reverse=True)
            target = cls._nearest_entity(after, entities, reverse=False)
            if source and target and source != target:
                relations.append(SemanticRelation(source, relation_type, target, label, 0.65))
        return relations

    @staticmethod
    def _nearest_entity(fragment: str, entities: Sequence[SemanticEntity], *, reverse: bool) -> str | None:
        normalized_fragment = PARSIEngine._normalize_entity(fragment)
        ordered = reversed(entities) if reverse else entities
        for entity in ordered:
            if entity.normalized and entity.normalized in normalized_fragment:
                return entity.normalized
        return None

    @staticmethod
    def _domain_hints(text: str) -> List[str]:
        lexicon = {
            "science": ("estudo", "evidence", "scientific", "cientifico", "hipotese", "hypothesis"),
            "medicine": ("paciente", "clinical", "clinico", "tratamento", "disease", "doenca"),
            "biology": ("cell", "celula", "protein", "proteina", "gene", "fibroblasto"),
            "skin": ("pele", "skin", "colageno", "collagen", "acne", "bakuchiol", "resveratrol"),
        }
        lowered = text.lower()
        return [domain for domain, terms in lexicon.items() if any(term in lowered for term in terms)]

    @staticmethod
    def _interpretation_confidence(*, normalized: str, entities: Sequence[SemanticEntity], relations: Sequence[SemanticRelation], sentences: Sequence[str], intent: str) -> float:
        score = 0.45
        score += min(len(normalized) / 500.0, 0.15)
        score += min(len(entities) / 12.0, 0.20)
        score += min(len(relations) * 0.08, 0.12)
        if len(sentences) > 1:
            score += 0.04
        if intent != "observation":
            score += 0.04
        return round(min(score, 0.98), 3)

    @staticmethod
    def _warnings(
        text: str,
        entities: Sequence[SemanticEntity],
        relations: Sequence[SemanticRelation],
        context: SemanticContext,
        intent: str,
    ) -> List[str]:
        warnings: List[str] = []
        if intent in {"hypothesis", "evidence", "observation"} or context.modality == "assertive":
            warnings.append("PARSI interpreta a estrutura do texto; não interpreta isso como prova científica")
        if len(text.split()) < 4:
            warnings.append("input curto; interpretação semântica limitada")
        if not entities:
            warnings.append("nenhuma entidade semântica candidata identificada")
        if context.modality == "assertive":
            warnings.append("linguagem assertiva detectada; PARSI não interpreta isso como prova científica")
        if not relations:
            warnings.append("nenhuma relação explícita identificada")
        return warnings

    @staticmethod
    def _build_summary(text: str, intent: str) -> str:
        sentence = PARSIEngine._split_sentences(text)[0]
        return f"{intent}: {sentence[:240]}"

    @staticmethod
    def _unique(values: Iterable[str]) -> List[str]:
        result: List[str] = []
        seen: set[str] = set()
        for value in values:
            value = value.strip()
            if value and value.lower() not in seen:
                result.append(value)
                seen.add(value.lower())
        return result


# Alias explícito para manter o nome arquitetural curto disponível.
PARSI = PARSIEngine
