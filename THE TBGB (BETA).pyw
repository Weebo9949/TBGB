import tkinter as tk #gui for the menu
import pyautogui #controls keyboard
import pygetwindow as gw #gets window name and directory
import pyperclip #handles paste
import time #handles request limit
import webbrowser #spitting out windows
import subprocess #spitting out windows in new instances
import os #used for usb directory 
import win32api #used for usb directory
import win32file #used for usb directory
import ast #turns string got from txt into dictionary

###READ current next step, see the functions usbdrive quick save and get for what to do now after saving to a file the file needs to be read and turned
#into a dictionary and then appended into outdic for tabsgetter to work 

#devnotes:
#the code takes advantage of many prereques such as universally used hotkeys and directories thus, if one were to change
#settings for things such as hotkeys, directories or even an os that is not windows, this will not work

#future improvments:
#run some function that gets the directory to defualt browser instead of only chrome 
#sleeptime can be tested in the future for more time saving



outdic = [] #local storage for desired output
storage = {"sto1":None,"sto2":None,"sto3":None} #local storage for dictionary of dictionary of instances

#used ai for majority of finding drives and check if removable and getting match name
#gets a list of all drives, checks only removable drives and locks the location of "tbgb" the usb name
def find_usb_drive(drive_name):
    drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]  # Get all drives
    for drive in drives:
        # Get the drive type to check if it's a removable device (USB)
        drive_type = win32file.GetDriveType(drive)
        if drive_type == win32file.DRIVE_REMOVABLE:
            # Check if the drive's label matches the given drive name
            volume_name = win32api.GetVolumeInformation(drive)[0]
            if volume_name == drive_name:
                return drive
    return None

usb_drive = find_usb_drive("TBGB")
#used to check if the directory matches
print(usb_drive)


#function that takes all open tabs and throws dictionary of lists 
def tabsgetter():
    
    #check for if a single window of chrome is gone after deleting a tab
    def tabscheck(titleslen):
        titles = gw.getAllTitles() #if amount of legnth of window
        lencheck = len(titles) 
        if lencheck == (titleslen): #is equal to the amount of window at start delete another tab
            return (titleslen,True) #this current window still has more tabs, thus run again
        if lencheck == titleslen-1: #if not update the current length of all tabs and return false
            titleslen = titleslen-1 
            return (titleslen,False)
        else:
            titleslen = titleslen-1
            return (titleslen,False)
            
        
    #function accounts for windows with the same title, thus when stores will store into the same key
    #if this is found it is killed then renamed to ensure unique takees the list of titles of windows 
    def dupkiller(chrome_titles):
        rename = set() 
        count = {key:0 for key in chrome_titles} #dic doesnt take repeat 
        for i in range(len(chrome_titles)):
            curche = chrome_titles[i]
            count[curche] += 1 #update seen count
            if count[curche] > 1: #if seen key more then once 
                outadd = curche + str(count[curche]-1)
                rename.add(outadd) #change the next one 
            else:
                rename.add(curche) #or just add 
        return(rename) #give back set of names which ensures there is definetly no dups

    #tabsgetter run starts here 
    windows = gw.getAllWindows() #get windows directory
    
    chrome_windows = [window for window in windows if "Google Chrome" in window.title] #list of chrome window directory 

    titles = gw.getAllTitles() #get windows titles

    chrome_titles = [title for title in titles if "Google Chrome" in title] #list of chrome titles

    #apply dupkiller function to return a list of nice non-duplicated names 
    titset = dupkiller(chrome_titles)
    titli = list(titset)
    
    #dic for lists of urls for each window
    urldic = {key:[] for key in titset}

    #original amount of windows before killing
    titleslen = len(gw.getAllTitles())
    print(titleslen)#checks if this number makes sense 

    #killing stuff and adding begins
    for i in range(len(titset)): # runs the program for each window instance of chroeme
        window = chrome_windows[i]
        #working on the current chrome directory
        
        #essentially brings up this directory and fullscreen the window
        if window.isMinimized:
            window.restore() 
        time.sleep(0.5)
        window.activate()
        time.sleep(0.5)
        window.maximize()
        time.sleep(0.5)
        print("window out passed") #checking if the right directory pulled out right
        
        #after the current insance of the window is pulled out we can run autoscript
        while True:
            checkthing = tabscheck(titleslen) #get a list in form [titleslen, T/F] 
            print(checkthing)
            if checkthing[1] == True: #if test is passed this window is not yet dead, run 
                pyautogui.click(200,200) #autoscript that gets the url and kills the current tab
                pyautogui.hotkey("ctrl", "l")
                pyautogui.hotkey("ctrl", "x")
                copied_content = pyperclip.paste() 
                urldic[titli[i]].append(copied_content) #here is where the url is saved, in the list of the right key
                time.sleep(0.5) #using sleep to avoid bugs 
                pyautogui.hotkey("ctrl", "w")
                time.sleep(0.5)
                titleslen = checkthing[0]
                print(titleslen)
            else: #if not ok (meaning the currently worked on window died) update 
                  #then run next instance 
                titleslen = checkthing[0] #updates the length of the titles 
                print(titleslen)
                break
    outdic.append(urldic) #after everything we now have the dic put this in local libary for use
    print(urldic)

#funtion takes list of ONE window and spits it out
#used ai to help with subprocess tool that ensures each instance i run will open in a new window 
def windowspitter(urls):#takes a list spits the window of urls
    #loop for list
    for index, url in enumerate(urls):
        if index == 0:
            # if first one new window open
            subprocess.Popen(["C:/Program Files/Google/Chrome/Application/chrome.exe", "--new-window", url])
        else:
            # if not first one open in SAME window
            subprocess.Popen(["C:/Program Files/Google/Chrome/Application/chrome.exe", url])
        time.sleep(0.5)  # Small delay to ensure proper opening

#function to spit tabs 
def tabsspitter():
    #runs windowspitter for each key value pair
    keylist = list(outdic[0].keys())
    for i in range(len(keylist)):
        curlist = outdic[0][keylist[i]]
        windowspitter(curlist)
    outdic.clear

#most functions have the line "outdic.clear" at some point to ensure integrity of the localsave always ensuring only 1 thing is in it
#function responsible to run the gui of the "storage" menu 
def tabstorage():
    #*these functions are based off "quickspit" a fucnction later in the code
    #function that is used to shoot data from a save on the usb which allows the files to be independent from the computer
    #storage1,2,3 do the same thing to its different save files 
    def storage1():
        outdic.clear 
        with open(usb_drive + "Sto1.txt", "r") as file:
            adddics = file.read() #reads the entire file as one string
            adddic = ast.literal_eval(adddics) #the string gotten would be a dic of list turn this string into dic
            outdic.append(adddic)#append into local save 
            print(outdic)
        tabsspitter() #spit it out
        
    def storage2():
        outdic.clear
        with open(usb_drive + "Sto2.txt", "r") as file:
            adddics = file.read()
            adddic = ast.literal_eval(adddics)
            outdic.append(adddic)
            print(outdic)
        tabsspitter()
        
    def storage3():
        outdic.clear
        with open(usb_drive + "Sto3.txt", "r") as file:
            adddics = file.read()
            adddic = ast.literal_eval(adddics)
            outdic.append(adddic)
            print(outdic)
        tabsspitter()


    popup = tk.Toplevel() #new independent window
    popup.title("Manage Stored Tabs")
    
    # Add buttons to this popup window
    
    #this brings to the function stochoser which is responsible for saving of storages
    storeadd = tk.Button(popup, text="add an instance to a storage", command=stochoser)
    storeadd.pack(pady=20)  # Adds some space around the button
    
    #these spit the save of the its storage
    sto1 = tk.Button(popup, text="restore storage 1", command=storage1)
    sto1.pack(pady=20)  # Adds some space around the button
    
    sto2 = tk.Button(popup, text="restore storage 2", command=storage2)
    sto2.pack(pady=20)  # Adds some space around the button
    
    sto3 = tk.Button(popup, text="restore storage 3", command=storage3)
    sto3.pack(pady=20)  # Adds some space around the button
    
    popup.mainloop()  # Start the popup window"s event loop

#"quick" refers to the main instance of storing/output in main page
#this function runs tabsgetter, tells quicksave to store it then clears localsave
def quickget():
    outdic.clear
    tabsgetter()
    print("before quicksave") #before and after to ensure the usb saved something 
    quicksave()
    print("after quicksave")
    outdic.clear

#function saves instance gotten from quickget
def quicksave():
    addic = str(outdic[0]) #takes which is in the local save (dic)
    print(addic) #tests if its correct format
    #using with open "w" as a cheap trick to clear the file
    with open(usb_drive + "Quick.txt", "w") as file:
        pass
    #add the dic
    with open(usb_drive + "Quick.txt", 'a') as file:
        file.write(addic)
    #tells tester the txt saved properly
    print("Content successfully appended to the file.")

#function spits the main save instance ***
def quickspit():
    outdic.clear
    #opens the save file
    with open(usb_drive + "Quick.txt", "r") as file:
        adddics = file.read() #reads and takes as a string
        adddic = ast.literal_eval(adddics) #turns it into dic
        outdic.append(adddic) #puts into localsave for tabspitter
        print(outdic) #tests if correct 
    tabsspitter() #outputs it

#stbstosto1,2,3, same logic and based off quicksave does essentially the same thing
def tabstosto1():
    outdic.clear
    tabsgetter()
    addic = str(outdic[0])
    with open(usb_drive + "Sto1.txt", "w") as file:
        pass
    with open(usb_drive + "Sto1.txt", 'a') as file:
        file.write(addic)
    print("Content successfully appended to the file.")
    outdic.clear

def tabstosto2():
    outdic.clear
    tabsgetter()
    addic = str(outdic[0])
    with open(usb_drive + "Sto2.txt", "w") as file:
        pass
    with open(usb_drive + "Sto2.txt", 'a') as file:
        file.write(addic)
    print("Content successfully appended to the file.")
    outdic.clear

def tabstosto3():
    outdic.clear
    tabsgetter()
    addic = str(outdic[0])
    with open(usb_drive + "Sto3.txt", "w") as file:
        pass
    with open(usb_drive + "Sto3.txt", 'a') as file:
        file.write(addic)
    print("Content successfully appended to the file.")
    outdic.clear
    
#same function from before with same name, put here for convenience and future usage 
def storage1():
    outdic.clear
    with open(usb_drive + "Sto1.txt", "r") as file:
        adddics = file.read()
        adddic = ast.literal_eval(adddics)
        outdic.append(adddic)
        print(outdic)
    tabsspitter()
    
def storage2():
    outdic.clear
    with open(usb_drive + "Sto2.txt", "r") as file:
        adddics = file.read()
        adddic = ast.literal_eval(adddics)
        outdic.append(adddic)
        print(outdic)
    tabsspitter()
    
def storage3():
    outdic.clear
    with open(usb_drive + "Sto3.txt", "r") as file:
        adddics = file.read()
        adddic = ast.literal_eval(adddics)
        outdic.append(adddic)
        print(outdic)
    tabsspitter()
    
    
#first menu was made based on an abetrary example from ai
#function responsible for gui for storing instances to the storage vault
def stochoser():    
    popup = tk.Toplevel()
    popup.title("Choose a storage")
    # Add buttons to this popup window
    storeadd = tk.Button(popup, text="save to storage 1", command=tabstosto1)
    storeadd.pack(pady=20)  # Adds some space around the button
    
    sto1 = tk.Button(popup, text="save to storage 2", command=tabstosto2)
    sto1.pack(pady=20)  # Adds some space around the button
    
    sto2 = tk.Button(popup, text="save to stroage 3", command=tabstosto3)
    sto2.pack(pady=20)  # Adds some space around the button
    
    popup.mainloop()  # Start the popup window"s event loop


#MENU BEGINS HERE 
root = tk.Tk() #starts tab
root.title("THE EPIC TABSGETTER") #names it


# Creates the command that adds tabs 
tabgetter = tk.Button(root, text="Store current tabs", command=quickget)
tabgetter.pack(pady=20)  # Adds some space around the button

# Creates the command that spits tabs
quickspit = tk.Button(root, text="retores last stored tabs", command=quickspit)
quickspit.pack(pady=20)  # Adds some space around the button

# Creates the command that stores instances
tabstore = tk.Button(root, text="check your storage of tabs", command=tabstorage)
tabstore.pack(pady=20)

# Start the GUI event loop
root.mainloop()
