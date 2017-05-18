import PIL
from PIL import Image, ImageTk
import tkinter as tk
import argparse
import cv2
import sys
import os
import socket

from keras.models import Model, load_model
from keras.layers import Input, Conv2D, MaxPooling2D, Activation, Dropout, Flatten, Dense


class Application:

    def __init__(self, camera, car):

        def leftKey(event):
            self.leftKeyDown = True
        def leftKeyReleased(event):
            self.leftKeyDown = False
        def rightKey(event):
            self.rightKeyDown = True
        def rightKeyReleased(event):
            self.rightKeyDown = False
        def upKey(event):
            self.upKeyDown = True
        def upKeyReleased(event):
            self.upKeyDown = False
        def setAutonomousMode():
            self.autonomousMode = True
        def setManualMode():
            self.autonomousMode = False

        self.leftKeyDown = False
        self.rightKeyDown = False
        self.upKeyDown = False

        self.speed = 0
        self.angle = 0

        self.angleInterval = 10
        self.speedInterval = 16

        self.autonomousMode = False

        self.camera = camera
        self.car = car
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.vs = cv2.VideoCapture("http://" + self.camera + ":8080/video") # capture video frames, 0 is your default video
        print(self.vs)
        self.current_image = None  # current image from the camera
        self.root = tk.Tk()  # initialize root window
        self.root.title("Carnet2")  # set window title
        # self.destructor function gets fired when the window is closed
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.panel = tk.Label(self.root)  # initialize image panel
        self.panel.pack(padx=10, pady=10)
        self.interfacePanel = tk.Label(self.root)  # initialize image panel
        self.interfacePanel.pack(padx=10, pady=10)
        self.trainingButton = tk.Button(self.interfacePanel, text ="Training Mode", command = setManualMode)
        self.trainingButton.pack()
        self.autonomousButton = tk.Button(self.interfacePanel, text ="Autonomous Mode", command = setAutonomousMode)
        self.autonomousButton.pack()
        self.speedLabel = tk.Label(self.interfacePanel, text = "Speed: ")
        self.speedLabel.pack()
        self.angleLabel = tk.Label(self.interfacePanel, text = "Angle: ")
        self.angleLabel.pack()
        self.speed = 0
        self.angle = 0
        self.root.config(cursor="arrow")
        self.root.bind('<Left>', leftKey)
        self.root.bind("<KeyRelease-Left>", leftKeyReleased)
        self.root.bind('<Right>', rightKey)
        self.root.bind("<KeyRelease-Right>", rightKeyReleased)
        self.root.bind('<Up>', upKey)
        self.root.bind("<KeyRelease-Up>", upKeyReleased)

        self.video_loop()
        self.key_loop()
        self.network_loop()

    def network_loop(self):    
        car_bytes = bytearray()
        car_bytes.append(self.speed)
        car_bytes.append(':')
        car_bytes.append(self.angle)
        self.sock.sendto(car_bytes, (self.car, 42069))
        self.root.after(10, self.network_loop)

    def key_loop(self):
        if(not self.autonomousMode):
            if(self.rightKeyDown and self.angle + self.angleInterval <= 90):
                self.angle += self.angleInterval
            if(self.leftKeyDown and self.angle - self.angleInterval >= -90):
                self.angle -= self.angleInterval
            if(not self.leftKeyDown and not self.rightKeyDown):
                self.angle = 0
            if(self.upKeyDown and self.speed + self.speedInterval <= 128):
                self.speed += self.speedInterval
            if(not self.upKeyDown):
                self.speed = 0
        self.root.after(100, self.key_loop)

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream

        if ok:  # frame captured without any errors
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image = Image.fromarray(cv2image)  # convert image for PIL
            resized_image = self.current_image.resize([880, 720],PIL.Image.ANTIALIAS)
            imgtk = ImageTk.PhotoImage(image=resized_image)  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image

        print("Speed: " + str(self.speed))
        self.speedLabel.config(text="Speed: " + str(self.speed))
        print("Angle: " + str(self.angle))
        self.angleLabel.config(text="Angle: " + str(self.angle))
        self.root.after(1, self.video_loop)  # call the same function after 30 milliseconds

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.root.destroy()
        self.vs.release()  # release web camera


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("--camera", default="192.168.12.70")
ap.add_argument("--car")
args = vars(ap.parse_args())

# start the app
print("[INFO] starting...")
pba = Application(args["camera"], args["car"])
pba.root.mainloop()
