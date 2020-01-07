#!/usr/bin/env bash
case "$1" in
"stats" | "s")
	~/.local/lib/battis-stats.py ${@:2}
    ;;
"query" | "q")
	~/.local/lib/battis-query.py ${@:2}
    ;;
*)
	echo "top10, query (q)"
    ;;
esac
