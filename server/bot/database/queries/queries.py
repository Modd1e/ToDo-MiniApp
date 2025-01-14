# from sqlalchemy import select, update, delete
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.exc import SQLAlchemyError
# import logging

# from bot.database.queries.role import create_role, get_role, get_roles, update_role, delete

# from bot.database.models import UserRole, Role

# logging.basicConfig(level=logging.INFO)

# async def create_user_role(session: AsyncSession, data: dict):
#     try:
#         user_role = UserRole(
#             user_id=user_id,
#             role_id=role_id
#         )
#         session.add(user_role)
#         await session.commit()
#         logging.info(f"Create user_role successful: {user_role}")
#         return user_role
#     except SQLAlchemyError as e:
#         logging.error(f"Create user_role error: {e}")
#         await session.rollback()
#         return False
