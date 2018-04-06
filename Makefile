# Paths
FILE="/usr/local/bin/kaliya"
DBASE="$$HOME/.kaliya.list"

# Colors
ccred='\033[0;31m'
ccyellow='\033[0;33m'
ccend='\033[0m'

install:
	@echo $(ccyellow)"[INFO] Installing needed prerequisites"$(ccend)
	@pip install requests
	@pip install bs4
	@echo $(ccyellow)"[INFO] Installing script"$(ccend)
	echo "#!$$(type python | cut -d' ' -f3)" > $(FILE)
	cat "kaliya.py" >> $(FILE)
	chmod u+x $(FILE)
	@echo $(ccyellow)"[INFO] Creating local dabase"$(ccend)
	touch $(DBASE)
	@echo "Please install geodriver for firefox: "$(ccyellow)"https://github.com/mozilla/geckodriver/releases"$(ccend)

uninstall:
	@echo $(ccred)"[Warning] Uninstalling script"$(ccend)
	@echo $(ccyellow)"[INFO] Data found you can backup them for later:"$(ccend)
	@echo ""
	@touch $(DBASE) && cat $(DBASE)
	@echo ""
	rm -f $(FILE)
	rm -f $(DBASE)
