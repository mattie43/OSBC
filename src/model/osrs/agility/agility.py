import time
import random
import string
import pyautogui

from model.osrs.osrs_bot import OSRSBot
from utilities.geometry import Point, Rectangle
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
import utilities.color as clr
import utilities.ocr as ocr


class OSRSAgility(OSRSBot):
    def __init__(self):
        bot_title = "AgilityRooftops"
        description = "Agility Rooftop Courses"
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 200
        self.api_m = MorgHTTPSocket()
        # self.api_s = StatusSocket()

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        self.running_time = options["running_time"]
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def seers_course(self):
        return [
            {
                "color": clr.PINK,
                "coord": (2729, 3491, 3),
                "text": "Climb-up",
                "timeout": 10,
                "wait": 0.5,
            },
            {
                "color": clr.CYAN,
                "coord": (2713, 3494, 2),
                "text": "Jump",
                "timeout": 10,
                "wait": 0.1,
                "failed_coord": (2715, 3494, 0),
            },
            {
                "color": clr.BLUE,
                "coord": (2710, 3480, 2),
                "text": "Cross",
                "timeout": 10,
                "wait": 2,
                "failed_coord": (2710, 3484, 0),
            },
            {
                "color": clr.ORANGE,
                "coord": (2710, 3472, 3),
                "text": "Jump",
                "timeout": 10,
                "wait": 0.5,
            },
            {
                "color": clr.YELLOW,
                "coord": (2702, 3465, 2),
                "text": "Jump",
                "timeout": 10,
                "wait": 0.1,
            },
            {
                "color": clr.RED,
                "coord": (2704, 3464, 0),
                "text": "Jump",
                "timeout": 20,
                "wait": 0.1,
            },
        ]

    def main_loop(self):
        # get course from options
        course = self.seers_course()
        self._attempts = 1

        while True:
            for index, step in enumerate(course):
                if self._click_color(step["color"]):
                    if not self._wait_for_xp_or_fail():
                        break
                    time.sleep(step["wait"])
                    self._mog_check()

                if index == len(course) - 1:
                    self._run_back()

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
            if self._attempts > 3:
                self.log_msg("Couldn't find run back, stopping script.. ")
                self.stop()
            self._attempts = self._attempts + 1
            return

        self._attempts = 1
        sq_point = random.choice(sqs).random_point()
        self.mouse.move_to(sq_point)
        self.mouse.click()
        self._check_idle()

    def _check_idle(self):
        prev_player_idle = None

        while True:
            player_idle = self.api_m.get_is_player_idle()
            if player_idle and prev_player_idle:
                break
            prev_player_idle = player_idle
            time.sleep(0.6)

    def _mog_check(self):
        item_text = ocr.find_text(["Mark of grace"], self.win.game_view, ocr.PLAIN_11, clr.PURPLE)
        if item_text and item_text[0]:
            item = item_text[0]
            item.set_rectangle_reference(self.win.game_view)
            if item.distance_from_center() < 100:
                self.pick_up_loot("Mark of grace")
                time.sleep(4)

    def _point_variance(self, x: int, y: int, variance: int = 3):
        if not x and not y:
            return None
        x += random.randint(-variance, variance)
        y += random.randint(-variance, variance)
        return Point(x, y)

    # # # # # #
    def do_step(self):
        self.pre_wait()
        while self.is_coursestep():
            if self.search_object():
                break
        self.log_msg("Clicked object")
        while not self.is_step_completed():
            time.sleep(3 / 10)
        self.log_msg("Step completed")
        self.add_step()

    def search_object(self):
        self.win.run_orb
        if obj := self.get_current_tags():
            self.log_msg("Found object")
            if self.try_click(obj):
                return True
            return False

    def try_click(self, obj):
        self.mouse.move_to(obj.random_point())
        if self.is_current_mouseover():
            while not self.mouse.click(check_red_click=True):
                if obj := self.get_current_tags():
                    self.mouse.move_to(obj.random_point())
                else:
                    self.mouse.move_to(self.win.game_view.random_point())
            return True
        return False

    def find_coord_index(self):
        course = self.seers_course()
        coord = self.get_player_position()
        for index, step in enumerate(course):
            if coord == step.get("coord", []):
                self.current_step = index + 1
                return index + 1  # Adding 1 to make the index start from 1 instead of 0
        return 0

    def set_ape_atoll_course(self):
        all_ascii = string.ascii_letters + string.punctuation + "".join(ocr.problematic_chars)
        self.filtered_ascii = "".join([char for char in all_ascii if char not in "0123456789 ,"])
        self.set_course(self.seers_course())
        self.find_coord_index()

    def set_course(self, course):
        self.course = course

    def add_step(self):
        self.current_step += 1

    def get_current_step(self):
        return self.course[self.current_step]

    def get_current_color(self):
        return self.get_current_step().get("color")

    def get_current_coord(self):
        return self.get_current_step().get("coord")

    def get_current_text(self):
        return self.get_current_step().get("text")

    def get_current_wait(self):
        return self.get_current_step().get("wait", 0)

    def get_current_timeout(self):
        return self.get_current_step().get("timeout", 5000)

    def get_course(self):
        return self.course

    def get_course_steps(self):
        return len(self.course)

    def get_current_tags(self):
        return self.get_nearest_tag(self.get_current_color())

    def is_current_mouseover(self, color=clr.OFF_WHITE):
        return self.mouseover_text(self.get_current_text(), color)

    def is_coursestep(self):
        if self.current_step < self.get_course_steps():
            return True
        return False

    def set_last_run_energy(self):
        self.last_energy = self.get_run_energy()
        self.log_msg(f"Last run energy set to {self.last_energy}")

    def get_last_run_energy(self):
        if self.last_energy:
            return self.last_energy
        return 100

    def turn_on_run_energy(self):
        if self.get_last_run_energy() and self.get_last_run_energy() < self.get_run_energy() and self.get_run_energy() > 80:
            self.click_run()
        self.set_last_run_energy()

    def is_step_completed(self):
        if self.get_player_position() == self.get_current_coord():
            return True
        return False

    def get_player_position(self):
        box = Rectangle(left=self.win.game_view.get_top_left()[0], top=self.win.game_view.get_top_left()[1], width=150, height=50)
        extracted = ocr.extract_text(box, ocr.PLAIN_12, [clr.OFF_WHITE], exclude_chars=self.filtered_ascii)
        result = tuple(int(item) for item in extracted.split(","))
        return result

    def get_pixel_color(self, x: int, y: int):
        pixel_color = pyautogui.screenshot().getpixel((x, y))
        return pixel_color

    def get_pixel_run_orb(self):
        x, y = self.win.run_orb.get_center()
        self.get_pixel_color(x, y)
        return x, y

    def is_run_toggled(self):
        if self.get_pixel_run_orb() != (217, 180, 59):
            return False
        return True

    def click_run(self):
        if not self.is_run_toggled():
            while not self.mouseover_text("Toggle"):
                self.mouse.move_to(self.win.run_orb.random_point())
            self.mouse.click()
