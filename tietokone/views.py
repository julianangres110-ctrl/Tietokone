from django.core.mail import send_mail
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import KostenvoranschlagForm
from datetime import timedelta
import math
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse

@login_required
def tietokone(request):
    results = None
    if request.method == 'POST':
        form = KostenvoranschlagForm(request.POST)
        if form.is_valid():
            jahr = form.cleaned_data['jahr']
            days = form.cleaned_data['einsatztage']
            aufbautag = form.cleaned_data['aufbautag']
            name_veranstaltung = form.cleaned_data['name_veranstaltung']
            einsatzbeginn = form.cleaned_data['einsatzbeginn']
            sonderequipment_text = form.cleaned_data['sonderequipment']
            sonderequipment_preis = form.cleaned_data['sonderequipment_preis'] or 0

            if days == 1 and aufbautag:
                form.add_error('aufbautag', 'Aufbautag nicht möglich bei 1 Einsatztag.')
            else:
                base_factor = {'2025': 1.0, '2026': 1.05, '2027': 1.10, '2028': 1.15}[jahr]

                # Preise (täglich, Basis)
                manpower_prices = {
                    'projektabwicklung': 150,  # Immer inkludiert
                    'kameramann': 200,
                    'bimi': 180,
                }
                equipment_prices = {
                    'broadcastkamera': 300,
                    'ptz': 250,
                    'satellitenkamera': 200,
                    'videofunk': 150,
                    'bildmischer': 100,
                    'aufzeichnungsmaterial': 40,
                    'master_recorder': 80,
                    'backup_recorder': 70,
                    'intercom': 50,
                    'on_demand_files': 50,
                    'livestreaming': 200,
                }

                # Ausgewählte Items extrahieren
                selected_manpower = {
                    'kameramann': form.cleaned_data['kameramann'],
                    'bimi': form.cleaned_data['bimi'],
                }
                kameramann_anzahl = form.cleaned_data['kameramann_anzahl'] or 1
                bimi_anzahl = form.cleaned_data['bimi_anzahl'] or 1
                selected_equipment = {k: form.cleaned_data[k] for k in equipment_prices}

                # Berechnungen
                manpower_sub = 0
                manpower_details = {}

                # Immer Projektabwicklung (fixed 1)
                adjusted_price = manpower_prices['projektabwicklung'] * base_factor
                total = 1 * adjusted_price  # Fixed 1
                manpower_sub += total
                manpower_details['projektabwicklung'] = f"1 x {adjusted_price:.2f} € = {total:.2f} €"

                for item in ['kameramann', 'bimi']:
                    if selected_manpower[item]:
                        anzahl = kameramann_anzahl if item == 'kameramann' else bimi_anzahl
                        effective_days = days - 1 if item == 'kameramann' and aufbautag else days
                        adjusted_price = manpower_prices[item] * base_factor
                        total = anzahl * effective_days * adjusted_price
                        manpower_sub += total
                        manpower_details[item] = f"Anzahl: {anzahl}, {effective_days} x {adjusted_price:.2f} € = {total:.2f} €"

                equipment_sub = 0
                equipment_details = {}
                for item, price in equipment_prices.items():
                    if selected_equipment[item]:
                        if item in ['broadcastkamera', 'ptz', 'satellitenkamera', 'videofunk', 'bildmischer']:
                            anzahl = form.cleaned_data[f'{item}_anzahl'] or 1
                            adjusted_price = price * base_factor
                            total = anzahl * days * adjusted_price
                            detail = f"{days} x {adjusted_price:.2f} € = {total:.2f} €"
                            if anzahl > 1:
                                detail = f"Anzahl: {anzahl}, {detail}"
                        elif item == 'aufzeichnungsmaterial':
                            anzahl = form.cleaned_data['aufzeichnungsmaterial_anzahl'] or 1
                            adjusted_price = price * base_factor
                            total = anzahl * adjusted_price  # Keine Tagesabhängigkeit
                            detail = f"Anzahl: {anzahl}, {adjusted_price:.2f} € = {total:.2f} €"
                        elif item == 'on_demand_files':
                            anzahl = 1  # Keine Stückzahl-Option, nur einheitlich
                            effective_days = days - 1 if aufbautag else days
                            adjusted_price = price * base_factor
                            total = anzahl * effective_days * adjusted_price
                            detail = f"{effective_days} x {adjusted_price:.2f} € = {total:.2f} €"
                        else:
                            anzahl = 1
                            adjusted_price = price * base_factor
                            total = anzahl * days * adjusted_price
                            detail = f"{days} x {adjusted_price:.2f} € = {total:.2f} €"
                        equipment_sub += total
                        equipment_details[item] = detail

                # Anfahrten automatisch berechnen
                anfahrtsgrundwert = 50  # Festgelegter Wert in €
                kameramann_tage = (days - 1 if aufbautag else days) * kameramann_anzahl if selected_manpower['kameramann'] else 0
                bimi_tage = days * bimi_anzahl if selected_manpower['bimi'] else 0
                anfahrten_total = (kameramann_tage + bimi_tage) * anfahrtsgrundwert * base_factor
                equipment_sub += anfahrten_total
                equipment_details['anfahrten'] = f"{kameramann_tage + bimi_tage} x {anfahrtsgrundwert:.2f} € = {anfahrten_total:.2f} €"

                # Sonderequipment als einmaliger Posten
                if sonderequipment_text and sonderequipment_preis:
                    sonderequipment_total = sonderequipment_preis * base_factor
                    equipment_sub += sonderequipment_total
                    equipment_details['sonderequipment'] = f"{sonderequipment_text}: {sonderequipment_preis} € = {sonderequipment_total:.2f} €"

                sum_manpower = manpower_sub
                sum_equipment = equipment_sub
                grand_total = sum_manpower + sum_equipment

                # Zeitraum-Berechnung
                if einsatzbeginn:
                    if days <= 1:
                        zeitraum = f"Am {einsatzbeginn.strftime('%d.%m.%Y')}"
                    else:
                        end_date = einsatzbeginn + timedelta(days=math.ceil(days) - 1)
                        zeitraum = f"Von {einsatzbeginn.strftime('%d.%m.%Y')} bis {end_date.strftime('%d.%m.%Y')}"
                else:
                    zeitraum = "Kein Einsatzbeginn angegeben"

                results = {
                    'manpower_sub': manpower_sub,
                    'equipment_sub': equipment_sub,
                    'sum_manpower': sum_manpower,
                    'sum_equipment': sum_equipment,
                    'grand_total': grand_total,
                    'manpower_details': manpower_details,
                    'equipment_details': equipment_details,
                    'name_veranstaltung': name_veranstaltung,
                    'zeitraum': zeitraum,
                }

                # E-Mail versenden
                subject = f"{name_veranstaltung or 'Kostenvoranschlag'} - {zeitraum}"
                message = f"Ergebnisse für {name_veranstaltung or 'Kostenvoranschlag'}\n\n"
                message += f"Zeitraum: {zeitraum}\n\n"
                message += "Manpower:\n"
                for item, calc in manpower_details.items():
                    message += f"- {item}: {calc}\n"
                message += f"Summe Manpower: {sum_manpower:.2f} €\n\n"
                message += "Equipment:\n"
                for item, calc in equipment_details.items():
                    message += f"- {item}: {calc}\n"
                message += f"Summe Equipment: {sum_equipment:.2f} €\n\n"
                message += f"Grand Total: {grand_total:.2f} €"

                send_mail(
                    subject,
                    message,
                    'info@nuntii.tech',
                    ['mediatv.studio@t-online.de'],
                    fail_silently=False,  # Zum Debugging: Setze auf True in Prod
                )
                request.session['results'] = results
    else:
        form = KostenvoranschlagForm()

    return render(request, 'tietokone/tietokone.html', {'form': form, 'results': results})

@login_required
def generate_pdf(request):
    results = request.session.get('results')
    if not results:
        return HttpResponse("Keine Daten verfügbar.", status=400)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="kostenvoranschlag.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Titel
    elements.append(Paragraph(f"Ergebnisse für {results['name_veranstaltung']}", styles['Heading1']))
    elements.append(Paragraph(f"Zeitraum: {results['zeitraum']}", styles['Heading2']))
    elements.append(Spacer(1, 12))

    # Manpower-Tabelle
    elements.append(Paragraph("Manpower", styles['Heading2']))
    manpower_data = [['Item', 'Details']]
    for item, calc in results['manpower_details'].items():
        manpower_data.append([item, calc])
    manpower_table = Table(manpower_data)
    elements.append(manpower_table)
    elements.append(Paragraph(f"Summe Manpower: {results['sum_manpower']:.2f} €", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Equipment-Tabelle
    elements.append(Paragraph("Equipment", styles['Heading2']))
    equipment_data = [['Item', 'Details']]
    for item, calc in results['equipment_details'].items():
        equipment_data.append([item, calc])
    equipment_table = Table(equipment_data)
    elements.append(equipment_table)
    elements.append(Paragraph(f"Summe Equipment: {results['sum_equipment']:.2f} €", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Grand Total
    elements.append(Paragraph(f"Grand Total: {results['grand_total']:.2f} €", styles['Heading1']))

    doc.build(elements)
    return response