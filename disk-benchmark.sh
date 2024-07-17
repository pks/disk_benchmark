#!/bin/bash

dd if=/dev/zero of=dd.file bs=1M status=progress count=10K &>dd.out
rm dd.file

dd if=/dev/zero of=dd.file bs=4K status=progress count=10M &>dd-4k.out
rm dd.file

ioping -c 300 . &>ioping.out

for rw in rw randrw; do
for rwmixread in 33 66; do
for numjobs in 1 3 10; do
for iodepth in 1 3 10; do
for bs in 4k 1M; do 
name="fio-rw:$rw-rwmixread:$rwmixread-numjobs:$numjobs-iodepth:$iodepth-bs:$bs"
fio --name=$name \
    --ioengine=libaio \
    --rw=$rw \
    --rwmixread=$rwmixread \
    --bs=$bs \
    --numjobs=$numjobs \
    --size=4g \
    --iodepth=$iodepth \
    --refill_buffers=1 \
    --runtime=300 \
    --time_based \
    --end_fsync=1 \
    --group_reporting \
    &>$name.out
rm fio*.*.*
done
done
done
done
done
