#
# Freecycle editor
#
# Copyright (C) 2018-2025 Mark McIntyre

import tkinter as tk
import sys
from tkinter import messagebox, Frame, Menu
import time
import configparser
from cryptography.fernet import Fernet
from tksheet import Sheet
import pandas as pd

import createJsFromCSV

from ddbTables import loadItemDetails, addRow

global_bg = "Black"
global_fg = "Gray"
MAXAGE = 50


def quitApp():
    # Cleanly exits the app
    root.quit()
    root.destroy()


class fsEditor(Frame):
    def __init__(self, parent, cfgfile):
        self.parent = parent
        Frame.__init__(self, self.parent)#, bg = global_bg)
        #self.parent.configure(bg = global_bg)  # Set backgound color

        config = configparser.ConfigParser()
        config.read(cfgfile)
        self.cfgfile = cfgfile
        self.listtype = config['source']['listtype']
        self.fsdata = []

        with open('freecycle.key', 'rb') as keyf:
            privatekey = keyf.read()
        decor = Fernet(privatekey)
        self.dkey = decor.decrypt(config['aws']['KEY'].encode()).decode()
        self.dsec = decor.decrypt(config['aws']['SEC'].encode()).decode()

        self.loadData()

        self.parent.title(f'{self.listtype} Maintenance')
        # Make menu
        self.menuBar = Menu(self.parent)
        self.parent.config(menu=self.menuBar)

        # File menu
        fileMenu = Menu(self.menuBar, tearoff=0)
        fileMenu.add_command(label="Exit", command=self.quitApplication)

        self.menuBar.add_cascade(label="File", underline=0, menu=fileMenu)

        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)
        self.frame = tk.Frame(self, bg=global_fg)

        self.frame.grid_columnconfigure(0, weight = 1)
        self.frame.grid_rowconfigure(0, weight = 1)
        self.sheet = Sheet(self.parent,
            page_up_down_select_row = True,
            expand_sheet_if_paste_too_big = True,
            #empty_vertical = 0,
            column_width = 120,
            startup_select = (0,1,"rows"),
            data = self.fsdata, 
            headers = self.hdrs, 
            height = 700, 
            width = 700) 

        self.sheet.enable_bindings(("single_select", 
                                    "column_width_resize",
                                    "arrowkeys",
                                    "right_click_popup_menu",
                                    "copy",
                                    "cut",
                                    "paste",
                                    "delete",
                                    "undo",
                                    "edit_cell"
                                    ))

        self.frame.grid(row = 1, column = 0, sticky = "nswe")
        self.sheet.grid(row = 0, column = 0, sticky = "nswe")
        self.sheet.set_all_column_widths()
        self.sheet.change_theme("light green")

        self.sheet.extra_bindings([("begin_edit_cell", self.begin_edit_cell),
                                   ("end_edit_cell", self.end_edit_cell)])

    def quitApplication(self):
        if messagebox.askyesno("Quit", "Do you want to save changes?"):
            if self.saveData() is True:
                quitApp()
        else:
            quitApp()

    def loadData(self):
        df = loadItemDetails(self.listtype)
        self.orig_hdrs = df.columns.tolist()
        df2=df[['isdeleted','recType','Item','contact_n','contact_p','contact_e','price','description','url1','url2','url3', 'created', 'uniqueid']]
        self.hdrs = df2.columns.tolist()
        self.fsdata = df2.values.tolist()
        self.rows = len(self.fsdata)
        print(f'read {self.rows} rows from {self.listtype}')
    
    def saveData(self):
        df = pd.DataFrame(self.fsdata, columns=self.hdrs)
        #df = df2[self.orig_hdrs].copy()

        # update the webpage - retry a few times if necessary
        retries = 0
        succ = createJsFromCSV.main(self.cfgfile, True, df=df)
        while succ is False and retries < 5:
            print('retrying...')
            time.sleep(3)
            succ = createJsFromCSV.main(self.cfgfile, True, df=df)
            retries += 1
        if not succ:
            messagebox.showinfo("Freecycle GUI", "Webpage NOT updated, please try again")
            return False
        else:
            messagebox.showinfo("Freecycle GUI", "Webpage Refreshed")
            return True

    def begin_edit_cell(self, event):
        self.oldval = event['value']
        #print(self.oldval, event['row'])
        return self.oldval

    def end_edit_cell(self, event):
        #print(event)
        if event['value'] != self.oldval: 
            #print('changed value')

            data = self.fsdata[event['row']]
            #print(data)
            #print('new data', event['value'], 'for', event['column'])
            newdata = {'uniqueid': data[-1], 'recType': data[1], 
                   'Item': str(data[2]), 'description':data[7], 'price': str(data[6]), 
                   'contact_n': data[3], 'contact_p': data[4], 'contact_e': data[5],
                   'url1': data[8], 'url2': data[9], 'url3': data[10], 
                   'isdeleted': data[0], 'created': str(data[11])}
            #print(newdata)
            addRow(newdata=newdata)
        return 
    

if __name__ == '__main__':
    if len(sys.argv) > 1:
        root = tk.Tk()
        root.geometry('+0+0')
        app = fsEditor(root, sys.argv[1])
        root.protocol('WM_DELETE_WINDOW', app.quitApplication)
        root.mainloop()
    else:
        print('usage: python editorGUI.pi config.ini')
