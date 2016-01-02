# naptime

Das Skript "naptime" legt einen Rechner sobald der nicht mehr benötigt wird schlafen oder schaltet ihn aus. Hierzu muss das Skript per Cron-Job regelmäßig ausgeführt werden. Der rechner wird erst nach dem zweiten positiven Abschluss aller Tests ausgeschaltet.

Bei der Verwendung von TVheadend wird der Rechner vor der nachsten Aufnahme automatisch wieder gestartet.

## Installation
Daten kopieren:

	cd /usr/local
	git clone ...

### Konfiguration
Das Skript sucht in /etc nach der Konfigurationsdatei. Kopieren der Vorlage:

	cp /usr/local/naptime/conf/naptime.conf.example /etc/naptime.conf
	vi /etc/naptime.conf

Die Konfigurationsdatei kann an die presönlichen Bedürfnisse angepasst werden. Hierbei ist folgendes zu beachten:
* Die Konfigurationsdatei bestimmt die Checkreihenfolge des Skriptes.
* Nicht benötigte Gruppen/Einträge können mit **#** auskommentiert werden. 

### Cron-Job
Um das Skript alle 10 min auszuführen, müssen in

	/etc/crontab 

folgende Zeilen eingefügt werden:

	## naptime
	*/10 *    * * * root	/usr/bin/python /usr/local/naptime/naptime.py > /var/log/naptime.log

## Power Button deaktivieren
Seit Ubuntu 14.04 wird systemd's logind verwendet

	vi /etc/systemd/logind.conf

Folgende Zeilen anhängen:

	HandlePowerKey=ignore
	HandleSuspendKey=ignore
	HandleHibernateKey=ignore
	HandleLidSwitch=ignore

Dienst neu starten:

	service systemd-logind restart

## Shutdown und Reboot in KDE ausblenden

* Systemsteuerung > Starten und Beenden > Sitzungverwaltung > Allgemein > "Optionen für das Heruterfahren anbieten" abwählen

##  Quellen
- [ACPI not running custom script on power button press](http://askubuntu.com/questions/493499/acpi-not-running-custom-script-on-power-button-press)
- [How to Disable ‘Logout/Reboot/Shutdown’ Conformation dialog in KDE (4.8x)](http://www.hecticgeek.com/2012/05/disable-logout-reboot-shutdown-conformation-kde/)
