#!/bin/bash

if [ "$(cat /proc/acpi/bbswitch | grep OFF)" ]; then
	echo OFF
else
  gpu_stats=$(optirun nvidia-smi 2>/dev/null | grep Default | cut -d '|' -f3,4)
  mem=$(echo $gpu_stats | cut -d"/" -f1 | tr -d " ")
	perc=$(echo $gpu_stats | cut -d"|" -f2 | sed "s/Default//g" | tr -d " ")
	echo $perc / $mem
fi


