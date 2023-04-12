import pandas as pd
import numpy as np
import math  as mt
import random as rd
from IPython.display import display,HTML,clear_output
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://matteo:Ettore2021@localhost:5432/imdb_py")

def firstQuestion(n=0, d=2) :
       #ATTENZIONE È POSSIBILE CHE ESCA PIù VOLTE LO STESSO FILM PROBABILMENTE PERCHè CI SONO RECORD CON STESSO OFFICIAL TITLE MA ATTORE DIVERSO
    #In quale tra i seguenti film ha recitato 
    if d == 1 :
        #Seleziono film aventi ricevuto un voto ed un numero di recensioni alto, assumendo che in tal modo il quiz coinvolga
        #film maggiormente conosciuti e diventi quindi più facile.
         sql = """
        SELECT official_title, movie.id, year, first_name, last_name, given_name
        FROM imdb.movie 
        INNER JOIN imdb.crew ON movie.id = crew.movie 
        INNER JOIN imdb.person ON crew.person=person.id
        INNER JOIN imdb.rating ON movie.id=rating.movie
        WHERE crew.p_role = 'actor' AND first_name notnull AND votes > 80000 AND score > 7
        GROUP BY movie.id, first_name, last_name, given_name
        """
    else:
        sql = """
        SELECT official_title, movie.id, year, first_name, last_name, given_name
        FROM imdb.movie 
        INNER JOIN imdb.crew ON movie.id = crew.movie 
        INNER JOIN imdb.person ON crew.person=person.id
        WHERE crew.p_role = 'actor' AND first_name notnull GROUP BY movie.id, first_name, last_name, given_name
        """
    resultMovies = pd.read_sql(sql, engine)
    resultMovies
    table = "" #inizializzo tabella vuota
    actors = []
    movies = []
    for i in range(4):
        allIndex = resultMovies.index #prendo gli indici dal dataframe
        index = rd.choice(allIndex) #scelgo un indice random
        row = resultMovies.loc[index] #scelgo riga in relazione indice indivituato riga prec. PS: con iloc schioppa tutto se index >1000
        #rimuovo eventuali altri record con lo stesso official_title
        resultMovies = resultMovies[(resultMovies['official_title'] != row['official_title'])] 
        #resultMovies = resultMovies.drop(index, axis=0) #droppo la riga selezionata per evitare di selezionarla nuovamente
        actor = row['first_name'] + " " + row['last_name'] + " (" +  row['given_name'] + ")"
        actors.append(actor)
        movies.append(row['official_title'])
        table += "<tr><td style='text-align:left'>" 
        table += str(i+1) + ") " + str(row['official_title'])
        table += "</td></tr>" 
    #quesito
    answerIndex = rd.randint(0,3) #IMPLEMENTARE QUESTA STRATEGIA ANCHE PER ALTRI
    question = possibleQuest[0].format(actors[answerIndex])
    content = '<tr><th style="color:red; text-align:center">Quiz n°'+ str(n) +'</th></tr><tr><td style="text-align:left">' + question + '</td></tr>'
    content += table
    return content, answerIndex #roba

def secondQuestion(n=0, d=2):
    table = ""
    answerIndex = None
    if d == 1 :
        sql = """
        SELECT id, official_title, year 
        FROM imdb.movie
        INNER JOIN imdb.rating ON movie.id=rating.movie
        WHERE year notnull AND votes > 80000 AND score > 7
        """
    else:
        sql = """
        SELECT id, official_title, year 
        FROM imdb.movie
        WHERE year notnull
        """
    resultMovies = pd.read_sql(sql, engine)
    allIndex = resultMovies.index
    index = rd.choice(allIndex)
    movie = resultMovies.loc[index]
    title = movie['official_title']
    year = movie['year']
    possibilities = np.random.normal(int(year), 6, 2)
    superWrong = np.random.normal(int(year), 30,1)[0]
    possibilities = np.append(possibilities, superWrong)
    possibilities = np.append(possibilities, year)
    np.random.shuffle(possibilities) #mischio gli elementi dell'array per randomizzare disposizione opzioni
    #controllo che non vi siano elemtenti dell'array uguali
    for i  in range(len(possibilities)):
        a = mt.trunc(float(possibilities[i]))
        for j  in range(len(possibilities)):     
            b = mt.trunc(float(possibilities[j]))
            if (i != j ) and (a == b) :
                    possibilities[j] = mt.trunc(float(possibilities[i])) + 2 #DA MIGLIORARE
        if (a == int(year)): #if per recuperare l'indice della risposta esatta
            answerIndex = i 
        table += "<tr><td style='text-align:left'>"    
        table += str(i+1) + ") " + str(a)
        table += "</td></tr>" 
    question = possibleQuest[1].format(title)
    content = '<tr><th style="color:red; text-align:center">Quiz n°'+ str(n) +'</th></tr><tr><td style="text-align:left">' + question + '</td></tr>'
    content += table 
    return content, answerIndex

def thirdQuestion(n=0) : 
    answerIndex = None
    table = ""
    sql = """
    SELECT movie.id, official_title, name AS "country_name" 
    FROM imdb.produced INNER JOIN imdb.movie ON movie.id = produced.movie INNER JOIN imdb.country ON produced.country= country.iso3 
    """
    resultMovies = pd.read_sql(sql, engine)
    resultMovies
    allIndex = resultMovies.index #prendo gli indici dal dataframe
    index = rd.choice(allIndex) #scelgo un indice random
    row = resultMovies.loc[index] #scelgo riga in relazione indice indivituato riga prec. PS: con iloc schioppa tutto se index >1000
    title = row['official_title']
    country = row['country_name']
    #gestione opzioni sbagliate
    sql = """
    SELECT distinct(name) as "country_name" 
    FROM imdb.country where name != '{}'
    """
    sql = sql.format(country)
    resultCountry = pd.read_sql(sql, engine)
    coList = []
    for i in range(3):
        countryIndex = resultCountry.index
        index = rd.choice(countryIndex)
        chosen = resultCountry.loc[index]['country_name']
        resultCountry.drop(index, axis=0)
        coList.append(chosen)
    coList.append(country)
    rd.shuffle(coList)
    for j in range(len(coList)):
        if coList[j] == country:
            answerIndex = j
        table += "<tr><td style='text-align:left'>" 
        table += str(j+1) + ") " + str(coList[j])
        table += "</td></tr>" 
    question = possibleQuest[2].format(title)
    content = '<tr><th style="color:red; text-align:center">Quiz n°'+ str(n) +'</th></tr><tr><td style="text-align:left">' + question + '</td></tr>'
    content += table
    return content, answerIndex


def fourthQuestion(n=0): #"Quale tra i seguenti attori ha recitato nel film \"{}\"?"
    #VERIFICARE CHE VENGANO RIMOSSI CORRETTAMENTE I FILM DOVE HA RECITATO L'ATTORE
    answerIndex = None
    table = ""
    sql = """
    SELECT official_title, movie.id, year, first_name, last_name, given_name
    FROM imdb.movie 
    INNER JOIN imdb.crew ON movie.id = crew.movie 
    INNER JOIN imdb.person ON crew.person=person.id
    WHERE crew.p_role = 'actor' AND first_name notnull GROUP BY movie.id, first_name, last_name, given_name
    """
    resultMovies = pd.read_sql(sql, engine)
    resultMovies
    allIndex = resultMovies.index #prendo gli indici dal dataframe
    index = rd.choice(allIndex) #scelgo un indice random
    row = resultMovies.loc[index] #scelgo riga in relazione indice indivituato riga prec. PS: con iloc schioppa tutto se index >1000
    title = row['official_title']
    actor = row['first_name'] + " " + row['last_name'] + " (" +  row['given_name']  + ")"
    #rimuovo eventuali altri film dove l'attore è presente DA VERIFICARE FUNZIONAMENTO
    resultMovies = resultMovies[(resultMovies['first_name'] != row['first_name']) & (resultMovies['last_name'] != row['last_name'])] 
    actors = []
    for i in range(3):
        allIndex = resultMovies.index #prendo gli indici dal dataframe
        index = rd.choice(allIndex)
        chosenAct =  resultMovies.loc[index]['first_name'] + " " + resultMovies.loc[index]['last_name'] + " (" +  resultMovies.loc[index]['given_name']  + ")"
        resultMovies.drop(index, axis=0)
        actors.append(chosenAct)
    actors.append(actor)
    rd.shuffle(actors)
    for j in range(len(actors)):
        if actors[j] == actor:
            answerIndex = j
        table += "<tr><td style='text-align:left'>" 
        table += str(j+1) + ") " + str(actors[j])
        table += "</td></tr>" 
    question = possibleQuest[3].format(title)
    content = '<tr><th style="color:red; text-align:center">Quiz n°'+ str(n) +'</th></tr><tr><td style="text-align:left">' + question + '</td></tr>'
    content += table
    return content, answerIndex

## DA SISTEMARE DISCORSO CHE DEVO ELIMINARE TUTTI I FILM DOVE C'è QUELL'ATTORE PER EVITARE PIù DI UNA POSSIBILE RISP CORRETTA
#POSSO UTILIZZARE LA list comprehension DA QUALCHE PARTE?
possibleQuest = [
    "In quale tra i seguenti film ha recitato {}?",
    "In che anno è stato pubblicato il film \"{}\"?",
    "Qual è il paese di produzione del film \"{}\"?",
    "Quale dei seguenti attori ha recitato nel film \"{}\"?"
    ]

def generateQuiz():
    display(HTML('<tr><th text-align:center">Selezionare il numero di quesiti che si desidera ricevere.</th></tr>'))
    while True:
            try:
               n = int(input("Indicare un numero maggiore di 0\n"))
            except ValueError:
                print("Input non valido, inserire un numero intero.")
                continue
            if n <= 0:
                print("Inserire un numero maggiore di 0")
                continue
            break
    #SISTEMARE HTML, ORA NON HA SENSO RESTITUIRLO ALLA FINE E CREARE LA TABELLA ALL'INIZIO ED ALLA FINE
    result = [] 
    inputs = []
    html = ""
    correctAns = []
    risp = ""
    cor = ""
    points = 0
    for i in range(n):
        display(HTML('<tr><th text-align:center">Selezionale la difficoltà del prossimo quesito.</th></tr><tr><td>1)Facile</td><td>2)Normale</td></td></tr>'))
        while True:
            try:
               diff = int(input("Indicare il numero corrispondente alla difficoltà desiderata\n"))
            except ValueError:
                print("Input non valido, inserire un numero compreso tra 1 e 2.")
                continue
            if diff > 2 or diff < 1:
                print("Inserire un numero compreso tra 1 e 2.")
                continue
            break
        j = rd.randint(0, len(possibleQuest) - 1) 
        #j=1
        quizNum = i + 1
        if j == 0:
            result.append(firstQuestion(quizNum, diff))
        if j == 1:
            result.append(secondQuestion(quizNum, diff))
        if j == 2:
            result.append(thirdQuestion(quizNum))
        if j == 3:
            result.append(fourthQuestion(quizNum))
        display(HTML(result[i][0]))
        while True:
            try:
               a = int(input("Indicare il numero della risposta desiderata relativamente al quiz n°" + str(quizNum) +"\n"))
            except ValueError:
                print("Input non valido, inserire un numero compreso tra 1 e 4.")
                continue
            if a > 4 or a < 1:
                print("Inserire un numero compreso tra 1 e 4.")
                continue
            break
        inputs.append(a)
        correctAns.append(result[i][1]+1) 
        html += result[i][0] 
        points = points + 1 if int(result[i][1]+1)==inputs[i] else points + 0
        risp += str(inputs[i]) + " "
        cor += str(result[i][1]+1) + " "
    print("Punteggio: " + str(points) +"/"+ str(n))
    print("Risposte date: " + risp)
    print("Risposte corrette: " + cor)
    
    print(correctAns)
    return # html, correctAns