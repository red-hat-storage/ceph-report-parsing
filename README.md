ceph-report-parsing
===================

Scripts to parse the output from Ceph Report

Pipe the output of ceph report into each of the .py files in modules to generate an output equivalent to the ceph commands of the same name.

Depends on:
===========
python-simplejson

Install & Usage:
================

Clone this repo:

```
git clone https://github.com/red-hat-storage/ceph-report-parsing.git
cd ceph-report-parsing/modules
```

Install prereq:

```
pip install simplejson
```

Pipe the <sosreport>/sos_commands/ceph/ceph_repot json into your desired module. Example:

```
cat <PATH_to_sosreport_folder>/sos_commands/ceph/ceph_report | ./ceph_health.py
cat <PATH_to_sosreport_folder>/sos_commands/ceph/ceph_report | ./ceph_osd_tree.py
cat <PATH_to_sosreport_folder>/sos_commands/ceph/ceph_report | ./ceph_osd_getcrushmap.py
```
