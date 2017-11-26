#!/usr/bin/python3.5

import requests
import json
import logging
import time
import sys
import random
import traceback
import ssl
import copy
import threading

LOGLEVEL_BulbControl = logging.INFO

class BulbControl(object):
    def __init__(self, bulb_ids, name="BulbControl"):

        if not isinstance(bulb_ids, list) or not bulb_ids:
            bulb_ids = [0]
        
        self.bulb_id_set        = bulb_ids
        self.bulb_id            = bulb_ids[0]
        self.brightness         = 200
        self.params             = {}
        self._loop              = None
        self.template_url       = ""
        self._logger            = logging.getLogger(name)
        self._logger.setLevel(LOGLEVEL_BulbControl)
        self._logger.info("Initiating BulbControl API")
        self._initialize()
        self.threads = []

    def _initialize(self):
        self.set_url_template()
        self.color_profiles = {"red":(0.63, 0.3), "blue":(0.1, 0.2), "green": (0.18, 0.70), "white":(0.3, 0.3), \
                               "pink":(0.48, 0.23), "purple":(0.32, 0.1), "yellow":(0.42, 0.50), "orange":(0.42, 0.42)}
        
        self.color_proile_keys = list(self.color_profiles.keys())
        
    def set_url_template(self, url_template=""):
        if url_template=="":    url_template = "https://5nk8a0rfn5.execute-api.eu-west-1.amazonaws.com/v1/command?device={}&level={}&colour_x={}&colour_y={}"
        self.template_url = url_template

    def set_bulb_id(self, id):
        self.bulb_id = id

    def set_brightness(self, level):
        self.brightness = level

    def _get(self, url):
        r = requests.get(url)
        print(r.content)

    def _execute_control(self, control):
        try:
            if control=="random":
                x = random.uniform(0, 0.7) * 2**16
                y = random.uniform(0, 0.8) * 2**16
                index = random.randint(0, len(self.bulb_id_set)-1)
                bulb_id = self.bulb_id_set[index]
                brightness = random.randint(50,255)
                params = {"device": bulb_id, "level":brightness, "colour_x":x, "colour_y":y}
                url = self.template_url.format(params["device"], params["level"], params["colour_x"], params["colour_y"])
                self._get(url)

            elif control=="random-fixedBulb":
                index = random.randint(0, len(self.color_profiles)-1)
                key = self.color_proile_keys[index]
                print("Choosen color profile: ", key)
                xy_coord = self.color_profiles[key]
                (x, y) = xy_coord
                x = int(x * 2**16)
                y = int(y * 2**16)
                brightness = random.randint(100,255)
                params = {"device": self.bulb_id, "level":brightness, "colour_x":x, "colour_y":y}
                url = self.template_url.format(params["device"], params["level"], params["colour_x"], params["colour_y"])
                self._get(url)

            elif control=="random-knownColors":
                index = random.randint(0, len(self.color_profiles)-1)
                key = self.color_proile_keys[index]
                #print("Choosen color profile: ", key)
                xy_coord = self.color_profiles[key]
                (x, y) = xy_coord
                x = int(x * 2**16)
                y = int(y * 2**16)
                index = random.randint(0, len(self.bulb_id_set)-1)
                bulb_id = self.bulb_id_set[index]
                brightness = random.randint(100,255)
                params = {"device": bulb_id, "level":brightness, "colour_x":x, "colour_y":y}
                url = self.template_url.format(params["device"], params["level"], params["colour_x"], params["colour_y"])
                self._get(url)
                
            elif control in self.color_proile_keys:
                print(True)
                self._execute_colors(control)
            
        except Exception as ex:
            print(ex)


    def _execute_colors(self, control):
        x, y = self.get_color_coord(control)
        f = self.set_color

        for b in self.bulb_id_set:
            args= (b, x, y,)
            t = threading.Thread(target= f, args=(b, x, y))
            #t = threading.Thread(target= self.test_worker, args=(b,))
            self.threads.append(t)
            t.start()
            
    def test_worker(self, id):    
        print("Before", id)
        time.sleep(1)
        print("After", id)

    def get_color_coord(self, color):
        xy_coord = self.color_profiles[color]
        return xy_coord

    def set_color(self, bulb_id, x, y):
        x = int(x * 2**16)
        y = int(y * 2**16)
        params = {"device": bulb_id, "level": self.brightness, "colour_x": x, "colour_y": y}
        url = self.template_url.format(params["device"], params["level"], params["colour_x"], params["colour_y"])
        self._get(url)

    def turn_off(self, bulb_id):
        x,y=(0,0)
        self.set_color(bulb_id, x, y)

    def turn_on(self, bulb_id):
        x,y = self.get_color_coord("white")
        self.set_color(bulb_id, x, y)

if __name__ == '__main__':
    bc = BulbControl([0, 3, 8])
    """
    for b in range(0,3):
        bc._execute_control("random-fixedBulb")
        time.sleep(2)
    """
    bc._execute_control("red")    
    