import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

# Zakładamy, że mamy zmienne:
# - y_test_gemini_final (prawdziwe etykiety dla podzbioru)
# - y_pred_gemini_final (przewidziane etykiety dla podzbioru)
# - accuracy_nb (dokładność Naive Bayes - musisz mieć tę zmienną z wcześniejszych komórek, ok. 0.52)
# - model_gemini_name (np. "Gemini 2.5")

print("\n=== SZCZEGÓŁOWA ANALIZA WYNIKÓW (NB vs GEMINI) ===\n")

# 1. Raport klasyfikacji (Precision, Recall, F1)
print(f"--- Raport Klasyfikacji: Gemini ---")
# Unikalne etykiety z danych testowych
unique_labels = sorted(list(set(y_test_gemini_final) | set(y_pred_gemini_final)))
print(classification_report(y_test_gemini_final, y_pred_gemini_final, zero_division=0))

# 2. Macierz Pomyłek (Confusion Matrix)
cm = confusion_matrix(y_test_gemini_final, y_pred_gemini_final, labels=unique_labels)

plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=unique_labels, yticklabels=unique_labels)
plt.title(f'Macierz Pomyłek - Gemini')
plt.ylabel('Prawdziwa kategoria')
plt.xlabel('Przewidziana kategoria')
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

# 3. Porównanie Dokładności (Bar Chart)
# Obliczamy accuracy dla Gemini (jeśli nie jest jeszcze obliczone)
acc_gemini = accuracy_score(y_test_gemini_final, y_pred_gemini_final)

# Zakładamy, że accuracy_nb jest dostępne z wcześniejszej części notebooka
# Jeśli nie, wpisz ręcznie np. 0.5263
if 'accuracy_nb' not in locals():
    accuracy_nb = 0.5263 # Wartość z Twojego notatnika dla NB

models = ['Naive Bayes (TF-IDF)', 'Gemini (LLM)']
accuracies = [accuracy_nb, acc_gemini]

plt.figure(figsize=(8, 5))
bars = plt.bar(models, accuracies, color=['gray', 'green'])
plt.ylabel('Dokładność (Accuracy)')
plt.title('Porównanie skuteczności modeli')
plt.ylim(0, 1.0)

# Dodanie wartości na słupkach
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2%}',
             ha='center', va='bottom', fontweight='bold')

plt.grid(axis='y', alpha=0.3)
plt.show()

# 4. Tabela porównawcza (DataFrame)
df_comparison = pd.DataFrame({
    'Model': models,
    'Accuracy': accuracies,
    'Opis': ['Baseline (statystyczny)', 'AI (semantyczny)']
})
print("\n--- Tabela Podsumowująca ---")
display(df_comparison) # display() działa w Jupyterze
