import tkinter
import customtkinter
import os
import can
import time
import random
import threading
import re
import platform
import subprocess
#import tkinter as tk
from CTkScrollableDropdown import *
from can.interfaces.virtual import VirtualBus
from customtkinter import CTkLabel,CTkFont
from tkinter import ttk
#from CTkMessagebox import CTkMessagebox


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("200x300")

        self.label = customtkinter.CTkLabel(self, text="ERROR")
        self.label.pack(padx=200, pady=200)
      
class App(customtkinter.CTk):
    def __init__(self):
        
        super().__init__()

        customtkinter.set_appearance_mode("Dark")
        # customtkinter.set_default_color_theme("blue")
        customtkinter.set_default_color_theme("blue")
        
        # exits the program when the window is closed by the user
        self.font = customtkinter.CTkFont(family="Rockwell", size=40)

        self.title("FUZZER")
        self.geometry(f"{1280}x{720}")
        #self.attributes("-fullscreen", True)
        
        self.bind("<1>", lambda event: event.widget.focus_set())
        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.toplevel_window = None
        
        self.can_bus = None

        self.tagline_font = customtkinter.CTkFont(
            family="Rockwell", size=40, weight="bold"
        )
        
        self.display_font = customtkinter.CTkFont(
            family="Rockwell", size=20, weight="bold"
        )
        
        # create sidebar frame with widgets
        
        self.sidebar_frame = customtkinter.CTkScrollableFrame(self, width=500, corner_radius=20)
        self.sidebar_frame.grid(row=0, column=0, rowspan=3, sticky="nsew", columnspan=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        self.sidebar_frame.rowconfigure(1, weight=1)
        
        #create logo frame
        # self.logo_frame = customtkinter.CTkFrame(self, corner_radius=20)
        # self.logo_frame.grid(row=0, column=1, sticky="nsew", rowspan=1, columnspan=2)
        # self.logo_frame.grid_rowconfigure(0, weight=1)

        self.logo_label = customtkinter.CTkLabel(self, text="CAN PROTOCOL FUZZER", font=self.tagline_font, corner_radius=20, height=50, width=700, anchor="center")
        self.logo_label.grid(row=0, column=1, pady=10, sticky="nsew", columnspan=2)
        
        # create displaybox
        self.textbox_display = customtkinter.CTkTextbox(self, width=300, height=700, corner_radius=20, border_width=2, border_color="gray50", font=self.display_font)
        self.textbox_display.grid(row=1, column=1, padx=10, pady=10, sticky="nsew", rowspan=10)
        self.textbox_display.insert("0.0", "CAN FUZZER INITIATING..................")
        self.textbox_display.bind("<Key>", lambda e: "break")
        
        # Create a bold font
        bold_font = CTkFont(weight="bold",family="Helvetica", size=18)
        
        
        # create text input Frame for bitrate and can interface 
        self.bitrate_var = tkinter.StringVar()
        self.label_textbox = customtkinter.CTkLabel(master=self.sidebar_frame, text="SELECT BITRATE", font=bold_font) 
        self.label_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.combo_bitrate = customtkinter.CTkComboBox(master=self.sidebar_frame, width=200, height=40, variable=self.bitrate_var, state='readonly')
        self.combo_bitrate.grid(row=1, column=0, pady=10, padx=10, sticky="n")
        CTkScrollableDropdown(self.combo_bitrate, values=[
                                                        "1000000",
                                                        "800000",
                                                        "500000",
                                                        "250000",
                                                        "200000",
                                                        "125000",
                                                        "100000",
                                                        "95.238000",
                                                        "83.333000",
                                                        "50000",
                                                        "47.619000",
                                                        "40000",
                                                        "33.333000",
                                                        "20000",
                                                        "10000",
                                                        "5000"])
        # Increase the font size and make the text bold for the label
        #label_style = ttk.Style()
        #label_style.configure("LabelStyle.TLabel", font=("Arial", 16, "bold"))
        
        # two buttons or one button is enough i guess to start and stop can service via system commands 
        
        # combobox for can interface
        self.interface_var = customtkinter.StringVar()
        self.label_radio_group = customtkinter.CTkLabel(master=self.sidebar_frame, text="SELECT INTERFACE", font=bold_font)
        self.label_radio_group.grid(row=2, column=0, padx=10, pady=10)
        self.combobox_interface = customtkinter.CTkComboBox(master=self.sidebar_frame, width=150, height=40, variable=self.interface_var, border_width=2, state='readonly')
        self.combobox_interface.grid(row=3, column=0, pady=10, padx=10)
        
        #create buttons
        self.start_can_button = customtkinter.CTkButton(master=self.sidebar_frame, border_width=1, text="CAN UP", command=self.start_and_stop_can_ip, font=bold_font, width=200)
        self.start_can_button.grid(row=4, column=0, pady=20, padx=20)
        # self.stop_can_button = customtkinter.CTkButton(master=self.sidebar_frame, border_width=2, text="Stop Can Ip", command=self.stop_can_ip, font=bold_font, width=100)
        # self.stop_can_button.grid(row=4, column=0)
        
        # # select attack based mechanism
        self.combobox_attack_var = customtkinter.StringVar()
        self.label_radio_group = customtkinter.CTkLabel(master=self.sidebar_frame, text="SELECT ATTACK MECHANISM", font=bold_font)
        self.label_radio_group.grid(row=5, column=0, columnspan=1, padx=10, pady=10, sticky="")
        self.combobox_interface_attack_selection = customtkinter.CTkComboBox(master=self.sidebar_frame, width=250, height=40, command=self.combo_attack_selection, values=["CAN ID INJECTION ATTACKS","AUTOMATED CAN ID ATTACKS"], variable=self.combobox_attack_var, state='readonly')
        self.combobox_interface_attack_selection.grid(row=6, column=0, pady=15, padx=15, sticky="n")
        
        
        # # create two new frames for two different attacks 
        self.mannual_Attack_Frame = customtkinter.CTkFrame(self.sidebar_frame, width=500, corner_radius=0)
        self.mannual_Attack_Frame.grid(row=7, column=0, padx=10, pady=10, sticky="nsew")
        self.mannual_Attack_Frame.grid_columnconfigure(0, weight=1)
        self.mannual_Attack_Frame.grid_rowconfigure(0, weight=1)
        
        # # frame 2 for automactic attacks
        self.automatic_attack_frame = customtkinter.CTkFrame(self.sidebar_frame, width=500, corner_radius=0)
        self.automatic_attack_frame.grid(row=8, column=0, padx=10, pady=10, sticky="nsew")
        self.automatic_attack_frame.grid_columnconfigure(0, weight=1)
        self.automatic_attack_frame.grid_rowconfigure(0, weight=1)
        
        # # SCAN Can Device 
        self.hex_values = []
        self.combobox_device_var = customtkinter.StringVar()
        self.button_1 = customtkinter.CTkButton(master=self.automatic_attack_frame, border_width=1, text="SCAN CAN DEVICE ID's", font=bold_font, command=self.open_input_dialog_event, width=250, height=40)
        self.button_1.grid(row=1, column=0, pady=20, padx=20)

        self.label_can_device = customtkinter.CTkLabel(master=self.automatic_attack_frame, text="SELECT CAN ID", font=bold_font)
        self.label_can_device.grid(row=2, column=0, padx=15, pady=15)
        self.combobox_device = customtkinter.CTkComboBox(master=self.automatic_attack_frame, width=200,height=40, variable=self.combobox_device_var, state='readonly')
        self.combobox_device.grid(row=3, column=0, pady=10, padx=10)
        CTkScrollableDropdown(self.combobox_device, values=self.hex_values)
        # self.combobox_device.pack(fill="x")

        self.combobox_var = customtkinter.StringVar()
        self.label_radio_group = customtkinter.CTkLabel(master=self.automatic_attack_frame, text="SELECT METHOD", font=bold_font)
        self.label_radio_group.grid(row=4, column=0, columnspan=1, padx=15, pady=15, sticky="")
        self.combobox_method = customtkinter.CTkComboBox(master=self.automatic_attack_frame,
                                     values=["BRUTE FORCE ATTACK","RANDOM PACKET ATTACK"],
                                     command=self.combobox_callback, variable=self.combobox_var, width=200, height=40, state='readonly')
        # self.combobox_method.bind("<<ComboboxSelected>>", self.on_combo_select)
        self.combobox_method.grid(row=5, column=0, pady=10, padx=20)

        # manual attack frame
        
        self.combobox_manual_attack_var = customtkinter.StringVar()
        self.label_manual_attack = customtkinter.CTkLabel(master=self.mannual_Attack_Frame, text="SELECT METHOD", font=bold_font)
        self.label_manual_attack.grid(row=4, column=0, columnspan=1, padx=15, pady=15, sticky="")
        self.combobox_manual_attack = customtkinter.CTkComboBox(master=self.mannual_Attack_Frame, width=230, height=40, command=self.combobox_callback_manual, values=["TEMPLATE BASED ATTACK","DOS ATTACK","PGN ATTACK"], variable=self.combobox_manual_attack_var, state='readonly')
        self.combobox_manual_attack.grid(row=5, column=0, pady=10, padx=20, sticky="n")

        # create textframe
        self.all_input_frame = customtkinter.CTkFrame(self.sidebar_frame, corner_radius=0)
        self.all_input_frame.grid(row=9, column=0, padx=10, pady=10, sticky="nsew")
        self.all_input_frame.grid_columnconfigure(0, weight=1)
        self.all_input_frame.grid_rowconfigure(0, weight=1)

        # create textbox
        self.textbox_var = tkinter.IntVar(value=0)
        self.input_var = customtkinter.IntVar()

    
        self.label_textbox_packet = customtkinter.CTkLabel(master=self.all_input_frame, text="ENTER THE NUMBER OF PACKETS", font=bold_font)
        self.label_textbox_packet.grid(row=1, column=0, padx=10, pady=10, sticky="n")
        self.textbox_packet = customtkinter.CTkTextbox(self.all_input_frame, width=100, height=20, border_width=2)
        self.textbox_packet.grid(row=2, column=0, padx=10, pady=10, sticky="n")

        self.label_textbox_seconds = customtkinter.CTkLabel(master=self.all_input_frame, text="ENTER THE NUMBER OF SECONDS", font=bold_font)
        self.label_textbox_seconds.grid(row=3, column=0, padx=10, pady=10, sticky="n")  
        self.textbox_packet_2 = customtkinter.CTkTextbox(self.all_input_frame, width=100, height=20,border_width=2)
        self.textbox_packet_2.grid(row=4, column=0, padx=10, pady=10, sticky="n")     

        self.label_textbox = customtkinter.CTkLabel(master=self.all_input_frame, text="ENTER 00 or FF", font=bold_font)
        self.label_textbox.grid(row=5, column=0, padx=10, pady=10, sticky="n")
        self.textbox_packet_hexa = customtkinter.CTkTextbox(self.all_input_frame, width=100, height=20,border_width=2)
        self.textbox_packet_hexa.grid(row=6, column=0, padx=10, pady=10, sticky="n")
        
        self.label_first_bit = customtkinter.CTkLabel(master=self.all_input_frame, text="ENTER 0 or 1", font=bold_font)
        self.label_first_bit.grid(row=7, column=0, padx=10, pady=10, sticky="n")
        self.textbox_packet_first_bit = customtkinter.CTkTextbox(self.all_input_frame, width=100, height=20,border_width=2)
        self.textbox_packet_first_bit.grid(row=8, column=0, padx=10, pady=10, sticky="n")
        
        self.label_can_id = customtkinter.CTkLabel(master=self.all_input_frame, text="ENTER LAST TWO DIGITS OF THE CAN ID", font=bold_font)
        self.label_can_id.grid(row=9, column=0, padx=10, pady=10, sticky="n")
        self.textbox_packet_first_can_id = customtkinter.CTkTextbox(self.all_input_frame, width=100, height=20,border_width=2)
        self.textbox_packet_first_can_id.grid(row=10, column=0, padx=10, pady=10, sticky="n")
        

        self.all_input_frame.grid_remove()
        
        # create bottom button frame 
        self.bottom_button_frame = customtkinter.CTkFrame(self)
        self.bottom_button_frame.grid(row=6, column=0, padx=(10, 10), pady=(10, 0), sticky="nsew")
        self.bottom_button_frame.grid_columnconfigure(0, weight=1)
        # self.bottom_button_frame.grid_rowconfigure(0, weight=1)
        row = self.bottom_button_frame.grid_size()[1]

        #create buttons
        self.button_1 = customtkinter.CTkButton(master=self.bottom_button_frame, border_width=1, text="START FUZZING", font=bold_font, command=self.start_fuzzers, width=200)
        self.button_1.grid(row=row + 1, column=0, pady=20, padx=20)
        self.button_2 = customtkinter.CTkButton(master=self.bottom_button_frame, border_width=2, text="STOP FUZZING", font=bold_font, command=self.can_bus_shutdown, width=200)
        self.button_2.grid(row=row + 2, column=0, pady=20, padx=20)
                                
        
        self.button_2.configure(state="disabled", text="STOP", font=bold_font)
        self.button_1.configure(state="disabled", text="START", font=bold_font)
        
        # # # load interface based on platforms
        self.load_interface_based_on_platform()
        self.stop_event = threading.Event()
        self.automatic_attack_frame.grid_remove()
        self.mannual_Attack_Frame.grid_remove()   
        
       
    def ctrlEvent(event):
        if(12==event.state and event.keysym == 'c'):
            return
        else:
            return "break"   

    def stop_event_threading(self):
        self.stop_event.set()
                
    def can_bus_shutdown(self):
        print("shutdown in progress")
        if self.can_bus is not None:
            if self.can_bus._is_shutdown == True:
                print("already shutdown")
            else:
                self.can_bus.shutdown()
              
    def combobox_interface(self, event):
        selected_item = self.combobox_device_var.get()

    def load_interface_based_on_platform(self):
        self.something = []
        os_name = platform.system()
        if os_name == "Windows":
            self.combobox_interface.configure(values=["PCAN_USBBUS1"])
        elif os_name == "Linux":
            CTkScrollableDropdown(self.combobox_interface, values=["can0","can1"], state='readonly')
            # self.combobox_interface.configure(values=["can0","can1"])
        elif os_name == "Darwin":
            self.combobox_interface.configure(values=[])
        else:
            print("Invalid OS Not Supported")

    def open_toplevel(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it

    def combo_attack_selection(self, choice):
        selected_attack = self.combobox_attack_var.get()
        
        if selected_attack == "CAN ID INJECTION ATTACKS":
            self.automatic_attack_frame.grid_remove()
            self.mannual_Attack_Frame.grid()
            self.all_input_frame.grid_remove()
            print("manual frame")
            self.combobox_manual_attack.set(value = "")
            self.combobox_var.set(value="")
            self.combobox_manual_attack_var = ""
        else: 
            self.mannual_Attack_Frame.grid_remove()
            self.automatic_attack_frame.grid()
            self.all_input_frame.grid_remove()
            print("automatic frame")
            self.combobox_manual_attack.set(value = "")
            self.combobox_method.set(value = "")


    def combobox_callback(self, choice):
        print("combobox dropdown clicked:", self.combobox_var.get())

        selected_device = self.combobox_device_var.get()
        select_method = self.combobox_var.get()
        selected_can_id = self.combobox_device_var.get()

        if selected_device and select_method and selected_can_id:
            self.button_1.configure(state="enabled", text="START FUZZING")
            self.all_input_frame.grid()

        if self.combobox_var.get() == "BRUTE FORCE ATTACK":
            self.textbox_packet_2.grid_remove()
            self.textbox_packet.grid_remove()
            self.textbox_packet_hexa.grid_remove()
            self.label_textbox_packet.grid_remove()
            self.label_textbox_seconds.grid_remove()
            self.label_textbox.grid_remove()
            self.textbox_packet_first_bit.grid_remove()
            self.textbox_packet_first_can_id.grid_remove()
            self.label_first_bit.grid_remove()
            self.label_can_id.grid_remove()
            self.all_input_frame.grid_remove()
        elif self.combobox_var.get() == "RANDOM PACKET ATTACK":                
            print("random packet attack")
            self.textbox_packet.grid()
            self.textbox_packet_2.grid_remove()
            self.textbox_packet_hexa.grid_remove()
            self.label_textbox_packet.grid()
            self.label_textbox_seconds.grid_remove()
            self.label_textbox.grid_remove()
            self.textbox_packet_first_bit.grid_remove()
            self.textbox_packet_first_can_id.grid_remove()
            self.label_first_bit.grid_remove()
            self.label_can_id.grid_remove()
            self.all_input_frame.grid()
        else:
            print("Invalid Input")
            
    def combobox_callback_manual(self, choice):
        print("combobox dropdown Manual clicked:", choice)        
        selected_method = self.combobox_interface_attack_selection.get()
        self.combobox_manual_attack_var = self.combobox_manual_attack.get()
        # self.combobox_manual_attack.set(value=choice)
        if selected_method and choice:
            self.button_1.configure(state="enabled", text="START FUZZING")
            self.all_input_frame.grid()
            
            if self.combobox_manual_attack.get() == "TEMPLATE BASED ATTACK":
                print("template based attack")
                self.textbox_packet_2.grid()
                self.textbox_packet.grid_remove()
                self.textbox_packet_hexa.grid_remove()
                self.label_textbox_packet.grid_remove()
                self.label_textbox_seconds.grid()
                self.label_textbox.grid_remove()
                self.textbox_packet_first_bit.grid_remove()
                self.textbox_packet_first_can_id.grid_remove()
                self.label_first_bit.grid_remove()
                self.label_can_id.grid_remove()
            elif self.combobox_manual_attack.get() == "DOS ATTACK":
                print("dos attack")
                self.textbox_packet.grid_remove()
                self.textbox_packet_2.grid()
                self.textbox_packet_hexa.grid()
                self.label_textbox_packet.grid_remove()
                self.label_textbox_seconds.grid()
                self.label_textbox.grid()
                self.textbox_packet_first_bit.grid_remove()
                self.textbox_packet_first_can_id.grid_remove()
                self.label_first_bit.grid_remove()
                self.label_can_id.grid_remove()
            elif self.combobox_manual_attack.get() == "PGN ATTACK":
                print("PGN ATTACK")
                self.textbox_packet_2.grid_remove()
                self.textbox_packet.grid_remove()
                self.textbox_packet_hexa.grid_remove()
                self.label_textbox_packet.grid_remove()
                self.label_textbox_seconds.grid_remove()
                self.label_textbox.grid_remove()
                self.textbox_packet_first_bit.grid()
                self.textbox_packet_first_can_id.grid()
                self.label_first_bit.grid()
                self.label_can_id.grid()
            else:
                print("Invalid Input")        

        ####TEMPLATE BASED FUZZING BACKEND         
    def send_can_message(self, interface, can_id, data):
        # Create a CAN bus instance
        bus = can.interface.Bus(bustype='socketcan', channel=interface)

        # Create a CAN message
        message = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)

        # Send the CAN message
        bus.send(message)
        #print(bus.send(message))
        
        #Close the CAN bus
        bus.shutdown()

    def send_can_packets_from_file(self, interface, file_path):
        # Open the file in read mode
        with open(str(file_path), 'r') as file:
            # Read the file line by line
            for line in file:
                # Extract the CAN ID and data from the line
                can_id, data = line.strip().split(',')

                # Convert the CAN ID to an integer
                can_id = int(can_id)

                # Convert the hexadecimal data to bytes
                data_bytes = bytes.fromhex(data)

                # Send the CAN message
                self.send_can_message(interface, can_id, data_bytes)
                # Convert the bytes data to decimal
                data_decimal = int.from_bytes(data_bytes, byteorder='big', signed=False)
                print("Sent CAN message:", can_id, data_decimal)
                self.textbox_display.insert("end",f"Sent CAN message:{can_id}, {data_decimal}\n")
                self.textbox_display.see("end")
                #time.sleep(0.1)
                

    # Call the send_can_packets_from_file function with the provided file path and interface
    
    def template_can_messages(self):
        # Initialize a connection to the CAN bus (can0)
        # Prompt the user to enter the file path and interface
        self.textbox_display.delete("1.0",customtkinter.END)
        file_path = 'CAN_ID_template.txt'
        interface = 'can0'
        can_interface_val = self.combobox_interface.get()
        seconds = self.textbox_packet_2.get("0.0", "end").strip()
        bitrate_var = self.combo_bitrate.get()
        try:
            if can_interface_val == "":
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE SELECT VALID INTERFACE")
            elif bitrate_var == "":
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE SELECT VALID BITRATE")
            elif seconds == "":
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID DURATION")
                self.textbox_packet_2.configure(border_color="red")
            else:    
                self.textbox_packet_2.configure(border_color="gray50")
                self.can_bus = can.interface.Bus(bustype='socketcan', channel=can_interface_val, bitrate=bitrate_var)
                self.button_2.configure(state="enabled", text="STOP FUZZING")
                duration = seconds
                can_device_id = self.combobox_device_var.get()
                # selected_can_id_decimal = int(can_device_id, 16)
                if not duration:
                    tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID DURATION")
                elif not duration.isdigit():
                    self.textbox_packet_2.configure(border_color="red")
                    tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID DURATION")
                else:
                    self.textbox_packet_2.configure(border_color="gray50")
                    end_time = time.time() + float(duration)
                
                    with open('CAN_ID_template.txt', 'w') as sniff_can_msg:
                        while time.time() < end_time:
                            try:
                                # Receive message
                                received_msg = self.can_bus.recv()
                                received_can_id = received_msg.arbitration_id
                                data = received_msg.data.hex()
                                print("Received message:", received_msg)
                                formatted_msg = f"Received message: {received_msg}"
                                threading.Thread(target=self.add_line(received_msg)).start()
                                sniff_can_msg.write(f"{received_can_id},{data}\n")
	                            # Extract CAN ID and convert data to decimal
	                            #can_id = received_can_id
	                            #data_bytes = bytes.fromhex(data)
	                            #data_decimal = int.from_bytes(data_bytes, byteorder='big', signed=False)
	                            # Display Sent CAN message in the GUI
	                            #self.textbox_display.insert("end", f"Sent CAN message: {can_id}, {data_decimal}\n")
	                            #self.textbox_display.see("end")  # Scroll to the end of the text widget
                            except Exception as e:
                                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message=str(e))
                                break
                    self.send_can_packets_from_file(can_interface_val, file_path) 
                    self.can_bus.shutdown()
        except Exception as e:
            tkinter.messagebox.showinfo(title="ERROR MESSAGE", message=str(e))
        
    def start_and_stop_can_ip(self):
        #subprocess.run(['sudo', 'ip', 'link', 'set', 'can0', 'down'])
        bitrate_var = self.combo_bitrate.get()
        can_interface_val = self.combobox_interface.get()
        text = self.start_can_button.cget("text")
        if can_interface_val == "":
            tkinter.messagebox.showinfo(title="ERROR", message="PLEASE SELECT VALID INTERFACE")
            return
        elif bitrate_var == "":
            tkinter.messagebox.showinfo(title="ERROR", message="PLEASE SELECT VALID BITRATE")
            return
        try:
            if text == "CAN UP":
                command = f"sudo ip link set {can_interface_val} down && sudo ip link set {can_interface_val} up type can bitrate {bitrate_var}"
                subprocess.run(command, shell=True, check=True)
                tkinter.messagebox.showinfo(title="Success", message="{can_interface_val} up and Running")
                self.start_can_button.configure(text="CAN DOWN")
            elif text == "CAN DOWN":
                command = f"sudo ip link set {can_interface_val} down"
                subprocess.run(command, shell=True, check=True)
                tkinter.messagebox.showinfo(title="Success", message="{can_interface_val} Shutdown")
                self.start_can_button.configure(text="CAN UP")
        except Exception as e:
            tkinter.messagebox.showinfo(title="ERROR", message=str(e))

    # def stop_can_ip(self):
    #     #subprocess.run(['sudo', 'ip', 'link', 'set', 'can0', 'down'])
    #     can_interface_val = self.combobox_interface.get()
    #     try:
    #         command = f"sudo ip link set {can_interface_val} down"
    #         subprocess.run(command, shell=True, check=True)
    #         tkinter.messagebox.showinfo(title="Success", message="{can_interface_val} Shutdown")
    #     except Exception as e:
    #         tkinter.messagebox.showinfo(title="ERROR", message=str(e))
        
    def start_fuzzers(self):
        # self.button_2.configure(state="enabled", text="Disabled Stop")
        if self.combobox_var.get() == "BRUTE FORCE ATTACK":
            print(self.combobox_var.get())
            self.brute_force_attack()
        elif self.combobox_var.get() == "RANDOM PACKET ATTACK":
            print(self.combobox_var.get())
            self.random_packet_attack()
        elif self.combobox_manual_attack.get() == "TEMPLATE BASED ATTACK":
            print("start_fuzzing", self.combobox_manual_attack.get())
            self.template_can_messages()
        elif self.combobox_manual_attack.get() == "DOS ATTACK":
            print("start_fuzzing", self.combobox_manual_attack.get())
            self.dos_can_messages()
        elif self.combobox_manual_attack.get() == "PGN ATTACK":
            print("start_fuzzing", self.combobox_manual_attack.get())
            self.do_pgn_attack()
        else:
            print("Invalid Input")

    ####BRUTE FORCE FUZZING BACKENDs        
    def brute_force_attack(self):
        # Initialize a connection to the CAN bus (can0)
        self.textbox_display.delete("1.0",customtkinter.END)
        self.button_2.configure(state="enabled", text="STOP FUZZING")
        can_interface_val = self.combobox_interface.get()
        bitrate_var = self.combo_bitrate.get()
        try:
            if can_interface_val == "":
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE SELECT VALID INTERFACE")
            elif bitrate_var == "":
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE SELECT VALID BITRATE")
            else:
                self.can_bus = can.interface.Bus(bustype='socketcan', channel=can_interface_val, bitrate=bitrate_var)
                self.button_2.configure(state="enabled", text="STOP FUZZING")

                #for virtual device uncomment this
                # self.can_bus = VirtualBus(bustype='vsocketcan', channel='vcan0', bitrate=bitrate_var)

                # Create a list of 500 zeros to represent the initial message
                can_msg = [0] * 500
                can_device_id = self.combobox_device_var.get()
                can_id = int(can_device_id, 16)

                self.fuzzing = True  # Start the fuzzing process
                for one in range(255):
                    for two in range(255):
                        for three in range(255):
                            for four in range(255):
                                for five in range(255):
                                    for six in range(255):
                                        for seven in range(255):
                                            for eight in range(255):
                                                packet = [can_msg[one] + one, can_msg[two] + two, can_msg[three] + three, can_msg[four] + four, can_msg[five] + five, can_msg[six] + six, can_msg[seven] + seven, can_msg[eight] + eight]
                                                packet_str = ', '.join(map(str, packet))
                                                print(f"{can_id}    [8]  {packet_str}\n")  # Update the log text in the required format
                                                msg = can.Message(arbitration_id=can_id, data=packet, is_extended_id=False)
                                                threading.Thread(target=self.add_line(msg)).start()
                                                self.can_bus.send(msg)
                                                time.sleep(0.1)  # Delay between packets
                                            can_msg[eight] = 0
                                        can_msg[seven] = 0
                                    can_msg[six] = 0
                                can_msg[five] = 0
                            can_msg[four] = 0
                        can_msg[three] = 0
                    can_msg[two] = 0
                self.can_bus.flush_tx_buffer()
                self.can_bus.shutdown()
        except Exception as e:
            tkinter.messagebox.showinfo(title="ERROR MESSAGE", message=str(e))
            
    #### RANDOM METHOD
    def random_packet_attack(self):
        self.textbox_display.delete("1.0",customtkinter.END)
        can_interface_val = self.combobox_interface.get()
        bitrate_var = self.combo_bitrate.get()
        packets = self.textbox_packet.get("0.0", "end").strip()
        try:
            if can_interface_val == "":
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE SELECT VALID INTERFACE")
            elif bitrate_var == "":
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE SELECT VALID BITRATE")
            elif packets == "":
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID NUMBER OF PACKETS")
                self.textbox_packet.configure(border_color="red")
            else:  
                self.textbox_packet.configure(border_color="gray50")
                self.can_bus = can.interface.Bus(bustype='socketcan', channel=can_interface_val, bitrate=bitrate_var)
                self.button_2.configure(state="enabled", text="STOP FUZZING")
                #for virtual device uncomment this
                #can_bus = VirtualBus(bustype='vsocketcan', channel='vcan0', bitrate=250000)
                # Create a list of 500 zeros to represent the initial message
                can_msg = [0] * 500
                n = self.textbox_packet.get("0.0", "end").strip()
                can_device_id = self.combobox_device_var.get()
                can_id = int(can_device_id, 16)
                if n.isdigit():
                    n = int(n)
                    if n == 0:
                        tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID NUMBER OF PACKETS")
                    else:
                        for x in range(n):
                            a=random.randint(1,255)
                            b=random.randint(1,255)
                            c=random.randint(1,255)
                            d=random.randint(1,255)
                            e=random.randint(1,255)
                            f=random.randint(1,255)
                            g=random.randint(1,255)
                            h=random.randint(1,255)
                            print("random - ",a,b,c,d,e,f,g,h) # send can msg in this line
                            values = "random - ",a,b,c,d,e,f,g,h
                            msg = can.Message(arbitration_id=can_id, data=[a, b, c, d, e, f, g, h], is_extended_id=False)
                            threading.Thread(target=self.add_line(values)).start()
                            
                            try:
                                self.can_bus.send(msg)
                            except ValueError as e:
                                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message=f"Error while sending CAN message: {str(e)}")
                                
                            time.sleep(0.1)
                self.can_bus.shutdown()
                #else:
                    # Handle invalid input
                    # tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID DATA")
        except Exception as e:
            # Handle other exceptions here
            tkinter.messagebox.showinfo(title="ERROR MESSAGE", message=str(e))


    def add_line(self,msg):
        line = msg
        print("inside add line method", msg)
        self.textbox_display.insert(customtkinter.END, str(line) + '\n')
        self.textbox_display.see(customtkinter.END)
        self.textbox_display.update()

        
    def open_input_dialog_event(self):
        bitrate_var = self.combo_bitrate.get()
        can_interface_val = self.combobox_interface.get()
        if bitrate_var == "":
            tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID BITRATE")
        elif can_interface_val == "":
            tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID INTERFACE")
        else:
            answer = customtkinter.CTkInputDialog(text = "ENTER DURATION TO SNIFF PACKETS", title="DURATION")
            self.input_var = answer.get_input()
            if self.input_var == "":
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID DURATION")
            elif not self.input_var.isdigit():
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID DURATION")
            else:
                self.sniff_can_messages()
                # self.load_can_id()


    def combobox_device(self, choice):
        print("combobox  device dropdown clicked:", self.combobox_device_var.get())

    def load_can_id(self):
        self.hex_values = []
        try:
            with open("Unique_ID.txt", 'r') as file:
                text = file.read()
                self.hex_values = re.findall(r'HEX Format: (0x[a-fA-F0-9]+)', text)
                # self.combobox_device.configure(values=self.hex_values)
                CTkScrollableDropdown(self.combobox_device, values=self.hex_values)
                self.combobox_device.set(self.hex_values[0])
        except:
            tkinter.messagebox.showerror("ERROR MESSAGE", "File is Empty Please Check the Connection and Try Again")

    ####SCAN PACKETS AND SORT UNIQUE NODES BACKEND                
    def sort_can_id(self):
        can_interface_val = self.combobox_interface.get()
        self.can_bus = can.interface.Bus(bustype='socketcan', channel=can_interface_val, bitrate=250000)
        input_file = 'CAN_ID.txt'
        output_file = 'Unique_ID.txt'
        with open(input_file, 'r') as file_in, open(output_file, 'w') as file_out:
            unique_strings = set()
            for line in file_in:
                line = line.strip()
                if line:
                    unique_strings.add(line)
            for string in unique_strings:
                file_out.write(string + '\n')
        self.load_can_id()

    def sniff_can_messages(self):
        # Initialize a connection to the CAN bus (can0)
        can_interface_val = self.combobox_interface.get()
        bitrate_var = self.combo_bitrate.get()
        if can_interface_val == "":
            tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID INTERFACE")
        elif bitrate_var == "":
            tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID BITRATE")
        else:
            try:   
                self.can_bus = can.interface.Bus(bustype='socketcan', channel=can_interface_val, bitrate=bitrate_var)        
                self.textbox_display.delete("1.0", customtkinter.END)
                duration = self.input_var
                end_time = time.time() + float(duration)
                with open('CAN_ID.txt', 'a') as sniff_can_msg:
                    while time.time() < end_time:
                        # Receive message
                        received_msg = self.can_bus.recv()
                        print("Received message:", received_msg)
                        threading.Thread(target=self.add_line(received_msg)).start()
                        sniff_can_msg.write("HEX Format: "+str(hex(received_msg.arbitration_id)) + " Integer Format: " +str(received_msg.arbitration_id)+ "\n")
                self.sort_can_id()
            except:
                # self.open_toplevel()
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="SOMETHING WENT WRONG PLEASE TRY AGAIN")
    
    ####DOS BASED FUZZING BACKEND
    def send_can_message_dos(self, interface, can_id, data):
        
        # Create a CAN bus instance
        bus = can.interface.Bus(bustype='socketcan', channel=interface)

        # Create a CAN message
        message = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
               
                
        # Send the CAN message
        bus.send(message)
    
        #Close the CAN bus
        bus.shutdown()
        
    def send_can_packets_from_file_dos(self, interface, file_path):
        # Open the file in read mode
        with open(file_path, 'r') as file:
            # Read the file line by line
            for line in file:
                # Extract the CAN ID and data from the line
                can_id, data = line.strip().split(',')
                
                # print("Sending Can Meesage: ", data)
        
                formatted_msg = f"Sending Can message: {data}"
                print("Sending CAN message with ID:", can_id)
                threading.Thread(target=self.add_line(formatted_msg)).start()


                # Convert the CAN ID to an integer
                can_id = int(can_id)

                # Convert the hexadecimal data to bytes
                data_bytes = bytes.fromhex(data)
                
                
                # Send the CAN message
                self.send_can_message_dos(interface, can_id, data_bytes)
                time.sleep(0.1)
                
    
    # Call the send_can_packets_from_file function with the provided file path and interface
    def dos_can_messages(self):
        self.textbox_display.delete("1.0",customtkinter.END)
        file_path = 'CAN_ID_DOS.txt'
        # interface = 'can0'
        # Initialize a connection to the CAN bus (can0)

        can_interface_val = self.combobox_interface.get()
        duration = self.textbox_packet_2.get("0.0", "end").strip()
        data_flood = self.textbox_packet_hexa.get("0.0", "end").strip()
        
        bitrate_var = self.combo_bitrate.get()
        if can_interface_val == "":
            tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID INTERFACE")
        elif bitrate_var == "":
            tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID BITRATE")
        elif not duration and not data_flood:
            tkinter.messagebox.showinfo(title="Error", message="PLEASE ENTER VALID DURATION")
            self.textbox_packet_hexa.configure(border_color="red")
            self.textbox_packet_2.configure(border_color="red")
        elif not duration.isdigit():
            tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID DURATION")
            self.textbox_packet_2.configure(border_color="red")
        elif data_flood not in ["00", "FF"] or len(data_flood) != 2:
            tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID DATA 00 or FF")
            self.textbox_packet_hexa.configure(border_color="red")
        else:
            self.textbox_packet_2.configure(border_color="gray50")
            self.textbox_packet_hexa.configure(border_color="gray50")
            self.can_bus = can.interface.Bus(bustype='socketcan', channel=can_interface_val, bitrate=bitrate_var)
            self.button_2.configure(state="enabled", text="STOP FUZZING")
            can_device_id = self.combobox_device_var.get()
            # selected_can_id_decimal = int(can_device_id, 16)
            end_time = time.time() + float(duration)
            #data_flood = data_flood * 8
            with open('CAN_ID_DOS.txt', 'w') as sniff_can_msg:
                while time.time() < end_time:
                    #Receive nessage
                    received_msg = self.can_bus.recv()
                    received_can_id = received_msg.arbitration_id
                    data = data_flood * 8
                    #data = received_msg.data.hex()  
                    sniff_can_msg.write(f"{received_can_id},{data}\n")
                    #threading.Thread(target=self.add_line(received_msg)).start()
                    #print("Sending CAN message with ID:", can_id)
            #self.dos_can_messages(interface)
            self.send_can_packets_from_file_dos(can_interface_val, file_path)
               
            
            
###PGN ATTACK
    def generate_random_payload(self):
        payload = [random.randint(1, 255) for _ in range(7)]
        return payload

    def generate_random_4bit_hex(self):
        # hex_value = ''.join(random.choice('0123456789ABCDEF') for _ in range(1))
        # return hex_value
        random_value = random.randint(0, 15)
        hex_value = format(random_value, "X")
        return hex_value
    
    def is_valid_hexa(self,hexa):
        hex_pattern = r'^[0-9a-fA-F]+$'
        return bool(re.match(hex_pattern, hexa))
        
    def do_pgn_attack(self):
        with open('CAN_ID_PGN', 'a') as sniff_can_msg:
            self.textbox_display.delete("1.0",customtkinter.END)
            can_interface_val = self.combobox_interface.get()
            bitrate_var = self.combo_bitrate.get()
        
            first_bit = self.textbox_packet_first_bit.get("0.0", "end").strip()
            last_hex_digits = self.textbox_packet_first_can_id.get("0.0", "end").strip()

            # Validation check for first_bit
            if first_bit == "":
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="first_bit MUST BE EITHER 0 or 1")
                self.textbox_packet_first_bit.configure(border_color="red")
            elif first_bit not in ["0", "1"]:
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="first_bit MUST BE EITHER 0 or 1")
                self.textbox_packet_first_bit.configure(border_color="red")
            elif last_hex_digits == "":
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="last_hex_digits MUST BE A VALID two-digit NUMBER") 
                self.textbox_packet_first_can_id.configure(border_color="red")
            elif first_bit == "" and last_hex_digits == "":
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE ENTER VALID DATA")
                self.textbox_packet_first_bit.configure(border_color="red")
                self.textbox_packet_first_can_id.configure(border_color="red")
                return
            else:
                self.textbox_packet_first_bit.configure(border_color="gray50")
                self.textbox_packet_first_can_id.configure(border_color="gray50")


            # Validation check for last_hex_digits
            if not all(c in "0123456789" for c in last_hex_digits) or len(last_hex_digits) != 2:
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="last_hex_digits MUST BE A VALID two-digit NUMBER")
                self.textbox_packet_first_can_id.configure(border_color="red")
                return

            if can_interface_val == "":
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE SELECT VALID INTERFACE")
            elif bitrate_var == "":
                tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="PLEASE SELECT VALID BITRATE")
            else:
                self.textbox_packet_first_bit.configure(border_color="gray50")
                self.textbox_packet_first_can_id.configure(border_color="gray50")
                # self.can_bus = VirtualBus(bustype='vsocketcan', channel='vcan0', bitrate=bitrate_var)
                self.button_2.configure(state="enabled", text="STOP FUZZING")
                self.can_bus = can.interface.Bus(bustype='socketcan', channel=can_interface_val, bitrate=bitrate_var)    
                while True:
                    payload = self.generate_random_payload()
                    hex_value_list = [self.generate_random_4bit_hex() for _ in range(4)]
                    random_hex_string = "".join(hex_value_list)
                    can_id = first_bit + random_hex_string + last_hex_digits
                
                    if not self.is_valid_hexa(can_id):
                        print("Invalid CAN ID generated. Exiting.")
                        tkinter.messagebox.showinfo(title="ERROR MESSAGE", message="Invalid CAN ID generated. Exiting.")
                        return
                
                    can_id_in_int = int(can_id,16)
                
                    msg = can.Message(arbitration_id=int(can_id, 16), data=payload, is_extended_id=True)
                    self.can_bus.send(msg)
                    formatted_string = "Timestamp: {:>16} ID: {} X Rx DL: 8 {}".format("0.000000", can_id, payload)
                    threading.Thread(target=self.add_line(formatted_string)).start()
                    print("Timestamp: {:>16} ID: {} X Rx DL: 8 {}".format("0.000000", can_id, payload))
                    sniff_can_msg.write(f"{can_id},{','.join(map(str, payload))}\n")

                self.can_bus.shutdown()
            
if __name__ == "__main__":
    app = App()
    app.mainloop()
