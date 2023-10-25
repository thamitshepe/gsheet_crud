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
    return str(size)

def sku_to_string(sku):
    if isinstance(sku, list):
        return [str(s) for s in sku]
    else:
        return [str(sku)]

@app.post("/edit-shoe")
async def edit_shoe(
    shoe_name: str,
    sku: typing.Union[str, typing.List[str]],  # Accepts both single string and list
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

    if not isinstance(sku, list):
        sku = [sku]  # Convert single SKU to a list for uniform handling

    # Find all the rows matching the specified "Shoe," "SKU," and optionally "Size"
    all_rows = sheet.get_all_records()
    rows_to_update = []

    for index, row in enumerate(all_rows, start=2):
        if row.get("Shoe") == shoe_name and row.get("Sku") in skus:
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
        if size:
            # Delete specific SKU and Size combination
            rows_to_delete = [index for index, row in enumerate(all_rows, start=2)
                              if row.get("Sku") in skus and size_to_string(row.get("Size")) == size]
        else:
            # Delete all rows with any of the specified SKUs
            rows_to_delete = [index for index, row in enumerate(all_rows, start=2)
                              if row.get("Sku") in skus]

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

@app.post("/add-size")
async def add_size(
    shoe_name: str,
    sku: str,
    add_size: typing.Optional[str] = Query(None, title="Size"),
    complete: typing.Optional[str] = Query(None, title="Complete"),
    cur_source: typing.Optional[str] = Query(None, title="Source"),
    cur_seller: typing.Optional[str] = Query(None, title="Seller"),
    cur_note: typing.Optional[str] = Query(None, title="Note"),
    date: typing.Optional[str] = Query(None, title="Date"),
    cost: typing.Optional[str] = Query(None, title="Cost")
):
    # Ensure that sku and add_size are always treated as strings
    sku = sku_to_string(sku)
    add_size = size_to_string(add_size)

    # Find the last row containing the specified SKU
    all_records = sheet.get_all_records()
    last_row_index = None

    for index, row in enumerate(all_records, start=2):
        if sku_to_string(row.get("Sku")) == sku:
            last_row_index = index

    if last_row_index is not None:
        # Get the header row (the row containing field names)
        header_row = sheet.row_values(1)  # Assuming header row is the first row

        # Create a dictionary to map column names to their respective index
        column_mapping = {header: index for index, header in enumerate(header_row)}

        # Create a new row with the provided data
        new_row = [""] * len(header_row)  # Initialize a list with empty values

        # Map the data to the appropriate columns
        new_row[column_mapping["Shoe"]] = shoe_name
        new_row[column_mapping["Sku"]] = sku
        new_row[column_mapping["Size"]] = add_size
        new_row[column_mapping["Complete"]] = complete
        new_row[column_mapping["Source"]] = cur_source
        new_row[column_mapping["Seller"]] = cur_seller
        new_row[column_mapping["Note"]] = cur_note
        new_row[column_mapping["Date"]] = date
        new_row[column_mapping["Cost"]] = cost

        # Insert a new row right after the last row containing the specified SKU
        sheet.insert_rows([new_row], last_row_index + 1)

        return {"message": "New size added"}
    else:
        return {"message": "No rows found for the specified SKU"}
