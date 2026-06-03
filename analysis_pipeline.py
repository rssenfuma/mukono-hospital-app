import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib  # Added for exporting the model artifacts
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score, recall_score, precision_score, f1_score, roc_curve, auc
from imblearn.over_sampling import SMOTE

sns.set_theme(style="whitegrid")
os.makedirs("chapter_six_outputs", exist_ok=True)

print("=== 1. COMMENCING DATA CLEANING & PREPROCESSING ===")
df = pd.read_csv('Dataset-MGH.csv')

core_features = [
    'Maternal_Age', 'Parity', 'ANC_Attendance_Visits', 'Mode_of_Delivery', 
    'Sex_of_Neonate', 'Birth_Weight_kg', 'Gestational_Age_Weeks', 'Apgar_5min', 
    'Feeding_Type_at_Discharge', 'Duration_of_Initial_Stay_Days', 'Discharge_Condition'
]
target_col = 'Neonatal_Readmission_Within_28_Days'

df[target_col] = df[target_col].fillna('No')
df[target_col] = df[target_col].map({'Yes': 1, 'No': 0})

encoders = {}
categorical_cols = ['Mode_of_Delivery', 'Sex_of_Neonate', 'Feeding_Type_at_Discharge', 'Discharge_Condition']

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    encoders[col] = le

X = df[core_features]
y = df[target_col]
print("\n=== CLASS DISTRIBUTION ===")
print(df[target_col].value_counts())

print("\n=== PERCENTAGE DISTRIBUTION ===")
print(round(df[target_col].value_counts(normalize=True) * 100, 2))

print("\n=== 2. GENERATING DESCRIPTIVE STATISTICS ===")
print(pd.read_csv('Dataset-MGH.csv')[['Maternal_Age', 'Birth_Weight_kg', 'Gestational_Age_Weeks', 'Apgar_5min']].describe().T)

print("\n=== 3. EXECUTING VISUALIZATION PACKS ===")
plt.figure(figsize=(6, 5))
sns.countplot(data=pd.read_csv('Dataset-MGH.csv'), x=target_col, palette=['#34495E', '#E74C3C'])
plt.title("28-Day Neonatal Readmissions")
plt.tight_layout()
plt.savefig("chapter_six_outputs/readmission_distribution.png", dpi=300)
plt.close()

print("\n=== 4. EXECUTING DATA SPLIT & CLASS BALANCING (SMOTE) ===")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=42, stratify=y)
smote = SMOTE(random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_res)
X_test_scaled = scaler.transform(X_test)

print("\n=== 5. TRAINING MODELS & CALCULATING PERFORMANCE METRICS ===")
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "Support Vector Machine": SVC(probability=True, random_state=42)
}

performance_summary = []
plt.figure(figsize=(8, 6))

for name, model in models.items():
    model.fit(X_train_scaled, y_train_res)
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    
    performance_summary.append({
        "Model": name, "Accuracy": accuracy_score(y_test, y_pred), 
        "Sensitivity": recall_score(y_test, y_pred), "Specificity": recall_score(y_test, y_pred, pos_label=0), 
        "AUC-ROC": roc_auc
    })
    plt.plot(fpr, tpr, label=f'{name} (AUC = {roc_auc:.2f})')

plt.plot([0, 1], [0, 1], 'k--')
plt.title('ROC Curve Comparison')
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig("chapter_six_outputs/roc_curve_comparison.png", dpi=300)
plt.close()

print(pd.DataFrame(performance_summary).to_string(index=False))

print("\n=== 6. EXTRACTION OF FEATURE IMPORTANCE WEIGHTS ===")
rf_model = models["Random Forest"]
feat_imp = pd.DataFrame({'Feature': core_features, 'Importance': rf_model.feature_importances_}).sort_values(by='Importance', ascending=False)
print(feat_imp.to_string(index=False))

plt.figure(figsize=(10, 6))
sns.barplot(data=feat_imp, x='Importance', y='Feature', palette='viridis')
plt.title('Random Forest Feature Importance')
plt.tight_layout()
plt.savefig("chapter_six_outputs/feature_importances.png", dpi=300)
plt.close()

print("\n=== 7. EXPORTING TRAINED APP ASSETS ===")
# Create a dedicated directory for application deployment binaries
os.makedirs("models", exist_ok=True)

# Save the primary Random Forest classifier, Scaler, and categorical text encoders
joblib.dump(rf_model, "models/rf_model.joblib")
joblib.dump(scaler, "models/scaler.joblib")
joblib.dump(encoders, "models/categorical_encoders.joblib")

print("Production assets successfully compiled and saved to standard 'models/' layout.")
print("\n=== PIPELINE PROCESS TERMINATED SUCCESSFULLY ===")