#!/usr/bin/env python

import sys
import simplejson as json

obj=json.load(sys.stdin)


# osd_data_object  osd.id = [ 'osdSize': [size,used,avail,used%], 'TotalPGs': [primary, secondary], 'PoolName1': [primary, secondary] , 'PoolName2': [primary, secondary], ... ];
osd_data={}

# pool_data_object Pool.id = [ pool object from json ];
pool_data={}

dfFields=['Size','Used','Avail','Use%']		# Headers for OSD Size data
fields=['TotalPGs']				# Begin headers for PG Count data
for pool in obj['osdmap']['pools']:		# Loop through pools to populate Pool data and Field Headers (with pool_name)
	pool_data[str(pool['pool'])]=pool	# Populate pool_data
	fields.append(pool['pool_name'])	# Populate Field Headers with pool_name


for osd in obj['pgmap']['osd_stats']:		# Loop through OSD Size statistics
	osd_data[osd['osd']]={'osdSize': []}	# Create osdSize bucket for Size statistics
	for field in ['kb','kb_used','kb_avail']:			# Loop through the fields we care about
		osd_data[osd['osd']]['osdSize'].append(osd[field])	# Append fields to osdSize bucket
	if osd['kb'] > 0:
		osd_data[osd['osd']]['osdSize'].append("{0:0.2f}".format(float(osd['kb_used'])/osd['kb']*100)) # Append Use Percentage formatted to 2 decimal points
	else:
		osd_data[osd['osd']]['osdSize'].append("0.00")
	for field in fields:						# Loop through All Fields
		osd_data[osd['osd']][field]={'PrimPG#': 0, 'SecPG#': 0}	# Create PG Count Buckets

for pg in obj['pgmap']['pg_stats']:		# Loop through ALL PGs
	poolID,_=pg['pgid'].split('.',1)	# Split the Pool ID from the PG.id
	primSec='PrimPG#'			# Default to Primary PG
	for osdIndex in range(0,len(pg['acting'])):	# Loop through all OSDs in the 'acting' state
		if osdIndex > 0:			# If we're not on the first one, it's a secondary copy
			primSec='SecPG#'
		osd_data[pg['acting'][osdIndex]]['TotalPGs'][primSec]+=1			# Increment TotalPG counter for either Pri or Sec copy
		osd_data[pg['acting'][osdIndex]][pool_data[poolID]['pool_name']][primSec]+=1	# Increment PerPool counter for either Pri or Sec copy

## Begin output of per OSD data
print ',,'+','.join('' for x in dfFields)+',,,'.join(str(x) for x in fields)				# Print top row of header
print 'osd,'+','.join(x for x in dfFields)+',pri,sec,sum'.join('' for x in fields)+',pri,sec,sum'	# Print 2nd row of header

for osdid in osd_data:									# Loop through all OSDs
	osdSum=0									# Reset per-OSD Sum
	outline=str(osdid)								# Start output line with OSD.id
	for field in range(0,len(dfFields)):						# Loop through osdSize fields
		outline+=','+str(osd_data[osdid]['osdSize'][field])			# Append osdSize statistics to the output line
	for field in fields:								# Loop through PG Count Fields
		both=osd_data[osdid][field]['PrimPG#']+osd_data[osdid][field]['SecPG#']	# Calculate sum of both Pri and Sec PGs
		outline+=','+str(osd_data[osdid][field]['PrimPG#'])+','+str(osd_data[osdid][field]['SecPG#'])+','+str(both);	# Append Pri, Sec and Sum PG counts
	print outline									# Print output line

## Start Summary lines
sumLine='Sum'
avgLine='Avg'
minLine='Min'
maxLine='Max'
for field in range(0,len(dfFields)):							# Loop through osdSize fields
	if field < 3:									# If we're on osd Sizes / use KB, adjust it to Gb to not exceed max int size
		sumLine+=','+str(sum(osd_data[x]['osdSize'][field]/1024/1024 for x in osd_data))+'g'	# Append sum of the osdSize field
	else:										# We're on the Use%, so sum doesn't make sense here, leave it empty
		sumLine+=','
	minLine+=','+str(min(osd_data[x]['osdSize'][field] for x in osd_data))		# Append min value to Summary line
	maxLine+=','+str(max(osd_data[x]['osdSize'][field] for x in osd_data))		# Append max value to Summary line
	avgLine+=','+str("{0:0.2f}".format(sum(float(osd_data[x]['osdSize'][field]) for x in osd_data)/len(osd_data))) # Append Average value to Summary line

for field in fields:									# Loop through all PG Count Fields, appending sum, min, max and avg
	sumLine+=','+str(sum(osd_data[x][field]['PrimPG#'] for x in osd_data))+','+str(sum(osd_data[x][field]['SecPG#'] for x in osd_data))+','+str(sum(osd_data[x][field]['PrimPG#']+osd_data[x][field]['SecPG#'] for x in osd_data))
	minLine+=','+str(min(osd_data[x][field]['PrimPG#'] for x in osd_data))+','+str(min(osd_data[x][field]['SecPG#'] for x in osd_data))+','+str(min(osd_data[x][field]['PrimPG#']+osd_data[x][field]['SecPG#'] for x in osd_data))
	maxLine+=','+str(max(osd_data[x][field]['PrimPG#'] for x in osd_data))+','+str(max(osd_data[x][field]['SecPG#'] for x in osd_data))+','+str(max(osd_data[x][field]['PrimPG#']+osd_data[x][field]['SecPG#'] for x in osd_data))
	avgLine+=','+str("{0:0.2f}".format(sum(float(osd_data[x][field]['PrimPG#']) for x in osd_data)/len(osd_data)))+','+str("{0:0.2f}".format(sum(float(osd_data[x][field]['SecPG#']) for x in osd_data)/len(osd_data)))+','+str("{0:0.2f}".format(sum(float(osd_data[x][field]['PrimPG#']+osd_data[x][field]['SecPG#']) for x in osd_data)/len(osd_data)))

## Print Summary lines
print sumLine
print avgLine
print minLine
print maxLine
