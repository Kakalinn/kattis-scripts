build:
	mkdir -p ~/.local/lib
	cp battis.sh ~/.local/bin/battis
	cp query.py ~/.local/lib/battis-query.py
	cp stats.py ~/.local/lib/battis-stats.py
clean:
	rm ~/.local/bin/battis
	rm ~/.local/lib/battis-query.py
	rm ~/.local/lib/battis-stats.py
