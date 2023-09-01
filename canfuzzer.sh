#!/usr/bin/env bash
sudo ip link set can0 up type can bitrate 250000
# Run your command and capture its exit status
your_command_status=$?

if [ $your_command_status -eq 0 ]; then
    echo "CAN Interface up with 250000 baudrate"
    folder_name="CANFUZZER"
    if [ -d "$folder_name" ]; then
        echo "Repo Already Cloned"
        echo "Checking the dependencies please wait......Do not exit"
        pip3 install -r CANFUZZER/requirements.txt
        echo "Done checking dependencies"
        echo "Initializing GUI"
        sudo ip link set can0 txqueuelen 500000
        python3 CANFUZZER/canlinuxgui.py  
    else
        echo "Downloading CANFuzzer"
        git clone https://github.com/ankitha-2129/CANFUZZER.git
        echo "Checking the dependencies please wait......Do not exit"
        pip3 install -r CANFUZZER/requirements.txt
        echo "Done checking dependencies"
        echo "Initializing GUI"
        sudo ip link set can0 txqueuelen 500000
        python3 CANFUZZER/canlinuxgui.py
    fi
else
    echo "Command failed with exit status $your_command_status."
    echo "Please connect PCAN USB properly"
fi
