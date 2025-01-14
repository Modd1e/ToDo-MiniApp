import json
import os
import dotenv
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from datetime import datetime, date

from bot.database.engine import session_maker
from bot.database.queries.user import create_user, delete_user_by_id, get_user_by_game_username, get_user_by_id, get_users, update_user
from bot.database.queries.banner import orm_add_banner, orm_get_banners, orm_delete_banner, orm_update_banner, orm_get_banner
from bot.database.queries.event import get_event, get_events, update_event, delete_event, create_event
from bot.database.queries.role import get_role, get_role_by_title, get_roles, create_role, delete_role, update_role

dotenv.load_dotenv()

SHEETS_TO_DB = {
    "Banners": {
        "range": "A2:E",
        "get": orm_get_banner,
        "gets": orm_get_banners,
        "add": orm_add_banner,
        "update": orm_update_banner,
        "delete": orm_delete_banner,
        "fields": ["id", "title", "image", "callback_answer", "description"],
    },
    "Events": {
        "range": "A2:H",
        "get": get_event,
        "gets": get_events,
        "add": create_event,
        "update": update_event,
        "delete": delete_event,
        "fields": ["id", "title", "description", "image", "event_datetime", "is_active"] # "user_target", "role_target"
    },
    "Roles": {
        "range": "A2:K",
        "get": get_role,
        "gets": get_roles,
        "add": create_role,
        "update": update_role,
        "delete": delete_role,
        "fields": [
            "id", 
            "title", 
            "name", 
            "can_use_default_func", 
            "can_confirm_guests", 
            "can_manage_debts", 
            "can_change_role", 
            "can_ban_and_unban_users", 
            "can_spam",
            "can_sync_db",
            "can_confirm_events"
        ]
    }
}


DB_TO_SHEET = {
    "Users": {
        "range": "A2:H",
        "get": get_user_by_id,
        "gets": get_users,
        "add": create_user,
        "update": update_user,
        "delete": delete_user_by_id,
        "fields": ["id", "tg_id", "game_username", "username", "firstname", "lastname", "role", "is_baned"]
    }
}


async def get_google_sheets_data(sheet_title: str, sheet_range: str):
    with open(os.getenv("GOOGLE_SHEET_CREDS_PATH"), "r") as file:
        creds_data = json.load(file)
    
    creds = ServiceAccountCreds(scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"], **creds_data)
    
    async with Aiogoogle(service_account_creds=creds) as aiogoogle:
        sheets_api = await aiogoogle.discover("sheets", "v4")
        range_name = f"{sheet_title}!{sheet_range}"
        response = await aiogoogle.as_service_account(
            sheets_api.spreadsheets.values.get(spreadsheetId=os.getenv("GOOGLE_SHEET_ID"), range=range_name)
        )
        return response["values"]


async def sync_sheet_to_db(session: AsyncSession):
    for sheet_title, config in SHEETS_TO_DB.items():
        data = await get_google_sheets_data(sheet_title, config["range"])
        google_sheet_ids = set()

        for row in data:
            if len(row) < len(config["fields"]):
                row.extend([""] * (len(config["fields"]) - len(row)))
            field_data = dict(zip(config["fields"], row))

            for key, value in field_data.items():
                if key == "event_datetime":
                    field_data[key] = datetime.strptime(value, "%d.%m.%Y %H:%M")
                if value == "TRUE":
                    field_data[key] = True
                if value == "FALSE":
                    field_data[key] = False

            id = field_data.pop("id")
            google_sheet_ids.add(id)

            if not id:
                continue
            
            item = await config["get"](session, int(id))
            if item:
                await config["update"](session, int(id), field_data)
            else:
                await config["add"](session, field_data)


        db_items = await config["gets"](session)
        for db_item in db_items:
            if str(db_item.id) not in google_sheet_ids:
                await config["delete"](session, db_item.id)


async def sync_db_to_sheet(session: AsyncSession):
    users = await get_users(session)
    data_to_write = [[getattr(user, field) for field in DB_TO_SHEET["Users"]["fields"]] for user in users]
    db_ids = {str(user.id) for user in users}

    try:
        with open(os.getenv("GOOGLE_SHEET_CREDS_PATH"), "r") as file:
            creds_data = json.load(file)

        creds = ServiceAccountCreds(scopes=["https://www.googleapis.com/auth/spreadsheets"], **creds_data)
        
        async with Aiogoogle(service_account_creds=creds) as aiogoogle:
            sheets_api = await aiogoogle.discover("sheets", "v4")
            range_name = f'Users!{DB_TO_SHEET["Users"]["range"]}'

            sheet_data_response = await aiogoogle.as_service_account(
                sheets_api.spreadsheets.values.get(
                    spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
                    range=range_name
                )
            )
            sheet_data = sheet_data_response.get("values", [])
            
            sheet_ids = set(row[0] for row in sheet_data if row)
            data_to_update = []
            
            for user_data in data_to_write:
                user_id = str(user_data[0])
                if user_id not in sheet_ids:
                    data_to_update.append(user_data)
                else:
                    sheet_row = next((row for row in sheet_data if row[0] == user_id), None)
                    if sheet_row and sheet_row != user_data:
                        data_to_update.append(user_data)
                        
            if data_to_update:
                await aiogoogle.as_service_account(
                    sheets_api.spreadsheets.values.update(
                        spreadsheetId=os.getenv("GOOGLE_SHEET_ID"),
                        range=range_name,
                        valueInputOption="USER_ENTERED",
                        json={"values": data_to_update}
                    )
                )
    except Exception as e:
        logging.error(f"Failed to sync data to Google Sheets: {e}")



async def sync_data():
    async with session_maker() as session:
        await sync_sheet_to_db(session)
        await sync_db_to_sheet(session)
    logging.info("Data synchronized.")
