#!/usr/bin/env ruby
require 'open3'

# Execute the command and capture its exit status
command = "sudo ip link set can0 up type can bitrate 250000"
stdout, stderr, status = Open3.capture3(command)

if status.success?
  puts "CAN Interface up with 250000 baudrate"
  folder_name = "CANFUZZER"

  if Dir.exist?(folder_name)
    puts "Repo Already Cloned"
    puts "Checking the dependencies, please wait... Do not exit"
    system("pip3 install -r #{folder_name}/requirements.txt")
    puts "Done checking dependencies"
    puts "Initializing GUI"
    system("sudo ip link set can0 txqueuelen 500000")
    system("python3 #{folder_name}/canlinuxgui.py")
  else
    puts "Downloading CANFuzzer"
    system("git clone https://github.com/ankitha-2129/CANFUZZER.git")
    puts "Checking the dependencies, please wait... Do not exit"
    system("pip3 install -r #{folder_name}/requirements.txt")
    puts "Done checking dependencies"
    puts "Initializing GUI"
    system("sudo ip link set can0 txqueuelen 500000")
    system("python3 #{folder_name}/canlinuxgui.py")
  end
else
  puts "Command failed with exit status #{status.exitstatus}."
  puts "Please connect PCAN USB properly"
end
