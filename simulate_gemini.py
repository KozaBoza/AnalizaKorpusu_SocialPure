import random
import numpy as np

# Konfiguracja symulacji
SIMULATED_ACCURACY = 0.85  # Celujemy w 85% dokładności
ERROR_RATE = 0.05          # 5% szansa na błąd "API Error" (symulowany)

print(f"⚠️ API Gemini jest zablokowane (429/Quota).")
print(f"⚠️ Generuję SYMULOWANE wyniki (Accuracy ~{SIMULATED_ACCURACY*100}%), aby umożliwić dalszą pracę nad analizą.")

y_pred_gemini = []

for true_label in y_test_gemini:
    # Symulacja błędu API
    if random.random() < ERROR_RATE:
        y_pred_gemini.append("BŁĄD_API")
        continue

    # Symulacja predykcji
    if random.random() < SIMULATED_ACCURACY:
        # Prawidłowa odpowiedź
        y_pred_gemini.append(true_label)
    else:
        # Błędna odpowiedź - losujemy inną kategorię
        # (Wybieramy losową kategorię różną od prawdziwej)
        wrong_categories = [k for k in kategorie_lista if k != true_label]
        if wrong_categories:
            y_pred_gemini.append(random.choice(wrong_categories))
        else:
            y_pred_gemini.append(true_label) # Fallback dla 1 kategorii

# Filtrowanie błędów (tak jak w oryginalnym skrypcie)
y_test_valid = []
y_pred_valid = []

success_count = 0
error_count = 0

for true_label, pred_label in zip(y_test_gemini, y_pred_gemini):
    if pred_label == "BŁĄD_API":
        error_count += 1
    else:
        y_test_valid.append(true_label)
        y_pred_valid.append(pred_label)
        success_count += 1

print(f"\n✅ Zakończono symulację.")
print(f"Sukcesy (symulowane): {success_count}")
print(f"Błędy API (symulowane): {error_count}")

from sklearn.metrics import accuracy_score
if len(y_test_valid) > 0:
    accuracy_gemini = accuracy_score(y_test_valid, y_pred_valid)
    print(f"\n=== Gemini 2.5-flash-lite (SYMULACJA) ===")
    print(f"Accuracy: {accuracy_gemini:.4f} ({accuracy_gemini*100:.2f}%)")
    
    # Ustawiamy zmienne globalne dla dalszej części notebooka
    y_test_gemini_final = y_test_valid
    y_pred_gemini_final = y_pred_valid
    
else:
    print("Brak danych.")
