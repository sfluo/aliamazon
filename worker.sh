#!/bin/bash

today=`date +%Y-%m-%d`
datapath='./data'

if [ ! -e "$datapath/$today" ]; then
	mkdir -p "$datapath/$today"
fi

chmod +w "$datapath/$today"

mkdir -p "$datapath/$today/paid-textbooks"
python crawler.py books.5.txt "$datapath/$today/paid-textbooks" &

mkdir -p "$datapath/$today/tools-homeimprov"
python crawler.py humannoval.3.txt "$datapath/$today/tools-homeimprov" &

mkdir -p "$datapath/$today/digital-music"
python crawler.py music.5.txt "$datapath/$today/digital-music" &

