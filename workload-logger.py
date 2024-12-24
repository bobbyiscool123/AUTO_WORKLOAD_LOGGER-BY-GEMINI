import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import google.generativeai as genai
from datetime import datetime
import os
from dotenv import load_dotenv
import re
import json
import threading
from google.ai.generativelanguage_v1beta.types import content

load_dotenv()

# Get the Gemini API key from the environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Check if the API key is set
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not set in .env file.")
    exit()

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# --- Gemini Model Configuration ---
generation_config = {
    "temperature": 2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
    system_instruction="You are a system that simulates a console logging environment. For every user input you receive, you will generate a simulated console log entry.\n\nIf the user input contains the phrase \"bad news\", format the output as a JavaScript error log, starting with [Error] followed by the user's input.\n\nFor all other user inputs shorter than 30 characters, format the output as a structured log entry that resembles code, demonstrating the logical structure of the input. Start each log with [Log] and use indentation or keywords to show the parts of the input. For example, if the input is \"The cat sat\", the output could be:\n\n[Log] {\n[Log] subject: \"The cat\",\n[Log] action: \"sat\"\n[Log] }\n\nIf the user input is longer than 30 characters, break it down into multiple logically connected console log entries that make sense. Each entry should start with [Server] followed by a descriptive message about a part of the user's input. For example, if the user input is \"The quick brown fox jumps over the lazy fox with great agility and speed\", the output could be:\n\n[Server] Processing input: \"The quick brown fox jumps over the lazy fox with great agility and speed\"\n[Server] Analyzing subject: \"The quick brown fox\"\n[Server] Identifying action: \"jumps over the lazy fox\"\n[Server] Detecting attributes: \"with great agility and speed\"",
)

chat_session = model.start_chat(
    history=[
    ]
)

# --- Color Palettes ---
themes = {
    "Windows 11 Blue": {
        "bg_color": "#f0f8ff",
        "frame_bg": "#e6f0ff",
        "button_bg": "#d0e0ff",
        "button_fg": "#333333",
        "button_hover": "#c0d0ef",
        "text_color": "#000000",
        "entry_bg": "#ffffff",
        "entry_fg": "#000000",
        "scroll_bg": "#c0d0ef",
        "scroll_fg": "#333333",
    },
    "Light Gray": {
        "bg_color": "#f0f0f0",
        "frame_bg": "#e0e0e0",
        "button_bg": "#e0e0e0",
        "button_fg": "#333333",
        "button_hover": "#d0d0d0",
        "text_color": "#333333",
        "entry_bg": "#ffffff",
        "entry_fg": "#000000",
        "scroll_bg": "#d0d0d0",
        "scroll_fg": "#333333",
    },
     "Dark": {
        "bg_color": "#2b2b2b",  # Dark gray background
        "frame_bg": "#333333",  # Darker gray frame background
        "button_bg": "#444444",  # Slightly lighter dark gray for buttons
        "button_fg": "#ffffff",  # White for button text
        "button_hover": "#555555",  # Lighten on hover
        "text_color": "#ffffff",  # White text
        "entry_bg": "#444444",  # Dark gray for entry
        "entry_fg": "#ffffff",  # White foreground for entry
        "scroll_bg": "#555555", # Dark gray for scrollbar
        "scroll_fg": "#ffffff"  # White for scrollbar
    },
    "High Contrast": {
        "bg_color": "#000000",  # Black background
        "frame_bg": "#222222",  # Slightly lighter black frame background
        "button_bg": "#ffff00",  # Bright yellow for buttons
        "button_fg": "#000000",  # Black for button text
        "button_hover": "#bbbb00",  # Darker yellow on hover
        "text_color": "#ffffff",  # White for text
        "entry_bg": "#ffffff",  # White background for entry
        "entry_fg": "#000000",  # Black foreground for entry
        "scroll_bg": "#ffff00",  # Bright yellow for scrollbar
        "scroll_fg": "#000000" # Black for scrollbar
    }
}

# Default Theme
current_theme = "Windows 11 Blue"

# --- Cache Directory ---
CACHE_DIR = "cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
CACHE_FILE = os.path.join(CACHE_DIR, "previous_file.json")
THEME_FILE = os.path.join(CACHE_DIR, "previous_theme.json")

# --- Loading Indicators ---
loading_bar = None
gemini_loading_label = None

# --- Loading Indicator Functions ---
def show_loading_bar(message):
    global loading_bar
    if loading_bar is None:
        loading_bar = ttk.Progressbar(root, mode='indeterminate')
        loading_bar.pack(pady=10)
        tk.Label(root, text=message).pack()
    loading_bar.start()
    root.update_idletasks() # Forces immediate redraw

def hide_loading_bar():
    global loading_bar
    if loading_bar:
        loading_bar.stop()
        loading_bar.destroy()
        loading_bar = None
        for widget in root.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("text") in ["Saving File...", "Opening File...", "Loading File..."]:
                widget.destroy()

def show_gemini_loading():
    global gemini_loading_label
    if gemini_loading_label is None:
        gemini_loading_label = tk.Label(root, text="Generating text...", font=("TkDefaultFont", 10))
        gemini_loading_label.pack(pady=5)
        root.update_idletasks()  # Forces the label to be shown immediately.

def hide_gemini_loading():
    global gemini_loading_label
    if gemini_loading_label:
        gemini_loading_label.destroy()
        gemini_loading_label = None

def translate_to_console_style(text):
    """Translates the text to console-style log with Gemini, using the new instructions."""
    show_gemini_loading()
    try:
        response = chat_session.send_message(text)
        cleaned_text = response.text.strip()
        return cleaned_text
    except Exception as e:
        messagebox.showerror("Error", f"Error with Gemini API: {e}")
        return "Error in translation."
    finally:
        hide_gemini_loading()

def save_log(log_text, file_path):
    try:
        with open(file_path, "a") as f:
            f.write(log_text + "\n")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error saving log: {e}")
        return False

def update_log():
    text = text_entry.get()
    if not text:
         messagebox.showerror("Error", "Please enter text to log.")
         return
    if not file_path:
        if messagebox.askyesno("Save File", "No file is currently opened. Do you want to save as a new file?"):
          save_as_file()
        else:
           return

    translated_text = translate_to_console_style(text)

    if translated_text == "Error in translation.":
        return

    log_text = f"{translated_text}"

    if save_log(log_text, file_path):
        log_display.insert(tk.END, log_text + '\n')
        text_entry.delete(0, tk.END)
        text_entry.focus_set()
    else:
        messagebox.showerror("Error", "Failed to update log file.")

def save_file():
    global file_path
    if file_path:
      show_loading_bar("Saving File...")
      try:
        with open(file_path, "w") as f:
           f.write(log_display.get("1.0", tk.END))
      except Exception as e:
         messagebox.showerror("Error", f"Error saving file: {e}")
      hide_loading_bar()
    else:
        save_as_file()

def save_as_file():
    global file_path
    show_loading_bar("Saving File...")
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        update_file_label()
        save_previous_file(file_path)
    hide_loading_bar()

def change_file():
    global file_path
    show_loading_bar("Opening File...")
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        update_file_label()
        save_previous_file(file_path)
        # Load file content into display
        log_display.delete("1.0", tk.END)
        try:
            with open(file_path, "r") as f:
                log_display.insert(tk.END, f.read())
        except Exception as e:
             messagebox.showerror("Error", f"Error loading file contents: {e}")
    hide_loading_bar()

def update_file_label():
    file_label.config(text=f"Current File: {file_path}")

def on_button_enter(event):
    event.widget.config(bg=themes[current_theme]["button_hover"])

def on_button_leave(event):
    event.widget.config(bg=themes[current_theme]["button_bg"])

def on_enter_key(event):
    update_log()

def clear_text_entry():
    text_entry.delete(0, tk.END)
    text_entry.focus_set()

# --- Persistent File Handling ---
def load_previous_file():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache_data = json.load(f)
                return cache_data.get("previous_file")
        except (json.JSONDecodeError, KeyError):
            return None
    return None

def save_previous_file(file_path):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump({"previous_file": file_path}, f)
    except Exception as e:
         messagebox.showerror("Error", f"Error saving file to cache: {e}")

def file_menu_save():
    save_file()

def file_menu_open():
    change_file()

def file_menu_view():
    if file_path:
        try:
            show_loading_bar("Loading File...")
            with open(file_path, "r") as f:
                content = f.read()
                view_window = tk.Toplevel(root)
                view_window.title(f"Viewing {os.path.basename(file_path)}")
                view_text = tk.Text(view_window, wrap=tk.WORD, bg=themes[current_theme]["bg_color"], fg=themes[current_theme]["text_color"], borderwidth=0)
                view_text.insert(tk.END, content)
                view_text.config(state=tk.DISABLED)
                view_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

                scrollbar = tk.Scrollbar(view_window, command=view_text.yview, bg=themes[current_theme]["scroll_bg"], activebackground=themes[current_theme]["scroll_fg"])
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                view_text.config(yscrollcommand=scrollbar.set)
            hide_loading_bar()
        except Exception as e:
            messagebox.showerror("Error", f"Error viewing file: {e}")
            hide_loading_bar()
    else:
        messagebox.showerror("Error", "No file opened to view.")

# --- Theme Handling ---
def load_previous_theme():
    if os.path.exists(THEME_FILE):
        try:
            with open(THEME_FILE, "r") as f:
                cache_data = json.load(f)
                return cache_data.get("previous_theme", "Windows 11 Blue")
        except (json.JSONDecodeError, KeyError):
             return "Windows 11 Blue"
    return "Windows 11 Blue"

def save_previous_theme(theme_name):
     try:
         with open(THEME_FILE, "w") as f:
            json.dump({"previous_theme": theme_name}, f)
     except Exception as e:
          messagebox.showerror("Error", f"Error saving theme to cache: {e}")

def apply_theme(theme_name):
    global current_theme
    current_theme = theme_name
    root.configure(bg=themes[current_theme]["bg_color"])
    input_frame.config(bg=themes[current_theme]["frame_bg"])
    file_frame.config(bg=themes[current_theme]["frame_bg"])
    file_label.config(bg=themes[current_theme]["frame_bg"], fg=themes[current_theme]["text_color"])
    log_frame.config(bg=themes[current_theme]["bg_color"])
    log_display.config(bg=themes[current_theme]["bg_color"], fg=themes[current_theme]["text_color"])
    scrollbar.config(bg=themes[current_theme]["scroll_bg"], activebackground=themes[current_theme]["scroll_fg"])
    text_entry.config(bg=themes[current_theme]["entry_bg"], fg=themes[current_theme]["entry_fg"], insertbackground=themes[current_theme]["entry_fg"])

    # Update button colors
    update_button.config(bg=themes[current_theme]["button_bg"], fg=themes[current_theme]["button_fg"])
    save_file_button.config(bg=themes[current_theme]["button_bg"], fg=themes[current_theme]["button_fg"])
    change_file_button.config(bg=themes[current_theme]["button_bg"], fg=themes[current_theme]["button_fg"])
    clear_button.config(bg=themes[current_theme]["button_bg"], fg=themes[current_theme]["button_fg"])

    # Manually call hover binding functions
    update_button.bind("<Enter>", on_button_enter)
    update_button.bind("<Leave>", on_button_leave)
    save_file_button.bind("<Enter>", on_button_enter)
    save_file_button.bind("<Leave>", on_button_leave)
    change_file_button.bind("<Enter>", on_button_enter)
    change_file_button.bind("<Leave>", on_button_leave)
    clear_button.bind("<Enter>", on_button_enter)
    clear_button.bind("<Leave>", on_button_leave)

    save_previous_theme(theme_name)

def create_theme_menu(menu_bar):
    theme_menu = tk.Menu(menu_bar, tearoff=0)
    for theme_name in themes:
        theme_menu.add_command(label=theme_name, command=lambda name=theme_name: apply_theme(name))
    menu_bar.add_cascade(label="Theme", menu=theme_menu)

# --- GUI Setup ---
root = tk.Tk()
root.title("Gemini Workload Logger")
root.geometry("600x400")
root.configure(borderwidth=0)

# Set Icon
try:
    icon_path = os.path.join(os.path.dirname(__file__), "geminiicon.png")
    icon = tk.PhotoImage(file=icon_path)
    root.iconphoto(False, icon)
except Exception as e:
    print(f"Error loading icon: {e}")

# Variable to store the file path
file_path = None

# --- File Menu ---
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Save", command=file_menu_save)
file_menu.add_command(label="Open", command=file_menu_open)
file_menu.add_command(label="View", command=file_menu_view)
menu_bar.add_cascade(label="File", menu=file_menu)
create_theme_menu(menu_bar)
root.config(menu=menu_bar)

# Load previous theme
current_theme = load_previous_theme()

# Input Frame
input_frame = tk.Frame(root, borderwidth=0)
input_frame.pack(pady=10, padx=10, fill=tk.X)

text_entry = tk.Entry(input_frame, width=40, borderwidth=0)
text_entry.pack(side=tk.LEFT, padx=5)
text_entry.bind("<Return>", on_enter_key)

update_button = tk.Button(input_frame, text="Update Log", borderwidth=0)
update_button.pack(side=tk.LEFT, padx=5)
update_button.bind("<Enter>", on_button_enter)
update_button.bind("<Leave>", on_button_leave)
update_button.config(command=update_log)

clear_button = tk.Button(input_frame, text="Clear", borderwidth=0)
clear_button.pack(side=tk.LEFT, padx=5)
clear_button.bind("<Enter>", on_button_enter)
clear_button.bind("<Leave>", on_button_leave)
clear_button.config(command=clear_text_entry)

# File Frame
file_frame = tk.Frame(root, borderwidth=0)
file_frame.pack(pady=10, padx=10, fill=tk.X)

file_label = tk.Label(file_frame, text="Current File: None", borderwidth=0)
file_label.pack(side=tk.LEFT, expand=True, fill=tk.X)

save_file_button = tk.Button(file_frame, text="Save as File", borderwidth=0)
save_file_button.pack(side=tk.LEFT, padx=5)
save_file_button.bind("<Enter>", on_button_enter)
save_file_button.bind("<Leave>", on_button_leave)
save_file_button.config(command=save_as_file)

change_file_button = tk.Button(file_frame, text="Change File", borderwidth=0)
change_file_button.pack(side=tk.LEFT, padx=5)
change_file_button.bind("<Enter>", on_button_enter)
change_file_button.bind("<Leave>", on_button_leave)
change_file_button.config(command=change_file)

# Log Display
log_frame = tk.Frame(root, borderwidth=0)
log_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

log_display = tk.Text(log_frame, height=15, wrap=tk.WORD, borderwidth=0)
log_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(log_frame, command=log_display.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_display.config(yscrollcommand=scrollbar.set)

# Load previous file if exists
previous_file = load_previous_file()
if previous_file and messagebox.askyesno("Load Previous", f"Load previously opened file '{os.path.basename(previous_file)}'?"):
    file_path = previous_file
    update_file_label()
    text_entry.focus_set()  # Set focus to text_entry after loading previous file
    root.after(100, lambda: text_entry.focus_set())
    # Load file content into display
    log_display.delete("1.0", tk.END)
    try:
        with open(file_path, "r") as f:
            log_display.insert(tk.END, f.read())
    except Exception as e:
        messagebox.showerror("Error", f"Error loading file contents: {e}")

apply_theme(current_theme)
text_entry.focus_set() # Set focus to text_entry on start
root.after(100, lambda: text_entry.focus_set())

root.mainloop()