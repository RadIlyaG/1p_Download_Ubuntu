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

        print(f'\n{gen.my_time()} ENV before set')
        ser.send('printenv\r', "PCPE>>")
        ser.send('setenv serverip 10.10.10.1\r', "PCPE>>")
        ser.send(f'setenv ipaddr   10.10.10.1{mainapp.gaSet['gui_num']}\r', "PCPE>>")
        ser.send('setenv gatewayip 10.10.10.1\r', "PCPE>>")
        ser.send('setenv netmask 255.255.255.0\r', "PCPE>>")

        dtb_sh = ''
        dtb_file = ''
        ma = re.search(r'REV([\d\.]+)\w', mainapp.gaSet['main_pcb'])
        main_pc_rev = float(ma.group(1))
        if mainapp.gaSet['uut_opt'] == 'ETX':
            dtb_sh = 'set_etx1p'
            dtb_file = '/boot/armada-3720-Etx1p.dtb'
        else:
            if re.search('/HL', mainapp.gaSet['dbr_name']):
                dtb_sh = 'set_sf1p_superset_hl'
                dtb_file = '/boot/armada-3720-SF1p_superSet_hl.dtb'
            elif mainapp.gaSet['wanPorts'] == '2U':
                dtb_sh = 'set_sf1p'
                dtb_file = '/boot/armada-3720-SF1p.dtb'
            elif main_pc_rev < 0.6:
                dtb_sh = 'set_sf1p_superset'
                dtb_file = '/boot/armada-3720-SF1p_superSet.dtb'
            elif main_pc_rev >= 0.6:
                dtb_sh = 'set_sf1p_superset_cp2'
                dtb_file = '/boot/armada-3720-SF1p_superSet_cp2.dtb'
        print(f'dtb_sh:{dtb_sh} dtb_file:{dtb_file}')

        if True:
            ser.send(f'setenv fdt_name {dtb_file}\r', "PCPE>>")
            ser.send(f'setenv bootcmd "run bootEmmc"\r', "PCPE>>")
            ser.send(f'saveenv\r', "PCPE>>", 15)
        else:
            ser.send(f'run {dtb_sh}\r', "PCPE>>")
            if 'Error: "set_sf1p_superset_cp2" not defined' in ser.buffer:
                mainapp.gaSet['fail'] = '"set_sf1p_superset_cp2" not defined'
                ser.close()
                return -1
            
        gui_num = mainapp.gaSet['gui_num']
        ser.send(f'setenv eth1addr 00:55:82:11:21:{gui_num}{gui_num}\r', "PCPE>>")

        ser.send(f'setenv ethact neta@40000\r', "PCPE>>")
        ser.send(f'setenv NFS_VARIANT general\r', "PCPE>>")
        ser.send(f'setenv config_nfs "setenv NFS_DIR /srv/nfs/pcpe-general"\r', "PCPE>>")

        ser.send(f'setenv set_bootnetargs "setenv bootargs console=ttyMV0,115200 earlycon=ar3700_uart,0xd0012000 '
                 f'root=/dev/nfs rw rootwait rootfstype=nfs '
                 f'ip=$ipaddr:$serverip:$gatewayip:$netmask:$hostname:lan0:none '
                 f'nfsroot=$serverip:/srv/nfs/pcpe-general,vers=2,tcp= $NFS_TYPE"\r', "PCPE>>")
        ser.send(f'saveenv\r', "PCPE>>", 15)

        print(f'\n{gen.my_time()} ENV after set\n')
        ser.send('printenv\r', "PCPE>>")

        ret = ser.send('ping 10.10.10.1\r', "is alive")
        if ret != 0:
            time.sleep(2)
            ret = ser.send('ping 10.10.10.1\r', "is alive")
            if ret != 0:
                mainapp.gaSet['fail'] = "Ping to 10.10.10.1 Fail"


        ser.close()

        return ret
    
    def Eeprom(self):
        gen = lib_gen.Gen()
        ret = gen.build_eeprom_string()
        return ret

