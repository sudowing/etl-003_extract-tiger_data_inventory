#!/bin/bash
. ../log.sh;

log info 'EXTRACT [START]';

rm -Rf temp && mkdir temp;

# download by python [requests]
python3 01_process.py


rm -Rf temp

log info 'EXTRACT [COMPLETE]';
