#!/bin/sh
# Initiates a shutdown when the power putton has been
# pressed.

SCRIPT=$(readlink "$0")
DIR=$(dirname "$SKRIPT")

/usr/bin/python $DIR/naptime.py > /var/log/naptime.log

# 1.- sudo gedit /etc/acpi/events/powerbtn
# 2.- Add # to comment line: #action=/etc/acpi/powerbtn.sh
# 3.- Add a new line: action=/root/naptime/powerbtn.sh
# 4.- Save file
# 5.- Open a console and type: sudo acpid restart
