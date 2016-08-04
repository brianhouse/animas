#!/usr/bin/env python3

import json, datetime, requests
from housepy import config, log, util, strings
from mongo import db, DESCENDING, DuplicateKeyError


try:
    # find most recent entry
    start_date = db.entries.find().sort([('t_utc', DESCENDING)]).limit(1)[0]['datetime'].split(' ')[0]
except Exception:
    start_date = config['start_date']
log.info("START_DATE %s" % start_date)
today = util.dt(tz=config['tz'])
yesterday = today - datetime.timedelta(days=1)
end_date = yesterday.strftime("%Y-%m-%d")
log.info("END_DATE %s" % end_date)


for site, name in config['sites'].items():

    url = "http://nwis.waterdata.usgs.gov/usa/nwis/uv/?cb_00065=on&cb_00060=on&cb_00095=on&cb_00010=on&cb_00400=on&cb_63680=on&format=rdb&site_no=%s&period=&begin_date=%s&end_date=%s" % (site, start_date, end_date)
    log.info("%s: %s" % (site, name))
    log.info(url)
    try:
        response = requests.get(url)
        response = response.text
    except Exception as e:
        log.error(log.exc(e))
        log.error(url)
        continue


    lines = response.split('\n')
    log.info("%s lines" % len(lines))
    fields = None
    nop = None

    for line in lines:
        line = line.strip()
        if not len(line):
            continue
        if line[0] == '#':
            continue
        params = line.split('\t')
        if fields is None:        
            fields = params
            for f, field in enumerate(fields):
                for (key, label) in config['labels'].items():
                    if key in field and "_cd" not in field:
                        fields[f] = label
            continue
        if nop is None:
            nop = params
            continue
        data = {fields[f]: param for (f, param) in enumerate(params)}
        data = {(key if key != 'site_no' else 'site'): (strings.as_numeric(value.strip()) if key != 'site_no' else value) for (key, value) in data.items()}
        data = {key: (value if type(value) != str or len(value) else None) for (key, value) in data.items() if "_cd" not in key}
        if 'datetime' not in data:
            continue
        data['t_utc'] = util.timestamp(util.parse_date(data['datetime'], tz=config['tz']))
        log.info(json.dumps(data, indent=4))
        try:
            entry_id = db.entries.insert_one(data).inserted_id
            log.info("INSERT %s" % entry_id)
        except DuplicateKeyError:
            log.warning("DUPLICATE")
        except Exception as e:
            log.error(log.exc(e))

