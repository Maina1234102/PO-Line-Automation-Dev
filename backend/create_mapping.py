import pandas as pd
import os

data = {
    "ProjectId": [
        "300000022898415", "300000003145066", "300000003145048", "300000003145084", 
        "300000003148118", "300000003302035", "300000003302047", "300000003145075",
        "300000003148109", "300000003302011", "300000003302023", "300000003302227",
        "300000003302239", "300000003302251", "300000003302263", "300000003302275",
        "300000003302287", "300000003302299", "300000003302311", "300000003302407",
        "300000003302419", "300000003302431", "300000003302443", "300000003302455",
        "300000003302467", "300000003302479"
    ],
    "ProjectNumber": [
        "6572", "21822", "PRJOJECT01", "25752", "25753", "1114", "1070", "22758",
        "25751", "1029", "1062", "1046", "1091", "1068", "1057", "1064", "1044", 
        "1033", "1066", "1016", "1077", "1023", "1081", "1060", "1115", "1117"
    ]
}

df = pd.DataFrame(data)

# Ensure string type for IDs to avoid scientific notation
df["ProjectId"] = df["ProjectId"].astype(str)
df["ProjectNumber"] = df["ProjectNumber"].astype(str)

output_path = os.path.join(os.path.dirname(__file__), "project_mapping.xlsx")
try:
    df.to_excel(output_path, index=False)
    print(f"Successfully created {output_path}")
except ImportError:
    print("openpyxl not installed. Installing...")
    os.system("pip install openpyxl pandas")
    df.to_excel(output_path, index=False)
    print(f"Successfully created {output_path}")
