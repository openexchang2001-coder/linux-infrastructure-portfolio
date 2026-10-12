# Alertmanager Gmail Notification — Validation Report

**Recorded:** 2026-10-13  
**Environment:** Windows 11 / WSL2 Ubuntu / Docker Compose  
**Components:** Minecraft Paper Server, Prometheus, Alertmanager, Grafana, mc-monitor

## 1. Objective

Implement and validate automated email notifications for Minecraft server failures and recovery events.

## 2. Architecture

```text
Minecraft Server
      |
      v
mc-monitor (Health Metrics)
      |
      v
Prometheus (Alert Evaluation)
      |
      v
Alertmanager (Notification Routing)
      |
      v
Gmail SMTP (Email Delivery)
```

## 3. Configuration

- Prometheus evaluates the `MinecraftServerDown` alert rule.
- Alertmanager receives alerts from Prometheus.
- Gmail SMTP is configured with STARTTLS on port 587.
- Gmail authentication uses a Google App Password.
- SMTP credentials are stored in a local file and excluded from Git.
- `send_resolved: true` enables recovery notifications.

## 4. Validation Results

| Test | Result |
|---|---|
| Alertmanager configuration validation | PASS |
| Alertmanager container startup | PASS |
| SMTP authentication | PASS |
| Synthetic email notification | PASS |
| Minecraft server failure detection | PASS |
| FIRING email received | PASS |
| Minecraft server recovery | PASS |
| RESOLVED email received | PASS |

### Test A — SMTP Notification

Submitted a synthetic alert through the Alertmanager HTTP API.

**Result:** Gmail notification successfully received.

### Test B — Real Server Failure

1. Intentionally stopped the Minecraft server.
2. Prometheus detected the failure.
3. Alertmanager delivered a FIRING notification to Gmail.
4. Restarted the Minecraft server.
5. Prometheus detected recovery.
6. Alertmanager delivered a RESOLVED notification to Gmail.

**Result: PASS**

## 5. Troubleshooting

### Issue: Gmail SMTP Authentication Failure

Alertmanager logs reported:

`535 5.7.8 Username and Password not accepted`

Investigation identified a Gmail authentication problem.

The Google App Password was regenerated and the locally stored credential was updated.

After restarting Alertmanager, the notification test succeeded.

### Lessons Learned

- Application startup does not guarantee successful notification delivery.
- Configuration syntax validation does not validate SMTP credentials.
- Application logs are essential for troubleshooting.
- Both failure and recovery notifications should be tested.
- Credentials must be kept outside version control.

## 6. Security

- Google App Password is used instead of the account login password.
- SMTP password is stored in a locally mounted file.
- The credential file is excluded from Git.
- Local Gmail configuration containing the account address is excluded from Git.
- Secret files are not included in the public repository.

## 7. Limitations

- The monitoring stack currently runs on a local Windows/WSL2 environment.
- Monitoring and notifications stop when the host PC is unavailable.
- Detection and delivery latency have not been measured.
- Production high availability has not been implemented.

## 8. Conclusion

Successfully implemented and tested automated failure and recovery email notifications for a containerized Minecraft server.

This project demonstrates practical experience in monitoring, alerting, incident simulation, troubleshooting, recovery validation, and secure credential handling.
