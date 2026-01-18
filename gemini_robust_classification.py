# Robust Gemini Classification Script

import asyncio
import time
import random
from sklearn.metrics import accuracy_score

# Assuming `model_gemini` and `X_test_gemini`, `y_test_gemini`, `kategorie_lista`, `kategorie_z_opisami` are already defined in the notebook context.
# This script is intended to be copied into a cell in the notebook.

async def klasyfikuj_gemini_robust(tekst: str, lista_kategorii: list, kategorie_z_opisami: dict, max_retries=5) -> str:
    """
    Klasyfikuje tekst używając Gemini z obsługą błędów 429 (Resource Exhausted) i ponawianiem prób.
    """
    lista_kategorii_tekst = "\n".join([
        f"- {kat}: {kategorie_z_opisami.get(kat, 'Brak opisu')}" 
        for kat in lista_kategorii
    ])
    
    prompt = f"""Jesteś ekspertem w dziedzinie analizy komentarzy. Przypisz jeden z poniższych kategorii do następującego komentarza:

Komentarz:
{tekst}

Dostępne kategorie (z opisami):
{lista_kategorii_tekst}

Zwróć TYLKO nazwę kategorii (bez dodatkowych wyjaśnień, bez cudzysłowów, bez numeracji).
Jeśli komentarz nie pasuje do żadnej kategorii, wybierz najbardziej pasującą na podstawie opisów kategorii.
"""
    
    for attempt in range(max_retries):
        try:
            # Opóźnienie losowe przed każdym strzałem, aby nie uderzać idealnie równo
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            response = await asyncio.to_thread(
                model_gemini.generate_content,
                prompt
            )
            
            if response and response.text:
                kategoria = response.text.strip()
                # czyszczenie
                kategoria = kategoria.strip('"\'')
                kategoria = kategoria.split('.')[-1].strip()
                kategoria = kategoria.split(':')[-1].strip()
                
                # weryfikacja
                if kategoria not in lista_kategorii:
                    # szukaj case-insensitive
                    for nazwa in lista_kategorii:
                        if nazwa.lower() == kategoria.lower():
                            return nazwa
                    # jeśli nic nie pasuje - fallback
                    return lista_kategorii[0] 
                
                return kategoria
                
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "ResourceExhausted" in error_str:
                # Exponential backoff: 2s, 4s, 8s, 16s...
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"  ⚠️ Limit API (429) dla '{tekst[:20]}...'. Próba {attempt+1}/{max_retries}. Czekam {sleep_time:.2f}s...")
                await asyncio.sleep(sleep_time)
            else:
                print(f"  ❌ Błąd inny niż limit: {e}")
                break # Inne błędy przerywają
                
    return "BŁĄD_API" # Specjalna flaga błędu

print("Klasyfikacja tekstów testowych przez Gemini 2.5-flash-lite (Robust Mode)...")
print("Dodano opóźnienia i ponawianie prób dla błędów 429.")

y_pred_gemini_raw = []

# CRITICAL CHANGE: Smoke Test Mode
# Running on only first 10 items to verify accuracy without hitting limits.
limit_items = 10
X_test_subset = X_test_gemini[:limit_items]
y_test_subset  = y_test_gemini[:limit_items] 

start_time = time.time()

# Main execution block
async def main_classification():
    global y_pred_gemini_raw
    print(f"Rozpoczynam TESTOWĄ klasyfikację (pierwsze {limit_items} sztuk). Pauza: 10s")
    
    total_items = len(X_test_subset)
    
    for i, tekst in enumerate(X_test_subset):
        # Klasyfikacja pojedynczego tekstu
        kategoria = await klasyfikuj_gemini_robust(tekst, kategorie_lista, kategorie_z_opisami)
        y_pred_gemini_raw.append(kategoria)
        
        # Progress log
        print(f"Przetworzono {i+1}/{total_items}. Wynik: {kategoria}. Pauza 10s...")
        
        # Bardzo długa pauza dla bezpieczeństwa
        await asyncio.sleep(10)

# Reszta kodu obsługująca obliczanie accuracy powinna działać, bo zip() przytnie do długości predykcji.

# In Jupyter, you would run: await main_classification()
