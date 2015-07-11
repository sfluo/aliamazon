#!/bin/bash
# automate the analyzing daily

today=`date +%Y-%m-%d`
dstpath="/data/$today"
srcpath='/home/ubuntu/amazoncrawl'

# if data does not exist, then nothing to do 
if [ ! -e "$dstpath" ]; then
	exit
fi

find $dstpath -name '*.json' | xargs python $srcpath/analyzer.py "$dstpath.csv"

