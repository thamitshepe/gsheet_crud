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

    rows_to_update = []

    all_records = sheet1.get_all_records()
    for index, row in enumerate(all_records, start=2):
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

            rows_to_update.append((index, row))

    if delete:
        rows_to_delete = []
        if size:
            rows_to_delete = [index for index, row in enumerate(all_records, start=2)
                              if sku_to_string(row.get("Sku")) == sku and size_to_string(row.get("Capacity")) == size]
        else:
            rows_to_delete = [index for index, row in enumerate(all_records, start=2)
                              if sku_to_string(row.get("Sku")) == sku]

        if not rows_to_delete:
            return {"message": "No rows found for deletion"}

        rows_to_delete.sort(reverse=True)

        for index in rows_to_delete:
            sheet1.delete_rows(index)

        return {"message": f"{len(rows_to_delete)} rows deleted"}

    if not rows_to_update:
        return {"message": "Name, SKU, and Size combination not found"}

    for index, row in rows_to_update:
        if new_size is not None:
            row["Capacity"] = new_size
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
        if cost is not None:
            row["Cost"] = cost
        if status is not None:
            row["Status"] = status
        if listed is not None:
            row["Listed"] = listed
        if source is not None:
            row["Source"] = source
        if new_manufacturer is not None:
            row["Manufacturer"] = new_manufacturer
        if seller is not None:
            row["Seller"] = seller
        if note is not None:
            row["Notes"] = note
        if new_damages is not None:
            row["Damages"] = new_damages
        if new_code is not None:
            row["Code"] = new_code

        update_row(sheet1, index, row)
        update_row(sheet2, index, row)

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
    code: typing.Optional[str] = Query(None, title="Code")
):
    sku = sku_to_string(sku)
    add_size = size_to_string(add_size)

    all_records = sheet1.get_all_records()
    last_row_index = None

    for index, row in enumerate(all_records, start=2):
        if sku_to_string(row.get("Sku")) == sku:
            last_row_index = index

    if last_row_index is not None:
        header_row = sheet1.row_values(1)
        column_mapping = {header: index for index, header in enumerate(header_row)}
        new_row = [""] * len(header_row)
        new_row[column_mapping["Model"]] = shoe_name
        new_row[column_mapping["Sku"]] = sku
        new_row[column_mapping["Capacity"]] = add_size
        new_row[column_mapping["Complete"]] = complete
        new_row[column_mapping["Source"]] = cur_source
        new_row[column_mapping["Seller"]] = cur_seller
        new_row[column_mapping["Notes"]] = cur_note
        new_row[column_mapping["Manufacturer"]] = manufacturer
        new_row[column_mapping["Price Paid"]] = price_paid
        new_row[column_mapping["Damages"]] = damages
        new_row[column_mapping["Code"]] = code

        sheet1.insert_rows([new_row], last_row_index + 1)
        sheet2.insert_rows([new_row], last_row_index + 1)

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
    manufacturer: typing.Optional[str] = Query(None, title="Optional: Manufacturer"),
    cost: typing.Optional[str] = Query(None, title="Cost"),
    damages: typing.Optional[str] = Query(None, title="Damages"),
    code: typing.Optional[str] = Query(None, title="Code")
):
    add_sku = sku_to_string(add_sku)

    all_records = sheet1.get_all_records()
    last_row_index = None

    for index, row in enumerate(all_records, start=2):
        if row.get("Model") == shoe_name:
            last_row_index = index

    if last_row_index is not None:
        header_row = sheet1.row_values(1)
        column_mapping = {header: index for index, header in enumerate(header_row)}
        new_row = [""] * len(header_row)
        new_row[column_mapping["Model"]] = shoe_name
        new_row[column_mapping["Sku"]] = add_sku
        new_row[column_mapping["Complete"]] = complete
        new_row[column_mapping["Source"]] = cur_source
        new_row[column_mapping["Seller"]] = cur_seller
        new_row[column_mapping["Notes"]] = cur_note
        new_row[column_mapping["Manufacturer"]] = manufacturer
        new_row[column_mapping["Price Paid"]] = cost
        new_row[column_mapping["Damages"]] = damages
        new_row[column_mapping["Code"]] = code

        sheet1.insert_rows([new_row], last_row_index + 1)
        sheet2.insert_rows([new_row], last_row_index + 1)

        return {"message": "New SKU added"}
    else:
        return {"message": "No rows found for the specified Shoe"}
