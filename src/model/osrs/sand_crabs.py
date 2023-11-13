import time
import random
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
import utilities.game_launcher as launcher
import utilities.helpers as helpers
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
        self.running_time = 1
        self.api_m = MorgHTTPSocket()
        self.api_s = StatusSocket()
        self.food_choice = ids.ANGLERFISH
        self.camera_movement = 1

    def create_options(self):
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
        while True:
            self._combat_check()
            self._check_hp()
            # self._check_xp()
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
        if atk_xp > xp_diff:
            self.log_msg("Nearing max xp! Stopping script..")
            self.stop()

    def _combat_check(self):
        loops = 1
        max_time = 40
        while loops < max_time:
            in_combat = self.api_m.get_is_in_combat()
            if in_combat:
                loops = 1
            else:
                loops += 1
            time.sleep(0.6)

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
        helpers.call_discord(f"Failed to find step: {step_num}")
        self.stop()

    def _walk_to(self, sqs):
        sq_point = random.choice(sqs).random_point()
        self.mouse.move_to(sq_point)
        self.mouse.click()
        time.sleep(1.2)

        while True:
            player_idle = self.api_m.get_is_player_idle()
            if player_idle:
                break
            time.sleep(0.7)
