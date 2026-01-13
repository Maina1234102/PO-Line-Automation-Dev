import pandas as pd
import os

data = {
    "OrganizationId": [
        "300000003141330"
    ],
    "OrganizationName": [
        "Inspira Item Master"
    ]
}

df = pd.DataFrame(data)

# Ensure string type for IDs
df["OrganizationId"] = df["OrganizationId"].astype(str)
df["OrganizationName"] = df["OrganizationName"].astype(str)

output_path = os.path.join(os.path.dirname(__file__), "organization_mapping.xlsx")
try:
    df.to_excel(output_path, index=False)
    print(f"Successfully created {output_path}")
except ImportError:
    print("openpyxl not installed. Installing...")
    os.system("pip install openpyxl pandas")
    df.to_excel(output_path, index=False)
    print(f"Successfully created {output_path}")
