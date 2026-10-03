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
// 6. Evidence Contract (Packet 02 Specification)
// SVI relevance is non-linear and multidimensional. Does not enforce
// an arbitrary additive formula. Final scoring model belongs to Packet 11.
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
  source_reference: z.string().optional(),
  timestamp_start_ms: z.number().int().nonnegative().optional(),
  timestamp_end_ms: z.number().int().nonnegative().optional(),
  raw_snippet: z.string(),
  confidence: z.number().min(0.0).max(1.0),
  quality_score: z.number().min(0.0).max(1.0).optional(),
  model_provider: z.string().optional(),
  model_version: z.string().optional(),
  translation_provenance: z.string().optional(),
  provenance: ProvenanceLabelSchema.default("AI_EXTRACTED"),
  uncertainty_state: UncertaintyStateSchema.default("NONE"),
  provisional_signal_weight: z.number().optional(),
  human_review_status: z
    .enum(["PENDING", "CONFIRMED", "DISMISSED", "MODIFIED"])
    .default("PENDING"),
  created_at: z.string(),
});

export type EvidenceItem = z.infer<typeof EvidenceItemSchema>;

// =============================================================================
// 7. Full SIH26093 Support Service Taxonomy & Freshness
// Explicitly covers all SIH expected outcomes and verified public pathways.
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

export const ServiceFreshnessStatusSchema = z.enum([
  "VERIFIED_CURRENT",
  "STALE",
  "UNKNOWN",
  "SANDBOX",
  "ADAPTER_READY",
  "LIVE",
]);

export type ServiceFreshnessStatus = z.infer<
  typeof ServiceFreshnessStatusSchema
>;

// =============================================================================
// 8. Referral Lifecycle & Verified Support Outcome Model
// Answering the core product USP: "Did support actually arrive?"
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

// =============================================================================
// 9. Policy-Driven Follow-Up Model
// Versioned and configurable per service type and urgency level.
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
});

export type FollowUpPolicy = z.infer<typeof FollowUpPolicySchema>;

// =============================================================================
// 10. Operator Override Model
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
