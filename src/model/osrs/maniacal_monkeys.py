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


class OSRSManiacalMonkeys(OSRSBot, launcher.Launchable):
    def __init__(self):
        bot_title = "ManiacalMonkeys"
        description = "ManiacalMonkeys"
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
        start_point = 0

        while True:
            boulder = self._get_boulder()
            if not boulder:
                time.sleep(3)
                continue
            self.mouse.move_to(boulder.random_point())
            text = self._check_text()
            # if check, drop tail
            if text == "check":
                self.mouse.click()
                time.sleep(3)
                self._drop_tail()
            ind = self._get_banana(start_point)
            start_point = ind
            time.sleep(0.6)
            self.mouse.move_to(boulder.random_point())
            self.mouse.click()
            time.sleep(3)

        self.log_msg("Finished.")
        self.stop()

    def _get_boulder(self):
        return self.get_nearest_tag(clr.PINK)

    def _check_text(self):
        text = self.mouseover_text()
        if "Check" in text:
            return "check"
        return "trap"

    def _drop_tail(self):
        return self.drop([0])

    def _get_banana(self, start_point):
        return self.find_in_inv(contains="Empty", start_point=start_point)
