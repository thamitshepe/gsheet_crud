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

@app.post("/edit-shoe")
async def edit_shoe(
    shoe_name: str,
    sku: str,
    size: str,
    new_shoe_name: typing.Optional[str] = Query(None, title="Optional: New Shoe Name"),
    new_sku: typing.Optional[str] = Query(None, title="Optional: New SKU"),
    new_cost: typing.Optional[float] = Query(None, title="Optional: New Cost"),
    new_size: typing.Optional[str] = Query(None, title="Optional: New Size"),
    new_quantity: typing.Optional[int] = Query(None, title="Optional: New Quantity"),
    new_list_price: typing.Optional[float] = Query(None, title="Optional: New List Price"),
    new_condition: typing.Optional[str] = Query(None, title="Optional: New Condition")
):

    # Debugging: Log the received size parameter
    print(f"Received size parameter: '{size}'")

    # Find all rows matching the specified "Shoe" and "SKU"
    all_rows = sheet.get_all_records()
    rows_to_update = []

    for index, row in enumerate(all_rows, start=2):
        if row.get("Shoe") == shoe_name and row.get("Sku") == sku and row.get("Size") == size:
            # Update the columns based on the provided values
            if new_shoe_name is not None:
                row["Shoe"] = new_shoe_name
            if new_sku is not None:
                row["Sku"] = new_sku
            if new_cost is not None:
                row["Cost"] = new_cost
            if new_size is not None:
                row["Size"] = new_size
            if new_quantity is not None:
                row["Quantity"] = new_quantity
            if new_list_price is not None:
                row["List Price"] = new_list_price
            if new_condition is not None:
                row["Condition"] = new_condition
            rows_to_update.append((index, list(row.values())))

    if not rows_to_update:
        return {"message": "Shoe, SKU, and Size combination not found"}

    # Prepare the values for updating the specified columns
    for index, columns in rows_to_update:
        # Update the columns with the modified values
        # Calculate the range based on the number of columns in the data
        range_start = f"A{index}"
        range_end = chr(ord("A") + len(columns) - 1) + str(index)
        sheet.update(range_start + ":" + range_end, [columns], value_input_option="RAW")

    return {"message": "Cells updated"}
