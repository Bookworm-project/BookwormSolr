#!/usr/bin/env bash

## Arg 1: Path to list of "unigram\tyear" to search
unigrams=$1
## Arg 2: The Google NGrams compressed file to search
file=$2
## Arg 3: How many simultaneous jobs is this script allows to run?
maxjobs=$3

## Which characters does the compressed file represent?
chars=`echo $file | cut -d '-' -f 6 | cut -d '.' -f 1`

## get all the unigrams to be found in this file,
## and search the file for all their occurrances
grep -P "^$chars.*?\t" $unigrams | \
	perl -pe "s/([\^\$\[\]\*\.\\\(\)\|\+\?\{\}])/\\\\\1/g" | \
	perl -pe "s/^/\^/g" | \
	/share/apps/bin/parallel -n 1 -j $maxjobs "zgrep \"{}\" $file"
