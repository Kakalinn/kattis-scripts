#!/usr/bin/env bash
# An example of a simple script the uses the query.py script.
# It takes as an argument whatever you want to submit using
# Kattis's submition client and submits. It then waits until
# the status of your most recent submission is not "New" or
# "Running" and prints it.
# In other words, waits for a verdict, and tells you how you
# did.
./submit.py -f $@
t=$(./query.py -m -c 1)
while [ "$t" == "New" ] || [ "$t" == "Running" ]
do
	sleep 3
	t=$(./query.py -m -c 1)
done
echo $t
