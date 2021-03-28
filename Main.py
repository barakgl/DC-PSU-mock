from functools import partial

import PySimpleGUI as sg
import datetime
import logzero
from logzero import logger

from CapsLockListener import start_listen
from DC_PSU import DCPowerSupplyUnit, State
from Images.images import Buttons

# Theme of the GUI #
sg.theme('Reddit')


# Logger settings #
logzero.json()
logzero.logfile(f"./logs/psu_{datetime.datetime.now().strftime('%m-%d-%Y, %H-%M')}.log")


def change_frame_status(window: sg.Window, key, status, psu):
    """
    Updates a specific channel frame element in the main GUI according to the status argument.
    :param window: sg.Window object
    :param key: int/str key of the objects group
    :param status: bool
    :param psu: DCPowerSupplyUnit object
    :return:
    """
    psu.disable_channel(1)
    psu.disable_channel(2)
    window[f'{key}_toggle'].update(disabled=status, checkbox_color='red', value=False)
    window[f'{key}_spin'].update(disabled=status, value=0)
    window[f'{key}_play'].update(disabled=status, text='Play', button_color='grey')


def channel_frame(title, key, max_volt):
    """
    Creates a frame of a single channel panel.
    :param title: str title
    :param key: key for the buttons/toggles of the frame panel.
    :param max_volt:
    :return:
    """
    frame_layout = [
        sg.T(f'Active'),
        sg.Checkbox(text='', checkbox_color='red', key=f'{key}_toggle', enable_events=True, size=(3, 1), disabled=True),
        sg.T(f'Amplitude'),
        sg.Spin(values=[i for i in range(max_volt)], size=(4, 1), key=f'{key}_spin', disabled=True),
        sg.T(f'V'),
        sg.Button(key=f'{key}_play', button_text='Play', button_color='grey', disabled=True)
    ]
    return sg.Frame(title, [frame_layout], font='Any 12', title_color='grey')


# - Click Handlers - #
def power_button_handler(window: sg.Window, psu: DCPowerSupplyUnit):
    """
    Power button event handler.
    Turn PSU on/off according to status.
    Enables/Disables other GUI element according to power status.
    :param window: sg.Window object
    :param psu: DCPowerSupplyUnit object
    :return:
    """
    element = window['power_button']
    if psu.status == State.OFF:
        if psu.power_on():
            logger.info('PSU turn on')
            # window['power'].update(value='Turn OFF')
            window['status'].update(value='Status: ON')
            element.update(image_data=Buttons.power_on_small)
            change_frame_status(window, '1', False, psu)
            change_frame_status(window, '2', False, psu)
    elif psu.status == State.ON:
        if psu.power_off():
            logger.info('PSU turn off')
            # window['power'].update(value='Turn ON')
            window['status'].update(value='Status: OFF')
            element.update(image_data=Buttons.power_off_small)
            change_frame_status(window, '1', True, psu)
            change_frame_status(window, '2', True, psu)


def channel_toggle_handler(window: sg.Window, psu: DCPowerSupplyUnit, ch_num: int):
    """
    Channel enable/disable toggle button event handler.
    Calls PSU class methods according to enable/disable status and channel number.
    Updates status bar in case of an error.
    :param window: sg.Window object
    :param psu: DCPowerSupplyUnit object
    :param ch_num: int channel number.
    :return:
    """
    key = f'{ch_num}_toggle'
    element = window[key]
    if window[f'{ch_num}_play'].ButtonText == 'Pause':
        window['status_bar'].update(f'Cannot change channel {ch_num} status while injecting.')
        return
    if window.ReturnValuesDictionary[key]:
        if psu.enable_channel(ch_num):
            logger.info(f'Channel {ch_num} enabled')
            element.update(checkbox_color='green')
    else:
        if psu.disable_channel(ch_num):
            logger.info(f'Channel {ch_num} disabled')
            element.update(checkbox_color='red')


def channel_play_handler(window: sg.Window, psu: DCPowerSupplyUnit, ch_num: int):
    """
    Play button event handler.
    Calls PSU class methods according to play/pause status and channel number.
    Updates status bar in case of an error.
    :param window: sg.Window object
    :param psu: DCPowerSupplyUnit object
    :param ch_num: int channel number.
    :return:
    """
    key = f'{ch_num}_play'
    amp = window[f'{ch_num}_spin'].get()
    element = window[key]
    if element.get_text() == 'Play':
        if psu.channels[ch_num - 1].state == State.OFF:
            window['status_bar'].update(f'Channel {ch_num} is disabled.')
            return
        if psu.set_ch_amp(ch_num, amp):
            if psu.channel_on(ch_num):
                logger.info(f'Channel {ch_num} injecting ')
                element.update(text='Pause', button_color='green')
    else:
        if psu.channel_off(ch_num):
            # element.ButtonText = ''
            logger.info(f'Channel {ch_num} stopped injection.')
            element.update(text='Play', button_color='grey')


# - Main Window - #
def main():
    """
    Main GUI loop.
    Create a layout, run event loop and event handlers calls.
    :return:
    """
    psu = DCPowerSupplyUnit('sn')
    psu.connect('someip', 'user', 'password')

    layout = [
        [sg.T(' ' * 55), sg.T('Status: OFF', key='status')],
        [channel_frame('Channel 1', '1', 24)],
        [channel_frame('Channel 2', '2', 24)],

        [sg.T(' ' * 30), sg.Text('', key='power')],
        [sg.T(' ' * 30), sg.Button(image_data=Buttons.power_off_small, size=(10, 10), key='power_button')]
        ,
        [sg.Text(size=(40, 0), key='status_bar')],
        [sg.Button('Exit')]]

    window = sg.Window('DC Power Supply Unit Controller', layout)
    power_handler = partial(power_button_handler, window, psu)
    start_listen(power_handler)
    while True:  # Event Loop
        event, values = window.read()
        logger.info(event)
        window['status_bar'].update(value='')
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if 'power_button' in event:
            power_button_handler(window, psu)
        if 'toggle' in event:
            channel_toggle_handler(window, psu, int(event[0]))
        if 'play' in event:
            channel_play_handler(window, psu, int(event[0]))

    window.close()


if __name__ == '__main__':
    main()
