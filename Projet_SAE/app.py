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
            host="192.168.128.152",
            user="adam",
            password="azerty",
            database="BDD_abajic",
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
    sql_produits = ''' SELECT id_produit                  AS id, 
                              libelle_produit             AS libelle, 
                              prix_produit                AS prix, 
                              categorie_id, 
                              periode_recolte_optimale    AS recolte, 
                              periode_plantation_optimale AS plantation
                       FROM produit
                       ORDER BY id_produit;'''
    mycursor.execute(sql_produits)
    liste_produits = mycursor.fetchall()
    sql_categories = "SELECT id_categorie AS id, libelle_categorie AS libelle FROM categorie;"
    mycursor.execute(sql_categories)
    liste_categories = mycursor.fetchall()
    return render_template('produit/show_produit.html', produits=liste_produits, categories=liste_categories)


@app.route('/produit/add', methods=['GET'])
def add_produit():
    print('''affichage du formulaire pour saisir un produit''')
    mycursor = get_db().cursor()
    sql = "SELECT id_categorie AS id, libelle_categorie AS libelle FROM categorie;"
    mycursor.execute(sql)
    liste_categories = mycursor.fetchall()
    return render_template('produit/add_produit.html', categorie=liste_categories)

@app.route('/produit/delete')
def delete_produit():
    id=request.args.get('id',0)
    message = 'suppression du produit : ' + id
    print(message)
    flash(message, 'alert-warning')
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
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql_produit = ''' SELECT id_produit                  AS id, 
                             libelle_produit             AS libelle, 
                             prix_produit                AS prix, 
                             categorie_id, 
                             periode_plantation_optimale AS plantation, 
                             periode_recolte_optimale    AS recolte
                      FROM produit
                      WHERE id_produit = %s;'''
    mycursor.execute(sql_produit, (id))
    produit = mycursor.fetchone()
    sql_categories = "SELECT id_categorie AS id, libelle_categorie AS libelle FROM categorie;"
    mycursor.execute(sql_categories)
    liste_categories = mycursor.fetchall()
    return render_template('produit/edit_produit.html', produit=produit, categorie=liste_categories)

@app.route('/produit/add', methods=['POST'])
def valid_add_produit():
    print('''ajout du produit dans le tableau''')
    libelle = request.form.get('libelle')
    prix = request.form.get('prix')
    categorie_id = request.form.get('categorie_id')
    plantation = request.form.get('plantation')
    recolte = request.form.get('recolte')
    message = 'Ajout d\'un nouveau produit : ' + ' --- libelle : ' + libelle + ' - prix : ' + prix + ' --- periode de plantation optimal ' + plantation + ' --- periode de recolte optimale : ' + recolte + ' --- categorie : ' + categorie_id
    print(message)
    flash(message, 'alert-success')
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
    message = 'modification d\'un produit ' + 'libelle : ' + libelle + ' --- prix : ' + prix + ' --- periode de plantation optimal : ' + plantation + ' --- periode de recolte optimale : ' + recolte + ' --- pour le produit d identifiant : ' + id + ' --- categorie id : ' + categorie_id
    print(message)
    flash(message, 'alert-success')
    mycursor = get_db().cursor()
    param = (libelle, prix, categorie_id, recolte, plantation, id)
    sql="UPDATE produit SET libelle_produit = %s, prix_produit = %s, categorie_id = %s, periode_recolte_optimale = %s, periode_plantation_optimale = %s WHERE id_produit=%s;"
    mycursor.execute(sql,param)
    get_db().commit()
    return redirect('/produit/show')

@app.route('/produit/statistique', methods=['GET'])
def statistique_produit():
    mycursor = get_db().cursor()


    sql_repartition = '''
        SELECT 
            categorie.libelle_categorie AS libelle, 
            COUNT(produit.id_produit) AS nombre, 
            AVG(produit.prix_produit) AS prix_moyen
        FROM categorie
        LEFT JOIN produit ON categorie.id_categorie = produit.categorie_id
        GROUP BY categorie.id_categorie, categorie.libelle_categorie;
    '''
    mycursor.execute(sql_repartition)
    repartition_categories = mycursor.fetchall()



    sql_top_produits = '''
        SELECT libelle_produit, prix_produit
        FROM produit
        ORDER BY prix_produit DESC
        LIMIT 5;
    '''
    mycursor.execute(sql_top_produits)
    top_produits = mycursor.fetchall()

    sql_periodes = '''
                   SELECT periode_recolte_optimale AS periode, COUNT(id_produit) AS nbr_produits
                   FROM produit
                   WHERE periode_recolte_optimale IS NOT NULL
                   GROUP BY periode_recolte_optimale
                   ORDER BY nbr_produits DESC; 
                   '''
    mycursor.execute(sql_periodes)
    stats_periodes = mycursor.fetchall()


    return render_template('produit/statistique_produit.html',
                           repartition=repartition_categories,
                           top_produits=top_produits,
                           stats_periodes=stats_periodes)


############################# ACTION #############################
############### ACTION — SHOW ###############

@app.route('/action/show')
def action_show():
    mycursor = get_db().cursor()
    mycursor.execute("""
        SELECT 
            ac.id_action AS id,
            ac.libelle_action,
            ta.libelle_type_action AS type_action,
            ac.parcelle_id,
            da.date_action
        FROM action ac
        JOIN type_action ta ON ta.id_type_action = ac.type_action_id
        JOIN date_action da ON da.id_date_action = ac.date_action_id
        ORDER BY ac.id_action;
    """)
    actions = mycursor.fetchall()
    return render_template('action/show_action.html', actions=actions)
############### ACTION — SHOW ###############
############### ACTION — edit ###############
@app.route('/action/edit')
def action_edit():
    id_action = request.args.get('id')

    mycursor = get_db().cursor()
    mycursor.execute("SELECT * FROM action WHERE id_action=%s;", (id_action,))
    action = mycursor.fetchone()

    # Types
    mycursor.execute("SELECT id_type_action, libelle_type_action FROM type_action;")
    types = mycursor.fetchall()

    # Dates
    mycursor.execute("SELECT id_date_action, date_action FROM date_action;")
    dates = mycursor.fetchall()

    # Parcelles
    mycursor.execute("SELECT id_parcelle FROM parcelle;")
    parcelles = mycursor.fetchall()

    return render_template("/action/edit_action.html",
                           action=action,
                           types=types,
                           parcelles=parcelles,
                           dates=dates)


@app.route('/action/edit_validation', methods=['POST'])
def action_edit_validation():
    id_action = request.form.get('id_action')
    libelle_action = request.form.get('libelle_action')
    type_action_id = request.form.get('type_action_id')
    parcelle_id = request.form.get('parcelle_id')
    date_action = request.form.get('date_action')

    mycursor = get_db().cursor()

    mycursor.execute("INSERT INTO date_action (date_action) VALUES (%s);", (date_action,))

    date_action_id = mycursor.lastrowid

    sql = """UPDATE action
             SET libelle_action=%s, \
                 type_action_id=%s, \
                 parcelle_id=%s, \
                 date_action_id=%s
             WHERE id_action = %s;"""

    mycursor.execute(sql, (libelle_action, type_action_id, parcelle_id, date_action_id, id_action))

    get_db().commit()
    message = (
            "ATTENTION : Une action a été modifié : Son identifiant d'action est " + id_action + ". Son libellé action est : " + libelle_action + " et son identifiant est : " + type_action_id + ". L'identifiant de sa parcelle est : " + parcelle_id + ". Sa date est : " + date_action + ".")
    flash(message, 'alert-success')
    return redirect('/action/show?id=' + id_action)

############### ACTION — edit ###############
############### ACTION — delete ###############
@app.route('/action/delete', methods=['POST'])
def action_delete():
    id_action = request.form.get('id')

    mycursor = get_db().cursor()

    mycursor.execute("""
        DELETE FROM effectue WHERE action_id=%s;
    """, (id_action,))

    mycursor.execute("""
        DELETE FROM action WHERE id_action=%s;
    """, (id_action,))

    get_db().commit()

    message = ("ATTENTION : Une action a été supprimée : Son identifiant action est " + id_action + ".")
    flash(message, 'alert-warning')

    return redirect('/action/show')
############### ACTION — delete ###############
############### ACTION — add ###############
@app.route('/action/add')
def action_add():
    mycursor = get_db().cursor()

    mycursor.execute("SELECT id_type_action, libelle_type_action FROM type_action;")
    types = mycursor.fetchall()

    mycursor.execute("SELECT id_parcelle FROM parcelle;")
    parcelles = mycursor.fetchall()

    return render_template("action/add_action.html", types=types, parcelles=parcelles)


@app.route('/action/add_validation', methods=['POST'])
def action_add_validation():
    libelle = request.form['libelle_action']
    type_action = request.form['type_action_id']
    parcelle = request.form['parcelle_id']
    date_action = request.form['date_action']

    mycursor = get_db().cursor()

    mycursor.execute("INSERT INTO date_action (date_action) VALUES (%s);", (date_action,))

    date_action_id = mycursor.lastrowid

    mycursor.execute("""
                     INSERT INTO action(libelle_action, type_action_id, parcelle_id, date_action_id)
                     VALUES (%s, %s, %s, %s)
                     """, (libelle, type_action, parcelle, date_action_id))

    get_db().commit()

    message = (
                "ATTENTION : Une action a été ajoutée : De libellé " + libelle + ". Il s'agit du type d'action : " + type_action + ". Effectué sur la parcelle : " + parcelle + ". Et sa date : " + date_action + ".")
    flash(message, 'alert-success')

    return redirect('/action/show')

############### ACTION — add ###############
############### ACTION — calcul ###############

@app.route('/action/calcul')
def calcul_action():
    mycursor = get_db().cursor()

    mycursor.execute('''
    SELECT p.id_parcelle AS parcelle_id, COUNT(a.id_action) AS nb_actions
    FROM parcelle p
    LEFT JOIN action a ON a.parcelle_id = p.id_parcelle
    GROUP BY p.id_parcelle
    ORDER BY p.id_parcelle;
    ''')
    stats_parcelles = mycursor.fetchall()

    mycursor.execute('''
    SELECT ad.nom AS adherent, COUNT(a.id_action) AS nb_actions
    FROM adherent ad
    LEFT JOIN effectue e ON e.adherent_id = ad.id_adherent
    LEFT JOIN action a ON a.id_action = e.action_id
    GROUP BY ad.id_adherent
    ORDER BY nb_actions DESC;
    ''')
    stats_adherents = mycursor.fetchall()

    mycursor.execute('''
    SELECT ta.libelle_type_action AS type_action, COUNT(a.id_action) AS nb_actions
    FROM action a
    JOIN type_action ta ON ta.id_type_action = a.type_action_id
    GROUP BY ta.id_type_action
    ORDER BY nb_actions DESC
    LIMIT 1;
    ''')
    action_frequente = mycursor.fetchone()

    return render_template('action/calcul_action.html',
                           stats_parcelles=stats_parcelles,
                           stats_adherents=stats_adherents,
                           action_frequente=action_frequente)

############################# EST PLANTE / EST RECOLTE #############################

############################# EST PLANTE / EST RECOLTE SHOW #############################

@app.route('/plantation/show')
def show_plantation():
    mycursor = get_db().cursor()

    sql_plantations = '''
    SELECT 
        ep.id_est_plante,
        ep.parcelle_id,
        ep.produit_id,
        p.libelle_produit AS produit,
        dp.id_date_plantation AS date_id,
        dp.date_plantation
    FROM est_plante ep
    JOIN produit p ON ep.produit_id = p.id_produit
    JOIN date_plantation dp ON ep.date_plantation_id = dp.id_date_plantation
        GROUP BY ep.id_est_plante
    '''
    mycursor.execute(sql_plantations)
    plantations = mycursor.fetchall()

    sql_recoltes = '''
    SELECT 
        er.id_est_recolte,
        er.parcelle_id,
        er.produit_id,
        p.libelle_produit AS produit,
        dr.id_date_recolte AS date_id,
        dr.date_recolte,
        er.quantite_recoltee
    FROM est_recolte er
    JOIN produit p ON er.produit_id = p.id_produit
    JOIN date_recolte dr ON er.date_recolte_id = dr.id_date_recolte
    ORDER BY er.id_est_recolte;
    '''
    mycursor.execute(sql_recoltes)
    recoltes = mycursor.fetchall()

    return render_template('/plantation/show_plantation.html', plantations=plantations, recoltes=recoltes)

############################# EST PLANTE / EST RECOLTE DELETE #############################

@app.route('/plantation/delete')
def delete_plantation_plante():
    print('''Suppression d'une entrée de plantation :''')
    print(request.args)
    print(request.args.get('id'))
    id_est_plante =request.args.get('id')

    mycursor = get_db().cursor()
    param = id_est_plante
    delete_sql = "DELETE FROM est_plante WHERE id_est_plante=%s;"
    mycursor.execute(delete_sql, param)

    get_db().commit()
    message = ("ATTENTION : Une entrée de plantation a été supprimée : Son identifiant de plantation est "
               + id_est_plante + ".")
    flash(message, 'alert-warning')
    return redirect('/plantation/show')

############################# EST PLANTE / EST RECOLTE DELETE 2 #############################


@app.route('/plantation/delete2')
def delete_plantation_recolte():
    print('''Suppression d'une entrée de récolte :''')
    print(request.args)
    print(request.args.get('id'))
    id_est_recolte =request.args.get('id')

    mycursor = get_db().cursor()
    param = id_est_recolte
    delete_sql2 = "DELETE FROM est_recolte WHERE id_est_recolte=%s;"
    mycursor.execute(delete_sql2, param)

    get_db().commit()
    message = ("ATTENTION : Une entrée de récolte a été supprimée : Son identifiant de récolte est " +
               id_est_recolte + ".")
    flash(message, 'alert-warning')
    return redirect('/plantation/show')

############################# EST PLANTE / EST RECOLTE ADD #############################

@app.route('/plantation/add', methods=['GET'])
def add_plantation():
    mycursor = get_db().cursor()

    # Recupère les parcelles
    sql_parcelles = "SELECT id_parcelle FROM parcelle ORDER BY id_parcelle;"
    mycursor.execute(sql_parcelles)
    parcelles = mycursor.fetchall()

    # Récupère les id des produits et leur libellé
    sql_produits = "SELECT id_produit, libelle_produit FROM produit ORDER BY id_produit;"
    mycursor.execute(sql_produits)
    identifiantproduit = mycursor.fetchall()

    return render_template('plantation/add_plantation.html', parcelles=parcelles, identifiantproduit=identifiantproduit)
@app.route('/plantation/add', methods=['POST'])
def valid_add_plantation():
    id_parcelle = request.form.get('id_parcelle')
    produit_id = request.form.get('produit_id')
    date_plantation_str = request.form.get('date_plantation')

    mycursor = get_db().cursor()

    # Insertion de la date dans la table date_plantation pour récup l'id
    sql_insert_date = "INSERT INTO date_plantation (date_plantation) VALUES (%s);"
    mycursor.execute(sql_insert_date, (date_plantation_str,))
    date_plantation_id = mycursor.lastrowid  # récup l'ID auto-incrémenté de la date

    # Insertion dans est_planté avec l'id qu'on a récup
    sql_insert_plantation = """
                            INSERT INTO est_plante (parcelle_id, produit_id, date_plantation_id)
                            VALUES (%s, %s, %s);
                            """
    tuple_param = (id_parcelle, produit_id, date_plantation_id)
    mycursor.execute(sql_insert_plantation, tuple_param)

    get_db().commit()

    message = (
            "Un produit vient d'être planté sur la parcelle n°" + id_parcelle +
            ". Il s'agit du produit n°" + produit_id +
            ". Le produit a été planté à la date du " + date_plantation_str + ".")
    flash(message, 'alert-success')

    return redirect('/plantation/show')

############################# EST PLANTE / EST RECOLTE ADD 2 #############################
@app.route('/plantation/add2', methods=['GET'])
def add_plantation2():
    mycursor = get_db().cursor()

    # Recupère les parcelles
    sql_parcelles = "SELECT id_parcelle FROM parcelle ORDER BY id_parcelle;"
    mycursor.execute(sql_parcelles)
    parcelles = mycursor.fetchall()

    # Récupère les id des produits et leur libellé
    sql_produits = "SELECT id_produit, libelle_produit FROM produit ORDER BY id_produit;"
    mycursor.execute(sql_produits)
    identifiantproduit = mycursor.fetchall()

    return render_template('plantation/add2_plantation.html', parcelles=parcelles, identifiantproduit=identifiantproduit)
@app.route('/plantation/add2', methods=['POST'])
def valid_add_plantation2():
    id_parcelle = request.form.get('id_parcelle')
    produit_id = request.form.get('produit_id')
    date_recolte_str = request.form.get('date_recolte')
    quantite_recoltee = request.form.get('quantite_recoltee')

    mycursor = get_db().cursor()

    # Insertion de la date dans la table date_recolte pour récup l'id
    sql_insert_date = "INSERT INTO date_recolte (date_recolte) VALUES (%s);"
    mycursor.execute(sql_insert_date, (date_recolte_str,))
    date_recolte_id = mycursor.lastrowid # récup l'ID auto-incrémenté de la date

    # Insertion dans est_récolté avec l'id qu'on a récup
    sql_insert_recolte = """
                         INSERT INTO est_recolte (parcelle_id, produit_id, date_recolte_id, quantite_recoltee)
                         VALUES (%s, %s, %s, %s); 
                         """
    tuple_param = (id_parcelle, produit_id, date_recolte_id, quantite_recoltee)
    mycursor.execute(sql_insert_recolte, tuple_param)

    get_db().commit()

    message = (
            "Un produit vient d'être planté sur la parcelle n°" + id_parcelle +
            ". Il s'agit du produit n°" + produit_id +
            ". Le produit a été planté à la date du " + date_recolte_str +
            ". La quantité récolté est la suivante : " + quantite_recoltee + ".")
    flash(message, 'alert-success')

    return redirect('/plantation/show')

############################# EST PLANTE / EST RECOLTE EDIT #############################
@app.route('/plantation/edit')
def edit_plantation():
    id = request.args.get('id')

    mycursor = get_db().cursor()

    sql = '''
    SELECT ep.id_est_plante,
           ep.parcelle_id,
           ep.produit_id,
           ep.date_plantation_id,
           p.libelle_produit,
           DATE_FORMAT(dp.date_plantation, '%%Y-%%m-%%d') AS date_plantation_formatee
    FROM est_plante ep
    JOIN produit p ON p.id_produit = ep.produit_id
    JOIN date_plantation dp ON dp.id_date_plantation = ep.date_plantation_id
    WHERE ep.id_est_plante = %s;
    '''
    mycursor.execute(sql, (id,))
    plantation = mycursor.fetchone()

    mycursor.execute('SELECT id_parcelle AS id FROM parcelle;')
    parcelles = mycursor.fetchall()

    mycursor.execute('SELECT id_produit AS id, libelle_produit AS libelle FROM produit;')
    produits = mycursor.fetchall()


    print(plantation,parcelles,produits)
    return render_template("plantation/edit_plantation.html",
                           plantation=plantation,
                           parcelles=parcelles,
                           produits=produits)
@app.route('/plantation/edit', methods=['POST'])
def valid_edit_plantation():
    mycursor = get_db().cursor()

    id_est_plante = request.form.get('id')
    id_parcelle = request.form.get('id_parcelle')
    produit_id = request.form.get('produit_id')
    date_plantation_str = request.form.get('date_plantation')

    sql_date = "SELECT id_date_plantation FROM date_plantation WHERE date_plantation = %s;"
    mycursor.execute(sql_date, (date_plantation_str,))

    sql_insert_date = "INSERT INTO date_plantation (date_plantation) VALUES (%s);"
    mycursor.execute(sql_insert_date, (date_plantation_str,))
    get_db().commit()
    date_plantation_id = mycursor.lastrowid

    commande_sql = '''
                   UPDATE est_plante
                   SET parcelle_id = %s,
                       produit_id = %s,
                       date_plantation_id = %s
                   WHERE id_est_plante = %s; 
                   '''
    tuple_param = (id_parcelle, produit_id, date_plantation_id, id_est_plante)
    mycursor.execute(commande_sql, tuple_param)
    get_db().commit()

    message = (
            "Un enregistrement de plantation vient d'être modifié. Il concerne la parcelle n°" + id_parcelle +
            ". Il s'agit du produit n°" + produit_id +
            ". Le produit a été planté à la date du " + date_plantation_str + "."
    )
    flash(message, 'alert-success')

    return redirect('/plantation/show')

############################# EST PLANTE / EST RECOLTE EDIT 2 #############################
@app.route('/plantation/edit2')
def edit_recolte():
    id = request.args.get('id')
    mycursor = get_db().cursor()
    commande_sql = '''
    SELECT er.id_est_recolte, 
          er.parcelle_id, 
          er.produit_id, 
          er.date_recolte_id, 
          er.quantite_recoltee, 
          p.libelle_produit, 
          DATE_FORMAT(dr.date_recolte, '%%Y-%%m-%%d') AS date_recolte_formatee
    FROM est_recolte er
            JOIN produit p ON er.produit_id = p.id_produit
            JOIN date_recolte dr ON er.date_recolte_id = dr.id_date_recolte
    WHERE er.id_est_recolte = %s;
    '''
    tuple_param = (id,)
    mycursor.execute(commande_sql, tuple_param)
    plantation_recolte = mycursor.fetchone()

    # on a aussi besoin des parcelles :
    sql_parcelles = "SELECT id_parcelle FROM parcelle ORDER BY id_parcelle;"
    mycursor.execute(sql_parcelles)
    parcelles = mycursor.fetchall()

    # et les produits avec leur libellé :
    sql_produits = "SELECT id_produit, libelle_produit FROM produit ORDER BY libelle_produit;"
    mycursor.execute(sql_produits)
    identifiantproduit = mycursor.fetchall()

    return render_template('plantation/edit2_plantation.html',
                           plantation_recolte=plantation_recolte,
                           parcelles=parcelles,
                           identifiantproduit=identifiantproduit)


@app.route('/plantation/edit2', methods=['POST'])
def valid_edit_recolte():
    mycursor = get_db().cursor()

    id_est_recolte = request.form.get('id')
    id_parcelle = request.form.get('id_parcelle')
    produit_id = request.form.get('produit_id')
    date_recolte_str = request.form.get('date_recolte')
    quantite_recoltee = request.form.get('quantite_recoltee')



    # a. Vérifier si la date existe déjà
    sql_check_date = "SELECT id_date_recolte FROM date_recolte WHERE date_recolte = %s;"
    mycursor.execute(sql_check_date, (date_recolte_str,))

    sql_insert_date = "INSERT INTO date_recolte (date_recolte) VALUES (%s);"
    mycursor.execute(sql_insert_date, (date_recolte_str,))
    get_db().commit()
    date_recolte_id = mycursor.lastrowid

    commande_sql = '''
                   UPDATE est_recolte
                   SET parcelle_id       = %s,
                       produit_id        = %s,
                       date_recolte_id   = %s,
                       quantite_recoltee = %s
                   WHERE id_est_recolte = %s; 
                   '''

    tuple_param = (id_parcelle, produit_id, date_recolte_id, quantite_recoltee, id_est_recolte)
    mycursor.execute(commande_sql, tuple_param)
    get_db().commit()

    message = (
            "Un enregistrement de récolte vient d'être modifié. Il concerne la parcelle n°" + id_parcelle +
            ". Il s'agit du produit n°" + produit_id +
            ". Le produit a été récolte à la date du " + date_recolte_str +
            ". Avec une quantité de : " + quantite_recoltee + "."
    )
    flash(message, 'alert-success')


    return redirect('/plantation/show')

############################# EST PLANTE / EST RECOLTE STATISTIQUES  #############################
@app.route('/plantation/stat')
def stat_plantation():
    mycursor = get_db().cursor()

    # Classement des produits les plus récoltés

    sql_produits_plus_recoltes = """
                                 SELECT p.libelle_produit         AS produit, 
                                        SUM(er.quantite_recoltee) AS total_recolte
                                 FROM est_recolte er
                                          JOIN produit p ON p.id_produit = er.produit_id
                                 GROUP BY er.produit_id
                                 ORDER BY total_recolte DESC; 
                                 """
    mycursor.execute(sql_produits_plus_recoltes)
    produits_plus_recoltes = mycursor.fetchall()

    # Classement des mois de récolte les plus productifs

    sql_mois_recolte = """
                       SELECT
                           MONTH(dr.date_recolte) AS mois, 
                           SUM(er.quantite_recoltee) AS total_recolte
                       FROM est_recolte er
                           JOIN date_recolte dr 
                       ON er.date_recolte_id = dr.id_date_recolte
                       GROUP BY mois
                       ORDER BY total_recolte DESC; 
                       """
    mycursor.execute(sql_mois_recolte)
    mois_recolte = mycursor.fetchall()

    # Classement des produits les plus plantés

    sql_produits_plus_plantes = """
                                SELECT p.libelle_produit       AS produit, 
                                       COUNT(ep.id_est_plante) AS nb_plantations
                                FROM est_plante ep
                                         JOIN produit p ON p.id_produit = ep.produit_id
                                GROUP BY ep.produit_id
                                ORDER BY nb_plantations DESC; 
                                """
    mycursor.execute(sql_produits_plus_plantes)
    produits_plus_plantes = mycursor.fetchall()

    # Classement des mois de plantation les plus actifs

    sql_mois_plantation = """
                          SELECT
                              MONTH(dp.date_plantation) AS mois, COUNT(ep.id_est_plante) AS nb_plantations
                          FROM est_plante ep
                              JOIN date_plantation dp
                          ON dp.id_date_plantation = ep.date_plantation_id
                          GROUP BY mois
                          ORDER BY nb_plantations DESC; 
                          """
    mycursor.execute(sql_mois_plantation)
    mois_plantation = mycursor.fetchall()

    # Programme python simple qui convertit le nombre du mois renvoyé
    # par la fonction d'agrégation MONTH en nom du mois en lui-même pour plus de lisibilité

    mois_fr = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
        5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
        9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }

    for row in mois_recolte:
        row['mois'] = mois_fr.get(row['mois'], row['mois'])

    for row in mois_plantation:
        row['mois'] = mois_fr.get(row['mois'], row['mois'])

    return render_template(
        'plantation/stat_plantation.html',
        produits_plus_recoltes=produits_plus_recoltes,
        mois_recolte=mois_recolte,
        produits_plus_plantes=produits_plus_plantes,
        mois_plantation=mois_plantation
    )


@app.route('/plantation/statchoix', methods=['POST'])
def statchoix_plantation():
    mycursor = get_db().cursor()
    choix = request.form.get('choix')
    sql_produits_plus_recoltes = """
                                 SELECT p.libelle_produit         AS produit,
                                        SUM(er.quantite_recoltee) AS total_recolte
                                 FROM est_recolte er
                                          JOIN produit p ON p.id_produit = er.produit_id
                                          JOIN categorie c ON c.id_categorie = p.categorie_id
                                 WHERE c.libelle_categorie = %s 
                                 GROUP BY er.produit_id
                                 ORDER BY total_recolte DESC; 
                                 """

    mycursor.execute(sql_produits_plus_recoltes, choix)
    produits_plus_recoltes = mycursor.fetchall()

    sql_mois_recolte = """
                       SELECT MONTH(dr.date_recolte)    AS mois,
                              SUM(er.quantite_recoltee) AS total_recolte
                       FROM est_recolte er
                                JOIN date_recolte dr ON er.date_recolte_id = dr.id_date_recolte
                                JOIN produit p ON p.id_produit = er.produit_id
                                JOIN categorie c ON c.id_categorie = p.categorie_id
                       WHERE c.libelle_categorie = %s 
                       GROUP BY mois
                       ORDER BY total_recolte DESC;
                       """
    mycursor.execute(sql_mois_recolte, choix)
    mois_recolte = mycursor.fetchall()

    sql_produits_plus_plantes = """
                                SELECT p.libelle_produit       AS produit,
                                       COUNT(ep.id_est_plante) AS nb_plantations
                                FROM est_plante ep
                                         JOIN produit p ON p.id_produit = ep.produit_id
                                         JOIN categorie c ON c.id_categorie = p.categorie_id
                                WHERE c.libelle_categorie = %s 
                                GROUP BY ep.produit_id
                                ORDER BY nb_plantations DESC;
                                """
    mycursor.execute(sql_produits_plus_plantes, choix)
    produits_plus_plantes = mycursor.fetchall()

    sql_mois_plantation = """
                          SELECT MONTH(dp.date_plantation) AS mois,
                                 COUNT(ep.id_est_plante)   AS nb_plantations
                          FROM est_plante ep
                                   JOIN date_plantation dp ON dp.id_date_plantation = ep.date_plantation_id
                                   JOIN produit p ON p.id_produit = ep.produit_id
                                   JOIN categorie c ON c.id_categorie = p.categorie_id
                          WHERE c.libelle_categorie = %s
                          GROUP BY mois
                          ORDER BY nb_plantations DESC;
                          """
    mycursor.execute(sql_mois_plantation, choix)
    mois_plantation = mycursor.fetchall()

    mois_fr = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
        5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
        9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }

    for row in mois_recolte:
        row['mois'] = mois_fr.get(row['mois'], row['mois'])

    for row in mois_plantation:
        row['mois'] = mois_fr.get(row['mois'], row['mois'])

    return render_template(
        'plantation/stat_plantation.html',
        produits_plus_recoltes=produits_plus_recoltes,
        mois_recolte=mois_recolte,
        produits_plus_plantes=produits_plus_plantes,
        mois_plantation=mois_plantation
    )

if __name__ == '__main__':
    app.run(debug=True)
