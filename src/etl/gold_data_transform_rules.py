from typing import List, Tuple

class TransformRule:
    """Since there are no categories yet which have the same name but different parent categories,
    no distinction is necessary regarding their full path. So until there are no such categories it
    is sufficient to only replace one string with another without having to traverse any category tree.
    So only the 'leaf' categories of the 'category tree' are replaced."""

    cat_replacements: List[Tuple[str, str]]

class TransformRule1(TransformRule): #TODO: Train a model on this (data can be found in commit ef93afaf77a3161c554ea997925a5a65b0db04dc data/training_data/codings_merged/train100-eval0/eval_data.csv)
    """SC + SM + Andere Anwendungsfelder"""
    # formerly TransformRule2

    cat_replacements = [
        ("Soziales, soz. Interaktion, Companions, vermenschlichte Robots", "Social Companions"),
        ("Robotik", "Social Companions"),
        ("Seniorenbetreuung, Altenpflege", "Social Companions"),

        ("Social Media (Facebook, Youtube & Co.), Suchmaschinen, Plattfor", "Soziale Medien"),
        ("Politische Informationen und Nachrichten in Sozialen Medien/SM+", "Soziale Medien"),

        ("mehrere Anwendungsfelder", "Andere Anwendungsfelder"),
        ("KI, Rob, Alg oder Autom allgem/unabhängig von AF/Meta/", "Andere Anwendungsfelder"),
        ("Ausbildung, Bildung zu und für KI, Algo, Bots, Autom", "Andere Anwendungsfelder"),
        ("Agrar-/Landwirtschaft (zB Smart Farming, Autom. in LW), Lebensm", "Andere Anwendungsfelder"),
        ("Industrie, Fertigung, Industrie 4.0 (z.b. Automatisierung von F", "Andere Anwendungsfelder"),
        ("F&E: Industrie, Fertigung, Maschinen / gener. Forsch an KI, Rob", "Andere Anwendungsfelder"),
        ("Medizinische Forschung (zb Automatis. der Qualitätskontrolle)", "Andere Anwendungsfelder"),
        ("Medizin, Gesundheit (Anwendungsbezogen)", "Andere Anwendungsfelder"),
        ("Werbung/Marketing/PR, CRM, SEO", "Andere Anwendungsfelder"),
        ("Verkehr/Logistik, Mobilität (autonomes Fahren)", "Andere Anwendungsfelder"),
        ("Luftfahrt, Raumfaht", "Andere Anwendungsfelder"),
        ("Smart home, smart living, consumer electronics", "Andere Anwendungsfelder"),
        ("Medien, Telekommunikation", "Andere Anwendungsfelder"),
        ("Druck/Reprotechnik", "Andere Anwendungsfelder"),
        ("Energie- und Bauwirtschaft", "Andere Anwendungsfelder"),
        ("Sport/Wettbewerbe (z.B. Roboter-Cup)", "Andere Anwendungsfelder"),
        ("Computer-/Videospiele", "Andere Anwendungsfelder"),
        ("Kreativleistung (KI schreibt, komponiert) und E-Kunst", "Andere Anwendungsfelder"),
        ("Öffentl. Sicherheit (Polizei, Geheimdienst, Predictiv Policing)", "Andere Anwendungsfelder"),
        ("Militär und Krieg", "Andere Anwendungsfelder"),
        ("Post / Zustelldienste", "Andere Anwendungsfelder"),
        ("Rettungswesen, Bergungen", "Andere Anwendungsfelder"),
        ("Gastgewerbe, Handel, Tourismus", "Andere Anwendungsfelder"),
        ("Mess-/Analyse-/Labortechnik", "Andere Anwendungsfelder"),
        ("Bilderkennung, Spracherkennung, Sentiment Analyse, Machine Lear", "Andere Anwendungsfelder"),
        ("diverse IT-Anwendungen (Kryptogr., Netzwerkanal., etc)", "Andere Anwendungsfelder"),
        ("Reinigungsbranche", "Andere Anwendungsfelder"),
        ("Banken, Börsen-, Versicherungen, Finanzdienste", "Andere Anwendungsfelder"),
        ("Recht & Justiz", "Andere Anwendungsfelder"),
        ("Automatisierung/KI in anderen Feldern: MEMO!", "Andere Anwendungsfelder"),
        ("Personalwesen (Personalauswahl/-recruting, HR, AMS)", "Andere Anwendungsfelder"),
    ]

class TransformRule2(TransformRule):
    """SC + SM + Alle Anwendungsfelder
    Improvement on TransformRule2
    """
    # formerly TransformRule2_1

    cat_replacements = [
        ("Soziales, soz. Interaktion, Companions, vermenschlichte Robots", "AF: Social Companions"),
        ("Robotik", "AF: Social Companions"),
        ("Seniorenbetreuung, Altenpflege", "AF: Social Companions"),

        ("Social Media (Facebook, Youtube & Co.), Suchmaschinen, Plattfor", "AF: Soziale Medien"),
        ("Politische Informationen und Nachrichten in Sozialen Medien/SM+", "AF: Soziale Medien"),

        ("mehrere Anwendungsfelder", "AF: mehrere Anwendungsfelder"),
        ("KI, Rob, Alg oder Autom allgem/unabhängig von AF/Meta/", "AF: KI, Rob, Alg oder Autom allgem/unabhängig von AF/Meta/"),
        ("Ausbildung, Bildung zu und für KI, Algo, Bots, Autom", "AF: Ausbildung, Bildung zu und für KI, Algo, Bots, Autom"),
        ("Agrar-/Landwirtschaft (zB Smart Farming, Autom. in LW), Lebensm", "AF: Agrar-/Landwirtschaft (zB Smart Farming, Autom. in LW), Lebensm"),
        ("Industrie, Fertigung, Industrie 4.0 (z.b. Automatisierung von F", "AF: Industrie, Fertigung, Industrie 4.0 (z.b. Automatisierung von F"),
        ("F&E: Industrie, Fertigung, Maschinen / gener. Forsch an KI, Rob", "AF: F&E: Industrie, Fertigung, Maschinen / gener. Forsch an KI, Rob"),
        ("Medizinische Forschung (zb Automatis. der Qualitätskontrolle)", "AF: Medizinische Forschung (zb Automatis. der Qualitätskontrolle)"),
        ("Medizin, Gesundheit (Anwendungsbezogen)", "AF: Medizin, Gesundheit (Anwendungsbezogen)"),
        ("Werbung/Marketing/PR, CRM, SEO", "AF: Werbung/Marketing/PR, CRM, SEO"),
        ("Verkehr/Logistik, Mobilität (autonomes Fahren)", "AF: Verkehr/Logistik, Mobilität (autonomes Fahren)"),
        ("Luftfahrt, Raumfaht", "AF: Luftfahrt, Raumfaht"),
        ("Smart home, smart living, consumer electronics", "AF: Smart home, smart living, consumer electronics"),
        ("Medien, Telekommunikation", "AF: Medien, Telekommunikation"),
        ("Druck/Reprotechnik", "AF: Druck/Reprotechnik"),
        ("Energie- und Bauwirtschaft", "AF: Energie- und Bauwirtschaft"),
        ("Sport/Wettbewerbe (z.B. Roboter-Cup)", "AF: Sport/Wettbewerbe (z.B. Roboter-Cup)"),
        ("Computer-/Videospiele", "AF: Computer-/Videospiele"),
        ("Kreativleistung (KI schreibt, komponiert) und E-Kunst", "AF: Kreativleistung (KI schreibt, komponiert) und E-Kunst"),
        ("Öffentl. Sicherheit (Polizei, Geheimdienst, Predictiv Policing)", "AF: Öffentl. Sicherheit (Polizei, Geheimdienst, Predictiv Policing)"),
        ("Militär und Krieg", "AF: Militär und Krieg"),
        ("Post / Zustelldienste", "AF: Post / Zustelldienste"),
        ("Rettungswesen, Bergungen", "AF: Rettungswesen, Bergungen"),
        ("Gastgewerbe, Handel, Tourismus", "AF: Gastgewerbe, Handel, Tourismus"),
        ("Mess-/Analyse-/Labortechnik", "AF: Mess-/Analyse-/Labortechnik"),
        ("Bilderkennung, Spracherkennung, Sentiment Analyse, Machine Lear", "AF: Bilderkennung, Spracherkennung, Sentiment Analyse, Machine Lear"),
        ("diverse IT-Anwendungen (Kryptogr., Netzwerkanal., etc)", "AF: diverse IT-Anwendungen (Kryptogr., Netzwerkanal., etc)"),
        ("Reinigungsbranche", "AF: Reinigungsbranche"),
        ("Banken, Börsen-, Versicherungen, Finanzdienste", "AF: Banken, Börsen-, Versicherungen, Finanzdienste"),
        ("Recht & Justiz", "AF: Recht & Justiz"),
        ("Automatisierung/KI in anderen Feldern: MEMO!", "AF: Automatisierung/KI in anderen Feldern: MEMO!"),
        ("Personalwesen (Personalauswahl/-recruting, HR, AMS)", "AF: Personalwesen (Personalauswahl/-recruting, HR, AMS)"),
    ]


class TransformRule3(TransformRule):
    """Tonalitäten"""

    cat_replacements = [
        ("negativ", "T: negativ"),
        ("überwiegend negativ", "T: negativ"),
        ("ambivalent", "T: ambivalent"),
        ("überwiegend positiv ", "T: positiv"),
        ("positiv", "T: positiv"),
        ("keine Tonalität ggü. KI, Algorithmen, Automatisierung", "T: keine Tonalität ggü. KI, Algorithmen, Automatisierung"),
    ]


class TransformRule4(TransformRule):
    """Genres"""

    cat_replacements = [
        ("1 Nachricht, Bericht, Meldung", "G: 1 Nachricht, Bericht, Meldung"),
        ("2 Kurzmeldung", "G: 2 Kurzmeldung"),
        ("3 Meldungsblock", "G: 3 Meldungsblock"),
        ("4 Hintergrundberichterstattung/Doku/Analyse/Reportage", "G: 4 Hintergrundberichterstattung/Doku/Analyse/Reportage"),
        ("5 Interview", "G: 5 Interview"),
        ("6 Meinungsbeitrag Journalist_Medium", "G: 6 Meinungsbeitrag Journalist_Medium"),
        ("7 Meinungsbeitrag andere (Gastautoren etc)", "G: 7 Meinungsbeitrag andere (Gastautoren etc)"),
        ("8 Leserbrief", "G: 8 Leserbrief"),
        ("9 Programm-/Veranstaltungshinweise", "G: 9 Programm-/Veranstaltungshinweise"),
        ("10 Sonstige", "G: 10 Sonstige"),
        ("11 dienstleistender Sachtext (auch informierend Sachtext)", "G: 11 dienstleistender Sachtext (auch informierend Sachtext)"),
        ("12 Filmkritiken", "G: 12 Filmkritiken"),
    ]


class TransformRule5(TransformRule):
    """Thematisierungsintensität"""

    cat_replacements = [
        ("Hauptthema", "TI: Hauptthema"),
        ("Nebenthema", "TI: Nebenthema"),
        ("Verweis", "TI: Verweis"),
    ]


class TransformRule6(TransformRule):
    """Alle Anwendungsfelder"""

    cat_replacements = [
        ("mehrere Anwendungsfelder", "AF: mehrere Anwendungsfelder"),
        ("KI, Rob, Alg oder Autom allgem/unabhängig von AF/Meta/", "AF: KI, Rob, Alg oder Autom allgem/unabhängig von AF/Meta/"),
        ("Ausbildung, Bildung zu und für KI, Algo, Bots, Autom", "AF: Ausbildung, Bildung zu und für KI, Algo, Bots, Autom"),
        ("Agrar-/Landwirtschaft (zB Smart Farming, Autom. in LW), Lebensm", "AF: Agrar-/Landwirtschaft (zB Smart Farming, Autom. in LW), Lebensm"),
        ("Industrie, Fertigung, Industrie 4.0 (z.b. Automatisierung von F", "AF: Industrie, Fertigung, Industrie 4.0 (z.b. Automatisierung von F"),
        ("F&E: Industrie, Fertigung, Maschinen / gener. Forsch an KI, Rob", "AF: F&E: Industrie, Fertigung, Maschinen / gener. Forsch an KI, Rob"),
        ("Medizinische Forschung (zb Automatis. der Qualitätskontrolle)", "AF: Medizinische Forschung (zb Automatis. der Qualitätskontrolle)"),
        ("Medizin, Gesundheit (Anwendungsbezogen)", "AF: Medizin, Gesundheit (Anwendungsbezogen)"),
        ("Seniorenbetreuung, Altenpflege", "AF: Seniorenbetreuung, Altenpflege"),
        ("Social Media (Facebook, Youtube & Co.), Suchmaschinen, Plattfor", "AF: Social Media (Facebook, Youtube & Co.), Suchmaschinen, Plattfor"),
        ("Werbung/Marketing/PR, CRM, SEO", "AF: Werbung/Marketing/PR, CRM, SEO"),
        ("Verkehr/Logistik, Mobilität (autonomes Fahren)", "AF: Verkehr/Logistik, Mobilität (autonomes Fahren)"),
        ("Luftfahrt, Raumfaht", "AF: Luftfahrt, Raumfaht"),
        ("Smart home, smart living, consumer electronics", "AF: Smart home, smart living, consumer electronics"),
        ("Politische Informationen und Nachrichten in Sozialen Medien/SM+", "AF: Politische Informationen und Nachrichten in Sozialen Medien/SM+"),
        ("Medien, Telekommunikation", "AF: Medien, Telekommunikation"),
        ("Druck/Reprotechnik", "AF: Druck/Reprotechnik"),
        ("Soziales, soz. Interaktion, Companions, vermenschlichte Robots", "AF: Soziales, soz. Interaktion, Companions, vermenschlichte Robots"),
        ("Energie- und Bauwirtschaft", "AF: Energie- und Bauwirtschaft"),
        ("Sport/Wettbewerbe (z.B. Roboter-Cup)", "AF: Sport/Wettbewerbe (z.B. Roboter-Cup)"),
        ("Computer-/Videospiele", "AF: Computer-/Videospiele"),
        ("Kreativleistung (KI schreibt, komponiert) und E-Kunst", "AF: Kreativleistung (KI schreibt, komponiert) und E-Kunst"),
        ("Öffentl. Sicherheit (Polizei, Geheimdienst, Predictiv Policing)", "AF: Öffentl. Sicherheit (Polizei, Geheimdienst, Predictiv Policing)"),
        ("Militär und Krieg", "AF: Militär und Krieg"),
        ("Post / Zustelldienste", "AF: Post / Zustelldienste"),
        ("Rettungswesen, Bergungen", "AF: Rettungswesen, Bergungen"),
        ("Gastgewerbe, Handel, Tourismus", "AF: Gastgewerbe, Handel, Tourismus"),
        ("Mess-/Analyse-/Labortechnik", "AF: Mess-/Analyse-/Labortechnik"),
        ("Bilderkennung, Spracherkennung, Sentiment Analyse, Machine Lear", "AF: Bilderkennung, Spracherkennung, Sentiment Analyse, Machine Lear"),
        ("diverse IT-Anwendungen (Kryptogr., Netzwerkanal., etc)", "AF: diverse IT-Anwendungen (Kryptogr., Netzwerkanal., etc)"),
        ("Reinigungsbranche", "AF: Reinigungsbranche"),
        ("Banken, Börsen-, Versicherungen, Finanzdienste", "AF: Banken, Börsen-, Versicherungen, Finanzdienste"),
        ("Recht & Justiz", "AF: Recht & Justiz"),
        ("Automatisierung/KI in anderen Feldern: MEMO!", "AF: Automatisierung/KI in anderen Feldern: MEMO!"),
        ("Personalwesen (Personalauswahl/-recruting, HR, AMS)", "AF: Personalwesen (Personalauswahl/-recruting, HR, AMS)"),
    ]


class TransformRule7(TransformRule):
    """Verantwortungen"""

    cat_replacements = [
        ("ZP_Politik_1", "Verantwortungsreferenz"),
        ("ZP_Wirtschaft_1", "Verantwortungsreferenz"),
        ("ZP_Rechtsorgane_1", "Verantwortungsreferenz"),
        ("ZP_Wissenschaft/Bildung_1", "Verantwortungsreferenz"),
        ("ZP_Gesellschaft/Öffentlichkeit_1", "Verantwortungsreferenz"),
        ("ZP_Individuum/en_1", "Verantwortungsreferenz"),
        ("ZP_Medien/Presse_1", "Verantwortungsreferenz"),
        ("ZP_Kultur_1", "Verantwortungsreferenz"),
        ("VS_Politik_1", "Verantwortungsreferenz"),
        ("VS_Wirtschaft_1", "Verantwortungsreferenz"),
        ("VS_Rechtsorgane_1", "Verantwortungsreferenz"),
        ("VS_Wissenschaft/Bildung_1", "Verantwortungsreferenz"),
        ("VS_Gesellschaft/Öffentlichkeit_1", "Verantwortungsreferenz"),
        ("VS_Individuum/en_1", "Verantwortungsreferenz"),
        ("VS_Medien/Presse_1", "Verantwortungsreferenz"),
        ("VS_Kultur_1", "Verantwortungsreferenz"),
        ("Fremdzuschreibung_1", "Verantwortungsreferenz"),
        ("Selbstzuschreibung_1", "Verantwortungsreferenz"),
        ("Leugnung/Ablehnung_Fremdzuschreibung_1", "Verantwortungsreferenz"),
        ("Leugnung/Ablehnung_Selbstzuschreibung_1", "Verantwortungsreferenz"),
        ("Prospektive Verantwortung_1", "Verantwortungsreferenz"),
        ("Retrospektive Verantwortung_1", "Verantwortungsreferenz"),
        ("ZP_Politik_2", "Verantwortungsreferenz"),
        ("ZP_Wirtschaft_2", "Verantwortungsreferenz"),
        ("ZP_Rechtsorgane_2", "Verantwortungsreferenz"),
        ("ZP_Wissenschaft/Bildung_2", "Verantwortungsreferenz"),
        ("ZP_Gesellschaft/Öffentlichkeit_2", "Verantwortungsreferenz"),
        ("ZP_Individuum/en_2", "Verantwortungsreferenz"),
        ("ZP_Medien/Presse_2", "Verantwortungsreferenz"),
        ("VS_Politik_2", "Verantwortungsreferenz"),
        ("VS_Wirtschaft_2", "Verantwortungsreferenz"),
        ("VS_Rechtsorgane_2", "Verantwortungsreferenz"),
        ("VS_Wissenschaft/Bildung_2", "Verantwortungsreferenz"),
        ("VS_Gesellschaft/Öffentlichkeit_2", "Verantwortungsreferenz"),
        ("VS_Individuum/en_2", "Verantwortungsreferenz"),
        ("VS_Medien/Presse_2", "Verantwortungsreferenz"),
        ("Fremdzuschreibung_2", "Verantwortungsreferenz"),
        ("Selbstzuschreibung_2", "Verantwortungsreferenz"),
        ("Leugnung/Ablehnung_Fremdzuschreibung_2", "Verantwortungsreferenz"),
        ("Leugnung/Ablehnung_Selbstzuschreibung_2", "Verantwortungsreferenz"),
        ("Retrospektive Verantwortung_2", "Verantwortungsreferenz"),
        ("Prospektive Verantwortung_2", "Verantwortungsreferenz"),
        ("ZP_Politik_3", "Verantwortungsreferenz"),
        ("ZP_Wirtschaft_3", "Verantwortungsreferenz"),
        ("ZP_Rechtsorgane_3", "Verantwortungsreferenz"),
        ("ZP_Wissenschaft/Bildung_3", "Verantwortungsreferenz"),
        ("ZP_Gesellschaft/Öffentlichkeit_3", "Verantwortungsreferenz"),
        ("ZP_Individuum/en_3", "Verantwortungsreferenz"),
        ("ZP_Medien/Presse_3", "Verantwortungsreferenz"),
        ("VS_Politik_3", "Verantwortungsreferenz"),
        ("VS_Wirtschaft_3", "Verantwortungsreferenz"),
        ("VS_Rechtsorgane_3", "Verantwortungsreferenz"),
        ("VS_Wissenschaft/Bildung_3", "Verantwortungsreferenz"),
        ("VS_Gesellschaft/Öffentlichkeit_3", "Verantwortungsreferenz"),
        ("VS_Individuum/en_3", "Verantwortungsreferenz"),
        ("VS_Medien/Presse_3", "Verantwortungsreferenz"),
        ("Fremdzuschreibung_3", "Verantwortungsreferenz"),
        ("Selbstzuschreibung_3", "Verantwortungsreferenz"),
        ("Leugnung/Ablehnung _Fremdzuschreibung_3", "Verantwortungsreferenz"),
        ("Leugnung/Ablehnung_Selbstzuschreibung_3", "Verantwortungsreferenz"),
        ("Prospektive Verantwortung_3", "Verantwortungsreferenz"),
        ("Retrospektive Verantwortung_3", "Verantwortungsreferenz"),
        ("ZP_Politik_4", "Verantwortungsreferenz"),
        ("ZP_Wirtschaft_4", "Verantwortungsreferenz"),
        ("ZP_Rechtsorgane_4", "Verantwortungsreferenz"),
        ("ZP_Wissenschaft/Bildung_4", "Verantwortungsreferenz"),
        ("ZP_Gesellschaft/Öffentlichkeit_4", "Verantwortungsreferenz"),
        ("ZP_Individuum/en_4", "Verantwortungsreferenz"),
        ("ZP_Presse/Medien_4", "Verantwortungsreferenz"),
        ("VS_Politik_4", "Verantwortungsreferenz"),
        ("VS_Wirtschaft_4", "Verantwortungsreferenz"),
        ("VS_Rechtsorgane_4", "Verantwortungsreferenz"),
        ("VS_Wissenschaft/Bildung_4", "Verantwortungsreferenz"),
        ("VS_Gesellschaft/Öffentlichkeit_4", "Verantwortungsreferenz"),
        ("VS_Individuum/en_4", "Verantwortungsreferenz"),
        ("VS_Presse/Medien_4", "Verantwortungsreferenz"),
        ("Fremdzuschreibung_4", "Verantwortungsreferenz"),
        ("Selbstzuschreibung_4", "Verantwortungsreferenz"),
        ("Leugnung/Ablehnung_Fremdzuschreibung_4", "Verantwortungsreferenz"),
        ("Leugnung/Ablehnung_Selbstzuschreibung_4", "Verantwortungsreferenz"),
        ("Prospektive Verantwortung_4", "Verantwortungsreferenz"),
        ("Retrospektive Verantwortung_4", "Verantwortungsreferenz"),
        ("ZP_Politik_5", "Verantwortungsreferenz"),
        ("ZP_Wirtschaft_5", "Verantwortungsreferenz"),
        ("ZP_Rechtsorgane_5", "Verantwortungsreferenz"),
        ("ZP_Wissenschaft/Bildung_5", "Verantwortungsreferenz"),
        ("ZP_Gesellschaft/Öffentlichkeit_5", "Verantwortungsreferenz"),
        ("ZP_Individuum/en_5", "Verantwortungsreferenz"),
        ("ZP_Presse/Medien_5", "Verantwortungsreferenz"),
        ("VS_Politik_5", "Verantwortungsreferenz"),
        ("VS_Wirtschaft_5", "Verantwortungsreferenz"),
        ("VS_Rechtsorgane_5", "Verantwortungsreferenz"),
        ("VS_Wissenschaft/Bildung_5", "Verantwortungsreferenz"),
        ("VS_Gesellschaft/Öffentlichkeit_5", "Verantwortungsreferenz"),
        ("VS_Individuum/en_5", "Verantwortungsreferenz"),
        ("VS_Presse/Medien_5", "Verantwortungsreferenz"),
        ("Fremdzuschreibung_5", "Verantwortungsreferenz"),
        ("Selbstzuschreibung_5", "Verantwortungsreferenz"),
        ("Leugnung/Ablehnung_Fremdzuschreibung_5", "Verantwortungsreferenz"),
        ("Leugnung/Ablehnung_Selbstzuschreibung_5", "Verantwortungsreferenz"),
        ("Prospektive Verantwortung_5", "Verantwortungsreferenz"),
        ("Retrospektive Verantwortung_5", "Verantwortungsreferenz"),
        ("ZP_Politik_6", "Verantwortungsreferenz"),
        ("ZP_Wirtschaft_6", "Verantwortungsreferenz"),
        ("ZP_Rechtsorgane_6", "Verantwortungsreferenz"),
        ("ZP_Wissenschaft/Bildung_6", "Verantwortungsreferenz"),
        ("ZP_Gesellschaft/Öffentlichkeit_6", "Verantwortungsreferenz"),
        ("ZP_Individuum/en_6", "Verantwortungsreferenz"),
        ("ZP_Presse/Medien_6", "Verantwortungsreferenz"),
        ("VS_Politik_6", "Verantwortungsreferenz"),
        ("VS_Wirtschaft_6", "Verantwortungsreferenz"),
        ("VS_Rechtsorgane_6", "Verantwortungsreferenz"),
        ("VS_Wissenschaft/Bildung_6", "Verantwortungsreferenz"),
        ("VS_Gesellschaft/Öffentlichkeit_6", "Verantwortungsreferenz"),
        ("VS_Individuum/en_6", "Verantwortungsreferenz"),
        ("VS_Presse/Medien_6", "Verantwortungsreferenz"),
        ("Fremdzuschreibung_6", "Verantwortungsreferenz"),
        ("Selbstzuschreibung_6", "Verantwortungsreferenz"),
        ("Leugnung/Ablehnung_Fremdzuschreibung_6", "Verantwortungsreferenz"),
        ("Leugnung/Ablehnung_Selbstzuschreibung_6", "Verantwortungsreferenz"),
        ("Prospektive Verantwortung 6", "Verantwortungsreferenz"),
        ("Retrospektive Verantwortung 6", "Verantwortungsreferenz"),
        ("ZP_Wissenschaft/Bildung_7", "Verantwortungsreferenz"),
        ("VS_Gesellschaft/Öffentlichkeit_7", "Verantwortungsreferenz"),
        ("Fremdzuschreibung_7", "Verantwortungsreferenz"),
        ("Retrospektive Verantwortung_7", "Verantwortungsreferenz"),
    ]

class TransformRule8(TransformRule):
    # formerly: TransformRule8__s1_tr2_1__s3__s4__s5__s6

    # These replacements seem redundant but they are used to remove all other cats that do not match
    cat_replacements = [
        ("AF: Social Companions", "AF: Social Companions"),
        ("AF: Soziale Medien", "AF: Soziale Medien"),
    ]

class TransformRule9(TransformRule):
    # formerly: TransformRule9__s2

    cat_replacements = [
        ("Social Companions", "AF: Social Companions"),
        ("Soziale Medien", "AF: Soziale Medien"),
    ]

class TransformRule10(TransformRule):
    # formerly: TransformRule10__s3__s4__s5__s6

    # These replacements seem redundant but they are used to remove all other cats that do not match
    cat_replacements = [
        ("TI: Hauptthema", "TI: Hauptthema"),
        ("TI: Nebenthema", "TI: Nebenthema"),
        ("TI: Verweis", "TI: Verweis")
    ]

class TransformRule11(TransformRule): 
    """Risikotypen"""

    cat_replacements = [
        ("Datenschutz, Privatsphäre, Überwachung",                          "RT: Datenschutz, Privatsphäre, Überwachung"), 
        ("Haftung/Verantwortung",                                           "RT: Haftung/Verantwortung"), 
        ("Manipulation, Verzerrung, Unwahrh, Filterblas, Polarisieru, Zen", "RT: Manipulation, Verzerrung, Unwahrh, Filterblas, Polarisieru, Zen"), 
        ("Souv-/Autonomie/Kontrollverlust,Fremdbest.,Überlegenh,Macht/Ein", "RT: Souv-/Autonomie/Kontrollverlust,Fremdbest.,Überlegenh,Macht/Ein"), 
        ("Intransparenz (Blackbox)",                                        "RT: Intransparenz (Blackbox)"), 
        ("Kommodifizierung der Nutzer (Ausbeutung)",                        "RT: Kommodifizierung der Nutzer (Ausbeutung)"), 
        ("Sozialität, Entfremdung vom Natürlichen, Lebenssinn, uncanny ",   "RT: Sozialität, Entfremdung vom Natürlichen, Lebenssinn, uncanny"), 
        ("Diskriminierung, Ungleichheit",                                   "RT: Diskriminierung, Ungleichheit"), 
        ("mangelnde Qualität der Automatisierung, Algorithmen, Ki",         "RT: mangelnde Qualität der Automatisierung, Algorithmen, Ki"), 
        ("Missbrauch d KI, Algorith durch Staat, Unternehm,Interessengrup", "RT: Missbrauch d KI, Algorith durch Staat, Unternehm,Interessengrup"), 
        ("ethisch, moralisch, philosophische Fragen der KI, Algorithmen",   "RT: ethisch, moralisch, philosophische Fragen der KI, Algorithmen"), 
        ("Sicherheit (Safety), Unfälle, körperliche/psychische Sicherheit", "RT: Sicherheit (Safety), Unfälle, körperliche/psychische Sicherheit"), 
        ("IT-/KI-Security (Sicherheit vor Hackern etc)",                    "RT: IT-/KI-Security (Sicherheit vor Hackern etc)"), 
        ("Ungleichheit bei Sozialabgaben / Steuergerechtigkeit",            "RT: Ungleichheit bei Sozialabgaben / Steuergerechtigkeit"), 
        ("Fehlallokation von Ressourcen",                                   "RT: Wirtschaftlichkeit und Effizienz"), 
        ("Mängel bei produktiver Effizienz",                                "RT: Wirtschaftlichkeit und Effizienz"), 
        ("Investitionsrisiko",                                              "RT: Wirtschaftlichkeit und Effizienz"), 
        ("mangelnde Adaption/Literacy/Ausbildung/Bildung",                  "RT: mangelnde Adaption/Literacy/Ausbildung/Bildung"), 
        ("mangelnde Adpation v. Industrie, Wirtschaft, Volkswirtschaft",    "RT: mangelnde Adpation v. Industrie, Wirtschaft, Volkswirtschaft"), 
        ("Arbeitsplatzverluste / Zukünftige Arbeit",                        "RT: Arbeitsplatzverluste / Zukünftige Arbeit"), 
        ("Marktmacht, Monopolisierung",                                     "RT: Marktmacht, Monopolisierung")
    ]

class TransformRule12(TransformRule): 
    """Verantwortungsreferenzen für g8"""

    cat_replacements = [
        ("VR: enthalten", "Verantwortungsreferenz"), 
    ]
