# Packet 03 Representative Query Plans

Run against the canonical PostgreSQL database with:

```text
cd backend
python scripts/explain_queries.py
```

The script covers the eight foundational queries: urgent case queue, case interaction history, assessment/evidence retrieval, pending referral queue, due follow-ups, service lookup by jurisdiction/type/freshness, available async jobs, and audit history for an entity.

The query predicates intentionally align with the foundational indexes in the model. Plan output is environment- and cardinality-dependent; this packet records query/index alignment rather than a national-scale performance claim. Any local `Seq Scan` on an empty or tiny table is expected. Synthetic load testing remains Packet 29 work.
