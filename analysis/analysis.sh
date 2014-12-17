# 1. Get 40 biggest Ngram files to sample from
du -B MB google/2gram/* | sort -n | tail -n 40 | grep -o "google/.*$" >Biggest2GramFiles.txt

# 2. Manually clean to remove punctuation, numeric, other data

# 3. Sample A small percentage of bi-grams from each file

cat Biggest2GramFiles.txt | /share/apps/bin/parallel -j 16 -n 1 --progress "zgrep -P \"(.*?\t){2,}\d{4,}\" {} | grep -Pv \" [\'\,\.-]|_\S+_\" | perl -n -e 'print if (rand() < 0.01)'" >bigram-sample.txt

# 4 Trim the sample some more, and remove bigrams where either of the grams doesn't start with an alphanumeric character
sort -R bigram-sample.txt | grep -P "^[\w\d].*? [\w\d].*?" | head -n 1000 >bigram-sample-sm.txt

# 5. Pull out all unigram/year pairs
perl -pe "s/(.*?) (.*?)\t(\d{4}).*/\1\t\3/g" bigram-sample-sm.txt >unigram-list.txt
perl -pe "s/(.*?) (.*?)\t(\d{4}).*/\2\t\3/g" bigram-sample-sm.txt >>unigram-list.txt
less unigram-list.txt | sort | uniq >unigram-list-nodupes.txt
rm unigram-list.txt

# 6. For each sampled bigram, search again for all lines with that bigram (i.e. all years)

## First, find all the characters that start words, so we know which Ngram exports should be looked in.
## The past the proper file and a MAXJOBS argument to find-unigrams.sh
grep -o "^." unigram-list-nodupes.txt | \
	tr '[:upper:]' '[:lower:]' | \
	uniq | \
	/share/apps/bin/parallel -n 1 -j 5 --progress --eta ./find-unigrams.sh unigram-list-nodupes.txt google/1gram/googlebooks-eng-all-1gram-20120701-{}.gz 4 >unigrams.txt
