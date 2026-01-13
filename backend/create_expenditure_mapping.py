import pandas as pd
import os

data = {
    "ExpenditureTypeId": [
        "300000004181249", "300000028558057", "300000028558081", "300000028558152",
        "300000028558152", "300000028558178", "3000000396542392", "300000028558065",
        "300000028558065", "300000028558113", "3000000396542496", "3000000396542498",
        "3000000396542536", "3000000396542342", "3000000396542382", "3000000396542397",
        "300000004181245", "300000028558033", "300000028558042", "3000000396542450",
        "3000000396542425", "3000000396542425", "3000000396542491", "3000000396542493",
        "3000000397609630"
    ],
    "ExpenditureTypeName": [
        "Local Conveyance", "Car Parking Charges", "Conveyance", "Training Charges",
        "Training Charges", "Vehicle Maintenance", "COGS (NAV)", "Carriage Inward",
        "Carriage Inward", "Postage & Courier", "Custom Duty-Gst", "Custom Duty / Thc - Health Care",
        "Depreciation On Vehicles", "Bank Charges", "Books & Periodicals", "COGS Other",
        "Local Conveyance1", "Bank Charges For Letter Of Credit (Lc)", "Car Hire Charges", "Csr Expenditure",
        "Cost Of Goods Sold -Goods", "Cost Of Goods Sold -Goods", "Depreciation On Electrical Installations", "Depreciation On Computer Software",
        "Rate Difference (CM)"
    ]
}

df = pd.DataFrame(data)

# Ensure string type for IDs
df["ExpenditureTypeId"] = df["ExpenditureTypeId"].astype(str)
df["ExpenditureTypeName"] = df["ExpenditureTypeName"].astype(str)

output_path = os.path.join(os.path.dirname(__file__), "expenditure_mapping.xlsx")
try:
    df.to_excel(output_path, index=False)
    print(f"Successfully created {output_path}")
except ImportError:
    print("openpyxl not installed. Installing...")
    os.system("pip install openpyxl pandas")
    df.to_excel(output_path, index=False)
    print(f"Successfully created {output_path}")
