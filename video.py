#!/usr/bin/env python3


import time
import sys
import cv2
from color import name_to_bgr, detect_bgr, rect_average
import json
import threading
import color

REGION_SIZE = 10  # was 32
REGION_PAD = 90  # was 192

PREVIEW_SIZE = 20 # was 64
PREVIEW_PAD = 1
PREVIEW_CUBE_SIZE = (PREVIEW_SIZE+PREVIEW_PAD)*3
PREVIEW_X = 330 # was 1020
PREVIEW_Y = 200 # was 220
PREVIEW_SIDE_OFFSETS = [
    [PREVIEW_X+PREVIEW_CUBE_SIZE+5, PREVIEW_Y-PREVIEW_CUBE_SIZE-5],
    [PREVIEW_X, PREVIEW_Y],
    [PREVIEW_X+PREVIEW_CUBE_SIZE+5, PREVIEW_Y],
    [PREVIEW_X+PREVIEW_CUBE_SIZE*2+10, PREVIEW_Y],
    [PREVIEW_X+PREVIEW_CUBE_SIZE*3+15, PREVIEW_Y],
    [PREVIEW_X+PREVIEW_CUBE_SIZE+5, PREVIEW_Y+PREVIEW_CUBE_SIZE+5]
]

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

GRID_ORIGIN_X = 60
GRID_ORIGIN_Y = 230

WEBCAM_INDEX = 1

class Webcam:
    """
    Webcam class for handling video capture, region drawing, and state management for a Rubik's Cube solver interface.
    Methods:
        __init__():
            Initializes the Webcam object, sets up the initial state, and prints preview side offsets.
        draw_regions(frame):
            Draws the 3x3 grid regions on the provided video frame, highlights each region, and detects the color in each region.
        draw_state(frame):
            Draws the current cube state as a 6x3x3 preview on the provided video frame using color rectangles.
        update_window(frame):
            Updates the display window by drawing regions and state on the frame, resizing, and showing it.
        update_state(state="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"):
            Updates the internal cube state representation.
        video_loop():
            Main video capture loop. Continuously reads frames from the webcam, updates the window, and handles window events.
        start_video():
            Initializes regions, sets running flag, and starts the video capture loop.
        stop_video():
            Stops the video capture loop.
        scan():
            Scans the current frame, extracts the average color from each region, and returns the detected state as a list.
    """
   
    def __init__(self):
        """
        Initializes the object by updating its state and printing the preview side offsets.

        Calls the `update_state` method to set up the initial state of the object,
        and prints the value of the `PREVIEW_SIDE_OFFSETS` variable for debugging or informational purposes.
        """
        self.update_state()
        # print("Initiating webcam: " + str(PREVIEW_SIDE_OFFSETS))

    def draw_regions(self, frame):
        """
        Draws predefined regions on the given video frame and annotates them.
        This method performs the following actions:
            - Draws a black rectangle covering the right half of the frame.
            - Iterates over 9 predefined regions, drawing a white rectangle around each.
            - For each region, extracts the corresponding sub-image and detects its average color.
        Args:
            frame (numpy.ndarray): The video frame on which to draw the regions and annotations.
        Note:
            - Assumes `self.regions` is a list of (x, y) tuples specifying the top-left corner of each region.
            - Assumes `REGION_SIZE`, `detect_bgr`, and `rect_average` are defined elsewhere in the class or module.
        """
        # print("Drawing regions on frame")
        cv2.rectangle(frame, (FRAME_WIDTH // 2, 0), (FRAME_WIDTH, FRAME_HEIGHT), (0, 100, 0), -1)
        for index in range(9):
            x, y = self.regions[index]
            # print("Drawing region " + str(index) + " at: " + str([x, y]))
            rect  = frame[y:y+REGION_SIZE, x:x+REGION_SIZE]
            cv2.rectangle(frame, (x,y), (x+REGION_SIZE, y+REGION_SIZE), (255, 255, 255), 2)

            color = detect_bgr(rect_average(rect))[0]
            # print("Region " + str(index) + " color: " + str(color))
        # print("Regions drawn")

    def draw_state(self, frame):
        """
        Draws the current state of the Rubik's cube onto the provided video frame.

        Args:
            frame (numpy.ndarray): The image frame on which to draw the cube state.

        Description:
            For each of the six sides of the cube, this method draws a 3x3 grid of colored squares
            representing the stickers of that side. The position of each side is determined by
            PREVIEW_SIDE_OFFSETS, and each sticker's color is determined by the cube's current state.
            The color is converted to BGR format using the name_to_bgr function. Each sticker is drawn
            as a filled rectangle with size PREVIEW_SIZE and padding PREVIEW_PAD between stickers.
        """
        # print("Drawing state on frame")
        for side in range(6):
            offsetx, offsety = PREVIEW_SIDE_OFFSETS[side]
            for y in range(3):
                for x in range(3):
                    color = self.state[side*9 + y*3 + x]
                    # dummy_bgr = (0, 0, 255)
                    # print("Drawing for side " + str(side) + " (" + str(x) + ", " + str(y) + ") with color " + str(color))
                    cv2.rectangle(frame,
                        (offsetx+x*(PREVIEW_SIZE+PREVIEW_PAD), offsety+y*(PREVIEW_SIZE+PREVIEW_PAD)),
                        (offsetx+x*(PREVIEW_SIZE+PREVIEW_PAD)+PREVIEW_SIZE, offsety+y*(PREVIEW_SIZE+PREVIEW_PAD)+PREVIEW_SIZE),
                        name_to_bgr(color), -1)
                    # print("Drawing rectangle at: " + str((offsetx+x*(PREVIEW_SIZE+PREVIEW_PAD), offsety+y*(PREVIEW_SIZE+PREVIEW_PAD))) + " with color: " + str(name_to_bgr(color)))
                    

    def update_window(self, frame):
        """
        Updates the display window with the given video frame.

        This method draws predefined regions and the current state onto the provided frame,
        resizes the frame to half its original dimensions, and displays it in a window titled "win1".

        Args:
            frame (numpy.ndarray): The current video frame to be processed and displayed.

        Returns:
            None
        """
        self.draw_regions(frame)
        self.draw_state(frame)
        height, width, layers =  frame.shape
       # resize = cv2.resize(frame, (width//2, height//2)) 
       # cv2.imshow("win1", resize)
        cv2.imshow("win1", frame)


    def update_state(self, state = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"):
        """
        Update the current state of the object.

        Parameters:
            state (str): A string representing the new state. Defaults to a string of 54 'x' characters.

        Returns:
            None
        """
        self.state = state

    def video_loop(self):
        """
        Continuously captures video frames from the default camera and displays them in a window.
        This method initializes the camera, creates a display window, and enters a loop that reads frames
        from the camera while `self.running` is True. Each captured frame is stored in `self.current_frame`
        and passed to `self.update_window()` for display or processing. The loop checks for key presses
        every 10 milliseconds. When the loop ends, the camera is released and all OpenCV windows are closed.
        """
        print("Starting video loop")

        self.cam = cv2.VideoCapture(WEBCAM_INDEX)
        self.cam.set(cv2.CAP_PROP_AUTO_WB, 0.0)
        cv2.namedWindow("win1");
        cv2.moveWindow("win1", 20, 20);
        while self.running:
            ret, frame = self.cam.read()
           # print("Frame received: " + str(frame.shape))
            key = cv2.waitKey(10) & 0xff
            if ret:
                self.current_frame = frame.copy()
                self.update_window(frame)

        self.cam.release()
        cv2.destroyAllWindows()

    def start_video(self):
        """
        Initializes and starts the video processing loop.
        Sets the running flag to True, initializes the list of regions to be processed,
        and calculates the coordinates for a 3x3 grid of regions based on predefined
        REGION_SIZE and REGION_PAD constants. Then, starts the main video loop.
        """
        
        print("Starting video")
        
        self.running = True
        self.regions = []
        for y in range(3):
            for x in range(3):
                # print("Adding region at: " + str([GRID_ORIGIN_X+x*(REGION_SIZE+REGION_PAD), GRID_ORIGIN_Y+y*(REGION_SIZE+REGION_PAD)]))
                self.regions.append([GRID_ORIGIN_X+x*(REGION_SIZE+REGION_PAD), GRID_ORIGIN_Y+y*(REGION_SIZE+REGION_PAD)])
                
        self.video_loop()

    def stop_video(self):
        """
        Stops the video processing loop by setting the running flag to False.
        """
        self.running = False

    def scan(self):
        """
        Scans predefined regions in the current video frame and computes the average color for each region.
        Iterates over the list of region coordinates, extracts the corresponding rectangular area from the current frame,
        and calculates the average color using the `color.rect_average` function. Returns a list representing the state
        of all regions.
        Returns:
            list: A list of average color values for each region in the current frame.
        """
        state = []
        for index, (x,y) in enumerate(self.regions):
            rect  = self.current_frame[y:y+REGION_SIZE, x:x+REGION_SIZE]
            state.append(color.rect_average(rect))
        return state   

        return None

