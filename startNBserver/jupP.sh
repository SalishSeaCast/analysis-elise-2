#!/usr/bin/env bash
cd /data/eolson/results/MEOPAR/analysis-elise-2/notebooks/
tmux new -d -s jupP
tmux send-keys -t jupP.0 "jupyter lab --no-browser --port=8553" ENTER
