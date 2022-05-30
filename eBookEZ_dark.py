"""" eBookEZ_dark.py -- app that assists an eBook reader: the reader needs to select the word whose
    meaning they wish to find, and all they have to do is press CTRL + C or copy that text.
    Reader can put this app in some corner of screen, the app would always stay on top
    unless minimized or closed using respective buttons. The text of search bar updates
    in real-time as some text is copied.
    This dark version adjusts size and puts a dark theme for usability purposes.
"""

import tkinter as tk
import pyperclip
import re
import bs4
import requests
import time
import threading

app = tk.Tk()
app.title('eBookEZ')
app.lift()
app.attributes("-topmost", True)
app.resizable(0,0)

FONT_FAMILY = 'Segoe UI'
HEIGHT = 400
WIDTH = 300

app.iconbitmap('E:\Scripts\eBookEZ_icon.ico')

# function that gets the word from searchbar as arg and returns the meaning from the web
def find_meaning(words):

    initial_time = time.time()
    print('Words at start', words)
    baseSearchURL = 'https://www.google.com/search?q='
    query = 'some placeholder string'
    # QUERY
    wordsList = words.split(' ')
# so the split added a  n element in the list if word contained just one word, so i put the condition to remove that
    if wordsList[-1] == '\n':
        del wordsList[-1]
    print('words after split ', wordsList)
    if len(wordsList) == 0:
        result = "ERROR: No word to be searched!"
        # print(result)
        #return result
    elif len(wordsList) == 1:
        query = wordsList[0]
        # print('query1 ', query)
    elif len(wordsList) > 1:
        query = '+'.join(wordsList)
        # print('query2', query)

    searchURL = baseSearchURL + query + '+' + 'means'
    # print("Search URL: ", searchURL)
    googleSearchPage = requests.get(searchURL)
    googleSearchPageSoup = bs4.BeautifulSoup(googleSearchPage.text, 'html.parser')
    searchPageSimplified = googleSearchPageSoup.select('div')

    # desired element is at position 7 in the returned list i.e. searchPageSimplified
    desiredPart = str(searchPageSimplified[7])

    # regex for extracting word's definition
    defExtractorRE = re.compile('.*class="BNeawe s3v9rd AP7Wnd">([ a-zA-Z0-9.,;:–\'\"\-]*)</div></div><div.*', re.IGNORECASE)
    wordDef = defExtractorRE.findall(desiredPart)
    # print("definition: ", wordDef)
    definition = ''
    #print("wordDef len: {}".format(len(wordDef)))

    # here we check if the list wordDef contains more than one elements (each element 'should' be a definition but
    # may not be everytime). Regardless if it does, then due to limitation of space on app screen we limit definitions
    # to at most 2. but if list contains just 1 then we assign the first element to our new variable definition
    try:
        if len(wordDef)>1:
            for i in range(2):  # because we want at most 2 definitions
                definition += wordDef[i] + '\n'     # we insert \n with each element so when it displays, it's in a new line
        else:
            definition = wordDef[0]

        # now lets put the text in the defBox or definitions box!
        defBox['text'] = definition
    except:
        defBox['text'] = 'No definition found... :('

    #regex for extracting word's synonyms
    synExtractorRE = re.compile('.*class="r0bn4c rQMQod">synonyms: ([ a-zA-Z0-9.,;:–\'\"\-]*).*', re.IGNORECASE)
    wordSyns = synExtractorRE.findall(desiredPart)
    # print("synonyms: ", wordSyns)
    #print("wordSyns len: {}".format(len(wordSyns)))
    synonyms = ''
    try:
        if len(wordSyns) > 1:
            for i in range(2):
                synonyms += wordSyns[i]
        else:
            synonyms = wordSyns[0]

        # now lets put text in the synBox or synonyms box!
        synBox['text'] = synonyms
    except:
        synBox['text'] = 'No synonyms found... :('

    final_time = time.time()
    net_time = final_time - initial_time
    # print("Time taken: {}".format(net_time))


# the following function compares the text in search bar with current clipboard text and updates in case of change
def clipboard_monitor(lastClipboardText):
    while True:
        # we check clip board after every second
        time.sleep(0.5)
        clipboard_text_rn = pyperclip.paste()
        if str(lastClipboardText) != str(clipboard_text_rn):
            searchBar.delete('1.0', 'end')
            searchBar.insert('1.0', clipboard_text_rn)
            # the statement below is needed bcs otherwise the lastCLipboardText stays the same as the very first
            # clipboardtext when the code in the bottom(i.e. in gui section) runs.
            # so we need to update the last clipboardtext variable otherwise it keeps replacing the search bar text
            # with the current clipboardtext as the if condition above becomes true each time
            lastClipboardText = clipboard_text_rn

mainCanvas = tk.Canvas(app, height=HEIGHT, width=WIDTH, bg='#202529', bd=0, highlightthickness=0)
mainCanvas.pack()

# BANNER BANNER BANNER
logo_banner_img = tk.PhotoImage(file='./eBookEZ_banner_dark.png')
#bannerLabel = tk.Label(app, image=logo_banner_img)
#bannerLabel.place(relx=0.18, rely=0.01, relwidth=0.63, relheight=0.15)
mainCanvas.create_image(150, 25, image=logo_banner_img)

upperFrame = tk.Frame(app, bg='#1e1e1e')
upperFrame.place(relx=0.05, rely=0.15, relwidth=0.9, relheight=0.1, anchor='nw')

# Get the copied word (text) from the clipboard and paste it into the search bar
searchBar = tk.Text(upperFrame, bg='#32383D', fg='white', font=(FONT_FAMILY, 15), bd=0)
clipboardText = pyperclip.paste()

searchBar.insert('1.0', clipboardText)
searchBar.place(relx=0.01, rely=0.1, relwidth=0.65, relheight=0.8)

# lets now create start our clipboard monitor in a new thread
threadObj = threading.Thread(target=clipboard_monitor, args=[clipboardText])
threadObj.start()


searchButton = tk.Button(upperFrame, bg='#32383D', fg='#9e9e9e', text='MEANING', font=(FONT_FAMILY, 8, 'bold'), bd=0,
                         command=lambda:find_meaning(searchBar.get('1.0', 'end')))
searchButton.place(relx= 0.72, rely=0.1, relwidth=0.25, relheight=0.8)

lowerFrame = tk.Frame(app, bg='#1e1e1e')
lowerFrame.place(relx=0.05, rely=0.3, relwidth=0.9, relheight=0.65, anchor='nw')

# definitions box title
defBoxTitle = tk.Label(lowerFrame, font=(FONT_FAMILY, 10, 'bold'), bg='#4C555C', fg='#9e9e9e')
defBoxTitle.place(relwidth=1, relheight=0.1)
defBoxTitle['text'] = "Definition(s):"
# definition box
defBox = tk.Label(lowerFrame, font=(FONT_FAMILY, 10, 'italic'), bg='#32383D', justify='left', anchor='nw', fg='white', wraplength=240)
defBox.place(rely=0.1, relwidth=1, relheight=0.4)

# synonyms box title
synBoxTitle = tk.Label(lowerFrame, font=(FONT_FAMILY, 10, 'bold'), bg='#4C555C', fg='#9e9e9e')
synBoxTitle.place(rely=0.5, relwidth=1, relheight=0.1)
synBoxTitle['text'] = "Synonym(s):"
# synonyms box
synBox = tk.Label(lowerFrame, font=(FONT_FAMILY, 10, 'italic'), bg='#32383D', justify='left', anchor='nw', fg='white', wraplength=240)
synBox.place(rely=0.6, relwidth=1, relheight=0.4)

app.mainloop()
