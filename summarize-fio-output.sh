#!/bin/bash


for iodepth in 1 3 10; do
for numjobs in 1 3 10; do
for mix in 66; do
for rw in rw randrw; do
for bs in 4k 1M; do
    ../../summarize-fio-output.py fio-rw:${rw}-rwmixread:${mix}-numjobs:${numjobs}-iodepth:${iodepth}-bs:${bs}.out
done
done
done
done
done
