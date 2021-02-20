#!/usr/bin/env bash
cd /ocean/eolson/MEOPAR/analysis-elise-old/notebooks
tmux new -d -s jup0
tmux send-keys -t jup0.0 "jupyter lab --no-browser --port=8580" ENTER
