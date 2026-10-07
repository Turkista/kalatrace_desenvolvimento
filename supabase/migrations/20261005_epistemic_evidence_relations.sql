-- Epistemic persistence for Evidence -> IEC relationships.
-- The existing Kalatrace database had the Evidence and IEC tables but did not
-- yet have the persisted relationship table. This migration keeps the
-- relationship as the source of truth for SUPPORTS / CONTRADICTS / NEUTRAL.

CREATE TABLE IF NOT EXISTS public.evidence_iec_links (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    evidence_id uuid NOT NULL REFERENCES public.evidence(id) ON DELETE CASCADE,
    iec_id uuid NOT NULL REFERENCES public.iecs(id) ON DELETE CASCADE,
    relation text NOT NULL DEFAULT 'SUPPORTS',
    weight double precision NOT NULL DEFAULT 1.0,
    reason text NOT NULL DEFAULT '',
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    validated_at timestamptz
);

ALTER TABLE public.evidence_iec_links ENABLE ROW LEVEL SECURITY;

CREATE UNIQUE INDEX IF NOT EXISTS evidence_iec_links_evidence_iec_uidx
    ON public.evidence_iec_links(evidence_id, iec_id);

DROP POLICY IF EXISTS evidence_iec_links_all_own
    ON public.evidence_iec_links;

DROP POLICY IF EXISTS evidence_iec_links_own
    ON public.evidence_iec_links;

CREATE POLICY evidence_iec_links_all_own
    ON public.evidence_iec_links
    FOR ALL
    TO authenticated
    USING ((SELECT auth.uid()) = owner_id)
    WITH CHECK ((SELECT auth.uid()) = owner_id);

GRANT SELECT, INSERT, UPDATE, DELETE
    ON public.evidence_iec_links
    TO authenticated;

ALTER TABLE public.evidence_iec_links
    DROP CONSTRAINT IF EXISTS evidence_iec_links_relation_check;

ALTER TABLE public.evidence_iec_links
    ADD CONSTRAINT evidence_iec_links_relation_check
    CHECK (relation IN ('SUPPORTS', 'CONTRADICTS', 'NEUTRAL'));

ALTER TABLE public.evidence_iec_links
    DROP CONSTRAINT IF EXISTS evidence_iec_links_weight_check;

ALTER TABLE public.evidence_iec_links
    ADD CONSTRAINT evidence_iec_links_weight_check
    CHECK (weight >= 0.0 AND weight <= 1.0);

-- Align the persisted Evidence schema with contracts/evidence_contract.py.
ALTER TABLE public.evidence
    ADD COLUMN IF NOT EXISTS confidence double precision NOT NULL DEFAULT 0.50,
    ADD COLUMN IF NOT EXISTS quality_score double precision NOT NULL DEFAULT 0.50,
    ADD COLUMN IF NOT EXISTS evidence_level text,
    ADD COLUMN IF NOT EXISTS doi text,
    ADD COLUMN IF NOT EXISTS pmid text,
    ADD COLUMN IF NOT EXISTS url text,
    ADD COLUMN IF NOT EXISTS domain text,
    ADD COLUMN IF NOT EXISTS category text,
    ADD COLUMN IF NOT EXISTS version integer NOT NULL DEFAULT 1;

UPDATE public.evidence
SET confidence = COALESCE(confidence, reliability, 0.50);

ALTER TABLE public.evidence
    DROP CONSTRAINT IF EXISTS evidence_confidence_check;

ALTER TABLE public.evidence
    ADD CONSTRAINT evidence_confidence_check
    CHECK (confidence >= 0.0 AND confidence <= 1.0);

ALTER TABLE public.evidence
    DROP CONSTRAINT IF EXISTS evidence_quality_score_check;

ALTER TABLE public.evidence
    ADD CONSTRAINT evidence_quality_score_check
    CHECK (quality_score >= 0.0 AND quality_score <= 1.0);
