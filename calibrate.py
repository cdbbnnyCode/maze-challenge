#!/usr/bin/env python3

import servo
import interp

import time
import random
from tkinter import *

# The Plan
# --------
# Step 0: A basic window with a 'Start calibration' button
# Step 1: Select the horizontal axis--the vertical axis will be chosen automatically.
# Step 2: Center both axes
# Step 3: Set min/max range
# Step 4: Display results
currentStage = None
currentStageID = -1
results = ""

class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()

class AppStage:
    widgets = []

    def createWidgets(self, app):
        pass

    def destroyWidgets(self):
        for widget in self.widgets:
            widget.destroy()

    def getResults(self):
        return ''

def nextStage():
    global currentStage, currentStageID, results
    currentStageID += 1
    if currentStage is not None:
        results += currentStage.getResults()
        currentStage.destroyWidgets()
    if currentStageID == len(stages):
        root.destroy()
        print("\n\nCalibration results:")
        print("--------------------")
        print(results)
        return
    currentStage = stages[currentStageID]()
    currentStage.createWidgets(app)

class Stage0(AppStage):
    def createWidgets(self, app):
        self.widgets.append(Label(app, text="Marble Maze Calibrator"))
        self.widgets.append(Label(app, text="v1.0"))
        self.widgets.append(Button(app, text="Start Calibration", command=nextStage))
        for w in self.widgets:
            w.pack()

class Stage1(AppStage):
    def createWidgets(self, app):
        label = Label(app, text="Choose the horizontal (Y) axis servo")
        frame = Frame(app)
        self.btn1 = Button(frame, text="Pin 12", command=self.choose_pin12)
        self.btn2 = Button(frame, text="Pin 13", command=self.choose_pin13)

        self.btn_continue = Button(app, text="Continue", command=nextStage)
        # Layout
        label.pack()
        self.btn1.pack(side=LEFT)
        self.btn2.pack(side=RIGHT)
        frame.pack()
        # frame.place(relx=.5, rely=.5, anchor=CENTER)
        self.btn_continue.pack(side=BOTTOM, pady=100)
        self.btn_continue['state'] = DISABLED
        self.widgets.append(label)
        self.widgets.append(frame)
        self.widgets.append(self.btn_continue)

        self.hservo_pin = -1

    def test_servo(self, pin):
        servo.set_servo_angle(pin, random.random())
        time.sleep(0.01)
        servo.disable_servo(pin)

    def choose_pin12(self):
        # 12 is definitely better than 13
        self.btn1['text'] = '>Pin 12<'
        self.btn2['text'] = 'Pin 13'
        self.btn_continue['state'] = NORMAL
        self.hservo_pin = 12
        self.test_servo(12)

    def choose_pin13(self):
        # 13 is totally better than 12
        self.btn1['text'] = 'Pin 12'
        self.btn2['text'] = '>Pin 13<'
        self.btn_continue['state'] = NORMAL
        self.hservo_pin = 13
        self.test_servo(13)

    def getResults(self):
        servo.SERVO_HORIZ = self.hservo_pin
        if self.hservo_pin == 12:
            servo.SERVO_VERT = 13
            return "In servo.py, make sure that:\nSERVO_HORIZ = 12\nSERVO_VERT = 13\n"
        else:
            servo.SERVO_VERT = 12
            return "In servo.py, make sure that:\nSERVO_HORIZ = 13\nSERVO_VERT = 12\n"


class Stage2(AppStage):
    def createWidgets(self, app):
        label = Label(app, text="Center the axes")
        frame = Frame(app)
        self.btn_up = Button(frame, text="Up", command=self.inc_x)
        self.btn_left = Button(frame, text="Left", command=self.dec_y)
        self.btn_right = Button(frame, text="Right", command=self.inc_y)
        self.btn_down = Button(app, text="Down", command=self.dec_x)
        self.btn_continue = Button(app, text="Continue", command=nextStage)
        self.widgets = [label, frame, self.btn_down, self.btn_continue]
        
        # Layout
        label.pack()
        frame.pack()
        self.btn_up.pack()
        self.btn_left.pack(side=LEFT)
        self.btn_right.pack(side=RIGHT)
        self.btn_down.pack()
        self.btn_continue.pack(side=BOTTOM, pady=100)
        
        self.x_center = interp.get_servo_pos('X', 0)
        self.y_center = interp.get_servo_pos('Y', 0)
        self.update_xy()

    def update_xy(self):
        if self.x_center < 0: self.x_center = 0
        if self.y_center < 0: self.y_center = 0
        if self.x_center > 1: self.x_center = 1
        if self.y_center > 1: self.y_center = 1
        print("X = %.4f, y = %.4f" % (self.x_center, self.y_center))
        servo.set_servo_angle(servo.SERVO_HORIZ, self.y_center)
        servo.set_servo_angle(servo.SERVO_VERT, self.x_center)

    def inc_x(self):
        self.x_center += .01
        self.update_xy()

    def dec_x(self):
        self.x_center -= .01
        self.update_xy()

    def inc_y(self):
        self.y_center += .01
        self.update_xy()

    def dec_y(self):
        self.y_center -= .01
        self.update_xy()

    def getResults(self):
        interp.X_MIN = self.x_center
        interp.X_MAX = self.x_center
        interp.Y_MIN = self.y_center
        interp.Y_MAX = self.y_center
        return 'XY centered at (%.4f, %.4f)\n' % (self.x_center, self.y_center)


class Stage3(AppStage):
    def createWidgets(self, app):
        self.x_center = interp.X_MIN
        self.y_center = interp.Y_MIN

        label = Label(app, text="Set the maximum servo travel")
        self.x_travel = Scale(app, from_=0, to=self.get_max_travel('X'), label="X travel", orient=HORIZONTAL, resolution=.01, command=self.updateXY)
        self.y_travel = Scale(app, from_=0, to=self.get_max_travel('Y'), label="Y travel", orient=HORIZONTAL, resolution=.01, command=self.updateXY)
        label2 = Label(app, text="Test the range:")
        self.x_test = Scale(app, from_=-1, to=1, label="X coordinate", orient=HORIZONTAL, command=self.updateXY)
        self.y_test = Scale(app, from_=-1, to=1, label="Y coordinate", orient=HORIZONTAL, command=self.updateXY)
        self.btn_continue = Button(app, text="Finish", command=nextStage)
        
        self.widgets = [label, self.x_travel, self.y_travel, label2, self.x_test, self.y_test, self.btn_continue]
        
        label.pack()
        self.x_travel.pack(fill='x')
        self.y_travel.pack(fill='x')
        label2.pack()
        self.x_test.pack()
        self.y_test.pack()
        self.btn_continue.pack(side=BOTTOM, pady=10)
        
        self.updateXY()
    
    def get_max_travel(self, axis):
        x_to_min = interp.X_MIN # The distance from the x center to 0
        y_to_min = interp.Y_MIN # The distance from the y center to 0
        x_to_max = 1 - x_to_min # The distance from the x center to 1
        y_to_max = 1 - y_to_min # The distance from the y center to 1

        # This is how much travel we can have before one axis hits a limit
        if axis == 'X':
            return min(x_to_min, x_to_max)
        elif axis == 'Y':
            return min(y_to_min, y_to_max)
        else:
            return min(min(x_to_min, x_to_max), min(y_to_min, y_to_max))
    
    def updateXY(self, newvalue=0):
        interp.X_MIN = self.x_center - self.x_travel.get()
        interp.Y_MIN = self.y_center - self.y_travel.get()
        interp.X_MAX = self.x_center + self.x_travel.get()
        interp.Y_MAX = self.y_center + self.y_travel.get()
        x = interp.get_servo_pos('X', self.x_test.get())
        y = interp.get_servo_pos('Y', self.y_test.get())
        servo.set_servo_angle(servo.SERVO_HORIZ, y)
        servo.set_servo_angle(servo.SERVO_VERT, x)

    def getResults(self):
        return "Servo range: (+/-%.4f, +/-%.4f)\nIn interp.py, make sure that:\nX_MIN = %.4f\nY_MIN = %.4f\nX_MAX = %.4f\nY_MAX = %.4f\n" % \
            (self.x_travel.get(), self.y_travel.get(), interp.X_MIN, interp.Y_MIN, interp.X_MAX, interp.Y_MAX)


class Stage4(AppStage):
    def createWidgets(self, app):
        label = Label(app, text="Calibration Results:")
        frame = Frame(app)
        textarea = Text(frame, height = 12)
        btn_continue = Button(app, text="Done", command=nextStage)
        
        self.widgets = [label, textarea, btn_continue]
        
        label.pack()
        textarea.pack()
        frame.pack()
        btn_continue.pack()
        
        textarea.insert(END, results)
        textarea['state'] = DISABLED


stages = [Stage0, Stage1, Stage2, Stage3, Stage4]

if __name__ == "__main__":
    servo.init_outputs()
    root = Tk()
    root.title("Marble Maze Calibrator v1.0")
    root.geometry("480x320+100+100")
    app = Application(root)
    nextStage()
    app.mainloop()
