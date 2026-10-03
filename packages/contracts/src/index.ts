import { z } from "zod";

// =============================================================================
// 1. Health & System Telemetry Contracts (Foundation Approved)
// =============================================================================

export const HealthStatusSchema = z.object({
  status: z.enum(["ok", "degraded", "unhealthy"]),
  service: z.string(),
  version: z.string(),
  timestamp: z.string(),
  uptime_seconds: z.number().nonnegative(),
  dependencies: z.record(
    z.string(),
    z.object({
      status: z.enum(["healthy", "degraded", "unreachable"]),
      latency_ms: z.number().optional(),
      details: z.string().optional(),
    }),
  ),
});

export type HealthStatus = z.infer<typeof HealthStatusSchema>;

// =============================================================================
// 2. RFC 7807 Problem Details Error Contract (Foundation Approved)
// =============================================================================

export const ProblemDetailsSchema = z.object({
  type: z.string().url().default("about:blank"),
  title: z.string(),
  status: z.number().int().min(100).max(599),
  detail: z.string(),
  instance: z.string().optional(),
  request_id: z.string(),
  timestamp: z.string(),
  errors: z
    .array(
      z.object({
        field: z.string().optional(),
        message: z.string(),
        code: z.string().optional(),
      }),
    )
    .optional(),
});

export type ProblemDetails = z.infer<typeof ProblemDetailsSchema>;

// =============================================================================
// 3. Three-Dimensional Assessment Contracts (Packet 02 Authoritative Specification)
// =============================================================================

/**
 * Immediate Safety: Evaluates urgent safety-oriented human attention now.
 * NEVER a psychiatric or clinical diagnosis.
 */
export const ImmediateSafetyStateSchema = z.enum([
  "NO_IMMEDIATE_SIGNAL",
  "REVIEW_RECOMMENDED",
  "ELEVATED",
  "CRITICAL_REVIEW",
  "INSUFFICIENT_INFORMATION",
]);

export type ImmediateSafetyState = z.infer<typeof ImmediateSafetyStateSchema>;

/**
 * Stress Vulnerability Index (SVI): Triage prioritization band.
 * PROVISIONAL_TRIAGE_POLICY pending empirical calibration in Packet 11.
 * NEVER a clinical diagnosis or evidence of criminal conduct.
 */
export const SVIBandSchema = z.enum(["LOW", "MODERATE", "HIGH", "CRITICAL"]);

export type SVIBand = z.infer<typeof SVIBandSchema>;

/**
 * Reported Incident Urgency: Independent factual urgency of reported circumstances.
 * Evaluates timing, physical danger, proximity, and ongoing threat.
 * NEVER evaluates legal guilt, truthfulness, or legal proof of offence.
 */
export const ReportedUrgencyLevelSchema = z.enum([
  "ROUTINE",
  "PRIORITY",
  "URGENT",
  "CRITICAL",
]);

export type ReportedUrgencyLevel = z.infer<typeof ReportedUrgencyLevelSchema>;

// =============================================================================
// 4. Uncertainty Model (Packet 02 Authoritative Specification)
// Uncertainty MUST reduce automation and escalate to human review.
// =============================================================================

export const UncertaintyStateSchema = z.enum([
  "NONE",
  "INSUFFICIENT_EVIDENCE",
  "LOW_AUDIO_QUALITY",
  "TRANSCRIPT_UNCERTAIN",
  "LANGUAGE_UNCERTAIN",
  "MODEL_DISAGREEMENT",
  "OUT_OF_DISTRIBUTION",
  "HUMAN_REVIEW_REQUIRED",
]);

export type UncertaintyState = z.infer<typeof UncertaintyStateSchema>;

// =============================================================================
// 5. Provenance & Attribution Model (Packet 02 Authoritative Specification)
// No AI-derived field may silently masquerade as citizen testimony.
// =============================================================================

export const ProvenanceLabelSchema = z.enum([
  "COMPLAINANT_REPORTED",
  "SUPPORT_PERSON_REPORTED",
  "OFFICER_REPORTED",
  "AI_EXTRACTED",
  "AI_ESTIMATED",
  "HUMAN_CONFIRMED",
  "OFFICIAL_SOURCE",
  "SERVICE_PROVIDER_REPORTED",
  "SYNTHETIC_DEMO",
  "NEEDS_VERIFICATION",
]);

export type ProvenanceLabel = z.infer<typeof ProvenanceLabelSchema>;

// =============================================================================
// 6. Evidence Contract (Packet 02R Data-Minimizing Specification)
// References authoritative source testimony/transcript rather than duplicating
// raw sensitive text by default. Zero additive SVI scoring weights encoded.
// =============================================================================

export const EvidenceModalitySchema = z.enum([
  "ACOUSTIC",
  "TEXT_TRANSCRIPT",
  "TYPED_INPUT",
  "SILENT_TAP",
  "CONTEXTUAL",
  "OFFICIAL_RECORD",
]);

export type EvidenceModality = z.infer<typeof EvidenceModalitySchema>;

export const EvidenceItemSchema = z.object({
  evidence_id: z.string().uuid(),
  assessment_id: z.string().uuid(),
  modality: EvidenceModalitySchema,
  signal_type: z.string(),
  source_reference: z.string(), // Authoritative URI/offset (e.g. "transcript#L12-L14")
  source_start: z.number().int().nonnegative().optional(),
  source_end: z.number().int().nonnegative().optional(),
  display_excerpt: z.string().optional(), // Minimized excerpt strictly when needed for UI display
  confidence: z.number().min(0.0).max(1.0),
  quality_score: z.number().min(0.0).max(1.0).optional(),
  model_provider: z.string().optional(),
  model_version: z.string().optional(),
  translation_provenance: z.string().optional(),
  provenance: ProvenanceLabelSchema.default("AI_EXTRACTED"),
  uncertainty_state: UncertaintyStateSchema.default("NONE"),
  human_review_status: z
    .enum(["PENDING", "CONFIRMED", "DISMISSED", "MODIFIED"])
    .default("PENDING"),
  created_at: z.string(),
});

export type EvidenceItem = z.infer<typeof EvidenceItemSchema>;

// =============================================================================
// 7. Full SIH26093 Support Service Taxonomy & Freshness
// Explicitly covers all SIH expected outcomes and verified public pathways.
// Separates endpoint information freshness from adapter integration status.
// =============================================================================

export const SupportServiceTypeSchema = z.enum([
  "COUNSELLING",
  "MENTAL_HEALTH_SUPPORT",
  "LEGAL_AID",
  "MEDICAL_ASSISTANCE",
  "POLICE_INTERVENTION_REVIEW",
  "WITNESS_PROTECTION_REVIEW",
  "EMERGENCY_SUPPORT",
  "SHELTER",
  "REHABILITATION",
  "SOCIAL_WELFARE_SUPPORT",
  "FOLLOW_UP",
  "OTHER_VERIFIED_SUPPORT",
]);

export type SupportServiceType = z.infer<typeof SupportServiceTypeSchema>;

/** Endpoint contact information currency. */
export const ServiceFreshnessStatusSchema = z.enum([
  "VERIFIED_CURRENT",
  "STALE",
  "UNKNOWN",
]);

export type ServiceFreshnessStatus = z.infer<
  typeof ServiceFreshnessStatusSchema
>;

/** Technical integration capability of the dispatch adapter. */
export const IntegrationStatusSchema = z.enum([
  "NOT_CONFIGURED",
  "SANDBOX",
  "ADAPTER_READY",
  "LIVE",
  "DEGRADED",
  "DISABLED",
]);

export type IntegrationStatus = z.infer<typeof IntegrationStatusSchema>;

// =============================================================================
// 8. Lawful Basis & Policy Governance Model (Packet 02R Specification)
// Distinct from consent. Grounded in Indian statutory & privacy-by-design baselines.
// =============================================================================

export const LawfulBasisSchema = z.enum([
  "CONSENT",
  "VOLUNTARILY_PROVIDED_FOR_SPECIFIED_PURPOSE",
  "STATE_FUNCTION_UNDER_LAW",
  "LEGAL_OBLIGATION",
  "MEDICAL_EMERGENCY",
  "PUBLIC_ORDER_OR_DISASTER_ASSISTANCE",
  "OTHER_AUTHORIZED_LAWFUL_BASIS",
]);

export type LawfulBasis = z.infer<typeof LawfulBasisSchema>;

export const PolicySourceClassSchema = z.enum([
  "STATUTORY",
  "OFFICIAL_GOVERNMENT_POLICY",
  "OFFICIAL_SERVICE_POLICY",
  "INTERNAL_SAFETY_POLICY",
  "PILOT_CONFIGURATION",
  "DEMO_CONFIGURATION",
  "RESEARCH_ASSUMPTION",
]);

export type PolicySourceClass = z.infer<typeof PolicySourceClassSchema>;

// =============================================================================
// 9. Referral Lifecycle & Verified Support Outcome Model
// Answering the core product USP: "Did support actually arrive?"
// Separates operational referral state, outcome evidence, and administrative status.
// =============================================================================

export const ReferralStateSchema = z.enum([
  "RECOMMENDED",
  "REVIEW_REQUIRED",
  "APPROVED",
  "DECLINED",
  "REFERRED",
  "ACKNOWLEDGED",
  "CONTACT_PENDING",
  "CONTACTED",
  "APPOINTMENT_SCHEDULED",
  "SERVICE_STARTED",
  "FOLLOW_UP_DUE",
  "COMPLETED",
  "UNABLE_TO_CONTACT",
  "ESCALATED",
  "CANCELLED",
]);

export type ReferralState = z.infer<typeof ReferralStateSchema>;

/** Operational progression stages (RECOMMENDED != REFERRED != DELIVERED). */
export const VerifiedSupportOutcomeSchema = z.enum([
  "RECOMMENDED",
  "REFERRED",
  "ACKNOWLEDGED",
  "CONTACTED",
  "SERVICE_STARTED",
  "FOLLOW_UP_CONFIRMED",
  "COMPLETED",
]);

export type VerifiedSupportOutcome = z.infer<
  typeof VerifiedSupportOutcomeSchema
>;

/** Evidence provenance and confidence verifying actual support delivery. */
export const SupportOutcomeEvidenceSchema = z.enum([
  "UNVERIFIED",
  "PROVIDER_CONFIRMED",
  "CITIZEN_CONFIRMED",
  "DUAL_CONFIRMED",
  "DOCUMENT_CONFIRMED",
  "UNABLE_TO_VERIFY",
]);

export type SupportOutcomeEvidence = z.infer<
  typeof SupportOutcomeEvidenceSchema
>;

// =============================================================================
// 10. Data Retention & Deletion States (Packet 02R Ephemeral Doctrine)
// Verifiable multi-stage deletion tracking across replicas and backups.
// =============================================================================

export const DeletionStateSchema = z.enum([
  "DELETION_REQUESTED",
  "PRIMARY_OBJECT_DELETED",
  "RETENTION_HOLD",
  "BACKUP_EXPIRY_PENDING",
  "DELETION_VERIFIED",
]);

export type DeletionState = z.infer<typeof DeletionStateSchema>;

// =============================================================================
// 11. Policy-Driven Follow-Up Model
// Versioned and configurable per service type, urgency level, and source authority.
// =============================================================================

export const FollowUpPolicySchema = z.object({
  policy_id: z.string(),
  service_type: SupportServiceTypeSchema,
  urgency_level: ReportedUrgencyLevelSchema,
  interval_hours: z.number().positive(),
  trigger_event: z.string(),
  policy_version: z.string(),
  effective_from: z.string(),
  effective_to: z.string().optional(),
  source: z.string(),
  source_class: PolicySourceClassSchema.default("INTERNAL_SAFETY_POLICY"),
});

export type FollowUpPolicy = z.infer<typeof FollowUpPolicySchema>;

// =============================================================================
// 12. Operator Override Model
// Preserves original AI output, human decision, reason, timestamp, and actor.
// =============================================================================

export const OperatorOverrideActionSchema = z.enum([
  "ACCEPT",
  "MODIFY",
  "DISMISS",
  "ESCALATE",
  "REQUEST_SUPERVISOR",
  "CORRECT_TRANSCRIPT",
  "CORRECT_FACT",
  "FLAG_AI_ERROR",
]);

export type OperatorOverrideAction = z.infer<
  typeof OperatorOverrideActionSchema
>;

// =============================================================================
// 13. Packet 06 Canonical Channel Gateway & Consent Contracts
// =============================================================================

export const ChannelTypeSchema = z.enum([
  "WEB",
  "PORTAL",
  "IVR",
  "TELEPHONY",
  "CHATBOT",
  "MOBILE",
  "OPERATOR",
  "SYSTEM",
]);
export type ChannelType = z.infer<typeof ChannelTypeSchema>;

export const InteractionModeSchema = z.enum([
  "UNSELECTED",
  "VOICE",
  "TEXT",
  "SILENT",
]);
export type InteractionMode = z.infer<typeof InteractionModeSchema>;

export const ChannelCapabilityStatusSchema = z.enum([
  "LIVE_TESTED",
  "ADAPTER_READY",
  "NOT_CONFIGURED",
  "DISABLED",
]);

export const ChannelCapabilitySchema = z.object({
  channel: ChannelTypeSchema,
  status: ChannelCapabilityStatusSchema,
  supported_modes: z.array(InteractionModeSchema),
  provider_code: z.string().nullable(),
  public_entrypoint: z.boolean(),
  human_review_required: z.boolean(),
  note: z.string(),
});
export type ChannelCapability = z.infer<typeof ChannelCapabilitySchema>;

export const ChannelSessionCreateSchema = z.object({
  channel: z.literal("WEB").default("WEB"),
  interaction_mode: InteractionModeSchema.default("UNSELECTED"),
  locale: z
    .string()
    .regex(/^[A-Za-z-]+$/)
    .min(2)
    .max(20)
    .default("en"),
  client_request_id: z.string().min(1).max(255).optional(),
});
export type ChannelSessionCreate = z.infer<typeof ChannelSessionCreateSchema>;

export const ChannelSessionResponseSchema = z.object({
  session_id: z.string().uuid(),
  session_token: z.string().min(1),
  expires_at: z.string().datetime(),
  channel: z.literal("WEB"),
  interaction_mode: InteractionModeSchema,
  policy_version: z.string(),
  available_modes: z.array(InteractionModeSchema),
});
export type ChannelSessionResponse = z.infer<
  typeof ChannelSessionResponseSchema
>;

export const SessionStateResponseSchema = z.object({
  session_id: z.string().uuid(),
  channel: ChannelTypeSchema,
  interaction_mode: InteractionModeSchema,
  status: z.enum(["OPEN", "COMPLETED", "ABANDONED", "FAILED"]),
  language: z.string().nullable(),
  expires_at: z.string().datetime().nullable(),
  last_activity_at: z.string().datetime().nullable(),
  policy_version: z.string().nullable(),
});
export type SessionStateResponse = z.infer<typeof SessionStateResponseSchema>;

export const ConsentChoiceSchema = z.enum(["GRANTED", "DECLINED", "REVOKED"]);
export type ConsentChoice = z.infer<typeof ConsentChoiceSchema>;

export const ConsentModeSchema = z.enum([
  "REQUIRED",
  "OPTIONAL",
  "NOT_REQUIRED",
  "PROHIBITED_WITHOUT_HUMAN_AUTHORIZATION",
]);

export const ConsentRequirementSchema = z.object({
  purpose_code: z.string(),
  name: z.string(),
  lawful_basis: z.string(),
  consent_mode: ConsentModeSchema,
  notice_required: z.boolean(),
  notice_version: z.string(),
  can_decline: z.boolean(),
  effect_of_decline: z.string(),
  can_revoke: z.boolean(),
  human_approval_required: z.boolean(),
  why_needed: z.string(),
  data_categories: z.array(z.string()),
  recipients: z.array(z.string()),
  retention_status: z.string(),
});
export type ConsentRequirement = z.infer<typeof ConsentRequirementSchema>;

export const ConsentDecisionRequestSchema = z.object({
  purpose_code: z
    .string()
    .regex(/^[A-Z0-9-]+$/)
    .min(1)
    .max(50),
  choice: ConsentChoiceSchema,
  policy_version: z.string().min(1).max(80),
  client_action_id: z.string().min(1).max(255),
});
export type ConsentDecisionRequest = z.infer<
  typeof ConsentDecisionRequestSchema
>;

export const ConsentReceiptSchema = z.object({
  consent_event_id: z.string().uuid(),
  purpose_code: z.string(),
  choice: ConsentChoiceSchema,
  policy_version: z.string(),
  recorded_at: z.string().datetime(),
  current_processing_authorized: z.boolean(),
});
export type ConsentReceipt = z.infer<typeof ConsentReceiptSchema>;

export const SessionPolicyResponseSchema = z.object({
  policy_version: z.string(),
  requested_locale: z.string(),
  served_locale: z.string(),
  translation_status: z.enum([
    "AUTHORITATIVE",
    "HUMAN_VERIFIED",
    "MACHINE_TRANSLATED",
    "FALLBACK_LANGUAGE",
    "NOT_AVAILABLE",
  ]),
  required_notices: z.array(ConsentRequirementSchema),
  optional_consents: z.array(ConsentRequirementSchema),
  available_alternatives: z.array(z.string()),
  current_decisions: z.record(z.string(), ConsentChoiceSchema),
  capabilities: z.array(ChannelCapabilitySchema),
});
export type SessionPolicyResponse = z.infer<typeof SessionPolicyResponseSchema>;
