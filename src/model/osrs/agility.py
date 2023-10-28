import time
import random
import string
import pyautogui

import utilities.api.item_ids as ids
from model.osrs.osrs_bot import OSRSBot
from utilities.geometry import Point, Rectangle
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import utilities.color as clr
import utilities.ocr as ocr
import utilities.game_launcher as launcher
import pathlib


class OSRSAgility(OSRSBot, launcher.Launchable):
    def __init__(self):
        bot_title = "Rooftops"
        description = "Agility Rooftop Courses"
        super().__init__(bot_title=bot_title, description=description)
        self.course = "seers"
        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()

    def create_options(self):
        self.options_builder.add_dropdown_option("course", "Rooftop Course", ["seers"])

    def save_options(self, options: dict):
        self.course = options["course"]
        self.log_msg("Options set successfully.")
        self.options_set = True

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

    def seers_course(self):
        return [
            {
                "color": clr.PINK,
                "end_coord": (2729, 3491, 3),
                "text": "Climb-up",
                "timeout": 10,
                "wait": 0.5,
            },
            {
                "color": clr.CYAN,
                "end_coord": (2713, 3494, 2),
                "text": "Jump",
                "timeout": 10,
                "wait": 0.1,
                "failed_coord": (2715, 3494, 0),
            },
            {
                "color": clr.BLUE,
                "end_coord": (2710, 3480, 2),
                "text": "Cross",
                "timeout": 10,
                "wait": 2,
                "failed_coord": (2710, 3484, 0),
            },
            {
                "color": clr.ORANGE,
                "end_coord": (2710, 3472, 3),
                "text": "Jump",
                "timeout": 10,
                "wait": 0.5,
            },
            {
                "color": clr.YELLOW,
                "end_coord": (2702, 3465, 2),
                "text": "Jump",
                "timeout": 10,
                "wait": 0.1,
            },
            {
                "color": clr.RED,
                "end_coord": (2704, 3464, 0),
                "text": "Jump",
                "timeout": 20,
                "wait": 0.1,
            },
        ]

    def _get_course(self):
        match self.course:
            case "seers":
                return self.seers_course()
            case _:
                return self.seers_course()

    def main_loop(self):
        course = self._get_course()
        self._attempts = 1

        while True:
            for index, step in enumerate(course):
                if self._click_color(step["color"]):
                    self._attempts = 1
                    if not self._wait_for_xp_or_fail():
                        break
                    time.sleep(step["wait"])
                    self._mog_check()

                if index == len(course) - 1:
                    if not self._run_back():
                        self._attempts = self._attempts + 1

                if self._attempts > 3:
                    self.log_msg("Failed 3 loops, stopping script.. ")
                    self.stop()

        self.log_msg("Finished.")
        self.stop()

    def _click_color(self, color):
        obj = self.get_nearest_tag(color)
        if obj:
            self.mouse.move_to(obj.random_point())
            self.mouse.click()
            return True
        return False

    def _wait_for_xp_or_fail(self):
        xp_dmg = self.api_m.wait_til_gained_xp_or_damage(skill="Agility")
        # took dmg
        if xp_dmg == -2:
            time.sleep(0.5)
            return False
        return True

    def _run_back(self):
        sqs = self.get_all_tagged_in_rect(self.win.game_view, clr.GREEN)
        if not sqs:
            return False
        sq_point = random.choice(sqs).random_point()
        self.mouse.move_to(sq_point)
        self.mouse.click()
        self._check_idle()
        return True

    def _check_idle(self):
        time.sleep(1.2)
        while True:
            player_idle = self.api_m.get_is_player_idle()
            if player_idle:
                break
            time.sleep(0.6)

    def _mog_check(self):
        item_text = ocr.find_text(["Mark of grace"], self.win.game_view, ocr.PLAIN_11, clr.PURPLE)
        if item_text and item_text[0]:
            item = item_text[0]
            item.set_rectangle_reference(self.win.game_view)
            if item.distance_from_center() < 100:
                self.pick_up_loot("Mark of grace")
                self._inv_check()

    def _inv_check(self):
        start_count = self.api_m.get_inv_item_stack_amount(ids.MARK_OF_GRACE)
        if not start_count:
            return time.sleep(4)

        max_loops = 20
        loops = 0

        while loops < max_loops:
            time.sleep(0.2)
            curr_count = self.api_m.get_inv_item_stack_amount(ids.MARK_OF_GRACE)
            loops += 1
            if curr_count > start_count:
                time.sleep(0.6)
                break

    def _point_variance(self, x: int, y: int, variance: int = 3):
        if not x and not y:
            return None
        x += random.randint(-variance, variance)
        y += random.randint(-variance, variance)
        return Point(x, y)

    # # # # # #
    def __get_player_position(self):
        box = Rectangle(left=self.win.game_view.get_top_left()[0], top=self.win.game_view.get_top_left()[1], width=150, height=50)
        extracted = ocr.extract_text(box, ocr.PLAIN_12, [clr.OFF_WHITE], exclude_chars=self.filtered_ascii)
        result = tuple(int(item) for item in extracted.split(","))
        return result

    def __get_pixel_color(self, x: int, y: int):
        pixel_color = pyautogui.screenshot().getpixel((x, y))
        return pixel_color
