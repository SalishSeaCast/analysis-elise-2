#!/usr/bin/env bash
cd /ocean/eolson/MEOPAR/TPARCalcs/notebooks
tmux new -d -s jupPAR
tmux send-keys -t jupPAR.0 "jupyter notebook --no-browser --port=8583" ENTER
