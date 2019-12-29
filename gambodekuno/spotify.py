import os
import sys
from subprocess import Popen, PIPE
import requests
from pprint import pprint
import re


def is_running():
    _, out, _ = get_exitcode_stdout_stderr(["pidof", "spotify"])
    return bool(out)

def download_file(url, filename):
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)

def get_exitcode_stdout_stderr(args):
    proc = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    exitcode = proc.returncode
    return exitcode, out, err


dbus_dest = "org.mpris.MediaPlayer2.spotify"
dbus_contents = list(map(str.strip, """/org/mpris/MediaPlayer2
org.freedesktop.DBus.Properties.Get
string:org.mpris.MediaPlayer2.Player
string:Metadata""".split("\n")))
options = ["--print-reply", f"--dest={dbus_dest}"]

fields = {"cover": '"mpris:artUrl"',
          "album": '"xesam:album"',
          "artist": '"xesam:artist"',
          "title": '"xesam:title"'}

field_mapping = {v: k for k, v in fields.items()}

metadata_file = 'metadata.txt'
cover_file = 'cover.png'

[os.remove(file) for file in [metadata_file, cover_file] if os.path.exists(file)]

if not is_running():
    sys.exit(0)

exitcode, data, err = get_exitcode_stdout_stderr(["dbus-send", *options, *dbus_contents])

if not(data):
    raise Exception(f"Something unexpected happened. dbus-send exit code: {exitcode} error: {err}")

string = data.decode()
tokens = list(map(lambda s: s.strip(), string.split()))
tokens = list(filter(lambda s: s, tokens))
n, entries = 0, []
for token in tokens:
    if "entry(" in token:
        if len(entries): entries[-1].pop(-1)
        entries.append([])
        n += 1
    elif n > 0 and token not in "([{}])":
        entries[-1].append(token)
selection = list(filter(lambda l: any([e in field_mapping for e in l]), entries))
with open(metadata_file, "w") as f:
    for values in selection:
        field = list(filter(lambda e: e in field_mapping, values))[0]
        if field_mapping[field] == "cover":
            download_file(values[-1].replace('"', ''), cover_file)
            get_exitcode_stdout_stderr(["mogrify", cover_file])
        else:
            value = " ".join(values[values.index(field)+1:]).split('"', maxsplit=1)[-1].replace('"', '')
            f.write(value + "\n")
