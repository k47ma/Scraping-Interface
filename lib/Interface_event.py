# module for handling events


def on_enter(event):
    event.widget["bg"] = "#DCDCDC"


def on_leave(event):
    event.widget["bg"] = "#EFEFEF"


def on_click(event):
    event.widget["bg"] = "#BCBCBC"


def on_focusin(event):
    event.widget["bg"] = "#DCDCDC"


def on_focusout(event):
    event.widget["bg"] = "#FFFFFF"
