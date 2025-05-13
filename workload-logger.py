import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import google.generativeai as genai
import os
import platform
import subprocess
from dotenv import load_dotenv
import json
import pickle
import sys

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
    "temperature": 1.0,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
}

# Simplified model initialization with error handling
try:
    # Use a model name that's widely available
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    
    chat_session = model.start_chat(
        history=[],
    )
    print("Gemini model initialized successfully")
    
    # Define function to translate user text to console style using Gemini
    def translate_to_console_style(text):
        try:
            response = chat_session.send_message(f"Convert this text to console log format: {text}")
            return response.text
        except Exception as e:
            print(f"Error in translation: {e}")
            return f"[Log] {text}"  # Fallback to simple format
    
except Exception as e:
    print(f"Warning: Could not initialize Gemini model: {e}")
    print("The application will continue without Gemini integration.")
    # Create a dummy translate function as a fallback
    def translate_to_console_style(text):
        return f"[Log] {text}"

# Global variables
file_path = None  # Initialize the file path variable

# --- Dark Mode Toggle Functions ---
def toggle_dark_mode():
    if is_dark_mode.get():
        # Animate transition to dark mode
        animate_theme_transition("Windows 11 Blue", "Dark", 200)
    else:
        # Animate transition to light mode
        animate_theme_transition("Dark", "Windows 11 Blue", 200)
    save_dark_mode_preference(is_dark_mode.get())

def hex_to_int(hex_color):
    """Convert hex color string to RGB integer values"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def int_to_hex(rgb):
    """Convert RGB integer values to hex color string"""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def interpolate_color(start_color, end_color, ratio):
    """Interpolate between two colors based on ratio (0-1)"""
    start_rgb = hex_to_int(start_color)
    end_rgb = hex_to_int(end_color)
    
    interpolated_rgb = tuple(
        int(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * ratio)
        for i in range(3)
    )
    
    return int_to_hex(interpolated_rgb)

def animate_theme_transition(start_theme, end_theme, duration=200, steps=10):
    """Animate the transition between two themes over the specified duration"""
    # Ensure UI widgets are initialized
    if 'root' not in globals() or not root.winfo_exists():
        # If UI isn't ready, just apply the theme directly
        apply_theme(end_theme)
        return
        
    # Calculate time per step
    step_duration = duration // steps
    
    # Store all the widgets we'll update (safely check if they exist)
    widgets = {}
    
    # Only add widgets that exist and are accessible
    if 'root' in globals() and root.winfo_exists():
        widgets["root"] = (root, "bg", "bg_color")
        
    for widget_name, widget_var in [
        ("input_frame", "input_frame"), 
        ("file_frame", "file_frame"),
        ("file_label", "file_label"),
        ("log_frame", "log_frame"),
        ("log_display", "log_display"),
        ("text_entry", "text_entry"),
        ("update_button", "update_button"),
        ("save_file_button", "save_file_button"),
        ("change_file_button", "change_file_button"),
        ("clear_button", "clear_button")
    ]:
        if widget_var in globals() and globals()[widget_var].winfo_exists():
            widget = globals()[widget_var]
            if widget_name == "file_label":
                widgets[f"{widget_name}_bg"] = (widget, "bg", "frame_bg")
                widgets[f"{widget_name}_fg"] = (widget, "fg", "text_color")
            elif widget_name in ["log_display", "text_entry"]:
                widgets[f"{widget_name}_bg"] = (widget, "bg", f"{widget_name.split('_')[0]}_bg")
                widgets[f"{widget_name}_fg"] = (widget, "fg", f"{widget_name.split('_')[0]}_fg")
            elif widget_name.endswith("_button"):
                widgets[f"{widget_name}_bg"] = (widget, "bg", "button_bg")
                widgets[f"{widget_name}_fg"] = (widget, "fg", "button_fg")
            else:
                widgets[widget_name] = (widget, "bg", "bg_color" if "frame" not in widget_name else "frame_bg")
    
    # If no widgets found, just apply theme directly
    if not widgets:
        apply_theme(end_theme)
        return
    
    # Function for each animation step
    def run_animation_step(current_step):
        if current_step > steps:
            # Animation complete, update to final theme
            apply_theme(end_theme)
            return
            
        # Calculate current ratio (0 to 1)
        ratio = current_step / steps
        
        # Update each widget with interpolated colors
        for widget_name, (widget, property_name, theme_key) in widgets.items():
            # Skip if widget was destroyed during animation
            if not widget.winfo_exists():
                continue
                
            start_color = themes[start_theme][theme_key]
            end_color = themes[end_theme][theme_key]
            
            # Only animate colors that start with # (hex colors)
            if start_color.startswith('#') and end_color.startswith('#'):
                try:
                    interpolated_color = interpolate_color(start_color, end_color, ratio)
                    widget.config(**{property_name: interpolated_color})
                except Exception as e:
                    print(f"Error updating {widget_name}: {e}")
        
        # Schedule next step
        root.after(step_duration, run_animation_step, current_step + 1)
    
    # Start animation from step 1
    run_animation_step(1)

def save_dark_mode_preference(is_dark):
    """Save dark mode preference to a pickle file"""
    try:
        with open(DARK_MODE_FILE, 'wb') as f:
            pickle.dump(is_dark, f)
    except Exception as e:
        print(f"Error saving dark mode preference: {e}")

def load_dark_mode_preference():
    """Load dark mode preference from pickle file"""
    try:
        if os.path.exists(DARK_MODE_FILE):
            with open(DARK_MODE_FILE, 'rb') as f:
                return pickle.load(f)
    except Exception as e:
        print(f"Error loading dark mode preference: {e}")
    return False  # Default to light mode

def detect_system_dark_mode():
    """Detect if the system is using dark mode"""
    system = platform.system()
    
    if system == "Windows":
        try:
            # Windows 10 & 11
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0  # 0 means dark mode is enabled
        except Exception as e:
            print(f"Error detecting Windows dark mode: {e}")
            return False
            
    elif system == "Darwin":  # macOS
        try:
            # Use applescript to check dark mode
            cmd = 'defaults read -g AppleInterfaceStyle'
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
            return result.stdout.strip() == 'Dark'
        except Exception as e:
            print(f"Error detecting macOS dark mode: {e}")
            return False
            
    elif system == "Linux":
        try:
            # Try to detect for GNOME desktop environment
            cmd = 'gsettings get org.gnome.desktop.interface color-scheme'
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
            return 'dark' in result.stdout.lower()
        except Exception as e:
            print(f"Error detecting Linux dark mode: {e}")
            return False
            
    return False  # Default to light mode if we can't detect

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
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create cache directory: {e}")
        # Use a temp directory as fallback
        CACHE_DIR = os.path.join(os.path.expanduser("~"), ".gemini-workload-logger")
        os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, "previous_file.json")
THEME_FILE = os.path.join(CACHE_DIR, "previous_theme.json")
DARK_MODE_FILE = os.path.join(CACHE_DIR, "dark_mode_preference.pkl")

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

def save_log(log_text, file_path):
    try:
        with open(file_path, "a") as f:
            f.write(log_text + "\n")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error saving log: {e}")
        return False

def update_log():
    """Add text from the entry field to the log display and save to file"""
    text = text_entry.get()
    if not text:
         messagebox.showerror("Error", "Please enter text to log.")
         return
    if not file_path:
        if messagebox.askyesno("Save File", "No file is currently opened. Do you want to save as a new file?"):
          save_as_file()
          if not file_path:  # If user canceled save dialog
              return
        else:
           return

    # Show loading indicator
    show_gemini_loading()
    translated_text = translate_to_console_style(text)
    hide_gemini_loading()

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
      update_status(f"Saving file {os.path.basename(file_path)}...")
      show_loading_bar("Saving File...")
      try:
        with open(file_path, "w") as f:
           f.write(log_display.get("1.0", tk.END))
        update_status(f"File saved: {os.path.basename(file_path)}")
      except Exception as e:
         messagebox.showerror("Error", f"Error saving file: {e}")
         update_status("Error saving file")
      hide_loading_bar()
    else:
        save_as_file()

def save_as_file():
    global file_path
    update_status("Saving file as...")
    show_loading_bar("Saving File...")
    file_path_selected = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path_selected:  # Check if user didn't cancel
        file_path = file_path_selected
        update_file_label()
        save_previous_file(file_path)
        # Save current content
        try:
            with open(file_path, "w") as f:
               f.write(log_display.get("1.0", tk.END))
            update_status(f"File saved: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving file: {e}")
            update_status("Error saving file")
    else:
        update_status("Save canceled")
    hide_loading_bar()

def change_file():
    global file_path
    update_status("Opening file...")
    show_loading_bar("Opening File...")
    file_path_selected = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path_selected:
        file_path = file_path_selected
        update_file_label()
        save_previous_file(file_path)
        # Load file content into display
        log_display.delete("1.0", tk.END)
        try:
            with open(file_path, "r") as f:
                log_display.insert(tk.END, f.read())
            update_status(f"File opened: {os.path.basename(file_path)}")
        except Exception as e:
             messagebox.showerror("Error", f"Error loading file contents: {e}")
             update_status("Error opening file")
    else:
        update_status("Open canceled")
    hide_loading_bar()

def update_file_label():
    """Update the file label and status bar with current file path"""
    file_label.config(text=f"Current File: {file_path}")
    update_file_status()  # Update the status bar too

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

def apply_theme(theme_name, animate=False, previous_theme=None):
    """Apply the selected theme to all UI elements with optional animation"""
    global current_theme
    
    # If animation is requested and we know the previous theme
    if animate and previous_theme and previous_theme != theme_name:
        animate_theme_transition(previous_theme, theme_name)
        return
    
    previous_theme = current_theme
    current_theme = theme_name
    
    # Update each UI element with the new theme colors
    update_ui_colors(theme_name)
    
    # Save the theme preference
    save_previous_theme(theme_name)

def update_ui_colors(theme_name):
    """Update all UI elements with colors from the specified theme"""
    # Main window
    root.configure(bg=themes[theme_name]["bg_color"])
    
    # Frames
    input_frame.config(bg=themes[theme_name]["frame_bg"])
    file_frame.config(bg=themes[theme_name]["frame_bg"])
    dark_mode_frame.config(bg=themes[theme_name]["frame_bg"])
    log_frame.config(bg=themes[theme_name]["bg_color"])
    
    # Labels and text
    file_label.config(bg=themes[theme_name]["frame_bg"], fg=themes[theme_name]["text_color"])
    log_display.config(bg=themes[theme_name]["bg_color"], fg=themes[theme_name]["text_color"])
    dark_mode_toggle.config(bg=themes[theme_name]["frame_bg"], fg=themes[theme_name]["text_color"],
                          activebackground=themes[theme_name]["frame_bg"], 
                          activeforeground=themes[theme_name]["text_color"],
                          selectcolor=themes[theme_name].get("accent", themes[theme_name]["button_hover"]))
    
    # Input elements
    text_entry.config(bg=themes[theme_name]["entry_bg"], fg=themes[theme_name]["entry_fg"], 
                     insertbackground=themes[theme_name]["entry_fg"])
    scrollbar.config(bg=themes[theme_name]["scroll_bg"], activebackground=themes[theme_name]["scroll_fg"])
    
    # Buttons
    buttons = [update_button, save_file_button, change_file_button, clear_button]
    for button in buttons:
        button.config(bg=themes[theme_name]["button_bg"], fg=themes[theme_name]["button_fg"])
        button.bind("<Enter>", on_button_enter)
        button.bind("<Leave>", on_button_leave)

def create_theme_menu(menu_bar):
    theme_menu = tk.Menu(menu_bar, tearoff=0)
    for theme_name in themes:
        theme_menu.add_command(label=theme_name, command=lambda name=theme_name: apply_theme(name))
    menu_bar.add_cascade(label="Theme", menu=theme_menu)

# --- Color Checker Utility ---
def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def calculate_luminance(rgb):
    """Calculate relative luminance of an RGB color"""
    # Convert RGB values to sRGB
    r, g, b = [x/255 for x in rgb]
    
    # Adjust values
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    
    # Calculate luminance
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def calculate_contrast_ratio(color1, color2):
    """Calculate contrast ratio between two colors"""
    lum1 = calculate_luminance(hex_to_rgb(color1))
    lum2 = calculate_luminance(hex_to_rgb(color2))
    
    # Ensure the lighter color is first
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    
    # Calculate contrast ratio
    return (lighter + 0.05) / (darker + 0.05)

def verify_contrast_wcag_aa(color1, color2):
    """Verify if two colors meet WCAG AA contrast ratio of 4.5:1"""
    ratio = calculate_contrast_ratio(color1, color2)
    return ratio >= 4.5, ratio

def check_theme_contrast(theme_colors):
    """Verify contrast ratios for a theme palette"""
    results = []
    
    # Check text on backgrounds
    text_bg_pairs = [
        ("text_color", "bg_color", "Text on background"),
        ("text_color", "frame_bg", "Text on frame"),
        ("button_fg", "button_bg", "Button text on button"),
        ("entry_fg", "entry_bg", "Entry text on entry background")
    ]
    
    for fg_key, bg_key, description in text_bg_pairs:
        passes, ratio = verify_contrast_wcag_aa(
            theme_colors[fg_key], 
            theme_colors[bg_key]
        )
        results.append({
            "description": description,
            "passes": passes,
            "ratio": ratio,
            "fg_color": theme_colors[fg_key],
            "bg_color": theme_colors[bg_key]
        })
    
    return results

# Verify the dark theme meets contrast requirements
dark_theme_contrast = check_theme_contrast(themes["Dark"])
for result in dark_theme_contrast:
    if not result["passes"]:
        print(f"Warning: {result['description']} fails WCAG AA contrast with ratio {result['ratio']:.2f}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Gemini Workload Logger")
root.geometry("600x400")
root.configure(borderwidth=0)

# Define a close handler
def on_close():
    """Handle window close event properly"""
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

# Set the close handler
root.protocol("WM_DELETE_WINDOW", on_close)

# Create menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=file_menu_open)
file_menu.add_command(label="Save", command=file_menu_save)
file_menu.add_command(label="View", command=file_menu_view)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=on_close)
menu_bar.add_cascade(label="File", menu=file_menu)

# Edit menu
edit_menu = tk.Menu(menu_bar, tearoff=0)

def copy_selected_text():
    if log_display.tag_ranges(tk.SEL):
        selected_text = log_display.get(tk.SEL_FIRST, tk.SEL_LAST)
        root.clipboard_clear()
        root.clipboard_append(selected_text)

def paste_to_entry():
    try:
        text = root.clipboard_get()
        text_entry.insert(tk.INSERT, text)
    except Exception as e:
        print(f"Error pasting text: {e}")

edit_menu.add_command(label="Copy", command=copy_selected_text)
edit_menu.add_command(label="Paste", command=paste_to_entry)
menu_bar.add_cascade(label="Edit", menu=edit_menu)

# Version info
APP_VERSION = "1.0.0"

# Add theme menu
create_theme_menu(menu_bar)

# Help menu
help_menu = tk.Menu(menu_bar, tearoff=0)

def show_about_dialog():
    about_window = tk.Toplevel(root)
    about_window.title("About Gemini Workload Logger")
    about_window.geometry("400x300")
    about_window.resizable(False, False)
    about_window.transient(root)
    about_window.grab_set()
    
    # Icon
    try:
        about_window.iconphoto(False, root.iconphoto_get())
    except:
        pass
        
    # Content frame
    content_frame = tk.Frame(about_window, padx=20, pady=20)
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # App title
    title_label = tk.Label(content_frame, text="Gemini Workload Logger", font=("TkDefaultFont", 16, "bold"))
    title_label.pack(pady=(0, 10))
    
    # Version
    version_label = tk.Label(content_frame, text=f"Version {APP_VERSION}")
    version_label.pack(pady=(0, 20))
    
    # Description
    desc_label = tk.Label(content_frame, text="A simple logging tool that uses Gemini to\nconvert text to console-style log entries.", 
                      justify=tk.CENTER)
    desc_label.pack(pady=(0, 20))
    
    # Copyright
    copyright_label = tk.Label(content_frame, text="© 2023")
    copyright_label.pack(pady=(0, 20))
    
    # Close button
    close_button = tk.Button(content_frame, text="Close", command=about_window.destroy)
    close_button.pack(pady=10)

def show_help():
    help_window = tk.Toplevel(root)
    help_window.title("Help - Gemini Workload Logger")
    help_window.geometry("500x400")
    help_window.transient(root)
    help_window.grab_set()
    
    # Content frame
    content_frame = tk.Frame(help_window, padx=20, pady=20)
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # Help text
    help_text = tk.Text(content_frame, wrap=tk.WORD, borderwidth=0)
    help_text.pack(fill=tk.BOTH, expand=True)
    
    help_content = """
Gemini Workload Logger - Help

Basic Usage:
------------
1. Type text in the input field and press Enter or click 'Update Log'
2. The text will be converted to a console-style format using Gemini AI
3. The formatted text will be saved to the current log file

File Operations:
---------------
- Open: Open an existing log file
- Save: Save the current log
- Save As: Save the log to a new file
- Exit: Close the application

Keyboard Shortcuts:
-----------------
- Ctrl+O: Open file
- Ctrl+S: Save file
- Ctrl+C: Copy selected text
- Ctrl+V: Paste text
- Ctrl+L: Clear input field
- Ctrl+Q: Quit application

Themes:
------
Select a theme from the Theme menu to change the application appearance.
Toggle Dark Mode using the checkbox in the top-right corner.
"""
    
    help_text.insert(tk.END, help_content)
    help_text.config(state=tk.DISABLED)
    
    # Scrollbar
    scrollbar = tk.Scrollbar(help_text)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    help_text.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=help_text.yview)
    
    # Close button
    close_button = tk.Button(content_frame, text="Close", command=help_window.destroy)
    close_button.pack(pady=10)

help_menu.add_command(label="Help Topics", command=show_help)
help_menu.add_separator()
help_menu.add_command(label="About", command=show_about_dialog)
menu_bar.add_cascade(label="Help", menu=help_menu)

# Dark Mode State Variable (moved here after root is created)
is_dark_mode = tk.BooleanVar()

# Set Icon
try:
    icon_path = os.path.join(os.path.dirname(__file__), "geminiicon.png")
    if os.path.exists(icon_path):
        icon = tk.PhotoImage(file=icon_path)
        root.iconphoto(False, icon)
    else:
        # Create a simple fallback icon
        fallback_icon = tk.PhotoImage(width=64, height=64)
        for y in range(64):
            for x in range(64):
                # Create a simple gradient icon
                r = int(255 * (x / 64))
                g = int(255 * (y / 64))
                b = 150
                color = f'#{r:02x}{g:02x}{b:02x}'
                fallback_icon.put(color, (x, y))
        root.iconphoto(False, fallback_icon)
except Exception as e:
    print(f"Error loading icon: {e}")

# Load previous theme
current_theme = load_previous_theme()

# Dark Mode Toggle Frame (positioned at the top right)
dark_mode_frame = tk.Frame(root, borderwidth=0)
dark_mode_frame.pack(anchor=tk.NE, padx=10, pady=10)

# Set dark mode based on saved preference or system setting
system_dark_mode = detect_system_dark_mode()
saved_preference = load_dark_mode_preference()
# First check saved preference, if none exists, use system setting
is_dark_mode.set(saved_preference if saved_preference is not None else system_dark_mode)

# Dark Mode Toggle with updated event handling
dark_mode_toggle = tk.Checkbutton(
    dark_mode_frame, 
    text="Dark Mode", 
    variable=is_dark_mode,
    command=toggle_dark_mode,
    borderwidth=0
)
dark_mode_toggle.pack(side=tk.RIGHT)

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

# Status bar
status_bar = tk.Frame(root, borderwidth=1, relief=tk.SUNKEN)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

status_label = tk.Label(status_bar, text="Ready", anchor=tk.W, padx=5, pady=2)
status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

file_status_label = tk.Label(status_bar, text="No file", anchor=tk.E, padx=5, pady=2)
file_status_label.pack(side=tk.RIGHT)

def update_status(message):
    """Update status bar message"""
    status_label.config(text=message)
    root.update_idletasks()

def update_file_status():
    """Update file status in status bar"""
    if file_path:
        file_status_label.config(text=f"File: {os.path.basename(file_path)}")
    else:
        file_status_label.config(text="No file")

# Apply the correct theme based on initial dark mode setting
if is_dark_mode.get():
    apply_theme("Dark")
else:
    apply_theme("Windows 11 Blue")

# Load previous file if exists
previous_file = load_previous_file()
if previous_file and messagebox.askyesno("Load Previous", f"Load previously opened file '{os.path.basename(previous_file)}'?"):
    file_path = previous_file
    update_file_label()
    # Load file content into display
    log_display.delete("1.0", tk.END)
    try:
        with open(file_path, "r") as f:
            log_display.insert(tk.END, f.read())
    except Exception as e:
        messagebox.showerror("Error", f"Error loading file contents: {e}")

# Set focus to text_entry (only once)
text_entry.focus_set()

def test_dark_mode_toggle():
    """Test function to verify dark mode toggle works across platforms"""
    # Create a test window
    test_window = tk.Toplevel(root)
    test_window.title("Dark Mode Toggle Test")
    test_window.geometry("500x500")
    
    # Get system information
    system_info = f"OS: {platform.system()} {platform.version()}\n"
    system_info += f"Python: {sys.version}\n"
    system_info += f"Tkinter: {tk.TkVersion}\n"
    
    # Create info frame
    info_frame = tk.Frame(test_window)
    info_frame.pack(fill=tk.X, padx=10, pady=10)
    
    info_label = tk.Label(info_frame, text=system_info, justify=tk.LEFT)
    info_label.pack(anchor=tk.W)
    
    # Create test controls
    control_frame = tk.Frame(test_window)
    control_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Toggle states
    toggle_var = tk.BooleanVar()
    
    def update_sample_ui():
        theme = "Dark" if toggle_var.get() else "Windows 11 Blue"
        # Update test UI with theme colors
        sample_frame.config(bg=themes[theme]["bg_color"])
        sample_label.config(bg=themes[theme]["frame_bg"], fg=themes[theme]["text_color"])
        sample_button.config(bg=themes[theme]["button_bg"], fg=themes[theme]["button_fg"])
        sample_entry.config(bg=themes[theme]["entry_bg"], fg=themes[theme]["entry_fg"])
        sample_check.config(bg=themes[theme]["bg_color"], fg=themes[theme]["text_color"],
                         selectcolor=themes[theme].get("accent", themes[theme]["button_hover"]))
        results_text.config(bg=themes[theme]["bg_color"], fg=themes[theme]["text_color"])
    
    toggle = tk.Checkbutton(control_frame, text="Dark Mode", variable=toggle_var, 
                         command=update_sample_ui)
    toggle.pack(side=tk.LEFT, padx=5)
    
    # Create sample UI elements to test
    sample_frame = tk.Frame(test_window, bg=themes["Windows 11 Blue"]["bg_color"], padx=10, pady=10)
    sample_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    sample_label = tk.Label(sample_frame, text="Sample Text", 
                         bg=themes["Windows 11 Blue"]["frame_bg"], 
                         fg=themes["Windows 11 Blue"]["text_color"])
    sample_label.pack(anchor=tk.W, pady=5)
    
    sample_entry = tk.Entry(sample_frame, 
                         bg=themes["Windows 11 Blue"]["entry_bg"], 
                         fg=themes["Windows 11 Blue"]["entry_fg"])
    sample_entry.insert(0, "Sample Entry Text")
    sample_entry.pack(fill=tk.X, pady=5)
    
    sample_button = tk.Button(sample_frame, text="Sample Button", 
                           bg=themes["Windows 11 Blue"]["button_bg"], 
                           fg=themes["Windows 11 Blue"]["button_fg"])
    sample_button.pack(pady=5)
    
    sample_check = tk.Checkbutton(sample_frame, text="Sample Checkbox", 
                               bg=themes["Windows 11 Blue"]["bg_color"], 
                               fg=themes["Windows 11 Blue"]["text_color"])
    sample_check.pack(anchor=tk.W, pady=5)
    
    # Results area
    results_text = tk.Text(sample_frame, height=10, width=50, 
                        bg=themes["Windows 11 Blue"]["bg_color"], 
                        fg=themes["Windows 11 Blue"]["text_color"])
    results_text.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # Check contrast ratios
    def check_contrast():
        theme = "Dark" if toggle_var.get() else "Windows 11 Blue"
        results = check_theme_contrast(themes[theme])
        
        results_text.delete(1.0, tk.END)
        results_text.insert(tk.END, f"Contrast Ratio Results for {theme} theme:\n\n")
        
        for result in results:
            status = "✓ PASS" if result["passes"] else "✗ FAIL"
            results_text.insert(tk.END, f"{status} {result['description']}: {result['ratio']:.2f}:1\n")
            results_text.insert(tk.END, f"  FG: {result['fg_color']} on BG: {result['bg_color']}\n\n")
    
    check_button = tk.Button(control_frame, text="Check Contrast Ratios", command=check_contrast)
    check_button.pack(side=tk.LEFT, padx=5)
    
    # System detection
    def test_system_detection():
        is_dark = detect_system_dark_mode()
        messagebox.showinfo("System Theme Detection", 
                         f"System Dark Mode Detected: {is_dark}\n"
                         f"This reflects your current system setting.")
    
    system_button = tk.Button(control_frame, text="Test System Detection", command=test_system_detection)
    system_button.pack(side=tk.LEFT, padx=5)

# Bind keyboard shortcuts
def setup_keyboard_shortcuts():
    """Setup keyboard shortcuts for common actions"""
    # File operations
    root.bind("<Control-o>", lambda event: file_menu_open())
    root.bind("<Control-s>", lambda event: file_menu_save())
    root.bind("<Control-q>", lambda event: on_close())
    
    # Edit operations
    root.bind("<Control-c>", lambda event: copy_selected_text())
    root.bind("<Control-v>", lambda event: paste_to_entry())
    
    # Clear
    root.bind("<Control-l>", lambda event: clear_text_entry())

if __name__ == "__main__":
    # Disable test mode for now
    # root.after(1000, test_dark_mode_toggle)
    setup_keyboard_shortcuts()
    root.mainloop()