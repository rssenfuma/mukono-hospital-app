import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from sklearn.metrics import (
    accuracy_score,
    recall_score,
    roc_curve,
    auc,
    confusion_matrix
)

from imblearn.over_sampling import SMOTE

# ==========================================================
# 1. SETUP
# ==========================================================

sns.set_theme(style="whitegrid")

os.makedirs("chapter_six_outputs", exist_ok=True)
os.makedirs("models", exist_ok=True)

print("="*70)
print("NEONATAL READMISSION ANALYSIS PIPELINE")
print("="*70)

# ==========================================================
# 2. LOAD DATA
# ==========================================================

df = pd.read_excel("Dataset-MGH.xlsx")

print("\nDataset Shape:")
print(df.shape)

# ==========================================================
# 3. TARGET VARIABLE (FIXED - SAFE VERSION)
# ==========================================================

target_col = "Neonatal_Readmission_Within_28_Days"

# Step 1: Inspect raw values first (IMPORTANT)
print("\nRaw target values before cleaning:")
print(df[target_col].value_counts(dropna=False))

# # ==========================================================
# 3. TARGET VARIABLE (FINAL FIX - NUMERIC DATASET)
# ==========================================================

target_col = "Neonatal_Readmission_Within_28_Days"

# Ensure numeric conversion only (DO NOT MAP)
df[target_col] = pd.to_numeric(df[target_col], errors="coerce")

# Debug check
print("\nTarget distribution after numeric conversion:")
print(df[target_col].value_counts(dropna=False))

# Drop only missing values
df = df.dropna(subset=[target_col])

# Convert to integer
df[target_col] = df[target_col].astype(int)

print("\nFinal target distribution:")
print(df[target_col].value_counts())

print("\nDataset shape after target cleaning:", df.shape)

# Step 5: Check BEFORE dropping (VERY IMPORTANT DEBUG STEP)
print("\nAfter mapping (before dropna):")
print(df[target_col].value_counts(dropna=False))

# Step 6: Drop ONLY missing target rows
df = df.dropna(subset=[target_col])

# Step 7: Convert to integer
df[target_col] = df[target_col].astype(int)

print("\nFinal target distribution:")
print(df[target_col].value_counts())
print("\nDataset shape after target cleaning:", df.shape)
# ==========================================================
# 4. FEATURES
# ==========================================================

core_features = [

    "Maternal_Age",
    "Parity",
    "ANC_Attendance_Visits",

    "Mode_of_Delivery",
    "Sex_of_Neonate",

    "Birth_Weight_kg",
    "Gestational_Age_Weeks",
    "Apgar_5min",

    "Feeding_Type_at_Discharge",

    "Duration_of_Initial_Stay_Days",

    "Discharge_Condition",

    "Followup_Appointment_Given"
]

# ==========================================================
# 5. LABEL ENCODING
# ==========================================================

categorical_cols = [

    "Mode_of_Delivery",
    "Sex_of_Neonate",
    "Feeding_Type_at_Discharge",
    "Discharge_Condition",
    "Followup_Appointment_Given"
]

encoders = {}

encoding_table = []

for col in categorical_cols:

    le = LabelEncoder()

    df[col] = le.fit_transform(df[col].astype(str))

    encoders[col] = le

    for cls, code in zip(le.classes_, range(len(le.classes_))):

        encoding_table.append([
            col,
            cls,
            code
        ])

encoding_df = pd.DataFrame(
    encoding_table,
    columns=[
        "Column",
        "Original_Value",
        "Encoded_Value"
    ]
)

encoding_df.to_csv(
    "chapter_six_outputs/table_6_2_label_encoding.csv",
    index=False
)

# ==========================================================
# 6. DESCRIPTIVE STATISTICS
# ==========================================================

print("\nGenerating Descriptive Statistics...")

desc_stats = df[
    [
        "Maternal_Age",
        "Birth_Weight_kg",
        "Gestational_Age_Weeks",
        "Apgar_5min"
    ]
].describe().T

desc_stats.to_csv(
    "chapter_six_outputs/table_6_1_descriptive_statistics.csv"
)

print(desc_stats)

# ==========================================================
# 7. READMISSION DISTRIBUTION
# ==========================================================

distribution = (
    df[target_col]
    .value_counts()
)

distribution.to_csv(
    "chapter_six_outputs/table_6_5_readmission_distribution.csv"
)
distribution_percent = (
    df[target_col]
    .value_counts(normalize=True) * 100
)

distribution_percent.to_csv(
    "chapter_six_outputs/table_6_6_readmission_percentages.csv"
)


plt.figure(figsize=(6,5))

sns.countplot(
    x=target_col,
    data=df
)

plt.title(
    "28-Day Neonatal Readmission Outcomes"
)

plt.tight_layout()

plt.savefig(
    "chapter_six_outputs/figure_6_1_readmission_distribution.png",
    dpi=300
)

plt.close()

# ==========================================================
# 8. PREPARE DATA
# ==========================================================
missing_cols = set(core_features) - set(df.columns)

print("\nMissing feature columns:", missing_cols)

X = df[core_features]

y = df[target_col]

# ==========================================================
# 9. TRAIN TEST SPLIT
# ==========================================================

print("\nFinal dataset shape before training:", df.shape)

if df.shape[0] == 0:
    raise ValueError("Dataset is empty after cleaning. Check target variable mapping and feature columns.")

X = df[core_features]
y = df[target_col]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

print("\nTraining Records:", len(X_train))
print("Testing Records:", len(X_test))

# ==========================================================
# 10. SMOTE
# ==========================================================

print("\nApplying SMOTE...")

smote = SMOTE(
    random_state=42
)

X_train_resampled, y_train_resampled = (
    smote.fit_resample(
        X_train,
        y_train
    )
)

print(
    pd.Series(
        y_train_resampled
    ).value_counts()
)

# ==========================================================
# 11. SCALING
# ==========================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(
    X_train_resampled
)

X_test_scaled = scaler.transform(
    X_test
)

# ==========================================================
# 12. MODELS
# ==========================================================

models = {

    "Logistic Regression":
        LogisticRegression(
            max_iter=2000,
            random_state=42
        ),

    "Random Forest":
        RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            min_samples_split=10,
            random_state=42
        ),

    "Support Vector Machine":
        SVC(
            probability=True,
            random_state=42
        )
}

# ==========================================================
# 13. TRAINING
# ==========================================================

performance_summary = []

plt.figure(figsize=(8,6))

for name, model in models.items():

    print(f"\nTraining {name}...")

    model.fit(
        X_train_scaled,
        y_train_resampled
    )

    y_pred = model.predict(
        X_test_scaled
    )

    y_prob = model.predict_proba(
        X_test_scaled
    )[:,1]

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    sensitivity = recall_score(
        y_test,
        y_pred
    )

    specificity = recall_score(
        y_test,
        y_pred,
        pos_label=0
    )

    fpr, tpr, _ = roc_curve(
        y_test,
        y_prob
    )

    roc_auc = auc(
        fpr,
        tpr
    )

    performance_summary.append({

        "Model": name,
        "Accuracy": round(accuracy,4),
        "Sensitivity": round(sensitivity,4),
        "Specificity": round(specificity,4),
        "AUC_ROC": round(roc_auc,4)
    })

    plt.plot(
        fpr,
        tpr,
        label=f"{name} (AUC={roc_auc:.3f})"
    )

    cm = confusion_matrix(
        y_test,
        y_pred
    )

    pd.DataFrame(cm).to_csv(
        f"chapter_six_outputs/{name}_confusion_matrix.csv"
    )

# ==========================================================
# 14. ROC CURVE
# ==========================================================

plt.plot(
    [0,1],
    [0,1],
    linestyle="--"
)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")

plt.title(
    "ROC Curve Comparison"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "chapter_six_outputs/figure_6_2_roc_curves.png",
    dpi=300
)

plt.close()

# ==========================================================
# 15. MODEL PERFORMANCE TABLE
# ==========================================================

performance_df = pd.DataFrame(
    performance_summary
)

performance_df.to_csv(
    "chapter_six_outputs/table_6_3_model_performance.csv",
    index=False
)

print("\nModel Performance")

print(performance_df)

# ==========================================================
# 16. FEATURE IMPORTANCE
# ==========================================================

rf_model = models["Random Forest"]

feature_importance = pd.DataFrame({

    "Feature":
        core_features,

    "Importance":
        rf_model.feature_importances_
})

feature_importance = (
    feature_importance
    .sort_values(
        by="Importance",
        ascending=False
    )
)

feature_importance["Importance_%"] = (
    feature_importance["Importance"]
    * 100
).round(2)

feature_importance.to_csv(
    "chapter_six_outputs/table_6_4_feature_importance.csv",
    index=False
)

print("\nFeature Importance")

print(feature_importance)

# ==========================================================
# 17. FEATURE IMPORTANCE PLOT
# ==========================================================

plt.figure(figsize=(10,6))

sns.barplot(

    data=feature_importance,
    x="Importance",
    y="Feature"
)

plt.title(
    "Random Forest Feature Importance"
)

plt.tight_layout()

plt.savefig(
    "chapter_six_outputs/figure_6_3_feature_importance.png",
    dpi=300
)

plt.close()
# ==========================================================
# 18. CORRELATION HEATMAP
# ==========================================================

plt.figure(figsize=(12,8))

corr_matrix = df[core_features + [target_col]].corr()

sns.heatmap(
    corr_matrix,
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)

plt.title(
    "Correlation Matrix of Study Variables"
)

plt.tight_layout()

plt.savefig(
    "chapter_six_outputs/figure_6_4_correlation_heatmap.png",
    dpi=300
)

plt.close()

# ==========================================================
# 19. LOGISTIC REGRESSION COEFFICIENTS
# ==========================================================

lr_model = models["Logistic Regression"]

coefficients = pd.DataFrame({

    "Feature": core_features,
    "Coefficient": lr_model.coef_[0]
})

coefficients = coefficients.sort_values(
    by="Coefficient",
    ascending=False
)

coefficients.to_csv(
    "chapter_six_outputs/table_6_7_logistic_coefficients.csv",
    index=False
)

print("\nLogistic Regression Coefficients")
print(coefficients)

# ==========================================================
# 20. EXPORT MODELS FOR STREAMLIT
# ==========================================================

joblib.dump(
    rf_model,
    "models/rf_model.joblib"
)

joblib.dump(
    scaler,
    "models/scaler.joblib"
)

joblib.dump(
    encoders,
    "models/categorical_encoders.joblib")

print("\nModels Exported Successfully")

print("\nAnalysis Completed Successfully")