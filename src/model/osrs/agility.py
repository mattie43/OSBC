import time
import random
import string
import pyautogui
import pathlib
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.ocr as ocr
import utilities.game_launcher as launcher
import utilities.helpers as helpers
from model.osrs.osrs_bot import OSRSBot
from utilities.geometry import Point, Rectangle
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSAgility(OSRSBot, launcher.Launchable):
    def __init__(self):
        bot_title = "Rooftops"
        description = "Agility Rooftop Courses"
        super().__init__(bot_title=bot_title, description=description)

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

    def main_loop(self):
        self._set_camera()

        while True:
            tile = self._tile_check()
            if tile:
                time.sleep(1)
                self._mog_check()
                if tile["color"] == "ORANGE":
                    self._click_color(clr.GREEN)
                if tile["color"] == "GREEN":
                    self._click_color(clr.PINK)
                if tile["color"] == "PURPLE":
                    self._click_color(clr.PINK)
            time.sleep(2)

        self.log_msg("Finished.")
        self.stop()

    def _set_camera(self):
        # cam = self.api_m.get_camera_position()
        self.move_camera(vertical=90)
        self.move_camera(vertical=-10)
        self.set_compass_north()

    def _tile_check(self):
        colors = [{"color": "GREEN", "code": clr.GREEN}, {"color": "PURPLE", "code": clr.PURPLE}, {"color": "ORANGE", "code": clr.ORANGE}]

        for color in colors:
            sq = self.get_nearest_tag(color["code"])
            if sq:
                dist = sq.distance_from_rect_center()
                if dist < 25:
                    return color

        return None

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
        purp_sq = self.get_nearest_tag(clr.PURPLE)
        green_sq = self.get_nearest_tag(clr.GREEN)
        if not green_sq and not purp_sq:
            return False
        sq = green_sq if green_sq else purp_sq
        sq_point = self._point_variance(sq.center(), 15, 15)
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
            if item.distance_from_center() < 200:
                self.pick_up_loot("Mark of grace")
                time.sleep(6)

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

    def _point_variance(self, point: Point, x_variance: int = 3, y_variance: int = 3):
        if not point:
            return None
        x = point.x + random.randint(-x_variance, x_variance)
        y = point.y + random.randint(-y_variance, y_variance)
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
