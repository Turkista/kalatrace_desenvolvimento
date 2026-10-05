-- Epistemic relation fields for the existing Evidence -> IEC link.
-- Keeps evidence_iec_links as the persisted source for this relationship.

ALTER TABLE public.evidence_iec_links
    ADD COLUMN IF NOT EXISTS relation text NOT NULL DEFAULT 'SUPPORTS',
    ADD COLUMN IF NOT EXISTS weight double precision NOT NULL DEFAULT 1.0,
    ADD COLUMN IF NOT EXISTS reason text NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS metadata jsonb NOT NULL DEFAULT '{}'::jsonb;

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
