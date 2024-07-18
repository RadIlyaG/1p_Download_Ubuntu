import re
import time

import lib_gen_1pDownload as lib_gen

class Main:
    def __init__(self, mainapp):
        self.tests = []
        self.mainapp = mainapp

    def build_tests(self):
        test_names_lst = []
        test_names_lst = ["Secure_UBoot"]
        test_names_lst= ['Set_Env']
        test_names_lst = ['Eeprom']
        test_names_lst = ['ID']
        # test_names_lst= ['Set_Env', 'Eeprom', 'Run_BootNet', 'ID']

        if self.mainapp.gaSet['uut_opt'] != 'ETX':
            test_names_lst = ['MicroSD']

        test_names_lst = 'SOC_Flash_Memory', 'SOC_i2C', 'Front_Panel_Leds'

        ind = 1
        for te in test_names_lst:
            self.tests.append(f'{ind}..{te}')
            ind += 1
        print(f'Tests.AllTests.test_names_lst:{self.tests}')

        self.mainapp.start_from_combobox(self.tests, self.tests[0])

    def Set_Env(self):
        gen = lib_gen.Gen(self.mainapp)
        gen.power("1", "0")
        time.sleep(4)
        gen.power("1", "1")

        com = self.mainapp.gaSet['comDut']
        ser = lib_gen.RLCom(com)
        res = ser.open()
        if res is False:
            self.mainapp.gaSet['fail'] = f'Open COM {com} Fail'
            return -1

        ret = -1
        for i in range(1,21):
            self.mainapp.gaSet['root'].update()
            if self.mainapp.gaSet['act'] == 0:
                    ret = -2
                    break
            ret = ser.send('\r', 'PCPE>>', 1)
            print(f'{i} Set_Env ret: <{ret}>')
            if ret == 0:
                break
            time.sleep(1.0)

        if ret == -1:
            self.mainapp.gaSet['fail'] = "Can't get PCPE prompt"

        if ret == 0:
            print(f'\n{gen.my_time()} ENV before set')
            ser.send('printenv\r', "PCPE>>")
            ser.send('setenv serverip 10.10.10.1\r', "PCPE>>")
            ser.send(f'setenv ipaddr   10.10.10.1{self.mainapp.gaSet['gui_num']}\r', "PCPE>>")
            ser.send('setenv gatewayip 10.10.10.1\r', "PCPE>>")
            ser.send('setenv netmask 255.255.255.0\r', "PCPE>>")

            dtb_sh = ''
            dtb_file = ''
            ma = re.search(r'REV([\d\.]+)\w', self.mainapp.gaSet['main_pcb'])
            main_pc_rev = float(ma.group(1))
            if self.mainapp.gaSet['uut_opt'] == 'ETX':
                dtb_sh = 'set_etx1p'
                dtb_file = '/boot/armada-3720-Etx1p.dtb'
            else:
                if re.search('/HL', self.mainapp.gaSet['dbr_name']):
                    dtb_sh = 'set_sf1p_superset_hl'
                    dtb_file = '/boot/armada-3720-SF1p_superSet_hl.dtb'
                elif self.mainapp.gaSet['wanPorts'] == '2U':
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
                
            gui_num = self.mainapp.gaSet['gui_num']
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
                    self.mainapp.gaSet['fail'] = "Ping to 10.10.10.1 Fail"


        ser.close()

        return ret
    
    def Eeprom(self):
        gen = lib_gen.Gen(self.mainapp)

        ret, ee_file_name = gen.build_eeprom_string()
        if ret == 0:
            com = self.mainapp.gaSet['comDut']
            ser = lib_gen.RLCom(com)
            ret = ser.open()
            if ret is False:
                self.mainapp.gaSet['fail'] = f'Open COM {com} Fail'
                return -1

            ret = -1
            for i in range(1,21):
                self.mainapp.gaSet['root'].update()
                if self.mainapp.gaSet['act'] == 0:
                    ret = -2
                    break
                ret = ser.send('\r', 'PCPE>>', 1)
                print(f'{i} Set_Env ret: <{ret}>')
                if ret == 0:
                    break
                time.sleep(1.0)
            if ret == -1:
                self.mainapp.gaSet['fail'] = "Can't get PCPE prompt"
                            
            if ret == 0:
                self.mainapp.status_bar_frame.status('Erasing Eeprom')
                ret = ser.send('iic e 52\r', 'PCPE>>', 20)
                print(f'Erasing Eeprom ret: <{ret}>')
                if ret == -1:
                    self.mainapp.gaSet['fail'] = "Can't get PCPE prompt"

            if ret == 0:
                self.mainapp.status_bar_frame.status('Creating Eeprom')
                ret = ser.send(f'iic c {ee_file_name}\r', 'PCPE>>', 20)
                print(f'Creating Eeprom ret: <{ret}>, ser.buffer:<{ser.buffer}>')
                if ret == -1:
                    self.mainapp.gaSet['fail'] = "Can't get PCPE prompt"
                
            if ret != 0:
                ser.close()
                return -1 
            
        return ret
    

    def ID(self):
        gen = lib_gen.Gen(self.mainapp)
        gen.power("1", "1")
        com = self.mainapp.gaSet['comDut']
        ser = lib_gen.RLCom(com)
        res = ser.open()
        if res is False:
            self.mainapp.gaSet['fail'] = f'Open COM {com} Fail'
            return -1
        
        ret = self.login(gen, ser)
        if ret == 0:
            ret = ser.send('configure system\r', "system")
            if ret != 0:
                self.mainapp.gaSet['fail'] = "Can't reach 'system'"
        
        if ret == 0:
            ret = ser.send('show device-information\r', "ngine")
            buf = re.sub(r' +', ' ', ser.buffer)
            gen.add_to_log(buf)
            if ret != 0:
                self.mainapp.gaSet['fail'] = "Can't reach 'device-information'"
            
        if ret == 0:
            ma = re.search('Sw:\s+([\d\.a-z]+)\s', ser.buffer)
            if not ma:
                self.mainapp.gaSet['fail'] = "Can't read SW"
                ret = -1

        if ret == 0:        
            uut_ver = ma.group(1)
            dbr_ver = self.mainapp.gaSet['sw_app']
            print(f'uut_ver:<{uut_ver}>, dbr_ver:<{dbr_ver}>')
            gen.add_to_log(f'SW version: {uut_ver}')

            if uut_ver != dbr_ver:
                self.mainapp.gaSet['fail'] = f"SW is {uut_ver}. Should be {dbr_ver}"
                ret = -1

        if ret == 0:
            ma = re.search('Hw:\s+([\w\.\/]+)\s?', ser.buffer)
            if not ma:
                self.mainapp.gaSet['fail'] = "Can't read HW"
                ret = -1

        if ret == 0:        
            uut_ver = float(ma.group(1))
            ma = re.search(r'REV([\d\.]+)\w', self.mainapp.gaSet['main_pcb'])
            main_pcb_rev = float(ma.group(1))
            print(f'uut_ver:<{uut_ver}>, main_pcb_rev:<{main_pcb_rev}>')
            gen.add_to_log(f'HW version: {uut_ver}')

            if uut_ver != main_pcb_rev:
                self.mainapp.gaSet['fail'] = f"HW is {uut_ver}. Should be {main_pcb_rev}"
                ret = -1

        if ret == 0:
            ma = re.search('Model[:\s]+([a-zA-Z\d\-\_\/\s]+)\s[FL]', ser.buffer)
            if not ma:
                self.mainapp.gaSet['fail'] = "Can't read Model"
                ret = -1
        if ret == 0:
            model = ma.group(1).strip()
            print(f'model:<{model}>')
            gen.add_to_log(f'Model: {model}')
            if self.mainapp.gaSet['wanPorts'] in ['4U2S', '5U1S']:
                if main_pcb_rev < 0.6 and model != 'SF-1P superset':
                    self.mainapp.gaSet['fail'] = f"The Model is '{model}'. Should be 'SF-1P superset'"
                    ret = -1
                elif main_pcb_rev >= 0.6 and model != 'SF-1P superset CP_2':
                    self.mainapp.gaSet['fail'] = f"The Model is '{model}'. Should be 'SF-1P superset CP_2'"
                    ret = -1
            elif self.mainapp.gaSet['wanPorts'] in ['2U'] and model != 'SF-1P':
                self.mainapp.gaSet['fail'] = f"The Model is '{model}'. Should be 'SF-1P'"
                ret = -1
            elif self.mainapp.gaSet['wanPorts'] in ['1SFP1UTP'] and model != 'ETX-1P':
                self.mainapp.gaSet['fail'] = f"The Model is '{model}'. Should be 'ETX-1P'"
                ret = -1

        if ret == 0:        
            ret = self.read_boot_params(gen, ser)    

        ser.close()
        return ret
    
    def login(self, gen, ser):
        if self.mainapp.gaSet['act'] == 0: return -2
        print(f'\n{gen.my_time()} Login')
        self.mainapp.status_bar_frame.status(f'Login')
        if self.mainapp.gaSet['uut_opt'] == 'ETX':
            prmt = 'ETX-1p'
        else:
            prmt = 'SF-1p'

        ret = ser.send('\r\r\r\r', "user>", 1)
        if re.search(prmt, ser.buffer):
            ser.send('exit all\r', prmt)
            return 0

        ser.send('su\r', "assword")
        ret = ser.send('1234\r', "-1p#", 3)
        if ret == "-1":
            if re.search('Login failed user', ser.buffer):
                ser.send('su\r4\r', "again", 3)
            ser.send('4\r', "again", 3)
            ret = ser.send('4\r', "-1p#", 3)
        if ret == 0:
            return 0
        
        if self.mainapp.gaSet['act'] == 0: return -2
        
        st_sec = time.time()
        max_wait = 450
        run_sec = 0
        while True:
            self.mainapp.gaSet['root'].update()
            if self.mainapp.gaSet['act'] == 0: return -2
            run_sec = self.calc_run_sec(st_sec)
            self.mainapp.status_bar_frame.run_time(run_sec)
            self.mainapp.status_bar_frame.status(f'Wait for Login ({run_sec} sec)')
            if run_sec > max_wait:
                self.mainapp.gaSet['fail'] = "Can't login"
                return -1
        
            ser.send('\r', 'user>', 1)
            if re.search('PCPE>', ser.buffer):
                ser.send('boot\r', 'stam', 2)
            if re.search(' E ', ser.buffer):
                ser.send('x\rx\r', 'stam', 2)
            if re.search('user>', ser.buffer):
                ser.send('su\r', "assword")
                ret = ser.send('1234\r', "-1p#", 3)
                if ret == "-1":
                    if re.search('Login failed user', ser.buffer):
                        ser.send('su\r4\r', "again", 3)
                    ser.send('4\r', "again", 3)
                    ret = ser.send('4\r', "-1p#", 3)
                if ret == 0:
                    break

            time.sleep(4)

        if ret != 0:
            self.mainapp.gaSet['fail'] = "Can't login"
        
        return ret
        

    def calc_run_sec(self, st_sec):
        return int(time.time() - st_sec)
    
    def read_boot_params(self, gen, ser):
        print(f'\n{gen.my_time()} Read Boot Params')
        gen.power("1", "0")
        time.sleep(4)
        gen.power("1", "1")
        res = -1
        buf = ''
        for i in range(1,21):
            self.mainapp.gaSet['root'].update()
            if self.mainapp.gaSet['act'] == 0: return -2
            res = ser.send('\r', 'PCPE>>', 1)
            buf += ser.buffer
            print(f'{i} read_boot_params res: <{res}>')
            if res == 0:
                break
            #time.sleep(1.0)

        if res == -1:
            self.mainapp.gaSet['fail'] = "Can't get PCPE prompt"
            ret = -1
        else:
            ret = 0

        if ret == 0:            
            ma = re.search(f"VER{self.mainapp.gaSet['sw_boot'][1:]}", buf)
            print(f'buf:<{buf}> ma:<{ma}>')
            gen.add_to_log(f"Boot Ver.: VER{self.mainapp.gaSet['sw_boot'][1:]}")
            if not ma:
                self.mainapp.gaSet['fail'] = f"No VER{self.mainapp.gaSet['sw_boot'][1:]} in Boot"
                ret = -1

        if ret == 0:            
            ma = re.search(r"DRAM:\s+(\d)\s+GiB", buf)
            if not ma:
                self.mainapp.gaSet['fail'] = "Can't read DRAM"
                ret = -1
        if ret == 0:
            dbr_ram = str(self.mainapp.gaSet['mem'])
            uut_ram = ma.group(1)
            gen.add_to_log(f'DRAM: {uut_ram} GiB')
            if uut_ram != dbr_ram:
                self.mainapp.gaSet['fail'] = f"DRAM is {uut_ram}. Should be {dbr_ram}"
                ret = -1

        if ret == 0:
            ser.send('printenv NFS_VARIANT\r', 'PCPE>')
            gen.add_to_log(f'{ser.buffer}')
            if not re.search('NFS_VARIANT=general', ser.buffer):
                self.mainapp.gaSet['fail'] = f"No 'NFS_VARIANT=general' in Boot"
                ret = -1
        
        if ret == 0:
            ser.send('printenv fdt_name\r', 'PCPE>')
            gen.add_to_log(f'{ser.buffer}')
            if re.search('/HL', self.mainapp.gaSet['dbr_name']):                
                if not re.search('armada-3720-SF1p_superSet_hl.dtb', ser.buffer):
                    self.mainapp.gaSet['fail'] = f"'fdt_name' is not 'armada-3720-SF1p_superSet_hl.dtb'"
                    ret = -1
        
        ser.send('boot\r', 'stam', 1)
        return ret

    def MicroSD(self):
        gen = lib_gen.Gen(self.mainapp)
        com = self.mainapp.gaSet['comDut']
        ser = lib_gen.RLCom(com)
        res = ser.open()
        if res is False:
            self.mainapp.gaSet['fail'] = f'Open COM {com} Fail'
            return -1
        
        ret = ser.send('\r', 'PCPE>>', 1)
        if ret !=0:
            gen.power("1", "0")
            time.sleep(4)
            gen.power("1", "1")
        
            for i in range(1,21):
                self.mainapp.gaSet['root'].update()
                if self.mainapp.gaSet['act'] == 0:
                    ret = -2
                    break

                ret = ser.send('\r', 'PCPE>>', 1)
                print(f'{i} MicroSD ret: <{ret}>')
                if ret == 0:
                    break
                time.sleep(1.0)

            if ret == -1:
                self.mainapp.gaSet['fail'] = "Can't get PCPE prompt"            
            
        if ret == 0:
            ser.send('mmc dev 0:1\r', 'PCPE>')
            time.sleep(0.5)
            ret = ser.send('mmc dev 0:1\r', 'PCPE>')
            if ret != 0:
                self.mainapp.gaSet['fail'] = "'mmc dev 0:1' fail"
        
        if ret == 0:
            if not re.search('switch to partitions #0, OK', ser.buffer):
                time.sleep(0.5)
                ser.send('mmc dev 0:1\r', 'PCPE>')
                if not re.search('switch to partitions #0, OK', ser.buffer):
                    self.mainapp.gaSet['fail'] = "'switch to partitions #0, OK' doesn't exist"
                    ret = -1

        if ret == 0:
            if not re.search('mmc0 is current device', ser.buffer):
                time.sleep(0.5)
                ser.send('mmc dev 0:1\r', 'PCPE>')
                if not re.search('mmc0 is current device', ser.buffer):
                    self.mainapp.gaSet['fail'] = "'mmc0 is current device' doesn't exist"
                    ret = -1

        if ret == 0:
            ser.send('mmc info\r', 'PCPE')
            time.sleep(0.5)
            ret = ser.send('mmc info\r', 'PCPE>')
            if ret != 0:
                self.mainapp.gaSet['fail'] = "'mmc info' fail"

        if ret == 0:
            gen.add_to_log(ser.buffer)
            if not re.search('Capacity: 29.7 GiB', ser.buffer):
                self.mainapp.gaSet['fail'] = "'Capacity: 29.7 GiB' doesn't exist"
                ret = -1



        ser.close()
        return ret
        

    def SOC_Flash_Memory(self):
        gen = lib_gen.Gen(self.mainapp)
        com = self.mainapp.gaSet['comDut']
        ser = lib_gen.RLCom(com)
        res = ser.open()
        if res is False:
            self.mainapp.gaSet['fail'] = f'Open COM {com} Fail'
            return -1
        
        ret = ser.send('\r', 'PCPE>>', 1)
        if ret !=0:
            gen.power("1", "0")
            time.sleep(4)
            gen.power("1", "1")
        
            for i in range(1,21):
                self.mainapp.gaSet['root'].update()
                if self.mainapp.gaSet['act'] == 0:
                    ret = -2
                    break

                ret = ser.send('\r', 'PCPE>>', 1)
                print(f'{i} SOC_Flash_Memory ret: <{ret}>')
                if ret == 0:
                    break
                time.sleep(1.0)

            if ret == -1:
                self.mainapp.gaSet['fail'] = "Can't get PCPE prompt"            
            
        if ret == 0:
            ser.send('mmc dev 1:0\r', 'PCPE>')
            time.sleep(0.5)
            ret = ser.send('mmc dev 1:0\r', 'PCPE>')
            if ret != 0:
                self.mainapp.gaSet['fail'] = "'mmc dev 1:0' fail"

        if ret == 0:
            if not re.search('switch to partitions #0, OK', ser.buffer):
                time.sleep(0.5)
                ser.send('mmc dev 1:0\r', 'PCPE>')
                if not re.search('switch to partitions #0, OK', ser.buffer):
                    self.mainapp.gaSet['fail'] = "'switch to partitions #0, OK' doesn't exist"
                    ret = -1

        if ret == 0:
            if not re.search('mmc1\(part 0\) is current device', ser.buffer):
                time.sleep(0.5)
                ser.send('mmc dev 1:0\r', 'PCPE>')
                if not re.search('mmc1\(part 0\) is current device', ser.buffer):
                    self.mainapp.gaSet['fail'] = "'mmc1(part 0) is current device' doesn't exist"
                    ret = -1

        if ret == 0:
            ser.send('mmc info\r', 'PCPE')
            time.sleep(0.5)
            ret = ser.send('mmc info\r', 'PCPE>')
            # buf = re.sub(' +', ' ', ser.buffer)
            # gen.add_to_log(buf)
            if ret != 0:
                self.mainapp.gaSet['fail'] = "'mmc info' fail"

        if ret == 0:
            gen.add_to_log(ser.buffer)
            if not re.search('HC WP Group Size: 8 MiB', ser.buffer):
                self.mainapp.gaSet['fail'] = "'HC WP Group Size: 8 MiB' doesn't exist"
                ret = -1
    
        if ret == 0:
            if not re.search('Bus Width: 8-bit', ser.buffer):
                self.mainapp.gaSet['fail'] = "'Bus Width: 8-bit' doesn't exist"
                ret = -1

        if ret == 0:
            ser.send('mmc list\r', 'PCPE')
            if ret != 0:
                self.mainapp.gaSet['fail'] = "'mmc list' fail"

        if ret == 0:
            gen.add_to_log(ser.buffer)
            if not re.search('sdhci@d0000: 0', ser.buffer):
                self.mainapp.gaSet['fail'] = "'sdhci@d0000: 0' doesn't exist"
                ret = -1
    
        if ret == 0:
            if not re.search('sdhci@d8000: 1 \(eMMC\)', ser.buffer):
                self.mainapp.gaSet['fail'] = "'sdhci@d8000: 1 (eMMC)' doesn't exist"
                ret = -1

        ser.close()
        return ret
    
    def SOC_i2C(self):
        gen = lib_gen.Gen(self.mainapp)
        com = self.mainapp.gaSet['comDut']
        ser = lib_gen.RLCom(com)
        res = ser.open()
        if res is False:
            self.mainapp.gaSet['fail'] = f'Open COM {com} Fail'
            return -1
        
        ret = ser.send('\r', 'PCPE>>', 1)
        if ret !=0:
            gen.power("1", "0")
            time.sleep(4)
            gen.power("1", "1")
        
            for i in range(1,21):
                self.mainapp.gaSet['root'].update()
                if self.mainapp.gaSet['act'] == 0:
                    ret = -2
                    break

                ret = ser.send('\r', 'PCPE>>', 1)
                print(f'{i} SOC_i2C ret: <{ret}>')
                if ret == 0:
                    break
                time.sleep(1.0)

            if ret == -1:
                self.mainapp.gaSet['fail'] = "Can't get PCPE prompt"            
            
        if ret == 0:
            ser.send('i2c bus\r', 'PCPE>')
            if ret != 0:
                self.mainapp.gaSet['fail'] = "'i2c bus' fail"

        if ret == 0:
            if not re.search('Bus 0:	i2c@11000', ser.buffer):
                self.mainapp.gaSet['fail'] = "'Bus 0:	i2c@11000' doesn't exist"
                ret = -1
        
        if ret == 0:
            ser.send('i2c dev 0\r', 'PCPE>')
            if ret != 0:
                self.mainapp.gaSet['fail'] = "'i2c dev 0' fail"

        if ret == 0:
            ser.send('i2c probe\r', 'PCPE>')
            if ret != 0:
                self.mainapp.gaSet['fail'] = "'i2c probe' fail"

        if ret == 0:
            gen.add_to_log(ser.buffer)
            if not re.search('20 21', ser.buffer):
                self.mainapp.gaSet['fail'] = "'20 21' doesn't exist"
                ret = -1

        if ret == 0:
            if not re.search('7E 7F', ser.buffer):
                self.mainapp.gaSet['fail'] = "'7E 7F' doesn't exist"
                ret = -1

        if ret == 0:
            ser.send('i2c mw 0x52 0.2 0xaa 0x1\r', 'PCPE>')
            ret = ser.send('i2c md 0x52 0.2 0x20\r', 'PCPE>')
            if ret != 0:
                self.mainapp.gaSet['fail'] = "'2ic md' fail"

        if ret == 0:
            gen.add_to_log('')
            gen.add_to_log(ser.buffer[20:60])
            if not re.search('0000: aa', ser.buffer):
                self.mainapp.gaSet['fail'] = "'0000: aa' doesn't exist"
                ret = -1

        if ret == 0:
            ser.send('i2c mw 0x52 0.2 0xbb 0x1\r', 'PCPE>')
            ret = ser.send('i2c md 0x52 0.2 0x20\r', 'PCPE>')
            if ret != 0:
                self.mainapp.gaSet['fail'] = "'2ic md' fail"

        if ret == 0:
            gen.add_to_log('')
            gen.add_to_log(ser.buffer[20:60])
            if not re.search('0000: bb', ser.buffer):
                self.mainapp.gaSet['fail'] = "'0000: bb' doesn't exist"
                ret = -1

        ser.close()
        return ret
