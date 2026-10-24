# LAST 7 DAYS - Monitoring Incident Validation

Date: 2026-10-24

## Objective

Validate Prometheus alert detection and recovery
for the LAST 7 DAYS monitoring endpoint.

## Environment

- Minecraft Paper server
- Docker Compose
- mc-monitor
- Prometheus
- Alertmanager
- Grafana

## Alert

Name: Last7DaysMinecraftDown

Evaluation interval: 15 seconds

Alert threshold: 2 minutes

## Test Procedure

1. Confirmed the monitoring target was UP.
2. Stopped the LAST 7 DAYS mc-monitor container.
3. Confirmed the Prometheus alert entered FIRING.
4. Restarted the mc-monitor container.
5. Confirmed the monitoring target returned to UP.
6. Confirmed the alert returned to INACTIVE.

## Results

| Check | Result |
|---|---|
| Monitoring target restored | PASS |
| Minecraft health = 1 | PASS |
| Alert FIRING observed | PASS |
| Alert returned to INACTIVE | PASS |
| Rule evaluation health | PASS |
| Gmail notification delivery | Not yet verified |

## Scope and Limitations

This test simulated a monitoring endpoint outage,
not a Minecraft server outage.

Alert notification delivery and timing were not
fully verified in this test.

A separate server outage test is required before
production deployment.
