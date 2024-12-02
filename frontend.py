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
GAME_WIDTH = 600  # Width of each game window
GAME_HEIGHT = 300  # Height of each game window
COLUMNS = 3  # Number of columns in the layout
MARGIN = 50  # Margin between windows

# Game configurations
games = [
    # Tìm kiếm thông tin
    {
        "name": "Snake Game with Best First Search",
        "description": "Snake game using best first search algorithm to find path to food",
        "path": "TimKiemThongTin/BestFirstSearch.py",
        "icon": "icons/snake.png"
    },
    {
        "name": "Snake Game with A* Search",
        "description": "Snake game using A* search algorithm to find path to food",
        "path": "TimKiemThongTin/A_search.py",
        "icon": "icons/snake.png"
    },
    
    # Tìm kiếm mù
    {
        "name": "Snake Game with Uniform Cost Search",
        "description": "Snake game using uniform cost search algorithm",
        "path": "TimKiemMu/UniformCostSearch.py",
        "icon": "icons/snake.png"
    },
    {
        "name": "Snake Game with Depth First Search",
        "description": "Snake game using depth first search algorithm",
        "path": "TimKiemMu/DepthFirstSearch.py",
        "icon": "icons/snake.png"
    },
    {
        "name": "Snake Game with Depth Limited Search",
        "description": "Snake game using depth limited search algorithm",
        "path": "TimKiemMu/DepthLimitedSearch.py",
        "icon": "icons/snake.png"
    },
    {
        "name": "Snake Game with Iterative Deepening DFS",
        "description": "Snake game using iterative deepening depth first search",
        "path": "TimKiemMu/IterativeDeepeningDFS.py",
        "icon": "icons/snake.png"
    },

    # Local Search
    {
        "name": "Snake Game with Hill Climbing",
        "description": "Snake game using hill climbing search algorithm",
        "path": "LocalSearch/Hill-Climbing.py",
        "icon": "icons/snake.png"
    },
    {
        "name": "Snake Game with Simulated Annealing",
        "description": "Snake game using simulated annealing algorithm", 
        "path": "LocalSearch/SimulatedAnnealing.py",
        "icon": "icons/snake.png"
    },
    {
        "name": "Snake Game with Beam Search",
        "description": "Snake game using beam search algorithm",
        "path": "LocalSearch/BeamSearch.py",
        "icon": "icons/snake.png"
    },
    {
        "name": "Snake Game with Genetic Algorithm",
        "description": "Snake game using genetic algorithm",
        "path": "LocalSearch/GeneticAlgorithms.py",
        "icon": "icons/snake.png"
    },
    {
        "name": "Snake Game with Gradient Descent",
        "description": "Snake game using gradient descent algorithm",
        "path": "LocalSearch/GradientDescent.py",
        "icon": "icons/snake.png"
    },

    # Tìm kiếm đối kháng
    {
        "name": "Snake Game with Minimax",
        "description": "Snake game using minimax algorithm",
        "path": "TimKiemDoiKhang/Minimax.py",
        "icon": "icons/snake.png"
    },
    {
        "name": "Snake Game with Alpha-Beta Pruning",
        "description": "Snake game using alpha-beta pruning algorithm",
        "path": "TimKiemDoiKhang/AlphaBetaPruning.py",
        "icon": "icons/snake.png"
    },

    # Tìm kiếm thỏa mãn điều kiện
    {
        "name": "Snake Game with Backtracking",
        "description": "Snake game using backtracking search algorithm",
        "path": "TimKiemThoaManDieuKien/Backtracking.py",
        "icon": "icons/snake.png"
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
        
        # Add "Launch All" button
        self.create_launch_all_button()
        
        # Create game cards
        self.create_game_cards()
        
        # Add status bar
        self.status_bar = ttk.Label(self.root, text="Ready to launch games", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_launch_all_button(self):
        launch_all_btn = ttk.Button(
            self.main_frame,
            text="Launch All Games",
            style='Launch.TButton',
            command=self.launch_all_games
        )
        launch_all_btn.grid(row=0, column=0, columnspan=COLUMNS, pady=15, sticky="ew")
    
    def create_game_cards(self):
        for i, game in enumerate(games):
            # Calculate grid position
            row = (i // COLUMNS) + 1  # Adjust row to account for "Launch All" button
            col = i % COLUMNS
            
            # Create card frame with hover effect
            card = ttk.Frame(self.main_frame, style='Card.TFrame')
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            
            # Create game frame for embedding
            game_frame = ttk.Frame(card, width=GAME_WIDTH, height=GAME_HEIGHT)
            game_frame.pack_propagate(False)  # Prevent frame from shrinking
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
            # Update status bar
            self.status_bar.configure(text=f"Launching {game['name']}...")
            
            # Launch game process
            process = subprocess.Popen(['python', game["path"]])
            self.processes.append(process)
            
            # Update status after successful launch
            self.status_bar.configure(text=f"{game['name']} launched successfully")
            
        except Exception as e:
            self.status_bar.configure(text=f"Error launching {game['name']}")
            messagebox.showerror("Error", f"Failed to launch {game['name']}: {str(e)}")
    
    def launch_all_games(self):
        """Launch all games simultaneously."""
        try:
            for game in games:
                # Launch game process
                process = subprocess.Popen(['python', game["path"]])
                self.processes.append(process)
            
            # Update status after successful launch
            self.status_bar.configure(text="All games launched successfully")
            messagebox.showinfo("Success", "All games launched successfully!")
        except Exception as e:
            self.status_bar.configure(text="Error launching all games")
            messagebox.showerror("Error", f"Failed to launch all games: {str(e)}")
    
    def run(self):
        self.root.mainloop()

# Create game launcher instance
launcher = GameLauncher()
launcher.run()
