import csv


def get_size(bytes: float) -> str:
    '''
    Returns size of bytes in a nice format
    '''
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f'{bytes:.2f} {unit}B'
        bytes /= 1024


def table_row(data: list) -> str:
    row_format = '{:>15}' * len(data)
    return row_format.format(*data)


def append_row(file: str, data: list):
    with open(file, 'a', newline='') as fd:
        writer = csv.writer(fd, delimiter=';')
        writer.writerow(data)


if __name__ == '__main__':
    import argparse
    import datetime
    import psutil
    import time

    parser = argparse.ArgumentParser(description='Process utilization monitor')
    parser.add_argument(dest='pid', type=int, help='PID of monitored process.')
    parser.add_argument('-s', '--stdout', dest='std_output', action='store_true', help='Print results to screen.')
    parser.add_argument('-o', '--output', help='File to write the results (in CSV format).',
                        default='{dt}-PID{pid}.csv')

    # parse arguments
    args = parser.parse_args()
    output_file = args.output.format(dt=datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S'), pid=args.pid)

    total_mhz = psutil.cpu_freq().max
    if_counters_prev = psutil.net_io_counters()
    try:
        p = psutil.Process(args.pid)

        if args.std_output:
            print('Process name:', p.name())
            print(table_row(['Time', 'CPU', 'Virtual Mem', 'Used Mem', 'Network Sent', 'Network Recv']))
        else:
            append_row(output_file, ['Date', 'Time', 'CPU, MHz', 'Virtual Mem, bytes', 'Used Mem, bytes',
                                     'Network Sent, bytes', 'Network Recv, bytes'])

        while True:
            with p.oneshot():
                mem = p.memory_full_info()
                mhz = p.cpu_percent() * total_mhz / 100
                if_counters = psutil.net_io_counters()
                if_sent = if_counters.bytes_sent - if_counters_prev.bytes_sent
                if_recv = if_counters.bytes_recv - if_counters_prev.bytes_recv

            if_counters_prev = if_counters
            dt = datetime.datetime.now()

            if args.std_output:
                print(table_row([
                    dt.strftime('%d.%m.%Y %H:%M:%S'), f'{mhz:.2f} MHz', get_size(mem.vms),
                    get_size(mem.uss), get_size(if_sent), get_size(if_recv)
                ]))
            else:
                append_row(output_file, [
                    dt.strftime('%d.%m.%Y'), dt.strftime('%H:%M:%S'),
                    mhz, mem.vms, mem.uss, if_sent, if_recv
                ])

            time.sleep(1)

    except psutil.NoSuchProcess as ex:
        print(ex)
