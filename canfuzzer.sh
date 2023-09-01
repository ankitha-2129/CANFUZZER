#!/usr/bin/env bash
echo "Checking the dependencies please wait......Do not exit"
pip3 install -r requirements.txt
echo "Done checking dependencies"
sudo ip link set can0 up type can bitrate 250000
echo "CAN Interface up with 250000 baudrate"
echo "Initializing GUI"
python3 /home/kali/Desktop/CANFUZZEREXE/canlinuxgui.py