import PIL
from PIL import Image, ImageTk
import tkinter as tk
import argparse
import datetime
import cv2
import sys
import os

class Application:
    def __init__(self):

        self.vs = cv2.VideoCapture("http://192.168.12.70:8080/video") # capture video frames, 0 is your default video
        print(self.vs)
        self.current_image = None  # current image from the camera
        self.root = tk.Tk()  # initialize root window
        self.root.title("Carnet2")  # set window title
        # self.destructor function gets fired when the window is closed
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.panel = tk.Label(self.root)  # initialize image panel
        self.panel.pack(padx=10, pady=10)
        self.root.config(cursor="arrow")


        # start a self.video_loop that constantly pools the video sensor
        # for the most recently read frame
        self.video_loop()


    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream

#        frame = cv2.resize(frame, (1500,1000))
        if ok:  # frame captured without any errors
            #key = cv2.waitKey()
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image = Image.fromarray(cv2image)  # convert image for PIL
            resized_image = self.current_image.resize([800, 600],PIL.Image.ANTIALIAS)
            imgtk = ImageTk.PhotoImage(image=resized_image)  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image
            #self.root.attributes("-fullscreen",True)
        self.root.after(1, self.video_loop)  # call the same function after 30 milliseconds


    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.root.destroy()
        self.vs.release()  # release web camera


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
args = vars(ap.parse_args())

# start the app
print("[INFO] starting...")
pba = Application()
pba.root.mainloop()
