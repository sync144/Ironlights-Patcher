# Import statements -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfile
from os import path
from pathlib import Path
import os
import zipfile as z
import shutil
import subprocess
import time
import pathlib

# Window setup ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
wn = Tk()
wn.geometry("600x200")
wn.title("Ironlights Patcher v1.0")
wn.iconbitmap("ironlogo.ico")

# Variables ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
home = os.path.expanduser("~") # Gets the current PC username
style = ttk.Style(wn)

notiVar = StringVar() # Adjustable string variable for notification text
notiVar.set("No file selected.")

# Functions ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def doNothing():
    # A blank function that does nothing. For testing purposes.
    pass

def OpenBackupFolder():
    # This function is used to open the Ironlights APK backup folder from SideQuest. 
    # If an error is returned, a notification will show saying the folder was not found.

    try:
        os.startfile(f"{home}/AppData/Roaming/SideQuest/backups/com.emcneill.Ironlights/apks")
    except:
        messagebox.showerror("Backup Folder Not Found", "APK backup folder not found (was the APK backed up in SideQuest?)")

def PatchPC():
    # This function lets the user patch the PC sharedasset file of Ironlights

    global userSharedAsset
    global assetCopy
    userSharedAsset = askopenfile(initialdir=f"{home}/Documents", title="Select .assets File", filetypes=[("sharedasset Files", "*.assets")])

    if userSharedAsset is None:
        print("No file was selected, exiting...")
    else:
        print("File selected!")
        assetCopyFolder = f"{Path(os.path.dirname(userSharedAsset.name))}/assetCopy"

        if os.path.exists(assetCopyFolder): # Checks if the folder already exists, if it does it removes it.
            shutil.rmtree(assetCopyFolder)
            os.mkdir(assetCopyFolder)
        else:
            os.mkdir(assetCopyFolder) # Creates a new folder for the copy

        userSharedAsset.close()
        shutil.move(userSharedAsset.name, assetCopyFolder)
        shutil.copy2("sharedassets1.assets", Path(os.path.dirname(userSharedAsset.name)))
        messagebox.showinfo("Game Patched", "Game successfully patched! Asset file may now be modded.")

def UserSelectAPK():
    # This function allows the user to select the APK they wish to mod. 

    global userAPK
    try:
        userAPK = askopenfile(initialdir=f"{home}/AppData/Roaming/SideQuest/backups/com.emcneill.Ironlights/apks", title="Select APK Backup", filetypes=[("APK Files", "*.apk")])
    except:
        messagebox.showerror("Backup Folder Not Found", "APK backup folder not found (was the APK backed up in SideQuest?)")

    if (userAPK is None): # If no APK is selected, the UI will stay locked. If an APK is selected, the UI will be unlocked 
        print("No APK selected, keeping UI locked")
    else:
        messagebox.showinfo("APK Loaded", "Successfully loaded APK!")

        # All of this code enables UI elements, and fixes them.
        notiText.config(fg="black")
        notiVar.set("APK Selected")
        openBackup.config(state="normal")
        filemenu.entryconfig("Patch", state="normal")
        filemenu.entryconfig("Sign APK", state="normal")
        pathText.config(fg="black")
        pathBox.config(state="normal")
        pathBox.delete("1.0", END)
        pathBox.insert("1.0", userAPK.name)
        pathBox.config(state="disable")
        modAPK.config(state="disable")

        # Closes the file when operation is complete
        userAPK.close()

def patchAPK():
    # This function will patch the APK by simply just providing a sharedassets1 file with the modded tag.

    shutil.copy2("sharedassets1.assets", os.path.dirname(userAPK.name))
    messagebox.showinfo("APK Patched", "APK Patched! Asset file may now be modded, and imported using the \"Mod APK\" button.")
    filemenu.entryconfig("Patch", state="disable")
    modAPK.config(state="normal")

def signAPK():
    # This function will sign the APK using uber-apk-signer-1.2.1.jar.

    notiVar.set("Signing...")
    shutil.copy2("uber-apk-signer-1.2.1.jar", os.path.dirname(userAPK.name))
    os.chdir(os.path.dirname(userAPK.name))
    os.system(f"java -jar uber-apk-signer-1.2.1.jar --apks {os.path.basename(userAPK.name)} --debug")
    os.remove(f"{os.path.dirname(userAPK.name)}/uber-apk-signer-1.2.1.jar")
    os.remove(userAPK.name)
    notiVar.set("APK Signed")

def SwapSharedAsset():
    # This function will mod the APK by inserting the user's sharedasset file.

    # Preparing APK
    notiVar.set("Modding...")
    modAPK.config(state="disable") 
    filemenu.entryconfig("Open", state="disable")

    apkcopyFolder = f"{os.path.dirname(userAPK.name)}/apkcopy"

    if os.path.exists(apkcopyFolder): # Checks if the apkcopy folder already exists, if it does it removes it.
        shutil.rmtree(apkcopyFolder)
        os.mkdir(apkcopyFolder)
    else:
        os.mkdir(apkcopyFolder) # Creates a new folder for the copy
    shutil.copy2(userAPK.name, apkcopyFolder) # Makes a copy of the original APK and puts it into the new folder

    with z.ZipFile(userAPK.name, "a") as zipobj: # Accesses the zip file
        zipobj.write(f"{os.path.dirname(userAPK.name)}/sharedassets1.assets", "assets/bin/Data/sharedassets1.assets")
    zipobj.close()
    print("Zipobj closed")
    
    notiVar.set("Modding Complete")
    modAPK.config(state="normal") 
    filemenu.entryconfig("Open", state="normal")


# Widgets -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
openBackup = Button(wn, text="Open Ironlights Backup Folder", font=("Helvetica", 8), borderwidth=1, state="disable", command=OpenBackupFolder)
openBackup.place(x=445, y=3)

modAPK = Button(wn, text="Mod APK", font=("Helvetica", 12), borderwidth=1, state="disable", command=SwapSharedAsset)
modAPK.place(x=260, y=130)

notiText = Label(wn, textvariable=notiVar, font=("Roboto", 18, "bold"), fg="grey")
notiText.pack(side="top")

pathText = Label(wn, text="Path:", fg="grey")
pathText.place(x=151, y=78)

pathBox = Text(wn, width=30, height=1, state="disable", wrap="none")
pathBox.place(x=185, y=80)

scroll = Scrollbar(wn, command=pathBox.xview, orient="horizontal")
scroll.place(x=185, y=100, width=240)
pathBox.config(xscrollcommand=scroll.set)

menuBar = Menu(wn) # Creates the menu bar

# Creates the "File" option on the menu bar, along with the submenus for it.
filemenu = Menu(menuBar, tearoff=0)
filemenu.add_command(label="Open", command=UserSelectAPK)
filemenu.add_command(label="Patch", command=patchAPK, state="disable")
filemenu.add_command(label="Sign APK", command=signAPK, state="disable")
menuBar.add_cascade(label="File", menu=filemenu)

# Creates the "PC" option on the menu bar, along with the submenus for it.
pcmenu = Menu(menuBar, tearoff=0)
pcmenu.add_command(label="Patch", command=PatchPC)
menuBar.add_cascade(label="PC", menu=pcmenu)

# Creates the "Help" option on the menu bar, along with the submenus for it.
helpmenu = Menu(menuBar, tearoff=0)
helpmenu.add_command(label="Tutorial", command=doNothing)
menuBar.add_cascade(label="Help", menu=helpmenu)

# Finalization -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
wn.resizable(False, False)
wn.config(menu=menuBar) # Attaches the menu bar to the window
wn.mainloop()