import os
import time
import re
from datetime import datetime
from pathlib import Path
import subprocess
import socket
import json
import webbrowser

import lib_radapps_1pDownload as radapps


class Gen:
    def __init__(self):
        self.os = os.name
        self.hidraw = "0"
        
    def power(self, ps, state):
        print(f'Power self:{self}, ps:{ps}, state:{state}')
        
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

            command = os.path.join('C:/Program Files (x86)', 'teraterm', 'ttermpro.exe')
            command = str(command) + ' /c=' + str(com) + ' /baud=115200'
            # os.startfile(command)
            subprocess.Popen(command)
            print(command)
        else:
            pass
            
    def read_hw_init(self, gui_num, ip):
        print(f'read_hw_init')
        host = ip.replace('.', '_')
        Path(host).mkdir(parents=True, exist_ok=True)
        hw_file = Path(os.path.join(host, f"HWinit.{gui_num}.json"))
        if not os.path.isfile(hw_file):
            hw_dict = {
                'comDut': 'ttyUSB0',
                'pioBoxSerNum': "PWR",
            }
            # di = {**hw_dict, **dict2}

            with open(hw_file, 'w') as fi:
                # json.dump(hw_dict, fi, indent=2, sort_keys=True)
                json.dump(hw_dict, fi, indent=2, sort_keys=True)

        try:
            with open(hw_file, 'r') as fi:
                hw_dict = json.load(fi)
        except Exception as e:
            # print(e)
            # raise(e)
            raise Exception("e")

        return hw_dict

    def read_init(self, appwin, gui_num, ip):
        print(f'read_init, self:{self}, appwin:{appwin}, gui_num:{gui_num}, ip:{ip}')
        # print(f'read_init script_dir {os.path.dirname(__file__)}')
        host = ip.replace('.', '_')
        Path(host).mkdir(parents=True, exist_ok=True)
        ini_file = Path(os.path.join(host, "init." + str(gui_num) + ".json"))
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
        print(f'save_init, self:{self}, appwin:{appwin}')
        ip = appwin.gaSet['pc_ip']
        host = ip.replace('.', '_')
        gui_num = appwin.gaSet['gui_num']
        Path(host).mkdir(parents=True, exist_ok=True)
        ini_file = Path(os.path.join(host, "init." + str(gui_num) + ".json"))
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

    def add_to_log(self, mainapp, txt):
        with open(mainapp.gaSet['log'], 'a') as log:
            if txt == '':
                text = f'\n'
            else:
                text = f'{self.my_time()}..{txt}\n'
            log.write(text)


    def retrive_dut_fam(self, mainapp):
        print(f'\n{self.my_time()} retrive_dut_fam')
        # fields = mainapp.gaSet['dbr_name'].split('/')
        dbr_name = mainapp.gaSet['dbr_name'] + '/'
        print(mainapp.gaSet['dbr_name'], dbr_name)
        # print(f'retrive_dut_fam, {self}')

        # if 'HL' in fields:
        #     fields.remove('HL')

        sf_ma = re.search(r'([A-Z0-9\-\_]+)/E?', dbr_name)
        sf = sf_ma.group(1)
        # print(f'sf:{sf}')
        if sf in ['SF-1P', 'ETX-1P', 'SF-1P_ICE', 'ETX-1P_SFC', 'SF-1P_ANG']:
            mainapp.gaSet['prompt'] = '-1p#'
        elif sf == 'VB-101V':
            mainapp.gaSet['prompt'] = 'VB101V#'
        else:
            return f'Wrong product: {mainapp.gaSet["dbr_name"]}'
        # fields.remove(sf)

        if sf in ['ETX-1P', 'ETX-1P_SFC']:
            box = 'etx'
            ps_ma = re.search(r'1P/([A-Z0-9]+)/', dbr_name)
            if ps_ma is None:
                ps_ma = re.search(r'1P_SFC/([A-Z0-9]+)/', dbr_name)
            ps = ps_ma.group(1)
            wanPorts = "1SFP1UTP"
            lanPorts = "4UTP"
        else:
            box = re.search(r'P[_A-Z]*/(E[R\d]?)/', dbr_name).group(1)
            ps = re.search(r'E[R\d]?/([A-Z0-9]+)/', dbr_name).group(1)

            wanPorts_ma = re.search(r'/(2U)/', dbr_name)
            if wanPorts_ma is None:
                wanPorts_ma = re.search(r'/(4U2S)/', dbr_name)
                if wanPorts_ma is None:
                    wanPorts_ma = re.search(r'/(5U1S)/', dbr_name)
            wanPorts = wanPorts_ma.group(1)
            lanPorts = "NotExists"

        mainapp.gaSet['box'] = box
        mainapp.gaSet['ps'] = ps
        mainapp.gaSet['wanPorts'] = wanPorts
        mainapp.gaSet['lanPorts'] = lanPorts
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
            mainapp.gaSet['serPort'] = 'NotExists'
        else:
            mainapp.gaSet['serPort'] = serPort_ma.group(1)
        # if mainapp.gaSet['serPort'] in fields:
        #     fields.remove(mainapp.gaSet['serPort'])

        serPortCsp = re.search(r'/(CSP)/', dbr_name)
        if serPortCsp is None:
            mainapp.gaSet['serPortCsp'] = 'NotExists'
        else:
            mainapp.gaSet['serPortCsp'] = serPortCsp.group(1)
        # if mainapp.gaSet['serPortCsp'] in fields:
        #     fields.remove(mainapp.gaSet['serPortCsp'])

        mainapp.gaSet['poe'] = 'NotExists'
        # if mainapp.gaSet['poe'] in fields:
        #     fields.remove(mainapp.gaSet['poe'])

        mainapp.gaSet['plc'] = 'NotExists'
        # if mainapp.gaSet['plc'] in fields:
        #     fields.remove(mainapp.gaSet['plc'])

        mainapp.gaSet['cellType'] = 'NotExists'
        mainapp.gaSet['cellQty'] = 'NotExists'
        for cell in ['HSP', 'L1', 'L2', 'L3', 'L4', 'L450A', 'L450B', '5G', 'L4P', 'LG']:
            qty = len([i for i, x in enumerate(dbr_name.split('/')) if x == cell])
            # print(f'cell{cell}, qty:{qty}')
            if qty > 0:
                mainapp.gaSet['cellType'] = cell
                mainapp.gaSet['cellQty'] = qty
        # if mainapp.gaSet['cellType'] in fields:
        #     fields.remove(mainapp.gaSet['cellType'])
        # if mainapp.gaSet['cellType'] in fields:
        #     fields.remove(mainapp.gaSet['cellType'])

        gps = re.search(r'/(G)/', dbr_name)
        if gps is None:
            mainapp.gaSet['gps'] = 'NotExists'
        else:
            mainapp.gaSet['gps'] = gps.group(1)
        # if mainapp.gaSet['gps'] in fields:
        #     fields.remove(mainapp.gaSet['gps'])

        wifi_ma = re.search(r'/(WF)/', dbr_name)
        if wifi_ma is not None:
            mainapp.gaSet['wifi'] = 'WF'
        else:
            wifi_ma = re.search(r'/(WFH)/', dbr_name)
            if wifi_ma is not None:
                mainapp.gaSet['wifi'] = 'WH'
            else:
                wifi_ma = re.search(r'/(WH)/', dbr_name)
                if wifi_ma is not None:
                    mainapp.gaSet['wifi'] = 'WH'
                else:
                    mainapp.gaSet['wifi'] = 'NotExists'
        # if mainapp.gaSet['wifi'] in fields:
        #     fields.remove(mainapp.gaSet['wifi'])

        dryCon_ma = re.search(r'/(GO)/', dbr_name)
        if dryCon_ma is not None:
            mainapp.gaSet['dryCon'] = 'GO'
        else:
            mainapp.gaSet['dryCon'] = 'FULL'

        rg = re.search(r'/(RG)/', dbr_name)
        if rg is None:
            mainapp.gaSet['rg'] = 'NotExists'
        else:
            mainapp.gaSet['rg'] = 'RG'
        # if mainapp.gaSet['rg'] in fields:
        #     fields.remove(mainapp.gaSet['rg'])

        lora_ma = re.search(r'/(LR[1-6A-Z])/', dbr_name)
        if lora_ma is None:
            mainapp.gaSet['lora'] = 'NotExists'
            mainapp.gaSet['lora_region'] = 'NotExists'
            mainapp.gaSet['lora_fam'] = 'NotExists'
            mainapp.gaSet['lora_band'] = 'NotExists'
        else:
            lora = lora_ma.group(1)
            mainapp.gaSet['lora'] = lora
            if lora == 'LR1':
                mainapp.gaSet['lora_region'] = 'eu433'
                mainapp.gaSet['lora_fam'] = '4XX'
                mainapp.gaSet['lora_band'] = 'EU 433'
            elif lora == 'LR2':
                mainapp.gaSet['lora_region'] = 'eu868'
                mainapp.gaSet['lora_fam'] = '8XX'
                mainapp.gaSet['lora_band'] = 'EU 863-870'
            elif lora == 'LR3':
                mainapp.gaSet['lora_region'] = 'au915'
                mainapp.gaSet['lora_fam'] = '9XX'
                mainapp.gaSet['lora_band'] = 'AU 915-928 Sub-band 2'
            elif lora == 'LR4':
                mainapp.gaSet['lora_region'] = 'us902'
                mainapp.gaSet['lora_fam'] = '9XX'
                mainapp.gaSet['lora_band'] = 'US 902-928 Sub-band 2'
            elif lora == 'LR6':
                mainapp.gaSet['lora_region'] = 'as923'
                mainapp.gaSet['lora_fam'] = '9XX'
                mainapp.gaSet['lora_band'] = 'AS 923-925'
            elif lora == 'LRA':
                mainapp.gaSet['lora_region'] = 'us915'
                mainapp.gaSet['lora_fam'] = '9XX'
                mainapp.gaSet['lora_band'] = 'US 902-928 Sub-band 2'
            elif lora == 'LRB':
                mainapp.gaSet['lora_region'] = 'eu868'
                mainapp.gaSet['lora_fam'] = '8XX'
                mainapp.gaSet['lora_band'] = 'EU 863-870'
            elif lora == 'LRC':
                mainapp.gaSet['lora_region'] = 'eu433'
                mainapp.gaSet['lora_fam'] = '4XX'
                mainapp.gaSet['lora_band'] = 'EU 433'
        # if mainapp.gaSet['lora'] in fields:
        #     fields.remove(mainapp.gaSet['lora'])

        mem = re.search(r'/2R/', dbr_name)
        if mem is not None:
            mainapp.gaSet['mem'] = 2
            # fields.remove('2R')
        else:
            mainapp.gaSet['mem'] = 1

        plc_ma = re.search(r'/(PLC[DGO])/', dbr_name)
        if plc_ma is None:
            mainapp.gaSet['plc'] = 'NotExists'
        else:
            mainapp.gaSet['plc'] = plc_ma.group(1)

        # mainapp.gaSet['fields'] = fields

        # print(f'retrive dut fam {mainapp.gaSet}')
        # print(f'dbr_name:{dbr_name} fields:{fields}')

        return True

    def get_dbr_sw(self, mainapp):
        gswv = radapps.GetSWVersions()
        id_number = mainapp.gaSet['id_number']
        res, sw_l = gswv.gets_sw(id_number)
        print(res, sw_l)
        mainapp.gaSet['sw_boot'] = None
        mainapp.gaSet['sw_app'] = None
        for sw in sw_l:
            ver = sw['version']
            if ver[0] == 'B':
                mainapp.gaSet['sw_boot'] = ver
            else:
                mainapp.gaSet['sw_app'] = ver
        print(f'get dbr sw {mainapp.gaSet}')
        return res

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
        

        

