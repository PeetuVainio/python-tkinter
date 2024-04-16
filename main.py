import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import re
from random import randint, uniform

class CoordinateSystemApp:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.plot = self.fig.add_subplot(111)
        self.plot.set_xlabel('X')
        self.plot.set_ylabel('Y')
        self.plot.set_title('Koordinaatio systeemi')
        self.plot.grid(True, which='both', linestyle='--')
        self.plot.set_xlim(-10, 10)
        self.plot.set_ylim(-10, 10)
        self.plot.set_xticks(range(-10, 11, 5))
        self.plot.set_yticks(range(-10, 11, 5))

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.equation_label = tk.Label(self.frame, text="Lisää lasku (Esim., y=2*x+10):")
        self.equation_label.pack()
        self.equation_entry = tk.Entry(self.frame)
        self.equation_entry.pack()

        self.plot_button = tk.Button(self.frame, text="Piirrä", command=self.plot_button_click)
        self.plot_button.pack()

    def plot_button_click(self):
        equation = self.equation_entry.get()
        x_values = np.linspace(-10, 10, 400)
        try:
            match = re.match(r"y\s*=\s*(.*)", equation)
            if match:
                expr_str = match.group(1)
                expr_str = expr_str.replace('^', '**')
                y_values = eval(expr_str, {}, {'x': x_values})
                self.plot.plot(x_values, y_values, color='b', linestyle='-')
                self.canvas.draw()
        except Exception as e:
            print(f"Error: {e}")

class SpaceJourney:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.space_width = 800
        self.space_height = 800
        self.create_space()

        self.create_rockets()
        self.create_moon()

        self.launch_button = tk.Button(self.frame, text="Launch", command=self.launch)
        self.launch_button.pack()

        self.min_rocket_speed = 4
        self.max_rocket_speed = 7
        self.arrived_rockets = 0
        self.messages = {}

    def create_space(self):
        self.canvas = tk.Canvas(self.frame, width=self.space_width, height=self.space_height, bg="black")
        self.canvas.pack()

    def create_rockets(self):
        self.rockets = []
        for _ in range(1):
            x, y = self.generate_valid_position()
            rocket1 = self.canvas.create_rectangle(x, y, x + 10, y + 20, fill="blue")
            
            x, y = self.generate_valid_position()
            rocket2 = self.canvas.create_rectangle(x, y, x + 10, y + 20, fill="red")
            
            self.rockets.append((rocket1, rocket2))

    def generate_valid_position(self):
        overlapping = True
        while overlapping:
            x = randint(0, self.space_width)
            y = self.space_height - 20
            overlapping = False
            for rocket_pair in self.rockets:
                rx1, ry1, rx2, ry2 = self.canvas.coords(rocket_pair[0])
                if x < rx2 and x + 10 > rx1 and y < ry2 and y + 20 > ry1:
                    overlapping = True
                    break
        return x, y

    def create_moon(self):
        self.moon_x = 50
        self.moon_y = 50
        self.moon_radius = 40
        self.moon = self.canvas.create_oval(self.moon_x - self.moon_radius, self.moon_y - self.moon_radius, self.moon_x + self.moon_radius, self.moon_y + self.moon_radius, fill="gray")

    def launch(self):
        self.launch_button.config(state=tk.DISABLED)
        self.countdown()

    def countdown(self):
        for i in range(10, -1, -1):
            self.parent.after((10 - i) * 1000, lambda i=i: self.show_countdown(i))
        self.parent.after(11000, self.launch_rockets)

    def show_countdown(self, count):
        self.canvas.delete("countdown_text")
        
        if count == 0:
            self.canvas.after(1000, self.canvas.delete, "countdown_text") 
        else:
            self.canvas.create_text(self.space_width // 2, self.space_height // 2, text=str(count), fill="white", font=("Arial", 30), tags="countdown_text")

    def launch_rockets(self):
        for pair in self.rockets:
            self.launch_rocket(pair)

    def launch_rocket(self, pair):
        ernesti_rocket, kernesti_rocket = pair
        if randint(0, 99) < 1:
            messagebox.showerror("Launch Failure", "Rocket launch failed! Program terminated.")
            self.parent.destroy()
        else:
            self.move_rocket(pair, ernesti_rocket, "Ernesti", uniform(self.min_rocket_speed, self.max_rocket_speed))
            self.move_rocket(pair, kernesti_rocket, "Kernesti", uniform(self.min_rocket_speed, self.max_rocket_speed))
    
    def move_rocket(self, pair, rocket, name, speed):
        if not self.canvas.coords(rocket):
            return

        x1, y1, x2, y2 = self.canvas.coords(rocket)
        if y1 <= self.moon_y:
            self.canvas.itemconfig(rocket, fill="green")
            self.play_sound(name)
            return

        dx = self.moon_x - (x1 + x2) / 2
        dy = self.moon_y - (y1 + y2) / 2
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > speed:
            x_move = dx / distance * speed
            y_move = dy / distance * speed
        else:
            x_move = dx
            y_move = dy

        for other_rocket_pair in self.rockets:
            if other_rocket_pair != pair:
                other_rocket = other_rocket_pair[0]
                if self.canvas.coords(other_rocket):
                    ox1, oy1, ox2, oy2 = self.canvas.coords(other_rocket)
                    if x1 - 20 < ox2 and x2 + 20 > ox1 and y1 - 20 < oy2 and y2 + 20 > oy1:
                        collision_dx = ox1 - (x1 + x2) / 2
                        collision_dy = oy1 - (y1 + y2) / 2
                        collision_distance = (collision_dx ** 2 + collision_dy ** 2) ** 0.5
                        if collision_distance > speed:
                            x_move += collision_dx / collision_distance * speed
                            y_move += collision_dy / collision_distance * speed
                        else:
                            x_move += collision_dx
                            y_move += collision_dy

        self.canvas.move(rocket, x_move, y_move)
        self.parent.after(100, lambda: self.move_rocket(pair, rocket, name, speed))

    def play_sound(self, name):
        if name == "Ernesti":
            print("Ernesti saapui kuuhun onnistuneesti!")
        elif name == "Kernesti":
            print("Kernesti saapui kuuhun onnistuneesti!")

def main():
    root = tk.Tk()
    root.title("Tkinter tabs")

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    coordinate_system_frame = ttk.Frame(notebook)
    space_journey_frame = ttk.Frame(notebook)

    notebook.add(coordinate_system_frame, text='Koordinaatio')
    notebook.add(space_journey_frame, text='Avaruusmatka')

    coordinate_system_app = CoordinateSystemApp(coordinate_system_frame)
    space_journey_app = SpaceJourney(space_journey_frame)

    root.mainloop()

if __name__ == "__main__":
    main()
