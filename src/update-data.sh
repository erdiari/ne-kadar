#!/usr/bin/env bash

# Get the PID of the FastAPI process
PID=$(pgrep -f "python")

if [ -n "$PID" ]; then
    kill -SIGUSR1 $PID
    echo "Signal sent to process $PID"
else
    echo "FastAPI process not found"
fi
