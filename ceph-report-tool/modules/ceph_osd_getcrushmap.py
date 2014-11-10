#!/usr/bin/env python

import sys
import simplejson as json

obj=json.load(sys.stdin)

hashes_data={0:'rjenkins1', 'rjenkins1': 0}
ruletypes_data={1:'replicated',2:'raid4',3:'erasure'}
itemById={}

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
	if 'type' in rule:
		print '\ttype '+ruletypes_data[rule['type']]
	else:
		print '\ttype replicated'
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
