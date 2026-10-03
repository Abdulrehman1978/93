"""Correct scope-aware authorization uniqueness and consent provenance."""

import sqlalchemy as sa

from alembic import op

revision = "0011_packet06r2_hardening"
down_revision = "0010_packet06_consent_hardening"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text("DROP INDEX IF EXISTS uq_processing_authorizations_active_interaction_authority")
    )
    op.execute(
        sa.text(
            """
            CREATE UNIQUE INDEX uq_processing_authorizations_active_interaction_scope
            ON processing_authorizations (interaction_id, processing_purpose_id, authority_type_id)
            WHERE interaction_id IS NOT NULL AND case_id IS NULL AND status = 'ACTIVE'
            """
        )
    )
    op.execute(
        sa.text(
            """
            CREATE UNIQUE INDEX uq_processing_authorizations_active_case_scope
            ON processing_authorizations (case_id, processing_purpose_id, authority_type_id)
            WHERE case_id IS NOT NULL AND status = 'ACTIVE'
            """
        )
    )
    op.execute(
        sa.text(
            """
            CREATE OR REPLACE FUNCTION validate_processing_authorization_provenance()
            RETURNS trigger
            LANGUAGE plpgsql
            AS $$
            DECLARE v_authority_code text;
            BEGIN
                SELECT pat.authority_code INTO v_authority_code
                FROM processing_authority_types AS pat
                WHERE pat.id = NEW.authority_type_id;
                IF v_authority_code = 'CONSENT' AND NEW.consent_event_id IS NULL THEN
                    RAISE EXCEPTION 'CONSENT processing authorization requires a ConsentEvent';
                END IF;
                IF v_authority_code <> 'CONSENT' AND NEW.consent_event_id IS NOT NULL THEN
                    RAISE EXCEPTION 'Non-consent processing authorization cannot cite ConsentEvent';
                END IF;
                RETURN NEW;
            END;
            $$
            """
        )
    )
    op.execute(
        sa.text(
            """
            CREATE TRIGGER processing_authorizations_provenance
            BEFORE INSERT OR UPDATE ON processing_authorizations
            FOR EACH ROW EXECUTE FUNCTION validate_processing_authorization_provenance()
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP TRIGGER IF EXISTS processing_authorizations_provenance ON processing_authorizations"
        )
    )
    op.execute(sa.text("DROP FUNCTION IF EXISTS validate_processing_authorization_provenance()"))
    op.execute(sa.text("DROP INDEX IF EXISTS uq_processing_authorizations_active_case_scope"))
    op.execute(
        sa.text("DROP INDEX IF EXISTS uq_processing_authorizations_active_interaction_scope")
    )
    op.execute(
        sa.text(
            """
            CREATE UNIQUE INDEX uq_processing_authorizations_active_interaction_authority
            ON processing_authorizations (interaction_id, processing_purpose_id, authority_type_id)
            WHERE interaction_id IS NOT NULL AND status = 'ACTIVE'
            """
        )
    )
