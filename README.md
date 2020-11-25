# Python iMonke API Wrapper
A simple python API wrapper for iMonke that I've started working on.

This is far from finished, it's just a couple hours of me messing around with it.

# Quick Start
## No sign-in
```py
imonke = iMonke()

feed = imonke.collective()

post = next(feed)

print(post.link)
```
## Sign-in
```py
import asyncio

client = iMonkeClient('Email@email.com', 'Password1234')

my_meme = asyncio.run(client.post("C:/Users/MyName/Desktop/Memes/my_meme.jpg")

print(my_meme.link)
```
