import tkinter as tk
from tkinter import messagebox
import zipfile
import os
import pyboard
import serial.tools.list_ports

class GameberryInstaller(tk.Tk):
    def __init__(self):
        super().__init__()
        print("Initializing GUI")
        self.title("Gameberry Installer")

        self.label1 = tk.Label(self, text="WARNING: IF YOU CONTINUE, EVERY FILE ON YOUR MICROCONTROLLER WILL BE DELETED,", fg="red")
        self.label2 = tk.Label(self, text="MAKE SURE THAT YOU DOWNLOADED VERSION FOR CORRECT DEVICE!", fg="red")
        self.label1.pack(pady=5)
        self.label2.pack(pady=5)

        self.label = tk.Label(self, text="Select your device COM port:")
        self.label.pack(pady=10)

        self.com_port_var = tk.StringVar(self)
        self.com_ports = self.get_com_ports()
        if self.com_ports:
            self.com_port_var.set(self.com_ports[0])
            self.com_port_menu = tk.OptionMenu(self, self.com_port_var, *self.com_ports)
            self.com_port_menu.pack(pady=5)
        else:
            self.label.config(text="No COM ports found")

        self.start_button = tk.Button(self, text="Start", command=self.start_process)
        self.start_button.pack(pady=20)
        self.ghLabel = tk.Label(self, text="https://github.com/Kitki30/GameBerry")
        self.ghLabel.pack(pady=10)

    def get_com_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def start_process(self):
        print("Instalation started!")
        device = self.com_port_var.get()
        print("Selected COM Port: "+device)
        zip_path = "./package.zip" 
        extract_to = "./Package"

        try:
            pyb = pyboard.Pyboard(device)
        except pyboard.PyboardError:
            print("Failed to connect.")
            messagebox.showerror("Connection Error", "Failed to connect. Make sure the device you selected is your microcontroller.")
            return

        try:
            pyb.enter_raw_repl()

            list_files_command = """
import os

def list_files(directory):
    try:
        return [f for f in os.listdir(directory)]
    except:
        return []

def list_all_files(directory):
    files = []
    directories = [directory]
    while directories:
        current_dir = directories.pop(0)
        for entry in list_files(current_dir):
            full_path = current_dir + '/' + entry
            if entry != '.' and entry != '..':
                try:
                    if os.stat(full_path)[0] & 0x4000:  # Directory
                        directories.append(full_path)
                    else:
                        files.append(full_path)
                except:
                    pass
    return files

files = list_all_files('/')
for f in files:
    print(f)
"""
            print("Listing files on device")
            file_list = pyb.exec_(list_files_command).decode().split('\r\n')

            for file_path in file_list:
                if file_path:
                    delete_command = "import os\nos.remove('{}')".format(file_path)
                    pyb.exec_(delete_command)
                    print("Deleted file: "+file_path)

            pyb.exit_raw_repl()

            print("Extracting instalation package")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)

            pyb.enter_raw_repl()

            print("Uploading files")
            for root, dirs, files in os.walk(extract_to):
                for file in files:
                    local_path = os.path.join(root, file)
                    remote_path = "/".join(local_path.split('/')[1:])  # Construct remote path
                    try:
                        with open(local_path, 'rb') as f:
                            content = f.read()
                        pyb.fs_put(local_path, remote_path)
                        print(f"Uploaded {local_path} to {remote_path}")
                    except Exception as e:
                        print(e)
                        messagebox.showerror("Upload Error", f"Failed to upload {local_path}: {e}")
                        messagebox.showerror("Installation Failed!", "Installation failed!")
                        return 
            
            pyb.exit_raw_repl()
            pyb.close()
            print("Instalation succesfull")
            messagebox.showinfo("Success", "Gameberry succesfully installed to device.\nPlease restart it!")
            os.rmdir("./Package")
            print("Deleted extracted package from computer")

        except Exception as e:
            print(e)
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    app = GameberryInstaller()
    app.mainloop()
