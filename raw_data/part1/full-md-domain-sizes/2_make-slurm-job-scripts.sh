
#! /bin/bash

DOMAIN_SIZE_MIN=20
DOMAIN_SIZE_MAX=200
DOMAIN_SIZE_STEP=20

cd "$(dirname "$0")"
WORKDIR=$(pwd)
LS1_BIN_DIR=$(realpath "$WORKDIR/../../../ls1-mardyn/build/src/")

for FILE in $(ls ./*.job.template 2> /dev/null); do
	TEMPLATE=$FILE
	break
done

if [ -z "$TEMPLATE" ]; then
	echo "No .job.template file found!"
	exit 1
fi

echo "Using template file $TEMPLATE:"

for CONFIG_FILE in $(ls *.xml); do
	DOMAIN_SIZE=$(echo $CONFIG_FILE | grep -o "\-[0-9]*\.xml")
	DOMAIN_SIZE=${DOMAIN_SIZE:1:-4}
	FILENAME=${TEMPLATE/".job.template"/"-$DOMAIN_SIZE.job"}
	echo $DOMAIN_SIZE $FILENAME
	cat $TEMPLATE | sed "s/{domain_size}/$DOMAIN_SIZE/g" | \
		sed "s|{workdir}|$WORKDIR|g" | \
		sed "s|{ls1_bin_dir}|$LS1_BIN_DIR|g" \
		> $FILENAME
done

