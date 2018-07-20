#
#Makefile for kaliya
#In case reading my code I recomend https://www.suicideline.org.au/
#
.PHONY: all install uninstall

# Paths
FILE="/usr/local/bin/kaliya"
DBASE="$$HOME/.kaliya.list"

# Values
PYTHON3 := $(shell command -v python3.7 2>/dev/null)
PIP3 := $(command -v pip3 2>/dev/null)
USER := $(who | awk 'NR==1{print $$1}')

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
	@sudo touch $(FILE)
	@if [ "$$(uname)" = "Linux" ]; then \
		sudo chown "$$(who | awk 'NR==1{print $$1}'):$$(who | awk 'NR==1{print $$1}')" $(FILE); \
	elif [ "$$(uname)" = "Darwin" ]; then \
		sudo chown "$$(who | awk 'NR==1{print $$1}'):staff" $(FILE); \
	else \
		echo "Error";\
	fi
	@echo "#!$$(type python3.7 | cut -d ' ' -f3)" > $(FILE)
	@cat "kaliya.py" >> $(FILE)
	@chmod u+x $(FILE)
	@if [ "$$(uname)" = "Linux" ]; then \
		echo "[INFO] Detected linux machine";\
		wget $$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep browser_download_url | cut -d '"' -f 4 | grep linux64);\
  	elif [ "$$(uname)" = "Darwin" ]; then \
		echo "[INFO] Detected macos machine";\
		brew install wget;\
		wget $$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep browser_download_url | cut -d '"' -f 4 | grep macos); \
	else \
		echo "Error";\
	fi
	@tar -xvzf geckodriver*.gz
	@sudo mv geckodriver /usr/local/bin/
	@if [ "$$(uname)" = "Linux" ]; then \
		sudo chown "$$(who | awk 'NR==1{print $$1}'):$$(who | awk 'NR==1{print $$1}')" /usr/local/bin/geckodriver; \
	elif [ "$$(uname)" = "Darwin" ]; then \
		sudo chown "$$(who | awk 'NR==1{print $$1}'):staff" /usr/local/bin/geckodriver; \
	else \
		echo "Error";\
	fi
	@sudo rm -rf geckodriver*.gz
	@echo $(ccgreen)"[INFO] Creating local dabase"$(ccend)
	@touch $(DBASE)
	@if [ "$$(uname)" = "Linux" ]; then \
		sudo chown "$$(who | awk 'NR==1{print $$1}'):$$(who | awk 'NR==1{print $$1}')" $(DBASE); \
	elif [ "$$(uname)" = "Darwin" ]; then \
		sudo chown "$$(who | awk 'NR==1{print $$1}'):staff" $(DBASE); \
	else \
		echo "Error";\
	fi
else
	@echo $(ccred)"[Error] python3.7 is not installed exiting..."$(ccend)
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
