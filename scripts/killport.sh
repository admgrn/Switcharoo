#! /bin/sh
for port in $@
do
	((kill -9 `lsof -ti :$port` 2> /dev/null) && echo Port $port Closed) || echo Port $port Not Open
done
