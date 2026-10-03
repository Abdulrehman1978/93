"""Enforce Packet 04R human-approved break-glass semantics."""

import sqlalchemy as sa

from alembic import op

revision = "0008_auth_trust_boundary"
down_revision = "0007_authorization_privacy"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        "access_elevations_active_requires_approval",
        "access_elevations",
        "status <> 'ACTIVE' OR approved_by_actor_id IS NOT NULL",
    )
    op.execute(
        sa.text(
            """
            CREATE FUNCTION enforce_access_elevation_human_approval()
            RETURNS trigger
            LANGUAGE plpgsql
            AS $$
            DECLARE
                approver_type text;
                approver_status text;
            BEGIN
                IF NEW.status = 'ACTIVE' THEN
                    IF NEW.approved_by_actor_id IS NULL THEN
                        RAISE EXCEPTION 'active access elevation requires approval';
                    END IF;
                    IF NEW.approved_by_actor_id = NEW.actor_id THEN
                        RAISE EXCEPTION 'access elevation cannot be self-approved';
                    END IF;
                    SELECT actor_type, status
                    INTO approver_type, approver_status
                    FROM actors
                    WHERE id = NEW.approved_by_actor_id;
                    IF approver_type NOT IN ('STAFF', 'AUDITOR') OR approver_status <> 'ACTIVE' THEN
                        RAISE EXCEPTION 'access elevation requires an active human approver';
                    END IF;
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
            CREATE TRIGGER access_elevations_human_approval
            BEFORE INSERT OR UPDATE ON access_elevations
            FOR EACH ROW EXECUTE FUNCTION enforce_access_elevation_human_approval()
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("DROP TRIGGER IF EXISTS access_elevations_human_approval ON access_elevations")
    )
    op.execute(sa.text("DROP FUNCTION IF EXISTS enforce_access_elevation_human_approval()"))
    op.drop_constraint(
        op.f("ck_access_elevations_access_elevations_active_requires_approval"),
        "access_elevations",
        type_="check",
    )
