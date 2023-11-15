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
workbook = file.open("WholeCell Inventory Template")
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
    new_price_paid: typing.Optional[str] = Query(None, title="Optional: New Cost"),
    new_quantity: typing.Optional[str] = Query(None, title="Optional: New Quantity"),
    new_list_price: typing.Optional[str] = Query(None, title="Optional: New List Price"),
    cost: typing.Optional[str] = Query(None, title="Optional: Cost"),
    new_condition: typing.Optional[str] = Query(None, title="Optional: New Condition"),
    status: typing.Optional[str] = Query(None, title="Optional: Status"),
    listed: typing.Optional[str] = Query(None, title="Optional: Listed"),
    source: typing.Optional[str] = Query(None, title="Optional: Source"),
    seller: typing.Optional[str] = Query(None, title="Optional: Seller"),
    note: typing.Optional[str] = Query(None, title="Optional: Note"),
    delete: typing.Optional[bool] = Query(False, title="Optional: Delete")
):

    # Ensure that sku is always treated as a string
    sku = sku_to_string(sku)

    # Find all the rows matching the specified "Shoe," "SKU," and optionally "Size"
    rows_to_update = []
    
    all_records = sheet.get_all_records()
    for index, row in enumerate(all_records, start=2):
        if row.get("Model") == shoe_name:
            if size:  # If "size" is provided in the request, consider it
                if row.get("Capacity"):
                    size_from_sheets = size_to_string(row.get("Capacity"))
                    if size != size_from_sheets:
                        continue
                else:
                    continue
    
            if sku:  # If "sku" is provided in the request, consider it
                if row.get("Sku"):
                    sku_from_sheets = sku_to_string(row.get("Sku"))
                    if sku != sku_from_sheets:
                        continue
                else:
                    continue
    
            # If it reaches this point, it means it matched Shoe, Size, and SKU (if specified)
            rows_to_update.append((index, row))


    if delete:
        rows_to_delete = []
        if size:
            # Delete specific SKU and Size combination
            rows_to_delete = [index for index, row in enumerate(all_records, start=2)
                              if sku_to_string(row.get("Sku")) == sku and size_to_string(row.get("Capacity")) == size]
        else:
            # Delete all rows with a specific SKU
            rows_to_delete = [index for index, row in enumerate(all_records, start=2)
                              if sku_to_string(row.get("Sku")) == sku]

        if not rows_to_delete:
            return {"message": "No rows found for deletion"}

        # Sort rows in descending order so that rows can be deleted without shifting indices
        rows_to_delete.sort(reverse=True)

        for index in rows_to_delete:
            sheet.delete_rows(index)

        return {"message": f"{len(rows_to_delete)} rows deleted"}

    if not rows_to_update:
        return {"message": "Name, SKU, and Size combination not found"}

    for index, row in rows_to_update:
        # Update the columns based on the provided values
        if new_size is not None:
            row["Capacity"] = new_size
        if new_shoe_name is not None:
            row["Model"] = new_shoe_name
        if new_sku is not None:
            row["Sku"] = sku_to_string(new_sku)  # Ensure new_sku is treated as a string
        if new_price_paid is not None:
            row["Price Paid"] = new_price_paid
        if new_quantity is not None:
            row["Quantity"] = new_quantity
        if new_condition is not None:
            row["Grade"] = new_condition
        if new_list_price is not None:
            row["List Price"] = new_list_price
        if cost is not None:
            row["Cost"] = cost
        if status is not None:
            row["Status"] = status
        if listed is not None:
            row["Listed"] = listed
        if source is not None:
            row["Source"] = source
        if seller is not None:
            row["Seller"] = seller
        if note is not None:
            row["Notes"] = note

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
    price_paid: typing.Optional[str] = Query(None, title="Price Paid")
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
        new_row[column_mapping["Model"]] = shoe_name
        new_row[column_mapping["Sku"]] = sku
        new_row[column_mapping["Capacity"]] = add_size
        new_row[column_mapping["Complete"]] = complete
        new_row[column_mapping["Source"]] = cur_source
        new_row[column_mapping["Seller"]] = cur_seller
        new_row[column_mapping["Notes"]] = cur_note
        new_row[column_mapping["Price Paid"]] = price_paid

        # Insert a new row right after the last row containing the specified SKU
        sheet.insert_rows([new_row], last_row_index + 1)

        return {"message": "New size added"}
    else:
        return {"message": "No rows found for the specified SKU"}

@app.post("/add-sku")
async def add_sku(
    shoe_name: str,
    add_sku: typing.Optional[str] = Query(None, title="SKU"),
    complete: typing.Optional[str] = Query(None, title="Complete"),
    cur_source: typing.Optional[str] = Query(None, title="Source"),
    cur_seller: typing.Optional[str] = Query(None, title="Seller"),
    cur_note: typing.Optional[str] = Query(None, title="Note"),
    date: typing.Optional[str] = Query(None, title="Date"),
    cost: typing.Optional[str] = Query(None, title="Cost")
):
    # Ensure that add_sku is always treated as a string
    add_sku = sku_to_string(add_sku)

    # Find the last row containing the specified Shoe
    all_records = sheet.get_all_records()
    last_row_index = None

    for index, row in enumerate((all_records), start=2):
        if row.get("Model") == shoe_name:
            last_row_index = index

    if last_row_index is not None:
        # Get the header row (the row containing field names)
        header_row = sheet.row_values(1)  # Assuming header row is the first row

        # Create a dictionary to map column names to their respective index
        column_mapping = {header: index for index, header in enumerate(header_row)}

        # Create a new row with the provided data
        new_row = [""] * len(header_row)  # Initialize a list with empty values

        # Map the data to the appropriate columns
        new_row[column_mapping["Model"]] = shoe_name
        new_row[column_mapping["Sku"]] = add_sku  # Use the provided SKU
        new_row[column_mapping["Complete"]] = complete
        new_row[column_mapping["Source"]] = cur_source
        new_row[column_mapping["Seller"]] = cur_seller
        new_row[column_mapping["Notes"]] = cur_note
        new_row[column_mapping["Price Paid"]] = cost

        # Insert a new row right after the last row containing the specified Shoe
        sheet.insert_rows([new_row], last_row_index + 1)

        return {"message": "New SKU added"}
    else:
        return {"message": "No rows found for the specified Shoe"}
