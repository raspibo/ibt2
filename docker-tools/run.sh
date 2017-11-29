#!/bin/sh

if [ $# -lt 1 ] ; then
	exit 1
fi

cmd="$1"

if [ "${cmd}" = "--shell" ] ; then
	echo "INFO: opening shell..."
	mongo --host mongo ibt2
elif [ "${cmd}" = "--dump" ] ; then
	echo "INFO: dumping..."
	mongodump --host mongo --out /tmp/ --db ibt2 || (echo "ERROR: unable to dump the database" ; exit 10)
	cd /tmp
	tar cfz /data/ibt2-dump-`date +'%Y-%m-%dT%H:%M:%S'`.tgz ibt2
elif [ "${cmd}" = "--restore" ] ; then
	if [ -z "$2" ] ; then
		echo "ERROR: missing argument to --restore"
		exit 20
	fi
	echo "INFO: restoring $2..."
	tar xfz "/data/$2" -C /tmp || (echo "ERROR: error unpacking file" ; exit 21)
	mongo --host mongo ibt2 --eval "db.dropDatabase()" || (echo "ERROR: error dropping the database" ; exit 22)
	mongorestore --host mongo -d ibt2 /tmp/ibt2
else
	echo "ERROR: command not recognized: use --dump or --restore dumps/file.tgz"
	exit 30
fi

