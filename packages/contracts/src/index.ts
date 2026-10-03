import { z } from "zod";

// =============================================================================
// 1. Health & System Telemetry Contracts
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
// 2. RFC 7807 Problem Details Error Contract
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
// 3. Three-Dimensional Triage & Assessment Contracts
// =============================================================================

export const ImmediateSafetyStateSchema = z.enum([
  "NO_IMMEDIATE_SIGNAL",
  "REVIEW_RECOMMENDED",
  "ELEVATED",
  "CRITICAL_REVIEW",
  "INSUFFICIENT_INFORMATION",
]);

export type ImmediateSafetyState = z.infer<typeof ImmediateSafetyStateSchema>;

export const SVIBandSchema = z.enum(["LOW", "MODERATE", "HIGH", "CRITICAL"]);

export type SVIBand = z.infer<typeof SVIBandSchema>;

export const ReportedUrgencyLevelSchema = z.enum([
  "ROUTINE",
  "PRIORITY",
  "URGENT",
  "CRITICAL",
]);

export type ReportedUrgencyLevel = z.infer<typeof ReportedUrgencyLevelSchema>;

// =============================================================================
// 4. Evidence-First Domain Object
// =============================================================================

export const EvidenceItemSchema = z.object({
  evidence_id: z.string().uuid(),
  assessment_id: z.string().uuid(),
  modality: z.enum([
    "ACOUSTIC",
    "TEXT_TRANSCRIPT",
    "TYPED_INPUT",
    "SILENT_TAP",
    "CONTEXTUAL",
  ]),
  signal_type: z.string(),
  timestamp_start_ms: z.number().int().nonnegative(),
  timestamp_end_ms: z.number().int().nonnegative(),
  raw_snippet: z.string(),
  confidence: z.number().min(0.0).max(1.0),
  audio_quality_snr: z.number().optional(),
  model_version: z.string(),
  svi_point_contribution: z.number(),
  human_review_status: z
    .enum(["PENDING", "CONFIRMED", "DISMISSED", "MODIFIED"])
    .default("PENDING"),
  created_at: z.string(),
});

export type EvidenceItem = z.infer<typeof EvidenceItemSchema>;

// =============================================================================
// 5. Policy-Driven Follow-Up Model
// =============================================================================

export const FollowUpPolicySchema = z.object({
  policy_id: z.string(),
  service_type: z.enum([
    "COUNSELING",
    "LEGAL_AID",
    "POLICE_PROTECTION",
    "MEDICAL",
    "SHELTER",
  ]),
  urgency_level: ReportedUrgencyLevelSchema,
  interval_hours: z.number().positive(),
  trigger_event: z.string(),
  policy_version: z.string(),
  effective_from: z.string(),
  source: z.string(),
});

export type FollowUpPolicy = z.infer<typeof FollowUpPolicySchema>;

// =============================================================================
// 6. Closed-Loop Referral Lifecycle States
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
