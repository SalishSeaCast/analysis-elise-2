#!/usr/bin/env bash
cd /ocean/eolson/MEOPAR/northernNO3PaperCalcs/notebooks
tmux new -d -s jupNN
tmux send-keys -t jupNN.0 "jupyter notebook --no-browser --port=8586" ENTER
