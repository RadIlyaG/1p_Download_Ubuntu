#! /usr/bin/python3

print('sudo usermod -a -G plugdev ilya')
print('sudo usermod -a -G tty ilya')
print('sudo usermod -a -G dialout ilya')
print('usbrelay -d')
print('usbrelay HURTM_0=RMZ')
print('usbrelay HURTM_0=PWR')


import re
import os
import sys
import functools
from functools import partial
import glob
from subprocess import check_output
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk
import socket
from datetime import datetime
from pathlib import Path

import lib_gen_1pDownload as lib_gen
import lib_radapps_1pDownload as radapps
import test_my_procs as tmp
import MainTests_1pDownload as main
import lib_DialogBox as dbox

import app_logger



class App(tk.Tk):
    '''Create the application on base of tk.Tk, put the frames'''
    def __init__(self, gui_num):
        super().__init__()
        self.gaSet = {}
        self.title(f'{gui_num}: 1p Download Tool')
        self['relief'] = tk.GROOVE
        self['bd'] = 2
        
        self.os = os.name
        self.gen = lib_gen.Gen(self)
        ip = self.get_pc_ip()
        self.gaSet['gui_num'] = gui_num
        self.gaSet['pc_ip'] = ip

        host = ip.replace('.', '_')
        woDir = os.getcwd()
        if '1p_download' in woDir:
            host_fld = os.path.join(woDir, host)            
            temp_fld = f'{os.path.dirname(woDir)}/temp'
        else:
            host_fld = os.path.join(woDir, '1p_download', host)
            temp_fld = os.path.join(woDir, 'temp')
        print(f'woDir:<{woDir}> host_fld:<{host_fld}> temp_fld:<{temp_fld}>')
        # logger.warning(f'woDir:<{woDir}>host_fld:<{host_fld}>')
        self.gaSet['host_fld'] = host_fld
        self.gaSet['temp_fld'] = temp_fld
        Path(temp_fld).mkdir(parents=True, exist_ok=True)

        hw_dict = self.gen.read_hw_init(gui_num, host_fld)
        ini_dict = self.gen.read_init(self, gui_num, host_fld)
        self.gaSet = {**hw_dict, **ini_dict}
        self.gaSet['gui_num'] = gui_num
        self.gaSet['pc_ip'] = ip
        self.gaSet['root'] = self
        self.gaSet['host_fld'] = host_fld
        self.gaSet['temp_fld'] = temp_fld
        self.if_rad_net()
        
        self.put_frames()
        self.put_menu()
        self.gui_num = gui_num

        print(self.gaSet['geom'])
        self.geometry(self.gaSet['geom'])

        self.status_bar_frame.status("Scan UUT barcode to start")
        self.bind('<Alt-r>', partial(self.main_frame.frame_start_from.button_run))

        # print(self.gaSet)
        
    def put_frames(self):
        mainapp = self
        self.main_frame = MainFrame(self, mainapp)
        self.status_bar_frame = StatusBarFrame(self, mainapp)
        
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=2, pady=2)
        self.status_bar_frame.pack(expand=True, fill='x')
        
    def put_menu(self):
        self.config(menu=MainMenu(self))
        
    def quit(self):
        print('quit', self)
        self.gen.save_init(self)
        gen = lib_gen.Gen(self)
        gen.play_sound('info.wav')
        db_dict = {
            "title": "Confirm exit",
            "message": "Are you sure you want to close the application?",
            "type": ["Yes", "No"],
            "icon": "::tk::icons::question",
            'default': 0
        }
        dibox = dbox.DialogBox()
        dibox.create(self, db_dict)
        string, res_but, ent_dict = dibox.show()
        #string, res_but, ent_dict = neDialogBox(self, db_dict).show()
        print(string, res_but)
        if res_but == "Yes":
            for f in glob.glob("SW*.txt"):
                os.remove(f)
            self.destroy()
            # ?? no sys ??? sys.exit()
            
    def get_pc_ip(self):
        if self.os == "posix":
            for ip in check_output(['hostname', '--all-ip-addresses']).decode().split(' '):
                if '10.10.10' not in ip and ip != '\n':
                    break
        else:
            ip = socket.gethostbyname_ex(socket.gethostname())[2][0]
            
        print(f'get_pc_ip ip:{ip}')
        return ip
            
    def if_rad_net(self):
        rad_net = False
        ip = self.gaSet['pc_ip']
        if re.search('192.115.243', ip) or re.search('172.18.9', ip):
            rad_net = True
        self.gaSet['rad_net'] = rad_net

    def start_from_combobox(self, values, txt):
        self.main_frame.frame_start_from.cb_start_from.config(values=values)
        self.main_frame.frame_start_from.var_start_from.set(txt)
        
                
class MainMenu(tk.Menu):
    def __init__(self, appwin):
        super().__init__(appwin) 

        ramz = lib_gen.Ramzor()
                
        file_menu = tk.Menu(self, tearoff=0)
        file_menu.add_command(label="Capture Console")
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=appwin.quit)
        self.add_cascade(label="File", menu=file_menu)
        
        tools_menu = tk.Menu(self, tearoff=0)
        tools_menu.add_command(label="Setup Downloaded Package")
        tools_menu.add_separator()
        self.pwr_menu = tk.Menu(tools_menu, tearoff=0)
        self.pwr_menu.add_command(label="PS ON", command=lambda: appwin.gen.gui_Power(1, 1))
        self.pwr_menu.add_command(label="PS OFF", command=lambda: appwin.gen.gui_Power(1, 0))
        self.pwr_menu.add_command(label="PS OFF and ON", command=lambda: appwin.gen.gui_PowerOffOn(1))
        tools_menu.add_cascade(label="Power", menu=self.pwr_menu)
        tools_menu.add_separator()
        self.rmz_menu = tk.Menu(tools_menu, tearoff=0)
        self.rmz_menu.add_command(label="All ON", command=lambda: ramz.ramzor("all", "1"))
        self.rmz_menu.add_command(label="All OFF", command=lambda: ramz.ramzor("all", "0"))
        self.rmz_menu.add_command(label="Red ON", command=lambda: ramz.ramzor("red", "1"))
        self.rmz_menu.add_command(label="Red OFF", command=lambda: ramz.ramzor("red", "0"))
        self.rmz_menu.add_command(label="Green ON", command=lambda: ramz.ramzor("green", "1"))
        self.rmz_menu.add_command(label="Green OFF", command=lambda: ramz.ramzor("green", "0"))
        tools_menu.add_cascade(label="Ramzor", menu=self.rmz_menu)
        self.add_cascade(label="Tools", menu=tools_menu)
        
        terminal_menu = tk.Menu(self, tearoff=0)
        terminal_menu.add_command(label=f"UUT: {appwin.gaSet['comDut']}",
                             command=lambda: appwin.gen.open_terminal(appwin, "comDut"))
        self.add_cascade(label="Terminal", menu=terminal_menu)

        chk_menu = tk.Menu(self, tearoff=0)
        chk_menu.add_command(label="chk status",
                                  command=lambda: appwin.status_bar_frame.status("comDut", 'green'))
        chk_menu.add_command(label="chk startTime",
                             command=lambda: appwin.status_bar_frame.start_time("11:13:14 23/12/2024"))
        chk_menu.add_command(label="chk runTime",
                             command=lambda: appwin.status_bar_frame.run_time("1234"))
        self.add_cascade(label="checks", menu=chk_menu)
        
class MainFrame(tk.Frame):
    '''Create the Main Frame on base of tk.Frame'''
    def __init__(self, parent, mainapp):
        super().__init__(parent)
        print(f'MainFrame, self:<{self}>, parent:<{parent}>')
        self['relief'] = self.master['relief']
        # self['bd'] = self.master['bd']
        self.put_main_frames(mainapp)
        
    def put_main_frames(self, mainapp):
        self.frame_start_from = StartFromFrame(self, mainapp)
        self.frame_info = InfoFrame(self, mainapp)
        self.frame_barcodes = BarcodesFrame(self, mainapp)
        
        self.frame_start_from.grid(row=0, column=0, columnspan=2, sticky="news")
        self.frame_info.grid(row=1, column=0, sticky="news", padx=2, pady=2)
        self.frame_barcodes.grid(row=1, column=1, sticky="news", padx=2, pady=2)
        
    def put_widgets(self):
        pass
        

class StartFromFrame(tk.Frame):
    '''Create the StartFrom Frame on base of tk.Frame'''
    def __init__(self, parent, mainapp):
        super().__init__(parent)
        print(f'StartFromFrame, self:<{self}>, parent:<{parent}>, mainapp:<{mainapp}>')
        self.parent = parent
        self['relief'] = self.master['relief']
        self['bd'] = self.master['bd']
        self.put_widgets()
        self.mainapp = mainapp

    def put_widgets(self):
        self.lab_start_from = ttk.Label(self, text="Start from ")

        self.var_start_from = tk.StringVar()
        self.cb_start_from = ttk.Combobox(self, justify='center', width=20, textvariable=self.var_start_from)

        script_dir = os.path.dirname(__file__)
        self.img = Image.open(os.path.join(script_dir, "images", "run1.gif"))
        use_img = ImageTk.PhotoImage(self.img)
        self.b_start = ttk.Button(self, text="Start", image=use_img, command=partial(self.button_run))
        self.b_start.image = use_img

        self.img = Image.open(os.path.join(script_dir, "images", "stop1.gif"))
        use_img = ImageTk.PhotoImage(self.img)
        self.b_stop = ttk.Button(self, text="Stop", image=use_img, command=partial(self.button_stop))
        self.b_start.b_stop = use_img

        self.lab_curr_test = ttk.Label(self, text='Current Test:')
        self.var_curr_test = tk.StringVar()
        self.lab_curr_test_val = ttk.Label(self, width=20, relief=tk.SUNKEN, anchor="center", textvariable=self.var_curr_test)
        
        self.lab_start_from.pack(side='left', padx='2')
        self.cb_start_from.pack(side='left', padx='2')
        self.b_start.pack(side='left', padx='2')
        self.b_stop.pack(side='left', padx='2')
        self.lab_curr_test.pack(side='left', padx='2')
        self.lab_curr_test_val.pack(side='left', padx='2')

    def button_run(self, *event):
        
        gen = lib_gen.Gen(self.mainapp)
        print(f'\n{gen.my_time()} button_run1 mainapp:{self.mainapp}, {self.mainapp.gaSet}')
        
        self.mainapp.status_bar_frame.status('')
        self.mainapp.gaSet['act'] = 1
        self.b_start.state(["pressed", "disabled"])
        self.b_stop.state(["!pressed", "!disabled"])

        now = datetime.now()
        self.mainapp.gaSet['log_time'] = now.strftime("%Y.%m.%d-%H.%M.%S")
        temp_log = f"{self.mainapp.gaSet['temp_fld']}/{self.mainapp.gaSet['log_time']}_tmp.log"
        self.mainapp.logger = app_logger.get_logger(__name__, temp_log)
        self.mainapp.logger.warning(f'\n{gen.my_time()} button_run1 mainapp:{self.mainapp}, {self.mainapp.gaSet}')

        woDir = os.getcwd()
        if '1p_download' in woDir:
            logs = f'{os.path.dirname(woDir)}/logs'
        else:
            logs = f'{woDir}/logs'
        print(f'woDir:<{woDir}>logs:<{logs}>')
        Path(logs).mkdir(parents=True, exist_ok=True)
        self.mainapp.gaSet['logs_fld'] = logs

        gui_num = self.mainapp.gaSet['gui_num']

        ret = 0
        self.mainapp.gaSet['emp_numb'] = '114965'
        self.mainapp.gaSet['emp_name'] = 'KOBY LAZARY'
        if ret == 0:
            self.mainapp.gaSet['log'] = f"{logs}/{self.mainapp.gaSet['log_time']}_{gui_num}_{self.mainapp.gaSet['id_number']}.txt"
            gen.add_to_log(f"{self.mainapp.gaSet['id_number']} {self.mainapp.gaSet['dbr_name']}")
            gen.add_to_log(f"Main Board: {self.mainapp.gaSet['main_trace']} {self.mainapp.gaSet['main_pcb']}")
            if self.mainapp.gaSet['sub1_trace']:
                gen.add_to_log(f"Sub1 Board: {self.mainapp.gaSet['sub1_trace']} {self.mainapp.gaSet['sub1_pcb']}")
            gen.add_to_log(f"DBR Name: {self.mainapp.gaSet['dbr_name']}")
            gen.add_to_log(f"Employee Number: {self.mainapp.gaSet['emp_numb']}, Name: {self.mainapp.gaSet['emp_name']}")
            gen.add_to_log('\n')

            tests = self.mainapp.tests
            # fst_tst = test_names_lst.index(Toolbar.var_start_from.get())
            fst_tst = self.mainapp.main_frame.frame_start_from.var_start_from.get()
            tests_from = tests[tests.index(fst_tst):]
            print(f'\nbutton_run4 fst_tst:{fst_tst} tests:{tests} tests_from:{tests_from}')

            main_obj = main.Main(self.mainapp)
            for tst in tests_from:
                tst = tst.split('..')[1]
                gen.add_to_log(f"Start of {tst}")
                self.var_curr_test.set(tst)
                print(f'\n{gen.my_time()} Start of {tst}')
                self.mainapp.gaSet['root'].update()
                try:
                    ret = getattr(main_obj, tst)()
                except Exception as e:
                    ret = -1
                    self.mainapp.gaSet['fail'] = e

                if ret != 0:
                    if ret == -2:
                        self.mainapp.gaSet['fail'] = "User Stop"
                    ret_txt = f"Fail. Reason: {self.mainapp.gaSet['fail']}"
                else:
                    ret_txt = 'Pass'
                print(f'{gen.my_time()} Ret of Test {tst}:{ret}')
                gen.add_to_log(f"End of {tst}, result: {ret_txt}\n")
                if ret != 0:
                    break

        # After  Tests
        self.mainapp.status_bar_frame.run_time("")
        self.mainapp.gaSet['use_exist_barcode'] = 0
        src = None
        if 'log' in self.mainapp.gaSet:
            src = Path(self.mainapp.gaSet['log'])
        print(f'\n After Tests ret:{ret}')

        if ret == 0:
            wav = "pass.wav"
            # main_obj.my_statusbar.sstatus("")
            self.mainapp.status_bar_frame.status("Done", 'green')

            dst = f'{os.path.splitext(src)[0]}-PASS{os.path.splitext(src)[1]}'
            os.rename(src, dst)
            run_status = 'Pass'
        elif ret == 1:
            wav = "info.wav"
            self.mainapp.status_bar_frame.status("The test has been perform", 'yellow')
        else:
            run_status = 'Fail'
            if ret == -2:
                self.mainapp.gaSet['fail'] = 'User stop'
                run_status = ''
            elif ret == -3:
                run_status = ''

            self.mainapp.status_bar_frame.status(f"Test FAIL: {self.mainapp.gaSet['fail']}", 'red')
            wav = "fail.wav"
            if src and os.path.isfile(src):
                dst = f'{os.path.splitext(src)[0]}-FAIL{os.path.splitext(src)[1]}'
                os.rename(src, dst)

        self.b_start.state(["!pressed", "!disabled"])
        self.b_stop.state(["pressed", "disabled"])

        try:
            # gen = lib_gen.Gen()
            gen.play_sound(wav)
        except Exception as e:
            pass
        finally:
            # MenuBar.use_ex_barc.set(0)
            print(f'ButRun finally: ret:{ret}  {self.mainapp.gaSet}')

    def button_stop(self, *event):
        self.mainapp.gaSet['root'].update()
        gen = lib_gen.Gen(self.mainapp)
        print(f'\n{gen.my_time()} button_stop')
        # self.mainapp.status_bar_frame.status('')
        self.mainapp.gaSet['act'] = 0
        self.b_start.state(["!pressed", "!disabled"])
        self.b_stop.state(["pressed", "disabled"])
        self.mainapp.gaSet['root'].update()


class InfoFrame(tk.Frame):
    '''Create the Info Frame on base of tk.Frame'''
    def __init__(self, parent, mainapp):
        super().__init__(parent)
        print(f'InfoFrame, self:<{self}>, parent:<{parent}>, mainapp:<{mainapp}>')
        # self['relief'] = self.master['relief']
        self['relief'] = tk.GROOVE
        self['bd'] = 2
        self.put_widgets()
        self.mainapp = mainapp
        
    def put_widgets(self):
        self.lab_act_package_txt = ttk.Label(self, text='Package:')
        self.lab_act_package_val = ttk.Label(self, text='')
        self.lab_sw_txt = ttk.Label(self, text='SW Ver.:')
        self.lab_sw_val = ttk.Label(self, text='')
        self.lab_flash_txt = ttk.Label(self, text='Flash Image:')
        self.lab_flash_val = ttk.Label(self, text='')
        
        self.lab_act_package_txt.grid(row=0, column=0, sticky='w', padx=2, pady=2)
        self.lab_act_package_val.grid(row=0, column=1, sticky='e', padx=2, pady=2)
        self.lab_sw_txt.grid(row=1, column=0, sticky='w', padx=2, pady=2)
        self.lab_sw_val.grid(row=1, column=1, sticky='e', padx=2, pady=2)
        # self.lab_flash_txt.grid(row=2, column=0, sticky='w', padx=2, pady=2)
        # self.lab_flash_val.grid(row=2, column=1, sticky='e', padx=2, pady=2)

        
class BarcodesFrame(tk.Frame):
    '''Create the Barcodes Frame on base of tk.Frame'''
    def __init__(self, parent, mainapp):
        super().__init__(parent)
        # self['relief'] = self.master['relief']
        # self['bd'] = self.master['bd']
        self['relief'] = tk.GROOVE
        self['bd'] = 2
        print(f'BarcodesFrame, self:<{self}>, parent:<{parent}>, mainapp:<{mainapp}>')
        self.parent = parent
        self.mainapp = mainapp

        self.put_widgets()
        self.uut_id.set('DC1002333717')
        # self.main_id.set('21341063')
        self.ent_uut_id.select_range(0, tk.END)
        self.ent_uut_id.focus_set()

        self.mainapp.gaSet['main_pcb'] = False
        self.mainapp.gaSet['sub1_pcb'] = False
        self.mainapp.gaSet['main_trace'] = False
        self.mainapp.gaSet['sub1_trace'] = False
        
    def put_widgets(self):
        self.barcode_widgets = []
        self.lab_uut_id = ttk.Label(self, text='UUT ID:')
        self.barcode_widgets.append(self.lab_uut_id)
        self.uut_id = tk.StringVar()
        self.ent_uut_id = ttk.Entry(self, textvariable=self.uut_id, justify="center")
        self.ent_uut_id.bind('<Return>', partial(self.bind_uutId_entry, self.mainapp))
        self.barcode_widgets.append(self.ent_uut_id)
        self.lab_uut_dbr = ttk.Label(self, width=40, relief=tk.GROOVE, anchor="center")
        self.barcode_widgets.append(self.lab_uut_dbr)

        self.main_id = tk.StringVar()
        self.lab_main_id = ttk.Label(self, text='PCB_MAIN ID:')
        self.barcode_widgets.append(self.lab_main_id)
        self.ent_main_id = ttk.Entry(self, textvariable=self.main_id, justify="center")
        self.ent_main_id.bind('<Return>', partial(self.bind_mainId_entry, self.mainapp))
        self.barcode_widgets.append(self.ent_main_id)
        self.lab_main_dbr = ttk.Label(self, width=16, relief=tk.GROOVE, anchor="center")
        self.barcode_widgets.append(self.lab_main_dbr)

        self.sub1_id = tk.StringVar()
        self.lab_sub1_id = ttk.Label(self, text='PCB_SUB_CARD_1 ID:')
        self.barcode_widgets.append(self.lab_sub1_id)
        self.ent_sub1_id = ttk.Entry(self, textvariable=self.sub1_id, justify="center")
        self.ent_sub1_id.bind('<Return>', partial(self.bind_sub1Id_entry, self.mainapp))
        self.barcode_widgets.append(self.ent_sub1_id)
        self.lab_sub1_dbr = ttk.Label(self, width=16, relief=tk.GROOVE, anchor="center")
        self.barcode_widgets.append(self.lab_sub1_dbr)

        self.lab_ha_id = ttk.Label(self, text='Hardware Addition:')
        self.barcode_widgets.append(self.lab_ha_id)
        self.lab_ha_val = ttk.Label(self, width=16, relief=tk.GROOVE, anchor="center")
        self.barcode_widgets.append(self.lab_ha_val)
        self.lab_ha_0 = ttk.Label(self)
        self.barcode_widgets.append(self.lab_ha_0)

        self.lab_csl_id = ttk.Label(self, text='CSL:')
        self.barcode_widgets.append(self.lab_csl_id)
        self.lab_csl_val = ttk.Label(self, width=16, relief=tk.GROOVE, anchor="center")
        self.barcode_widgets.append(self.lab_csl_val)
        self.lab_csl_0 = ttk.Label(self)
        self.barcode_widgets.append(self.lab_csl_0)

        #print(f'self.barcode_widgets:<{self.barcode_widgets}>')
        for w in self.barcode_widgets:
            w.grid(row=self.barcode_widgets.index(w)//3, 
                   column=self.barcode_widgets.index(w)%3, 
                   sticky='w')


    def bind_uutId_entry(self, *event):
        gen = lib_gen.Gen(self.mainapp)
        print(f'\n{gen.my_time()}bind_uutId_entry self:{self} mainapp:{self.mainapp} event:{event}')
        id_number = self.uut_id.get()
        print(f'bind_uutId_entry id_number:{id_number}')
        dibox = dbox.DialogBox()

        if id_number == 'test_retrive_dut_family':
            tmp.test_retrive_dut_family(self.mainapp)
            return None

        self.mainapp.start_from_combobox([], '')
        self.mainapp.status_bar_frame.status(f'Getting data for {id_number}')

        ws = radapps.WebServices()
        ws.print_rtext = False

        res, dicti = ws.retrieve_oi4barcode(id_number)
        dbr_name = dicti['item']
        print(f'bind_uutId_entry res:{res} dbr_name:{dbr_name}')
        if res:
            self.mainapp.title(str(self.mainapp.gaSet['gui_num']) + ': ' + dbr_name)
            self.mainapp.gaSet['dbr_name'] = dbr_name
        else:
            # DialogBox(self.mainapp, db_dict={'title': "Get DBR Name fail", 'type': ['OK'], 'message': dbr_name, 'icon': '::tk::icons::error'}).show()
            dibox.create(self.mainapp, db_dict={'title': "Get DBR Name fail", 'type': ['OK'], 'message': dbr_name, 'icon': '::tk::icons::error'})
            string, res_but, ent_dict = dibox.show()
            self.mainapp.gaSet['fail'] = dbr_name
            return False

        # res, mrkt_name = gen.get_mrkt_name(id_number)
        res, dicti = ws.retrieve_mkt_name(id_number)
        mrkt_name = dicti['MKT Item']
        print(f'bind_uutId_entry res:{res} mrkt_name:{mrkt_name}')
        if res:
            self.mainapp.gaSet['mrkt_name'] = mrkt_name
        else:
            # DialogBox(self.mainapp, db_dict={'title': "Get Marketing Name fail", 'type': ['OK'], 'message': mrkt_name,
            #                                          'icon': '::tk::icons::error'}).show()
            dibox.create(self.mainapp, db_dict={'title': "Get Marketing Name fail", 'type': ['OK'], 'message': dbr_name, 'icon': '::tk::icons::error'})
            string, res_but, ent_dict = dibox.show()
            
            self.mainapp.gaSet['fail'] = mrkt_name
            return False

        # res, csl = gen.get_csl_name(id_number)
        res, dicti = ws.retrieve_csl(id_number)
        csl = dicti['CSL']
        print(f'bind_uutId_entry res:{res} csl:{csl}')
        if res:
            self.mainapp.gaSet['csl'] = csl
        else:
            # DialogBox(self.mainapp, db_dict={'title': "Get CSL fail", 'type': ['OK'], 'message': csl,
            #                             'icon': '::tk::icons::error'}).show()
            dibox.create(self.mainapp, db_dict={'title': "Get CSL fail", 'type': ['OK'], 'message': dbr_name, 'icon': '::tk::icons::error'})
            string, res_but, ent_dict = dibox.show()
            return False

        self.mainapp.gaSet['id_number'] = id_number
        #print(f'bind_uutId_entry mainapp.gaSet:{mainapp.gaSet}')

        res = gen.retrive_dut_fam()
        print(f'bind_uutId_entry res_retrive_dut_fam:{res}')
        if res != True:
            # DialogBox(self.mainapp, db_dict={'title': "Retrive UUT family fail", 'type': ['OK'],
            #                             'message': "Retrive UUT family fail",
            #                             'icon': '::tk::icons::error'}).show()
            dibox.create(self.mainapp, db_dict={'title': "Retrive UUT family fail", 'type': ['OK'], 
                                                'message': "Retrive UUT family fail", 
                                                'icon': '::tk::icons::error'})
            string, res_but, ent_dict = dibox.show()
            
            self.mainapp.status_bar_frame.status(f'Retrive UUT family fail for {id_number}', 'red')
            return False

        res = gen.get_dbr_sw()
        print(f'bind_uutId_entry res of get_dbr_sw:{res}')

        self.lab_csl_val.config(text=self.mainapp.gaSet['csl'])

        self.ent_main_id.focus_set()
        self.main_id.set('')
        self.ent_main_id.select_range(0, tk.END)
        self.mainapp.status_bar_frame.status('Ready')
        self.lab_uut_dbr.config(text=dbr_name)  #  width=len(dbr_name)+4

        main_obj = main.Main(self.mainapp)
        main_obj.build_tests()
        self.mainapp.tests = main_obj.tests

    def bind_mainId_entry(self, *event):
        gen = lib_gen.Gen(self.mainapp)
        ws = radapps.WebServices()
        ws.print_rtext = False

        print(f'\n{gen.my_time()}bind_mainId_entry self:{self} mainapp:{self.mainapp} event:{event}')
        barcode = self.main_id.get()
        res, dicti = ws.retrieve_traceId_data(barcode)
        # print(res, type(dicti))
        if res:
            # print(dicti['pcb'])
            self.lab_main_dbr.config(text=dicti['pcb'])
            self.mainapp.gaSet['main_pcb'] = dicti['pcb']
            self.ent_sub1_id.focus_set()
            self.sub1_id.set('')
            self.ent_sub1_id.select_range(0, tk.END)
            self.mainapp.gaSet['main_trace'] = barcode
        else:
            print(dicti)
        return res

    def bind_sub1Id_entry(self, *event):
        gen = lib_gen.Gen(self.mainapp)
        ws = radapps.WebServices()
        ws.print_rtext = False

        print(f'\n{gen.my_time()}bind_subId_entry self:{self} mainapp:{self.mainapp} event:{event}')
        barcode = self.sub1_id.get()
        res, dicti = ws.retrieve_traceId_data(barcode)
        # print(res, type(dicti))
        if res:
            print(dicti['pcb'])
            self.lab_sub1_dbr.config(text=dicti['pcb'])
            self.mainapp.gaSet['sub1_pcb'] = dicti['pcb']
            self.mainapp.gaSet['sub1_trace'] = barcode
        else:
            print(dicti)
        return res


class StatusBarFrame(tk.Frame):
    '''Create the Status Bar Frame on base of tk.Frame'''
    def __init__(self, parent, mainapp):
        super().__init__(parent)
        print(f'StatusBarFrame, self:<{self}>, parent:<{parent}>')
        self['relief'] = self.master['relief']
        self['bd'] = self.master['bd']
        self.mainapp = mainapp

        self.put_widgets()
        
    def put_widgets(self):
        self.label1 = tk.Label(self, anchor='center', width=66, relief="groove")
        self.label1.pack(side='left', padx=1, pady=1, expand=1, fill=tk.X)
        self.label2 = tk.Label(self, anchor=tk.W, width=15, relief="sunken")
        self.label2.pack(side='left', padx=1, pady=1)
        self.label3 = tk.Label(self, width=5, relief="sunken", anchor='center')
        self.label3.pack(side='left', padx=1, ipadx=2, pady=1)

    def status(self, txt, bg="gray85"):
        #  SystemButtonFace = gray85
        if bg == 'red':
            bg = 'salmon'
        elif bg == 'green':
            bg = 'springgreen'
        self.label1.configure(text=txt, bg=bg)
        self.label1.update_idletasks()

    def read_status(self):
        return self.label1.cget('text')

    def start_time(self, txt):
        self.label2.configure(text=txt)
        self.label2.update_idletasks()

    def run_time(self, txt):
        self.label3.configure(text=txt)
        self.label3.update_idletasks()
        

class neDialogBox(tk.Toplevel):
    def __init__(self, parent, db_dict, *args):
        self.args = args
        print(f"DialogBox parent:{parent} txt:{db_dict['message']} args:{args}")
        tk.Toplevel.__init__(self, parent)
        x_pos = parent.winfo_x() + 20
        y_pos = parent.winfo_y() + 20

        if 'message' in db_dict:
            msg = db_dict['message']
        else:
            db_dict['message'] = ''
            msg = ""
        message = msg

        if 'entry_qty' in db_dict:
            self.entry_qty = db_dict['entry_qty']
        else:
            self.entry_qty = 0

        if 'entry_per_row' in db_dict:
            entry_per_row = db_dict['entry_per_row']
        else:
            entry_per_row = 1

        entry_lines_qty = int(self.entry_qty/entry_per_row)
        # print(f'entry_lines_qty {entry_lines_qty}')

        new_lines_qty = message.count('\n')
        hei = 16*new_lines_qty + 44*entry_lines_qty + 60

        minH = 80
        # set minimum height to minH pixels
        if hei < minH:
            hei = minH
        # print(f'new_lines_qty {new_lines_qty} hei {hei}')

        maxW = 0
        for line in message.split('\n'):
            if len(line) > maxW:
                maxW = len(line)

        width = maxW * 8

        minW = 270
        # set minimum with to $minW pixels
        if width < minW:
            width = minW

        # print(f'self.max {maxW}, width {width}')
        # self.geometry(f'{width}x{hei}+{x_pos}+{y_pos}')
        self.geometry(f'+{x_pos}+{y_pos}')
        self.title(db_dict['title'])
        # self.bind('<Configure>', lambda event: print(self.geometry()))

        self.fr1 = tk.Frame(self)
        fr_img = tk.Frame(self.fr1)
        if re.search("tk::icons", db_dict['icon']):
            use_img_run = db_dict['icon']
        else:
            self.imgRun = Image.open(db_dict['icon'])
            use_img_run = ImageTk.PhotoImage(self.imgRun)
        l_img = tk.Label(fr_img, image=use_img_run)
        l_img.image = use_img_run
        l_img.pack(padx=10, anchor='n')

        fr_right = tk.Frame(self.fr1)
        fr_msg = tk.Frame(fr_right)
        l_msg = tk.Label(fr_msg, text=db_dict['message'])
        l_msg.pack(padx=10)

        if 'entry_lbl' in db_dict:
            entry_lbl = db_dict['entry_lbl']
        else:
            entry_lbl = ""
        if 'entry_frame_bd' in db_dict:
            bd = db_dict['entry_frame_bd']
        else:
            bd = 2
        self.ent_dict = {}
        if self.entry_qty > 0:
            self.list_ents = []
            fr_ent = tk.Frame(fr_right, bd=bd, relief='groove')
            for fi in range(0, self.entry_qty):
                f = tk.Frame(fr_ent, bd=0, relief='groove')
                txt = entry_lbl[fi]
                lab = tk.Label(f, text=txt)
                self.ent_dict[txt] = tk.StringVar()
                # CustomDialog.ent_dict[fi] = self.ent_dict[fi]
                self.list_ents.append(ttk.Entry(f, textvariable=self.ent_dict[txt]))
                # print(f'txt:{len(txt)}, entW:{ent.cget("width")}')
                self.list_ents[fi].pack(padx=2, side='right', fill='x')
                self.list_ents[fi].bind("<Return>", functools.partial(self.cmd_ent, fi))
                if entry_lbl != "":
                    lab.pack(padx=2, side='right')
                row = int((fi)/entry_per_row)
                column = int((fi)%entry_per_row)
                # print(f'fi:{fi}, txt:{txt}, row:{row} column:{column} entW:{ent.cget("width")}')
                f.grid(padx=(2, 10), pady=2, row=row, column=column, sticky='e')

        fr_msg.pack()
        if self.entry_qty > 0:
            fr_ent.pack(anchor='e', padx=2, pady=2, expand=1)

        fr_img.grid(row=0, column=0)
        fr_right.grid(row=0, column=1)

        self.frBut = tk.Frame(self)
        print(f"buts:{db_dict['type']}")

        self.buts_lst = []
        for butn in db_dict['type']:
            self.but = tk.ttk.Button(self.frBut, text=butn, width=10, command=functools.partial(self.on_but, butn))
            if args and butn == args[0]['invokeBut']:
                self.buts_lst.append((butn, self.but))
            self.but.bind("<Return>", functools.partial(self.on_but, butn))
            self.but.pack(side="left", padx=2)
            if 'default' in db_dict:
                default = db_dict['default']
            else:
                default = 0
            if db_dict['type'].index(butn) == default:
                self.but.configure(state="active")
                # self.bind('<space>', (lambda e, b=self.but: self.but.invoke()))
                self.but.focus_set()
                self.default_but = self.but

        if self.entry_qty > 0:
            self.list_ents[0].focus_set()

        self.fr1.pack(fill="both", padx=2, pady=2)

        self.frBut.pack(side="bottom", fill="y", padx=2, pady=2)

        self.var = tk.StringVar()
        self.but = ""

        if self.entry_qty > 0:
            # print(self.list_ents)
            # print(self.ent_dict)
            # print(self.args)
            # print(self.buts_lst)
            self.bind('<Control-y>', functools.partial(self.bind_diaBox, 'y'))
            self.bind('<Alt-l>', functools.partial(self.bind_diaBox, 'l'))

    def bind_diaBox(self, let, *event):
        for arg in self.args:
            for key, val in arg.items():
                print(let, key, val)
                if key != 'invokeBut':
                    if let == 'l':
                        val = arg['last']
                        key = "Scan here the Operator's Employee Number "
                    elif let == 'y' and 'ilya' in arg.keys():
                        val = arg['ilya']
                        key = "Scan here the Operator's Employee Number "

                    self.ent_dict[key].set(val)

        for butn, butn_obj in self.buts_lst:
            butn_obj.invoke()

    def cmd_ent(self, fi, event=None):
        # print(f'cmd_ent self:{self}, fi:{fi}, entry_qty:{self.entry_qty}, event:{event}')
        if fi+1 == self.entry_qty:
            # last entry -> set focus to default button
            self.default_but.invoke()
            # pass
        else:
            # not last entry -> set focus to next entry
            self.list_ents[fi+1].focus_set()

    def on_but(self, butn, event=None):
        # print(f'on_but self:{self}, butn:{butn}, event:{event}')
        self.but = butn
        self.destroy()
    # def on_ok(self, event=None):
    #     self.but = "ok"
    #     self.destroy()
    # def ca_ok(self, event=None):
    #     self.but = "ca"
    #     self.destroy()

    def show(self):
        self.wm_deiconify()
        # self.entry.focus_force()
        self.wait_window()
        # try:
        #     print(f'DialogBox show ent_dict:{self.ent_dict}')
        # except Exception as err:
        #     print(err)
        return [self.var.get(), self.but, self.ent_dict]
    

class DemoClass:
    def __init__(self):
        pass
    
    def decl(self):
        print('decl!!!')


'''print(sys.argv, len(sys.argv))
gui_num = sys.argv[1]
    
app = App(gui_num)
app.mainloop()'''

if __name__ == '__main__':
    print(sys.argv, len(sys.argv))
    if len(sys.argv)==2:
        gui_num = sys.argv[1]
    else:
        gui_num = 3
    app = App(gui_num)
    app.mainloop()
