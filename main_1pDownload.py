import re

class Main:
    def __init__(self):
        pass

    def build_tests(self, mainapp):
        self.tests = ["Secure_UBoot", 'Set_Env', 'Eeprom', 'Run_BootNet', 'ID']

        if mainapp.gaSet['uut_opt'] != 'ETX':
            self.tests += ['MicroSD']

        self.tests += 'SOC_Flash_Memory', 'SOC_i2C', 'Front_Panel_Leds'

        mainapp.start_from_combobox(self.tests, self.tests[0])
