import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import re
import functools
from functools import partial


class DialogBox(tk.Toplevel):
    def __init__(self, *args):
        self.args = args
        

    def create(self, parent, db_dict, *args):
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
    