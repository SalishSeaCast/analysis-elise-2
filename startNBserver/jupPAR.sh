#!/usr/bin/env bash
cd /ocean/eolson/MEOPAR/TPARCalcs
tmux new -d -s jupPAR
tmux send-keys -t jupPAR.0 "jupyter lab --no-browser --port=8583" ENTER
