from config import BASE_URL
from hamster import HamsterIO, pretty

import customtkinter
import threading
import random
import time
import webbrowser
import os
import sys
import psutil


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hamster IO | https://clck.ru/3B6d3c")
        self.geometry("400x600")
        self.minsize(400, 600)
        self.collected = 0
        self.iconbitmap(self.resource_path("hamster.ico"))

        self.resizable(True, True)
        self.bind_all("<Key>", self._onKeyRelease, "+")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create an input field for the token
        self.token_label = customtkinter.CTkLabel(self, text="⨠ Token:")
        self.token_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.token_entry = customtkinter.CTkEntry(self, placeholder_text="Input your Bearer token")
        self.token_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        # Create buttons
        self.start_button = customtkinter.CTkButton(self, text="Start", command=self.start_process)
        self.start_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.guide_button = customtkinter.CTkButton(self, 
            text="Guide", command=self.open_guide, 
            fg_color="#ADD8E6", hover_color="#87CEEB", text_color="black"
,
        )
        self.guide_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Create a text box to display logs
        self.log_box = customtkinter.CTkTextbox(self, width=300, height=200)
        self.log_box.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.about_label = customtkinter.CTkLabel(self, text="")
        self.about_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)


        self.thread = None
        self.hamster = None
        self.timer = None
    
    def _onKeyRelease(self, event):
        ctrl  = (event.state & 0x4) != 0
        if event.keycode == 88 and ctrl and event.keysym.lower() != "x": 
            event.widget.event_generate("<<Cut>>")

        if event.keycode == 86 and ctrl and event.keysym.lower() != "v": 
            event.widget.event_generate("<<Paste>>")

        if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
            event.widget.event_generate("<<Copy>>")

    def resource_path(self, relative_path):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def open_guide(self):
        webbrowser.open_new_tab("https://clck.ru/3B6d3c")

    def add_log(self, message):
        self.log_box.insert("0.0", message + "\n")

    def on_closing(self):
        self.destroy()
        self.thread = None
        current_system_pid = os.getpid()
        ThisSystem = psutil.Process(current_system_pid)
        ThisSystem.terminate()

    def start_process(self):
        token = self.token_entry.get()
        if token:
            self.start_button.configure(state="disabled")
            self.thread = threading.Thread(target=self.process_loop, args=(token,))
            self.thread.start()

    def stop_process(self):
        if self.hamster:
            self.hamster.stop_process = True
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.start_button.configure(state="normal")

    def process_loop(self, token):
        self.hamster = HamsterIO(base_url=BASE_URL, token=token, work=True, logs=self.add_log)
        self.hamster.stop_process = False

        while not self.hamster.stop_process:
            try:
                time.sleep(1)
                if self.timer == None or time.time() - self.timer > 60:
                    self.timer = time.time()
                    self.profile = self.hamster.sync_profile()
                    self.collected += self.profile['lastPassiveEarn']
                    self.about_label.configure(
                        text=(
                        f"Balance: {pretty(int(self.profile['balance']))} "
                        f"(+{pretty(int(self.profile['per_hour']))}/hour) "
                        f"\n"
                        f"Auto collected: {pretty(int(self.profile['lastPassiveEarn']))}, "
                        f"by using HamsterIO: {pretty(int(self.collected))}"
                        )
                    )
                if self.profile == None:
                    time.sleep(50)
                    continue
                
                time.sleep(random.randint(1, 3))

                self.upgrades = self.hamster.get_best_upgrades()
                time.sleep(random.randint(3, 5))

                buy_upgrade = self.hamster.buy_best_upgrade(self.upgrades)
                time.sleep(10)
            except:
                continue

        self.add_log("Process stopped.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
