import os
import time
import re
from datetime import datetime
from pathlib import Path
import subprocess
import socket
import json
import webbrowser
import serial

import lib_radapps_1pDownload as radapps


class Gen:
    def __init__(self, mainapp):
        self.os = os.name
        self.hidraw = "0"
        self.mainapp = mainapp
        
    def power(self, ps, state):
        print(f'Power ps:{ps}, state:{state}')  # self:{self}, 
        
        if state == 1:
            st = 'ON'
        else:
            st = 'OFF'
        
        # p = Path('/home/ilya/usb-relay-hid/bin-linux-x64/hidusb-relay-cmd')
        # # ret = subprocess.run([p, st, str(ps)], stdout=subprocess.PIPE).stdout.decode()
        # password = '1q2w3e4r5t'
        # cmd = f'echo {password} | sudo -S {p} id=HURTM {st} {str(ps)}'
        # print(cmd)
        # p = Path('usbrelay')
        # # ret = subprocess.run([p, st, str(ps)], stdout=subprocess.PIPE).stdout.decode()
        # password = '1q2w3e4r5t'
        # cmd = f'echo {password} | sudo -S {p} HURTM_{str(ps)}={state}'
        # cmd = f'usbrelay /dev/hidraw{self.hidraw}_{str(ps)}={state}'
        cmd = f'usbrelay PWR_{str(ps)}={str(state)}'
        print(cmd)
        for i in range(1,11):
            with subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
                stdout, stderr = process.communicate()
                print(f'i:{i} stdout:<{stdout}>, stderr:<{stderr}>, {process.returncode}')
                if process.returncode == 0:
                    break
        return 0

    def gui_Power(self, ps, state):
        print(f"gui_Power self:{self},  ps:{ps}, state:{state}")
        self.power(ps, state)

    def gui_PowerOffOn(self, ps):
        self.gui_Power(ps, 0)
        time.sleep(2)
        self.gui_Power(ps, 1)
        
        
    def open_terminal(self, appwin, com_name):
        print(f'open_terminal appwin:{appwin} os:{self.os}')
        if self.os == "nt":
            com = appwin.gaSet[com_name][3:]  # COM8 -> 8 (cut off COM)
            print(f"open_teraterm com_name:{com_name}, com:{com}")

            cmd = os.path.join('C:/Program Files (x86)', 'teraterm', 'ttermpro.exe')
            cmd = str(cmd) + ' /c=' + str(com) + ' /baud=115200'
            # os.startfile(cmd)
            subprocess.Popen(cmd)
            print(cmd)
        else:
            cmd = f'minicom -D /dev/ttyUSB3 -b 115200'
            with subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
                stdout, stderr = process.communicate()
                print(f'stdout:<{stdout}>, stderr:<{stderr}>, {process.returncode}')

            
    def read_hw_init(self, gui_num, host_fld):
        print(f'\nread_hw_init, gui_num:{gui_num}, host_fld:{host_fld}')
        # host = ip.replace('.', '_')
        # woDir = os.getcwd()
        # # host_fld = ''
        # if '1p_download' in woDir:
        #     host_fld = os.path.join(woDir, host)
        # else:
        #     host_fld = os.path.join(woDir, '1p_download', host)
        # print(f'woDir:<{woDir}>host_fld:<{host_fld}>')
        Path(host_fld).mkdir(parents=True, exist_ok=True)
        hw_file = Path(os.path.join(host_fld, f"HWinit.{gui_num}.json"))
        if not os.path.isfile(hw_file):
            hw_dict = {
                'comDut': 'ttyUSB0',
                'pioBoxSerNum': "PWR",
            }
            # di = {**hw_dict, **dict2}

            with open(hw_file, 'w') as fi:
                # json.dump(hw_dict, fi, indent=2, sort_keys=True)
                json.dump(hw_dict, fi, indent=2, sort_keys=True)
        else:
            print(f'hw_file:{hw_file}')
        try:
            with open(hw_file, 'r') as fi:
                hw_dict = json.load(fi)
        except Exception as e:
            # print(e)
            # raise(e)
            raise Exception("e")

        print(f'hw_file: hw_dict{hw_dict}')
        return hw_dict

    def read_init(self, appwin, gui_num, host_fld):
        print(f'read_init, self:{self}, appwin:{appwin}, gui_num:{gui_num}, host_fld:{host_fld}')
        # print(f'read_init script_dir {os.path.dirname(__file__)}')
        # host = ip.replace('.', '_')
        Path(host_fld).mkdir(parents=True, exist_ok=True)
        ini_file = Path(os.path.join(host_fld, "init." + str(gui_num) + ".json"))
        if os.path.isfile(ini_file) is False:
            dicti = {
                'geom': '+210+210'
            }
            self.save_init(appwin)

        try:
            with open(ini_file, 'r') as fi:
                dicti = json.load(fi)
        except Exception as e:
            # print(e)
            # raise(e)
            raise Exception("e")

        print(f'read_init {ini_file} {dicti}')
        return dicti

    def save_init(self, appwin):
        print(f'save_init, self:{self}, appwin:{appwin}, {appwin.gaSet}')
        ip = appwin.gaSet['pc_ip']
        host = ip.replace('.', '_')
        gui_num = appwin.gaSet['gui_num']
        host_fld = appwin.gaSet['host_fld']
        Path(host).mkdir(parents=True, exist_ok=True)
        ini_file = Path(os.path.join(host_fld, "init." + str(gui_num) + ".json"))
        print(f'save_init host:<{host}>, pwd:<{os.getcwd()}>, ini_file:<{ini_file}>')

        di = {}
        try:
            # di['geom'] = "+" + str(dicti['root'].winfo_x()) + "+" + str(dicti['root'].winfo_y())
            geom = self.get_xy(appwin)
        except:
            geom = "+230+233"
        di['geom'] = geom
        print(f'save_init, geom:{geom}')
        try:
            with open(ini_file, 'w') as fi:
                json.dump(di, fi, indent=2, sort_keys=True)
                # json.dump(gaSet, fi, indent=2, sort_keys=True)
        except Exception as e:
            print(e)
            raise (e)

    def get_xy(self, top):
        print('get_xy', top)
        return str("+" + str(top.winfo_x()) + "+" + str(top.winfo_y()))

    # def ne_get_dbr_name(self, id_number):
    #     ws = radapps.WebServices()
    #     ws.print_rtext = False
    #     res, dicti = ws.retrieve_oi4barcode(id_number)
    #     print(f'get_dbr_name res:<{res}> dicti:<{dicti}>')
    #     return res, dicti['item']

    # def ne_get_mrkt_name(self, id_number):
    #     ws = radapps.WebServices()
    #     ws.print_rtext = False
    #     res, dicti = ws.retrieve_mkt_name(id_number)
    #     print(f'get_mrkt_name res:<{res}> dicti:<{dicti}>')
    #     return res, dicti['MKT Item']

    # def ne_get_csl_name(self, id_number):
    #     ws = radapps.WebServices()
    #     ws.print_rtext = False
    #     res, dicti = ws.retrieve_csl(id_number)
    #     print(f'get_csl_name res:<{res}> dicti:<{dicti}>')
    #     return res, dicti['CSL']

    def open_history(self):
        new = 2  # open in a new tab, if possible
        url = "history.html"
        webbrowser.open(url, new=new)

    def my_time(self):
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def add_to_log(self, txt):
        with open(self.mainapp.gaSet['log'], 'a') as log:
            if txt == '':
                text = f'\n'
            else:
                text = f'{self.my_time()} {txt}\n'
            log.write(text)


    def retrive_dut_fam(self):
        print(f'\n{self.my_time()} retrive_dut_fam')
        # fields = mainapp.gaSet['dbr_name'].split('/')
        dbr_name = self.mainapp.gaSet['dbr_name'] + '/'
        print(self.mainapp.gaSet['dbr_name'], dbr_name)
        # print(f'retrive_dut_fam, {self}')

        # if 'HL' in fields:
        #     fields.remove('HL')

        sf_ma = re.search(r'([A-Z0-9\-\_]+)/E?', dbr_name)
        sf = sf_ma.group(1)
        # print(f'sf:{sf}')
        if sf in ['SF-1P', 'ETX-1P', 'SF-1P_ICE', 'ETX-1P_SFC', 'SF-1P_ANG']:
            self.mainapp.gaSet['prompt'] = '-1p#'
        elif sf == 'VB-101V':
            self.mainapp.gaSet['prompt'] = 'VB101V#'
        else:
            return f'Wrong product: {self.mainapp.gaSet["dbr_name"]}'
        # fields.remove(sf)

        if sf in ['ETX-1P', 'ETX-1P_SFC']:
            box = 'etx'
            uut_opt = 'ETX'
            ps_ma = re.search(r'1P/([A-Z0-9]+)/', dbr_name)
            if ps_ma is None:
                ps_ma = re.search(r'1P_SFC/([A-Z0-9]+)/', dbr_name)
            ps = ps_ma.group(1)
            wanPorts = "1SFP1UTP"
            lanPorts = "4UTP"
        else:
            box = re.search(r'P[_A-Z]*/(E[R\d]?)/', dbr_name).group(1)
            ps = re.search(r'E[R\d]+/([A-Z0-9]+)/', dbr_name).group(1)
            uut_opt = 'SF'

            wanPorts_ma = re.search(r'/(2U)/', dbr_name)
            if wanPorts_ma is None:
                wanPorts_ma = re.search(r'/(4U2S)/', dbr_name)
                if wanPorts_ma is None:
                    wanPorts_ma = re.search(r'/(5U1S)/', dbr_name)
            wanPorts = wanPorts_ma.group(1)
            lanPorts = "NotExists"

        self.mainapp.gaSet['box'] = box
        self.mainapp.gaSet['ps'] = ps
        self.mainapp.gaSet['uut_opt'] = uut_opt
        self.mainapp.gaSet['wanPorts'] = wanPorts
        self.mainapp.gaSet['lanPorts'] = lanPorts
        # if box in fields:
        #     fields.remove(box)
        # fields.remove(ps)
        # if wanPorts in fields:
        #     fields.remove(wanPorts)
        # if lanPorts in fields:
        #     fields.remove(lanPorts)

        serPort_ma = re.search(r'/(2RS)/', dbr_name)
        if serPort_ma is None:
            serPort_ma = re.search(r'/(2RSM)/', dbr_name)
            if serPort_ma is None:
                serPort_ma = re.search(r'/(1RS)/', dbr_name)
                if serPort_ma is None:
                    serPort_ma = re.search(r'/(2RMI)/', dbr_name)
                    if serPort_ma is None:
                        serPort_ma = re.search(r'/(2RSI)/', dbr_name)
        if serPort_ma is None:
            self.mainapp.gaSet['serPort'] = 'NotExists'
        else:
            self.mainapp.gaSet['serPort'] = serPort_ma.group(1)
        # if mainapp.gaSet['serPort'] in fields:
        #     fields.remove(mainapp.gaSet['serPort'])

        serPortCsp = re.search(r'/(CSP)/', dbr_name)
        if serPortCsp is None:
            self.mainapp.gaSet['serPortCsp'] = 'NotExists'
        else:
            self.mainapp.gaSet['serPortCsp'] = serPortCsp.group(1)
        # if mainapp.gaSet['serPortCsp'] in fields:
        #     fields.remove(mainapp.gaSet['serPortCsp'])

        self.mainapp.gaSet['poe'] = 'NotExists'
        # if mainapp.gaSet['poe'] in fields:
        #     fields.remove(mainapp.gaSet['poe'])

        self.mainapp.gaSet['plc'] = 'NotExists'
        # if mainapp.gaSet['plc'] in fields:
        #     fields.remove(mainapp.gaSet['plc'])

        self.mainapp.gaSet['cellType'] = 'NotExists'
        self.mainapp.gaSet['cellQty'] = 'NotExists'
        for cell in ['HSP', 'L1', 'L2', 'L3', 'L4', 'L450A', 'L450B', '5G', 'L4P', 'LG']:
            qty = len([i for i, x in enumerate(dbr_name.split('/')) if x == cell])
            # print(f'cell{cell}, qty:{qty}')
            if qty > 0:
                self.mainapp.gaSet['cellType'] = cell
                self.mainapp.gaSet['cellQty'] = qty
        # if mainapp.gaSet['cellType'] in fields:
        #     fields.remove(mainapp.gaSet['cellType'])
        # if mainapp.gaSet['cellType'] in fields:
        #     fields.remove(mainapp.gaSet['cellType'])

        gps = re.search(r'/(G)/', dbr_name)
        if gps is None:
            self.mainapp.gaSet['gps'] = 'NotExists'
        else:
            self.mainapp.gaSet['gps'] = gps.group(1)
        # if mainapp.gaSet['gps'] in fields:
        #     fields.remove(mainapp.gaSet['gps'])

        wifi_ma = re.search(r'/(WF)/', dbr_name)
        if wifi_ma is not None:
            self.mainapp.gaSet['wifi'] = 'WF'
        else:
            wifi_ma = re.search(r'/(WFH)/', dbr_name)
            if wifi_ma is not None:
                self.mainapp.gaSet['wifi'] = 'WH'
            else:
                wifi_ma = re.search(r'/(WH)/', dbr_name)
                if wifi_ma is not None:
                    self.mainapp.gaSet['wifi'] = 'WH'
                else:
                    self.mainapp.gaSet['wifi'] = 'NotExists'
        # if mainapp.gaSet['wifi'] in fields:
        #     fields.remove(mainapp.gaSet['wifi'])

        dryCon_ma = re.search(r'/(GO)/', dbr_name)
        if dryCon_ma is not None:
            self.mainapp.gaSet['dryCon'] = 'GO'
        else:
            self.mainapp.gaSet['dryCon'] = 'FULL'

        rg = re.search(r'/(RG)/', dbr_name)
        if rg is None:
            self.mainapp.gaSet['rg'] = 'NotExists'
        else:
            self.mainapp.gaSet['rg'] = 'RG'
        # if mainapp.gaSet['rg'] in fields:
        #     fields.remove(mainapp.gaSet['rg'])

        lora_ma = re.search(r'/(LR[1-6A-Z])/', dbr_name)
        if lora_ma is None:
            self.mainapp.gaSet['lora'] = 'NotExists'
            self.mainapp.gaSet['lora_region'] = 'NotExists'
            self.mainapp.gaSet['lora_fam'] = 'NotExists'
            self.mainapp.gaSet['lora_band'] = 'NotExists'
        else:
            lora = lora_ma.group(1)
            self.mainapp.gaSet['lora'] = lora
            if lora == 'LR1':
                self.mainapp.gaSet['lora_region'] = 'eu433'
                self.mainapp.gaSet['lora_fam'] = '4XX'
                self.mainapp.gaSet['lora_band'] = 'EU 433'
            elif lora == 'LR2':
                self.mainapp.gaSet['lora_region'] = 'eu868'
                self.mainapp.gaSet['lora_fam'] = '8XX'
                self.mainapp.gaSet['lora_band'] = 'EU 863-870'
            elif lora == 'LR3':
                self.mainapp.gaSet['lora_region'] = 'au915'
                self.mainapp.gaSet['lora_fam'] = '9XX'
                self.mainapp.gaSet['lora_band'] = 'AU 915-928 Sub-band 2'
            elif lora == 'LR4':
                self.mainapp.gaSet['lora_region'] = 'us902'
                self.mainapp.gaSet['lora_fam'] = '9XX'
                self.mainapp.gaSet['lora_band'] = 'US 902-928 Sub-band 2'
            elif lora == 'LR6':
                self.mainapp.gaSet['lora_region'] = 'as923'
                self.mainapp.gaSet['lora_fam'] = '9XX'
                self.mainapp.gaSet['lora_band'] = 'AS 923-925'
            elif lora == 'LRA':
                self.mainapp.gaSet['lora_region'] = 'us915'
                self.mainapp.gaSet['lora_fam'] = '9XX'
                self.mainapp.gaSet['lora_band'] = 'US 902-928 Sub-band 2'
            elif lora == 'LRB':
                self.mainapp.gaSet['lora_region'] = 'eu868'
                self.mainapp.gaSet['lora_fam'] = '8XX'
                self.mainapp.gaSet['lora_band'] = 'EU 863-870'
            elif lora == 'LRC':
                self.mainapp.gaSet['lora_region'] = 'eu433'
                self.mainapp.gaSet['lora_fam'] = '4XX'
                self.mainapp.gaSet['lora_band'] = 'EU 433'
        # if mainapp.gaSet['lora'] in fields:
        #     fields.remove(mainapp.gaSet['lora'])

        mem = re.search(r'/2R/', dbr_name)
        if mem is not None:
            self.mainapp.gaSet['mem'] = 2
            # fields.remove('2R')
        else:
            self.mainapp.gaSet['mem'] = 1

        plc_ma = re.search(r'/(PLC[DGO])/', dbr_name)
        if plc_ma is None:
            self.mainapp.gaSet['plc'] = 'NotExists'
        else:
            self.mainapp.gaSet['plc'] = plc_ma.group(1)

        # mainapp.gaSet['fields'] = fields

        # print(f'retrive dut fam {mainapp.gaSet}')
        # print(f'dbr_name:{dbr_name} fields:{fields}')

        return True

    def get_dbr_sw(self):
        gswv = radapps.GetSWVersions()
        id_number = self.mainapp.gaSet['id_number']
        res, sw_l = gswv.gets_sw(id_number)
        print(res, sw_l)
        if res:
            self.mainapp.gaSet['sw_boot'] = None
            self.mainapp.gaSet['sw_app'] = None
            for sw in sw_l:
                ver = sw['version']
                if ver[0] == 'B':
                    self.mainapp.gaSet['sw_boot'] = ver
                else:
                    self.mainapp.gaSet['sw_app'] = ver
                    self.mainapp.main_frame.frame_info.lab_sw_val.configure(text=ver)
            print(f'get dbr sw {self.mainapp.gaSet}')
        return res

    def play_sound(self, sound='pass.wav'):
        """ 'fail.wav' 'info.wav' 'pass.wav' 'warning.wav' """
        # with subprocess.Popen([f'aplay /home/ilya/Wav/{sound}'], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        #                  stderr=subprocess.PIPE, text=True) as process:
        #     print(f'returncode:<{process.returncode}>')
        subprocess.Popen([f'aplay /home/ilya/Wav/{sound}'], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True)
        
    def build_eeprom_string(self):
        print(f'\n{self.my_time()} Build EEprom String')

        cell_type = self.mainapp.gaSet['cellType']
        cell_qty = self.mainapp.gaSet['cellQty'] 
        wifi = self.mainapp.gaSet['wifi']
        lora = self.mainapp.gaSet['lora']

        if cell_qty == 'NotExists' and wifi == 'NotExists' and lora == 'NotExists':
            print("### #no modems, no wifi, no lora")
            mod1man = ""
            mod1type = ""
            mod2man = ""
            mod2type = ""
        elif cell_qty == 1 and wifi == 'NotExists' and lora == 'NotExists':
            print("#### just modem 1, no modem 2 and no wifi, no lora")
            mod1man = self.modem_manuf(cell_type)
            mod1type = self.modem_type(cell_type, lora)
            mod2man = ""
            mod2type = ""
        elif cell_qty == 1 and wifi != 'NotExists':
            print("#### modem 1 and wifi instead of modem 2")
            mod1man = self.modem_manuf(cell_type)
            mod1type = self.modem_type(cell_type, lora)
            mod2man = self.modem_manuf(wifi)
            mod2type = self.modem_type(wifi, lora)
        elif cell_qty == 'NotExists' and wifi != 'NotExists':
            print("#### mo modem 1 and wifi instead of modem 2")
            mod1man = ""
            mod1type = ""
            mod2man = self.modem_manuf(wifi)
            mod2type = self.modem_type(wifi, lora)
        elif cell_qty == 2:
            print("#### two modems are installed")
            mod1man = self.modem_manuf(cell_type)
            mod1type = self.modem_type(cell_type, lora)
            mod2man = self.modem_manuf(cell_type)
            mod2type = self.modem_type(cell_type, lora)
        elif cell_qty == 1 and lora != 'NotExists':
            print("#### modem 1 and LoRa instead of modem 2")
            mod1man = self.modem_manuf(cell_type)
            mod1type = self.modem_type(cell_type, lora)
            mod2man = self.modem_manuf('lora')
            mod2type = self.modem_type('lora', lora)
        elif cell_qty == 'NotExists' and lora != 'NotExists':
            print("#### no modem 1 and LoRa instead of modem 1")
            mod1man = self.modem_manuf('lora')
            mod1type = self.modem_type('lora', lora)
            mod2man = ''
            mod2type = ''

        res, mac = self.get_mac()
        if res is not True:
            self.mainapp.gaSet['fail'] = "Get MACs Fail"
            return -1
        
        ma = re.search(r'REV([\d\.]+)\w', self.mainapp.gaSet['main_pcb'])
        main_pcb_rev = float(ma.group(1))
        if self.mainapp.gaSet['ps'] == 'ACEX':
            ps = '12V'
        elif self.mainapp.gaSet['ps'] == 'DC' and main_pcb_rev <= 0.5:
            ps = '12V'
        elif self.mainapp.gaSet['ps'] == 'DC' and main_pcb_rev > 0.5:
            ps = 'DC'
        elif self.mainapp.gaSet['ps'] == 'WDC':
            ps = 'WDC-I'
        elif self.mainapp.gaSet['ps'] == '12V':
            ps = '12V-I'
        elif self.mainapp.gaSet['ps'] == 'D72V':
            ps = 'D72V-I'
        elif self.mainapp.gaSet['ps'] == 'FDC':
            ps = 'FDC-I'
        elif self.mainapp.gaSet['ps'] == 'RDC':
            ps = 'RDC-I'

        serial = self.mainapp.gaSet['serPort']
        if serial == 'NotExists':
            ser1 = ''
            ser2 = ''
            s1rs485 = ''
            s2rs485 = ''
            s1cts = ''
            s2cts = ''
        elif serial in ['2RS', '2RSI']:
            ser1 = 'RS232'
            ser2 = 'RS232'
            s1rs485 = ''
            s2rs485 = ''
            s1cts = 'YES'
            s2cts = 'YES'
        elif serial in ['2RSM', '2RMI']:
            ser1 = 'RS485'
            ser2 = 'RS232'
            s1rs485 = '2W'
            s2rs485 = ''
            s1cts = 'YES'
            s2cts = 'YES'
        elif serial in ['1RS']:
            ser1 = 'RS232'
            ser2 = ''
            s1rs485 = ''
            s2rs485 = ''
            s1cts = 'YES'
            s2cts = ''

        ee_str = ''
        ee_str += f'MODEM_1_MANUFACTURER={mod1man},'
        ee_str += f'MODEM_2_MANUFACTURER={mod2man},'
        ee_str += f'MODEM_1_TYPE={mod1type},'
        ee_str += f'MODEM_2_TYPE={mod2type},'
        ee_str += f'MAC_ADDRESS={mac},'

        ee_str += f'MAIN_CARD_HW_VERSION={main_pcb_rev},'

        if main_pcb_rev < 0.6:
            sub1_pcb_rev = ''
            hwAdd = 'A'
            sub1_pcb = ''
        else:
            hwAdd = 'C'
            if (main_pcb_rev == 0.6 and
                    self.mainapp.gaSet['dbr_name'] in ['SF-1P/E1/DC/4U2S/2RSM/5G/2R',
                                                  'SF-1P/E1/DC/4U2S/2RSM/5G/G/LRB/2R',
                                                  'SF-1P/E1/DC/4U2S/2RSM/5G/LRA/2R']):
                hwAdd = 'C'   
            if self.mainapp.gaSet['sub1_pcb']:
                ma = re.search(r'REV([\d\.]+)\w', self.mainapp.gaSet['sub1_pcb'])
                sub1_pcb_rev = float(ma.group(1))
                sub1_pcb = self.mainapp.gaSet['sub1_pcb']
            else:
                sub1_pcb_rev = ''
                sub1_pcb = ''

        ee_str += f'SUB_CARD_1_HW_VERSION={sub1_pcb_rev},'
        ee_str += f'HARDWARE_ADDITION={hwAdd},'
        ee_str += f'CSL={self.mainapp.gaSet['csl']},'
        ee_str += f'PART_NUMBER={self.mainapp.gaSet['mrkt_name']},'
        ee_str += f'PCB_MAIN_ID={self.mainapp.gaSet['main_pcb']},'
        ee_str += f'PCB_SUB_CARD_1_ID={sub1_pcb},'
        ee_str += f'PS={ps},'
        if re.search('/HL', self.mainapp.gaSet['dbr_name']) or re.search('ETX', self.mainapp.gaSet['dbr_name']):
            ee_str += f'SD_SLOT=,'
        else:
            ee_str += f'SD_SLOT=YES,'
        ee_str += f'SERIAL_1={ser1},'
        ee_str += f'SERIAL_2={ser2},'
        ee_str += f'SERIAL_1_CTS_DTR={s1cts},'
        ee_str += f'SERIAL_2_CTS_DTR={s2cts},'
        ee_str += f'RS485_1={s1rs485},'
        ee_str += f'RS485_2={s2rs485},'
        
        if re.search('ETX', self.mainapp.gaSet['dbr_name']):
            ee_str += f'DRY_CONTACT_IN_OUT=,'
        else:
            ee_str += f'DRY_CONTACT_IN_OUT=2_2,'

        if self.mainapp.gaSet['wanPorts'] == "4U2S":
            ee_str += f'NNI_WAN_1=FIBER,NNI_WAN_2=FIBER,LAN_3_4=YES,'
        elif self.mainapp.gaSet['wanPorts'] == "2U":
            ee_str += f'NNI_WAN_1=,NNI_WAN_2=,LAN_3_4=,'
        elif self.mainapp.gaSet['wanPorts'] == "5U1S":
            ee_str += f'NNI_WAN_1=FIBER,NNI_WAN_2=FIBER,LAN_3_4=YES,'
        elif self.mainapp.gaSet['wanPorts'] == "1SFP1UTP":
            ee_str += f'NNI_WAN_1=FIBER,NNI_WAN_2=COPPER,LAN_3_4=YES,'
        
        ee_str += f'LIST_REF=0.0,END='

        self.add_to_log(ee_str)

        ee_file_name = f"eeprom.{str(self.mainapp.gaSet['gui_num'])}.txt"
        ee_file = Path(os.path.join(self.mainapp.gaSet['logs_fld'], ee_file_name))
        with open(ee_file, 'w+') as ee:
            ee.write(ee_str)

        tftpboot_fld =  '/var/lib/tftpboot'
        tftpboot_ee_file = Path(os.path.join(tftpboot_fld, ee_file_name))
        try:
            subprocess.check_output(f'echo 1q2w3e4r5t | sudo -S cp {ee_file} {tftpboot_ee_file}', 
                            shell=True)            
        except Exception as e:
            self.mainapp.gaSet['fail'] = e
            return -1
            
        return 0, ee_file_name
  

    def get_mac(self):
        ws = radapps.MacReg()
        if True:
            res, (mac, qty) = True, ('112233445566', 0)
        else:    
            res, (mac,qty) = ws.mac_server(10)
        ma = ':'.join(mac[i:i+2] for i in range(0, len(mac),2))
        return res, ma

    def modem_manuf(self, cell_type):
        if cell_type in ['HSP', 'L1', 'L2', 'L3', 'L4', 'LG']:
            return 'QUECTEL'
        elif cell_type in ['WF']:
            return 'AZUREWAVE'
        elif cell_type in ['lora']:
            return 'RAK'
        elif cell_type in ['L450A']:
            return 'Unitac'
        elif cell_type in ['L450B']:
            return 'Unitac'
        elif cell_type in ['WH']:
            return 'GATEWORKS'
        elif cell_type in ['L4P']:
            return 'Sequans'
        elif cell_type in ['LTA', 'LTG']:
            return 'Telit'
        elif cell_type in ['5G']:
            return 'SIERRA WIRELESS'

    def modem_type(self, cell_type, lora):  
        if cell_type == 'HSP': return 'UC20'
        if cell_type == 'L1': return 'EC25-E'
        if cell_type == 'L2': return 'EC25-A'
        if cell_type == 'L3': return 'EC25-AU'
        if cell_type == 'L4': return 'EC25-AFFD'
        if cell_type == 'WF': return 'AW-CM276MA'
        if cell_type == 'lora':
            if lora == 'LR1': return 'EU433'
            if lora == 'LR2': return 'RAK-5146'
            if lora == 'LR3': return 'US915'
            if lora == 'LR4': return 'US915'
            if lora == 'LR6': return 'AS923'
            if lora == 'LR7': return 'EU868'
            if lora == 'LRA': return '9XX'
            if lora == 'LRB': return '8XX'
            if lora == 'LRC': return 'LRC'
        if cell_type == 'L450A': return 'AML620EU'
        if cell_type == 'L450B': return 'ML660PC'
        if cell_type == '5G': return 'EM9191'
        if cell_type == 'LG': return 'EC25-G'
        if cell_type == 'WH': return 'GW16146'
        if cell_type == 'L4P': return 'CA410M'
        if cell_type == 'LTA': return 'MPLS83-X'
        if cell_type == 'LTG': return 'MPLS83-W'


class Ramzor:
    def __init__(self):
        # self.hidraw = "1"
        pass
            
    def ramzor(self, color, state):
        if color.lower() == 'red':
            rlys = "2"
        elif color == 'green':
            rlys = "1"
        elif color == 'all':
            rlys = ['1', '2']

        # cmd = f'usbrelay /dev/hidraw{self.hidraw}_{rly}={state}'
        for rly in rlys:
            cmd = f'usbrelay RMZ_{rly}={str(state)}'
            print(cmd)
            for i in range(1,11):
                with subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
                    stdout, stderr = process.communicate()
                    print(f'i:{i} stdout:<{stdout}>, stderr:<{stderr}>, {process.returncode}')
                    if process.returncode == 0:
                        break
        
        return 0


class RLCom:
    def __init__(self, com):
        self.com = f'/dev/{com}'
        self.baudrate = 115200

    def open(self):
        try:
            self.ser = serial.Serial(self.com, self.baudrate, 8, 'N', 1, 0, 0, 2)
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            return True
        except Exception as e:
            res = f'Fail to open {self.com}'
            print(f'{res}: {e}')
            return False

    def close(self):
        self.ser.close()

    def read(self):
        data_bytes = self.ser.in_waiting
        if data_bytes:
            return self.ser.read(data_bytes).decode()
        else:
            return ''

    def send(self, sent, exp='', timeout=10):
        return self.my_send(sent, '', exp, timeout)

    def send_slow(self, sent, lett_dly, exp='', timeout=10):
        return self.my_send(sent, lett_dly, exp, timeout)

    def my_send(self, sent, lett_dly, exp, timeout):
        sent_txt = sent.replace("\r", "\\r")
        start_time = time.time()
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        if lett_dly != '':
            for byte in sent:
                self.ser.write(byte.encode())
                time.sleep(lett_dly / 1000)
        else:
            self.ser.write(sent.encode())

        self.ser.flush()
        res = 0

        if exp:
            rx = ''
            res = -1
            start_time = time.time()
            while True:
                if not self.ser.writable() or not self.ser.readable():
                    self.ser.close()
                    break

                data_bytes = self.ser.in_waiting
                if data_bytes:
                    try:
                        rx += self.ser.read(data_bytes).decode()
                        if re.search(exp, rx):
                            res = 0
                            break
                    except:
                        pass
                run_time = time.time() - start_time
                if run_time > float(timeout):
                    break

            send_time = '%.7s sec.' % (time.time() - start_time)

        else:
            send_time = 0
            rx = ''

        self.buffer = rx

        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f'\n{now} Send sent:<{sent_txt}>, exp:<{exp}>, snd_time:<{send_time}>, rx:<{rx}>')
        return res

