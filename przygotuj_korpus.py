"""
Skrypt do parsowania Korpus.docx i przygotowania kategorii z użyciem Gemini.
Tworzy plik korpus.json z komentarzami i przypisanymi kategoriami.
"""

import os
import json
import asyncio
from docx import Document
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List, Dict

# wczytanie zmiennych środowiskowych
load_dotenv()

# konfiguracja Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY nie znaleziony w .env")

genai.configure(api_key=GOOGLE_API_KEY)
model_kategorie = genai.GenerativeModel('gemini-2.5-flash')
model_przypisanie = genai.GenerativeModel('gemini-2.5-flash')


def wczytaj_dane_z_docx(sciezka: str) -> List[Dict]:
    """
    Wczytuje dane z tabeli w pliku DOCX.
    Każda komórka tabeli traktowana jest jako osobny komentarz.
    """
    doc = Document(sciezka)
    komentarze = []
    
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                tekst = cell.text.strip()
                if tekst:  
                    komentarze.append({
                        'id': len(komentarze) + 1,
                        'tekst': tekst
                    })
    
    print(f"Wczytano {len(komentarze)} komentarzy z {sciezka}")
    return komentarze


def zapisz_json(dane: List[Dict], sciezka: str):
    """Zapisuje dane do pliku JSON."""
    with open(sciezka, 'w', encoding='utf-8') as f:
        json.dump(dane, f, ensure_ascii=False, indent=2)
    print(f"Zapisano {len(dane)} rekordów do {sciezka}")


def wczytaj_json(sciezka: str) -> List[Dict]:
    """Wczytuje dane z pliku JSON."""
    with open(sciezka, 'r', encoding='utf-8') as f:
        return json.load(f)


def utworz_kategorie(komentarze: List[Dict]) -> Dict:
    """
    Wysyła wszystkie komentarze do Gemini i prosi o utworzenie kategorii.
    Zwraca słownik z listą kategorii i ich opisami.
    """
    print("\n=== Tworzenie kategorii ===")
    
    # przygotowanie tekstów do analizy
    teksty_do_analizy = "\n".join([
        f"{i+1}. {kom['tekst'][:300]}"  # ograniczenie długości dla każdego komentarza
        for i, kom in enumerate(komentarze)
    ])
    
    prompt = f"""Przeanalizuj poniższe komentarze z forum/dyskusji i zaproponuj listę szczegółowych, konkretnych kategorii tematycznych.

Komentarze:
{teksty_do_analizy}

WAŻNE: Zaproponuj 8-15 bardzo szczegółowych i konkretnych kategorii. Unikaj ogólnych kategorii typu "dyskurs społeczny" czy "osobiste refleksje". 
Zamiast tego tworz kategorie takie jak:
- "Krytyka polityków i partii" (zamiast ogólnej "Polityka")
- "Komentarze o talent show i uczestnikach" (zamiast ogólnej "Media")
- "Wypowiedzi w gwarze śląskiej" (zamiast ogólnej "Kultura regionalna")
- "Oskarżenia o oszustwa w grach online" (zamiast ogólnej "Gaming")

KLUCZOWE: Kategorie muszą być maksymalnie rozłączne - każdy komentarz powinien pasować tylko do jednej kategorii jednoznacznie. 
Unikaj nakładających się kategorii. Jeśli komentarz mógłby pasować do kilku kategorii, to znaczy że kategorie są zbyt ogólne lub źle zdefiniowane.

Dla każdej kategorii podaj:
1. Konkretną, szczegółową nazwę (2-5 słów, bardzo precyzyjną)
2. Krótki opis (1-2 zdania) wyjaśniający dokładnie jakie komentarze do niej należą, tak żeby było jasne że nie pasują do innych kategorii

Zwróć odpowiedź w formacie JSON:
{{
  "kategorie": [
    {{
      "nazwa": "konkretna szczegółowa nazwa kategorii",
      "opis": "dokładny opis jakie komentarze należą do tej kategorii"
    }}
  ]
}}
"""
    
    try:
        response = model_kategorie.generate_content(prompt)
        
        if response and response.text:
            # próba wyciągnięcia JSON z odpowiedzi
            tekst_odpowiedzi = response.text.strip()
            
            # jeśli odpowiedź zawiera markdown code block, wyciągnij JSON
            if "```json" in tekst_odpowiedzi:
                start = tekst_odpowiedzi.find("```json") + 7
                end = tekst_odpowiedzi.find("```", start)
                tekst_odpowiedzi = tekst_odpowiedzi[start:end].strip()
            elif "```" in tekst_odpowiedzi:
                start = tekst_odpowiedzi.find("```") + 3
                end = tekst_odpowiedzi.find("```", start)
                tekst_odpowiedzi = tekst_odpowiedzi[start:end].strip()
            
            kategorie_dict = json.loads(tekst_odpowiedzi)
            print(f"Utworzono {len(kategorie_dict['kategorie'])} kategorii:")
            for kat in kategorie_dict['kategorie']:
                print(f"  - {kat['nazwa']}: {kat['opis']}")
            
            return kategorie_dict
        else:
            raise ValueError("Brak odpowiedzi z Gemini")
            
    except Exception as e:
        print(f"Błąd przy tworzeniu kategorii: {e}")
        print("Używam domyślnych kategorii...")
        return {
            "kategorie": [
                {"nazwa": "nieokreślona", "opis": "Kategoria domyślna"}
            ]
        }


async def przypisz_kategorie_async(komentarz: Dict, lista_kategorii: List[Dict]) -> str:
    """
    Asynchronicznie przypisuje kategorię do pojedynczego komentarza.
    """
    nazwy_kategorii = [kat['nazwa'] for kat in lista_kategorii]
    lista_kategorii_tekst = "\n".join([
        f"- {kat['nazwa']}: {kat['opis']}"
        for kat in lista_kategorii
    ])
    
    prompt = f"""Przypisz jeden z poniższych kategorii do następującego komentarza:

Komentarz:
{komentarz['tekst']}

Dostępne kategorie:
{lista_kategorii_tekst}

Zwróć TYLKO nazwę kategorii (bez dodatkowych wyjaśnień, bez cudzysłowów, bez numeracji).
Jeśli komentarz nie pasuje do żadnej kategorii, wybierz najbardziej pasującą.
"""
    
    try:
        response = await asyncio.to_thread(
            model_przypisanie.generate_content,
            prompt
        )
        
        if response and response.text:
            kategoria = response.text.strip()
            # usuwanie ewentualncyh cudzysłowi i numeracji
            kategoria = kategoria.strip('"\'')
            kategoria = kategoria.split('.')[-1].strip()  
            kategoria = kategoria.split(':')[-1].strip()  # usuń "Kategoria:"
            
            # weryfikacja czy kategoria jest na liście
            if kategoria not in nazwy_kategorii:
                # szukaj podobnej (case-insensitive)
                kategoria_lower = kategoria.lower()
                for nazwa in nazwy_kategorii:
                    if nazwa.lower() == kategoria_lower:
                        return nazwa
                # Jeśli nie znaleziono, zwróć pierwszą kategorię jako fallback
                print(f"  Ostrzeżenie: '{kategoria}' nie jest na liście, przypisuję '{nazwy_kategorii[0]}'")
                return nazwy_kategorii[0]
            
            return kategoria
        else:
            return lista_kategorii[0]['nazwa']  # fallback
            
    except Exception as e:
        print(f"  Błąd przy przypisywaniu kategorii dla komentarza {komentarz['id']}: {e}")
        return lista_kategorii[0]['nazwa']  # fallback


async def przypisz_kategorie_batch(komentarze: List[Dict], lista_kategorii: List[Dict], batch_size: int = 15):
    """
    Przypisuje kategorie do komentarzy asynchronicznie w batchach.
    """
    print(f"\n=== Przypisywanie kategorii do {len(komentarze)} komentarzy ===")
    print(f"Batch size: {batch_size}")
    
    for i in range(0, len(komentarze), batch_size):
        batch = komentarze[i:i+batch_size]
        
        # wykonaj wszystkie zadania w batchu równolegle
        tasks = [
            przypisz_kategorie_async(kom, lista_kategorii)
            for kom in batch
        ]
        
        kategorie = await asyncio.gather(*tasks)
        
        # przypisz kategorie do komentarzy (z opisem)
        for kom, kat_nazwa in zip(batch, kategorie):
            kom['kategoria'] = kat_nazwa
            # znajdź opis kategorii i dodaj go do komentarza
            kat_dict = next((k for k in lista_kategorii if k['nazwa'] == kat_nazwa), None)
            if kat_dict:
                kom['opis_kategorii'] = kat_dict['opis']
            else:
                kom['opis_kategorii'] = ""
        
        print(f"Przetworzono {min(i+batch_size, len(komentarze))}/{len(komentarze)} komentarzy")
    
    print("Zakończono przypisywanie kategorii")


async def main():
    """Główna funkcja wykonująca cały proces."""
    
    # Krok 1: Parsowanie DOCX
    print("=== Krok 1: Parsowanie Korpus.docx ===")
    komentarze = wczytaj_dane_z_docx('Korpus.docx')
    zapisz_json(komentarze, 'korpus.json')
    
    # Krok 2: Utworzenie kategorii
    print("\n=== Krok 2: Tworzenie kategorii przez Gemini ===")
    kategorie_dict = utworz_kategorie(komentarze)
    zapisz_json(kategorie_dict, 'kategorie.json')
    
    # Krok 3: Przypisanie kategorii do komentarzy
    print("\n=== Krok 3: Przypisywanie kategorii do komentarzy ===")
    await przypisz_kategorie_batch(komentarze, kategorie_dict['kategorie'], batch_size=15)
    
    # Krok 4: Zapisanie wyników
    print("\n=== Krok 4: Zapisanie wyników ===")
    zapisz_json(komentarze, 'korpus.json')
    
    # Statystyki
    print("\n=== Statystyki ===")
    print(f"Łączna liczba komentarzy: {len(komentarze)}")
    print("\nRozkład kategorii:")
    kategorie_count = {}
    for kom in komentarze:
        kat = kom.get('kategoria', 'brak')
        kategorie_count[kat] = kategorie_count.get(kat, 0) + 1
    
    for kat, count in sorted(kategorie_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {kat}: {count} ({count/len(komentarze)*100:.1f}%)")
    
    print("  - korpus.json (komentarze z kategoriami)")
    print("  - kategorie.json (lista kategorii z opisami)")


if __name__ == "__main__":
    asyncio.run(main())

