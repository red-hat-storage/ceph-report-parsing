#!/usr/bin/env python

import json,sys
from subprocess import Popen, PIPE
from StringIO import StringIO
from optparse import OptionParser

usage = "Usage: %prog [-u] [-p] [-i pgid]"
parser = OptionParser()
parser.add_option("", "--metaosd", action="store_true",dest="metao",help="Display OSD metadata information",default=False)
parser.add_option("-c", "--crush", action="store_true",dest="crush",help="Display CRUSH map information",default=False)
parser.add_option("-m", "--mon", action="store_true",dest="mon",help="Display MON map information",default=False)
parser.add_option("-t", "--tree", action="store_true",dest="tree",help="Display OSD tree information",default=False)
parser.add_option("-u", "--du", action="store_true",dest="du",help="Display OSD usage information",default=False)
parser.add_option("-p", "--pg", action="store_true",dest="pg",help="Display PGID usage information",default=False)
parser.add_option("-d", "--od", action="store_true",dest="od",help="Display OSD dump information",default=False)
parser.add_option("-g", "--po", action="store_true",dest="po",help="Display PG per OSD stats information",default=False)
parser.add_option("-i", "--id", action="store",type="string",dest="pg_id",help="Filter PGID display to this single PG",default="")
parser.add_option("-o", "--osd", action="store",type="string",dest="osd_id",help="Filter OSD display to this single OSD",default="")
parser.add_option("-f", "--file", action="store",type="string",dest="report",help="Use an input file rather than a ceph report command",default="")

(options, args) = parser.parse_args()

if (options.report != ''):
   r = Popen(['cat',options.report],stdout=PIPE,stderr=PIPE)
else:
   r = Popen(['ceph','report'],stdout=PIPE,stderr=PIPE)

cephreport, _ = r.communicate()

obj=json.load(StringIO(cephreport))

hashes_data={0:'rjenkins1', 'rjenkins1': 0}
itemById={}
bucketById={}
osdById={}
global dump_bucket_type
dump_bucket_type = 0

def osdmeta():
   osdmeta = obj['osd_metadata']
   print "  ID\t        IPP\t\t       IPC\t        Host\t          RAM\t         SWAP\t        Version\t      Kernel"
   for OSD in osdmeta:
        outline="{0:6d}\t".format(OSD['id'])
        outline += "{0:15}\t".format(OSD['front_addr'].split('/')[0])
        outline += "{0:15}\t".format(OSD['back_addr'].split('/')[0])
        outline += "{0:12}\t".format(OSD['hostname'])
        usep=float(OSD['mem_total_kb'])/float(1024.0);
        outline += "{0:6.0f} MB\t".format(usep)
        usep=float(OSD['mem_swap_kb'])/float(1024.0);
        outline += "{0:6.0f} MB\t".format(usep)
        outline += "{0:12}\t".format(OSD['ceph_version'].split(' ')[2])
        outline += "{0:36}\t".format(OSD['kernel_version'])
        print outline

def dump_items(b):
   global dump_bucket_type
   dump_bucket_type += 1
   for osd in obj['osdmap']['osds']:
      osdById[osd['osd']] = osd

   for i in b['items']:
      index = 0
      if i['id'] > -1:
         outline = "{0:6d}\t".format(i['id'])
         outline += "{0:8.4}\t".format(float(i['weight'])*0.00001526)
         while index < dump_bucket_type:
            outline += '\t'
            index += 1
         outline += "osd."+str(i['id'])+"\t\t\t   "
         if osdById[i['id']]['up']  == 1:
            outline += "up/"
         else:
            outline += "down/"
         if osdById[i['id']]['in']  == 1:
            outline += "in\t"
         else:
            outline += "out\t"
         outline += "{0:4.3}".format(osdById[i['id']]['weight'])
         print outline
      else:
         cb = bucketById[i['id']]
         outline = "{0:6d}\t".format(cb['id'])
         outline += "{0:8.4}\t".format(float(cb['weight'])*0.00001526)
         while index < dump_bucket_type:
            outline += '\t'
            index += 1
         outline += cb['type_name']+" "
         outline += cb['name']
         print outline

         dump_items(cb)
         dump_bucket_type -= 1

def osdtree():
   dump_bucket_type = 0
   for bucket in obj['crushmap']['buckets']:
           bucketById[bucket['id']]=bucket

   #print bucketById

   print "  ID\t  Weight\t      Type\t        Name\t          Status\t         Reweight"
   for bucket in obj['crushmap']['buckets']:
      if bucket['type_name'] == 'root':
         outline = "{0:6d}\t".format(bucket['id'])
         outline += "{0:8.4}\t".format(float(bucket['weight'])*0.00001526)

         outline += bucket['type_name']+" "
         outline += bucket['name']
         print outline
         dump_items(bucket)
 
def crushmap():
   print '# begin crush map'
   # -- output tunables
   for tunable in sorted(obj['crushmap']['tunables'].iterkeys()):
	   print tunable+' '+str(obj['crushmap']['tunables'][tunable])
   print ''
 
   print '# devices'
   # -- output OSDs
   for device in obj['crushmap']['devices']:
	   print 'device '+str(device['id'])+' '+device['name']
	   itemById[device['id']]=device['name']
   print ''
 
   print '# types'
   # -- output types
   for bucketType in obj['crushmap']['types']:
	   print 'type '+str(bucketType['type_id'])+' '+bucketType['name']
   print ''
 
   print '# buckets'
   # -- Output host, etc.. buckets
   for bucket in obj['crushmap']['buckets']:
	   itemById[bucket['id']]=bucket['name']
 
   for bucket in obj['crushmap']['buckets']:
	   print bucket['type_name']+' '+bucket['name']+' {'
	   print '\tid '+str(bucket['id'])
	   print '\t# weight '+'{0:0.3f}'.format(float(bucket['weight'])/65536)
	   print '\talg '+bucket['alg']
	   print '\thash '+str(hashes_data[bucket['hash']])+' # '+bucket['hash']
	   for item in bucket['items']:
		   print '\titem '+itemById[item['id']]+' weight '+'{0:0.3f}'.format(float(item['weight'])/65536)
	   print '}'
   print ''
 
   print '# rules'
   # -- output all rules
   for rule in obj['crushmap']['rules']:
	   print 'rule '+rule['rule_name']+' {'
	   print '\truleset '+str(rule['rule_id'])
	   print '\ttype '+'# Doesnt seem to exist in the ceph report?'
	   print '\tmin_size '+str(rule['min_size'])
	   print '\tmax_size '+str(rule['max_size'])
	   for step in rule['steps']:
		   outline='\tstep '+str(step['op']).replace('_',' ')
		   for field in ['item_name','num']:
			   if field in step:
				   outline+=' '+str(step[field])
		   if 'type' in step:
			   outline+=' type '+step['type']
		   print outline
	   print '}'
	
def monmap():
   monmap = obj['monmap']
   print "MON Map information for cluster "+str(monmap['fsid'])+" last modified on "+str(monmap['modified'])
   print "  Name\t        Rank\t       IP\t        Port"
   for MON in obj['monmap']['mons']:
        outline="{0:12}\t".format(MON['name'])
        outline += "{0:2d}\t".format(MON['rank'])
        addr = str(MON['addr']).split(':')
        outline += "{0:15}\t".format(addr[0])
        outline += "\t{0:6}\t".format((addr[1].split('/'))[0])
        print outline

def dustats():
   print "  OSD\t        Size\t        Used\t       Avail\t  Used%"
   for OSD in obj['pgmap']['osd_stats']:
        outline="{0:5d}\t".format(OSD['osd'])
        for i in [ 'kb', 'kb_used', 'kb_avail' ]:
                outline+="{0:12d}\t".format(OSD[i])
        usep=float(OSD['kb_used'])/float(OSD['kb']);
        if (options.osd_id != ''):
           if (str(OSD['osd']) == options.osd_id):
              print outline+"{0:6.2f}".format(usep)
           else:
              pass
        else:
           print outline+"{0:6.2f}".format(usep)

def pgstats():
   bFilterPg = False
   if (options.pg_id != ""):
      bFilterPg = True
   print "  PG   \t   Bytes    \t   Objects  \t     Read   \t     ReadKB \t   Write    \t   WriteKB  "
   for PG in obj['pgmap']['pg_stats']:
        pgid = PG['pgid']
        outline="{0:7}\t".format(PG['pgid'])
        for j in [ 'num_bytes', 'num_objects', 'num_read', 'num_read_kb', 'num_write', 'num_write_kb' ]:
           outline+="{0:12d}\t".format(PG['stat_sum'][j])
        if (bFilterPg):
           if  pgid == options.pg_id:
              print outline
              break
           else:
              pass
        else:
           print outline

def pgsperosd():
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
	   osd_data[osd['osd']]['osdSize'].append("{0:0.2f}".format(float(osd['kb_used'])/float(osd['kb'])*100))	# Append Use Percentage formatted to 2 decimal points
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
   for field in range(0,len(dfFields)):						# Loop through osdSize fields
	   if field < 3:								# If we're on osd Sizes / use KB, adjust it to Gb to not exceed max int size
		   sumLine+=','+str(sum(osd_data[x]['osdSize'][field]/1024/1024 for x in osd_data))+'g'	# Append sum of the osdSize field
	   else:									# We're on the Use%, so sum doesn't make sense here, leave it empty
		   sumLine+=','
	   minLine+=','+str(min(osd_data[x]['osdSize'][field] for x in osd_data))	# Append min value to Summary line
	   maxLine+=','+str(max(osd_data[x]['osdSize'][field] for x in osd_data))	# Append max value to Summary line
	   avgLine+=','+str("{0:0.2f}".format(sum(float(osd_data[x]['osdSize'][field]) for x in osd_data)/len(osd_data)))	# Append Average value to Summary line
 
   for field in fields:								# Loop through all PG Count Fields, appending sum, min, max and avg
	   sumLine+=','+str(sum(osd_data[x][field]['PrimPG#'] for x in osd_data))+','+str(sum(osd_data[x][field]['SecPG#'] for x in osd_data))+','+str(sum(osd_data[x][field]['PrimPG#']+osd_data[x][field]['SecPG#'] for x in osd_data))
	   minLine+=','+str(min(osd_data[x][field]['PrimPG#'] for x in osd_data))+','+str(min(osd_data[x][field]['SecPG#'] for x in osd_data))+','+str(min(osd_data[x][field]['PrimPG#']+osd_data[x][field]['SecPG#'] for x in osd_data))
	   maxLine+=','+str(max(osd_data[x][field]['PrimPG#'] for x in osd_data))+','+str(max(osd_data[x][field]['SecPG#'] for x in osd_data))+','+str(max(osd_data[x][field]['PrimPG#']+osd_data[x][field]['SecPG#'] for x in osd_data))
	   avgLine+=','+str("{0:0.2f}".format(sum(float(osd_data[x][field]['PrimPG#']) for x in osd_data)/len(osd_data)))+','+str("{0:0.2f}".format(sum(float(osd_data[x][field]['SecPG#']) for x in osd_data)/len(osd_data)))+','+str("{0:0.2f}".format(sum(float(osd_data[x][field]['PrimPG#']+osd_data[x][field]['SecPG#']) for x in osd_data)/len(osd_data)))
 
   ## Print Summary lines
   print sumLine
   print avgLine
   print minLine
   print maxLine

	   
def osddump():
   for field in [ 'epoch', 'fsid', 'created','modified']:
	   print field+' '+str(obj['osdmap'][field]);
 
   print "";
 
   for pool in obj['osdmap']['pools']:
	   outline='pool '+str(pool['pool'])+' '+pool['pool_name'];
	   for field in ['size','min_size','crush_ruleset','object_hash','pg_num','pg_placement_num','last_change','flags','stripe_width']:
		   if field in pool:
			   outline+=' '+field.replace('pg_placement_num','pgp_num')+' '+str(pool[field]);
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
	
if (options.du == True):
   dustats()
if (options.pg == True):
   pgstats()
if (options.po == True):
   pgsperosd()
if (options.od == True):
   osddump()
if (options.mon == True):
   monmap()
if (options.crush == True):
   crushmap()
if (options.metao == True):
   osdmeta()
if (options.tree == True):
   osdtree()


