"""
This module sends specific OBS notifications to the macOS Notifications Center
via osascript. Specifically, it sends a notification when: (1) recording
starts, (2) recording stops (with total recording duration), and (3) the replay
buffer is saved. Additionally, it features starting the replay buffer
automatically on OBS start.
Author: Ryan Sheatsley
Mon Oct 17 2022
"""
import datetime  # Basic date and time types
import obspython  # obs scripting
import subprocess  # Subprocess management

# current time
start = None


def get_event(event):
    """
    This function serves as the main event handler. That is, this method
    processes recording start, recording end, and replay buffer save.

    :param event: a triggered event
    :type event: enum
    :return: None
    :rtype: NoneType
    """
    global start
    if event == obspython.OBS_FRONTEND_EVENT_RECORDING_STARTED:
        start = datetime.datetime.now()
        start_msg = start.strftime("%I:%M:%S %p")
        msg = f"Recording started at {start_msg}"
        print(msg)
        subprocess.call(
            [
                "osascript",
                "-e",
                f'display notification "{msg}" with title "OBS"',
            ]
        )
    elif event == obspython.OBS_FRONTEND_EVENT_RECORDING_STOPPED:
        stop = datetime.datetime.now()
        now = stop.strftime("%I:%M:%S %p")
        msg = f"Recording stopped at {now}. Duration: {str(stop - start).split('.')[0]}"
        print(msg)
        subprocess.Popen(["osascript", "-e", msg])
        subprocess.call(
            [
                "osascript",
                "-e",
                f'display notification "{msg}" with title "OBS"',
            ]
        )
    elif event == obspython.OBS_FRONTEND_EVENT_REPLAY_BUFFER_SAVED:
        now = datetime.datetime.now().strftime("%I:%M:%S %p")
        msg = f"Replay buffer saved at {now}"
        print(msg)
        subprocess.call(
            [
                "osascript",
                "-e",
                f'display notification "{msg}" with title "OBS"',
            ]
        )
    elif event == obspython.OBS_FRONTEND_EVENT_REPLAY_BUFFER_STOPPED:
        msg = "Replay buffer stopped"
        print(msg)
        subprocess.call(
            [
                "osascript",
                "-e",
                f'display notification "{msg}" with title "OBS"',
            ]
        )
    return None


def script_defaults(settings):
    """
    This function sets the default value for automatically enabling the replay
    buffer to false.

    :param settings: current data settings
    :type settings: obs_data_t object (SwigPyObject)
    :return: None
    :rtype: NoneType
    """
    obspython.obs_data_set_default_bool(
        settings,
        "enableRB",
        True if obspython.obs_frontend_replay_buffer_active() else False,
    )
    return None


def script_description():
    """
    This function returns a description string describing this module.

    :return: the description string
    :rtype: string
    """
    return """
    <center><h2>Recording Notifications</h2></center> <p>Sends notifications to
    the macOS Notification Center (via osascript) when recording starts, stops,
    or when a replay buffer is saved. As an additional feature, it also allows
    automatically starting the replay buffer when OBS starts.</p>

    Author: <a href="https://sheatsley.me">Ryan Sheatsley</a><br>
    Date: October 17th, 2022<br>
    Version: 1.0<br>
    Source: <a href="https://github.com/sheatsley/obs-scripts">GitHub</a><br>
    """


def script_load(settings):
    """
    This function sets up the necessary signal handlers to send appropriate
    notifications and enables the replay buffer (if enabled).

    :param settings: current data settings
    :type settings: obs_data_t object (SwigPyObject)
    :return: None
    :rtype: NoneType
    """
    print("Configuring callback...")
    obspython.obs_frontend_add_event_callback(get_event)
    print("Callback configured successfully")
    enable_replay_buffer = obspython.obs_data_get_bool(settings, "enableRB")
    if enable_replay_buffer:
        print("Enabling replay buffer...")
        obspython.obs_frontend_replay_buffer_start()
        print("Replay buffer enabled")
    return None


def script_properties():
    """
    This function populates the GUI and sets callbacks for turning the replay
    buffer on automatically.

    :return: OBS properties
    :rtype: obs_properties_t object
    """
    properties = obspython.obs_properties_create()
    obspython.obs_properties_add_bool(
        properties, "enableRB", "Start replay buffer automatically."
    )
    return properties


def script_unload():
    """
    This function releases any held objects and removes callbacks.

    :return: None
    :rtype: NoneType
    """
    print("Script unloading. Releasing objects and removing callbacks...")
    obspython.obs_frontend_remove_event_callback(get_event)
    return None


def script_update(settings):
    """
    This function is called when automatically enabling the replay buffer is
    toggled (in addition to once after the script loads).

    :param settings: current data settings
    :type settings: obs_data_t object (SwigPyObject)
    """
    start_replay_buffer = obspython.obs_data_get_bool(settings, "enableRB")
    if start_replay_buffer and not obspython.obs_frontend_replay_buffer_active():
        print("Starting replay buffer...")
        obspython.obs_frontend_replay_buffer_start()
        print("Replay buffer started")
    elif not start_replay_buffer and obspython.obs_frontend_replay_buffer_active():
        print("Stopping replay buffer...")
        obspython.obs_frontend_replay_buffer_stop()
        print("Replay buffer stopped")
