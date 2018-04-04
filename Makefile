FILE="/usr/local/bin/kaliya"

install:
	echo "#!$$(type python | cut -d' ' -f3)" > $(FILE)
	cat "kaliya.py" >> $(FILE)
	chmod u+x $(FILE)

uninstall:
	rm $(FILE)

