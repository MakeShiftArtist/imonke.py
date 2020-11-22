# Python iMonke API Wrapper
A simple python API wrapper for iMonke that I've started working on.

This is far from finished, it's just a couple hours of me messing around with it.

# Quick Start
```py
imonke = iMonke()

for post in imonke.collective():
  print(post.link)
  print(post.author.nick)
  break
  
client = iMonkeClient('Email@email.com', 'Password1234')
# I haven't actually added any client features
```
