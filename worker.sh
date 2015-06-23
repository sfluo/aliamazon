#!/bin/bash

today=`date +%Y-%m-%d`
datapath='/data'
currentpath='/home/ubuntu/amazoncrawl'

if [ ! -e "$datapath/$today" ]; then
    mkdir -p "$datapath/$today"
fi

chmod +w "$datapath/$today"

mkdir -p "$datapath/$today/paid-textbooks"
python $currentpath/crawler.py book "$currentpath/head3000urls/Paid-Textbooks_chemistry+books+paperback.1200.txt" "$datapath/$today/paid-textbooks" &
python $currentpath/crawler.py book "$currentpath/head3000urls/Paid-Textbooks_mathematics+books+paperback.1200.txt" "$datapath/$today/paid-textbooks" &
python $currentpath/crawler.py book "$currentpath/head3000urls/Paid-Textbooks_physics+books+paperback.1200.txt" "$datapath/$today/paid-textbooks" &

mkdir -p "$datapath/$today/kindle-freebooks"
python $currentpath/crawler.py book "$currentpath/head3000urls/Kindle-eBooks-(free)_Free+chemistry+books.219.txt" "$datapath/$today/kindle-freebooks" &
python $currentpath/crawler.py book "$currentpath/head3000urls/Kindle-eBooks-(free)_Free+fiction+novels.3000.txt" "$datapath/$today/kindle-freebooks" &
python $currentpath/crawler.py book "$currentpath/head3000urls/Kindle-eBooks-(free)_Free+mathematics+books.548.txt" "$datapath/$today/kindle-freebooks" &
python $currentpath/crawler.py book "$currentpath/head3000urls/Kindle-eBooks-(free)_Free+Physics+books.259.txt" "$datapath/$today/kindle-freebooks" &

mkdir -p "$datapath/$today/fiction-novels"
python $currentpath/crawler.py book "$currentpath/head3000urls/Humor-and-Entertainment_fiction+novels+paperback.1200.txt" "$datapath/$today/fiction-novels" &
python $currentpath/crawler.py book "$currentpath/head3000urls/Science-fiction-&-fantasy_fiction+novels+paperback.1200.txt" "$datapath/$today/fiction-novels" &

mkdir -p "$datapath/$today/tools-homeimprov"
python $currentpath/crawler.py home "$currentpath/head3000urls/Tools-&-Home-Improvement_air+conditioners.3000.txt" "$datapath/$today/tools-homeimprov" &
python $currentpath/crawler.py home "$currentpath/head3000urls/Refrigerators_fridges.923.txt" "$datapath/$today/tools-homeimprov" &

mkdir -p "$datapath/$today/digital-music"
python $currentpath/crawler.py music "$currentpath/head3000urls/Digital-Music_free+songs.3000.txt" "$datapath/$today/digital-music" &
python $currentpath/crawler.py music "$currentpath/head3000urls/Digital-Music_songs.3000.txt" "$datapath/$today/digital-music" &

mkdir -p "$datapath/$today/computers"
python $currentpath/crawler.py office "$currentpath/head3000urls/Computers_computers.3000.txt"  "$datapath/$today/computers" &  

mkdir -p "$datapath/$today/womanjewelry"
python $currentpath/crawler.py jewelry "$currentpath/head3000urls/Woman's-Jewelry_jewelry.3000.txt" "$datapath/$today/womanjewelry" &

mkdir -p "$datapath/$today/videogame"
python $currentpath/crawler.py office "$currentpath/head3000urls/Xbox-360-Games_video+games.3000.txt" "$datapath/$today/videogame" &

mkdir -p "$datapath/$today/officeproduct"
python $currentpath/crawler.py office "$currentpath/head3000urls/Office-Products_Calculator.3000.txt" "$datapath/$today/officeproduct" & 
python $currentpath/crawler.py office "$currentpath/head3000urls/Office-Products_Printer.3000.txt" "$datapath/$today/officeproduct" & 

mkdir -p "$datapath/$today/officefurniture"
python $currentpath/crawler.py office "$currentpath/head3000urls/Office-Furniture-&-Lighting_furniture.3000.txt" "$datapath/$today/officefurniture" &


