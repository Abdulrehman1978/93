"""Explicit Packet 04 permission and role registry.

This registry is intentionally narrower than a generic administrator concept.
It is versioned in code and role rows are seeded by migration 0007.
"""

from __future__ import annotations

PERMISSION_REGISTRY_VERSION = "packet04-v1"

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "HELPLINE_OPERATOR": frozenset(
        {
            "case.read.summary",
            "case.read.sensitive",
            "case.update",
            "contact.read",
            "transcript.read",
            "translation.read",
            "assessment.read",
            "referral.read",
            "referral.create",
            "support_outcome.read",
            "consent.read",
            "consent.record",
            "processing_authorization.read",
        }
    ),
    "SUPERVISOR": frozenset(
        {
            "case.read.summary",
            "case.read.sensitive",
            "case.update",
            "contact.read",
            "transcript.read",
            "translation.read",
            "assessment.read",
            "assessment.review",
            "referral.read",
            "referral.create",
            "referral.approve",
            "referral.transition",
            "support_outcome.read",
            "support_outcome.verify",
            "consent.read",
            "consent.record",
            "processing_authorization.read",
            "processing_authorization.manage",
            "access.break_glass",
        }
    ),
    "CASE_OFFICER": frozenset(
        {
            "case.read.summary",
            "case.read.sensitive",
            "case.update",
            "contact.read",
            "transcript.read",
            "translation.read",
            "assessment.read",
            "assessment.review",
            "referral.read",
            "referral.create",
            "referral.transition",
            "support_outcome.read",
            "consent.read",
            "processing_authorization.read",
        }
    ),
    "COUNSELLOR": frozenset(
        {"referral.read", "contact.read", "support_outcome.read", "support_outcome.verify"}
    ),
    "LEGAL_SUPPORT": frozenset(
        {"referral.read", "contact.read", "support_outcome.read", "support_outcome.verify"}
    ),
    "MEDICAL_SUPPORT": frozenset(
        {"referral.read", "contact.read", "support_outcome.read", "support_outcome.verify"}
    ),
    "DISTRICT_OFFICER": frozenset(
        {
            "case.read.summary",
            "case.read.sensitive",
            "assessment.read",
            "referral.read",
            "support_outcome.read",
            "audit.read",
            "access.break_glass",
        }
    ),
    "STATE_ADMIN": frozenset(
        {
            "case.read.summary",
            "assessment.read",
            "referral.read",
            "support_outcome.read",
            "audit.read",
        }
    ),
    "MINISTRY_ADMIN": frozenset(
        {"case.read.summary", "referral.read", "support_outcome.read", "audit.read"}
    ),
    "AUDITOR": frozenset({"audit.read", "consent.read", "processing_authorization.read"}),
    "SYSTEM_ADMIN": frozenset({"actor.manage", "role.manage", "resource.manage"}),
}

KNOWN_ACTIONS = frozenset().union(*ROLE_PERMISSIONS.values())

SENSITIVE_ACTIONS = frozenset(
    {
        "case.read.sensitive",
        "contact.read",
        "transcript.read",
        "translation.read",
        "assessment.read",
        "assessment.review",
        "consent.read",
        "consent.record",
        "processing_authorization.read",
        "processing_authorization.manage",
        "referral.read",
        "referral.create",
        "referral.approve",
        "referral.transition",
        "support_outcome.read",
        "support_outcome.verify",
    }
)

CASE_SCOPED_ACTIONS = frozenset(
    {
        "case.read.summary",
        "case.read.sensitive",
        "case.update",
        "contact.read",
        "transcript.read",
        "translation.read",
        "assessment.read",
        "assessment.review",
        "referral.read",
        "referral.create",
        "referral.approve",
        "referral.transition",
        "support_outcome.read",
        "support_outcome.verify",
        "consent.read",
        "consent.record",
        "processing_authorization.read",
        "processing_authorization.manage",
    }
)

ASSIGNMENT_REQUIRED_ROLES = frozenset({"HELPLINE_OPERATOR", "CASE_OFFICER"})
PROVIDER_ROLES = frozenset({"COUNSELLOR", "LEGAL_SUPPORT", "MEDICAL_SUPPORT"})

GLOBAL_ACTIONS = frozenset({"actor.manage", "role.manage", "resource.manage", "access.break_glass"})
CREATION_ACTIONS = frozenset(
    {"referral.create", "consent.record", "processing_authorization.manage"}
)

ACTION_RESOURCE_TYPES: dict[str, frozenset[str]] = {
    "case.read.summary": frozenset({"case"}),
    "case.read.sensitive": frozenset({"case"}),
    "case.update": frozenset({"case"}),
    "contact.read": frozenset({"contact", "referral"}),
    "transcript.read": frozenset({"transcript"}),
    "translation.read": frozenset({"translation"}),
    "assessment.read": frozenset({"assessment"}),
    "assessment.review": frozenset({"assessment"}),
    "referral.read": frozenset({"referral"}),
    "referral.create": frozenset({"case"}),
    "referral.approve": frozenset({"referral"}),
    "referral.transition": frozenset({"referral"}),
    "support_outcome.read": frozenset({"support_outcome"}),
    "support_outcome.verify": frozenset({"support_outcome"}),
    "consent.read": frozenset({"consent"}),
    "consent.record": frozenset({"case"}),
    "processing_authorization.read": frozenset({"processing_authorization"}),
    "processing_authorization.manage": frozenset({"case", "processing_authorization"}),
    "audit.read": frozenset(
        {
            "case",
            "referral",
            "assessment",
            "transcript",
            "translation",
            "contact",
            "consent",
            "processing_authorization",
            "support_outcome",
        }
    ),
}
