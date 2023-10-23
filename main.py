from fastapi import FastAPI, Query
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import typing

app = FastAPI()

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Load Google Sheets credentials
creds = ServiceAccountCredentials.from_json_keyfile_name("secretkey.json", scopes=scopes)

file = gspread.authorize(creds)
workbook = file.open("Inventory")
sheet = workbook.sheet1

def size_to_string(size):
    # Function to ensure size is always a string
    return str(size)

@app.post("/edit-shoe")
async def edit_shoe(
    shoe_name: str,
    sku: str,
    size: str,
    new_size: typing.Optional[str] = Query(None, title="Optional: New Size"),
    new_shoe_name: typing.Optional[str] = Query(None, title="Optional: New Shoe Name"),
    new_sku: typing.Optional[str] = Query(None, title="Optional: New SKU"),
    new_cost: typing.Optional[float] = Query(None, title="Optional: New Cost"),
    new_quantity: typing.Optional[int] = Query(None, title="Optional: New Quantity"),
    new_list_price: typing.Optional[float] = Query(None, title="Optional: New List Price"),
    new_condition: typing.Optional[str] = Query(None, title="Optional: New Condition")
):

    # Find the row matching the specified "Shoe," "SKU," and "Size"
    all_rows = sheet.get_all_records()
    row_to_update = None

    for index, row in enumerate(all_rows, start=2):
        if row.get("Shoe") == shoe_name and row.get("Sku") == sku and row.get("Size"):
            # Use the "Size" value from the Google Sheets column
            size_from_sheets = size_to_string(row.get("Size"))

            # Debugging: Log the received size parameter
            print(f"Received size parameter from the request: '{size}'")
            print(f"Size value from Google Sheets: '{size_from_sheets}'")

            # Check if the size from the request matches the size from the Google Sheets
            if size == size_from_sheets:
                row_to_update = row
                break

    if not row_to_update:
        return {"message": "Shoe, SKU, and Size combination not found"}

    # Update the columns based on the provided values
    if new_size is not None:
        row_to_update["Size"] = new_size
    if new_shoe_name is not None:
        row_to_update["Shoe"] = new_shoe_name
    if new_sku is not None:
        row_to_update["Sku"] = new_sku
    if new_cost is not None:
        row_to_update["Cost"] = new_cost
    if new_quantity is not None:
        row_to_update["Quantity"] = new_quantity
    if new_list_price is not None:
        row_to_update["List Price"] = new_list_price
    if new_condition is not None:
        row_to_update["Condition"] = new_condition

    # Calculate the range for the specific row
    range_start = f"A{index}"
    range_end = chr(ord("A") + len(row_to_update) - 1) + str(index)
    sheet.update(range_start + ":" + range_end, [list(row_to_update.values())], value_input_option="RAW")

    return {"message": "Cells updated", "size": size}
