#!/usr/bin/env python3

# Main program file.
# Main drawing loop handled in this file.
# Event queue is processed in this file.


import mtgsdk, sys, requests, os, multiprocessing, ntpath

from collectiondata import CollectionData
from requester import Requester
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from ui.cardviewer import CardViewer

class Application(object):
    def __init__(self):
        self.requester = Requester()
        self.window = Tk()
        self.window.title("MTG Collection Tracker")
        self.tab_control = ttk.Notebook(self.window)

        # create a toplevel menu
        menubar = Menu(self.window)
        filemenu = Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Save", command=self.save_collection)
        filemenu.add_command(label="Save as", command=self.save_collection_as)
        filemenu.add_command(label="Open", command=self.open_collection)
        filemenu.add_command(label="New", command=self.new_collection)
        # display the menu
        self.window.config(menu=menubar)
        

        searchable = Requester()
        self.web_searcher = CardViewer(self.window, searchable, height=700, background='bisque')
        self.web_searcher.pack(side=LEFT, fill=BOTH, expand=True)

        self.web_searcher.rowconfigure(0, weight=1)

        # Text entry
        self.txt_entry = Entry(self.web_searcher, width=100)
        self.txt_entry.grid(column=0, row=1, sticky=S+W+E)

        # Search button
        search_button = Button(self.web_searcher, text='Search', command=lambda:self.web_searcher.load_cards(self.txt_entry.get()))
        search_button.grid(column=1,row=1, sticky=S)
        
        
        self.tab_control.pack(side=RIGHT, fill=BOTH, expand=True)
        


        
        self.window.mainloop()
    
    def save_collection(self):
        active_tab_name = self.tab_control.select()
        active_tab = self.tab_control.nametowidget(active_tab_name)

        # If the collection has a file_path we save to that file path
        # otherwise we use the "save as" saving
        if active_tab.collection.file_path:
            active_tab.collection.save()
        else:
            self.save_collection_as()
            
        

    def save_collection_as(self):
        file_path = asksaveasfilename(title='Save as', defaultextension='.json')
        active_tab_name = self.tab_control.select()
        active_tab = self.tab_control.nametowidget(active_tab_name)
        active_tab.collection.save_as(file_path)

        file_name = ntpath.basename(file_path)
        file_name_no_extension = os.path.splitext(file_name)[0]

        self.tab_control.tab(active_tab, text=file_name_no_extension)

    def new_collection(self):
        self.new_card_viewer_tab(CollectionData())
    
    def open_collection(self):
        file_path = askopenfilename(initialdir = "~/",title = "Select file",filetypes = (("json files","*.json"),("all files","*.*")))
        file_name = ntpath.basename(file_path)
        file_name_no_extension = os.path.splitext(file_name)[0]

        collection = CollectionData(file_path=file_path)

        self.new_card_viewer_tab(collection, file_name_no_extension)
    
    def new_card_viewer_tab(self, searchable, title='New Collection'):
        # Main tab
        new_tab = CardViewer(self.tab_control, searchable, height=700, background='bisque')
        self.tab_control.add(new_tab, text=title)

        new_tab.rowconfigure(0, weight=1)


        # Text entry
        txt_entry = Entry(new_tab, width=100)
        txt_entry.grid(column=0,row=1, sticky=S)

        # Search button
        search_button = Button(new_tab, text='Search', command=lambda:new_tab.load_cards(txt_entry.get()))
        search_button.grid(column=1,row=1)

if __name__ == "__main__":
    Application()


