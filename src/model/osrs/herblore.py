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


class OSRSHerblore(OSRSBot, launcher.Launchable):
    def __init__(self):
        bot_title = "Herblore"
        description = "Herblore"
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
        while True:
            self._click_color(clr.ORANGE)
            time.sleep(0.6)
            self._click_color(clr.RED)
            self._click_color(clr.GREEN)
            self._click_color(clr.PURPLE)
            time.sleep(0.2)
            keyboard.press_and_release("esc")
            time.sleep(0.6)
            self.click_inv_slots([13, 14])
            time.sleep(0.8)
            keyboard.press_and_release("space")
            time.sleep(random.randint(17, 19))

        self.log_msg("Finished.")
        self.stop()
