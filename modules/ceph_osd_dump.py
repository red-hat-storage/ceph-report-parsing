#!/usr/bin/env python

import sys
import simplejson as json

obj=json.load(sys.stdin)

for field in [ 'epoch', 'fsid', 'created','modified']:
	print field+' '+str(obj['osdmap'][field]);

print "";

for pool in obj['osdmap']['pools']:
	outline='pool '+str(pool['pool'])+' '+pool['pool_name'];
	for field in ['size','min_size','crush_ruleset','object_hash','pg_num','pg_placement_num','last_change','flags_names','stripe_width']:
		if field in pool:
			outline+=' '+field.replace('pg_placement_num','pgp_num').replace('flags_names','flags')+' '+str(pool[field]);
	print outline;

print ""

for osd in obj['osdmap']['osds']:
	outline='osd.'+str(osd['osd'])
	if osd['up']:
		outline+=' up'
	else:
		outline+=' down'
	if osd['in']:
		outline+=' in'
	else:
		outline+=' out'
	for field in ['weight','up_from','up_thru','down_ad']:
		if field in osd:
			outline+=' '+field+' '+str(osd[field])
	outline+=' last_clean_interval ('+str(osd['last_clean_begin'])+','+str(osd['last_clean_end'])+') '
	for field in ['public_addr','cluster_addr','heartbeat_back_addr','heartbeat_front_addr']:
		if field in osd:
			outline+=' '+osd[field]
	outline+=' '+osd['state'][0]+','+osd['state'][1]+' '+osd['uuid']
	print outline

