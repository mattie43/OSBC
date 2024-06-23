import time
import random
import string
import pyautogui
import pathlib
import keyboard
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.ocr as ocr
import utilities.game_launcher as launcher
import utilities.helpers as helpers
import utilities.runelite_cv as rcv
from model.osrs.osrs_bot import OSRSBot
from utilities.geometry import Point, Rectangle


class OSRSTitheFarm(OSRSBot, launcher.Launchable):
    def __init__(self):
        bot_title = "TitheFarm"
        description = "TitheFarm"
        super().__init__(bot_title=bot_title, description=description)

    def create_options(self):
        None

    def save_options(self, options: dict):
        None

    def launch_game(self):
        settings = pathlib.Path(__file__).parent.joinpath("custom_settings.properties")
        launcher.launch_runelite(
            properties_path=settings,
            game_title=self.game_title,
            use_profile_manager=True,
            profile_name="osbc-profile",
            callback=self.log_msg,
        )
        pass

    def _click_color(self, color):
        obj = self.get_nearest_tag(color)
        if obj:
            self.mouse.move_to(obj.random_point())
            self.mouse.click()
            return True
        return False

    # # # # MAIN_LOOP # # # #

    def main_loop(self):
        water_count = 0

        while True:
            pink = self.get_nearest_tag(clr.PINK)
            if pink:
                self._click_plant(pink)
                time.sleep(3)
                water_count += 1
                continue
            orange = self.get_nearest_tag(clr.ORANGE)
            if orange:
                self._plant_seed(orange)
                time.sleep(3)
                continue
            if water_count > 20:
                self._fill_water()
                water_count = 0
            time.sleep(3)

        self.log_msg("Finished.")
        self.stop()

    def _plant_seed(self, obj):
        self.click_inv_slots([0])
        self.mouse.move_to(obj.random_point())
        self.mouse.click()

    def _click_plant(self, obj):
        self.mouse.move_to(obj.random_point())
        self.mouse.click()

    def _fill_water(self):
        self.click_inv_slots([1])
        self._click_color(clr.RED)
        time.sleep(5)
