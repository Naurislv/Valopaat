"""Implementation of motion detection together with extract intelligent layers
for lightning system.

"""

# Standard imports
import argparse
import warnings
import datetime
import json
import time

# Dependency imports
import imutils
import cv2

# Local imports
from bulb_control_api import BulbControl

# pylint: disable=E1101

def motion_detection(frame, avg):
    """Detect motion based on parameters in conf.json"""
    text = "Still"

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the average frame is None, initialize it
    if avg is None:
        print("[INFO] starting background model...")
        avg = gray.copy().astype("float")
        return frame

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
        (x_cnt, y_cnt, w_cnt, h_cnt) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x_cnt, y_cnt),
                      (x_cnt + w_cnt, y_cnt + h_cnt), (0, 255, 0), 2)
        text = "Moving"

    return frame, avg, text

def main():
    """Run programs main loop."""

    bulb_control = BulbControl()

    # initialize the camera and grab a reference to the raw camera capture
    # video_capture = cv2.VideoCapture('/dev/video0')
    video_capture = cv2.VideoCapture(0)

    # allow the camera to warmup, then initialize the average frame, last
    # uploaded timestamp, and frame motion counter
    print("[INFO] warming up...")
    time.sleep(CONFIG["camera_warmup_time"])
    avg = None
    last_uploaded = datetime.datetime.now()
    motion_counter = 0

    # capture frames from the camera
    while True:
        # grab the raw NumPy array representing the image and initialize
        # the timestamp and occupied/unoccupied text
        _, frame = video_capture.read()
        timestamp = datetime.datetime.now()

        # resize the frame, convert it to grayscale, and blur it
        frame = imutils.resize(frame, width=500)
        frame, avg, text = motion_detection(frame, avg)

        # draw the text and timestamp on the frame
        t_s = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        cv2.putText(frame, "Status: {}".format(text), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, t_s, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (0, 0, 255), 1)

        # check to see if the room is occupied
        if text == "Occupied":
            # check to see if enough time has passed between uploads
            if (timestamp - last_uploaded).seconds >= CONFIG["min_upload_seconds"]:
                # increment the motion counter
                motion_counter += 1

                # check to see if the number of frames with consistent motion is
                # high enough
                if motion_counter >= CONFIG["min_motion_frames"]:
                    path = timestamp.strftime("%b-%d_%H_%M_%S" + ".jpg")
                    cv2.imwrite(path, frame)

                    last_uploaded = timestamp
                    motion_counter = 0

                    bulb_control.execute_controls("green")

        # otherwise, the room is not occupied
        else:
            motion_counter = 0

        # check to see if the frames should be displayed to screen
        if CONFIG["show_video"]:
            # display the security feed
            cv2.imshow("Security Feed", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key is pressed, break from the lop
            if key == ord("q"):
                break


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
    main()
