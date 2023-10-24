import time
import random

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
import utilities.game_launcher as launcher
import pathlib
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject


class OSRSSandCrabs(OSRSBot, launcher.Launchable):
    def __init__(self):
        bot_title = "Sand Crabs"
        description = "Combat script made for sand crabs in Crabclaw Caves."
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1
        self.api_m = MorgHTTPSocket()
        # self.api_s = StatusSocket()
        self.food_choice = ids.ANGLERFISH
        self.camera_movement = 1

    def create_options(self):
        # self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        # self.options_builder.add_text_edit_option("text_edit_example", "Text Edit Example", "Placeholder text here")
        # self.options_builder.add_checkbox_option("multi_select_example", "Multi-select Example", ["A", "B", "C"])
        self.options_builder.add_dropdown_option("food_choice", "Food choice", ["ANGLERFISH", "MANTA_RAY"])

    def save_options(self, options: dict):
        for option in options:
            if option == "food_choice":
                self.log_msg(f"Food choice: {options[option]}")
                self.food_choice = getattr(ids, options[option])
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg("Options set successfully.")
        self.options_set = True

    def launch_game(self):
        settings = pathlib.Path(__file__).parent.parent.joinpath("custom_settings.properties")
        launcher.launch_runelite(
            properties_path=settings,
            game_title=self.game_title,
            use_profile_manager=True,
            profile_name="mattie-profile",
            callback=self.log_msg,
        )
        pass

    def main_loop(self):
        while True:
            in_combat = self._combat_check()

            if not in_combat:
                self._check_hp()
                self._check_xp()
                self._reset_aggro()

        self.stop()

    def _check_hp(self):
        currHP = self.api_m.get_hitpoints()[0]
        if currHP < 25:
            food_location = self.api_m.get_first_occurrence(self.food_id)
            food_point = self.win.inventory_slots[food_location].random_point()
            self.mouse.move_to(food_point)
            self.mouse.click()
            self.log_msg("Food eaten..")

    def _check_xp(self):
        xp_99 = 13034431
        xp_diff = xp_99 - 30000
        atk_xp = self.api_m.get_skill_xp("Attack")
        hp_xp = self.api_m.get_skill_xp("Hitpoints")
        if atk_xp > xp_diff or hp_xp > xp_diff:
            self.log_msg("Nearing max xp! Stopping script..")
            self.stop()

    def _combat_check(self, attempt=1):
        if attempt > 3:
            return False

        time.sleep(8)
        in_combat = self.api_m.get_is_in_combat()
        if not in_combat:
            return self._combat_check(attempt=attempt + 1)

        return True

    def _reset_aggro(self):
        for x in range(4):
            sqs = self._find_sqs(x + 1)
            self._walk_to(sqs)
        self.log_msg("Aggro reset..")

    def _find_sqs(self, step_num):
        step_dict = {1: clr.PINK, 2: clr.CYAN, 3: clr.PINK, 4: clr.GREEN}

        for x in range(3):
            sqs = self.get_all_tagged_in_rect(self.win.game_view, step_dict[step_num])
            if sqs:
                return sqs
            else:
                self.move_camera(horizontal=self.camera_movement)
                self.camera_movement = self.camera_movement * -1
                time.sleep(0.5)

        self.log_msg(f"Failed to find step: {step_num}")
        self.stop()

    def _walk_to(self, sqs):
        sq_point = random.choice(sqs).random_point()
        self.mouse.move_to(sq_point)
        self.mouse.click()
        time.sleep(0.6)

        prev_player_idle = None

        while True:
            player_idle = self.api_m.get_is_player_idle()
            if player_idle and prev_player_idle:
                break
            prev_player_idle = player_idle
            time.sleep(0.7)
