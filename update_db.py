'''
@author Enrico Biancotto

Local folder are organized like this:
.
|-- 1972
|-------allenatore
|-------assistenti
|-------attivitaGiovanile
|-------fotoSquadra
|-------galleria
|-------giocatori
|-------management
|-------rassegnaStampa
|-------statistica
|-------viceAllenatori
|--1973
...

This script represents the core for the data digitalization of a local basketball team.

We start to read from a spreadsheet which contains the roster and some statistic for a basketball team,
we then proceed to create a new row on the year table,
Now that we have in input all the data for a team: players, coaches, league of the championship, year and so on; we can upload a new team.
'''


#!/usr/bin/python
import os
from slugify import slugify
import sys
from time import sleep
import json
import pandas as pd
from contentful_management import Client
from locale import atof, setlocale, LC_NUMERIC


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def checkName(nameO, nameL):
    nameO = nameO.upper()
    nameL = nameL.upper()
    if (nameO == nameL):
        return True
    # se non sono uguali guardiamo le differenze
    spaziO = nameO.split(" ")
    spaziL = nameL.split(" ")
    if (len(spaziO) != len(spaziL)):
        return False
    else:
        if (len(spaziO) == 2):
            if (spaziO[1] + " " + spaziO[0] == nameL or nameO == spaziL[1] + " " + spaziL[0]):
                return True
            return False
        elif (len(spaziO) == 3):
            # 0 1 2 bruteforce
            if (nameO == spaziL[0] + " " + spaziL[2] + " " + spaziL[1]):
                return True
            elif (nameO == spaziL[1] + " " + spaziL[0] + " " + spaziL[2]):
                return True
            elif (nameO == spaziL[1] + " " + spaziL[2] + " " + spaziL[0]):
                return True
            elif (nameO == spaziL[2] + " " + spaziL[1] + " " + spaziL[0]):
                return True
            elif (nameO == spaziL[2] + " " + spaziL[0] + " " + spaziL[1]):
                return True
            # 0 2 1 bruteforce
            if (spaziO[0] + " " + spaziO[2] + " " + spaziO[1] == nameL):
                return True
            if (spaziO[0] + " " + spaziO[2] + " " + spaziO[1] == spaziL[0] + " " + spaziL[2] + " " + spaziL[1]):
                return True
            elif (spaziO[0] + " " + spaziO[2] + " " + spaziO[1] == spaziL[1] + " " + spaziL[0] + " " + spaziL[2]):
                return True
            elif (spaziO[0] + " " + spaziO[2] + " " + spaziO[1] == spaziL[1] + " " + spaziL[2] + " " + spaziL[0]):
                return True
            elif (spaziO[0] + " " + spaziO[2] + " " + spaziO[1] == spaziL[2] + " " + spaziL[1] + " " + spaziL[0]):
                return True
            elif (spaziO[0] + " " + spaziO[2] + " " + spaziO[1] == spaziL[2] + " " + spaziL[0] + " " + spaziL[1]):
                return True
            # 1 0 2 bruteforce
            if (spaziO[1] + " " + spaziO[0] + " " + spaziO[2] == nameL):
                return True
            if (spaziO[1] + " " + spaziO[0] + " " + spaziO[2] == spaziL[0] + " " + spaziL[2] + " " + spaziL[1]):
                return True
            elif (spaziO[1] + " " + spaziO[0] + " " + spaziO[2] == spaziL[1] + " " + spaziL[0] + " " + spaziL[2]):
                return True
            elif (spaziO[1] + " " + spaziO[0] + " " + spaziO[2] == spaziL[1] + " " + spaziL[2] + " " + spaziL[0]):
                return True
            elif (spaziO[1] + " " + spaziO[0] + " " + spaziO[2] == spaziL[2] + " " + spaziL[1] + " " + spaziL[0]):
                return True
            elif (spaziO[1] + " " + spaziO[0] + " " + spaziO[2] == spaziL[2] + " " + spaziL[0] + " " + spaziL[1]):
                return True
            # 1 2 0 bruteforce
            if (spaziO[1] + " " + spaziO[2] + " " + spaziO[0] == nameL):
                return True
            if (spaziO[1] + " " + spaziO[2] + " " + spaziO[0] == spaziL[0] + " " + spaziL[2] + " " + spaziL[1]):
                return True
            elif (spaziO[1] + " " + spaziO[2] + " " + spaziO[0] == spaziL[1] + " " + spaziL[0] + " " + spaziL[2]):
                return True
            elif (spaziO[1] + " " + spaziO[2] + " " + spaziO[0] == spaziL[1] + " " + spaziL[2] + " " + spaziL[0]):
                return True
            elif (spaziO[1] + " " + spaziO[2] + " " + spaziO[0] == spaziL[2] + " " + spaziL[1] + " " + spaziL[0]):
                return True
            elif (spaziO[1] + " " + spaziO[2] + " " + spaziO[0] == spaziL[2] + " " + spaziL[0] + " " + spaziL[1]):
                return True
            # 2 1 0 bruteforce
            if (spaziO[2] + " " + spaziO[1] + " " + spaziO[0] == nameL):
                return True
            if (spaziO[2] + " " + spaziO[1] + " " + spaziO[0] == spaziL[0] + " " + spaziL[2] + " " + spaziL[1]):
                return True
            elif (spaziO[2] + " " + spaziO[1] + " " + spaziO[0] == spaziL[1] + " " + spaziL[0] + " " + spaziL[2]):
                return True
            elif (spaziO[2] + " " + spaziO[1] + " " + spaziO[0] == spaziL[1] + " " + spaziL[2] + " " + spaziL[0]):
                return True
            elif (spaziO[2] + " " + spaziO[1] + " " + spaziO[0] == spaziL[2] + " " + spaziL[1] + " " + spaziL[0]):
                return True
            elif (spaziO[2] + " " + spaziO[1] + " " + spaziO[0] == spaziL[2] + " " + spaziL[0] + " " + spaziL[1]):
                return True
            # 2 0 1 bruteforce
            if (spaziO[2] + " " + spaziO[0] + " " + spaziO[1] == nameL):
                return True
            if (spaziO[2] + " " + spaziO[0] + " " + spaziO[1] == spaziL[0] + " " + spaziL[2] + " " + spaziL[1]):
                return True
            elif (spaziO[2] + " " + spaziO[0] + " " + spaziO[1] == spaziL[1] + " " + spaziL[0] + " " + spaziL[2]):
                return True
            elif (spaziO[2] + " " + spaziO[0] + " " + spaziO[1] == spaziL[1] + " " + spaziL[2] + " " + spaziL[0]):
                return True
            elif (spaziO[2] + " " + spaziO[0] + " " + spaziO[1] == spaziL[2] + " " + spaziL[1] + " " + spaziL[0]):
                return True
            elif (spaziO[2] + " " + spaziO[0] + " " + spaziO[1] == spaziL[2] + " " + spaziL[0] + " " + spaziL[1]):
                return True
            # se arriva qui nessuno è vero, dato che non ci sono giocatori con più di 3 parole nel nome, è False
            return False

def findPersona(db, nome):
    if (len(db) == 0):
        return False
    for key, value in db.items():
        if (checkName(value['nome'], nome)):
            return value['id']
    return False

def addPersona(db, nome, identifier, index_dict):
    if (findPersona(db, nome) == False):
        db[index_dict['index']] = {
            "nome": nome,
            "id": identifier
        }
        index_dict['index'] += 1
        file = open("persone-db.json", "w")
        json.dump(db, file, indent=4)
        file.close()

def findSquadra(db, nome):
    if (len(db) == 0):
        return False
    for key, value in db.items():
        if (value['nome'].upper() == nome.upper()):
            return value['id']
    return False

def addSquadra(db, nome, identifier, index_dict):
    if (findSquadra(db, nome) == False):
        db[index_dict['index']] = {
            "nome": nome,
            "id": identifier
        }
        index_dict['index'] += 1
        file = open("squadre-db.json", "w")
        json.dump(db, file, indent=4)
        file.close()

def findPeriodo(db, nome):
    if (len(db) == 0):
        return False
    for key, value in db.items():
        if (value['nome'].upper() == nome.upper()):
            return value['id']
    return False

def addPeriodo(db, nome, identifier, index_dict):
    if (findPeriodo(db, nome) == False):
        db[index_dict['index']] = {
            "nome": nome,
            "id": identifier
        }
        index_dict['index'] += 1
        file = open("periodi-db.json", "w")
        json.dump(db, file, indent=4)
        file.close()

def main():
    file_excel = [os.path.join(path, name) for path, subdirs, files in os.walk("./DATI") for name in files if name.endswith(".xlsx")]
    
    # DA FAR ESEGUIRE SOLO LA PRIMA VOLTA
    # connette a contentful
    client = Client('CFPAT-5BLAuJOxBs5VBHW19O4-CrZ7EMbwGV6s0hr93laB21Q')
    jSpace = client.spaces().find('c8y62hpixye3')
    environment = jSpace.environments().find('master-2021-04-18')

    # recupero informazioni sui periodi
    periodi_db = pd.read_json('periodi-db.json').to_dict()
    periodi_off_dict = pd.read_json('periodi-last-index.json').to_dict()
    periodi_index_dict = {}
    periodi_index_dict['index'] = periodi_off_dict[0]['index']
    # creo nuovo periodo
    periodo_attributes = {}
    # aggiungo periodi a contentful
    periodi =[{'start': 1963, 'end': 1970}]
    i = 1971
    while i < 2001:
        start = i
        if (i % 10 == 0):
            i += 1
            continue
        else:
            i += 9
        end = i
        periodi.append({'start': start, 'end': end})
    periodi.reverse()

    for periodo in periodi:
        nome = str(periodo['start'])+'-'+str(periodo['end'])
        slug = slugify(nome)
        periodo_fields = {
            'nome': {
                'it-IT': nome
            },
            'slug': {
                'it-IT': slug
            },
            'inizio': {
                'it-IT': int(periodo['start'])
            },
            'fine': {
                'it-IT': int(periodo['end'])
            }
        }
            
        periodo_attributes = {
            'content_type_id': 'periodo',
            'fields': periodo_fields
        }
        periodo_c = environment.entries().create(None, periodo_attributes)
        periodo_c.save()
        periodo_c.publish()
        addPeriodo(periodi_db, nome, periodo_c.sys['id'], periodi_index_dict)
        
    # salvo indice scrittura periodo
    periodi_off_dict[0]['index'] = periodi_index_dict['index']
    file = open("periodi-last-index.json", "w")
    json.dump(periodi_off_dict, file, indent=4)
    file.close()
    
    # caricamento squadra
    for excel in file_excel:
        uploadAnno(excel)

def uploadAnno(excel_file):
    setlocale(LC_NUMERIC, 'French_Canada.1252')
    # 1.a) apre db Persone
    persone_db = pd.read_json('persone-db.json').to_dict()
    persone_off_dict = pd.read_json('persone-last-index.json').to_dict()
    persone_index_dict = {}
    persone_index_dict['index'] = persone_off_dict[0]['index']
    # 1.b) apre db Squadre
    squadre_db = pd.read_json('squadre-db.json').to_dict()
    squadre_off_dict = pd.read_json('squadre-last-index.json').to_dict()
    squadre_index_dict = {}
    squadre_index_dict['index'] = squadre_off_dict[0]['index']
    # 1.c) apre db Periodi
    periodi_db = pd.read_json('periodi-db.json').to_dict()
    periodi_off_dict = pd.read_json('periodi-last-index.json').to_dict()
    periodi_index_dict = {}
    periodi_index_dict['index'] = periodi_off_dict[0]['index']

    # 2) da excel legge nuova squadra da inserire
    squadra = {}
    squadra['giocatori'] = pd.read_excel(excel_file, sheet_name='Giocatori').T.to_dict()
    squadra['allenatore'] = pd.read_excel(excel_file, sheet_name='Coach').T.to_dict()
    squadra['viceAllenatori'] = pd.read_excel(excel_file, sheet_name='ViceAllenatori').T.to_dict()
    squadra['assistenti'] = pd.read_excel(excel_file, sheet_name='Assistenti').T.to_dict()
    squadra['campionato'] = pd.read_excel(excel_file, sheet_name='Campionato').T.to_dict()
    squadra['nomeSquadra'] = pd.read_excel(excel_file, sheet_name='Squadra').T.to_dict()
    squadra['anno'] = pd.read_excel(excel_file, sheet_name='Anno').T.to_dict()
    
    # 3) se la squadra esiste, segnala e termina programma
    esiste = findSquadra(squadre_db, str(squadra['nomeSquadra'][0]['nome']) + " " + str(squadra['anno'][0]['anno']))
    if (esiste == False):
        # anno_dict conterrà tutte le informazioni (da excel e da cartella ./anno) sulla squadra da inserire
        anno_dict = {}
        anno_dict['anno'] = squadra['anno'][0]['anno']
        anno_dict['campionato'] = squadra['campionato'][0]['nome']
        anno_dict['nomeSquadra'] = squadra['nomeSquadra'][0]['nome']

        # 4) prende informazioni da ./anno
        with cd("./" + str(anno_dict['anno'])):
            # foto squadra
            foto_squad = {}
            with cd("./fotoSquadra"):
                for file in os.listdir(os.getcwd()):
                    path = os.path.join(os.getcwd(), file)
                    nome = file.split(".")[0]
                    filetype = ""
                    if (file.split(".")[1].upper() == "JPG" or file.split(".")[1].upper() == "JPEG"):
                        filetype = "image/jpeg"
                    elif (file.split(".")[1].upper() == "PNG"):
                        filetype = "image/png"
                    # inserisco i dati in dizionario allenatore
                    foto_squad["nome"] = nome
                    foto_squad["descrizione"] = nome
                    foto_squad["filename"] = file
                    foto_squad["path"] = path
                    foto_squad["filetype"] = filetype
            anno_dict['fotoSquadra'] = foto_squad

            # allenatore
            allenat = {}
            with cd("./allenatore"):
                # in allenatore c'è un solo file stile nome.tipo
                # se non ho immagini da inserire per questo anno
                if (len(os.listdir(os.getcwd())) == 0 and 'nome' in squadra['allenatore']):
                    allenat['nome'] = squadra['allenatore']['nome']

                # se ci sono immagini da inserire
                for file in os.listdir(os.getcwd()):
                    path = os.path.join(os.getcwd(), file)
                    nome = file.split(".")[0]
                    descrizione = "Foto di allenatore " + nome + " " + str(anno_dict['anno'])
                    filetype = ""
                    if (file.split(".")[1].upper() == "JPG" or file.split(".")[1].upper() == "JPEG"):
                        filetype = "image/jpeg"
                    elif (file.split(".")[1].upper() == "PNG"):
                        filetype = "image/png"
                    # inserisco i dati in dizionario allenatore
                    allenat["nome"] = nome
                    allenat["ruolo"] = "Primo allenatore"
                    allenat["descrizione"] = descrizione
                    allenat["filename"] = descrizione + "." + file.split(".")[1]
                    allenat["path"] = path
                    allenat["filetype"] = filetype
                    # elimino da allenatori noti
                    for i in squadra['allenatore']:
                        excel_coach = squadra['allenatore'][i]
                        # se è lo stesso giocatore, salvo le informazioni
                        if (checkName(excel_coach['nome'], nome)):
                            squadra['allenatore'].pop(i)
                            break
            for i in squadra['allenatore']:
                excel_coach = squadra['allenatore'][i]
                if (excel_coach['nome'] != "" and excel_coach['nome'] != "-"):
                    allenat['nome'] = excel_coach['nome']
            anno_dict["allenatore"] = allenat

            # giocatori
            giocatori = []
            with cd("./giocatori"):
                # per ogni giocatore teoricamente so nMaglia-ruolo-nome.tipo
                for file in os.listdir(os.getcwd()):
                    giocatore = {}
                    path = os.path.join(os.getcwd(), file)
                    filename = file.split(".")[0]
                    nMaglia = -1
                    ruolo = ""
                    nome = ""
                    # caso std nMaglia-Ruolo-Nome
                    if (filename.count("-") == 2 and not(filename.startswith("-"))):
                        nMaglia = int(filename.split("-")[0])
                        ruolo = filename.split("-")[1]
                        nome = filename.split("-")[2]
                    # caso -Ruolo-Nome
                    elif (filename.startswith("-") and filename.count("-") == 2):
                        ruolo = filename.split("-")[1]
                        nome = filename.split("-")[2]
                    # caso nMaglia-Nome
                    elif (filename.count("-") == 1):
                        nMaglia = int(filename.split("-")[0])
                        nome = filename.split("-")[1]
                    # caso solo Nome
                    elif (filename.count("-") == 0):
                        nome = filename
                    descrizione = "Foto di " + nome + " " + str(anno_dict['anno'])
                    filetype = ""
                    if (file.split(".")[1].upper() == "JPG" or file.split(".")[1].upper() == "JPEG"):
                        filetype = "image/jpeg"
                    elif (file.split(".")[1].upper() == "PNG"):
                        filetype = "image/png"
                    # memorizza informazioni
                    if (nMaglia > -1):
                        giocatore["numeroMaglia"] = nMaglia
                    giocatore["nome"] = nome
                    giocatore["descrizione"] = descrizione
                    giocatore["filename"] = descrizione + "." + file.split(".")[1]
                    # ruolo può essere stringa vuota
                    if (ruolo != ""):
                        giocatore["ruolo"] = ruolo
                    giocatore["filetype"] = filetype
                    giocatore["path"] = path
                    # excel mi dice qualcosa in più sul giocatore specifico, lo cerco
                    for i in squadra['giocatori']:
                        excel_giocatore = squadra['giocatori'][i]
                        # se è lo stesso giocatore, salvo le informazioni
                        if (checkName(excel_giocatore['nome'], nome)):
                            if (excel_giocatore['annoNascita'] != "-" and excel_giocatore['annoNascita'] != ""):
                                giocatore['annoNascita'] = int(excel_giocatore['annoNascita'])
                            if (excel_giocatore['punti'] != "-" and excel_giocatore['punti'] != ""):
                                giocatore['punti'] = int(excel_giocatore['punti'])
                            if (excel_giocatore['presenze'] != "-" and excel_giocatore['presenze'] != ""):
                                giocatore['presenze'] = int(excel_giocatore['presenze'])
                            if (excel_giocatore['numeroMaglia'] != "-" and excel_giocatore['numeroMaglia'] != ""):
                                giocatore['numeroMaglia'] = int(excel_giocatore['numeroMaglia'])
                            if (excel_giocatore['ruolo'] != "-" and excel_giocatore['ruolo'] != ""):
                                giocatore['ruolo'] = excel_giocatore['ruolo']
                            if (excel_giocatore['altezza'] != "-" and excel_giocatore['altezza'] != ""):
                                giocatore['altezza'] = atof(str(excel_giocatore['altezza']))
                            squadra['giocatori'].pop(i)
                            break
                    # aggiunge il giocatore alla lista di giocatori
                    giocatori.append(giocatore)
            # se ho ulteriori giocatori da excel (che non hanno foto)
            for i in squadra['giocatori']:
                excel_giocatore = squadra['giocatori'][i]
                giocatore = {}
                # se è lo stesso giocatore
                if (excel_giocatore['nome'] != "" and excel_giocatore['nome'] != "-"):
                    giocatore['nome'] = excel_giocatore['nome']
                if (excel_giocatore['annoNascita'] != "-" and excel_giocatore['annoNascita'] != ""):
                    giocatore['annoNascita'] = int(excel_giocatore['annoNascita'])
                if (excel_giocatore['punti'] != "-" and excel_giocatore['punti'] != ""):
                    giocatore['punti'] = int(excel_giocatore['punti'])
                if (excel_giocatore['presenze'] != "-" and excel_giocatore['presenze'] != ""):
                    giocatore['presenze'] = int(excel_giocatore['presenze'])
                if (excel_giocatore['numeroMaglia'] != "-" and excel_giocatore['numeroMaglia'] != ""):
                    giocatore['numeroMaglia'] = int(excel_giocatore['numeroMaglia'])
                if (excel_giocatore['ruolo'] != "-" and excel_giocatore['ruolo'] != ""):
                    giocatore['ruolo'] = excel_giocatore['ruolo']
                if (excel_giocatore['altezza'] != "-" and excel_giocatore['altezza'] != ""):
                    giocatore['altezza'] = atof(str(excel_giocatore['altezza']))
                giocatori.append(giocatore)
            # memorizzati tutti i giocatori, li inserisce in anno_dict
            anno_dict["giocatori"] = giocatori

            # vice allenatori
            viceAllenatori = []
            with cd("./viceAllenatori"):
                # per ogni viceAllenatore so nome.tipo
                for file in os.listdir(os.getcwd()):
                    vice = {}
                    path = os.path.join(os.getcwd(), file)
                    nome = file.split(".")[0]
                    descrizione = "Foto di " + nome + " " + str(anno_dict['anno'])
                    filetype = ""
                    if (file.split(".")[1].upper() == "JPG" or file.split(".")[1].upper() == "JPEG"):
                        filetype = "image/jpeg"
                    elif (file.split(".")[1].upper() == "PNG"):
                        filetype = "image/png"

                    # memorizza informazioni
                    vice["nome"] = nome
                    vice["ruolo"] = "Vice allenatore"
                    vice["descrizione"] = descrizione
                    vice["filename"] = descrizione + "." + file.split(".")[1]
                    vice["filetype"] = filetype
                    vice["path"] = path
                    # excel mi dice qualcosa in più sul viceAllenatore specifico, lo cerco
                    for i in squadra['viceAllenatori']:
                        excel_vice = squadra['viceAllenatori'][i]
                        # se è lo stesso viceAllenatore, lo rimuovo tra i giocatori noti
                        if (checkName(excel_vice['nome'], nome)):
                            squadra['viceAllenatori'].pop(i)
                            break
                    viceAllenatori.append(vice)
                # aggiungo viceAllenatori mancanti da excel
                for i in squadra['viceAllenatori']:
                    vice = {}
                    excel_vice = squadra['viceAllenatori'][i]
                    if (excel_vice['nome'] != "" and excel_vice['nome'] != "-"):
                        vice['nome'] = excel_vice['nome']
                    viceAllenatori.append(vice)
                # memorizzati tutti i giocatori, li inserisce in anno_dict
                anno_dict["viceAllenatori"] = viceAllenatori

            # management
            management = []
            with cd("./management"):
                for file in os.listdir(os.getcwd()):
                    assistente = {}
                    path = os.path.join(os.getcwd(), file)
                    nome = file.split(".")[0]
                    ruolo = ""
                    if (nome.count("-") == 1):
                        ruolo = nome.split("-")[0]
                        nome = nome.split("-")[1]
                    descrizione = "Foto di " + nome + " " + str(anno_dict['anno'])
                    filetype = ""
                    if (file.split(".")[1].upper() == "JPG" or file.split(".")[1].upper() == "JPEG"):
                        filetype = "image/jpeg"
                    elif (file.split(".")[1].upper() == "PNG"):
                        filetype = "image/png"

                    # memorizza informazioni
                    assistente["nome"] = nome
                    assistente["descrizione"] = descrizione
                    if (ruolo != ""):
                        assistente["ruolo"] = ruolo
                    assistente["filename"] = descrizione + "." + file.split(".")[1]
                    assistente["filetype"] = filetype
                    assistente["path"] = path
                    # aggiunge l'assistente alla lista di assistenti
                    management.append(assistente)
                # memorizzati tutti i giocatori, li inserisce in anno_dict
                anno_dict["management"] = management

            # assistenti
            assistenti = []
            with cd("./assistenti"):
                # per ogni assistente so nome.tipo
                for file in os.listdir(os.getcwd()):
                    assistente = {}
                    path = os.path.join(os.getcwd(), file)
                    nome = file.split(".")[0]
                    ruolo = ""
                    if (nome.count("-") == 1):
                        ruolo = nome.split("-")[0]
                        nome = nome.split("-")[1]
                    descrizione = "Foto di " + nome + " " + str(anno_dict['anno'])
                    filetype = ""
                    if (file.split(".")[1].upper() == "JPG" or file.split(".")[1].upper() == "JPEG"):
                        filetype = "image/jpeg"
                    elif (file.split(".")[1].upper() == "PNG"):
                        filetype = "image/png"

                    # memorizza informazioni
                    assistente["nome"] = nome
                    assistente["descrizione"] = descrizione
                    if (ruolo != ""):
                        assistente["ruolo"] = ruolo
                    assistente["filename"] = descrizione + "." + file.split(".")[1]
                    assistente["filetype"] = filetype
                    assistente["path"] = path
                    # excel mi dice qualcosa in più sul assistente specifico, lo cerco
                    for i in squadra['assistenti']:
                        excel_assistente = squadra['assistenti'][i]
                        # se è lo stesso viceAllenatore, lo rimuovo tra i giocatori noti
                        if (checkName(excel_assistente['nome'], nome)):
                            squadra['assistenti'].pop(i)
                            break
                    # aggiunge l'assistente alla lista di assistenti
                    assistenti.append(assistente)
                # aggiungo assistenti mancanti da excel
                for i in squadra['assistenti']:
                    assistente = {}
                    excel_assistente = squadra['assistenti'][i]
                    if (excel_assistente['nome'] != "" and excel_assistente['nome'] != "-"):
                        assistente['nome'] = excel_assistente['nome']
                    if (excel_assistente['ruolo'] != "" and excel_assistente['ruolo'] != "-"):
                        assistente['ruolo'] = excel_assistente['ruolo']
                    assistenti.append(assistente)

                # memorizzati tutti gli assistenti, li inserisce in anno_dict
                anno_dict["assistenti"] = assistenti

            # galleria
            galleria = []
            with cd("./galleria"):
                # per ogni foto so nomeFoto-Descrizione.tipo
                for file in os.listdir(os.getcwd()):
                    foto = {}
                    path = os.path.join(os.getcwd(), file)
                    filename = file.split(".")[0]
                    nome = ""
                    descrizione = ""
                    if (filename.count("-") == 1):
                        nome = filename.split("-")[0]
                        descrizione = filename.split("-")[1]
                    elif (filename.count("-") == 0):
                        nome = filename
                        descrizione = filename
                    filetype = ""
                    if (file.split(".")[1].upper() == "JPG" or file.split(".")[1].upper() == "JPEG"):
                        filetype = "image/jpeg"
                    elif (file.split(".")[1].upper() == "PNG"):
                        filetype = "image/png"

                    # memorizza informazioni
                    foto["nome"] = nome
                    foto["descrizione"] = descrizione
                    foto["filename"] = descrizione + "." + file.split(".")[1]
                    foto["filetype"] = filetype
                    foto["path"] = path
                    # aggiunge l'assistente alla lista di assistenti
                    galleria.append(foto)
                # memorizzati tutte le foto, li inserisce in anno_dict
                anno_dict["galleria"] = galleria

            # statistiche
            with cd("./statistica"):
                # statistica del tipo nome.pdf
                statistic = {}
                if (len(os.listdir(os.getcwd())) > 0):
                    file = os.listdir(os.getcwd())[0]
                    path = os.path.join(os.getcwd(), file)
                    nome = file.split(".")[0]
                    filetype = "document/pdf"
                    # memorizza informazioni
                    statistic["nome"] = nome
                    statistic["descrizione"] = nome
                    statistic["filename"] = nome + "." + file.split(".")[1]
                    statistic["filetype"] = filetype
                    statistic["path"] = path
                # memorizzati tutte le statistiche, li inserisce in anno_dict
                anno_dict["statistica"] = statistic

            # attivitaGiovanile
            attivitaGiovanile = []
            with cd("./attivitaGiovanile"):
                # per ogni att so nome.pdf o nome.jpg
                for file in os.listdir(os.getcwd()):
                    att = {}
                    path = os.path.join(os.getcwd(), file)
                    nome = file.split(".")[0]
                    filetype = ""
                    if (file.split(".")[1].upper() == "JPG" or file.split(".")[1].upper() == "JPEG"):
                        filetype = "image/jpeg"
                    elif (file.split(".")[1].upper() == "PNG"):
                        filetype = "image/png"
                    elif (file.split(".")[1].upper() == "PDF"):
                        filetype = "document/pdf"
                    # memorizza informazioni
                    att["nome"] = nome
                    att["descrizione"] = nome
                    att["filename"] = nome + "." + file.split(".")[1]
                    att["filetype"] = filetype
                    att["path"] = path
                    # aggiunge la att alla lista di attivitaGiovanili
                    attivitaGiovanile.append(att)
                # memorizzati tutte le att, li inserisce in anno_dict
                anno_dict["attivitaGiovanile"] = attivitaGiovanile

            # rassegnaStampa
            rassegneStampa = []
            with cd("./rassegnaStampa"):
                # per ogni rassegna Stampa so nome.pdf
                if (len(os.listdir(os.getcwd())) > 0):
                    stampa = {}
                    file = os.listdir(os.getcwd())[0]
                    path = os.path.join(os.getcwd(), file)
                    nome = file.split(".")[0]
                    filetype = "document/pdf"
                    # memorizza informazioni
                    stampa["nome"] = nome
                    stampa["descrizione"] = nome
                    stampa["filename"] = nome + "." + file.split(".")[1]
                    stampa["filetype"] = filetype
                    stampa["path"] = path
                    rassegneStampa.append(stampa)
                # memorizzati tutte le att, li inserisce in anno_dict
                anno_dict["rassegnaStampa"] = rassegneStampa
        
        # 4.a) Salva informazioni in ./INPUT
        input_file = open("./INPUT/" + str(anno_dict['anno'])+".json", "w")
        json.dump(anno_dict, input_file, indent=4)
        input_file.close()
        

        # 5) connette a contentful
        client = Client('CFPAT-5BLAuJOxBs5VBHW19O4-CrZ7EMbwGV6s0hr93laB21Q')
        jSpace = client.spaces().find('c8y62hpixye3')
        print("\n" + client.users().me().email + " logged in\nSpace: " + jSpace.name + "\n")
        # retrieve master environment
        environment = jSpace.environments().find('master-2021-04-18')
        # retrieve all periodi online
        periodi_content_type = environment.content_types().find('periodo')
        # 6) creo nuova squadra
        squadra_entry_attributes = {}
        squadra_entry_fields = {}

        # 6.a) nome squadra
        name = str(anno_dict['nomeSquadra']) + " " + str(anno_dict['anno'])
        squadra_entry_fields['nome'] = {
            'it-IT': name
        }
        # 6.a) slug squadra
        slug = slugify(name)
        squadra_entry_fields['slug'] = {
            'it-IT': slug
        }
        # 6.a) campionato squadra
        campionato = anno_dict['campionato']
        squadra_entry_fields['campionato'] = {
            'it-IT': campionato
        }
        print("Inserimento squadra" ,name)
        print()
        # publish of an asset is an async process --> add them to this list and at the end of the program publish them all 
        foto_to_be_published = []

        # 6.b) foto squadra
        if (len(anno_dict['fotoSquadra']) > 0):
            print("Inserimento Foto di squadra", anno_dict['fotoSquadra']['nome'])
            foto_squadra_upload = None
            foto_squadra_asset = None
            try:
                foto_squadra_upload = jSpace.uploads().create(anno_dict['fotoSquadra']['path'])
                foto_squadra_asset = environment.assets().create(None, {
                    'fields': {
                        'title': {
                            'it-IT': anno_dict['fotoSquadra']['nome']
                        },
                        'description': {
                            'it-IT': anno_dict['fotoSquadra']['nome']
                        },
                        'file': {
                            'it-IT': {
                                'fileName': anno_dict['fotoSquadra']['filename'],
                                'contentType': anno_dict['fotoSquadra']['filetype'],
                                'uploadFrom': foto_squadra_upload.to_link().to_json()
                            }
                        }
                    }
                })
                foto_squadra_asset.process()
            except Exception as e:
                print("!!!!!!!!! Error uploading foto SQUADRA")
                print(e)
                sys.exit(1)
            else:
                foto_to_be_published.append(foto_squadra_asset)
                print("    > Foto caricata")
            squadra_entry_fields['foto'] = {
                'it-IT': foto_squadra_asset.to_link().to_json()
            }

        sleep(1)
        # 6.c) giocatori
        if (len(anno_dict['giocatori']) > 0):
            giocatori = []
            index = 0
            for giocatore_locale in anno_dict['giocatori']:
                sleep(0.5)
                print()
                print("Inserimento giocatore", giocatore_locale['nome'])
                # controlla esistenza persona
                persona_id = findPersona(persone_db, giocatore_locale['nome'])
                if (persona_id == False):
                    # Se la persona non esiste --> Crea persona
                    persona_fields = {
                        'nome': {
                            'it-IT': giocatore_locale['nome']
                        }
                    }
                    if ('annoNascita' in giocatore_locale and giocatore_locale['annoNascita'] != '-'):
                        persona_fields['annoNascita'] = {
                            'it-IT': giocatore_locale['annoNascita']
                        }
                        
                    persona_attributes = {
                        'content_type_id': 'persona',
                        'fields': persona_fields
                    }
                    print("   > Creazione persona")
                    persona = None
                    persona = environment.entries().create(None, persona_attributes)
                    persona.save()
                    persona.publish()
                    persona_id = persona.sys['id']
                    addPersona(persone_db, giocatore_locale['nome'], persona_id, persone_index_dict)
                    print("   > Persona creata e pubblicata correttamente")

                #inserire entry con persona link.id = esiste_persona
                giocatore_fields= {
                    'nome': {
                        'it-IT': giocatore_locale['nome'] + " " + str(anno_dict['anno'])
                    },
                    'persona': {
                        'it-IT': {
                            'sys': {
                                'type': 'Link',
                                'linkType': 'Entry',
                                'id': persona_id
                            }
                        }
                    }
                }
                #inserire entry con numeroMaglia
                if ('numeroMaglia' in giocatore_locale and giocatore_locale['numeroMaglia'] != "-"):
                    giocatore_fields['numeroMaglia'] = {
                        'it-IT': giocatore_locale['numeroMaglia']
                    }
                #inserire entry con punti
                if ('punti' in giocatore_locale and giocatore_locale['punti'] != "-"):
                    giocatore_fields['punti'] = {
                        'it-IT': giocatore_locale['punti']
                    }
                #inserire entry con presenze
                if ('presenze' in giocatore_locale and giocatore_locale['presenze'] != "-"):
                    giocatore_fields['presenze'] = {
                        'it-IT': giocatore_locale['presenze']
                    }
                #inserire entry con ruolo
                if ('ruolo' in giocatore_locale and giocatore_locale['ruolo'] != "-"):
                    giocatore_fields['ruolo'] = {
                        'it-IT': giocatore_locale['ruolo']
                    }
                if ('altezza' in giocatore_locale and giocatore_locale['altezza'] != "-"):
                    giocatore_fields['altezza'] = {
                        'it-IT': giocatore_locale['altezza']
                    }
                # caricare asset e inserire entry con foto
                if ('path' in giocatore_locale and giocatore_locale['path'] != "-"):
                    print("   > Caricamento foto giocatore")
                    foto_giocatore_upload = None
                    foto_giocatore_asset = None
                    try:
                        foto_giocatore_upload = jSpace.uploads().create(giocatore_locale['path'])
                        foto_giocatore_asset = environment.assets().create(None, {
                            'fields': {
                                'title': {
                                    'it-IT': giocatore_locale['descrizione']
                                },
                                'description': {
                                    'it-IT': giocatore_locale['descrizione']
                                },
                                'file': {
                                    'it-IT': {
                                        'fileName': giocatore_locale['filename'],
                                        'contentType': giocatore_locale['filetype'],
                                        'uploadFrom': foto_giocatore_upload.to_link().to_json()
                                    }
                                }
                            }
                        })
                        foto_giocatore_asset.process()
                    except Exception as e:
                        print("!!!!!!!!! Error uploading FOTO GIOCATORE")
                        print(e)
                        sys.exit(1)
                    else:
                        foto_to_be_published.append(foto_giocatore_asset)
                        print("   > Foto caricata correttamente")
                    giocatore_fields['foto'] = {
                        'it-IT': foto_giocatore_asset.to_link().to_json()
                    }
                giocatore_attributes = {
                    'content_type_id': 'giocatore',
                    'fields': giocatore_fields
                }
                print("   > Creazione entry giocatore")
                giocatore = None
                giocatore = environment.entries().create(None, giocatore_attributes)
                giocatore.save()
                giocatore.publish()
                print("Entry giocatore creata e pubblicata correttamente")
                #inserire giocatore in lista giocatori squadra
                giocatori.append(giocatore.to_link().to_json())
                index += 1
            # inserisce giocatori in squadra
            squadra_entry_fields['giocatori'] = {
                'it-IT': giocatori
            }
        
        sleep(1)
        # 6.d) allenatore
        if (len(anno_dict['allenatore']) > 0):
            sleep(0.5)
            allenatore_locale = anno_dict['allenatore']
            print()
            print("Inserimento allenatore", allenatore_locale['nome'])
            # controlla esistenza persona
            persona_id = findPersona(persone_db, allenatore_locale['nome'])
            # Crea persona
            if (persona_id == False):
                #inserire entry con persona link.id = esiste_persona
                persona_attributes = {
                    'content_type_id': 'persona',
                    'fields': {
                        'nome': {
                            'it-IT': allenatore_locale['nome']
                        },
                    }
                }
                print("   > Creazione persona")
                persona = None
                persona = environment.entries().create(None, persona_attributes)
                persona.save()
                persona.publish()
                persona_id = persona.sys['id']
                addPersona(persone_db, allenatore_locale['nome'], persona_id, persone_index_dict)
                print("   > Persona creata e pubblicata correttamente")

            allenatore_fields= {
                'nome': {
                    'it-IT': allenatore_locale['nome'] + " " + str(anno_dict['anno'])
                },
                'persona': {
                    'it-IT': {
                        'sys': {
                            'type': 'Link',
                            'linkType': 'Entry',
                            'id': persona_id
                        }
                    }
                }
            }
            #inserire entry con ruolo
            if ('ruolo' in allenatore_locale and allenatore_locale['ruolo'] != "-"):
                allenatore_fields['ruolo'] = {
                    'it-IT': allenatore_locale['ruolo']
                }
            # caricare asset e inserire entry con foto
            if ('path' in allenatore_locale and allenatore_locale['path'] != "-"):
                print("   > Caricamento foto allenatore")
                foto_allenatore_upload = None
                foto_allenatore_asset = None
                try:
                    foto_allenatore_upload = jSpace.uploads().create(allenatore_locale['path'])
                    foto_allenatore_asset = environment.assets().create(None, {
                        'fields': {
                            'title': {
                                'it-IT': allenatore_locale['descrizione']
                            },
                            'description': {
                                'it-IT': allenatore_locale['descrizione']
                            },
                            'file': {
                                'it-IT': {
                                    'fileName': allenatore_locale['filename'],
                                    'contentType': allenatore_locale['filetype'],
                                    'uploadFrom': foto_allenatore_upload.to_link().to_json()
                                }
                            }
                        }
                    })
                    foto_allenatore_asset.process()
                except Exception as e:
                    print("!!!!!!!!! Error uploading foto ALLENATORE")
                    print(e)
                    sys.exit(1)
                else:
                    foto_to_be_published.append(foto_allenatore_asset)
                    print("   > Foto caricata correttamente")
                allenatore_fields['foto'] = {
                    'it-IT': foto_allenatore_asset.to_link().to_json()
                }
            allenatore_attributes = {
                'content_type_id': 'coach',
                'fields': allenatore_fields
            }
            print("   > Creazione entry allenatore")
            allenatore = None
            allenatore = environment.entries().create(None, allenatore_attributes)
            allenatore.save()
            allenatore.publish()
            print("Entry allenatore creata e pubblicata correttamente")   
            # inserisce allenatore in squadra
            squadra_entry_fields['allenatore'] = {
                'it-IT': allenatore.to_link().to_json()
            }

        sleep(1)
        # 6.e) viceallenatori
        if (len(anno_dict['viceAllenatori']) > 0):
            viceallenatori = []
            index = 0
            for allenatore_locale in anno_dict['viceAllenatori']:
                sleep(0.5)
                print()
                print("Inserimento vice allenatore", allenatore_locale['nome'])
                # controlla esistenza persona
                persona_id = findPersona(persone_db, allenatore_locale['nome'])
                # Crea persona
                if (persona_id == False):
                    #inserire entry con persona link.id = esiste_persona
                    persona_attributes = {
                        'content_type_id': 'persona',
                        'fields': {
                            'nome': {
                                'it-IT': allenatore_locale['nome']
                            },
                        }
                    }
                    print("   > Creazione persona")
                    persona = None
                    persona = environment.entries().create(None, persona_attributes)
                    persona.save()
                    persona.publish()
                    persona_id = persona.sys['id']
                    addPersona(persone_db, allenatore_locale['nome'], persona_id, persone_index_dict)
                    print("   > Persona creata e pubblicata correttamente")

                allenatore_fields= {
                    'nome': {
                        'it-IT': allenatore_locale['nome'] + " " + str(anno_dict['anno'])
                    },
                    'persona': {
                        'it-IT': {
                            'sys': {
                                'type': 'Link',
                                'linkType': 'Entry',
                                'id': persona_id
                            }
                        }
                    }
                }
                #inserire entry con ruolo
                if ('ruolo' in allenatore_locale and allenatore_locale['ruolo'] != "-"):
                    allenatore_fields['ruolo'] = {
                        'it-IT': allenatore_locale['ruolo']
                    }
                # caricare asset e inserire entry con foto
                if ('path' in allenatore_locale and allenatore_locale['path'] != "-"):
                    print("   > Caricamento foto vice allenatore")
                    foto_allenatore_upload = None
                    foto_allenatore_asset = None
                    try:
                        foto_allenatore_upload = jSpace.uploads().create(allenatore_locale['path'])
                        foto_allenatore_asset = environment.assets().create(None, {
                            'fields': {
                                'title': {
                                    'it-IT': allenatore_locale['descrizione']
                                },
                                'description': {
                                    'it-IT': allenatore_locale['descrizione']
                                },
                                'file': {
                                    'it-IT': {
                                        'fileName': allenatore_locale['filename'],
                                        'contentType': allenatore_locale['filetype'],
                                        'uploadFrom': foto_allenatore_upload.to_link().to_json()
                                    }
                                }
                            }
                        })
                        foto_allenatore_asset.process()
                        # it might take a few seconds for the asset processing to complete
                    except Exception as e:
                        print("!!!!!!!!! Error uploading foto ALLENATORE")
                        print(e)
                        sys.exit(1)
                    else:
                        foto_to_be_published.append(foto_allenatore_asset)
                        print("   > Foto vice allenatore caricata correttamente")

                    allenatore_fields['foto'] = {
                        'it-IT': foto_allenatore_asset.to_link().to_json()
                    }
                allenatore_attributes = {
                    'content_type_id': 'coach',
                    'fields': allenatore_fields
                }
                print("   > Creazione entry vice allenatore")
                allenatore = None
                allenatore = environment.entries().create(None, allenatore_attributes)
                allenatore.save()
                allenatore.publish()
                print("Entry Vice allenatore creata e pubblicata correttamente")
                #inserire viceallenatore in lista viceallenatori squadra
                viceallenatori.append(allenatore.to_link().to_json())
                index += 1
            # inserisce viceallenatori in squadra
            squadra_entry_fields['viceAllenatori'] = {
                'it-IT': viceallenatori
            }

        sleep(1)
        # 6.e) assistenti
        if (len(anno_dict['assistenti']) > 0):
            assistenti = []
            index = 0
            for assistente_locale in anno_dict['assistenti']:
                sleep(0.5)
                print()
                print("Inserimento Assistente", assistente_locale['nome'])
                # controlla esistenza persona
                persona_id = findPersona(persone_db, assistente_locale['nome'])
                # Crea persona
                if (persona_id == False):
                    #inserire entry con persona link.id = esiste_persona
                    persona_attributes = {
                        'content_type_id': 'persona',
                        'fields': {
                            'nome': {
                                'it-IT': assistente_locale['nome']
                            },
                        }
                    }
                    print("   > Creazione persona")
                    persona = None
                    persona = environment.entries().create(None, persona_attributes)
                    persona.save()
                    persona.publish()
                    persona_id = persona.sys['id']
                    addPersona(persone_db, assistente_locale['nome'], persona_id, persone_index_dict)
                    print("   > Persona creata e pubblicata correttamente")

                assistente_fields= {
                    'nome': {
                        'it-IT': assistente_locale['nome'] + " " + str(anno_dict['anno'])
                    },
                    'persona': {
                        'it-IT': {
                            'sys': {
                                'type': 'Link',
                                'linkType': 'Entry',
                                'id': persona_id
                            }
                        }
                    }
                }
                #inserire entry con ruolo
                if ('ruolo' in assistente_locale and assistente_locale['ruolo'] != "-"):
                    assistente_fields['ruolo'] = {
                        'it-IT': assistente_locale['ruolo']
                    }
                # caricare asset e inserire entry con foto
                if ('path' in assistente_locale and assistente_locale['path'] != "-"):
                    foto_assistente_upload = None
                    foto_assistente_asset = None
                    print("   > Caricamento foto assistente")
                    try:
                        foto_assistente_upload = jSpace.uploads().create(assistente_locale['path'])
                        foto_assistente_asset = environment.assets().create(None, {
                            'fields': {
                                'title': {
                                    'it-IT': assistente_locale['descrizione']
                                },
                                'description': {
                                    'it-IT': assistente_locale['descrizione']
                                },
                                'file': {
                                    'it-IT': {
                                        'fileName': assistente_locale['filename'],
                                        'contentType': assistente_locale['filetype'],
                                        'uploadFrom': foto_assistente_upload.to_link().to_json()
                                    }
                                }
                            }
                        })
                        foto_assistente_asset.process()
                    except Exception as e:
                        print("!!!!!!!!! Error uploading foto ASSISTENTE")
                        print(e)
                        sys.exit(1)
                    else:
                        foto_to_be_published.append(foto_assistente_asset)
                        print("   > Foto assistente caricata correttamente")
                        assistente_fields['foto'] = {
                            'it-IT': foto_assistente_asset.to_link().to_json()
                        }
                assistente_attributes = {
                    'content_type_id': 'coach',
                    'fields': assistente_fields
                }
                print("   > Creazione entry assistente")
                assistente = None
                assistente = environment.entries().create(None, assistente_attributes)
                assistente.save()
                assistente.publish()
                print("Entry assistente creata e pubblicata correttamente")
                #inserire assistente in lista assistenti squadra
                assistenti.append(assistente.to_link().to_json())
                index += 1
            # inserisce assistenti in squadra
            squadra_entry_fields['assistenti'] = {
                'it-IT': assistenti
            }
        
        sleep(1)
        # 6.e) management
        if (len(anno_dict['management']) > 0):
            managers = []
            index = 0
            for manager_locale in anno_dict['management']:
                sleep(0.5)
                print()
                print("Inserimento manager", manager_locale['nome'])
                # controlla esistenza persona
                persona_id = findPersona(persone_db, manager_locale['nome'])
                # Crea persona
                if (persona_id == False):
                    #inserire entry con persona link.id = esiste_persona
                    persona_attributes = {
                        'content_type_id': 'persona',
                        'fields': {
                            'nome': {
                                'it-IT': manager_locale['nome']
                            },
                        }
                    }
                    print("   > Creazione persona")
                    persona = None
                    persona = environment.entries().create(None, persona_attributes)
                    persona.save()
                    persona.publish()
                    persona_id = persona.sys['id']
                    addPersona(persone_db, manager_locale['nome'], persona_id, persone_index_dict)
                    print("   > Persona creata e pubblicata correttamente")

                manager_fields= {
                    'nome': {
                        'it-IT': manager_locale['nome'] + " " + str(anno_dict['anno'])
                    },
                    'persona': {
                        'it-IT': {
                            'sys': {
                                'type': 'Link',
                                'linkType': 'Entry',
                                'id': persona_id
                            }
                        }
                    }
                }
                #inserire entry con ruolo
                if ('ruolo' in manager_locale and manager_locale['ruolo'] != "-"):
                    manager_fields['ruolo'] = {'it-IT': manager_locale['ruolo']}
                # caricare asset e inserire entry con foto
                if ('path' in manager_locale and manager_locale['path'] != "-"):
                    print("   > Caricamento foto manager")
                    foto_manager_upload = None
                    foto_manager_asset = None
                    try:
                        foto_manager_upload = jSpace.uploads().create(manager_locale['path'])
                        foto_manager_asset = environment.assets().create(None, {
                            'fields': {
                                'title': {
                                    'it-IT': manager_locale['descrizione']
                                },
                                'description': {
                                    'it-IT': manager_locale['descrizione']
                                },
                                'file': {
                                    'it-IT': {
                                        'fileName': manager_locale['filename'],
                                        'contentType': manager_locale['filetype'],
                                        'uploadFrom': foto_manager_upload.to_link().to_json()
                                    }
                                }
                            }
                        })
                        foto_manager_asset.process()
                    except Exception as e:
                        print("!!!!!!!!! Error uploading foto MANAGER")
                        print(e)
                        sys.exit(1)
                    else:
                        foto_to_be_published.append(foto_manager_asset)
                        print("   > Foto Manager caricata correttamente")
                    manager_fields['foto'] = {
                        'it-IT': foto_manager_asset.to_link().to_json()
                    }
                manager_attributes = {
                    'content_type_id': 'management',
                    'fields': manager_fields
                }
                print("   > Creazione entry manager")
                manager = None
                manager = environment.entries().create(None, manager_attributes)
                manager.save()
                manager.publish()
                print("Entry manager creata e pubblicata correttamente")
                #inserire managers in lista assistenti squadra
                managers.append(manager.to_link().to_json())
                index += 1
            # inserisce managers in squadra
            squadra_entry_fields['management'] = {
                'it-IT': managers
            }

        sleep(1)
        # inserimento file statistica
        if (len(anno_dict['statistica']) > 0):
            print()
            sleep(0.5)
            print("Inserimento statistica", anno_dict['statistica']['nome'])
            # caricare asset e inserire entry con foto
            print("   > Caricamento file statistica")
            statistica_upload = None
            statistica_asset = None
            try:
                statistica_upload = jSpace.uploads().create(anno_dict['statistica']['path'])
                statistica_asset = environment.assets().create(None, {
                    'fields': {
                        'title': {
                            'it-IT': anno_dict['statistica']['descrizione']
                        },
                        'description': {
                            'it-IT': anno_dict['statistica']['descrizione']
                        },
                        'file': {
                            'it-IT': {
                                'fileName': anno_dict['statistica']['filename'],
                                'contentType': anno_dict['statistica']['filetype'],
                                'uploadFrom': statistica_upload.to_link().to_json()
                            }
                        }
                    }
                })
                statistica_asset.process()
            except Exception as e:
                print("!!!!!!!!! Error uploading file STATISTICA")
                print(e)
                sys.exit(1)
            else:
                foto_to_be_published.append(statistica_asset)
                print("   > Statistica creata e pubblicata correttamente")
            # inserisce statistica in squadra
            squadra_entry_fields['statistica'] = {
                'it-IT': statistica_asset.to_link().to_json()
            }

        sleep(1)
        # inserimento foto galleria
        if (len(anno_dict['galleria']) > 0):
            galleria = []
            index = 0
            for foto_locale in anno_dict['galleria']:
                sleep(0.5)
                print()
                print("Inserimento foto", foto_locale['nome'])
                # caricare asset e inserire entry con foto
                print("   > Caricamento foto galleria")
                foto_upload = None
                foto_asset = None
                try:
                    foto_upload = jSpace.uploads().create(foto_locale['path'])
                    foto_asset = environment.assets().create(None, {
                        'fields': {
                            'title': {
                                'it-IT': foto_locale['descrizione']
                            },
                            'description': {
                                'it-IT': foto_locale['descrizione']
                            },
                            'file': {
                                'it-IT': {
                                    'fileName': foto_locale['filename'],
                                    'contentType': foto_locale['filetype'],
                                    'uploadFrom': foto_upload.to_link().to_json()
                                }
                            }
                        }
                    })
                    foto_asset.process()
                except Exception as e:
                    print("!!!!!!!!! Error uploading foto GALLERIA")
                    print(e)
                    sys.exit(1)
                else:
                    foto_to_be_published.append(foto_asset)
                    print("   > Foto creata e pubblicata correttamente")
                galleria.append(foto_asset.to_link().to_json())
                index += 1
            # inserisce galleria in squadra
            squadra_entry_fields['galleria'] = {
                'it-IT': galleria
            }

        sleep(1)
        # inserimento foto attivitaGiovanile
        if (len(anno_dict['attivitaGiovanile']) > 0):
            attivitas = []
            index = 0
            for file_locale in anno_dict['attivitaGiovanile']:
                sleep(0.5)
                print()
                print("Inserimento Attivita Giovanile", file_locale['nome'])
                # caricare asset e inserire entry con foto
                print("   > Caricamento file")
                file_upload = None
                file_asset = None
                try:
                    file_upload = jSpace.uploads().create(file_locale['path'])
                    file_asset = environment.assets().create(None, {
                        'fields': {
                            'title': {
                                'it-IT': file_locale['descrizione']
                            },
                            'description': {
                                'it-IT': file_locale['descrizione']
                            },
                            'file': {
                                'it-IT': {
                                    'fileName': file_locale['filename'],
                                    'contentType': file_locale['filetype'],
                                    'uploadFrom': file_upload.to_link().to_json()
                                }
                            }
                        }
                    })
                    file_asset.process()
                except Exception as e:
                    print("!!!!!!!!! Error uploading file ATTIVITA GIOVANILE")
                    print(e)
                    sys.exit(1)
                else:
                    foto_to_be_published.append(file_asset)
                    print("   > File creato e pubblicata correttamente")
                attivitas.append(file_asset.to_link().to_json())
                index += 1
            # inserisce attivitaGiovanile in squadra
            squadra_entry_fields['attivitaGiovanile'] = {
                'it-IT': attivitas
            }
            
        sleep(1)
        # inserimento foto rassegnaStampa
        if (len(anno_dict['rassegnaStampa']) > 0):
            stampas = []
            index = 0
            for file_locale in anno_dict['rassegnaStampa']:
                sleep(0.5)
                print()
                print("Inserimento Rassegna Stampa", file_locale['nome'])
                # caricare asset e inserire entry con foto
                print("   > Caricamento file")
                file_upload = None
                file_asset = None
                try:
                    file_upload = jSpace.uploads().create(file_locale['path'])
                    file_asset = environment.assets().create(None, {
                        'fields': {
                            'title': {
                                'it-IT': file_locale['descrizione']
                            },
                            'description': {
                                'it-IT': file_locale['descrizione']
                            },
                            'file': {
                                'it-IT': {
                                    'fileName': file_locale['filename'],
                                    'contentType': file_locale['filetype'],
                                    'uploadFrom': file_upload.to_link().to_json()
                                }
                            }
                        }
                    })
                    file_asset.process()
                except Exception as e:
                    print("!!!!!!!!! Error uploading file RASSEGNA STAMPA")
                    print(e)
                    sys.exit(1)
                else:
                    foto_to_be_published.append(file_asset)
                    print("   > Rassegna stampa creata e pubblicata correttamente")
                stampas.append(file_asset.to_link().to_json())
                index += 1
            # inserisce rassegnaStampa in squadra
            squadra_entry_fields['rassegnaStampa'] = {
                'it-IT': stampas
            }

        #-------------------------PUBLISHING PROCESSED FILES--------------------------------
        print()
        for photo in foto_to_be_published:
            try:
                environment.assets().find(photo.sys['id']).publish()
            except Exception as e:
                print('!!!!! Error Publishing Contentful Asset')
                print(e)
                sys.exit(1)
            else:
                print("===== Contentful Upload and Publish Complete =====")

        #-------------------------CREAZIONE SQUADRA-----------------------------------------
        print()
        print("Creazione entry squadra")
        squadra_entry_attributes = {
            'content_type_id': 'squadra',
            'fields': squadra_entry_fields
        }

        # Salvo informazioni in ./OUTPUT
        output_file = open("./OUTPUT/" + str(anno_dict['anno'])+".json", "w")
        json.dump(squadra_entry_attributes, output_file, indent=4)
        output_file.close()

        squadra = environment.entries().create(None, squadra_entry_attributes)
        squadra.save()
        squadra.publish()
        addSquadra(squadre_db, name, squadra.sys['id'], squadre_index_dict)
        print("Squadra creata e pubblicata correttamente")

        # salvo squadra in anno
        squadre = []
        squadre.append(squadra.to_link().to_json())

        anno_fields = {
            'anno': {
                'it-IT': str(anno_dict['anno']),
            },
            'squadre': {
                'it-IT': squadre
            }
        }
        anno_attributes = {
            'content_type_id': 'anno',
            'fields': anno_fields
        }
        anno = environment.entries().create(None, anno_attributes)
        anno.save()
        anno.publish()
        
        # trova periodo dell'anno
        periodi =[{'start': 1963, 'end': 1970}]
        i = 1971
        while i < 2021:
            start = i
            if (i % 10 == 0):
                i += 1
                continue
            else:
                i += 9
            end = i
            periodi.append({'start': start, 'end': end})
        periodi.append({'start': 2021, 'end': 2021})

        for periodo_r in periodi:
            if (anno_dict['anno'] >= periodo_r['start'] and anno_dict['anno'] <= periodo_r['end']):
                nome = str(periodo_r['start'])+'-'+str(periodo_r['end'])
                periodo_id = findPeriodo(periodi_db, nome)
                # salvo anno in periodo
                if (periodo_id != False):
                    periodo = periodi_content_type.entries().find(periodo_id)
                    periodo_raw = periodo.raw
                    if ("anni" in periodo_raw['fields']):
                        periodo_raw['fields']['anni']['it-IT'].append(anno.to_link().to_json())
                    else:
                        periodo_raw['fields']['anni']= {
                            'it-IT': [anno.to_link().to_json()]
                        }
                    periodo.update(periodo_raw)
                    periodo.save()
                    periodo.publish()
        

        # salvo indice scrittura persone
        persone_off_dict[0]['index'] = persone_index_dict['index']
        file = open("persone-last-index.json", "w")
        json.dump(persone_off_dict, file, indent=4)
        file.close()
        # salvo indice scrittura squadre
        squadre_off_dict[0]['index'] = squadre_index_dict['index']
        file = open("squadre-last-index.json", "w")
        json.dump(squadre_off_dict, file, indent=4)
        file.close()

if __name__ == "__main__":
    main()
