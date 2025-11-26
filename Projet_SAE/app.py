#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect, flash, url_for, g

import pymysql.cursors

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'une cle(token) : grain de sel(any random string)'

# mysql --user=??? --password=??? --host=ASUSVAL.local --database=sae_mon_potager

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host="???",
            user="???",
            password="???",
            database="sae_mon_potager",
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


############### ACCUEIL ###############

@app.route('/')
def show_accueil():
    return render_template('index.html')


############### SIGNALEMENT ###############

############### SIGNALEMENT — SHOW ###############

@app.route('/signalement/show')
def show_signalement():
    mycursor = get_db().cursor()
    sql = '''
    SELECT s.id_signalement AS id,
           s.descriptif,
           s.photo,
           s.date_signalement,
           ts.libelle_type_signalement AS type_signalement,
           a.nom AS adherent,
           c.parcelle_id
    FROM signalement s
    JOIN type_signalement ts ON ts.id_type_signalement = s.type_signalement_id
    JOIN adherent a ON a.id_adherent = s.adherent_id
    LEFT JOIN correspond c ON c.signalement_id = s.id_signalement
    ORDER BY s.id_signalement;
    '''
    mycursor.execute(sql)
    signalements = mycursor.fetchall()
    return render_template('signalement/show_signalement.html', signalements=signalements)


############### SIGNALEMENT — ADD ###############

@app.route('/signalement/add', methods=['GET'])
def add_signalement():
    mycursor = get_db().cursor()

    mycursor.execute('SELECT id_type_signalement AS id, libelle_type_signalement AS libelle FROM type_signalement ORDER BY libelle_type_signalement;')
    types = mycursor.fetchall()

    mycursor.execute('SELECT id_adherent AS id, nom FROM adherent ORDER BY nom;')
    adherents = mycursor.fetchall()

    mycursor.execute('SELECT id_parcelle AS id FROM parcelle ORDER BY id_parcelle;')
    parcelles = mycursor.fetchall()

    return render_template('signalement/add_signalement.html', types=types, adherents=adherents, parcelles=parcelles)


@app.route('/signalement/add', methods=['POST'])
def valid_add_signalement():
    descriptif = request.form.get('descriptif')
    photo = request.form.get('photo')
    date_signalement = request.form.get('date_signalement')
    type_signalement_id = request.form.get('type_signalement_id')
    adherent_id = request.form.get('adherent_id')
    parcelle_id = request.form.get('parcelle_id')

    mycursor = get_db().cursor()

    mycursor.execute('SELECT libelle_type_signalement FROM type_signalement WHERE id_type_signalement = %s;',(type_signalement_id,))
    type_label = mycursor.fetchone()['libelle_type_signalement']

    mycursor.execute('SELECT nom FROM adherent WHERE id_adherent = %s;', (adherent_id,))
    adherent_name = mycursor.fetchone()['nom']

    sql = '''
    INSERT INTO signalement (descriptif, photo, date_signalement, type_signalement_id, adherent_id)
    VALUES (%s, %s, %s, %s, %s);
    '''
    mycursor.execute(sql, (descriptif, photo, date_signalement, type_signalement_id, adherent_id))
    signalement_id = mycursor.lastrowid

    mycursor.execute('INSERT INTO correspond (parcelle_id, signalement_id) VALUES (%s, %s);',(parcelle_id, signalement_id))

    get_db().commit()

    message = f"Signalement ajouté | Type: {type_label} | Adhérent: {adherent_name} | Parcelle: {parcelle_id} | Date: {date_signalement}"
    flash(message, 'alert-success')
    return redirect('/signalement/show')


############### SIGNALEMENT — DELETE ###############

@app.route('/signalement/delete', methods=['POST'])
def delete_signalement():
    id = request.form.get('id')

    mycursor = get_db().cursor()
    mycursor.execute('DELETE FROM correspond WHERE signalement_id = %s;', (id,))
    mycursor.execute('DELETE FROM signalement WHERE id_signalement = %s;', (id,))
    get_db().commit()

    flash(f'Signalement supprimé / id : {id}', 'alert-warning')
    return redirect('/signalement/show')


############### SIGNALEMENT — EDIT ###############

@app.route('/signalement/edit', methods=['GET'])
def edit_signalement():
    id = request.args.get('id')

    mycursor = get_db().cursor()

    sql =sql = '''
    SELECT s.id_signalement AS id,
           s.descriptif,
           s.photo,
           s.date_signalement,
           s.type_signalement_id,
           s.adherent_id,
           c.parcelle_id,
           ts.libelle_type_signalement,
           a.nom
    FROM signalement s
    LEFT JOIN correspond c ON c.signalement_id = s.id_signalement
    LEFT JOIN type_signalement ts ON ts.id_type_signalement = s.type_signalement_id
    LEFT JOIN adherent a ON a.id_adherent = s.adherent_id
    WHERE s.id_signalement = %s;
    '''
    mycursor.execute(sql, (id,))
    signalement = mycursor.fetchone()

    mycursor.execute('SELECT id_type_signalement AS id, libelle_type_signalement AS libelle FROM type_signalement;')
    types = mycursor.fetchall()

    mycursor.execute('SELECT id_adherent AS id, nom FROM adherent;')
    adherents = mycursor.fetchall()

    mycursor.execute('SELECT id_parcelle AS id FROM parcelle;')
    parcelles = mycursor.fetchall()

    return render_template('signalement/edit_signalement.html', signalement=signalement, types=types, adherents=adherents, parcelles=parcelles)


@app.route('/signalement/edit', methods=['POST'])
def valid_edit_signalement():
    id = request.form.get('id')
    descriptif = request.form.get('descriptif')
    photo = request.form.get('photo')
    date_signalement = request.form.get('date_signalement')
    type_signalement_id = request.form.get('type_signalement_id')
    adherent_id = request.form.get('adherent_id')
    parcelle_id = request.form.get('parcelle_id')

    mycursor = get_db().cursor()

    mycursor.execute('SELECT libelle_type_signalement FROM type_signalement WHERE id_type_signalement = %s;',(type_signalement_id,))
    type_label = mycursor.fetchone()['libelle_type_signalement']

    mycursor.execute('SELECT nom FROM adherent WHERE id_adherent = %s;', (adherent_id,))
    adherent_name = mycursor.fetchone()['nom']

    sql = '''
    UPDATE signalement
    SET descriptif = %s,
        photo = %s,
        date_signalement = %s,
        type_signalement_id = %s,
        adherent_id = %s
    WHERE id_signalement = %s;
    '''
    mycursor.execute(sql, (descriptif, photo, date_signalement, type_signalement_id, adherent_id, id))

    mycursor.execute('DELETE FROM correspond WHERE signalement_id = %s;', (id,))
    mycursor.execute('INSERT INTO correspond (parcelle_id, signalement_id) VALUES (%s, %s);', (parcelle_id, id))

    get_db().commit()

    message = f"Signalement modifié (ID: {id}) | Type: {type_label} | Adhérent: {adherent_name} | Parcelle: {parcelle_id} | Date: {date_signalement}"
    flash(message, 'alert-success')
    return redirect('/signalement/show')


############### SIGNALEMENT — STATISTIQUES ###############

@app.route('/signalement/calcul')
def calcul_signalement():
    mycursor = get_db().cursor()

    mycursor.execute('''
    SELECT p.id_parcelle AS parcelle_id, COUNT(c.signalement_id) AS nb_signalements
    FROM parcelle p
    LEFT JOIN correspond c ON c.parcelle_id = p.id_parcelle
    GROUP BY p.id_parcelle
    ORDER BY p.id_parcelle;
    ''')
    stats_parcelles = mycursor.fetchall()

    mycursor.execute('''
    SELECT a.nom AS adherent, COUNT(s.id_signalement) AS nb_signalements
    FROM adherent a
    LEFT JOIN signalement s ON s.adherent_id = a.id_adherent
    GROUP BY a.id_adherent
    ORDER BY nb_signalements DESC;
    ''')
    stats_adherents = mycursor.fetchall()

    mycursor.execute('''
    SELECT ts.libelle_type_signalement AS type_signalement, COUNT(s.id_signalement) AS nb_signalements
    FROM signalement s
    JOIN type_signalement ts ON ts.id_type_signalement = s.type_signalement_id
    GROUP BY ts.id_type_signalement
    ORDER BY nb_signalements DESC
    LIMIT 1;
    ''')
    signalement_frequent = mycursor.fetchone()

    return render_template('signalement/calcul_signalement.html', stats_parcelles=stats_parcelles, stats_adherents=stats_adherents, signalement_frequent=signalement_frequent)


############################# PRODUIT #############################

@app.route('/produit/show')
def show_produits():
    mycursor = get_db().cursor()
    sql = ''' SELECT id_produit AS id, libelle_produit AS libelle, prix_produit AS prix, categorie_id, periode_recolte_optimale AS recolte, periode_plantation_optimale AS plantation
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
    return redirect('/produit/show')

@app.route('/produit/edit', methods=['GET'])
def edit_produit():
    print('''affichage du formulaire pour modifier un produit''')
    print(request.args)
    print(request.args.get('id'))
    id=request.args.get('id')
    mycursor = get_db().cursor()
    sql=''' SELECT id_produit AS id, libelle_produit AS libelle, prix_produit AS prix, categorie_id, periode_plantation_optimale AS plantation, periode_recolte_optimale AS recolte
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
    plantation = request.form.get('plantation')
    recolte = request.form.get('recolte')
    message = 'libelle :' + libelle + ' - prix :' + prix + ' - periode de plantation optimal' + plantation + ' - periode de recolte optimale :' + recolte + ' - categorie :' + categorie_id
    print(message)
    mycursor = get_db().cursor()
    tuple_param=(libelle, prix, categorie_id, plantation, recolte)
    sql="INSERT INTO produit(id_produit, libelle_produit, prix_produit, categorie_id, periode_recolte_optimale, periode_plantation_optimale) VALUES (NULL, %s, %s, %s, %s, %s);"
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
    plantation = request.form.get('plantation')
    recolte = request.form.get('recolte')
    message = 'libelle :' + libelle + ' - prix :' + prix + ' - periode de plantation optimal' + plantation + ' - periode de recolte optimale :' + recolte + ' pour le produit d identifiant :' + id
    print(message)
    mycursor = get_db().cursor()
    tuple_param = (libelle, prix, categorie_id, recolte, plantation, id)
    sql="UPDATE produit SET libelle_produit = %s, prix_produit = %s, categorie_id = %s, periode_recolte_optimale = %s, periode_plantation_optimale = %s WHERE id_produit=%s;"
    mycursor.execute(sql,tuple_param)
    get_db().commit()
    return redirect('/produit/show')

@app.route('/produit/statistique', methods=['GET'])
def statistique_produit():
    mycursor = get_db().cursor()


    sql_dates = '''
    SELECT 
        p.libelle_produit AS nom_produit, 
        dp.date_plantation, 
        dr.date_recolte
    FROM produit p
    JOIN est_plante ep ON p.id_produit = ep.produit_id
    JOIN date_plantation dp ON ep.date_plantation_id = dp.id_date_plantation
    LEFT JOIN est_recolte er ON p.id_produit = er.produit_id AND ep.parcelle_id = er.parcelle_id
    LEFT JOIN date_recolte dr ON er.date_recolte_id = dr.id_date_recolte
    ORDER BY LEAST(
        ABS(DATEDIFF(dp.date_plantation, CURDATE())), 
        ABS(DATEDIFF(IFNULL(dr.date_recolte, '2099-12-31'), CURDATE()))
    ) ASC
    LIMIT 10;
    '''
    mycursor.execute(sql_dates)
    produits_dates_proches = mycursor.fetchall()


    sql_duree = '''
    SELECT 
        p.libelle_produit AS nom_produit, 
        DATEDIFF(dr.date_recolte, dp.date_plantation) AS duree_culture
    FROM produit p
    JOIN est_plante ep ON p.id_produit = ep.produit_id
    JOIN date_plantation dp ON ep.date_plantation_id = dp.id_date_plantation
    JOIN est_recolte er ON p.id_produit = er.produit_id AND ep.parcelle_id = er.parcelle_id
    JOIN date_recolte dr ON er.date_recolte_id = dr.id_date_recolte
    ORDER BY duree_culture DESC;
    '''
    mycursor.execute(sql_duree)
    produits_longue_duree = mycursor.fetchall()


    return render_template('produit/statistique_produit.html',
                           produits_dates_proches=produits_dates_proches,
                           produits_longue_duree=produits_longue_duree)


############################# ACTION #############################

############################# EST PLANTE / EST RECOLTE #############################

if __name__ == '__main__':
    app.run(debug=True)
