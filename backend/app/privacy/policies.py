"""Versioned Packet 06 consent and lawful-basis policy catalog."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.channel.schemas import ConsentMode, ConsentRequirement
from app.db.models.governance import (
    PolicyVersion,
    ProcessingAuthorityType,
    ProcessingPurpose,
)

PACKET06_POLICY_VERSION = "packet-06-consent-v1"
_POLICY_TEXT = "SAMBAL Packet 06 lawful-basis and consent requirements; evaluated 2026-10-03."
PACKET06_POLICY_HASH = hashlib.sha256(_POLICY_TEXT.encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class PurposePolicy:
    code: str
    name: str
    lawful_basis: str
    consent_mode: ConsentMode
    notice_required: bool
    can_decline: bool
    effect_of_decline: str
    can_revoke: bool
    human_approval_required: bool
    why_needed: str
    data_categories: tuple[str, ...]
    recipients: tuple[str, ...]
    retention_status: str

    def as_requirement(self) -> ConsentRequirement:
        return ConsentRequirement(
            purpose_code=self.code,
            name=self.name,
            lawful_basis=self.lawful_basis,
            consent_mode=self.consent_mode,
            notice_required=self.notice_required,
            notice_version=PACKET06_POLICY_VERSION,
            can_decline=self.can_decline,
            effect_of_decline=self.effect_of_decline,
            can_revoke=self.can_revoke,
            human_approval_required=self.human_approval_required,
            why_needed=self.why_needed,
            data_categories=self.data_categories,
            recipients=self.recipients,
            retention_status=self.retention_status,
        )


PURPOSE_POLICIES: tuple[PurposePolicy, ...] = (
    PurposePolicy(
        "PURP-01",
        "Complaint Intake",
        "VOLUNTARILY_PROVIDED_FOR_SPECIFIED_PURPOSE",
        ConsentMode.NOT_REQUIRED,
        True,
        True,
        "A person may leave without creating a complaint; no service is forced.",
        False,
        False,
        "To receive and route information the person voluntarily submits.",
        ("user-provided complaint facts", "contact details if supplied"),
        ("authorized intake operator",),
        "Packet 07 case-intake retention policy; not configured by Packet 06.",
    ),
    PurposePolicy(
        "PURP-03",
        "Ephemeral Acoustic Processing",
        "CONSENT",
        ConsentMode.OPTIONAL,
        True,
        True,
        "Text-only interaction remains available; no audio is captured by this gateway.",
        True,
        False,
        "Future channel adapters may process live acoustic input transiently.",
        ("ephemeral acoustic signal",),
        ("approved processing boundary",),
        "Default off; Packet 10 must configure any transient handling.",
    ),
    PurposePolicy(
        "PURP-06",
        "Raw Audio Retention",
        "LEGAL_OBLIGATION",
        ConsentMode.PROHIBITED_WITHOUT_HUMAN_AUTHORIZATION,
        True,
        True,
        "No raw audio retention is available in the web gateway.",
        True,
        True,
        "Any future retention requires a documented lawful basis and human approval.",
        ("raw audio",),
        ("approved evidence store",),
        "Default off; no raw audio is accepted by Packet 06.",
    ),
    PurposePolicy(
        "PURP-08",
        "General Support Referral",
        "CONSENT",
        ConsentMode.OPTIONAL,
        True,
        True,
        "The person may continue without a referral; no contact is made from this gateway.",
        True,
        False,
        "To allow a later support workflow to use a specifically chosen referral purpose.",
        ("support need", "contact details if supplied"),
        ("authorized support workflow",),
        "Packet 14/15 referral policy; no provider dispatch in Packet 06.",
    ),
    PurposePolicy(
        "PURP-16",
        "Research and Service Improvement",
        "CONSENT",
        ConsentMode.OPTIONAL,
        True,
        True,
        "Declining has no effect on intake or support access.",
        True,
        False,
        "A separately chosen optional purpose for future de-identified research workflows.",
        ("de-identified service data",),
        ("approved research boundary",),
        "Separate optional purpose; no research export is implemented by Packet 06.",
    ),
    PurposePolicy(
        "PURP-09",
        "Emergency Handoff",
        "MEDICAL_EMERGENCY",
        ConsentMode.PROHIBITED_WITHOUT_HUMAN_AUTHORIZATION,
        True,
        True,
        "Emergency handoff cannot be initiated by an anonymous session or an automated actor.",
        False,
        True,
        "A future human supervisor may authorize a narrowly scoped emergency handoff.",
        ("minimum emergency facts", "contact details only when authorized"),
        ("authorized emergency workflow",),
        "Packet 14/19 emergency policy; no external handoff is implemented by Packet 06.",
    ),
)

PURPOSE_BY_CODE = {item.code: item for item in PURPOSE_POLICIES}


async def ensure_packet06_catalog(session: AsyncSession) -> PolicyVersion:
    """Ensure the runtime policy and the small purpose catalog exist."""
    policy = await session.scalar(
        select(PolicyVersion).where(PolicyVersion.version_code == PACKET06_POLICY_VERSION)
    )
    if policy is None:
        policy = PolicyVersion(
            policy_type="CONSENT_NOTICE",
            version_code=PACKET06_POLICY_VERSION,
            content_hash=PACKET06_POLICY_HASH,
            effective_from=datetime.now(UTC),
            is_active=True,
        )
        session.add(policy)
        await session.flush()

    authorities = {
        "CONSENT": ("Consent", "PRODUCT_POLICY", "Documented, purpose-specific consent."),
        "LEGAL_OBLIGATION": (
            "Legal obligation",
            "STATUTORY",
            "Applicable legal obligation recorded by an authorized workflow.",
        ),
        "VOLUNTARILY_PROVIDED_FOR_SPECIFIED_PURPOSE": (
            "Voluntary specified purpose",
            "PRODUCT_POLICY",
            "Information voluntarily provided for the specified service purpose.",
        ),
        "MEDICAL_EMERGENCY": (
            "Medical emergency",
            "STATUTORY",
            "Only a human supervisor may record a documented emergency authority.",
        ),
        "PUBLIC_ORDER_OR_DISASTER_ASSISTANCE": (
            "Public order or disaster assistance",
            "STATUTORY",
            "Only a human supervisor may record a documented emergency authority.",
        ),
    }
    authority_rows: dict[str, ProcessingAuthorityType] = {}
    for code, (name, source_class, reference) in authorities.items():
        row = await session.scalar(
            select(ProcessingAuthorityType).where(ProcessingAuthorityType.authority_code == code)
        )
        if row is None:
            row = ProcessingAuthorityType(
                authority_code=code,
                display_name=name,
                authority_source_class=source_class,
                legal_reference=reference,
                effective_from=datetime.now(UTC),
            )
            session.add(row)
            await session.flush()
        authority_rows[code] = row

    for item in PURPOSE_POLICIES:
        row = await session.scalar(
            select(ProcessingPurpose).where(ProcessingPurpose.purpose_code == item.code)
        )
        if row is None:
            session.add(
                ProcessingPurpose(
                    purpose_code=item.code,
                    name=item.name,
                    description=item.why_needed,
                    default_authority_code=item.lawful_basis,
                    policy_version_id=policy.id,
                    is_active=True,
                )
            )
    await session.flush()
    return policy


def resolve_purpose(code: str) -> PurposePolicy:
    try:
        return PURPOSE_BY_CODE[code]
    except KeyError as exc:
        raise KeyError(code) from exc
