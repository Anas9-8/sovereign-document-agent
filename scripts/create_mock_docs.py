"""Create 3 realistic German mock PDF documents for benchmarking."""

from fpdf import FPDF


def create_rechnung():
    """German invoice."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Rechnung", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", size=10)
    lines = [
        "Rechnungsnummer: RE-2024-001",
        "Rechnungsdatum: 15.03.2024",
        "",
        "Absender:",
        "TechSolutions GmbH",
        "Musterstrasse 42, 80331 Muenchen",
        "USt-IdNr.: DE123456789",
        "",
        "Empfaenger:",
        "Max Mustermann",
        "Beispielweg 7, 10115 Berlin",
        "",
        "-" * 60,
        "Pos.  Beschreibung                        Menge   Einzelpreis   Gesamt",
        "-" * 60,
        "1     IT-Beratung (Stunden)                 10    120,00 EUR   1.200,00 EUR",
        "2     Softwarelizenz Enterprise               1    850,00 EUR     850,00 EUR",
        "3     Cloud-Hosting (Monat)                   3    149,00 EUR     447,00 EUR",
        "-" * 60,
        "",
        "Zwischensumme (netto):                              2.497,00 EUR",
        "Umsatzsteuer (19%):                                   474,43 EUR",
        "Gesamtbetrag (brutto):                              2.971,43 EUR",
        "",
        "Zahlungsbedingungen: Zahlbar innerhalb von 14 Tagen ohne Abzug.",
        "",
        "Bankverbindung:",
        "TechSolutions GmbH",
        "IBAN: DE89 3704 0044 0532 0130 00",
        "BIC: COBADEFFXXX",
        "Commerzbank Muenchen",
        "",
        "Vielen Dank fuer Ihren Auftrag!",
    ]

    for line in lines:
        pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")

    pdf.output("data/docs/rechnung_2024_001.pdf")
    print("Created: rechnung_2024_001.pdf")


def create_datenblatt():
    """Technical data sheet."""
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Technisches Datenblatt", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", size=10)
    lines = [
        "Produktname: IndustrieController X200",
        "Modellnummer: IC-X200-PRO",
        "Hersteller: AutomaTech AG, Stuttgart",
        "",
        "Technische Spezifikationen:",
        "-" * 60,
        "Parameter                     Wert",
        "-" * 60,
        "Abmessungen (BxHxT)          220 x 150 x 45 mm",
        "Gewicht                       1,2 kg",
        "Leistungsaufnahme            24 W (max. 36 W)",
        "Versorgungsspannung          24 V DC (+/- 10%)",
        "Betriebstemperatur           -20 bis +60 Grad Celsius",
        "Lagertemperatur              -40 bis +85 Grad Celsius",
        "Schutzart                     IP65",
        "Schnittstellen                2x Ethernet, 1x RS-485, 1x USB-C",
        "Speicher                      4 GB RAM, 32 GB eMMC",
        "Prozessor                     ARM Cortex-A72, 1,5 GHz Quad-Core",
        "-" * 60,
        "",
        "Zertifizierungen:",
        "- CE-Konformitaet gemaess EU-Richtlinie 2014/30/EU",
        "- ISO 9001:2015 (Qualitaetsmanagement)",
        "- ISO 14001:2015 (Umweltmanagement)",
        "- UL 61010-1 (Sicherheit)",
        "",
        "Hersteller:",
        "AutomaTech AG",
        "Industriestrasse 15, 70565 Stuttgart",
        "Tel.: +49 711 123456-0",
        "E-Mail: info@automatech-ag.example.de",
        "",
        "Stand: Maerz 2024 | Technische Aenderungen vorbehalten.",
    ]

    for line in lines:
        pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")

    pdf.output("data/docs/datenblatt_produkt_x200.pdf")
    print("Created: datenblatt_produkt_x200.pdf")


def create_vertrag():
    """Service contract summary."""
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Dienstleistungsvertrag", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", size=10)
    lines = [
        "Vertragsnummer: DV-2024-0042",
        "",
        "Vertragsparteien:",
        "Auftraggeber: Mustermann Logistik GmbH, Hamburg",
        "Auftragnehmer: TechSolutions GmbH, Muenchen",
        "",
        "Leistungsbeschreibung:",
        "Der Auftragnehmer erbringt IT-Dienstleistungen im Bereich",
        "Systemadministration und Netzwerkueberwachung fuer die",
        "Infrastruktur des Auftraggebers. Dies umfasst:",
        "- Monitoring aller Server und Netzwerkkomponenten (24/7)",
        "- Monatliche Sicherheitsupdates und Patch-Management",
        "- Incident Response mit garantierter Reaktionszeit von 4 Stunden",
        "- Quartalsweise Sicherheitsaudits und Berichte",
        "",
        "Vertragslaufzeit:",
        "Beginn: 01.04.2024",
        "Ende: 31.03.2025",
        "",
        "Verguetung:",
        "Monatliche Pauschale: 4.500,00 EUR (netto)",
        "Zahlbar jeweils zum 1. des Monats.",
        "",
        "Kuendigungsfrist: 3 Monate zum Quartalsende.",
        "",
        "Anwendbares Recht:",
        "Dieser Vertrag unterliegt dem Recht der Bundesrepublik Deutschland.",
        "Gerichtsstand ist Muenchen.",
        "",
        "Unterschriften:",
        "",
        "____________________________    ____________________________",
        "Mustermann Logistik GmbH        TechSolutions GmbH",
        "Hamburg, 15.03.2024              Muenchen, 15.03.2024",
    ]

    for line in lines:
        pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")

    pdf.output("data/docs/vertrag_dienstleistung_2024.pdf")
    print("Created: vertrag_dienstleistung_2024.pdf")


if __name__ == "__main__":
    create_rechnung()
    create_datenblatt()
    create_vertrag()
    print("\nAll 3 documents created in data/docs/")
