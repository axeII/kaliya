# Paths
FILE="/usr/local/bin/kaliya"
DBASE="$$HOME/.kaliya.list"

# Colors
ccred='\033[0;31m'
ccyellow='\033[0;33m'
ccend='\033[0m'

install:
	@echo $(ccred)"Installing script"$(ccend)
	echo "!$$(type python | cut -d' ' -f3)" > $(FILE)
	cat "kaliya.py" >> $(FILE)
	chmod u+x $(FILE)
	@echo $(ccred)"Creating local dabase"$(ccend)
	touch $(DBASE)

uninstall:
	@echo $(ccred)"Uninstalling script"$(ccend)
	@echo $(ccyellow)"Data found you can backup them for later:"$(ccend)
	@echo ""
	@touch $(DBASE) && cat $(DBASE)
	@echo ""
	rm -f $(FILE)
	rm -f $(DBASE)
