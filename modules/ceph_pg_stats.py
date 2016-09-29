#!/usr/bin/env python

import sys
import math
import simplejson as json

obj=json.load(sys.stdin)


def format_kbytes(b):
    if b > math.pow(1024,2):
        retval=b/math.pow(1024,2)
        retunit='G'
    elif b> 1024:
        retval=b/1024
        retunit='K'
    else:
        retval=b
        retunit=''

    return "{0:.0f}{1}".format(retval,retunit)

pgFields=['last_scrub_stamp','last_deep_scrub_stamp','last_clean_scrub_stamp']
statFields=['num_bytes','num_objects','avg_obj_size','num_object_clones','num_read','num_read_kb','num_write','num_write_kb','num_scrub_errors']
#statFields=['num_bytes','num_objects','avg_obj_size','num_object_clones','avg_clones_per_obj','num_read','num_read_kb','num_write','num_write_kb','num_scrub_errors']

print "pgid," + ",".join(pgFields) + "," + ",".join(statFields)

for pg in obj['pgmap']['pg_stats']:
    outline="'"+pg['pgid']+"'"
    for field in pgFields:
        outline+=','+str(pg[field])
    for field in statFields:
        if field == "avg_obj_size":
            if pg['stat_sum']['num_objects'] > 0:
                outline+=',{0:d}'.format(pg['stat_sum']['num_bytes']/pg['stat_sum']['num_objects'])
            else:
                outline+=',0'
        elif field == "avg_clones_per_obj":
            if pg['stat_sum']['num_objects'] > 0:
                outline+=',{0:d}'.format(pg['stat_sum']['num_object_clones']/pg['stat_sum']['num_objects'])
            else:
                outline+=',0'
        else:
            outline+=','+str(pg['stat_sum'][field])
    print outline
