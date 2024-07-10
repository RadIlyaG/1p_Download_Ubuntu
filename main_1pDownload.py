import re
import time

import lib_gen_1pDownload as lib_gen

class Main:
    def __init__(self):
        self.tests = []

    def build_tests(self, mainapp):
        test_names_lst = []
        test_names_lst = ["Secure_UBoot"]
        test_names_lst= ['Set_Env', 'Eeprom', 'Run_BootNet', 'ID']

        if mainapp.gaSet['uut_opt'] != 'ETX':
            test_names_lst += ['MicroSD']

        test_names_lst += 'SOC_Flash_Memory', 'SOC_i2C', 'Front_Panel_Leds'

        ind = 1
        for te in test_names_lst:
            self.tests.append(f'{ind}..{te}')
            ind += 1
        print(f'Tests.AllTests.test_names_lst:{self.tests}')

        mainapp.start_from_combobox(self.tests, self.tests[0])

    def Set_Env(self, mainapp):
        gen = lib_gen.Gen()
        gen.power("1", "0")
        time.sleep(4)
        gen.power("1", "1")

        com = mainapp.gaSet['comDut']
        ser = lib_gen.RLCom(com)
        res = ser.open()
        if res is False:
            mainapp.gaSet['fail'] = f'Open COM {com} Fail'
            return -1

        res = -1
        for i in range(1,21):
            res = ser.send('\r', 'PCPE>>', 1)
            print(f'{i} Set_Env res: <{res}>')
            if res == 0:
                break
            time.sleep(1.0)

        if res == -1:
            mainapp.gaSet['fail'] = "Can't get PCPE prompt"
            ser.close()
            return -1

        ser.send('printenv\r', "PCPE>>")
        ser.send('setenv serverip 10.10.10.1\r', "PCPE>>")
        ser.send(f'setenv ipaddr   10.10.10.1{mainapp.gaSet['gui_num']}\r', "PCPE>>")
        ser.send('setenv gatewayip 10.10.10.1\r', "PCPE>>")
        ser.send('setenv netmask 255.255.255.0\r', "PCPE>>")

        ser.close()

        return 0
