#!/usr/bin/env python
import os
from enum import IntEnum

import guizero

from modules import TranslationAPI


class OpMode(IntEnum):
    OP_ONLINE = 1
    OP_OFFLINE = 2


class LangMode(IntEnum):
    SRC_FIRST = 0
    DEST_FIRST = 1


resetActive = False
my_op_mode: OpMode = OpMode.OP_ONLINE
my_lang_mode: LangMode = LangMode.SRC_FIRST

SOURCE_TEXT = "Source"
TRANSLATION_TEXT = "Translation"
FILES_DIR = "./word_lists"
DEFAULT_SRC_LANG = "en"
DEFAULT_DEST_LANG = "fil"

# List of Files with word lists
fileList = []
wordList = []
curWord = 0
curFileNum = 0
srcWord = ""
destWord = ""

SAVED_PHRASES_FILE = '.00_saved.txt'

# TOGGLE BUTTON - ICON WILL SWITCH
ICON_ONLINE = './icons/online2.png'
ICON_OFFLINE = './icons/offline2.png'

# TOGGLE BUTTON
# TEXT WILL SWITCH: E->T, T->E
ICON_SWITCH_E_T = './icons/switch_e_t2.png'
ICON_SWITCH_T_E = './icons/switch_t_e2.png'

# MAIN ACTION BUTTON
#   IN ONLINE MODE switches between
#      * TRANSLATE
#      * RESET
#   IN OFFLINE MODE is NEXT
ICON_TRANSLATE = './icons/translate2.png'
ICON_RESET = './icons/reset2.png'
ICON_NEXT_WORD = './icons/next_word2.png'

# These 2 icons swap between online/offline
# SAVE AND NEXT FILE BUTTON
ICON_SAVE = './icons/save2.png'
ICON_NEXT_FILE = './icons/next_file2.png'

# EXIT BUTTON
ICON_EXIT = './icons/exit2.png'

ICON_WIDTH = 48
BUTTON_WIDTH = 64
BUTTON_PAD = 8
# ICON_BG="white"

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
BORDER_PADDING = 5
BORDER_COLOR = "DeepSkyBlue1"
DEFAULT_FONT_SIZE = 24

grpBoxes = {str: guizero.TitleBox}
textBoxes = {str: guizero.TextBox}

DEFAULT_SOURCE_CAPTION = "Enter text to translate"

appDelay = 4  # seconds


def init_me():
    global wordList, fileList, curFileNum, my_op_mode
    load_file_list()

    if len(fileList) == 0:
        print("No word files found!")
        my_op_mode = OpMode.OP_ONLINE

    if OpMode.OP_OFFLINE == my_op_mode:

        wordList = load_file(fileList[curFileNum])
        if len(wordList) == 0:
            print("No words found in first file: " + fileList[curFileNum])
        else:
            grpBoxes[SOURCE_TEXT].text = fileList[curFileNum]
            display_word()

    handle_app_resize()


def handle_lang_mode_change():
    global ICON_SWITCH_E_T, ICON_SWITCH_T_E, ICON_TRANSLATE, \
        langModeToggle, my_op_mode, resetActive, mainActionButton

    if LangMode.SRC_FIRST == my_lang_mode:
        langModeToggle.image = ICON_SWITCH_E_T
    else:
        langModeToggle.image = ICON_SWITCH_T_E

    if OpMode.OP_OFFLINE == my_op_mode:
        display_word()
    else:
        reset_screen()
        resetActive = False
        mainActionButton.image = ICON_TRANSLATE


def change_lang_mode():
    global my_lang_mode

    if LangMode.SRC_FIRST == my_lang_mode:
        my_lang_mode = LangMode.DEST_FIRST
    else:
        my_lang_mode = LangMode.SRC_FIRST

    handle_lang_mode_change()


def handle_op_mode_change():
    global my_op_mode, curWord, curFileNum, fileList, opModeToggle, \
        wordList, resetActive

    if OpMode.OP_OFFLINE == my_op_mode:
        nextFileButton.enable()
        opModeToggle.image = ICON_OFFLINE
        curFileNum = 0
        wordList = load_file(fileList[curFileNum])
        curWord = 0
        grpBoxes[SOURCE_TEXT].text = fileList[curFileNum]
        display_word()
    else:
        nextFileButton.disable()
        opModeToggle.image = ICON_ONLINE
        grpBoxes[SOURCE_TEXT].text = DEFAULT_SOURCE_CAPTION
        reset_screen()
        resetActive = False
        mainActionButton.image = ICON_TRANSLATE


def change_op_mode():
    global my_op_mode

    if OpMode.OP_ONLINE == my_op_mode:
        my_op_mode = OpMode.OP_OFFLINE
    else:
        my_op_mode = OpMode.OP_ONLINE

    handle_op_mode_change()


def handle_main_action():
    global my_op_mode, resetActive, mainActionButton
    global ICON_TRANSLATE, ICON_RESET

    if OpMode.OP_OFFLINE == my_op_mode:

        go_next()
    else:
        # Are we translating or are we resetting
        if resetActive:
            reset_screen()
            mainActionButton.image = ICON_TRANSLATE
            resetActive = False
        else:
            get_translation()
            resetActive = True
            mainActionButton.image = ICON_RESET


def clean_text_for_submission(src_txt):
    print("Source Text before cleaning: " + src_txt)

    uglies = "`~\r\n\\t@#$%^&*()+={}[]|/\\:<>\"'"
    ret = src_txt
    ret = ret.strip()

    x = 0

    while x < len(uglies):
        ret = ret.replace(uglies[x], ' ')
        x += 1

    print("Source Text before cleaning: " + ret)

    return ret


def get_translation():
    global my_lang_mode, textBoxes, mainActionButton
    global ICON_RESET, TRANSLATION_TEXT, SOURCE_TEXT
    global DEFAULT_SRC_LANG, DEFAULT_DEST_LANG

    src_text = clean_text_for_submission(textBoxes[SOURCE_TEXT].value)
    src_lang = DEFAULT_SRC_LANG
    dest_lang = DEFAULT_DEST_LANG

    if LangMode.DEST_FIRST == my_lang_mode:
        dest_lang = DEFAULT_SRC_LANG
        src_lang = DEFAULT_DEST_LANG

    textBoxes[TRANSLATION_TEXT].value = TranslationAPI.get_translation(src_text, src_lang, dest_lang)


def handle_next_file():
    global curFileNum, fileList, wordList, curWord

    print("In handle next file")

    if curFileNum < len(fileList) - 1:
        curFileNum += 1
    else:
        curFileNum = 0

    wordList = load_file(fileList[curFileNum])
    curWord = 0
    display_word()


def go_next():
    global curWord, wordList, fileList, curFileNum

    if curWord < (len(wordList) - 1):
        curWord += 1
        display_word()
    else:
        if curFileNum < len(fileList) - 1:
            curFileNum += 1
        else:
            curFileNum = 0

        wordList = load_file(fileList[curFileNum])
        curWord = 0
        display_word()


def load_file_list():
    global fileList, FILES_DIR

    fileList = os.listdir(FILES_DIR)
    fileList.sort()


def do_quit():
    global app

    try:
        app.cancel(display_word)
    except InterruptedError:
        print("Error canceling displayWord in doQuit")

    app.after(10, exit_app)


def exit_app():
    global app

    print('We  are outta here!')

    try:
        app.destroy()
    except InterruptedError:
        print("Error destroying app")


def load_file(which_file):
    file1 = open(FILES_DIR + "/" + which_file, 'r', encoding="utf-8",
                 errors="ignore")

    return file1.readlines()


def reset_screen():
    global textBoxes, SOURCE_TEXT, TRANSLATION_TEXT

    textBoxes[SOURCE_TEXT].value = ""
    textBoxes[TRANSLATION_TEXT].value = ""


def handle_app_resize() -> None:
    global app, textBoxes

    cur_width = app.width
    fnt_size = get_new_font_size()
    textBoxes[SOURCE_TEXT].text_size = fnt_size
    textBoxes[SOURCE_TEXT].width = int(cur_width / fnt_size)
    textBoxes[TRANSLATION_TEXT].text_size = fnt_size
    textBoxes[TRANSLATION_TEXT].width = int(cur_width / fnt_size)

    topPadding.width = cur_width


def get_new_font_size() -> int:
    global DEFAULT_FONT_SIZE, app, SCREEN_WIDTH

    return int(DEFAULT_FONT_SIZE * (app.width / SCREEN_WIDTH))


def display_word():
    global curWord, appDelay, srcWord
    global destWord, wordList, textBoxes, SOURCE_TEXT
    global TRANSLATION_TEXT, my_lang_mode

    if curWord >= len(wordList):
        print("No words in list")
        return

    line = wordList[curWord]
    print(line)

    words = line.split("\t")

    if len(words) > 1:
        print(words[0])
        print(words[1])

        if my_lang_mode == LangMode.SRC_FIRST:
            srcWord = words[0]
            destWord = words[1]
        else:
            destWord = words[1]
            srcWord = words[0]

        textBoxes[SOURCE_TEXT].value = srcWord
        # time.sleep(appDelay)
        textBoxes[TRANSLATION_TEXT].value = destWord


app = guizero.App(title="svTranslator", layout="grid",
                  width=800, height=400, bg=(235, 235, 235))

# Add Widgets

# 1. Add row of controls for traversal, etc
controlBox = guizero.Box(app, align='left', border=BORDER_PADDING, grid=[0, 0], layout="grid")

# Add control buttons

# First set of Toggle Buttons
opModeToggle = guizero.PushButton(controlBox, width=BUTTON_WIDTH, padx=BUTTON_PAD, pady=BUTTON_PAD,
                                  image=ICON_ONLINE, grid=[1, 0], command=change_op_mode)

# Second set of Toggle Buttons
langModeToggle = guizero.PushButton(controlBox, width=BUTTON_WIDTH, padx=BUTTON_PAD, pady=BUTTON_PAD,
                                    image=ICON_SWITCH_E_T, grid=[2, 0], command=change_lang_mode)

pad1 = guizero.Text(controlBox, text="  ", grid=[3, 0])

# Main action button
# ***** In ONLINE MODE - toggles between:
# ********** TRANSLATE
# ********** RESET
# ***** In OFFLINE MOD - performs Next Word
mainActionButton = guizero.PushButton(controlBox, width=BUTTON_WIDTH, padx=BUTTON_PAD, pady=BUTTON_PAD,
                                      image=ICON_TRANSLATE, grid=[4, 0], command=handle_main_action)

# Next File Button, Disabled or hidden in ONLINE MODE
nextFileButton = guizero.PushButton(controlBox, width=BUTTON_WIDTH, padx=BUTTON_PAD, pady=BUTTON_PAD,
                                    image=ICON_NEXT_FILE, grid=[5, 0], enabled=False, command=handle_next_file)

pad2 = guizero.Text(controlBox, text="  ", grid=[6, 0])

quitButton = guizero.PushButton(controlBox, width=BUTTON_WIDTH, padx=BUTTON_PAD, pady=BUTTON_PAD,
                                image=ICON_EXIT, grid=[7, 0], command=do_quit)

# 2. Now add text areas to display verse
topPadding = guizero.Drawing(app, height=20, width=app.width, grid=[0, 2])

grpBoxes[SOURCE_TEXT] = guizero.TitleBox(app, text="Enter text to translate:", align="left",
                                         grid=[0, 3])
textBoxes[SOURCE_TEXT] = guizero.TextBox(grpBoxes[SOURCE_TEXT], text="", height=4, width=120,
                                         multiline=True, align="left")

grpBoxes[TRANSLATION_TEXT] = guizero.TitleBox(app, text='Translation:', align="left",
                                              grid=[0, 4])
textBoxes[TRANSLATION_TEXT] = guizero.TextBox(grpBoxes[TRANSLATION_TEXT], text="", height=4, width=120,
                                              multiline=True, align="left")

topPadding.bg = BORDER_COLOR

app.full_screen = True
app.after(20, init_me)
app.display()
