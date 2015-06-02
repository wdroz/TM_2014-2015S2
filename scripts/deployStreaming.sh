#!/bin/bash
main=$1
model=$2
graph=$3
user=wdroz
server=157.26.83.52
tmpZipList=zipList.txt
./createZips.sh
scp *.zip $main $user@$server:~
#scp ../src/*.p $main $user@$server:~
ls -1 *.zip > $tmpZipList
zipString=""
while read line
do
   zipString="$line,$zipString"
done < $tmpZipList
rm $tmpZipList
command=$(echo "./spark-1.3.1-bin-hadoop2.4/bin/spark-submit --deploy-mode client --master yarn-client --py-files \"$zipString\" --archives \"nltk_data.zip\" $main \"$model\" \"$graph\"")
#ssh $user@$server ''$command''
./runOnServer $user $server "$command"
