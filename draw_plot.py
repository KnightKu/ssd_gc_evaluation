#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib
import pylab as pl
import os, fnmatch, stat
import commands
import random

fio_cmd = "fio --readwrite=randwrite --eta=always --eta-newline=1 --runtime={0} --ioengine=libaio --direct=1 " \
          "--iodepth=32 --time_based --blocksize=4k --name randw_4K " \
          "--filename={1} --size={2}%|tee ${3}"
"""
PATH_CMP = '/home/1.factory/2.Docs/Python_dir/ssd_gc_base_line/ext4_discard_cmp/'
PATH_EXT4 = '/home/1.factory/2.Docs/Python_dir/ssd_gc_base_line/ext4_without_discard/'
PATH_SSD = '/home/1.factory/2.Docs/Python_dir/ssd_gc_base_line/raw_block/'
"""
matplotlib.rcdefaults()

p = matplotlib.rcParams

# 配置图表大小

p["figure.figsize"] = (14.15, 40) # 两张A4纸大小，竖向页面


# 配置图表分辨率


# 配置绘图区域的大小和位置，下面的值是基于图标的宽和高的比例
p["figure.subplot.left"] = 0.06   # 左边距
p["figure.subplot.right"] = 0.94   # 右边距
p["figure.subplot.bottom"] = 0.05  # 下边距
p["figure.subplot.top"] = 0.92   # 上边距

# 配置subplots之间的间距（水平间距和垂直间距），也是基于图标的宽和高的比例

p["figure.subplot.wspace"] = 0.12

p["figure.subplot.hspace"] = 0.9


def walk_all_files(path, patterns='*'):
    files = []
    patterns = patterns.split(';')
    for item in os.listdir(path):
        if os.path.isfile(os.path.join(path, item)):
            for pattern in patterns:
                if fnmatch.fnmatch(item, pattern):
                    item = os.path.join(path, item)
                    print item
                    files.append(item)
                    break
    return files


def erase_ssd(device):
    """ ata secure erase
    hdparm - I $1 | egrep "Model|Serial|Firmware"
    hdparm --user-master u --security-set-pass password $1 || fail "Unable to set password"
    hdparm --user-master u --security-erase password $1 || fail "Unable to erase device"
    """
    if not os.path.exists(device):
        return -1

    if not os.path.isfile(device):
        return -1

    device_stat = os.stat(device)
    if not device_stat:
        print "Failed to stat {0}\n".format(device)
        return -1

    if not stat.S_ISBLK(device_stat[stat.ST_MODE]):
        print "{0} is not block device\n".format(device)
        return -1

    # check whether device is in use
    ret, res = commands.getstatusoutput('mount | grep {0}'.format(device))
    if ret == 0:
        print "{0} is in use\n".format(device)

    ret, res = commands.getstatusoutput('lsof {0}'.format(device))
    if ret == 0:
        print "{0} is in use\n".format(device)

    # try ata secure erase first
    ret, res = commands.getstatusoutput(
        'hdparm --user-master u --security-set-pass password {0}'.format(device))
    if ret:
        print "Failed to set secure passwd for {0}\n".format(device)
    else:
        ret, res = commands.getstatusoutput(
            'hdparm --user-master u --security-erase password {0}'.format(device))
        if ret == 0:
            return 0
        else:
            print "Failed to secure erase {0}\n".format(device)

    # try blkdiscard
    ret, res = commands.getstatusoutput(
        'blkdiscard {0}'.format(device))
    if ret:
        print "Failed to blkdiscard {0}\n".format(device)
        return -1
    return 0


def excute_fio_benchmark(device, time, log_name, size_rate=100):
    tmp_log = random.random()
    try:
        os.system(fio_cmd.format(time, device, size_rate, tmp_log))
    except Exception:
        print "failed to run fio...\n"
        return -1

    # tidy up the log, output just eta runtime log
    """
    Jobs: 1 (f=1): [w(1)] [77.4% done] [0KB/150.7MB/0KB /s] [0/38.6K/0 iops] [eta 00m:07s]
    Jobs: 1 (f=1): [w(1)] [83.9% done] [0KB/151.8MB/0KB /s] [0/38.9K/0 iops] [eta 00m:05s]
    Jobs: 1 (f=1): [w(1)] [90.3% done] [0KB/151.5MB/0KB /s] [0/38.8K/0 iops] [eta 00m:03s]
    Jobs: 1 (f=1): [w(1)] [96.8% done] [0KB/156.6MB/0KB /s] [0/40.7K/0 iops] [eta 00m:01s]
    Jobs: 1 (f=1): [w(1)] [100.0% done] [0KB/150.7MB/0KB /s] [0/38.6K/0 iops] [eta 00m:00s]
    R64P2: (groupid=0, jobs=1): err= 0: pid=10258: Fri Oct 14 17:03:30 2016
      write: io=6266.4MB, bw=213877KB/s, iops=53469, runt= 30002msec
        slat (usec): min=1, max=6572, avg= 2.30, stdev= 9.33
        clat (usec): min=45, max=60520, avg=595.59, stdev=1185.38
         lat (usec): min=53, max=60522, avg=597.94, stdev=1185.42
        clat percentiles (usec):
         |  1.00th=[  123],  5.00th=[  322], 10.00th=[  358], 20.00th=[  358],
         | 30.00th=[  358], 40.00th=[  358], 50.00th=[  358], 60.00th=[  454],
         | 70.00th=[  604], 80.00th=[  820], 90.00th=[ 1112], 95.00th=[ 1336],
         | 99.00th=[ 1640], 99.50th=[ 1736], 99.90th=[ 6240], 99.95th=[34048],
         | 99.99th=[57600]
        bw (KB  /s): min=139135, max=355864, per=100.00%, avg=214852.25, stdev=89095.83
        lat (usec) : 50=0.01%, 100=0.55%, 250=3.01%, 500=59.60%, 750=13.96%
        lat (usec) : 1000=9.44%
        lat (msec) : 2=13.20%, 4=0.08%, 10=0.10%, 20=0.01%, 50=0.03%
        lat (msec) : 100=0.03%
      cpu          : usr=10.36%, sys=16.18%, ctx=1583343, majf=0, minf=31
      IO depths    : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=100.0%, >=64=0.0%
         submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
         complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.1%, 64=0.0%, >=64=0.0%
         issued    : total=r=0/w=1604181/d=0, short=r=0/w=0/d=0, drop=r=0/w=0/d=0
         latency   : target=0, window=0, percentile=100.00%, depth=32

    Run status group 0 (all jobs):
      WRITE: io=6266.4MB, aggrb=213876KB/s, minb=213876KB/s, maxb=213876KB/s, mint=30002msec, maxt=30002msec

    Disk stats (read/write):
      sdc: ios=77/1600107, merge=0/1, ticks=2511/939941, in_queue=942389, util=99.36%

    """
    ret, res = commands.getstatusoutput('bash ./dealwith_log.sh {0} {1}'.format(tmp_log, log_name))
    return ret


class my_draw:
    x = []
    y = []
    subplots = 0
    log = str("")

    def __init__(self, count):
        self.subplots = count

    def draw(self, i):
        pl.subplot(self.subplots, 1, i)
        pl.title(os.path.basename(self.log))
        pl.plot(self.x, self.y)  # use pylab to plot x and y
        self.x = []
        self.y = []

    def generate_table_iops(self, log):
        pl.xlabel('Rate of job (Total 1 hour)')
        pl.ylabel('IOPS')
        pl.ylim(0.0, 100000)
        self.log = log
        with open(self.log) as fd:
            for line in fd.readlines():
                if not len(line):
                    continue
                pair = line.strip().split(':')
                if len(pair) != 2:
                    continue
                self.x.append(pair[0])
                if pair[1].endswith('K'):
                    self.y.append(float(pair[1][:-1]) * 1000)
                else:
                    self.y.append(float(pair[1]))

    def save(self):
        pl.savefig(os.path.dirname(self.log) + '.pdf')

    def show(self):
        pl.show()

device = '/dev/sdb'
time = 1*60*60
size_rate = 100
log_name = 'randw_4k_{0}_{1}_{2}%'.format(os.path.basename(device), time, size_rate)

ret = erase_ssd(device)
if ret < 0:
    exit(ret)

ret = excute_fio_benchmark(device=device, size_rate=size_rate,
                           time=time, log_name=log_name)
if ret != 0:
    exit(ret)

if 0:
    flist = walk_all_files("xxxx",
                       patterns='smp_*')

    draw = my_draw(len(flist))

    i = 1
    for f in flist:
        draw.generate_table_iops(f)
        draw.draw(i)
        i += 1
    draw.save()
else:
    draw = my_draw(1)
    draw.generate_table_iops(log_name)
    draw.draw(1)
    draw.save()


