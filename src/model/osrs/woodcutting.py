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
from model.osrs.osrs_bot import OSRSBot
from utilities.geometry import Point, Rectangle
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSWoodcutting(OSRSBot, launcher.Launchable):
    def __init__(self):
        bot_title = "Woodcutting"
        description = "Woodcutting"
        super().__init__(bot_title=bot_title, description=description)
        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()

    def create_options(self):
        None
        # self.options_builder.add_dropdown_option("course", "Rooftop Course", ["seers"])

    def save_options(self, options: dict):
        None
        # self.course = options["course"]
        # self.log_msg("Options set successfully.")
        # self.options_set = True

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

    def _set_camera(self):
        # cam = self.api_m.get_camera_position()
        # self.move_camera(vertical=-10)
        self.set_compass_north()
        self.move_camera(vertical=90)

    def _click_color(self, color):
        obj = self.get_nearest_tag(color)
        if obj:
            self.mouse.move_to(obj.random_point())
            self.mouse.click()
            return True
        return False

    def _wait_for_xp_or_fail(self):
        xp_dmg = self.api_m.wait_til_gained_xp_or_damage(skill="Agility")
        # -2 == took dmg
        if xp_dmg == -2:
            time.sleep(0.5)
            return False
        return True

    def _run_back(self):
        None

    def _idle_loop(self):
        time.sleep(1.2)
        while True:
            player_idle = self.api_m.get_is_player_idle()
            if player_idle:
                break
            time.sleep(0.6)

    def _inv_check(self):
        inv_full = "Yourinventoryistoofulltoholdanymoreteaklogs"
        chat_text = self.chatbox_text()[-55:-1]
        if inv_full in chat_text:
            return True
        return False

    # # # # MAIN_LOOP # # # #

    def main_loop(self):
        # self._set_camera()

        while True:
            self._click_color(clr.PINK)
            time.sleep(3)
            while self.is_player_doing_action("Woodcutting"):
                time.sleep(1.2)
            if self._inv_check():
                self.drop_all()
                # keyboard.write(" ")
                # keyboard.press_and_release("enter")

        self.log_msg("Finished.")
        self.stop()

    # # # # # #
    def __get_player_position(self):
        box = Rectangle(left=self.win.game_view.get_top_left()[0], top=self.win.game_view.get_top_left()[1], width=150, height=50)
        extracted = ocr.extract_text(box, ocr.PLAIN_12, [clr.OFF_WHITE], exclude_chars=self.filtered_ascii)
        result = tuple(int(item) for item in extracted.split(","))
        return result

    def __get_pixel_color(self, x: int, y: int):
        pixel_color = pyautogui.screenshot().getpixel((x, y))
        return pixel_color
