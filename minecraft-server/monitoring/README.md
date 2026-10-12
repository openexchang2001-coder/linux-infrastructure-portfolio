# Minecraft Monitoring (WSL2 / Docker Compose)

## Purpose

Adds observability to the existing Minecraft Paper server **without modifying its existing Compose file**:

- `mc-monitor` exports Minecraft reachability, player count, and response time.
- `cAdvisor` exports Docker container CPU, memory, and network metrics.
- `Prometheus` scrapes these endpoints and evaluates two example alert rules.
- `Grafana` provisions a local dashboard and a Prometheus data source automatically.

## First-time setup

From `~/linux-infrastructure-portfolio/minecraft-server`:

```bash
mkdir -p secrets
openssl rand -hex 24 > secrets/grafana_admin_password.txt
chmod 600 secrets/grafana_admin_password.txt

docker compose -f compose.yaml -f monitoring.compose.yaml config -q

docker compose -f compose.yaml -f monitoring.compose.yaml up -d --no-recreate \
  mc-monitor cadvisor prometheus grafana

docker compose -f compose.yaml -f monitoring.compose.yaml ps
```

Grafana: <http://localhost:3000> (login `admin`, password in ignored secret file).
Prometheus: <http://localhost:9090/targets> (expect jobs `prometheus`, `mc-monitor`, `cadvisor` all UP).
Grafana dashboard: **Dashboards → Minecraft → Minecraft Infrastructure Overview**.

Do not publish the admin password or screenshots containing user identifiers.

## What to verify

1. Grafana login succeeds and provisioned Prometheus source is available.
2. In Prometheus, run `minecraft_status_healthy`: expect value 1 when server is reachable.
3. Run `minecraft_status_players_online_count` while connected/disconnected.
4. Run `container_memory_working_set_bytes` to check cAdvisor metrics are present.
5. Verify the Minecraft CPU and memory dashboard panels: if empty, inspect available cAdvisor labels with Prometheus; `container_label_com_docker_compose_service` may not be populated in Docker Desktop + WSL2.
6. Stop a **test** service and observe an alert only after the specified delay; do not deliberately interrupt a production server without approval.

## Caveats

- `cAdvisor` requires host filesystem access and reveals low-level resource data. Do not expose its port publicly. Docker Desktop with WSL2 may limit cAdvisor container metrics.
- Prometheus port 9090 and Grafana port 3000 are bound to `127.0.0.1` only.
- Alert rules are evaluated within Prometheus; they do **not** send email, LINE, Slack, or other notifications until a notification delivery component is configured.
- Prometheus data is retained for 7 days. Named volumes preserve dashboard and time-series state when containers restart.
- Docker Compose will not manage a host that is asleep or turned off. A local Windows PC is not a 24/7 server.
- For reproducibility in longer-lived operations, pin all images by digest after testing.

## Shutdown just the monitoring stack

```bash
docker compose -f compose.yaml -f monitoring.compose.yaml stop mc-monitor cadvisor prometheus grafana
```

## Troubleshooting

```bash
docker compose -f compose.yaml -f monitoring.compose.yaml logs --tail 80 mc-monitor

docker compose -f compose.yaml -f monitoring.compose.yaml logs --tail 80 cadvisor

docker compose -f compose.yaml -f monitoring.compose.yaml logs --tail 80 prometheus

docker compose -f compose.yaml -f monitoring.compose.yaml logs --tail 80 grafana
```

## Portfolio evidence checklist

- [ ] Capture a Grafana dashboard screenshot after checking for private information.
- [ ] Record a Prometheus target page showing `UP` for all three jobs.
- [ ] Record the test date/time and troubleshooting performed.
- [ ] Describe a simulated outage, its detection, and recovery time if tested.
- [ ] Update main README with links to monitoring documentation.
