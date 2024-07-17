#!/usr/bin/env python3

import sys, re


def convert_bw_to_mib_per_s(bw):
    value, unit = re.match(r"([\d.]+)([KMGT]?iB/s)", bw).groups()
    value = float(value)

    if unit == "KiB/s":
        return value / 1024
    elif unit == "MiB/s":
        return value
    elif unit == "GiB/s":
        return value * 1024
    elif unit == "TiB/s":
        return value * 1024**2
    else:
        return 0.0


def normalize_iops(iops, read_weight, write_weight):
    for j, i in enumerate(iops):
        if i.endswith("k"):
            iops[j] = 1000 * float(i.strip("k"))
        else:
            iops[j] = float(i)

    total_iops = (iops[0] * read_weight) + (iops[1] * write_weight)

    return total_iops / 1000  # Normalize to 'K' (Divide by 1000)


def convert_latency_to_ms(latency, unit):
    value = float(latency)
    if unit == "nsec":
        return value / 1e6
    elif unit == "usec":
        return value / 1e3
    elif unit == "msec":
        return value
    else:
        return 0.0


def summarize_fio_output(fio_output, read_weight=0.5, write_weight=0.5, verbose=False):
   read_iops_re = re.compile(r"read: IOPS=([\d.]+k?)")
   write_iops_re = re.compile(r"write: IOPS=([\d.]+k?)")
   read_bw_re = re.compile(r"read:.*BW=([\d.]+[KMGT]?iB/s)")
   write_bw_re = re.compile(r"write:.*BW=([\d.]+[KMGT]?iB/s)")
   slat_re = re.compile(r"slat \((nsec|usec|msec)\):.*avg=([\d.]+)")
   clat_re = re.compile(r"clat \((nsec|usec|msec)\):.*avg=([\d.]+)")

   read_iops = read_iops_re.search(fio_output).group(1) if read_iops_re.search(fio_output) else "0"
   write_iops = write_iops_re.search(fio_output).group(1) if write_iops_re.search(fio_output) else "0"
   aggregated_iops = normalize_iops([read_iops, write_iops], read_weight, write_weight)

   read_bw = read_bw_re.search(fio_output).group(1) if read_bw_re.search(fio_output) else "0KiB/s"
   write_bw = write_bw_re.search(fio_output).group(1) if write_bw_re.search(fio_output) else "0KiB/s"
   read_bw_in_mib_s = convert_bw_to_mib_per_s(read_bw)
   write_bw_in_mib_s = convert_bw_to_mib_per_s(write_bw)
   aggregated_bw_in_mib_s = (read_weight * read_bw_in_mib_s) + (write_weight * write_bw_in_mib_s)

   slat_unit, slat_avg = slat_re.search(fio_output).groups() if slat_re.search(fio_output) else ("usec", "0")
   clat_unit, clat_avg = clat_re.search(fio_output).groups() if clat_re.search(fio_output) else ("usec", "0")
   slat_avg_in_ms = convert_latency_to_ms(slat_avg, slat_unit)
   clat_avg_in_ms = convert_latency_to_ms(clat_avg, clat_unit)
   total_latency_avg_in_ms = slat_avg_in_ms + clat_avg_in_ms

   if verbose:
   summary = (f"FIO Summary:\n"
              f"    Read - IOPS: {read_iops} (Weight: {read_weight*100}%), Bandwidth: {read_bw_in_mib_s:.2f} MiB/s\n"
              f"    Write - IOPS: {write_iops} (Weight: {write_weight*100}%), Bandwidth: {write_bw_in_mib_s:.2f} MiB/s\n"
              f"    Aggregated - IOPS: {aggregated_iops:.3f}K, Bandwidth: {aggregated_bw_in_mib_s:.2f} MiB/s\n"
              f"    Submission Latency Avg: {slat_avg_in_ms:.3f} ms\n"
              f"    Completion Latency Avg: {clat_avg_in_ms:.3f} ms\n"
              f"    Total Latency Avg: {total_latency_avg_in_ms:.3f} ms")
   else:
       summary = f"{aggregated_iops:.3f},{aggregated_bw_in_mib_s:.2f}"

   return summary


if __name__ == "__main__":
    fio_output = open(sys.argv[1], "r").read()

    print(summarize_fio_output(fio_output, read_weight=0.66, write_weight=0.34))
