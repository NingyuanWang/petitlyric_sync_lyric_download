from petitlyrics import find_lyric_folder
from tkinter import filedialog
from tkinter import *

def main():
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    find_lyric_folder(folder_selected)

if __name__ == '__main__':
    main()
