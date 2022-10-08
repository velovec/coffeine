#!/usr/bin/env python3

import json
import os.path
import logging

from pynput import mouse, keyboard
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import random
import time

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)

    dc = ImageDraw.Draw(image)

    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)

    return image


DISABLED_ICON = create_image(64, 64, 'black', 'white')
ENABLED_ICON = create_image(64, 64, 'green', 'white')


class Coffeine:

    enabled = False

    def __init__(self, scenario_path):
        self.icon = Icon("coffeine", DISABLED_ICON, "Coffeine v0.1", menu=Menu(
            MenuItem("Enabled", self.toggle, checked=lambda item: self.enabled)
        ))
        self.icon.run_detached()
        self.type_handlers = {}

        if not os.path.exists(scenario_path) or not os.path.isfile(scenario_path):
            raise ValueError("Scenario file doesn't exists!")

        with open(scenario_path) as scenario_file:
            self.scenario = json.load(scenario_file)

    def toggle(self, item):
        self.enabled = not self.enabled

        self.icon.icon = ENABLED_ICON if self.enabled else DISABLED_ICON
        logging.info("Coffeine enabled" if self.enabled else "Coffeine disabled")

    def tick(self):
        item = random.choice(self.scenario['items'])
        if item['type'] in self.type_handlers.keys():
            self.type_handlers[item['type']](item['parameters'])
            logging.info(f"Executing '{item['type']}'")
        else:
            logging.warning(f"Scenario item type {item['type']} is not available!")

    def run(self):
        logging.info("Coffeine started")
        try:
            while True:
                if self.enabled:
                    self.tick()

                time.sleep(random.uniform(
                    self.scenario['min_tick_duration'],
                    self.scenario['max_tick_duration'],
                ))
        except KeyboardInterrupt:
            self.icon.stop()

    def handler(self, type_name):
        def decorator(func):
            def wrapper(params):
                func(params)

            self.type_handlers[type_name] = wrapper

            return wrapper

        return decorator


if __name__ == "__main__":
    cf = Coffeine("scenario.json")

    mc = mouse.Controller()
    kc = keyboard.Controller()

    @cf.handler("random_mouse")
    def random_mouse(params):
        x, y = random.randint(-200, 200), random.randint(-200, 200)
        mc.move(x, y)  # Relative move

        click_allowed = [x for x in params['click'].keys() if params['click'][x]]
        if (len(click_allowed) > 0) and (1 - random.uniform(0, 1) > .4):
            click_button = random.choice(click_allowed)

            mc.click(getattr(mouse.Button, click_button), 1)

        if params['scroll'] and (1 - random.uniform(0, 1) > .6):
            mc.scroll(0, random.randint(1, 10))


    @cf.handler("window_change")
    def window_change(params):
        for i in range(1, params["max_change"]):
            with kc.pressed(keyboard.Key.alt_l):
                kc.press(keyboard.Key.tab)
                time.sleep(0.3)
                kc.release(keyboard.Key.tab)

    cf.run()
