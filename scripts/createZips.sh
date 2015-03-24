#!/bin/bash
cpt=1
here=$(pwd)
while read line
do
    zipFolder=$line
    cd $zipFolder
    zip -r "$here/PySrc$cpt.zip" .
    ((cpt++))
    
done < zip.conf
