from flask import Flask

app=Flask(__name__)

@app.get('/')
def Fetch():
    return 'Get  Route'