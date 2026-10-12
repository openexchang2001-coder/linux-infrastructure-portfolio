# Minecraft Monitoring — Alert Validation Report

**Date:** 2026-10-12  
**Environment:** Windows 11 / Ubuntu WSL2 / Docker Compose  
**Monitoring:** Prometheus, Grafana, mc-monitor, Docker Exporter

## 1. Objective

Verify that the monitoring system detects Minecraft server failures, monitoring service failures, and missing metrics.

## 2. Test Results

| Test | Result |
|---|---|
| Minecraft server shutdown detection | PASS |
| MinecraftServerDown alert firing | PASS |
| Minecraft server recovery | PASS |
| mc-monitor shutdown detection | PASS |
| MinecraftMonitoringUnavailable alert firing | PASS |
| MinecraftMetricsMissing alert firing | PASS |
| Monitoring service recovery | PASS |
| All alerts returned to Inactive | PASS |

## 3. Failure Detection

**Test A — Minecraft server shutdown**

- Intentionally stopped the Minecraft server.
- Confirmed MinecraftServerDown entered Firing state.
- Restarted the Minecraft server.
- Verified that minecraft_status_healthy returned to 1.
- Confirmed the alert returned to Inactive.

**Test B — Monitoring exporter shutdown**

- Intentionally stopped mc-monitor.
- Confirmed MinecraftMonitoringUnavailable entered Firing state.
- Confirmed MinecraftMetricsMissing entered Firing state.
- Confirmed MinecraftServerDown remained Inactive.
- Restarted mc-monitor.
- Confirmed all three alerts returned to Inactive.

## 4. Lessons Learned

- Prometheus detects service failures using alert rules.
- Missing metrics and unhealthy services require separate detection rules.
- Grafana and Prometheus support infrastructure troubleshooting.
- Docker Exporter was used to obtain container resource metrics after cAdvisor compatibility issues in WSL2.

## 5. Limitations

- Alertmanager notification delivery has not been implemented.
- Detection and recovery durations were not measured.
- Production deployment and security hardening remain future work.

## 6. Conclusion

Successfully validated failure detection and recovery of a containerized Minecraft server and its monitoring exporter using Prometheus alert rules.
