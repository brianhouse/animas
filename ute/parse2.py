#!/usr/bin/env python3

import csv, sys, json
import numpy as np
import signal_processing as sp
from housepy import strings, timeutil, log, drawing, util

PATH = "ute/2015/AR 19-3 continuous.csv"

FIELDNAMES = ['dt', 't_utc', 'temp_c', 'spcond', 'tds', 'ph', 'ph_mv', 'ODOsat', 'ODO', 'battery']
# FIELDNAMES = ['t_utc', 'dt', 'oxygen_mgl', 'discharge_cfs']
FIELDNAMES = ['t_utc', 'dt', 'ph', 'discharge_cfs']

ph = []
discharge_cfs = []

print("Parsing...")
with open(PATH) as csvfile:
    reader = csv.reader(csvfile)
    for r, row in enumerate(reader):
        if r < 2:
            continue
        try:
            if len(''.join(row).strip()) == 0:
                continue

            row = [strings.as_numeric(item) for item in row]
            row = [(None if type(item) == str and not len(item) else item) for item in row]
            
            dt_1 = timeutil.string_to_dt(row[0], tz="America/Denver")
            t_utc_1 = timeutil.timestamp(dt_1)
            datestring_1 = timeutil.t_to_string(t_utc_1, tz="America/Denver") 
            ph.append(dict(zip(['t_utc', 'ph'], [t_utc_1, row[1]])))

            dt_2 = timeutil.string_to_dt(row[2], tz="America/Denver")
            t_utc_2 = timeutil.timestamp(dt_2)
            datestring_2 = timeutil.t_to_string(t_utc_2, tz="America/Denver") 
            discharge_cfs.append(dict(zip(['t_utc', 'discharge_cfs'], [t_utc_2, row[3]])))

        except Exception as e:
            continue
            # print(e)
            # print(row)

print("Sorting...")
ph.sort(key=lambda d: d['t_utc'])
discharge_cfs.sort(key=lambda d: d['t_utc'])

print("Saving...")
util.save("ute_2015_ph.pkl", ph)
util.save("ute_2015_discharge_cfs_2.pkl", discharge_cfs)

print("--> done")
