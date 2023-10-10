import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class OSRSMyCombat(OSRSBot):
    def __init__(self):
        bot_title = "My Combat"
        description = "Combat script made by Mattie."
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 1
        self.api_m = MorgHTTPSocket()
        # self.api_s = StatusSocket()

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_text_edit_option("text_edit_example", "Text Edit Example", "Placeholder text here")
        self.options_builder.add_checkbox_option("multi_select_example", "Multi-select Example", ["A", "B", "C"])
        self.options_builder.add_dropdown_option("menu_example", "Menu Example", ["A", "B", "C"])

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "text_edit_example":
                self.log_msg(f"Text edit example: {options[option]}")
            elif option == "multi_select_example":
                self.log_msg(f"Multi-select example: {options[option]}")
            elif option == "menu_example":
                self.log_msg(f"Menu example: {options[option]}")
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        # set food to use
        food_id = ids.ANGLERFISH

        while True:
            # check hp
            self._check_hp(food_id)

            # check xp (close to 99?)
            self._check_xp()

            # check in combat (animation?)
            in_combat = self.api_m.get_is_in_combat()

            # check for closest crab and atk
            if in_combat:
                self.log_msg("Already in combat..")
            else:
                self._attack_crab()

            # wait 30-60sec?
            time.sleep(rd.fancy_normal_sample(5, 10))

        self.stop()

    def _check_hp(self, food_id):
        self.log_msg("Checking hp..")
        currHP = self.api_m.get_hitpoints()[0]
        if currHP < 25:
            food_location = self.api_m.get_first_occurrence(food_id)
            food_point = self.win.inventory_slots[food_location].random_point()
            self.mouse.move_to(food_point)
            self.mouse.click()
            self.log_msg("Ate food")

    def _check_xp(self):
        self.log_msg("Checking xp..")
        xp_99 = 13034431
        xp_diff = xp_99 - 10000
        atk_xp = self.api_m.get_skill_xp("Attack")
        hp_xp = self.api_m.get_skill_xp("Hitpoints")
        if atk_xp > xp_diff or hp_xp > xp_diff:
            self.log_msg("Nearing max xp! Stopping script..")
            self.stop()

    def _attack_crab(self):
        nearest_crab = self.get_nearest_tagged_NPC()
        if not nearest_crab:
            return self.log_msg("Failed to find crab..")
        self.mouse.move_to(nearest_crab.random_point())
        self.mouse.click()
        self.log_msg("Attacking crab..")
