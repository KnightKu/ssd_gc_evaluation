#!/usr/bin/env bash
# rate:iops
cat $1 | grep '\[eta' | awk -F "[\\\\[\\\\]]" '{printf ("%.2f:%s\n", substr($4, 0, length($4) - 6), substr($8, 3, length($8) - 9))}' > $2
# rate:bandwidth
#cat $1 | grep '\[eta' | awk -F "[\\\\[\\\\]]" '{split($6, s, "/");printf ("%.2f:%s\n", 200 + substr($4, 0, length($4) - 6), s[2])}' > $2