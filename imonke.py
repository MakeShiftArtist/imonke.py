import requests as req
from datetime import datetime
import json
import asyncio
class _format:
    @staticmethod
    def ordinal(num) -> str:
        """
        Returns ordinal number string from int, e.g. 1, 2, 3 becomes 1st, 2nd, 3rd, etc.
        """
        n = int(num)
        if 4 <= n <= 20:
          suffix = 'th'
        elif (n % 10) == 1:
          suffix = 'st'
        elif (n % 10) == 2:
          suffix = 'nd'
        elif (n % 10) == 3:
          suffix = 'rd'
        elif n < 100:
          suffix = 'th'
        ord_num = str(n) + suffix
        return ord_num
    @staticmethod
    def get_full_date(time=None) -> str:
        if time is None:
            time = datetime.now()
        start = time.strftime('%A, %B')
        day = _format.ordinal(int(time.strftime('%d')))
        end = time.strftime('%Y %H:%M %p')
        return  f"{start} {day}, {end}"


class _objects:
    class User:
        """ The general user object. You pass the user json """
        def __init__(self, user):
            self.nick = user['nick']
            self.id = user['id']
            bio = user['bio']
            if bio == '':
                bio = None
            self.bio = bio
            self.post_count = user['post_count']
            self.subscriber_count = user['subscriber_count']
            self.subscription_count = user['subscription_count']
            self.admin = user['admin']
            self.moderator = user['moderator']
            self.powers = {'admin': self.admin, 'moderator': self.moderator} # This is completely unnecessary because we have self.admin and self.moderator but the idea was to list what they can do and can't do, when the moderation is set up.

    class Post:
        """ General Post object. You pass the post json """
        def __init__(self, post):
            self.id = post['id']
            self.all = post # this is to see all the fields from the post json
            find = FindUser()
            self.author = asyncio.run(find._id(post['author'])) # post['author'] only give the id of the user, so this generates the full user object.
            self.mime = post['mime']
            self.link = post['file_url']
            self.tags = post['tags']
            self.like_count = post['like_count']
            self.dislike_count = post['dislike_count']
            self.repub_count = post['repub_count']
            self.view_count = post['view_count']
            self.comment_count = post['comment_count']
            unix = post['created']
            time = datetime.utcfromtimestamp(unix)
            self.created_at = _format.get_full_date(time) # You can remove the function to just get the datetime as a UTC int.
            self.is_featured = post['featured']
            self.featurable = post['featurable']
            self.is_removed = post['removed']
            self.is_nsfw = post['nsfw']

class FindUser:
    """ Classes for finding a user """
    def __init__(self):
        self.api = 'http://imonke.gastrodon.io/user'
        self.id_endpoint = self.api + "/id/"
        self.nick_endpoint = self.api + "/nick/"

    async def _id(self, id:str=None) -> _objects.User or Exception:
        if id is None:
            raise Exception("You need an ID to get the user")
        response =  req.get(f"{self.id_endpoint}{id}")
        json = response.json()
        if response.ok:
            user = json['user']
            return _objects.User(user)
        else:
            raise ValueError(f"{json['error']}: {id}") # Raises the error with the id

    async def nick(self, username:str=None) -> _objects.User or Exception:
        if username is None:
            raise Exception("You need a username to get the user")
        response =  req.get(f"{self.nick_endpoint}{username}")
        json = response.json()
        if response.ok:
            user = json['user']
            return _objects.User(user)
        else:
            raise ValueError(f"{json['error']}: {username}") # Raises the error with the nickname

class Check:

    def __init__(self):
        self.api = 'http://imonke.gastrodon.io/check'
        self.email_end = self.api + "/email/"
        self.nick_end = self.api + "/nick/"

    def nick(self, username:str=None)-> bool:
        if username is None:
            raise Exception("You need a username to check for")
        else:
            response =  req.get(f"{self.nick_end}{username}")
            json = response.json()
            return json['exists']

    def email(self, email:str=None) -> bool:
        if email is None:
            raise Exception("You need a userID to search for")
        else:
            response =  req.get(f"{self.email_end}{email}")
            json = response.json()
            return json['exists']


class iMonkeClient:
    """ Generates the iMonke Client. """
    def __init__(self, email=None, password=None):
        self.api = 'http://imonke.gastrodon.io'
        self.auth_endpoint = self.api + '/auth/'
        self.post_endpoint = self.api + '/content/'

        data = req.post(self.auth_endpoint, data=json.dumps({'email': email, 'password': password}))
        data = data.json()
        self.email = email
        self.secret = data['auth']['secret']
        self.token = data['auth']['token']
        self.headers = {'token': self.token}
        time = datetime.utcfromtimestamp(data['auth']['expires'])
        self.expires = _format.get_full_date(time)


    async def post(self, image_dir, mime:str="image/png", nsfw:bool=False, featurable:bool=True, tags:list=[]) -> _objects.Post or Exception:
        """Examples:
            You need to initialize iMonkeClient with the correct account login information to post

        >>> client = iMonkeClient("email@email.com", "password123!")
        >>> post = await client.post(image_dir="C:/Users/MyName/Desktop/Memes/my_meme.jpg", mime="image/jpeg", nsfw=True, tags=["Funny", "Coder", "NSFW"])
        >>> print(post.like_count)
        0

        """
        tags = list(set(tags))
        if tags == []:
            all_tags = 'null'
        else:
            all_tags = "[\n"
            for tag in tags:
                if tag == tags[-1]:
                    all_tags += f"\"{tag}\"]"
                else:
                    all_tags += f"\"{tag}\",\n"

        if nsfw:
            nsfw = 'true'
        else:
            nsfw = 'false'
        if featurable:
            feat = 'true'
        else:
            feat = 'false'

        # You can change featurable
        payload = {'json': f'{{"mime": "{mime}", "nsfw": {nsfw}, "featurable": {feat}, "tags": {all_tags}}}'}

        auth = f"Bearer {self.token}"
        headers = {
        'Authorization': auth
        }
        files = [('file', open(image_dir, 'rb'))]
        data = req.request("POST", self.post_endpoint, headers=headers, data=payload, files=files)

        json = data.json()
        return _objects.Post(json['content'])

    async def generate_token(self) -> None:
        """ This will regenerate a token if the token has expired """
        data = req.post(self.auth_endpoint, data=json.dumps({'email': self.email, 'secret': self.secret}))
        self.token = data['auth']['token']
        self.headers = {'token': self.token}
        time = datetime.utcfromtimestamp(data['auth']['expires'])
        self.expires = _format.get_full_date(time)

class iMonke:
    def __init__(self):
        self.api = 'http://imonke.gastrodon.io'
        self.check = Check()
        self.user = FindUser()

    async def is_username_taken(self, username:str=None) -> bool:
        return not self.check.nick(username)

    async def is_email_taken(self, email:str=None) -> bool:
        return not self.check.email(email)

    async def user_by_id(self, id:str=None) -> _objects.User or None :
        return await self.user._id(id)

    async def user_by_nick(self, username:str=None) -> _objects.User or None:
        return await self.user.nick(username)

    def collective(self) -> _objects.Post:
        """ Generator for every post in the feed """
        response = req.get(f"{self.api}/feed/all")
        if response.ok:
            json = response.json()
            all_posts = json['content']
            for post in all_posts:
                yield _objects.Post(post)
