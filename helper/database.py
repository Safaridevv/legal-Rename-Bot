import motor.motor_asyncio
from config import Config
from .utils import send_log

class Database:
    default_verify = {
        'is_verified': False,
        'verified_time': 0,
        'verify_token': "",
        'link': ""
    }
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.user

    def new_user(self, id):
        return dict(
            _id=int(id),                                   
            file_id=None,
            caption=None, 
            verify_status=self.default_verify
        )

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            await self.col.insert_one(user)            
            await send_log(b, u)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'_id': int(user_id)})
    
    async def set_thumbnail(self, id, file_id):
        await self.col.update_one({'_id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('file_id', None)

    async def set_caption(self, id, caption):
        await self.col.update_one({'_id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('caption', None)
        
    async def get_verify_status(self, user_id):
        user = await self.col.find_one({'_id':int(user_id)})
        if user:
            return user.get('verify_status', self.default_verify)
        return self.default_verify
        
    async def update_verify_status(self, user_id, verify):
        await self.col.update_one({'_id': int(user_id)}, {'$set': {'verify_status': verify}})


db = Database(Config.DB_URL, Config.DB_NAME)




