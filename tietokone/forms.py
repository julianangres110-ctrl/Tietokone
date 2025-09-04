from django import forms

class KostenvoranschlagForm(forms.Form):
    jahr = forms.ChoiceField(choices=[('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('2028', '2028')], label='Jahr wählen')
    einsatztage = forms.FloatField(min_value=0.5, label='Zahl der Einsatztage angeben (auch Dezimalzahl mit Komma möglich, z. B. 1,5 für Eineinhalb Einsatztage)')
    aufbautag = forms.BooleanField(required=False, label='Mit Aufbautag (reduzierte Manpower, Beginn der Veranstaltung am Folgetag, keine Proben)')
    name_veranstaltung = forms.CharField(max_length=200, required=False, label='Name Veranstaltung')
    einsatzbeginn = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False, label='Einsatzbeginn')

    # Manpower Items (auswählbar)
    kameramann = forms.BooleanField(required=False, initial=False, label='Kameramann')
    kameramann_anzahl = forms.IntegerField(min_value=1, required=False, initial=1, label='Anzahl Kameramänner')
    bimi = forms.BooleanField(required=False, initial=False, label='Bimi')
    bimi_anzahl = forms.IntegerField(min_value=1, required=False, initial=1, label='Anzahl Bimis')

    # Equipment Items (auswählbar mit Stückzahllogik)
    broadcastkamera = forms.BooleanField(required=False, initial=False, label='Broadcastkamera')
    broadcastkamera_anzahl = forms.IntegerField(min_value=1, required=False, initial=1, label='Anzahl Broadcastkameras')
    ptz = forms.BooleanField(required=False, initial=False, label='PTZ inkl. Steuergerät')
    ptz_anzahl = forms.IntegerField(min_value=1, required=False, initial=1, label='Anzahl PTZ')
    satellitenkamera = forms.BooleanField(required=False, initial=False, label='Satellitenkamera (unbesetzt)')
    satellitenkamera_anzahl = forms.IntegerField(min_value=1, required=False, initial=1, label='Anzahl Satellitenkameras')
    videofunk = forms.BooleanField(required=False, initial=False, label='Prof. Videofunk')
    videofunk_anzahl = forms.IntegerField(min_value=1, required=False, initial=1, label='Anzahl Videofunk')
    aufzeichnungsmaterial = forms.BooleanField(required=False, initial=False, label='Aufzeichnungsmaterial XDCAM (je 2 Std.)')
    aufzeichnungsmaterial_anzahl = forms.IntegerField(min_value=1, required=False, initial=1, label='Anzahl Aufzeichnungsmaterial')
    bildmischer = forms.BooleanField(required=False, initial=False, label='Bildmischer')
    bildmischer_anzahl = forms.IntegerField(min_value=1, required=False, initial=1, label='Anzahl Bildmischer')
    master_recorder = forms.BooleanField(required=False, initial=False, label='Master-Recorder')
    backup_recorder = forms.BooleanField(required=False, initial=False, label='Backup-Recorder')
    intercom = forms.BooleanField(required=False, initial=False, label='Intercom/Returnvideo/Kabel/Adapter')
    on_demand_files = forms.BooleanField(required=False, initial=False, label='Anfertigung On-Demand-Files (je Tag)')
    livestreaming = forms.BooleanField(required=False, initial=False, label='Livestreaming Unit inkl. Backup')

    # Neues Sonderequipment-Feld
    sonderequipment = forms.CharField(max_length=200, required=False, label='Sonderequipment, Reserve, Eventualitäten: ')
    sonderequipment_preis = forms.IntegerField(min_value=0, required=False, label='     Preis')