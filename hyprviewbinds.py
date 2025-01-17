#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import subprocess
import json
import re
import sys


def main():
    win = Gtk.Window(title="HyprViewBinds")
    win.set_default_size(500, 300)
    win.set_border_width(15)

    vbox = Gtk.Box(
        spacing=10,
        orientation=Gtk.Orientation.VERTICAL
    )
    cbox = Gtk.Box()
    stack = Gtk.Stack()

    unsorted_binds = get_unsorted_binds_array()
    sorted_binds = get_sorted_binds_array(unsorted_binds)

    all_binds_scroller = Gtk.ScrolledWindow()
    application_binds_scroller = Gtk.ScrolledWindow()
    window_binds_scroller = Gtk.ScrolledWindow()
    workspace_binds_scroller = Gtk.ScrolledWindow()
    media_binds_scroller = Gtk.ScrolledWindow()

    all_binds_list = write_binds_list(unsorted_binds)
    application_binds_list = write_binds_list(sorted_binds["applications"])
    window_binds_list = write_binds_list(sorted_binds["windows"])
    workspace_binds_list = write_binds_list(sorted_binds["workspaces"])
    media_binds_list = write_binds_list(sorted_binds["media"])

    all_binds_tree_view = Gtk.TreeView(model=all_binds_list)
    application_binds_tree_view = Gtk.TreeView(model=application_binds_list)
    window_binds_tree_view = Gtk.TreeView(model=window_binds_list)
    workspace_binds_tree_view = Gtk.TreeView(model=workspace_binds_list)
    media_binds_tree_view = Gtk.TreeView(model=media_binds_list)

    render_tree_view_column(all_binds_tree_view, "Keybind", 0)
    render_tree_view_column(application_binds_tree_view, "Keybind", 0)
    render_tree_view_column(window_binds_tree_view, "Keybind", 0)
    render_tree_view_column(workspace_binds_tree_view, "Keybind", 0)
    render_tree_view_column(media_binds_tree_view, "Keybind", 0)

    render_tree_view_column(all_binds_tree_view, "Action", 1)
    render_tree_view_column(application_binds_tree_view, "Action", 1)
    render_tree_view_column(window_binds_tree_view, "Action", 1)
    render_tree_view_column(workspace_binds_tree_view, "Action", 1)
    render_tree_view_column(media_binds_tree_view, "Action", 1)

    all_binds_scroller.add(all_binds_tree_view)
    application_binds_scroller.add(application_binds_tree_view)
    workspace_binds_scroller.add(workspace_binds_tree_view)
    window_binds_scroller.add(window_binds_tree_view)
    media_binds_scroller.add(media_binds_tree_view)

    stack.add_titled(all_binds_scroller, "all", "All")
    stack.add_titled(application_binds_scroller, "applications", "Applications")
    stack.add_titled(window_binds_scroller, "windows", "Windows")
    stack.add_titled(workspace_binds_scroller, "workspaces", "Workspaces")
    stack.add_titled(media_binds_scroller, "media", "Media")

    stack_switcher = Gtk.StackSwitcher()
    stack_switcher.set_stack(stack)

    cbox.set_center_widget(stack_switcher)

    vbox.pack_start(cbox, False, True, 10)
    vbox.pack_start(stack, True, True, 10)

    win.add(vbox)

    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


def get_binds_json():
    output = subprocess.check_output(["hyprctl", "binds", "-j"], text=True)
    try:
        binds = json.loads(output)
    except ValueError:
        print("Error: could not parse hyprctl output.")
        sys.exit(1)
    return binds


def get_sorted_binds_array(unsorted_binds):
    sorted_binds = {}
    sorted_binds["applications"] = []
    sorted_binds["windows"] = []
    sorted_binds["workspaces"] = []
    sorted_binds["media"] = []
    r = r'.*(amixer|volume|wpctl|playerctl|brightness|light|b""rillo|audio).*'

    for u in unsorted_binds:
        if "workspace" in u["action"].lower():
            sorted_binds["workspaces"].append(u)
            continue

        if "audio" in u["bind"].lower():
            sorted_binds["media"].append(u)
            continue

        if re.search(r, u["action"].lower()):
                sorted_binds["media"].append(u)
                continue

        if "exec" in u["action"].lower():
            sorted_binds["applications"].append(u)
            continue
        else:
            sorted_binds["windows"].append(u)
    return sorted_binds


def get_unsorted_binds_array():
    unsorted_binds = []
    binds_json = get_binds_json();
    n = len(binds_json)

    for i in range(0, n):
        unsorted_binds.append({})
        unsorted_binds[i]["bind"] = ""
        unsorted_binds[i]["action"] = ""
        
        if binds_json[i]["modmask"]:
            unsorted_binds[i]["bind"] += modmask_code_to_string(
                binds_json[i]["modmask"])

        if binds_json[i]["key"] != "":
            if binds_json[i]["modmask"]:
                unsorted_binds[i]["bind"] += " + " + binds_json[i]["key"]
            else:
                unsorted_binds[i]["bind"] += binds_json[i]["key"]
        elif binds_json[i]["keycode"]:
            unsorted_binds[i]["bind"] += (
                "keycode:" 
                + str(binds_json[i]["keycode"])
            )

        if binds_json[i]["dispatcher"]:
            unsorted_binds[i]["action"] += binds_json[i]["dispatcher"]
            if binds_json[i]["arg"]:
                unsorted_binds[i]["action"] += ", "

        if binds_json[i]["arg"]:
            unsorted_binds[i]["action"] += binds_json[i]["arg"]

    return unsorted_binds


def modmask_code_to_string(code, string=""):
    modmasks = [
        {"name": "Mod5", "code": 128},
        {"name": "Super", "code": 64},
        {"name": "Mod3", "code": 32},
        {"name": "Mod2", "code": 16},
        {"name": "Alt", "code": 8},
        {"name": "Ctrl", "code": 4},
        {"name": "Lock", "code": 2},
        {"name": "Shift", "code": 1},
    ]

    remainder = code

    for m in modmasks:
        if code >= m["code"]:
            remainder -= m["code"]
            string += m["name"]
            break

    if remainder != 0:
        string += " + "
        return modmask_code_to_string(remainder, string)

    return string


def render_tree_view_column(tree_view, name, index):
    renderer = Gtk.CellRendererText()
    bind_column = Gtk.TreeViewColumn(name)
    bind_column.pack_start(renderer, True)
    bind_column.add_attribute(renderer, "text", index)
    tree_view.append_column(bind_column)


def write_binds_list(binds_array):
    binds_list = Gtk.ListStore(str, str)
    for b in binds_array:
        binds_list.append([b["bind"], b["action"]])
    return binds_list


main()
