#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect, flash, session, g
import pymysql.cursors

app = Flask(__name__)
app.secret_key = 'une cle(token) : grain de sel(any random string)'


def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host="localhost",  # à modifier
            user="valou",  # à modifier
            password="1301",  # à modifier
            database="projet",  # à modifier
            charset='utf8mb4',
            port=3307,
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route('/')
@app.route('/produit/show')
def show_produits():
    mycursor = get_db().cursor()
    sql = ''' SELECT id_produit AS id, libelle_produit AS libelle, prix_produit AS prix, categorie_id \
    FROM produit
    ORDER BY id_produit;'''
    mycursor.execute(sql)
    liste_produits = mycursor.fetchall()
    return render_template('produit/show_produit.html', produits=liste_produits)


@app.route('/produit/add', methods=['GET'])
def add_produit():
    print('''affichage du formulaire pour saisir un produit''')
    return render_template('produit/add_produit.html')

@app.route('/produit/delete')
def delete_produit():
    print('''suppression d'un produit''')
    id=request.args.get('id',0)
    print(id)
    mycursor = get_db().cursor()
    tuple_param=(id)
    sql="DELETE FROM produit WHERE id_produit=%s;"
    mycursor.execute(sql,tuple_param)

    get_db().commit()
    print(request.args)
    print(request.args.get('id'))
    id = request.args.get('id', 0)
    return redirect('/produit/show')

@app.route('/produit/edit', methods=['GET'])
def edit_produit():
    print('''affichage du formulaire pour modifier un produit''')
    print(request.args)
    print(request.args.get('id'))
    id=request.args.get('id')
    mycursor = get_db().cursor()
    sql=''' SELECT id_produit AS id, libelle_produit AS libelle, prix_produit AS prix, categorie_id
    FROM produit
    WHERE id_produit=%s;'''
    tuple_param=(id)
    mycursor.execute(sql,tuple_param)
    produit = mycursor.fetchone()
    return render_template('produit/edit_produit.html', produit=produit)


@app.route('/produit/add', methods=['POST'])
def valid_add_produit():
    print('''ajout du produit dans le tableau''')
    libelle = request.form.get('libelle')
    prix = request.form.get('prix')
    categorie_id = request.form.get('categorie_id')
    message = 'libelle :' + libelle + ' - prix :' + prix + ' - categorie :' + categorie_id
    print(message)
    mycursor = get_db().cursor()
    tuple_param=(libelle, prix, categorie_id)
    sql="INSERT INTO produit(id_produit, libelle_produit, prix_produit, categorie_id) VALUES (NULL, %s, %s, %s);"
    mycursor.execute(sql,tuple_param)
    get_db().commit()
    return redirect('/produit/show')

@app.route('/produit/edit', methods=['POST'])
def valid_edit_produit():
    print('''modification du produit dans le tableau''')
    id = request.form.get('id')
    libelle = request.form.get('libelle')
    prix = request.form.get('prix')
    categorie_id = request.form.get('categorie_id')
    message = 'libelle :' + libelle + ' - prix :' + prix + ' pour le produit d identifiant :' + id
    print(message)
    mycursor = get_db().cursor()
    tuple_param=(libelle, prix, categorie_id, id)
    sql="UPDATE produit SET libelle_produit = %s, prix_produit = %s, categorie_id = %s WHERE id_produit=%s;"
    mycursor.execute(sql,tuple_param)
    get_db().commit()
    return redirect('/produit/show')

if __name__ == '__main__':
    app.run(debug=True, port=5000)