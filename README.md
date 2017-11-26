# Valopaat
Youtube demo: https://www.youtube.com/watch?v=gRnZnipXp54&feature=youtu.be
Devpost: https://devpost.com/software/valopaat-b12c4q
https://hackjunction.com/


## Inspiration
The original idea is to use the power of artificial intelligence in the field of image recognition to control lighting in various environments and for different scenarios.

Example scenarios:

1. Adjusting light brightness through Fingertip gestures.

This can be used in addition to Helvar occupancy sensor so than when someone enters the room light turns on then the level of Brightness can be controlled through lifting one finger and moving to the left or the right.

Lights could be turned off with a certain gesture, for example by putting your hand in fist. After this the occupancy sensor no longer turns on the lights even in case some movement occurs. In addition to office-like environments, this enables the usage of the solution in bedrooms. Otherwise rolling in a bed or someone entering the bedroom would cause lights to turn on. A traditional light switch can be used for activating the occupancy sensor and gesture detection when desired.

2. Adjust lighting based on number of people in the room

3. Detect day or night and adjust light accordingly

## What it does

We have implemented all the scenarios above, and with the help of an android application

At the moment the application detects any movements and acts only as a light switch. If no movement is detected, light goes off and when movement occurs light goes back on.

We had the web cam installed so that it detects only every passer-by of the Helvar light and any other movement is ignored. The python application acts similarly as an occupancy sensor. With further improvements it could be possible to adjust brightness with either speed of movement or gesture recognition.

## How we built it

The system is composed of 3 layers for image processing:

layer 1: Motion detection by video camera
layer 2: We implemented SSD You Only Look Once (YOLO) neural network specifically made for real time object detection applications. Therefore we are able to detect 100 objects in real time.
layer 3: Gesture recognition

We used Helvar REST API to control light switches

Harware: Normal web camera

An Android application to configure the system.

## Challenges we ran into
Fingertip gesture recognition turned out to be challenging. The quality of laptop web cams was quite poor and the overall lighting in the event was a bit dim which made image processing more difficult. We also used techniques that based on background subtraction and those are challenging in noisy environments like junction.

## Accomplishments that we're proud of

Creating a smart lighting system in a few days.

## What we learned
Opencv is a good open source library for image processing.
Helvar sensors and API were fun to play with.

## What's next for valopaat
Improving hand gesture recognition through use of thermal camera. To work in the dark.