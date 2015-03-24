#!/bin/bash
main=$1
user=wdroz
server=157.26.83.52
tmpZipList=zipList.txt
./createZips.sh
scp *.zip $main $user@$server:~
ls -1 *.zip > $tmpZipList
zipString=""
while read line
do
   zipString="$line,$zipString"
done < $tmpZipList
rm $tmpZipList
command=$(echo "./spark-1.2.1-bin-hadoop2.4/bin/spark-submit --deploy-mode client --master yarn-client --py-files \"$zipString\" $main")
#ssh $user@$server ''$command''
./runOnServer $user $server "$command"
