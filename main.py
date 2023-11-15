from fastapi import FastAPI, Query
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import typing

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
    cost: typing.Optional[str] = Query(None, title="Optional: Cost"),
    new_condition: typing.Optional[str] = Query(None, title="Optional: New Condition"),
    status: typing.Optional[str] = Query(None, title="Optional: Status"),
    listed: typing.Optional[str] = Query(None, title="Optional: Listed"),
    source: typing.Optional[str] = Query(None, title="Optional: Source"),
    seller: typing.Optional[str] = Query(None, title="Optional: Seller"),
    new_manufacturer: typing.Optional[str] = Query(None, title="Optional: Manufacturer"),
    note: typing.Optional[str] = Query(None, title="Optional: Note"),
    new_damages: typing.Optional[str] = Query(None, title="Optional: New Damages"),
    new_code: typing.Optional[str] = Query(None, title="Optional: New Code"),
    delete: typing.Optional[bool] = Query(False, title="Optional: Delete")
):

    sku = sku_to_string(sku)

    rows_to_update_sheet1 = []
    rows_to_update_sheet2 = []

    all_records_sheet1 = sheet1.get_all_records()
    all_records_sheet2 = sheet2.get_all_records()

    for index, row in enumerate(all_records_sheet1, start=2):
        if row.get("Model") == shoe_name:
            if size:
                if row.get("Capacity"):
                    size_from_sheets = size_to_string(row.get("Capacity"))
                    if size != size_from_sheets:
                        continue
                else:
                    continue

            if sku:
                if row.get("Sku"):
                    sku_from_sheets = sku_to_string(row.get("Sku"))
                    if sku != sku_from_sheets:
                        continue
                else:
                    continue

            rows_to_update_sheet1.append((index, row))

    for index, row in enumerate(all_records_sheet2, start=2):
        # Similar logic for filtering rows in sheet2 based on shoe_name and sku
        if row.get("Model") == shoe_name:

            if sku:
                if row.get("Sku"):
                    sku_from_sheets = sku_to_string(row.get("Sku"))
                    if sku != sku_from_sheets:
                        continue
                else:
                    continue

            rows_to_update_sheet2.append((index, row))

    if delete:
        rows_to_delete_sheet1 = []
        rows_to_delete_sheet2 = []

        if size:
            rows_to_delete_sheet1 = [index for index, row in enumerate(all_records_sheet1, start=2)
                                      if sku_to_string(row.get("Sku")) == sku and size_to_string(row.get("Capacity")) == size]
            rows_to_delete_sheet2 = [index for index, row in enumerate(all_records_sheet2, start=2)
                                      if sku_to_string(row.get("Sku")) == sku]
        else:
            rows_to_delete_sheet1 = [index for index, row in enumerate(all_records_sheet1, start=2)
                                      if sku_to_string(row.get("Sku")) == sku]
            rows_to_delete_sheet2 = [index for index, row in enumerate(all_records_sheet2, start=2)
                                      if sku_to_string(row.get("Sku")) == sku]

        if not rows_to_delete_sheet1 and not rows_to_delete_sheet2:
            return {"message": "No rows found for deletion"}

        # Deleting rows from sheet1
        rows_to_delete_sheet1.sort(reverse=True)
        for index in rows_to_delete_sheet1:
            sheet1.delete_rows(index)

        # Deleting rows from sheet2
        rows_to_delete_sheet2.sort(reverse=True)
        for index in rows_to_delete_sheet2:
            sheet2.delete_rows(index)

        return {"message": f"{len(rows_to_delete_sheet1) + len(rows_to_delete_sheet2)} rows deleted"}

    if not rows_to_update_sheet1 and not rows_to_update_sheet2:
        return {"message": "Name and SKU combination not found"}

    for index, row in rows_to_update_sheet1:
        # Update logic for sheet1
        if new_size is not None and "Capacity" in row:
            row["Capacity"] = new_size
        if new_shoe_name is not None:
            row["Model"] = new_shoe_name
        if new_sku is not None:
            row["Sku"] = sku_to_string(new_sku)
        if new_price_paid is not None and "Price Paid" in row:
            row["Price Paid"] = new_price_paid
        if new_quantity is not None and "Quantity" in row:
            row["Quantity"] = new_quantity
        if new_condition is not None and "Grade" in row:
            row["Grade"] = new_condition
        if new_list_price is not None and "List Price" in row:
            row["List Price"] = new_list_price
        if cost is not None and "Cost" in row:
            row["Cost"] = cost
        if status is not None and "Status" in row:
            row["Status"] = status
        if listed is not None and "Listed" in row:
            row["Listed"] = listed
        if source is not None and "Source" in row:
            row["Source"] = source
        if new_manufacturer is not None and "Manufacturer" in row:
            row["Manufacturer"] = new_manufacturer
        if seller is not None and "Seller" in row:
            row["Seller"] = seller
        if note is not None and "Notes" in row:
            row["Notes"] = note
        if new_damages is not None and "Damages" in row:
            row["Damages"] = new_damages
        if new_code is not None and "Code" in row:
            row["Code"] = new_code

        # Calculate the range for the specific row in the first sheet
        range_start_sheet1 = f"A{index}"
        range_end_sheet1 = chr(ord("A") + len(row) - 1) + str(index)
        sheet1.update(range_start_sheet1 + ":" + range_end_sheet1, [list(row.values())], value_input_option="RAW")

    for index, row in rows_to_update_sheet2:
        # Update logic for sheet2
        if new_shoe_name is not None:
            row["Model"] = new_shoe_name
        if new_sku is not None:
            row["Sku"] = sku_to_string(new_sku)
        if new_price_paid is not None:
            row["Price Paid"] = new_price_paid
        if new_quantity is not None:
            row["Quantity"] = new_quantity
        if new_condition is not None:
            row["Grade"] = new_condition
        if new_list_price is not None:
            row["List Price"] = new_list_price
        if new_manufacturer is not None:
            row["Manufacturer"] = new_manufacturer
        if new_damages is not None:
            row["Damages"] = new_damages
        if new_code is not None:
            row["Code"] = new_code

        # Calculate the range for the specific row in the second sheet
        range_start_sheet2 = f"A{index}"
        range_end_sheet2 = chr(ord("A") + len(row) - 1) + str(index)
        sheet2.update(range_start_sheet2 + ":" + range_end_sheet2, [list(row.values())], value_input_option="RAW")

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
    code: typing.Optional[str] = Query(None, title="Code"),
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
    new_row_sheet2[column_mapping_sheet2["Manufacturer"]] = manufacturer
    new_row_sheet2[column_mapping_sheet2["Damages"]] = damages
    new_row_sheet2[column_mapping_sheet2["Code"]] = code
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
    cost: typing.Optional[str] = Query(None, title="Cost"),
    damages: typing.Optional[str] = Query(None, title="Damages"),
    code: typing.Optional[str] = Query(None, title="Code"),
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
    new_row_sheet1[column_mapping_sheet1["Price Paid"]] = cost
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
    new_row_sheet2[column_mapping_sheet2["Code"]] = code
    new_row_sheet2[column_mapping_sheet2["Grade"]] = grade

    # Insert rows into both sheets
    sheet1.insert_rows([new_row_sheet1], last_row_index_sheet1 + 1)
    sheet2.insert_rows([new_row_sheet2], last_row_index_sheet2 + 1)

    return {"message": "New SKU added"}

