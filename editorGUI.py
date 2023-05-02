import tkinter as tk
import os
import sys
from tkinter import messagebox, Frame, Menu
import boto3
import datetime
import time
import configparser
from cryptography.fernet import Fernet
from tksheet import Sheet
import pandas as pd

import createJsFromCSV

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
        self.targetBucket = config['source']['BUCKET']
        self.listfldr = config['source']['LISTFLDR']
        self.csvname = config['source']['CSVNAME']
        self.newname = config['source']['NEWNAME']
        self.fsdata = []

        with open('freecycle.key', 'rb') as keyf:
            privatekey = keyf.read()
        decor = Fernet(privatekey)
        self.dkey = decor.decrypt(config['aws']['KEY'].encode()).decode()
        self.dsec = decor.decrypt(config['aws']['SEC'].encode()).decode()

        self.inuseflg = self.listfldr + '/inuse.txt'
        self.srccsvfile = self.listfldr + '/' + self.csvname

        self.loadData()
        self.initUI()

        # Update UI changes
        parent.update_idletasks()
        parent.update()
        self.update()
        return 

    def quitApplication(self):
        if messagebox.askyesno("Quit", "Do you want to save changes?"):
            if self.saveData() is True:
                self.s3.delete_object(Bucket=self.targetBucket, Key=self.inuseflg)
                quitApp()
        else:
            self.s3.delete_object(Bucket=self.targetBucket, Key=self.inuseflg)
            quitApp()


    def initUI(self):
        self.parent.title('Freecycle Maintenance')
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
                                         "double_click_column_resize",
                                         "arrowkeys",
                                         "rc_delete_row",
                                         "copy",
                                         "cut",
                                         "paste",
                                         "delete",
                                         "undo",
                                         "edit_cell"
                                    ))

        self.frame.grid(row = 1, column = 0, sticky = "nswe")
        self.sheet.grid(row = 0, column = 0, sticky = "nswe")
        self.sheet.change_theme("light green")
        self.sheet.set_all_column_widths()

    def loadData(self):
        self.s3 = boto3.client('s3', aws_access_key_id=self.dkey, aws_secret_access_key=self.dsec, region_name='eu-west-2')

        # upload flag to warn the email handler that the CSV file is in use
        self.s3.upload_file(Bucket=self.targetBucket, Key=self.inuseflg, Filename='inuse.txt')

        # download the source file
        fileName = os.path.join(os.getenv('TMP'), self.csvname)
        self.s3.download_file(Bucket=self.targetBucket, Key=self.srccsvfile, Filename=fileName)

        # read the data and count how many rows i need
        df = pd.read_csv(fileName)
        df = df.fillna('')
        self.orig_hdrs = df.columns.tolist()
        df2=df[['deleted','Type','Item','Contact_n','contact_p','Contact_e','Price','Description','url1','url2','url3', 'recDt']]
        self.hdrs = df2.columns.tolist()
        self.fsdata = df2.values.tolist()
        self.rows = len(self.fsdata)
        print(f'read {self.rows} rows from {fileName}')
        return 
    
    def saveData(self):
        uplName = os.path.join(os.getenv('TMP'), self.newname)
        df2 = pd.DataFrame(self.fsdata, columns=self.hdrs)
        df = df2[self.orig_hdrs].copy()
        now = datetime.datetime.now()
        df['age']=[(now - datetime.datetime.strptime(str(ds),'%Y%m%d%H%M%S')).days for ds in df.recDt]
        nold = len(df[df.age>=MAXAGE])
        if nold > 0:
            print(f'deleting entries more than {MAXAGE} days old')
            print(df[df.age>=50])
        df = df[df.age<50]
        df = df.drop(columns=['age'])
        df.to_csv(uplName, index=False)

        self.s3.upload_file(Bucket=self.targetBucket, Key=self.srccsvfile, Filename=uplName)

        # update the webpage - retry a few times if necessary
        retries = 0
        succ = createJsFromCSV.main(self.cfgfile)
        while succ is False and retries < 5:
            print('retrying...')
            time.sleep(3)
            succ = createJsFromCSV.main(self.cfgfile)
            retries += 1
        if not succ:
            messagebox.showinfo("Freecycle GUI", "Webpage NOT updated, please try again")
            return False
        else:
            messagebox.showinfo("Freecycle GUI", "Webpage Refreshed")
            return True



if __name__ == '__main__':
    if len(sys.argv) > 1:
        root = tk.Tk()
        root.geometry('+0+0')
        app = fsEditor(root, sys.argv[1])
        root.protocol('WM_DELETE_WINDOW', app.quitApplication)
        root.mainloop()
    else:
        print('usage: python editorGUI.pi config.ini')
