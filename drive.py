#import dependencies
import PIL
from PIL import Image, ImageTk
import tkinter as tk
import argparse
import cv2
import sys
import os
import socket
import numpy as np
import pickle

#imports Keras module for image processing
from keras.models import Model, load_model
from keras.layers import Input, Conv2D, MaxPooling2D, Activation, Dropout, Flatten, Dense


class Application:
    def __init__(self, camera, car):
        #functions related to key presses.
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

        #initialize as 0
        self.leftKeyDown = False
        self.rightKeyDown = False
        self.upKeyDown = False
        #text used to indicate direction
        self.leftText = 'left'
        self.rightText = 'right'
        #initializes as 0 for speed and angle (to be displayed)
        self.speed = 0
        self.angle = 0
        #rate of increase
        self.angleInterval = 10
        self.speedInterval = 51
        #initializes the program in training mode
        self.autonomousMode = False

        #Instances of such objects started
        self.camera = camera
        self.car = car
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #format (IP PROTOCOL, packet structure(datagram))

        #Opens data file for training data
        self.file = open('data.npy', 'ab') #(file, binary append)
        try:
            self.model = load_model('autopilot.h5')
        except:
            print("Error loading model.")

        #setup GUI
        self.vs = cv2.VideoCapture("http://" + self.camera + ":8080/video") # capture video frames, 0 is your default video
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
        self.root.config(cursor="arrow")
        self.root.bind('<Left>', leftKey)
        self.root.bind("<KeyRelease-Left>", leftKeyReleased)
        self.root.bind('<Right>', rightKey)
        self.root.bind("<KeyRelease-Right>", rightKeyReleased)
        self.root.bind('<Up>', upKey)
        self.root.bind("<KeyRelease-Up>", upKeyReleased)

        #Runs loops
        self.video_loop()
        self.key_loop()
        self.network_loop()
        self.record_loop()
        self.ai_loop()


    def record_loop(self):
        if(not self.autonomousMode and (self.speed is not 0 or self.angle is not 0)):
            np.save(self.file, [self.cv2image, self.angle]) #(numpy array)
        self.root.after(500, self.record_loop)


    def network_loop(self):
        message = str(self.speed) + ':' + str(self.angle) + '&'
        self.sock.sendto(str.encode(message), (self.car, 42069))
        self.root.after(10, self.network_loop)


    def key_loop(self): #only if in self driving mode
        if(not self.autonomousMode):
            if(self.rightKeyDown and self.angle + self.angleInterval <= 90):
                self.angle += self.angleInterval
            if(self.leftKeyDown and self.angle - self.angleInterval >= -90):
                self.angle -= self.angleInterval
            if(not self.leftKeyDown and not self.rightKeyDown):
                self.angle = 0
            if(self.upKeyDown and self.speed + self.speedInterval <= 255):
                self.speed += self.speedInterval
            if(not self.upKeyDown):
                self.speed = 0
        self.root.after(10, self.key_loop)

    def ai_loop(self):
        if(self.autonomousMode):
            a = self.model.predict(np.array(self.cv2image).reshape(1, 144,176,3)) #Uses the model to predict
            if(a[0][0] > 90):
                a[0][0] = 90
            elif(a[0][0] < -90):
                a[0][0] = -90

            self.speed = 255
            self.angle = int(a[0][0])


        self.root.after(30, self.ai_loop)

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream

        if ok:  # frame captured without any errors
            self.cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # convert colors from BGR to RGBA
            self.current_image = Image.fromarray(self.cv2image)  # convert image for PIL
            resized_image = self.current_image.resize([880, 720],PIL.Image.ANTIALIAS)
            imgtk = ImageTk.PhotoImage(image=resized_image)  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image

        self.speedLabel.config(text="Speed: " + str(self.speed))

        if(self.angle > 0):
            self.angleLabel.config(text="Angle: " + RightText + str(abs(self.angle)))
        elif(self.angle < 0):
            self.angleLabel.config(text="Angle: " + LeftText + str(abs(self.angle)))
        else:
            self.angleLabel.config('0')

        self.root.after(1, self.video_loop)  # call the same function after 30 milliseconds

    def destructor(self):

        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.file.close()
        self.root.destroy()
        self.vs.release()  # release web camera


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("--camera", default="192.168.12.8")
ap.add_argument("--car", default="192.168.12.220")
args = vars(ap.parse_args())

# start the app
print("[INFO] starting...")
pba = Application(args["camera"], args["car"])
pba.root.mainloop()
