"""
Skrypt do przygotowania pliku korpus.json na podstawie new_dataset.json.
Przepisuje dane, zmienia nazwy kluczy i ekstrahuje kategorie.
"""

import json
import os
from typing import List, Dict

def wczytaj_json(sciezka: str) -> List[Dict]:
    """Wczytuje dane z pliku JSON."""
    if not os.path.exists(sciezka):
        raise FileNotFoundError(f"Plik nie istnieje: {sciezka}")
        
    with open(sciezka, 'r', encoding='utf-8') as f:
        return json.load(f)

def zapisz_json(dane: List[Dict] | Dict, sciezka: str):
    """Zapisuje dane do pliku JSON."""
    with open(sciezka, 'w', encoding='utf-8') as f:
        json.dump(dane, f, ensure_ascii=False, indent=2)
    print(f"Zapisano do {sciezka}")

def przetworz_dane(input_data: List[Dict]) -> tuple[List[Dict], Dict]:
    """
    Przetwarza dane wejściowe:
    1. Przypisuje ID
    2. Zmienia nazwy kluczy (text -> tekst, category -> kategoria)
    3. Zachowuje opis_kategorii
    4. Ekstrahuje unikalne kategorie
    """
    komentarze = []
    kategorie_map = {} # nazwa -> opis

    print(f"Przetwarzanie {len(input_data)} rekordów...")

    for i, item in enumerate(input_data):
        # Pobranie danych
        tekst = item.get('text', '')
        kat_nazwa = item.get('category', 'Nieokreślona')
        kat_opis = item.get('opis_kategorii', '')
        
        # Budowanie nowego obiektu
        nowy_komentarz = {
            'id': i + 1,
            'tekst': tekst,
            'kategoria': kat_nazwa,
            'opis_kategorii': kat_opis
        }
        
        # Zachowanie innych pól jeśli są (np. sentiment), opcjonalnie
        if 'sentiment' in item:
            nowy_komentarz['sentiment'] = item['sentiment']

        komentarze.append(nowy_komentarz)
        
        # Zbieranie definicji kategorii
        if kat_nazwa not in kategorie_map and kat_nazwa:
             kategorie_map[kat_nazwa] = kat_opis

    # Formatowanie listy kategorii do zapisu
    lista_kategorii = []
    for nazwa, opis in kategorie_map.items():
        lista_kategorii.append({
            "nazwa": nazwa,
            "opis": opis
        })
    
    kategorie_dict = {"kategorie": lista_kategorii}
    
    return komentarze, kategorie_dict

def main():
    plik_wejsciowy = 'new_dataset.json'
    
    # Sprawdzenie czy plik istnieje
    if not os.path.exists(plik_wejsciowy):
        print(f"Błąd: Nie znaleziono pliku {plik_wejsciowy}")
        # Spróbujmy znaleźć plik w katalogu skryptu
        plik_wejsciowy_alt = os.path.join(os.path.dirname(__file__), 'new_dataset.json')
        if os.path.exists(plik_wejsciowy_alt):
            plik_wejsciowy = plik_wejsciowy_alt
        else:
             # Spróbujmy znaleźć plik w bieżącym katalogu (jeśli uruchamiamy z root)
             plik_wejsciowy_alt2 = os.path.join('AnalizaKorpusu_SocialPure', 'new_dataset.json')
             if os.path.exists(plik_wejsciowy_alt2):
                 plik_wejsciowy = plik_wejsciowy_alt2
             else:
                 print(f"Nie znaleziono pliku również w: {plik_wejsciowy_alt} ani {plik_wejsciowy_alt2}")
                 return

    # Krok 1: Wczytanie
    print(f"=== Wczytywanie {plik_wejsciowy} ===")
    raw_data = wczytaj_json(plik_wejsciowy)
    
    # Krok 2: Przetwarzanie
    print("=== Przetwarzanie danych ===")
    komentarze, kategorie_dict = przetworz_dane(raw_data)
    
    # Krok 3: Zapis wyników
    print("=== Zapisywanie wyników ===")
    zapisz_json(komentarze, 'korpus.json')
    zapisz_json(kategorie_dict, 'kategorie.json')
    
    # Statystyki
    print("\n=== Statystyki ===")
    print(f"Łączna liczba komentarzy: {len(komentarze)}")
    print(f"Łączna liczba kategorii: {len(kategorie_dict['kategorie'])}")
    
    print("\nRozkład kategorii:")
    kategorie_count = {}
    for kom in komentarze:
        kat = kom.get('kategoria', 'brak')
        kategorie_count[kat] = kategorie_count.get(kat, 0) + 1
    
    for kat, count in sorted(kategorie_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {kat}: {count} ({count/len(komentarze)*100:.1f}%)")

if __name__ == "__main__":
    main()
