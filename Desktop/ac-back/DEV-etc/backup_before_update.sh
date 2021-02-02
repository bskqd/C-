#!/bin/bash
# sotore backups file count
sbc=12
# backupdir
bdir=/mnt/backups/update/api/
# set env vars
      source $1/.env;
# run
      tar cfz /mnt/backups/update/api/$(date +%H:%M_%d.%m.%y).tag.gz $1;
      pg_dump --dbname=postgresql://$COMMUNICATION_USER:$COMMUNICATION_PASSWORD@$COMMUNICATION_HOST:$COMMUNICATION_PORT/$COMMUNICATION_NAME --no-owner >/mnt/backups/update/api/COMMUNICATION_NAME_$(date +%H:%M_%d.%m.%y).dump;
      pg_dump --dbname=postgresql://$MAIN_DATABASE_USER:$MAIN_DATABASE_PASSWORD@$MAIN_DATABASE_HOST:$MAIN_DATABASE_PORT/$MAIN_DATABASE_NAME --no-owner >/mnt/backups/update/api/MAIN_DATABASE_NAME_$(date +%H:%M_%d.%m.%y).dump;
      pg_dump --dbname=postgresql://$INSPECTION_USER:$INSPECTION_PASSWORD@$INSPECTION_HOST:$INSPECTION_PORT/$INSPECTION_NAME --no-owner >/mnt/backups/update/api/INSPECTION_NAME_$(date +%H:%M_%d.%m.%y).dump;

# old
#      find /mnt/backups/update/api/ -mtime +7 |sort|xargs rm -f;

# backups count
bc=$(ls -1 -r --sort=time /mnt/backups/update/api/ |wc -l)
# calculate count file to remove
rbc=$(( $bc - $sbc ))
# delete old backup's
stat -c "%Y %n" $bdir/* | sort -rn | tail -$rbc | xargs rm -f
