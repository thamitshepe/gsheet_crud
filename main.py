from fastapi import FastAPI
from oauth2client.service_account import ServiceAccountCredentials
from fastapi.middleware.cors import CORSMiddleware
import gspread
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lus-sheet.onrender.com"],  # Replace with your web app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Load Google Sheets credentials
creds = ServiceAccountCredentials.from_json_keyfile_name("secretkey.json", scopes=scopes)

file = gspread.authorize(creds)
workbook = file.open("Inventory")
sheet = workbook.sheet1

@app.post("/edit-shoe")
async def edit_shoe(
    shoe_name: str, sku: str, new_shoe_name: str = None, new_sku: str = None,
    new_cost: float = None, new_size: str = None, size: str = None, new_quantity: int = None, quantity: int = None,
    new_list_price: float = None, list_price: float = None, condition: str = None, new_condition: str = None
):

    # Find all rows matching the specified "Shoe" and "SKU"
    all_rows = sheet.get_all_records()
    rows_to_update = []

    for index, row in enumerate(all_rows, start=2):
        if row.get("Shoe") == shoe_name and row.get("Sku") == sku:
            # Create a flag to track whether any update condition is met
            update_flag = False

            if new_shoe_name is not None:
                row["Shoe"] = new_shoe_name
                update_flag = True
            if new_sku is not None:
                row["Sku"] = new_sku
                update_flag = True
            if new_cost is not None:
                row["Cost"] = new_cost
                update_flag = True
            if new_size is not None and row.get("Size") == size:
                row["Size"] = new_size
                update_flag = True
            if new_quantity is not None and row.get("Size") == size and row.get("Quantity") == quantity:
                row["Quantity"] = new_quantity
                update_flag = True
            if new_list_price is not None and row.get("Size") == size and row.get("List Price") == list_price:
                row["List Price"] = new_list_price
                update_flag = True
            if new_condition is not None and row.get("Size") == size and row.get("Condition") == condition:
                row["Condition"] = new_condition
                update_flag = True

            if update_flag:
                rows_to_update.append((index, list(row.values())))

    if not rows_to_update:
        return {"message": "Shoe and SKU combination not found"}

    # Prepare the values for updating the specified columns
    for index, columns in rows_to_update:
        # Update the columns with the modified values
        # Calculate the range based on the number of columns in the data
        range_start = f"A{index}"
        range_end = chr(ord("A") + len(columns) - 1) + str(index)
        sheet.update(range_start + ":" + range_end, [columns], value_input_option="RAW")

    return {"message": "Cells updated"}

