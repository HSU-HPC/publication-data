
#! /bin/bash

DOMAIN_SIZE_MIN=20
DOMAIN_SIZE_MAX=210
DOMAIN_SIZE_STEP=10

cd "$(dirname "$0")"

for FILE in $(ls ./*.xml.template 2> /dev/null); do
	TEMPLATE=$FILE
	break
done

if [ -z "$TEMPLATE" ]; then
	echo "No .xml.template file found!"
	exit 1
fi

echo "Using template file $TEMPLATE:"

for ((DOMAIN_SIZE=$DOMAIN_SIZE_MIN; DOMAIN_SIZE<=$DOMAIN_SIZE_MAX; DOMAIN_SIZE += $DOMAIN_SIZE_STEP)); do
	FILENAME=${TEMPLATE/".xml.template"/"-$DOMAIN_SIZE.xml"}
	echo $DOMAIN_SIZE $FILENAME
	cat $TEMPLATE | sed "s/{domain_size}/$DOMAIN_SIZE/g" > $FILENAME
done

