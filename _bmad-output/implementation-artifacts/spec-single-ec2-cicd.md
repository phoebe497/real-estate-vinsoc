---
title: 'Single-EC2 CI/CD for Development and Production'
type: 'feature'
created: '2026-07-21'
status: 'done'
baseline_commit: '209eb128337d309d66d6a0cb003c078cd09c8d90'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/planning-artifacts/research/technical-single-ec2-cicd-pipeline-research-2026-07-21.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** CI publishes GHCR images, but no AWS CD exists and the current HTTPS stack embeds Caddy, preventing `dev` and production from sharing one EC2. Deployment also lacks pgvector parity, host locking, constrained AWS authorization, and automatic rollback.

**Approach:** Add one shared Caddy edge, a parameterized pgvector application stack run as isolated `ocean-park-dev`/`ocean-park-prod` projects, immutable environment-qualified images, and GitHub OIDC → fixed SSM documents → a host-owned deploy wrapper. Reuse current CI, health checks, backup, and rollback concepts.

## Boundaries & Constraints

**Always:** Separate environment files, directories, networks, volumes, aliases, tags, and ledgers; keep databases private; reserve 80/443 for Caddy; serialize host mutations; validate production backup before mutation; fail CD on SSM/health failure; retain the previous image pair; keep secrets outside workflow/SSM parameters.

**Ask First:** Any live AWS, GitHub Environment, DNS, EC2, or production-data mutation; destructive cleanup/schema reversal; replacement of legacy deployment paths before coexistence testing.

**Never:** Put the self-hosted runner on the deployment EC2; use long-lived AWS keys, SSH CD, arbitrary `AWS-RunShellScript`, mutable deploy tags, public app/database ports, privileged app containers, or Docker socket mounts; claim strong isolation from one host.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Behavior | Error Handling |
|---|---|---|---|
| Dev deploy | Successful `dev` CI; matching `dev-sha-*` pair | Update only `ocean-park-dev`; record success | Roll back images and fail SSM/CD on readiness failure |
| Prod deploy | Successful approved `main` CI; `prod-sha-*` pair | Validate backup, then update only production | Abort before mutation on backup failure; otherwise roll back images |
| Concurrent deploys | Dev and prod arrive together | GitHub concurrency plus `flock` serialize mutation | Timeout/fail clearly; never race |
| Invalid image | Wrong repo/prefix or metacharacters | Reject before Docker invocation | No files/services change |
| EC2 restart | Three healthy projects existed | Edge/dev/prod restart with separate data | Runbook identifies failures without destructive repair |

</frozen-after-approval>

## Code Map

- `.github/workflows/ci.yml`, `.github/workflows/cd-single-ec2.yml` -- environment-tagged builds and OIDC/SSM CD.
- `deploy/compose/{edge,application}.yml`, `deploy/caddy/Caddyfile.single-ec2` -- shared ingress and isolated stacks.
- `deploy/aws/single-ec2-cicd.yml` -- parameterized OIDC roles/policies and constrained SSM documents.
- `scripts/deploy/{ec2_deploy,verify_single_ec2}.sh` -- host deployment transaction and invariant checks.
- `.env.staging.example`, `.env.production.example`, `docs/deployment/aws-single-ec2-runbook.md` -- environment contract and operations.

## Tasks & Acceptance

**Execution:**
- [x] `.github/workflows/ci.yml`, `.github/workflows/cd-single-ec2.yml` -- publish `dev-sha-*`/`prod-sha-*`; deploy successful push runs through GitHub Environments, OIDC, fixed SSM documents, status polling, and one concurrency group.
- [x] `deploy/compose/{edge,application}.yml`, `deploy/caddy/Caddyfile.single-ec2` -- use pgvector, project-private data, unique edge aliases, resource/log limits, no app host ports, and sole Caddy ownership of 80/443.
- [x] `deploy/aws/single-ec2-cicd.yml` -- create environment-scoped role trust and least-privilege document invocation; validate exact repository/environment image patterns; call only `/usr/local/sbin/ocean-park-deploy`.
- [x] `scripts/deploy/ec2_deploy.sh` -- validate inputs, lock, atomically switch images, validate production dump, deploy the selected project, health-check, ledger success, and automatically restore previous images on failure.
- [x] `scripts/deploy/verify_single_ec2.sh` -- render edge/dev/prod fixtures and assert aliases, distinct resources, pgvector, private app/database ports, and edge 80/443 ownership.
- [x] Environment examples and runbook -- document `/opt`/`/etc` layout, secrets/GHCR, CloudFormation and GitHub setup, monitoring, rollback, restore, reboot, and migration triggers.

**Acceptance Criteria:**
- Given rendered configurations, when verification runs, then only edge publishes 80/443, aliases/volumes differ, pgvector is used, and databases are not edge/public reachable.
- Given successful branch CI, when CD runs, then `dev` deploys only `dev-sha-*`; `main` waits for approval and deploys only `prod-sha-*`; both use temporary OIDC credentials and fixed SSM documents.
- Given production backup/readiness failure, when deployment runs, then mutation is prevented or prior images return, SSM/CD fails, and no secret is logged.
- Given a host audit, when the checklist runs, then no Actions runner, arbitrary SSM shell, public app/database port, privileged app, or Docker socket mount exists.

## Spec Change Log

## Design Notes

CloudFormation accepts an existing GitHub OIDC provider ARN and EC2 instance ID, then outputs role ARNs/document names for GitHub Environment variables. Account identifiers are parameters, not guessed values. Legacy deployment files coexist until manual recovery testing passes.

## Verification

**Commands:**
- `bash -n scripts/deploy/ec2_deploy.sh scripts/deploy/verify_single_ec2.sh` -- scripts parse.
- `bash scripts/deploy/verify_single_ec2.sh` -- all rendered invariants pass.
- `python -m pytest tests -v --tb=short` -- backend remains green.
- `npm --prefix FE run build` -- frontend remains green.
- `git diff --check` -- no whitespace errors.

**Manual checks (if no CLI):**
- Validate CloudFormation, Environment rules, SSM node status, GHCR access, broken-image rollback, production restore, reboot recovery, and CloudWatch alarms in a non-production rehearsal before production CD.

## Suggested Review Order

**Pipeline entry and artifact identity**

- Start with the protected CD entry, digest manifest validation, OIDC, and SSM polling.
  [`cd-single-ec2.yml:30`](../../.github/workflows/cd-single-ec2.yml#L30)

- Review branch-aware queuing that preserves production while the host lock serializes mutations.
  [`cd-single-ec2.yml:14`](../../.github/workflows/cd-single-ec2.yml#L14)

- Trace tested builds into full-SHA tags and the run-scoped immutable digest manifest.
  [`ci.yml:75`](../../.github/workflows/ci.yml#L75)

- Confirm the manifest captures the exact backend and frontend build outputs.
  [`ci.yml:182`](../../.github/workflows/ci.yml#L182)

**AWS and host trust boundary**

- Inspect fixed SSM documents and their strict tag-or-digest allowlists first.
  [`single-ec2-cicd.yml:29`](../../deploy/aws/single-ec2-cicd.yml#L29)

- Verify environment-bound OIDC trust and least-privilege document invocation.
  [`single-ec2-cicd.yml:97`](../../deploy/aws/single-ec2-cicd.yml#L97)

- Follow input validation and immutable digest resolution inside the root-owned wrapper.
  [`ec2_deploy.sh:46`](../../scripts/deploy/ec2_deploy.sh#L46)

- Review backup gating, atomic mutation, readiness, ledger, and cached rollback behavior.
  [`ec2_deploy.sh:293`](../../scripts/deploy/ec2_deploy.sh#L293)

**Single-host runtime separation**

- Confirm private pgvector data, unique aliases, limits, and zero application host ports.
  [`application.yml:1`](../../deploy/compose/application.yml#L1)

- Confirm one edge project exclusively owns public HTTP and HTTPS ports.
  [`edge.yml:1`](../../deploy/compose/edge.yml#L1)

- Check four-domain routing against environment-unique service aliases.
  [`Caddyfile.single-ec2:12`](../../deploy/caddy/Caddyfile.single-ec2#L12)

**Operations and verification**

- Use the runbook for secrets, bootstrap, AWS/GitHub setup, rollback, and restore.
  [`aws-single-ec2-runbook.md:68`](../../docs/deployment/aws-single-ec2-runbook.md#L68)

- Finish with executable Compose and security invariants.
  [`verify_single_ec2.sh:130`](../../scripts/deploy/verify_single_ec2.sh#L130)
