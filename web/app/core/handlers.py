from app.db.db import GardensLogs, Gardens, User
import ormar


async def upload_garden_data(garden_data):
    try:
        await Gardens.objects.get(id=int(garden_data.garden_id))
    except ormar.NoMatch:
        return False, "A garden with such an identifier does not exist."

    if not garden_data.data:
        return False, "The data field cannot be empty."

    if garden_data:
        await GardensLogs.objects.create(
            garden_id=garden_data.garden_id,
            data=garden_data.data,
        )
        return True, ""
    else:
        return False, "Data recording error"


async def get_garden_data(garden_id):
    try:
        result = (
            await GardensLogs.objects.order_by("-id").filter(garden_id=garden_id).all()
        )
        return result[0]
    except ormar.NoMatch:
        return None


async def get_user(email: str):
    try:
        user = await User.objects.get(email=email)
        return user
    except ormar.NoMatch:
        return None


async def check_garden(garden_id: int):
    try:
        garden = await Gardens.objects.get(id=int(garden_id))
        return garden
    except ormar.NoMatch:
        return None
