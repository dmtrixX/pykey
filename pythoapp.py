import numpy as np
import pygame
import tkinter as tk
from tkinter import ttk, messagebox

class NoteFrequencyCalculator:
    def __init__(self, master):
        self.master = master
        self.master.title("Py Key player")
        
        self.base_frequency = tk.DoubleVar(value=32.59)
        self.base_frequency.trace('w', self.update_note_info)
        self.notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.pythagorean_ratio = [1, 256/243, 9/8, 32/27, 81/64, 4/3, 729/512, 3/2, 128/81, 27/16, 16/9, 243/128]

        self.setup_widgets()
        self.update_note_info()

        pygame.mixer.init(frequency=44100)

    def setup_widgets(self):
        tk.Label(self.master, text="Note").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(self.master, text="Frequency (Hz)").grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self.master, text="BPM").grid(row=0, column=2, padx=5, pady=5)
        tk.Label(self.master, text="BPM1").grid(row=0, column=3, padx=5, pady=5)
        tk.Label(self.master, text="BPM2").grid(row=0, column=4, padx=5, pady=5)
        tk.Label(self.master, text="BPM3").grid(row=0, column=5, padx=5, pady=5)

        self.base_freq_entry = ttk.Entry(self.master, textvariable=self.base_frequency, width=10)
        self.base_freq_entry.grid(row=1, column=0, padx=5, pady=5)

        self.update_button = ttk.Button(self.master, text="Update", command=self.update_note_info)
        self.update_button.grid(row=1, column=1, padx=5, pady=5)

        self.freq_slider = ttk.Scale(self.master, from_=18, to=36, variable=self.base_frequency, orient='horizontal', command=self.update_note_info)
        self.freq_slider.grid(row=1, column=2, columnspan=4, padx=5, pady=5, sticky='ew')

        self.master.bind("<Button-3>", self.increment_frequency)
        self.master.bind("<MouseWheel>", self.scroll_frequency)

        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save", command=self.save_config)
        file_menu.add_command(label="Load", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def update_note_info(self, *args):
        base_frequency = round(self.base_frequency.get(), 2)  # Round to 2 decimal places
        self.base_frequency.set(base_frequency)  # Update the displayed value in the entry and slider
        
        for widget in self.master.grid_slaves():
            if int(widget.grid_info()["row"]) > 1:
                widget.grid_forget()

        for i, note in enumerate(self.notes, start=2):
            frequency = base_frequency * self.pythagorean_ratio[i-2]
            bpm = (60 * frequency) / 4
            bpm1 = (60 * frequency) / 8
            bpm2 = (60 * frequency) / 16
            bpm3 = (60 * frequency) / 32
            tk.Label(self.master, text=note).grid(row=i, column=0, padx=5, pady=5)
            tk.Label(self.master, text=f"{frequency:.2f}").grid(row=i, column=1, padx=5, pady=5)
            tk.Label(self.master, text=f"{bpm:.2f}").grid(row=i, column=2, padx=5, pady=5)
            tk.Label(self.master, text=f"{bpm1:.2f}").grid(row=i, column=3, padx=5, pady=5)
            tk.Label(self.master, text=f"{bpm2:.2f}").grid(row=i, column=4, padx=5, pady=5)
            tk.Label(self.master, text=f"{bpm3:.2f}").grid(row=i, column=5, padx=5, pady=5)
            tk.Button(self.master, text="\u25B6""Play", command=lambda f=frequency: self.play_frequency(f)).grid(row=i, column=6, padx=5, pady=5)

    def increment_frequency(self, event):
        self.base_frequency.set(self.base_frequency.get() + 0.01)
        self.update_note_info()

    def scroll_frequency(self, event):
        self.base_frequency.set(self.base_frequency.get() + (0.01 if event.delta > 0 else -0.01))  
        self.update_note_info()

    def play_frequency(self, frequency):
        fs = 44100  
        seconds = 1.8
        fade_duration = 0.03
        
        t = np.linspace(0, seconds, int(fs * seconds), False)
        
        note = np.sin(frequency * t * 2 * np.pi)
        
        fade_samples = int(fade_duration * fs)
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        
        fade = np.ones_like(note)
        fade[:fade_samples] = fade_in 
        fade[-fade_samples:] = fade_out
        
        note *= fade
        note = np.column_stack((note, note))
        audio = (note * 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(audio)
        sound.play()

    def save_config(self):
        config = {'base_frequency': self.base_frequency.get()}
        with open('config.txt', 'w') as file:
            file.write(str(config))
        messagebox.showinfo("Save Configuration", "Configuration saved successfully.")

    def load_config(self):
        try:
            with open('config.txt', 'r') as file:
                config = eval(file.read())
                self.base_frequency.set(config['base_frequency'])
                self.update_note_info()
            messagebox.showinfo("Load Configuration", "Configuration loaded successfully.")
        except Exception as e:
            messagebox.showerror("Load Configuration", f"Error loading configuration: {e}")

    def show_about(self):
        messagebox.showinfo("About", "Note Frequency to BPM Calculator and Key Player\n"
        "Version 1.0\n"
        "Developed by Dmitriy Krastev\n\n"
        "This application allows you to calculate the frequencies of musical notes based on a base frequency input, "
        "using the Pythagorean tuning system. The Pythagorean tuning system is an ancient method of tuning that is based "
        "on pure perfect fifths (3:2 ratio) and other simple ratios derived from it. This system emphasizes harmonic "
        "relationships that are pleasing to the ear.\n\n"
        "Key Features:\n"
        "- Calculate note frequencies from a base frequency using Pythagorean ratios.\n"
        "- Convert note frequencies to beats per minute (BPM) for different subdivisions.\n"
        "- Real-time updates and user-friendly controls for adjusting frequencies.\n"
        "- Play calculated note frequencies.\n"
        "- Save and load configurations for recurring use.\n\n"
        "This tool is ideal for musicians, music producers, educators, and hobbyists to explore and understand "
        "the relationships between frequencies, notes, and rhythms.\n\n"
        "For more information or support, please contact Dmitriy Petrov Krastev.\n"
        "ratracedmtrix@gmail.com")

def main():
    root = tk.Tk()
    app = NoteFrequencyCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
