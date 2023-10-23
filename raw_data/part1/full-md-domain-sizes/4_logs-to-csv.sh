#! /bin/bash

OUTPUT_FILE="full-md-domain-size.csv"

cd "$(dirname "$0")"

echo "filename,md_domain_size,energy_consumption_kWh,wall_time,cpu_time" > $OUTPUT_FILE
for LOGFILE in $(ls *.log 2>/dev/null); do
    # Skip all files that are not 
    LAST_LOGFILE_LINE=$(tail -n 1 $LOGFILE)
    if [[ $LAST_LOGFILE_LINE = Energy* ]]; then
        : # Continue with processing the file
    else
        >&2 echo "Logfile $LOGFILE not done yet! (skipping)"
        continue
    fi

    ENERGY_CONSUMPTION_KWH=$(tail -n 1 $LOGFILE | grep -Eo "[\.0-9]+kWh")
    WALL_TIME=$(cat $LOGFILE | grep -o "^Used walltime\s*:\s*.*" | awk '{print $4}')
    CPU_TIME=$(cat $LOGFILE | grep -o "^Used CPU time\s*:\s*.*" | awk '{print $5}')
    DOMAIN_SIZE=$(echo $LOGFILE | grep -Eo "md-[0-9]+_")
    echo "\"$LOGFILE\",${DOMAIN_SIZE:3:-1},${ENERGY_CONSUMPTION_KWH::-3},$WALL_TIME,$CPU_TIME" >> $OUTPUT_FILE
done
