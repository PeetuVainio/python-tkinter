import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import re
from random import randint, uniform

class Koordinaatiosysteemi:
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

class Avaruusmatka:
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
            messagebox.showerror("Lähtö epäonnistui!", "Raketin lähtö epäonnistui!")
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

class Matriisilaskin:
    def __init__(self, root):
        self.root = root

        tk.Label(root, text="Matriisi 1 (rivit x sarakkeet):").grid(row=0, column=0, padx=10, pady=5)
        self.rows1_entry = tk.Entry(root, width=5)
        self.rows1_entry.insert(0, "2")
        self.rows1_entry.grid(row=0, column=1, padx=5, pady=5)
        self.cols1_entry = tk.Entry(root, width=5)
        self.cols1_entry.insert(0, "3")
        self.cols1_entry.grid(row=0, column=2, padx=5, pady=5)

        tk.Label(root, text="Matriisi 2 (rivit x sarakkeet):").grid(row=1, column=0, padx=10, pady=5)
        self.rows2_entry = tk.Entry(root, width=5)
        self.rows2_entry.insert(0, "2")
        self.rows2_entry.grid(row=1, column=1, padx=5, pady=5)
        self.cols2_entry = tk.Entry(root, width=5)
        self.cols2_entry.insert(0, "3")
        self.cols2_entry.grid(row=1, column=2, padx=5, pady=5)

        self.matrix1_text = tk.Text(root, height=5, width=30)
        self.matrix1_text.insert(tk.END, "1 2 3\n4 5 6")
        self.matrix1_text.grid(row=2, column=0, columnspan=3, padx=10, pady=5)

        self.matrix2_text = tk.Text(root, height=5, width=30)
        self.matrix2_text.insert(tk.END, "7 8 9\n10 11 12")
        self.matrix2_text.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

        self.add_button = tk.Button(root, text="Lisää", command=self.perform_addition)
        self.add_button.grid(row=4, column=0, padx=10, pady=5)

        self.subtract_button = tk.Button(root, text="Vähennä", command=self.perform_subtraction)
        self.subtract_button.grid(row=4, column=1, padx=10, pady=5)

        self.multiply_button = tk.Button(root, text="Kerro", command=self.perform_multiplication)
        self.multiply_button.grid(row=4, column=2, padx=10, pady=5)

    def get_matrix_from_text(self, text_widget, rows, cols):
        """Hae matriisin elementit tekstilaatikosta."""
        matrix_elements = []
        try:
            lines = text_widget.get("1.0", tk.END).strip().split("\n")
            for line in lines:
                row_elements = [float(x) for x in line.strip().split()]
                if len(row_elements) != cols:
                    messagebox.showerror("Virhe", f"Jokaisessa rivissä tulee olla {cols} elementtiä.")
                    return None
                matrix_elements.append(row_elements)
            if len(matrix_elements) != rows:
                messagebox.showerror("Virhe", f"Matriisin tulee olla {rows}x{cols}.")
                return None
            return np.array(matrix_elements)
        except ValueError:
            messagebox.showerror("Virhe", "Virheellisiä matriisin elementtejä. Syötä numeerisia arvoja.")
            return None

    def perform_addition(self):
        rows1 = int(self.rows1_entry.get())
        cols1 = int(self.cols1_entry.get())
        matrix1 = self.get_matrix_from_text(self.matrix1_text, rows1, cols1)

        rows2 = int(self.rows2_entry.get())
        cols2 = int(self.cols2_entry.get())
        matrix2 = self.get_matrix_from_text(self.matrix2_text, rows2, cols2)

        if matrix1 is not None and matrix2 is not None:
            if matrix1.shape == matrix2.shape:
                result = np.add(matrix1, matrix2)
                messagebox.showinfo("Tulos", f"Lisäyksen tulos:\n{result}")
            else:
                messagebox.showerror("Virhe", "Matriisien ulottuvuuksien tulee olla samat lisäystä varten.")

    def perform_subtraction(self):
        rows1 = int(self.rows1_entry.get())
        cols1 = int(self.cols1_entry.get())
        matrix1 = self.get_matrix_from_text(self.matrix1_text, rows1, cols1)

        rows2 = int(self.rows2_entry.get())
        cols2 = int(self.cols2_entry.get())
        matrix2 = self.get_matrix_from_text(self.matrix2_text, rows2, cols2)

        if matrix1 is not None and matrix2 is not None:
            if matrix1.shape == matrix2.shape:
                result = np.subtract(matrix1, matrix2)
                messagebox.showinfo("Tulos", f"Vähennyksen tulos:\n{result}")
            else:
                messagebox.showerror("Virhe", "Matriisien ulottuvuuksien tulee olla samat vähennystä varten.")

    def perform_multiplication(self):
        rows1 = int(self.rows1_entry.get())
        cols1 = int(self.cols1_entry.get())
        matrix1 = self.get_matrix_from_text(self.matrix1_text, rows1, cols1)

        rows2 = int(self.rows2_entry.get())
        cols2 = int(self.cols2_entry.get())
        matrix2 = self.get_matrix_from_text(self.matrix2_text, rows2, cols2)

        if matrix1 is not None and matrix2 is not None:
            if matrix1.shape[1] == matrix2.shape[0]:
                result = np.dot(matrix1, matrix2)
                messagebox.showinfo("Tulos", f"Kertolaskun tulos:\n{result}")
            else:
                messagebox.showerror("Virhe", "Matriisin 1 sarakkeiden tulee olla samat kuin matriisin 2 rivit kertolaskua varten.")

class Kuutio:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(5, 5))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        sliders_frame = ttk.Frame(self.frame)
        sliders_frame.pack(side=tk.TOP, pady=10)

        self.create_slider(sliders_frame, "X")
        self.create_slider(sliders_frame, "Y")
        self.create_slider(sliders_frame, "Z")

        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0

        self.update_plot()

    def create_slider(self, parent, text):
        label = ttk.Label(parent, text=text)
        label.pack(side=tk.LEFT, padx=10)

        scale = ttk.Scale(parent, from_=-180, to=180, length=100,
        command=self.update_plot, orient=tk.HORIZONTAL)
        scale.pack(side=tk.LEFT, padx=10)

        if text == "X":
            self.angle_x_slider = scale
        elif text == "Y":
            self.angle_y_slider = scale
        elif text == "Z":
            self.angle_z_slider = scale

    def update_plot(self, event=None):
        self.angle_x = np.radians(self.angle_x_slider.get())
        self.angle_y = np.radians(self.angle_y_slider.get())
        self.angle_z = np.radians(self.angle_z_slider.get())

        self.ax.clear()
        self.ax.set_xlim([-2, 2])
        self.ax.set_ylim([-2, 2])
        self.ax.set_zlim([-2, 2])

        vertices = np.array([
            [-1, -1, -1],
            [1, -1, -1],
            [1, 1, -1],
            [-1, 1, -1],
            [-1, -1, 1],
            [1, -1, 1],
            [1, 1, 1],
            [-1, 1, 1]
        ])

        edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],
            [4, 5], [5, 6], [6, 7], [7, 4],
            [0, 4], [1, 5], [2, 6], [3, 7]
        ]

        rot_x = np.array([
            [1, 0, 0],
            [0, np.cos(self.angle_x), -np.sin(self.angle_x)],
            [0, np.sin(self.angle_x), np.cos(self.angle_x)]
        ])
        rot_y = np.array([
            [np.cos(self.angle_y), 0, np.sin(self.angle_y)],
            [0, 1, 0],
            [-np.sin(self.angle_y), 0, np.cos(self.angle_y)]
        ])
        rot_z = np.array([
            [np.cos(self.angle_z), -np.sin(self.angle_z), 0],
            [np.sin(self.angle_z), np.cos(self.angle_z), 0],
            [0, 0, 1]
        ])

        rotated_vertices = vertices.dot(rot_x).dot(rot_y).dot(rot_z)

        for edge in edges:
            self.ax.plot3D(
                [rotated_vertices[edge[0], 0], rotated_vertices[edge[1], 0]],
                [rotated_vertices[edge[0], 1], rotated_vertices[edge[1], 1]],
                [rotated_vertices[edge[0], 2], rotated_vertices[edge[1], 2]],
                'b'
            )

        self.canvas.draw()

def main():
    root = tk.Tk()
    root.title("test")

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    koordinaatio_system_frame = ttk.Frame(notebook)
    avaruus_journey_frame = ttk.Frame(notebook)
    matriisi_system_frame = ttk.Frame(notebook)
    kuutio_system_frame = ttk.Frame(notebook)

    notebook.add(koordinaatio_system_frame, text='Koordinaatio')
    notebook.add(avaruus_journey_frame, text='Avaruusmatka')
    notebook.add(matriisi_system_frame, text='Matriisilaskin')
    notebook.add(kuutio_system_frame, text='3DKuutio')

    koordinaatio_system_app = Koordinaatiosysteemi(koordinaatio_system_frame)
    avaruus_journey_app = Avaruusmatka(avaruus_journey_frame)
    matriisi_calculator_app = Matriisilaskin(matriisi_system_frame)
    kuutio_rotation_app = Kuutio(kuutio_system_frame)

    root.mainloop()

if __name__ == "__main__":
    main()