#!/usr/bin/env sh
# --------------------------------------------------------------------------- #
# wait until the server is ready
# --------------------------------------------------------------------------- #
until curl -s -f -o /dev/null "http://server:80/ready"
do
  sleep 5
done
# --------------------------------------------------------------------------- #
mkdir -p results

robot -d results test-server.robot
