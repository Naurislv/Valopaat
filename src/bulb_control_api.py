#!/usr/bin/python3.5

import asyncio
import aiohttp
import json
import logging
import time
import sys
import random
import traceback
import ssl
import copy

LOGLEVEL_BulbControl = logging.INFO

class BulbControl(object):
    def __init__(self, name="BulbControl"):
        self.bulb_id            = 8
        self.brightness         = 150
        self.params             = {}
        self._loop              = None
        self.template_url       = ""
        self.buld_id_set        = [0,3,8]
        self._logger            = logging.getLogger(name)
        self._logger.setLevel(LOGLEVEL_BulbControl)
        self._logger.info("Initiating BulbControl API")
        self._initialize()

    def _initialize(self):
        self.set_url_template()
        self.color_profiles = {"red":(0.63, 0.3), "blue":(0.1, 0.2), "green": (0.18, 0.70), "white":(0.3, 0.3), \
                               "pink":(0.48, 0.23), "purple":(0.32, 0.1), "yellow":(0.42, 0.50), "orange":(0.42, 0.42)}
        
        self.color_proile_keys = list(self.color_profiles.keys())
        
    def set_url_template(self, url_template=""):
        if url_template=="":
            url_template = "https://5nk8a0rfn5.execute-api.eu-west-1.amazonaws.com/v1/command?"
            
        self.template_url = url_template

    def _connect(self):
        try:
            tcp_conn             = aiohttp.TCPConnector(loop=self._loop)
            self.control_session = aiohttp.ClientSession(connector=tcp_conn)
        except Exception as ex:
            self._logger.error("Failure initiating the bulb control client")
            self._logger.error(ex)

    def close(self):
        self.control_session.close()

    def set_bulb_id(self, id):
        self.bulb_id = id

    def check_bulb_id_validity(self, id):
        bulb_id = int(id)
        if bulb_id in [0,3,8]:
            return True
        return False
        
    @asyncio.coroutine
    def get(self, params=None, timeout=2):
        with aiohttp.Timeout(timeout):
            resp = None                                     # To handles issues related to connectivity with url
            try:
                resp = yield from self.control_session.get(self.template_url, params=params) 
                bulb_resp = yield from resp.text()
                print(bulb_resp)
                return bulb_resp
                
            except Exception as ex:
                # .close() on exception.
                if resp!=None:
                    resp.close()
                self._logger.error(ex)
            finally:
                if resp!=None:
                    yield from resp.release()               # .release() - returns connection into free connection pool.

    def execute_controls(self, control):
        self._loop = asyncio.get_event_loop()
        self._connect()
        self.execute_control(control)
    
    def execute_control(self, control):
        try:
            if control=="random":
                x = random.uniform(0, 0.7) * 2**16
                y = random.uniform(0, 0.8) * 2**16
                index = random.randint(0, len(self.bulb_id_set)-1)
                bulb_id = self.buld_id_set[index]
                brightness = random.randint(50,255)
                params = {"device": bulb_id, "level":brightness, "colour_x":x, "colour_y":y}
                self._loop.run_until_complete(self.get(params=params))

            elif control=="random-fixedBulb":
                index = random.randint(0, len(self.color_profiles)-1)
                key = self.color_proile_keys[index]
                #print("Choosen color profile: ", key)
                xy_coord = self.color_profiles[key]
                (x, y) = xy_coord
                x = int(x * 2**16)
                y = int(y * 2**16)
                brightness = random.randint(100,255)
                params = {"device": self.bulb_id, "level":brightness, "colour_x":x, "colour_y":y}
                self._loop.run_until_complete(self.get(params=params))

            elif control=="random-knownColors":
                index = random.randint(0, len(self.color_profiles)-1)
                key = self.color_proile_keys[index]
                #print("Choosen color profile: ", key)
                xy_coord = self.color_profiles[key]
                (x, y) = xy_coord
                x = int(x * 2**16)
                y = int(y * 2**16)
                index = random.randint(0, len(self.bulb_id_set)-1)
                bulb_id = self.buld_id_set[index]
                brightness = random.randint(100,255)
                params = {"device": bulb_id, "level":brightness, "colour_x":x, "colour_y":y}
                self._loop.run_until_complete(self.get(params=params))

            elif control=="red":
                self._loop.run_until_complete(self.execute_color_red())
            elif control=="green":
                self._loop.run_until_complete(self.execute_color_green())
            elif control=="blue":
                self._loop.run_until_complete(self.execute_color_blue())
            elif control=="white":
                self._loop.run_until_complete(self.execute_color_white())
            elif control=="green":
                self._loop.run_until_complete(self.execute_color_green())
            elif control=="on":
                self._loop.run_until_complete(self.turn_on())
            elif control=="off":
                self._loop.run_until_complete(self.turn_off())
        except Exception as ex:
            print(ex)
        finally:
            self.close()
            self._loop.close()

    @asyncio.coroutine                
    def execute_color_red(self):
        params = {}
        params["device"] = self.bulb_id           # 0,3,8
        params["level"] = self.brightness                     # 0-255        brightness
        params["colour_x"] = 1900000              # 0-1931
        params["colour_y"] = 1900000              # 0-1931
        yield from self.get(params)

    @asyncio.coroutine                
    def execute_color_green(self):
        params = {}
        params["device"] = self.bulb_id           # 0,3,8
        params["level"] = self.brightness                     # 0-255        brightness
        params["colour_x"] = 6000              # 0-1931
        params["colour_y"] = 52000              # 0-1931
        yield from self.get(params)

    @asyncio.coroutine                
    def execute_color_white(self):
        params = {}
        params["device"] = self.bulb_id            # 0,3,8
        params["level"] = self.brightness              # 0-255        brightness
        params["colour_x"] = 19000              # 0-1931
        params["colour_y"] = 19000              # 0-1931
        yield from self.get(params)

    @asyncio.coroutine                
    def execute_color_blue(self):
        params = {}
        params["device"] = self.bulb_id            # 0,3,8
        params["level"] = self.brightness              # 0-255        brightness
        params["colour_x"] = 190              # 0-1931
        params["colour_y"] = 190              # 0-1931
        yield from self.get(params)

    @asyncio.coroutine                
    def turn_off(self):
        params = {}
        params["device"] = self.bulb_id            # 0,3,8
        params["level"] = 0              # 0-255        brightness
        params["colour_x"] = 0              # 0-1931
        params["colour_y"] = 0              # 0-1931
        yield from self.get(params)

    @asyncio.coroutine                
    def turn_on(self):
        yield from self.execute_color_white()

if __name__ == '__main__':
    bc = BulbControl()
    #bc.execute_controls("blue")
    bc.execute_controls("random-fixedBulb")

    
