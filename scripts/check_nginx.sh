#!/bin/bash

if curl -fsS -o /dev/null http://localhost/practice.html; then
echo "OK: Web server is working"
else
echo "NG: Web server check failed"
fi
