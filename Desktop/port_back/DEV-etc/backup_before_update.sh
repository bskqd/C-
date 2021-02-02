#!/bin/bash
# sotore backups file count
sbc=12
# backupdir
bdir=/mnt/backups/update/api-port/
# set env vars
      source $1/.env;
# run
      tar cfz $bdir/$(date +%H:%M_%d.%m.%y).tag.gz $1;
      pg_dump --dbname=postgresql://$MAIN_DATABASE_USER:$MAIN_DATABASE_PASSWORD@$MAIN_DATABASE_HOST:$MAIN_DATABASE_PORT/$MAIN_DATABASE_NAME --no-owner > $bdir/$MAIN_DATABASE_NAME_$(date +%H:%M_%d.%m.%y).dump;


# backups count
bc=$(ls -1 -r --sort=time $bdir |wc -l)
# calculate count file to remove
rbc=$(( $bc - $sbc ))
# delete old backup's
stat -c "%Y %n" $bdir/* | sort -rn | tail -$rbc | xargs rm -f
