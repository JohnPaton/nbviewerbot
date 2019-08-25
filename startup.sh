#!/bin/bash
screen -S nbviewerbot -X quit || :
screen -S nbviewerbot -dm bash -c "cd ~/nbviewerbot && source activate && while true; do nbviewerbot; done"
echo 'Started process in screen session "nbviewerbot"'
echo 'To see output, do "screen -r nbviewerbot"'

