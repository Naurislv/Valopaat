"""Implementation of motion detection together with extract intelligent layers
for lightning system.

Blob IDs: [0, 3, 8]
"""

# Standard imports
import argparse
import warnings
import datetime
import json
import time
import threading

# Dependency imports
import imutils
import cv2

# Local imports
from bulb_control_api import BulbControl
from detect import HandDetector

# pylint: disable=E1101

class Main(object):
    """Main class."""

    def __init__(self):

        self.bulb_control = BulbControl(CONFIG['bulb_ids'])
        self.detector = HandDetector()

        self.last_motion = False

    def motion_detection(self, frame, avg):
        """Detect motion based on parameters in conf.json"""
        timestamp = datetime.datetime.now()
        text = "Still"

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # if the average frame is None, initialize it
        if avg is None:
            print("[INFO] starting background model...")
            avg = gray.copy().astype("float")
            return frame, avg, text

        # accumulate the weighted average between the current frame and
        # previous frames, then compute the difference between the current
        # frame and running average
        cv2.accumulateWeighted(gray, avg, 0.5)
        frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

        # threshold the delta image, dilate the thresholded image to fill
        # in holes, then find contours on thresholded image
        thresh = cv2.threshold(frame_delta, CONFIG["delta_thresh"],
                               255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(
            thresh.copy(),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # loop over the contours
        for cnt in cnts[1]:
            # print(c.shape)

            # print(cv2.contourArea(c))
            # if the contour is too small, ignore it
            if cv2.contourArea(cnt) < CONFIG["min_area"]:
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text

            if CONFIG['draw_motion_rectangles']:
                (x_cnt, y_cnt, w_cnt, h_cnt) = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x_cnt, y_cnt),
                              (x_cnt + w_cnt, y_cnt + h_cnt), (0, 255, 0), 2)
            text = "Moving"

        # draw the text and timestamp on the frame
        t_s = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        cv2.putText(frame, "Status: {}".format(text), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(frame, t_s, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (0, 0, 255), 1)

        return frame, avg, text

    def detect_daylight(self, frame):
        """Based on pixel values adjust light intensity."""

        if frame.mean() > 150:
            return True
        else:
            return False

    def run(self):
        """Run programs main loop."""

        # initialize the camera and grab a reference to the raw camera capture
        # video_capture = cv2.VideoCapture('/dev/video0')
        video_capture = cv2.VideoCapture(0)

        # allow the camera to warmup, then initialize the average frame, last
        # uploaded timestamp, and frame motion counter
        print("[INFO] warming up...")
        time.sleep(CONFIG["camera_warmup_time"])
        avg = None

        # capture frames from the camera
        while True:
            # grab the raw NumPy array representing the image and initialize
            # the timestamp and occupied/unoccupied text
            _, frame = video_capture.read()

            # resize the frame, convert it to grayscale, and blur it
            frame = imutils.resize(frame, width=CONFIG['image_width'])

            # is_bright = self.detect_daylight(frame)

            # if is_bright:
            #     self.bulb_control.brightness = 0
            # else:
            #     self.bulb_control.brightness = 150

            ######### After this line frame is augmented with additional information #########
            frame, avg, text = self.motion_detection(frame, avg)
            # check to see if the room is occupied
            if text == "Moving":
                motion = True
                frame = self.detector.run_with_boxes(frame, CONFIG['class_probability'])
            else:
                motion = False

            threading.Thread(target=self._bolb_job, args=(motion,)).start()

            # check to see if the frames should be displayed to screen
            if CONFIG["show_video"]:
                # display the security feed
                cv2.imshow("Security Feed", frame)
                key = cv2.waitKey(1) & 0xFF

                # if the `q` key is pressed, break from the lop
                if key == ord("q"):
                    break

    def _bolb_job(self, motion):
        if CONFIG['mode'] == 'dance':
            self.bulb_control._execute_control('random-knownColors') # pylint: disable=W0212
        elif CONFIG['mode'] == 'normal':
            if motion and motion != self.last_motion:

                self.bulb_control.brightness = 200
                self.bulb_control._execute_control('white') # pylint: disable=W0212
                self.last_motion = motion

                print('Renew intensity', self.bulb_control.brightness)
            elif not motion:
                if self.bulb_control.brightness >= 1:
                    self.bulb_control.brightness -= 1
                    self.bulb_control._execute_control('white') # pylint: disable=W0212

                self.last_motion = motion

                print('Decreasing intensity', self.bulb_control.brightness)

def args_parse():
    """construct the argument parser and parse the arguments"""
    a_parse = argparse.ArgumentParser()
    a_parse.add_argument("-c", "--conf", required=True,
                         help="path to the JSON configuration file")
    return vars(a_parse.parse_args())

if __name__ == "__main__":
    ARGS = args_parse()

    # filter warnings, load the configuration and initialize the Dropbox
    # client
    warnings.filterwarnings("ignore")
    CONFIG = json.load(open(ARGS["conf"]))

    # Start program
    MAIN = Main()
    MAIN.run()
