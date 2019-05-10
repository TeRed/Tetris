"""
Autor: Albert Duź
Temat: Tetris
"""

from tkinter import *
import tkinter.messagebox
import random
from PIL import ImageTk
import winsound


#Class cointing bricks and functions to bricks
class Brick:
    #Bricks are made of boxes
    BOX_SIZE = 30
    CANVAS_WIDTH = 420
    CANVAS_HEIGHT = 540
    #Used to calculate where brick should start while remaining on columns
    START_POINT = (CANVAS_WIDTH // (2 * BOX_SIZE)) * BOX_SIZE - BOX_SIZE

    #Table with bricks definitions
    BRICKS = (
        ("green", (0, 1), (1, 0), (0, 0), (1, 1)),
        ("red", (1, 1), (1, 0), (0, 0), (2, 1)),
        ("blue", (2, 0), (1, 0), (0, 0), (3, 0)),
        ("orange", (1, 1), (0, 1), (1, 0), (2, 1)),
        ("pink", (1, 1), (0, 1), (0, 0), (2, 1)),
        ("brown", (1, 0), (1, 1), (0, 1), (2, 0)),
        ("black", (1, 1), (0, 1), (2, 0), (2, 1))
    )

    def __init__(self, canvas):
        self.canvas = canvas
        self.brick = random.choice(Brick.BRICKS)
        self.color = self.brick[0]
        self.boxes = []

        for point in self.brick[1:]:
            box = self.canvas.create_rectangle(
                point[0] * Brick.BOX_SIZE + Brick.START_POINT,
                point[1] * Brick.BOX_SIZE,
                point[0] * Brick.BOX_SIZE + Brick.BOX_SIZE + Brick.START_POINT,
                point[1] * Brick.BOX_SIZE + Brick.BOX_SIZE,
                fill=self.color,
                outline=""
            )
            self.boxes.append(box)

    #Check if box can be moved (x, y) * BOZ_SIZE
    def move_box_bool(self, box, x, y):
        x *= Brick.BOX_SIZE
        y *= Brick.BOX_SIZE
        coords = self.canvas.coords(box)

        if coords[0] + x < 0: return False
        if coords[1] + y < 0: return False
        if coords[2] + x > Brick.CANVAS_WIDTH: return False
        if coords[3] + y > Brick.CANVAS_HEIGHT: return False

        overlap = set(self.canvas.find_overlapping(
            (coords[0] + coords[2]) / 2 + x,
            (coords[1] + coords[3]) / 2 + y,
            (coords[0] + coords[2]) / 2 + x,
            (coords[1] + coords[3]) / 2 + y
        ))

        other_boxes = set(self.canvas.find_all()) - set(self.boxes)
        if other_boxes & overlap:
            return False

        return True

    # Check if brick can be moved (x, y) * BOZ_SIZE
    def move_brick_bool(self, x, y):
        for box in self.boxes:
            if not self.move_box_bool(box, x, y):
                return False

        return True

    #If can than move (x, y) * BOZ_SIZE this Brick
    def move(self, x, y):
        if not self.move_brick_bool(x, y):
            return False

        for box in self.boxes:
            self.canvas.move(box, x * Brick.BOX_SIZE, y * Brick.BOX_SIZE)

        return True

    #Subfunction for rotate function
    #Return move_coords * BOX_SIZE than box should be moved to rotate
    def new_position_move(self, box, pivot):
        box_coords = self.canvas.coords(box)
        pivot_coords = self.canvas.coords(pivot)

        box_coords[0] /= Brick.BOX_SIZE
        pivot_coords[0] /= Brick.BOX_SIZE
        box_coords[1] /= Brick.BOX_SIZE
        pivot_coords[1] /= Brick.BOX_SIZE

        relative_coords = (box_coords[0] - pivot_coords[0], box_coords[1] - pivot_coords[1])

        transformed_coords = (-relative_coords[1], relative_coords[0])

        new_coords = (transformed_coords[0] + pivot_coords[0], transformed_coords[1] + pivot_coords[1])

        move_coords = (new_coords[0] - box_coords[0], new_coords[1] - box_coords[1])

        return move_coords

    #if rotation with clock is possible than this function rotate
    def rotate(self):
        if self.color == "green": return True
        boxes = list(self.boxes)
        pivot = boxes.pop(0)

        for box in boxes:
            move = self.new_position_move(box, pivot)
            if not self.move_box_bool(box, move[0], move[1]): return False

        for box in boxes:
            move = self.new_position_move(box, pivot)
            self.canvas.move(box, move[0] * Brick.BOX_SIZE, move[1] * Brick.BOX_SIZE)

        return True

class Tetris:

    def __init__(self, master):
        #Booleans used to store info about game options
        self.new_game_bool = True
        self.game_paused_bool = False
        #True when "Start new game button" is pushed
        self.sng_button_bool = False
        self.mute_bool = False

        # Levels, points and connected
        self.level = 1
        self.points = 0
        self.deleted_lines = 0
        self.higher_level_border = 1000
        # min=600 max=240
        self.speed = 600

        self.master = master
        self.master.title("Tetris")
        self.init_UI()
        self.master.bind("<Key>", self.key)
        self.master.resizable(width=False, height=False)
        self.master.mainloop()

    def init_UI(self):

        #Label with score
        self.label = Label(self.master, text=("Level: " + str(self.level) + " Points: " + str(self.points) + " Lines: " + str(self.deleted_lines)),
                           height=3,
                           font=("calibri", 12, "bold")
                           )
        self.label.grid(row=0, columnspan=3)

        #Buttons
        image = ImageTk.PhotoImage(file="img\\start.png")
        self.start_new_game_button = Button(self.master, command=self.sng_button, width=170, height=64)
        self.start_new_game_button.image = image
        self.start_new_game_button.config(image=image)
        self.start_new_game_button.grid(row=1, column=0)

        image = ImageTk.PhotoImage(file="img\\pause.png")
        self.pause_game_button = Button(self.master, command=self.pg_button, width=170, height=64)
        self.pause_game_button.image = image
        self.pause_game_button.config(image=image)
        self.pause_game_button.grid(row=1, column=2)

        image = ImageTk.PhotoImage(file="img\\muteoff.png")
        self.mute_button = Button(self.master, command=self.m_button, height=64)
        self.mute_button.image = image
        self.mute_button.config(image=image)
        self.mute_button.grid(row=1, column=1)

        #Canvas for creating bricks
        self.canvas = Canvas(self.master, width=Brick.CANVAS_WIDTH, height=Brick.CANVAS_HEIGHT, bg="grey")
        self.canvas.grid(row=2, columnspan=3)

    #Main game loop
    def loop(self):
        if self.new_game_bool:
            self.new_game_bool = False
            self.current_brick = Brick(self.canvas)
            self.level = 1
            self.points = 0
            self.deleted_lines = 0
            self.higher_level_border = 1000
            self.speed = 600
            self.label.config(text=("Level: " + str(self.level) + " Points: " + str(self.points) + " Lines: " + str(self.deleted_lines)))

        if not self.current_brick.move_brick_bool(0, 1) and not self.game_paused_bool:
            self.delete_complete_lines()
            self.current_brick = Brick(self.canvas)

            if not self.current_brick.move_brick_bool(0, 1):
                self.prepare_new_game()
                return

            self.update_score()

        elif not self.game_paused_bool:
            self.current_brick.move(0, 1)

        if self.sng_button_bool:
            self.prepare_new_game()
            return
        self.master.after(self.speed, self.loop)

    #Preparing variables for new game
    def prepare_new_game(self):
        image = ImageTk.PhotoImage(file="img\\start.png")
        self.start_new_game_button.image = image
        self.start_new_game_button.config(image=image)
        self.new_game_bool = True
        self.sng_button_bool = False
        self.game_paused_bool = False
        self.canvas.delete(tkinter.ALL)

    #Update score +15 points; update other variables connected with score
    def update_score(self):
        self.points += 15
        if self.points >= self.higher_level_border and self.level < 10:
            self.higher_level_border += 1000
            self.level += 1
            self.speed -= 40
        self.label.config(text=("Level: " + str(self.level) + " Points: " + str(self.points) + " Lines: " + str(self.deleted_lines)))

    # Look at function name
    def delete_complete_lines(self):
        boxes = self.canvas.find_all()

        lines = []
        deleted = []
        for _ in range(0, int(Brick.CANVAS_HEIGHT / Brick.BOX_SIZE)):
            lines.append([])

        for box in boxes:
            lines[int(self.canvas.coords(box)[1] / Brick.BOX_SIZE)].append(box)

        for line in lines:
            if len(line) == int(Brick.CANVAS_WIDTH / Brick.BOX_SIZE):
                self.line_sound()
                for _ in range(0, 7): self.update_score()
                for box in line:
                    self.canvas.delete(box)
                deleted.append(lines.index(line))
                self.deleted_lines += 1

        for i in deleted:
            for line in lines[0:i]:
                for box in line:
                    self.canvas.move(box, 0, Brick.BOX_SIZE)

    # Give sound when complete line is deleted
    def line_sound(self):
        if not self.mute_bool:
            winsound.PlaySound("wav\\line.wav", winsound.SND_ASYNC)

    #Events
    def key(self, event):
        if event.keysym == "Left" and not self.new_game_bool and not self.game_paused_bool:
            self.current_brick.move(-1, 0)
        if event.keysym == "Right" and not self.new_game_bool and not self.game_paused_bool:
            self.current_brick.move(1, 0)
        if event.keysym == "Down" and not self.new_game_bool and not self.game_paused_bool:
            self.current_brick.move(0, 1)
        if event.keysym == "Up" and not self.new_game_bool and not self.game_paused_bool:
            self.current_brick.rotate()
        if event.char == " " and not self.new_game_bool and not self.game_paused_bool:
            while self.current_brick.move_brick_bool(0, 1):
                self.current_brick.move(0, 1)
        if event.char == "s":
            self.pg_button()
        if event.char == "m":
            self.m_button()

    #Command for "Start new game button"
    def sng_button(self):
        if self.new_game_bool:
            self.game_paused_bool = False
            self.sng_button_bool = False
            image = ImageTk.PhotoImage(file="img\\stop.png")
            self.start_new_game_button.image = image
            self.start_new_game_button.config(image=image)
            self.loop()
            return
        self.sng_button_bool = True

    #Command for "Pause game button"
    def pg_button(self):
        self.game_paused_bool = not self.game_paused_bool

    #Command for "Mute button"
    def m_button(self):
        if not self.mute_bool:
            self.mute_bool = True
            image = ImageTk.PhotoImage(file="img\\muteon.png")
            self.mute_button.image = image
            self.mute_button.config(image=image)
        else:
            self.mute_bool = False
            image = ImageTk.PhotoImage(file="img\\muteoff.png")
            self.mute_button.image = image
            self.mute_button.config(image=image)


def main():
    root = Tk()
    Tetris(root)

if __name__ == "__main__":
    main()
