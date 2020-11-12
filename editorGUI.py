import tkinter as tk
import csv
import os
from tkinter import messagebox
import boto3
import datetime
import createJsFromCSV

targetBucket = 'tv-freecycle'


def updateData():
    root = tk.Tk()

    root.grid_rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    frame_main = tk.Frame(root, bg="gray")
    frame_main.grid(sticky='news')
    frame_main.winfo_toplevel().title("Manage Freecycle Entries")

    # Create a frame for the canvas with non-zero row&column weights
    frame_canvas = tk.Frame(frame_main)
    frame_canvas.grid(row=2, column=0, pady=(5, 0), sticky='nw')
    frame_canvas.grid_rowconfigure(0, weight=1)
    frame_canvas.grid_columnconfigure(0, weight=1)

    # Set grid_propagate to False to allow resizing later
    frame_canvas.grid_propagate(False)

    # Add a canvas in that frame
    canvas = tk.Canvas(frame_canvas, bg="yellow")
    canvas.grid(row=0, column=0, sticky="news")

    # Link a scrollbar to the canvas
    vsb = tk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
    vsb.grid(row=0, column=1, sticky='ns')
    canvas.configure(yscrollcommand=vsb.set)

    # Create a frame to contain the buttons
    frame_buttons = tk.Frame(canvas, bg="blue")
    canvas.create_window((0, 0), window=frame_buttons, anchor='nw')

    s3 = boto3.client('s3')
    # upload flag to warn the email handler that the CSV file is in use
    s3.upload_file(Bucket=targetBucket, Key='inputs/inuse.txt', Filename='inuse.txt')

    # download the CSVfile
    keyName = 'inputs/freecycle-data.csv'
    fileName = os.path.join(os.getenv('TMP'), 'freecycle-data.csv')
    s3.download_file(Bucket=targetBucket, Key=keyName, Filename=fileName)

    # read the data and count how many rows i need
    rows = 0
    fsdata = []
    with open(fileName) as csvfile:
        rows = sum(1 for row in csvfile) - 1
        csvfile.seek(0)
        data = csv.reader(csvfile, delimiter=',')
        hdr = next(data)  # skip the header row
        for r in data:
            fsdata.append(r)

    rc = 0
    columns = 5
    buttons = [[tk.Entry() for j in range(columns)] for i in range(rows)]

    for r in range(rows):
        buttons[rc][0] = tk.Entry(frame_buttons, width=3)
        buttons[rc][0].insert("end", fsdata[rc][11])
        buttons[rc][0].grid(row=rc, column=0, sticky='news')
        buttons[rc][1] = tk.Button(frame_buttons, text=fsdata[rc][1])
        buttons[rc][1].grid(row=rc, column=1, sticky='news')
        buttons[rc][2] = tk.Button(frame_buttons, text=fsdata[rc][2])
        buttons[rc][2].grid(row=rc, column=2, sticky='news')
        buttons[rc][3] = tk.Button(frame_buttons, text=fsdata[rc][5])
        buttons[rc][3].grid(row=rc, column=3, sticky='news')
        buttons[rc][4] = tk.Button(frame_buttons, text=fsdata[rc][6])
        buttons[rc][4].grid(row=rc, column=4, sticky='news')
        rc += 1

    # function to save the data. Needs to be here as it needs 'rows'
    def saveme():
        with open('newfile.csv', 'w', newline='') as outfile:
            csvw = csv.writer(outfile, delimiter=',', lineterminator='\n')
            csvw.writerow(hdr)
            for i in range(rows):
                fsdata[i][11] = buttons[i][0].get()
                dateof = datetime.datetime.strptime(fsdata[i][0], '%Y%m%d%H%M%S')
                ageof = (datetime.datetime.now() - dateof).days
                if ageof < 50:
                    csvw.writerow(fsdata[i])
                else:
                    print('removing ', fsdata[i][2], ' as more than 7wks old')

        s3.upload_file(Bucket=targetBucket, Key=keyName, Filename="newfile.csv")

        # delete the flagfile, its now safe to update the CSV file
        s3.delete_object(Bucket=targetBucket, Key='inputs/inuse.txt')

        # update the webpage
        createJsFromCSV.main()

        messagebox.showinfo("Data saved", "Webpage Refreshed")
        root.destroy()

    label1 = tk.Button(frame_main, text="Save", fg="green", command=saveme)
    label1.grid(row=0, column=0, pady=(5, 0), sticky='nw')

    # Update buttons frames idle tasks to let tkinter calculate buttons sizes
    frame_buttons.update_idletasks()

    # Resize the canvas frame to show exactly 5-by-5 buttons and the scrollbar
    first5columns_width = sum([buttons[0][j].winfo_width() for j in range(0, 5)])
    first5rows_height = sum([buttons[i][1].winfo_height() for i in range(0, 20)])
    frame_canvas.config(width=first5columns_width + vsb.winfo_width(),
                        height=first5rows_height)

    # Set the canvas scrolling region
    canvas.config(scrollregion=canvas.bbox("all"))

    # Launch the GUI
    root.mainloop()
    
    # delete the flagfile, its now safe to update the CSV file
    s3.delete_object(Bucket=targetBucket, Key='inputs/inuse.txt')


if __name__ == '__main__':
    updateData()
