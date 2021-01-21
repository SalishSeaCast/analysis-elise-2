#!/usr/bin/env bash
cd /data/eolson/results/MEOPAR/analysis-elise-2/notebooks/
tmux new -d -s jup
tmux send-keys -t jup.0 "jupyter notebook --no-browser --port=8582" ENTER
