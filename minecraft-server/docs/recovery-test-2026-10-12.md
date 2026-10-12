# Minecraft Disaster Recovery Test

Date: 2026-10-12

## Environment
- OS: Ubuntu on WSL2
- Container: Docker
- Minecraft: 26.3
- Server: Paper 26.3 Build 175
- Backup: itzg/mc-backup

## Tests Performed
1. Created a backup using RCON.
2. Verified that server.properties and world/level.dat were included.
3. Extracted the backup into a separate directory.
4. Started an isolated recovery server on port 25566.
5. Confirmed that Paper started successfully.
6. Connected to the recovery server using Minecraft Java Edition.
7. Confirmed that the original Docker Compose services were healthy.

## Results
- Backup creation: PASS
- Archive extraction: PASS
- World file extraction: PASS
- Recovery server startup: PASS
- Client connection: PASS
- World content comparison: NOT YET VERIFIED

## Troubleshooting
An Invalid Session error occurred during the initial connection attempt. Connection succeeded after client-side troubleshooting.

## Security
- Online authentication remains enabled.
- Recovery server binds to localhost only.
- Backup data and RCON credentials are excluded from Git.
