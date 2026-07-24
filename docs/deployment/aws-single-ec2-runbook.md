# AWS single-EC2 CI/CD runbook

This is the canonical deployment runbook for the project. The AWS EC2 public
address is `52.221.55.193`, with these DNS names:

- production frontend: `https://vsocintern.online`
- production API: `https://api.vsocintern.online`
- development/staging frontend: `https://dev.vsocintern.online`
- development/staging API: `https://api-dev.vsocintern.online`

This runbook operates one trusted EC2 Docker host with three Compose projects:

- `ocean-park-edge`: the only Caddy service and the only project publishing ports 80/443.
- `ocean-park-dev`: development frontend, backend, PostgreSQL, private network, and volume.
- `ocean-park-prod`: production frontend, backend, PostgreSQL, private network, and volume.

This is operational separation, not a security or availability boundary. Both environments share the kernel, Docker daemon, EBS storage, instance role, and host failure domain. Do not use this design where development deployers are untrusted or production requires host-level high availability.

## 1. Prerequisites and host baseline

Use an EC2 instance with measured capacity for both stacks. Four vCPU and 8 GiB RAM is only a planning baseline, not a sizing guarantee. Encrypt EBS, assign a stable public address, and permit inbound 80/tcp, 443/tcp, and optionally 443/udp. Application ports 3000/8000 and PostgreSQL 5432 must remain closed. Automated deployment does not require port 22.

Attach an instance profile containing `AmazonSSMManagedInstanceCore`. Install and start:

- SSM Agent
- Docker Engine and the Docker Compose plugin
- `curl`, `flock`, `awk`, and standard GNU utilities

Confirm the instance is an online Systems Manager managed node. Do not install a GitHub Actions runner on this EC2.

For private GHCR packages, authenticate once as root with a read-only package token:

```bash
printf '%s' "$GHCR_READ_TOKEN" | sudo docker login ghcr.io -u GITHUB_USER --password-stdin
unset GHCR_READ_TOKEN
```

The credential must not appear in an environment file, SSM parameter, workflow variable, or repository file.

## 2. Fixed host layout

Create the directories without checking out a mutable branch on the host:

```bash
sudo install -d -m 0755 /opt/ocean-park/shared /opt/ocean-park/edge
sudo install -d -m 0755 /opt/ocean-park/dev /opt/ocean-park/prod
sudo install -d -m 0700 /etc/ocean-park
sudo install -d -m 0700 /var/lib/ocean-park/deployments
sudo install -d -m 0700 /var/backups/ocean-park/postgres
```

From a reviewed release, install the immutable operational files:

```bash
sudo install -o root -g root -m 0644 deploy/compose/application.yml /opt/ocean-park/shared/application.yml
sudo install -o root -g root -m 0644 deploy/compose/edge.yml /opt/ocean-park/shared/edge.yml
sudo install -o root -g root -m 0644 deploy/caddy/Caddyfile.single-ec2 /opt/ocean-park/shared/Caddyfile.single-ec2
sudo install -o root -g root -m 0755 scripts/deploy/ec2_deploy.sh /usr/local/sbin/ocean-park-deploy
```

Do not let a `dev` deployment replace these root-owned files. Review and reinstall them explicitly when deployment infrastructure changes.

The final layout is:

```text
/opt/ocean-park/shared/application.yml
/opt/ocean-park/shared/edge.yml
/opt/ocean-park/shared/Caddyfile.single-ec2
/opt/ocean-park/{edge,dev,prod}/
/etc/ocean-park/{edge,dev,prod}.env
/usr/local/sbin/ocean-park-deploy
/var/lib/ocean-park/deployments/{dev,prod}.json
/var/backups/ocean-park/postgres/
```

## 3. Environment and secret files

Copy `.env.staging.example` to `/etc/ocean-park/dev.env` and `.env.production.example` to `/etc/ocean-park/prod.env`. Replace every placeholder, use different database/JWT/admin secrets, and set the exact lowercase package prefix:

Set `DATABASE_URL` from the same database values. The safest Compose-compatible choice is a long URL-unreserved password generated with `openssl rand -hex 32`; it can be used unchanged in both `POSTGRES_PASSWORD` and `DATABASE_URL`. If you deliberately use reserved characters, account for both Compose interpolation and URL percent-encoding so the two settings still represent the same password.

```text
DEPLOY_IMAGE_PREFIX=ghcr.io/owner/repository
```

For bootstrap, `BACKEND_IMAGE` and `FRONTEND_IMAGE` must be an existing, known-good pair tagged `dev-sha-<40-hex-commit-sha>` or `prod-sha-<40-hex-commit-sha>`. The wrapper refuses branch-only tags, requires new tags to match the requested full commit SHA, pulls them before mutation, resolves each to `image@sha256:<digest>`, and atomically stores those immutable digest references for deployment and rollback. Subsequent runs accept the stored digest pair as the previous release.

Set public probes independently:

```text
BACKEND_READY_URL=https://api-dev.vsocintern.online/ready
FRONTEND_URL=https://dev.vsocintern.online
```

Production uses its production domains. Lock both files:

```bash
sudo chown root:root /etc/ocean-park/dev.env /etc/ocean-park/prod.env
sudo chmod 600 /etc/ocean-park/dev.env /etc/ocean-park/prod.env
```

Create `/etc/ocean-park/edge.env`:

```text
ACME_EMAIL=security@vsocintern.online
DEV_FRONTEND_DOMAIN=dev.vsocintern.online
DEV_API_DOMAIN=api-dev.vsocintern.online
PROD_FRONTEND_DOMAIN=vsocintern.online
PROD_API_DOMAIN=api.vsocintern.online
CADDYFILE_PATH=/opt/ocean-park/shared/Caddyfile.single-ec2
```

Protect it with root ownership and mode `600`. Point all four DNS records at the EC2 public address. When using Cloudflare, use Full (strict); initially using DNS-only records makes ACME troubleshooting simpler.

## 4. Bootstrap the three projects

Create the shared edge network and start Caddy:

```bash
sudo docker network inspect ocean-park-edge >/dev/null 2>&1 || sudo docker network create ocean-park-edge
sudo docker compose --env-file /etc/ocean-park/edge.env \
  --project-name ocean-park-edge \
  --project-directory /opt/ocean-park/edge \
  --file /opt/ocean-park/shared/edge.yml config --quiet
sudo docker compose --env-file /etc/ocean-park/edge.env \
  --project-name ocean-park-edge \
  --project-directory /opt/ocean-park/edge \
  --file /opt/ocean-park/shared/edge.yml up -d
```

Before enabling CD, manually start a known-good development image pair. Exporting `APP_ENV_FILE` and `DEPLOY_ENV` supplies Compose-only routing values without copying secrets:

```bash
sudo env DEPLOY_ENV=dev APP_ENV_FILE=/etc/ocean-park/dev.env \
  docker compose --env-file /etc/ocean-park/dev.env \
  --project-name ocean-park-dev --project-directory /opt/ocean-park/dev \
  --file /opt/ocean-park/shared/application.yml up -d
```

Bootstrap production the same way with `DEPLOY_ENV=prod`, its environment file, project name, and project directory. This manual first start is required: automated production deployment demands a running database and validates a `pg_dump` before it mutates images.

Verify all public endpoints, then run a production backup and restore rehearsal before enabling the production GitHub Environment.

## 5. AWS OIDC and CloudFormation

Create the GitHub OIDC provider once if the account does not already have it:

```text
Provider URL: https://token.actions.githubusercontent.com
Audience: sts.amazonaws.com
```

Validate and deploy `deploy/aws/single-ec2-cicd.yml` with lowercase owner/repository values, their immutable numeric GitHub IDs, and the existing provider ARN and EC2 instance ID. Obtain the IDs with `gh api users/OWNER --jq .id` and `gh api repos/OWNER/REPOSITORY --jq .id`:

```bash
aws cloudformation validate-template \
  --template-body file://deploy/aws/single-ec2-cicd.yml

aws cloudformation deploy \
  --stack-name ocean-park-single-ec2-cicd \
  --template-file deploy/aws/single-ec2-cicd.yml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    GitHubOidcProviderArn=arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com \
    GitHubOwner=owner \
    GitHubOwnerId=12345678 \
    GitHubRepository=repository \
    GitHubRepositoryId=123456789 \
    Ec2InstanceId=i-0123456789abcdef0
```

The two role trust policies accept only the matching immutable GitHub repository and Environment subject (`repo:OWNER@OWNER_ID/REPOSITORY@REPOSITORY_ID:environment:ENVIRONMENT`). Each role can invoke only its environment's custom SSM document on the specified instance. The documents accept only exact environment-qualified GHCR image patterns and call `/usr/local/sbin/ocean-park-deploy`; they do not grant arbitrary `AWS-RunShellScript` access.

## 6. GitHub configuration

Create repository variables used while building the environment-specific frontend images:

```text
DEVELOPMENT_NEXT_PUBLIC_API_URL=https://api-dev.vsocintern.online/api/v1
PRODUCTION_NEXT_PUBLIC_API_URL=https://api.vsocintern.online/api/v1
```

Create GitHub Environments named exactly `development` and `production`. Add these variables to each Environment using the matching CloudFormation outputs:

```text
AWS_REGION
AWS_ROLE_ARN
EC2_INSTANCE_ID
SSM_DOCUMENT_NAME
```

The CD workflow uses `workflow_run`, which GitHub loads from the default branch. Consequently, GitHub evaluates both jobs' Environment deployment branch policies against `main`, even though the development job separately and strictly validates `github.event.workflow_run.head_branch == 'dev'`. Allow `main` in the `development` Environment deployment branch policy, and restrict `production` to `main`. Configure required reviewers for production where the GitHub plan supports it. Protect both branches. The workflow uses OIDC temporary credentials; do not add AWS access keys or SSH keys.

`CI` records the exact backend/frontend build digests in a run-scoped deployment manifest artifact. `cd-single-ec2.yml` is triggered by that successful push run, downloads the artifact from the triggering run ID, validates its commit, environment, repository, and digests, then sends that exact pair through SSM. GitHub requires a `workflow_run` workflow to exist on the default branch, so merge the reviewed workflow to the default branch before expecting automatic `dev` deployment.

## 7. Deployment transaction and rollback

GitHub keeps only the latest pending commit for each branch-specific concurrency key, so a development run cannot evict a pending production run. The host wrapper takes the shared `/var/lock/ocean-park-deploy.lock` to serialize actual mutations across both environments. The wrapper:

1. validates the environment, full commit SHA, exact image prefix/tags, root-owned app/edge configuration, and HTTPS probes against the domains actually routed by the shared edge;
2. validates the current image pair so rollback is possible;
3. renders Compose before mutation;
4. creates and validates a custom-format production dump before production mutation;
5. pulls the requested full-commit tags, resolves and atomically writes their immutable registry digests, starts only the selected project, and waits for container and public readiness;
6. writes a non-secret success ledger containing the deployed digests;
7. restores the previous pair automatically and returns failure if deployment health fails.

Image rollback cannot undo an incompatible database migration. Use backward-compatible expand/deploy/contract migrations. To roll back a healthy but functionally bad release, invoke the matching fixed SSM document with a previously verified immutable pair and its original full commit SHA. Never edit the SSM document to accept shell commands.

Inspect state without exposing secrets:

```bash
sudo cat /var/lib/ocean-park/deployments/dev.json
sudo cat /var/lib/ocean-park/deployments/prod.json
sudo docker compose --env-file /etc/ocean-park/prod.env \
  --project-name ocean-park-prod --project-directory /opt/ocean-park/prod \
  --file /opt/ocean-park/shared/application.yml ps
```

## 8. Backup and restore

Every production deployment writes a validated dump under `/var/backups/ocean-park/postgres`. Before dumping, the wrapper requires free space greater than twice the current database size plus 1 GiB, preventing automated deployment from consuming the filesystem's final headroom. Copy backups off-host to an encrypted, versioned S3 bucket with lifecycle retention, and alert on failed transfers; a local dump does not protect against EC2/EBS loss. Use AWS Backup or coordinated application-consistent EBS snapshots as a second recovery layer. Apply a reviewed retention policy to local dumps only after off-host copy verification.

Restore only during an approved incident or rehearsal. Stop application traffic, select the correct production dump, and create another safety backup. From a reviewed repository checkout, invoke the existing guarded helper with every single-EC2 setting explicitly:

```bash
sudo env RESTORE_CONFIRM=I_UNDERSTAND \
  PROJECT_NAME=ocean-park-prod \
  COMPOSE_FILE=/opt/ocean-park/shared/application.yml \
  ENV_FILE=/etc/ocean-park/prod.env \
  DEPLOY_ENV=prod \
  APP_ENV_FILE=/etc/ocean-park/prod.env \
  bash scripts/deploy/restore_postgres.sh \
  /var/backups/ocean-park/postgres/ocean-park-prod_TIMESTAMP.dump
```

This runs `pg_restore --clean --if-exists` against the selected production project. Restart the backend and verify `/ready`, authentication, migrations, and critical user flows. Record measured RPO/RTO and test restores regularly.

## 9. Reboot recovery and monitoring

Docker services use `restart: unless-stopped`; after reboot verify:

```bash
sudo systemctl is-active docker amazon-ssm-agent
sudo docker network inspect ocean-park-edge
sudo docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
curl -fsS https://api-dev.vsocintern.online/ready
curl -fsS https://api.vsocintern.online/ready
```

Install CloudWatch Agent for host memory and disk metrics. Alert on:

- memory above 85%;
- disk above 80% and critical above 90%;
- sustained CPU above 85%;
- container restarts or unhealthy status;
- external frontend/API readiness failure;
- production backup age over 24 hours;
- SSM command failures, Caddy 5xx responses, and certificate renewal failures.

Apply S3 lifecycle rules, CloudWatch log retention, GHCR image retention, and safe Docker image cleanup while retaining all images needed for rollback.

## 10. Audit and migration gates

Run the repository verifier before installing changed operational files:

```bash
bash scripts/deploy/verify_single_ec2.sh
```

On the EC2 host confirm no Actions runner, Docker socket mount, privileged app, or public app/database port exists:

```bash
systemctl list-units --type=service | grep -i actions.runner && exit 1 || true
sudo docker ps --format '{{.Names}} {{.Ports}}'
sudo docker inspect ocean-park-dev-backend-1 ocean-park-prod-backend-1 \
  --format '{{.Name}} privileged={{.HostConfig.Privileged}} binds={{json .HostConfig.Binds}}'
```

Rehearse a deliberately unhealthy development image, production backup failure, automatic rollback, database restore, and EC2 reboot in a non-production exercise before enabling production CD.

Move to separate EC2 instances or managed services when production needs meaningful availability, development degrades production, teams require a trust boundary, recovery objectives tighten, PostgreSQL operations become burdensome, or vertical scaling is no longer economical.
