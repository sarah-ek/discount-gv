## discount-gv
/r/badmathematics archive bot. Named in honor of its predecessor, Godel's Vortex.

Requires `python 3.7` and the following packages:  
 - `praw`
 - `markdown`
 - `lxml`
 - `archivenow`


`identifiers.csv` should be in the same directory as `main.py`, and should have the following format
```
client_id,$CLIENT_ID
client_secret,$CLIENT_SECRET
user_agent,'archive'
username,$USERNAME
password,$PASSWORD
```
