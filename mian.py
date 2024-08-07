import json
import tkinter as tk
from tkinter import messagebox, filedialog
import sys

# Constants
RED_POINTS = 2
BLUE_POINTS = 3

# Game class encapsulating the game state and logic
class NimGame:
    def __init__(self, num_red, num_blue, version, first_player, depth):
        self.num_red = num_red
        self.num_blue = num_blue
        self.version = version
        self.current_player = first_player
        self.depth = depth

    @classmethod
    def from_dict(cls, data):
        return cls(data['num_red'], data['num_blue'], data['version'], data['current_player'], data['depth'])

    def to_dict(self):
        return {
            'num_red': self.num_red,
            'num_blue': self.num_blue,
            'version': self.version,
            'current_player': self.current_player,
            'depth': self.depth
        }

    def save_state(self, filename):
        try:
            with open(filename, 'w') as f:
                json.dump(self.to_dict(), f)
            messagebox.showinfo("Save Game", f"Game state saved to {filename}")
        except IOError as e:
            messagebox.showerror("Save Game", f"Error saving game state to {filename}: {e}")

    @classmethod
    def load_state(cls, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            messagebox.showinfo("Load Game", f"Game state loaded from {filename}")
            return cls.from_dict(data)
        except IOError as e:
            messagebox.showerror("Load Game", f"Error loading game state from {filename}: {e}")
            sys.exit(1)

    def game_over(self):
        return self.num_red == 0 or self.num_blue == 0

    def score(self):
        return self.num_red * RED_POINTS + self.num_blue * BLUE_POINTS

    def human_move(self, red_move, blue_move):
        if red_move < 0 or blue_move < 0:
            raise ValueError("Number of marbles cannot be negative.")
        if red_move > self.num_red or blue_move > self.num_blue:
            raise ValueError("Cannot remove more marbles than are available.")
        self.num_red -= red_move
        self.num_blue -= blue_move

    def computer_move(self):
        best_move = self.minmax(self.depth, True, -float('inf'), float('inf'))[1]
        self.num_red -= best_move[0]
        self.num_blue -= best_move[1]
        messagebox.showinfo("Computer Move", f"Computer removes {best_move[0]} red marbles and {best_move[1]} blue marbles.")

    def minmax(self, depth, is_maximizing, alpha, beta):
        if depth == 0 or self.game_over():
            return self.score(), (0, 0)
        if is_maximizing:
            max_eval = -float('inf')
            best_move = (0, 0)
            for move in self.get_moves():
                self.num_red -= move[0]
                self.num_blue -= move[1]
                eval = self.minmax(depth - 1, False, alpha, beta)[0]
                self.num_red += move[0]
                self.num_blue += move[1]
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = (0, 0)
            for move in self.get_moves():
                self.num_red -= move[0]
                self.num_blue -= move[1]
                eval = self.minmax(depth - 1, True, alpha, beta)[0]
                self.num_red += move[0]
                self.num_blue += move[1]
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def get_moves(self):
        if self.version == "standard":
            return [(2, 0), (0, 2), (1, 0), (0, 1)]
        else:
            return [(0, 1), (1, 0), (0, 2), (2, 0)]

    def play(self, red_move=None, blue_move=None):
        if not self.game_over():
            if self.current_player == "human":
                try:
                    self.human_move(red_move, blue_move)
                    self.current_player = "computer"
                except ValueError as e:
                    messagebox.showerror("Invalid Move", str(e))
                    return
            else:
                self.computer_move()
                self.current_player = "human"
            self.update_gui()
        else:
            messagebox.showinfo("Game Over", f"Game over! Final score: {self.score()}")
            self.disable_inputs()

    def update_gui(self):
        red_label.config(text=f"Red Marbles: {self.num_red}")
        blue_label.config(text=f"Blue Marbles: {self.num_blue}")

    def disable_inputs(self):
        red_move_entry.config(state=tk.DISABLED)
        blue_move_entry.config(state=tk.DISABLED)
        move_button.config(state=tk.DISABLED)
        save_button.config(state=tk.DISABLED)

def start_game():
    global game
    try:
        num_red = int(num_red_entry.get())
        num_blue = int(num_blue_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Number of marbles must be integers.")
        return
    game = NimGame(num_red, num_blue, version_var.get(), first_player_var.get(), int(depth_entry.get()))
    game.update_gui()

def load_game():
    filename = filedialog.askopenfilename(title="Load Game", filetypes=[("JSON files", "*.json")])
    if filename:
        global game
        game = NimGame.load_state(filename)
        game.update_gui()

def save_game():
    filename = filedialog.asksaveasfilename(title="Save Game", defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if filename:
        game.save_state(filename)

def make_move():
    try:
        red_move = int(red_move_entry.get())
        blue_move = int(blue_move_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Number of marbles to remove must be integers.")
        return
    game.play(red_move, blue_move)

# Setup the main window
root = tk.Tk()
root.title("Red-Blue Nim Game")

# Game settings
tk.Label(root, text="Number of Red Marbles:").grid(row=0, column=0)
num_red_entry = tk.Entry(root)
num_red_entry.grid(row=0, column=1)

tk.Label(root, text="Number of Blue Marbles:").grid(row=1, column=0)
num_blue_entry = tk.Entry(root)
num_blue_entry.grid(row=1, column=1)

tk.Label(root, text="Game Version:").grid(row=2, column=0)
version_var = tk.StringVar(value="standard")
tk.Radiobutton(root, text="Standard", variable=version_var, value="standard").grid(row=2, column=1)
tk.Radiobutton(root, text="Misere", variable=version_var, value="misere").grid(row=2, column=2)

tk.Label(root, text="First Player:").grid(row=3, column=0)
first_player_var = tk.StringVar(value="computer")
tk.Radiobutton(root, text="Computer", variable=first_player_var, value="computer").grid(row=3, column=1)
tk.Radiobutton(root, text="Human", variable=first_player_var, value="human").grid(row=3, column=2)

tk.Label(root, text="AI Depth:").grid(row=4, column=0)
depth_entry = tk.Entry(root)
depth_entry.grid(row=4, column=1)
depth_entry.insert(0, "3")

tk.Button(root, text="Start Game", command=start_game).grid(row=5, column=1)

# Game state
red_label = tk.Label(root, text="Red Marbles: 0")
red_label.grid(row=6, column=0)

blue_label = tk.Label(root, text="Blue Marbles: 0")
blue_label.grid(row=7, column=0)

tk.Label(root, text="Remove Red Marbles:").grid(row=8, column=0)
red_move_entry = tk.Entry(root)
red_move_entry.grid(row=8, column=1)

tk.Label(root, text="Remove Blue Marbles:").grid(row=9, column=0)
blue_move_entry = tk.Entry(root)
blue_move_entry.grid(row=9, column=1)

move_button = tk.Button(root, text="Make Move", command=make_move)
move_button.grid(row=10, column=1)


# Save/Load game
save_button = tk.Button(root, text="Save Game", command=save_game)
save_button.grid(row=11, column=0)

tk.Button(root, text="Load Game", command=load_game).grid(row=11, column=1)

root.mainloop()
