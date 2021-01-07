import requests
import PySimpleGUI as sg
import os.path
import action_event
from datetime import datetime
import time
import plyer.platforms.win.notification
from plyer import notification

current_milli_time = lambda: int(round(time.time() * 1000))
url = "https://api.kraken.com/0/public/Ticker"
currency_pair = "XXBTZEUR"
payload = {"pair": currency_pair}
last_poll = current_milli_time()
poll_offset = 1000
action_list = list()
value_list = list()
selected_action = None


#Price update
def update_current_value():
    req = requests.post(url, data=payload)
    if req.status_code != 200:
        print("Error: " + str(req.status_code))
        return
    data = req.json()
    if data["error"] != []:
        print("API Error")
        return
    result = data["result"]
    ask_price = result[currency_pair]["a"][0]
    return ask_price

def check_create_notification(current_value:float):
    for action in action_list:
        if action.notification_should_trigger(current_value):
            #toaster = ToastNotifier()
            #toaster.show_toast("Limit reached","Value is: " + str(current_value), threaded=True)
            notification.notify("Limit reached","Value is: " + str(current_value))
            
            action.notify_event()


# First the window layout in 2 columns

kraken_action = [
    [
        sg.Text(text="BTC Values:"),
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-VALUE LIST-"
        )
    ]
]

# For now will only show the name of the file that was chosen
kraken_display = [
    [
        sg.Text("Kraken Action"),
        sg.In(size=(25, 1), enable_events=True, key="-VALUE-")
    ],
    [
        sg.Button(key='-HIGHER-', button_text="higher"),
        sg.Button(key='-LOWER-', button_text="lower")
    ],
    [
        sg.Listbox(values=[], enable_events=True, size=(40,15),key="-LIMIT ACTIONS-")
    ],
    [
        sg.Button(key='-DELETE-', button_text="delete action"),
    ]
]

# ----- Full layout -----
layout = [
    [
        sg.Column(kraken_action),
        sg.VSeperator(),
        sg.Column(kraken_display)
    ]
]

window = sg.Window("Kraken Notificator", layout)

# Run the Event Loop
while True:
    
    
    event, values = window.read(timeout=0)
    
    if last_poll + poll_offset < current_milli_time():
        last_poll = current_milli_time()
        current_value = update_current_value()
        value_list.insert(0, current_value)
        s_values = [
            v
            for v in value_list
        ]
        check_create_notification(current_value)
        window["-LIMIT ACTIONS-"].update(action_list)
        window["-VALUE LIST-"].update(value_list)
        

    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    # Folder name was filled in, make a list of files in the folder
    if event == "-VALUE LIST-":
        value_selected = values["-VALUE LIST-"][0]
        window["-VALUE-"].update(value_selected)

    elif event == "-HIGHER-":
        limit_value = float(values["-VALUE-"])
        if limit_value > 0:
            new_action = action_event.Action(True, limit_value)
            action_list.append(new_action)
            window["-LIMIT ACTIONS-"].update(action_list)
    elif event == "-LOWER-":
        limit_value = float(values["-VALUE-"])
        if limit_value > 0:
            new_action = action_event.Action(False, limit_value)
            action_list.append(new_action)
            window["-LIMIT ACTIONS-"].update(action_list)
    elif event == "-LIMIT ACTIONS-":
        if len(values["-LIMIT ACTIONS-"]) > 0:
            selected_action = values["-LIMIT ACTIONS-"][0]

    elif event == "-DELETE-":
        if selected_action != None:
            if selected_action in action_list:
                action_list.remove(selected_action)
                window["-LIMIT ACTIONS-"].update(action_list)
    
    

    elif event == "-FILE LIST-":  # A file was chosen from the listbox
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            window["-TOUT-"].update(filename)
            window["-IMAGE-"].update(filename=filename)

        except:
            pass

window.close()