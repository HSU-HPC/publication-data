#! /bin/bash

RUNS_PER_DOMAIN_SIZE=3

cd "$(dirname "$0")"

for CONFIG_FILE in $(ls *.xml); do
	DOMAIN_SIZE=$(echo $CONFIG_FILE | grep -o "\-[0-9]*\.xml")
	DOMAIN_SIZE=${DOMAIN_SIZE:1:-4}
	echo $DOMAIN_SIZE

    RUNS_REMAINING=$(($RUNS_PER_DOMAIN_SIZE - $(ls *.log 2>/dev/null | grep "\-${DOMAIN_SIZE}_[0-9]*.log" | wc -l)))
    # for ((_I=0; _I<$RUNS_REMAINING; _I++)); do
    if [ $RUNS_REMAINING -gt 0 ]; then # Invoke multiple times to run more instances of the same job
        sbatch $(ls *-$DOMAIN_SIZE.job)
    else
        echo "No more jobs for $DOMAIN_SIZE!"
    fi
    # done
done
exec watch squeue -u $(whoami)
