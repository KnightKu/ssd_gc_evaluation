#!/usr/bin/env bash
if  [ ! -n "$1" ] ;then
    return
fi
pushd $1
for item in `ls`; do
	cat $item | grep '\[eta' | awk -F "[\\\\[\\\\]]" '{printf ("%.2f:%s\n", substr($4, 0, length($4) - 6), substr($8, 3, length($8) - 9))}' > smp_${item}
done
popd
