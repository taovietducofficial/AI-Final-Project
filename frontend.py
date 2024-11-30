import pygame
import subprocess
import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, font
from PIL import Image, ImageTk

# Initialize Pygame
pygame.init()

# Constants for window layout
WINDOW_WIDTH = 1920  # Total width
WINDOW_HEIGHT = 1080  # Total height
GAME_WIDTH = 500  # Width of each game window
GAME_HEIGHT = 500  # Height of each game window
COLUMNS = 3  # Number of columns in the layout
MARGIN = 50  # Margin between windows

# Game configurations
games = [
    {
        "path": "BlindSearch/AIproject1.py",
        "name": "Blind Search Snake",
        "description": "Snake game using blind search algorithms",
        "icon": "icons/blind_search.png"
    },
    {
        "path": "Search_Algorithms_Terminology/Binary_Search.py", 
        "name": "Binary Search Snake",
        "description": "Snake game demonstrating binary search",
        "icon": "icons/binary_search.png"
    },
    {
        "path": "LocalSearch/AIproject3.py",
        "name": "Local Search Snake", 
        "description": "Snake game with local search optimization",
        "icon": "icons/local_search.png"
    },
    {
        "path": "LookingResistance/AIproject4.py",
        "name": "Looking Resistance Snake",
        "description": "Snake game with resistance mechanics",
        "icon": "icons/resistance.png"
    },
    {
        "path": "SeekingComfort/AIproject5.py",
        "name": "Seeking Comfort Snake",
        "description": "Snake game with comfort-seeking behavior",
        "icon": "icons/comfort.png"
    }
]

ROWS = -(-len(games) // COLUMNS)  # Ceiling division for rows

class GameLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Snake Games Collection")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # Set theme and styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Card.TFrame', background='#ffffff', relief='raised')
        self.style.configure('GameTitle.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        self.style.configure('GameDesc.TLabel', font=('Arial', 12), foreground='#34495e')
        self.style.configure('Launch.TButton', font=('Arial', 12, 'bold'), padding=10)
        
        # Initialize game frames dictionary
        self.game_frames = {}
        self.processes = []
        
        # Create main frame with gradient background
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create game cards
        self.create_game_cards()
        
        # Add status bar
        self.status_bar = ttk.Label(self.root, text="Ready to launch games", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_game_cards(self):
        for i, game in enumerate(games):
            # Calculate grid position
            row = i // COLUMNS
            col = i % COLUMNS
            
            # Create card frame with hover effect
            card = ttk.Frame(self.main_frame, style='Card.TFrame')
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            
            # Create game frame for embedding
            game_frame = ttk.Frame(card)
            game_frame.pack(expand=True, fill='both')
            self.game_frames[game["name"]] = game_frame
            
            # Try to load and display game icon
            try:
                icon = Image.open(game["icon"])
                icon = icon.resize((64, 64), Image.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon)
                icon_label = ttk.Label(card, image=icon_photo)
                icon_label.image = icon_photo  # Keep reference
                icon_label.pack(pady=10)
            except:
                pass  # Skip icon if file not found
            
            # Add game info with improved styling
            ttk.Label(card, text=game["name"], style='GameTitle.TLabel').pack(pady=5)
            ttk.Label(card, text=game["description"], style='GameDesc.TLabel', wraplength=300).pack(pady=5)
            
            # Launch button with hover effect
            launch_btn = ttk.Button(
                card,
                text="Launch Game",
                style='Launch.TButton',
                command=lambda g=game: self.launch_game(g)
            )
            launch_btn.pack(pady=15)
            
            # Add hover effects
            self.add_hover_effects(card, launch_btn, game)
            
        # Configure grid weights for responsive layout
        for i in range(COLUMNS):
            self.main_frame.columnconfigure(i, weight=1)
        for i in range(ROWS):
            self.main_frame.rowconfigure(i, weight=1)
            
    def add_hover_effects(self, card, button, game):
        def on_enter(e):
            card.configure(relief='ridge')
            self.status_bar.configure(text=f"Ready to launch {game['name']}")
            
        def on_leave(e):
            card.configure(relief='raised')
            self.status_bar.configure(text="Ready to launch games")
            
        card.bind('<Enter>', on_enter)
        card.bind('<Leave>', on_leave)
            
    def launch_game(self, game):
        try:
            # Get game frame
            game_frame = self.game_frames[game["name"]]
            
            # Update status bar
            self.status_bar.configure(text=f"Launching {game['name']}...")
            
            # Launch game process with window ID
            env = os.environ.copy()
            env['SDL_WINDOWID'] = str(game_frame.winfo_id())
            
            # Launch game process
            process = subprocess.Popen(['python', game["path"]], env=env)
            self.processes.append(process)
            
            # Update status after successful launch
            self.status_bar.configure(text=f"{game['name']} launched successfully")
            
        except Exception as e:
            self.status_bar.configure(text=f"Error launching {game['name']}")
            messagebox.showerror("Error", f"Failed to launch {game['name']}: {str(e)}")
            
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle window closing
        self.root.mainloop()
        
    def cleanup(self):
        for process in self.processes:
            try:
                process.terminate()
            except:
                pass
                
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit? All running games will be closed."):
            self.cleanup()
            self.root.destroy()
            sys.exit()

if __name__ == "__main__":
    launcher = GameLauncher()
    try:
        launcher.run()
    finally:
        launcher.cleanup()
        sys.exit()
