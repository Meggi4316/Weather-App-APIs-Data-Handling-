from flask import Flask, render_template, request
import json, os, random

folderPath = os.path.dirname(os.path.abspath(__file__))

with open(folderPath + '/pokedex.json', 'r',  encoding="utf8") as f:
    pokedex = json.load(f)
app = Flask(__name__)
 
menu = ["Burgers", "Chips", "Drink"]

@app.route('/')
def test():
    return render_template("index.html", user = os.getlogin(), array = menu)

@app.route("/pokemon",  methods=["GET", "POST"])
def pokemon():
    if request.method == "POST":
        i = int( request.form["id"]) -1
        if i > len(pokedex) or i <= 0:
            i = 0
        return render_template("pokemon.html", pok = pokedex[i])
    else:

        i = random.randint(0, len(pokedex)-1)
        return render_template("pokemon.html", pok = pokedex[i])

@app.route("/<t>")
def type(t):
    type = []
    for p in pokedex[0:151]:
        if t.capitalize() in p["type"]:
            type.append(p)
    return render_template("manyPokemon.html", pokemon = type)


if __name__ == '__main__':
    app.run(debug = True)
