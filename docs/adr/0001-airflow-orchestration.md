# ADR 0001: Orchestrate the pipeline with self-hosted Airflow on EC2

- **Status:** Proposed
- **Date:** 2026-09-28

## Context

Today an EventBridge Scheduler rule (`deploy/scheduler.tf`) starts one ECS Fargate task every
12 hours. That task fetches the Celestrak catalog, propagates every LEO object for 7 days, and
overwrites `decays.geojson` in the public frontend bucket. This setup has several gaps:

- **No retries.** `maximum_retry_attempts = 0`, and a failure anywhere reruns the whole job.
- **No alerting.** Failures show up only in CloudWatch Logs.
- **No quality gate.** A bad or empty GeoJSON goes straight to the live site.
- **No history.** Each run overwrites the previous output, so there's nothing to backfill and
  no stored predictions to compare against actual decay dates.

Constraints: total AWS spend must stay under **$20/month** (current spend is about $0.01/day),
and prod must keep running unchanged until cutover.

## Options considered

Figures are approximate us-west-2 on-demand prices. Verify current pricing before relying on them.

### 1. Keep EventBridge Scheduler (status quo)

- **Added cost:** ~$0.
- **Pros:** Nothing new to run or patch. Already works.
- **Cons:** Retries, alerting, validation, and backfills would each need to be built separately
  (for example, EventBridge retries plus SNS on task-state-change plus a separate validation
  task). That ends up as a homemade orchestrator with no UI for rerunning failed tasks or
  running backfills over past dates.

### 2. Amazon MWAA (managed Airflow)

- **Added cost:** roughly $250–$350+/month for the smallest environment, before networking.
  MWAA also needs private subnets with outbound access, which in practice means a NAT gateway
  (~$32+/month plus data charges).
- **Pros:** Managed upgrades, scaling, and metadata database. Native AWS integration.
- **Cons:** More than 10× the entire budget. **Ruled out on cost.**

### 3. Self-hosted Airflow 3 on EC2 (chosen)

- **Added cost:** ~$18/month.

  | Item | Approx. monthly |
  |---|---|
  | EC2 t4g.small (on-demand) | $12.26 |
  | Public IPv4 address | $3.65 |
  | EBS 20 GB gp3 | $1.60 |
  | Staging bucket, CloudFront, data bucket | < $0.50 |

- **Pros:** Full Airflow feature set (per-task retries with backoff, failure callbacks,
  backfills, UI) within budget. Heavy compute stays on Fargate, so the host can stay small.
- **Cons:** We own patching, upgrades, backups of the metadata DB, and recovery. A single
  instance is a single point of failure for scheduling (but not for the site, which keeps
  serving the last good GeoJSON).

## Decision

Run **Airflow 3 on a single EC2 t4g.small** (LocalExecutor, Postgres on the same host, 2 GB swap,
systemd units). Specifically:

- **Airflow orchestrates, Fargate computes.** Propagation (6–8 min) stays on the existing ECS
  task definition, triggered by a deferrable `EcsRunTaskOperator` so it doesn't hold a worker slot.
- **No inbound network access.** The security group has no ingress rules. The UI is reached
  through SSM Session Manager port forwarding.
- **Idempotent, date-partitioned stages.** `fetch`, `propagate`, and `publish` read and write
  `dt=<logical date>/` keys in a private data bucket, which enables reruns, backfills, and
  prediction-accuracy tracking.
- **Validate before publish.** A GeoJSON schema and feature-count check gates the upload.
- **Staging first.** DAGs publish to `staging.fallingspacejunk.com` until a parallel run against
  EventBridge confirms matching output, then cut over.
- **No fan-out of propagation.** At 6–8 minutes per run, splitting it into parallel tasks isn't
  worth the extra cost and complexity.

## Consequences

- Airflow uses ~90% of the $20 budget. AWS Budgets alerts at $15 and $20 (plus a forecast alert),
  defined in `infra/budgets.tf`, are the guardrail against drift.
- Memory is tight: 2 GB RAM for the scheduler, API server, DAG processor, triggerer, and Postgres
  relies on swap and a small DAG count. If memory proves unstable, the fallback is a t4g.medium
  (~$24/month, which would require revisiting the budget) or trimming components.
- Maintenance burden: OS and Airflow upgrades, Postgres backups, and host recovery are manual.
  The host should be reproducible from Terraform plus a bootstrap script.
- Rollback: until Phase 5, EventBridge keeps running in parallel. After cutover, restoring
  `deploy/scheduler.tf` from git history brings it back.
