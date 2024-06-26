from fastapi import FastAPI, Query
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import typing
import copy

app = FastAPI()

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Load Google Sheets credentials for the first sheet
creds_sheet1 = ServiceAccountCredentials.from_json_keyfile_name("secretkey.json", scopes=scopes)
file_sheet1 = gspread.authorize(creds_sheet1)
workbook_sheet1 = file_sheet1.open("WholeCell Inventory Template")  # Change to the actual name of your first sheet
sheet1 = workbook_sheet1.sheet1

# Load Google Sheets credentials for the second sheet
creds_sheet2 = ServiceAccountCredentials.from_json_keyfile_name("secretkey.json", scopes=scopes)
file_sheet2 = gspread.authorize(creds_sheet2)
workbook_sheet2 = file_sheet2.open("product catalog template")  # Change to the actual name of your second sheet
sheet2 = workbook_sheet2.sheet1

def size_to_string(size):
    return str(size)

def sku_to_string(sku):
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
    new_cost: typing.Optional[str] = Query(None, title="Optional: Cost"),
    new_condition: typing.Optional[str] = Query(None, title="Optional: New Condition"),
    status: typing.Optional[str] = Query(None, title="Optional: Status"),
    listed: typing.Optional[str] = Query(None, title="Optional: Listed"),
    source: typing.Optional[str] = Query(None, title="Optional: Source"),
    seller: typing.Optional[str] = Query(None, title="Optional: Seller"),
    new_manufacturer: typing.Optional[str] = Query(None, title="Optional: Manufacturer"),
    note: typing.Optional[str] = Query(None, title="Optional: Note"),
    new_damages: typing.Optional[str] = Query(None, title="Optional: New Damages"),
    delete: typing.Optional[bool] = Query(False, title="Optional: Delete")
):

    sku = sku_to_string(sku)

    rows_to_update = []

    # Fetch the header row for sheet1
    header_row_sheet1 = sheet1.row_values(1)

    # Fetch the header row for sheet2
    header_row_sheet2 = sheet2.row_values(1)

    # Find the column indices for sheet1
    column_index_sheet1 = {key: idx + 1 for idx, key in enumerate(header_row_sheet1)}

    # Find the column indices for sheet2
    column_index_sheet2 = {key: idx + 1 for idx, key in enumerate(header_row_sheet2)}

    for index, row in enumerate(sheet1.get_all_records(), start=2):
        if row.get("Model") == shoe_name and (not size or size_to_string(row.get("Capacity")) == size) and sku_to_string(row.get("Sku")) == sku:
            rows_to_update.append((index, row))

    if delete:
        rows_to_delete_sheet1 = [index for index, row in enumerate(sheet1.get_all_records(), start=2)
                                  if row.get("Model") == shoe_name and sku_to_string(row.get("Sku")) == sku and (not size or size_to_string(row.get("Capacity")) == size)]
        rows_to_delete_sheet2 = [index for index, row in enumerate(sheet2.get_all_records(), start=2)
                                  if row.get("Model") == shoe_name and sku_to_string(row.get("Sku")) == sku and (not size or size_to_string(row.get("Capacity")) == size)]

        if not rows_to_delete_sheet1 and not rows_to_delete_sheet2:
            return {"message": "No rows found for deletion"}

        # Deleting rows from sheet1
        for index in reversed(rows_to_delete_sheet1):
            sheet1.delete_rows(index)

        # Deleting rows from sheet2
        for index in reversed(rows_to_delete_sheet2):
            sheet2.delete_rows(index)

        return {"message": f"{len(rows_to_delete_sheet1) + len(rows_to_delete_sheet2)} rows deleted"}

    if not rows_to_update:
        return {"message": "Name and SKU combination not found"}

    for index, row in rows_to_update:
        # Update logic for sheet1
        if new_size is not None:
            sheet1.update_cell(index, column_index_sheet1.get("Capacity"), new_size)
        if new_shoe_name is not None:
            sheet1.update_cell(index, column_index_sheet1.get("Model"), new_shoe_name)
        if new_sku is not None:
            sheet1.update_cell(index, column_index_sheet1.get("Sku"), sku_to_string(new_sku))
        if new_price_paid is not None:
            sheet1.update_cell(index, column_index_sheet1.get("Price Paid"), new_price_paid)
        if new_quantity is not None:
            sheet1.update_cell(index, column_index_sheet1.get("Quantity"), new_quantity)
        if new_condition is not None:
            sheet1.update_cell(index, column_index_sheet1.get("Grade"), new_condition)
        if new_list_price is not None:
            sheet1.update_cell(index, column_index_sheet1.get("List Price"), new_list_price)
        if new_cost is not None:
            sheet1.update_cell(index, column_index_sheet1.get("Cost"), new_cost)
        if status is not None:
            sheet1.update_cell(index, column_index_sheet1.get("Status"), status)
        if listed is not None:
            sheet1.update_cell(index, column_index_sheet1.get("Listed"), listed)
        if source is not None:
            sheet1.update_cell(index, column_index_sheet1.get("Source"), source)
        if new_manufacturer is not None:
            sheet1.update_cell(index, column_index_sheet1.get("Manufacturer"), new_manufacturer)
        if seller is not None:
            sheet1.update_cell(index, column_index_sheet1.get("Seller"), seller)
        if note is not None:
            sheet1.update_cell(index, column_index_sheet1.get("Notes"), note)
        if new_damages is not None:
            sheet1.update_cell(index, column_index_sheet1.get("Damages"), new_damages)

        # Update logic for sheet2
        if new_size is not None:
            sheet2.update_cell(index, column_index_sheet2.get("Capacity"), new_size)
        if new_shoe_name is not None:
            sheet2.update_cell(index, column_index_sheet2.get("Model"), new_shoe_name)
        if new_sku is not None:
            sheet2.update_cell(index, column_index_sheet2.get("Sku"), sku_to_string(new_sku))
        if new_condition is not None:
            sheet2.update_cell(index, column_index_sheet2.get("Grade"), new_condition)
        if new_manufacturer is not None:
            sheet2.update_cell(index, column_index_sheet2.get("Manufacturer"), new_manufacturer)
        if new_damages is not None:
            sheet2.update_cell(index, column_index_sheet2.get("Damages"), new_damages)

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
    manufacturer: typing.Optional[str] = Query(None, title="Optional: Manufacturer"),
    price_paid: typing.Optional[str] = Query(None, title="Price Paid"),
    damages: typing.Optional[str] = Query(None, title="Damages"),
    grade: typing.Optional[str] = Query(None, title="Grade")
):
    sku = sku_to_string(sku)
    add_size = size_to_string(add_size)

    all_records_sheet1 = sheet1.get_all_records()
    all_records_sheet2 = sheet2.get_all_records()

    last_row_index_sheet1 = None
    last_row_index_sheet2 = None

    # Find the last row index in sheet1
    for index, row in enumerate(all_records_sheet1, start=2):
        if sku_to_string(row.get("Sku")) == sku:
            last_row_index_sheet1 = index

    # Find the last row index in sheet2
    for index, row in enumerate(all_records_sheet2, start=2):
        # Adjust the condition according to your sheet2 structure
        if row.get("Sku") == sku:
            last_row_index_sheet2 = index

    # Use the header_row from sheet1 for column mapping
    header_row_sheet1 = sheet1.row_values(1)
    column_mapping_sheet1 = {header: index for index, header in enumerate(header_row_sheet1)}
    new_row_sheet1 = [""] * len(header_row_sheet1)
    new_row_sheet1[column_mapping_sheet1["Model"]] = shoe_name
    new_row_sheet1[column_mapping_sheet1["Sku"]] = sku
    new_row_sheet1[column_mapping_sheet1["Capacity"]] = add_size
    new_row_sheet1[column_mapping_sheet1["Complete"]] = complete
    new_row_sheet1[column_mapping_sheet1["Source"]] = cur_source
    new_row_sheet1[column_mapping_sheet1["Seller"]] = cur_seller
    new_row_sheet1[column_mapping_sheet1["Notes"]] = cur_note
    new_row_sheet1[column_mapping_sheet1["Manufacturer"]] = manufacturer
    new_row_sheet1[column_mapping_sheet1["Price Paid"]] = price_paid
    new_row_sheet1[column_mapping_sheet1["Damages"]] = damages
    new_row_sheet1[column_mapping_sheet1["Grade"]] = grade

    # Use the header_row from sheet2 for column mapping
    header_row_sheet2 = sheet2.row_values(1)
    column_mapping_sheet2 = {header: index for index, header in enumerate(header_row_sheet2)}
    new_row_sheet2 = [""] * len(header_row_sheet2)
    new_row_sheet2[column_mapping_sheet2["Model"]] = shoe_name
    new_row_sheet2[column_mapping_sheet2["Sku"]] = sku
    new_row_sheet2[column_mapping_sheet2["Capacity"]] = add_size
    new_row_sheet2[column_mapping_sheet2["Manufacturer"]] = manufacturer
    new_row_sheet2[column_mapping_sheet2["Damages"]] = damages
    new_row_sheet2[column_mapping_sheet2["Grade"]] = grade

    # Insert rows into both sheets
    sheet1.insert_rows([new_row_sheet1], last_row_index_sheet1 + 1)
    sheet2.insert_rows([new_row_sheet2], last_row_index_sheet2 + 1)

    return {"message": "New size added"}


@app.post("/add-sku")
async def add_sku(
    shoe_name: str,
    add_sku: typing.Optional[str] = Query(None, title="SKU"),
    complete: typing.Optional[str] = Query(None, title="Complete"),
    cur_source: typing.Optional[str] = Query(None, title="Source"),
    cur_seller: typing.Optional[str] = Query(None, title="Seller"),
    cur_note: typing.Optional[str] = Query(None, title="Note"),
    date: typing.Optional[str] = Query(None, title="Date"),
    manufacturer: typing.Optional[str] = Query(None, title="Optional: Manufacturer"),
    price_paid: typing.Optional[str] = Query(None, title="Price Paid"),
    damages: typing.Optional[str] = Query(None, title="Damages"),
    grade: typing.Optional[str] = Query(None, title="Grade")
):
    add_sku = sku_to_string(add_sku)

    all_records_sheet1 = sheet1.get_all_records()
    all_records_sheet2 = sheet2.get_all_records()

    last_row_index_sheet1 = None
    last_row_index_sheet2 = None

    # Find the last row index in sheet1
    for index, row in enumerate(all_records_sheet1, start=2):
        if row.get("Model") == shoe_name:
            last_row_index_sheet1 = index

    # Find the last row index in sheet2
    for index, row in enumerate(all_records_sheet2, start=2):
        # Adjust the condition according to your sheet2 structure
        if row.get("Model") == shoe_name:
            last_row_index_sheet2 = index

    # Use the header_row from sheet1 for column mapping
    header_row_sheet1 = sheet1.row_values(1)
    column_mapping_sheet1 = {header: index for index, header in enumerate(header_row_sheet1)}
    new_row_sheet1 = [""] * len(header_row_sheet1)
    new_row_sheet1[column_mapping_sheet1["Model"]] = shoe_name
    new_row_sheet1[column_mapping_sheet1["Sku"]] = add_sku
    new_row_sheet1[column_mapping_sheet1["Complete"]] = complete
    new_row_sheet1[column_mapping_sheet1["Source"]] = cur_source
    new_row_sheet1[column_mapping_sheet1["Seller"]] = cur_seller
    new_row_sheet1[column_mapping_sheet1["Notes"]] = cur_note
    new_row_sheet1[column_mapping_sheet1["Manufacturer"]] = manufacturer
    new_row_sheet1[column_mapping_sheet1["Price Paid"]] = price_paid
    new_row_sheet1[column_mapping_sheet1["Damages"]] = damages
    new_row_sheet1[column_mapping_sheet1["Grade"]] = grade

    # Use the header_row from sheet2 for column mapping
    header_row_sheet2 = sheet2.row_values(1)
    column_mapping_sheet2 = {header: index for index, header in enumerate(header_row_sheet2)}
    new_row_sheet2 = [""] * len(header_row_sheet2)
    new_row_sheet2[column_mapping_sheet2["Model"]] = shoe_name
    new_row_sheet2[column_mapping_sheet2["Sku"]] = add_sku
    new_row_sheet2[column_mapping_sheet2["Manufacturer"]] = manufacturer
    new_row_sheet2[column_mapping_sheet2["Damages"]] = damages
    new_row_sheet2[column_mapping_sheet2["Grade"]] = grade

    # Insert rows into both sheets
    sheet1.insert_rows([new_row_sheet1], last_row_index_sheet1 + 1)
    sheet2.insert_rows([new_row_sheet2], last_row_index_sheet2 + 1)

    return {"message": "New SKU added"}

