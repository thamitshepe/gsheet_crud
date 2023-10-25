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

def sku_to_string(sku):
    # Function to ensure sku is always a string
    return str(sku)

@app.post("/edit-shoe")
async def edit_shoe(
    shoe_name: str,
    sku: str,
    size: typing.Optional[str] = Query(None, title="Optional: Size"),
    new_size: typing.Optional[str] = Query(None, title="Optional: New Size"),
    new_shoe_name: typing.Optional[str] = Query(None, title="Optional: New Shoe Name"),
    new_sku: typing.Optional[str] = Query(None, title="Optional: New SKU"),
    new_cost: typing.Optional[str] = Query(None, title="Optional: New Cost"),
    new_quantity: typing.Optional[str] = Query(None, title="Optional: New Quantity"),
    new_list_price: typing.Optional[str] = Query(None, title="Optional: New List Price"),
    new_condition: typing.Optional[str] = Query(None, title="Optional: New Condition"),
    listed: typing.Optional[bool] = Query(None, title="Optional: Listed"),
    source: typing.Optional[str] = Query(None, title="Optional: Source"),
    seller: typing.Optional[str] = Query(None, title="Optional: Seller"),
    note: typing.Optional[str] = Query(None, title="Optional: Note"),
    delete: typing.Optional[bool] = Query(False, title="Optional: Delete")
):

    # Ensure that sku is always treated as a string
    sku = sku_to_string(sku)

    # Find all the rows matching the specified "Shoe," "SKU," and optionally "Size"
    all_rows = sheet.get_all_records()
    rows_to_update = []

    for index, row in enumerate(all_rows, start=2):
        if row.get("Shoe") == shoe_name and sku_to_string(row.get("Sku")) == sku:
            if size:  # If "size" is provided in the request, consider it
                if row.get("Size"):
                    size_from_sheets = size_to_string(row.get("Size"))
                    if size != size_from_sheets:
                        continue
                else:
                    continue

            # If it reaches this point, it means it matched Shoe, SKU, and Size (if specified)
            rows_to_update.append((index, row))

    if delete:
        rows_to_delete = []
        for index, _ in rows_to_update:
            rows_to_delete.append(index)

        if not rows_to_delete:
            return {"message": "No rows found for deletion"}

        # Sort rows in descending order so that rows can be deleted without shifting indices
        rows_to_delete.sort(reverse=True)

        for index in rows_to_delete:
            sheet.delete_rows(index)

        return {"message": f"{len(rows_to_delete)} rows deleted"}

    if not rows_to_update:
        return {"message": "Shoe, SKU, and Size combination not found"}

    for index, row in rows_to_update:
        # Update the columns based on the provided values
        if new_size is not None:
            row["Size"] = new_size
        if new_shoe_name is not None:
            row["Shoe"] = new_shoe_name
        if new_sku is not None:
            row["Sku"] = sku_to_string(new_sku)  # Ensure new_sku is treated as a string
        if new_cost is not None:
            row["Cost"] = new_cost
        if new_quantity is not None:
            row["Quantity"] = new_quantity
        if new_condition is not None:
            row["Condition"] = new_condition
        if new_list_price is not None:
            row["List Price"] = new_list_price
        if listed is not True:
            row["Listed"] = True
        else:
            row["Listed"] = False
        if source is not None:
            row["Source"] = source
        if seller is not None:
            row["Seller"] = seller
        if note is not None:
            row["Note"] = note

        # Calculate the range for the specific row
        range_start = f"A{index}"
        range_end = chr(ord("A") + len(row) - 1) + str(index)
        sheet.update(range_start + ":" + range_end, [list(row.values())], value_input_option="RAW")

    return {"message": "Cells updated"}
