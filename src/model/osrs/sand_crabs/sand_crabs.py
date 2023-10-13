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
        settings = pathlib.Path(__file__).parent.joinpath("custom_settings.properties")
        launcher.launch_runelite(
            properties_path=settings,
            game_title=self.game_title,
            use_profile_manager=True,
            profile_name="OSBCSandCrabs",
            callback=self.log_msg,
        )
        pass

    def main_loop(self):
        while True:
            # check hp
            self._check_hp()

            # check xp (close to 99?)
            self._check_xp()

            # check for combat reset
            self._combat_check()

        self.stop()

    def _check_hp(self):
        self.log_msg("Checking hp..")
        currHP = self.api_m.get_hitpoints()[0]
        if currHP < 25:
            food_location = self.api_m.get_first_occurrence(self.food_id)
            food_point = self.win.inventory_slots[food_location].random_point()
            self.mouse.move_to(food_point)
            self.mouse.click()
            self.log_msg("Ate food")

    def _check_xp(self):
        self.log_msg("Checking xp..")
        xp_99 = 13034431
        xp_diff = xp_99 - 30000
        atk_xp = self.api_m.get_skill_xp("Attack")
        hp_xp = self.api_m.get_skill_xp("Hitpoints")
        if atk_xp > xp_diff or hp_xp > xp_diff:
            self.log_msg("Nearing max xp! Stopping script..")
            self.stop()

    def _combat_check(self, attempt=1):
        if attempt > 3:
            return self._reset_aggro()

        time.sleep(8)
        in_combat = self.api_m.get_is_in_combat()
        if in_combat:
            self.log_msg("In combat already..")
        else:
            self._combat_check(attempt=attempt + 1)

    def _reset_aggro(self, step=1):
        if step > 4:
            return self.log_msg("Last step taken..")

        step_dict = {1: clr.PINK, 2: clr.CYAN, 3: clr.PINK, 4: clr.GREEN}
        sqs = self.get_all_tagged_in_rect(self.win.game_view, step_dict[step])

        if not sqs:
            self.log_msg(f"Failed to find step: {step}")
            self.stop()

        self.mouse.move_to(random.choice(sqs).random_point())
        self.mouse.click()
        time.sleep(9)
        self._reset_aggro(step=step + 1)
