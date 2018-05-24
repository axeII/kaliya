#
#Makefile for kaliya
#In case reading my code I recomend https://www.suicideline.org.au/
#
.PHONY: all install uninstall

# Paths
FILE="/usr/local/bin/kaliya"
DBASE="$$HOME/.kaliya.list"
spruce_type=linux64
ME := $(who | shell awk '{print $$1}')

# Values
PYTHON3 := $(shell command -v python3 &>/dev/null)
PIP3 := $(command -v pip3 &>/dev/null)

# Colors
ccred='\033[0;31m'
ccgreen='\033[0;32m'
ccyellow='\033[0;33m'
ccend='\033[0m'

install:
ifdef PIP3
	@echo $(ccgreen)"[INFO] Installing PIP3"$(ccend)
	@curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
	@sudo python3 get-pip.py --user
endif
	
ifdef PYTHON3
	@echo $(ccgreen)"[INFO] Please run as root if you are on linux"$(ccend)
	@echo $(ccgreen)"[INFO] Installing needed prerequisites"$(ccend)
	@pip3 install requests --user
	@pip3 install bs4 --user
	@pip3 install selenium --user
	@echo $(ccgreen)"[INFO] Installing script"$(ccend)
	@if [ "$$(uname)" = "Linux" ]; then\
		sudo touch $(FILE);\
		sudo chown $$(who | awk '{print $$1}'):$$(who | awk '{print $$1}') $(FILE);\
		echo "#!$$(type python3.6 | cut -d' ' -f3)" > $(FILE);\
		cat "kaliya.py" >> $(FILE);\
		chmod u+x $(FILE);\
	fi
	@if [ "$$(uname)" = "Linux" ]; then\
		echo "[INFO] Detected linux machine"
		wget $$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep browser_download_url | cut -d '"' -f 4 | grep linux64);\
		tar -xvzf geckodriver*.gz;\
		sudo mv geckodriver /usr/local/bin/;\
		sudo chown $$(who | awk '{print $$1}'):$$(who | awk '{print $$1}') /usr/local/bin/geckodriver;\
		sudo rm -rf geckodriver*.gz
	fi
	@echo $(ccgreen)"[INFO] Creating local dabase"$(ccend)
	@touch $(DBASE)
	@chown $$(who | awk '{print $$1}'):$$(who | awk '{print $$1}') $(DBASE)
	@echo "Please install geodriver for firefox: "$(ccyellow)"https://github.com/mozilla/geckodriver/releases"$(ccend)
else
	@echo $(ccred)"[Error] python3.6 is not installed... cannot continue"$(ccend)
endif

uninstall:
	@echo $(ccyellow)"[Warning] Uninstalling script"$(ccend)
	@echo ""
	@echo $(ccgreen)"[INFO] Data found you can backup them for later:"$(ccend)
	@echo ""
	@touch $(DBASE) && cat $(DBASE)
	@echo ""
	rm -f $(FILE)
	rm -f $(DBASE)
