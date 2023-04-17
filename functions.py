import pandas as pd
import numpy as np
import math  as mt
import random as rd
from IPython.display import display,HTML,clear_output
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://matteo:psswd@localhost:5432/imdb_py")

possibleQuestions = [
    "In quale tra i seguenti film ha recitato {}?",
    "In che anno è stato pubblicato il film \"{}\"?",
    "In quale paese o gruppo di paesi è stato girato il film \"{}\"?",
    "Quale dei seguenti attori ha recitato nel film \"{}\"?"
    ]

#n = numero del quiz, d = la difficoltà 
def firstQuestion(n=0, d=2) : #In quale tra i seguenti film ha recitato {}?"
    if d == 1 : 
        #Seleziono film aventi ricevuto un voto alto, assumendo che in tal modo il quiz coinvolga
        #film maggiormente conosciuti e diventi quindi più facile.
         sql = """
        SELECT official_title, movie.id, year, given_name
        FROM imdb.movie 
        INNER JOIN imdb.crew ON movie.id = crew.movie 
        INNER JOIN imdb.person ON crew.person=person.id
        INNER JOIN imdb.rating ON movie.id=rating.movie
        WHERE crew.p_role = 'actor' AND score > 7
        GROUP BY movie.id, given_name
        """
    else:
        sql = """
        SELECT official_title, movie.id, year, given_name
        FROM imdb.movie 
        INNER JOIN imdb.crew ON movie.id = crew.movie 
        INNER JOIN imdb.person ON crew.person=person.id
        WHERE crew.p_role = 'actor' GROUP BY movie.id, given_name
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
        actor = row['given_name']
        actors.append(actor)
        movies.append(row['official_title'])
        table += "<tr><td style='text-align:left'>" 
        table += str(i+1) + ") " + str(row['official_title'])
        table += "</td></tr>" 
    #quesito
    answerIndex = rd.randint(0,3) #IMPLEMENTARE QUESTA STRATEGIA ANCHE PER ALTRI
    question = possibleQuestions[0].format(actors[answerIndex])
    content = '<tr><th style="color:red; text-align:center">Quiz n°'+ str(n) +'</th></tr><tr><th style="text-align:left">' + question + '</th></tr>'
    content += table
    return content, answerIndex 

def secondQuestion(n=0, d=2): #"In che anno è stato pubblicato il film \"{}\"?"
    table = ""
    if d == 1 :
        sql = """
        SELECT id, official_title, year 
        FROM imdb.movie
        INNER JOIN imdb.rating ON movie.id=rating.movie
        WHERE year notnull AND score > 7
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
    possibilities = np.random.normal(int(year), 6, 2) #genero 2  opzioni del quiz che non si discostano troppo dall'opzione corretta
    superWrong = np.random.normal(int(year), 40,1)[0] #genero opzione mediamente più distante dal valore corretto
    possibilities = np.append(possibilities, [superWrong, year])
    #possibilities = np.append(possibilities, )
    np.random.shuffle(possibilities) #mischio gli elementi dell'array per randomizzare disposizione delle opzioni
    #controllo che non vi siano elemtenti dell'array uguali
    for i  in range(len(possibilities)):
        a = mt.trunc(float(possibilities[i])) #elimino le cifre decimali
        for j  in range(len(possibilities)):     
            b = mt.trunc(float(possibilities[j]))
            if (i != j ) and (a == b) :
                    #se trovo due record uguali sommo 2 ad uno dei due per differenziarlo
                    possibilities[j] = mt.trunc(float(possibilities[i])) + 2
        if (a == int(year)): #if per recuperare l'indice della risposta esatta
            answerIndex = i 
        #costruzione tabella html delle opzioni
        table += "<tr><td style='text-align:left'>"    
        table += str(i+1) + ") " + str(a)
        table += "</td></tr>" 
    question = possibleQuestions[1].format(title)
    content = '<tr><th style="color:red; text-align:center">Quiz n°'+ str(n) +'</th></tr><tr><th style="text-align:left">' + question + '</th></tr>'
    content += table 
    return content, answerIndex

def thirdQuestion(n=0, d=2) : #"In quale paese o gruppo di paesi è stato girato il film \"{}\"?",
    if d == 1:
         sql = """
            SELECT movie.id, official_title, name AS "country_name" 
            FROM imdb.produced INNER JOIN imdb.movie ON movie.id = produced.movie 
            INNER JOIN imdb.country ON produced.country= country.iso3
            INNER JOIN imdb.rating ON movie.id=rating.movie
            WHERE score > 7
            """
    else:
        sql = """
            SELECT movie.id, official_title, name AS "country_name" 
            FROM imdb.produced INNER JOIN imdb.movie ON movie.id = produced.movie 
            INNER JOIN imdb.country ON produced.country= country.iso3
            """
    table = ""
    resultMovies = pd.read_sql(sql, engine)
    allIndex = resultMovies.index #prendo gli indici dal dataframe
    index = rd.choice(allIndex) #scelgo un indice random
    row = resultMovies.loc[index] #scelgo riga in relazione indice indivituato riga prec. PS: con iloc schioppa tutto se index >1000 togliere
    #raggruppo in un data frame le righe con lo stesso film per vedere se ci sono diversi paesi
    rowsWithSameFilm = resultMovies[(resultMovies['official_title'] == row['official_title'])]
    countries = ""
    nCountries = 0
    for z in rowsWithSameFilm['country_name']:
        nCountries += 1
        countries += z + ", "
    #rimuovo ultimi due caratteri corrispondenti ad uno spazio ed un punto ed inserisco un punto
    countries = countries[:-2]
    countries += "."
    coList = [] #lista dei paesi/countries
    coList.append(countries)
    title = row['official_title']
    #gestione opzioni sbagliate:
    #elimino almeno un paese dal df per far in modo di avere opzioni diverse
    resultMovies = resultMovies[(resultMovies['country_name'] != rowsWithSameFilm['country_name'][rd.choice(rowsWithSameFilm.index)])]
    for i in range(3):
        chosen = ""
        for k in range(nCountries): #for per equiparare numero stati tra le varie opzioni
            countryIndex = resultMovies.index
            index = rd.choice(countryIndex)
            chosen += str(resultMovies.loc[index]['country_name']) + ", "
            #tolgo i record con lo stesso nome del paese:
            resultMovies = resultMovies[(resultMovies['country_name'] != resultMovies['country_name'][index])]
        chosen = chosen[:-2]
        chosen += "."  
        coList.append(chosen)
    rd.shuffle(coList)
    for j in range(len(coList)):
        if coList[j] == countries:
            answerIndex = j
        table += "<tr><td style='text-align:left'>" 
        table += str(j+1) + ") " + str(coList[j])
        table += "</td></tr>" 
    question = possibleQuestions[2].format(title)
    content = '<tr><th style="color:red; text-align:center">Quiz n°'+ str(n) +'</th></tr><tr><th style="text-align:left">' + question + '</th></tr>'
    content += table
    return content, answerIndex

def fourthQuestion(n=0, d=2): #"Quale tra i seguenti attori ha recitato nel film \"{}\"?"
    if d == 1 :
        #per la modalità facile genero il quiz partendo da una lista di attori famosi
        famusAct = ["Leonardo DiCaprio", 
                    "Cillian Murphy", 
                    "Anne Hathaway", 
                    "Matt Damon",
                     "Scarlett Johansson", 
                     "Ryan Gosling", 
                     "Ben Affleck", 
                     "Uma Thurman", 
                     "Jason Momoa", 
                     "Tobey Maguire"
                    ]
        sql = """
        SELECT official_title, movie.id, year, given_name
        FROM imdb.movie
        INNER JOIN imdb.crew ON movie.id = crew.movie
        INNER JOIN imdb.rating ON movie.id=rating.movie
        INNER JOIN imdb.person ON crew.person = person.id
        WHERE
        """
        #concateno gli "or" nella query in tal modo se volessi aggiungere altri attori famosi basterebbe inserirli nella lista
        for i in range(len(famusAct)) :
            if (i != len(famusAct) -1) :
                sql += " given_name ='" + famusAct[i] + "' OR"
            else:
                sql += " given_name ='" + famusAct[i] + "'"
        sql += " GROUP BY movie.id, given_name"
    else:
        sql = """
        SELECT official_title, movie.id, year, given_name
        FROM imdb.movie 
        INNER JOIN imdb.crew ON movie.id = crew.movie 
        INNER JOIN imdb.person ON crew.person=person.id
        WHERE crew.p_role = 'actor' GROUP BY movie.id, given_name
        """
    table = ""
    resultMovies = pd.read_sql(sql, engine)
    actors = []
    movies = []
    for i in range(4):
        allIndex = resultMovies.index #prendo gli indici dal dataframe
        index = rd.choice(allIndex)
        row = resultMovies.loc[index]
        movies.append(resultMovies.loc[index]['official_title'])
        chosenAct =  resultMovies.loc[index]['given_name']
        #rimuovo eventuali altri film dove l'attore è presente e righe con stesso film ma diverso attore
        resultMovies = resultMovies[(resultMovies['given_name'] != row['given_name']) & (resultMovies['official_title'] != row['official_title'])] 
        actors.append(chosenAct)
        table += "<tr><td style='text-align:left'>" 
        table += str(i+1) + ") " + str(chosenAct)
        table += "</td></tr>" 
    answerIndex = rd.randint(0,3)
    question = possibleQuestions[3].format(movies[answerIndex])
    content = '<tr><th style="color:red; text-align:center">Quiz n°'+ str(n) +'</th></tr><tr><th style="text-align:left">' + question + '</th></tr>'
    content += table
    return content, answerIndex

def generateQuiz(n=4):
    result = [] 
    inputs = []
    html = ""
    date = ""
    corrette = ""
    points = 0.0
    total = 0.0
    for i in range(n):
        display(HTML('<tr><th text-align:center">Inserire la difficoltà del prossimo quesito.</th></tr><tr><td>1)Facile</td><td>2)Normale</td></td></tr>'))
        while True:
            try:
               diff = int(input("Indicare il numero corrispondente alla difficoltà desiderata\n"))
            except ValueError:
                print("Input non valido, inserire un numero tra 1 e 2.")
                continue
            if diff > 2 or diff < 1:
                print("Inserire un numero tra 1 e 2.")
                continue
            break
        #creo un moltiplicatore in relazione alla difficoltà dela domanda
        if diff == 1:
            molt = 0.5
        else:
            molt = 1
        total += molt
        j = rd.randint(0, len(possibleQuestions) - 1) 
        #j=2
        quizNum = i + 1
        if j == 0:
            result.append(firstQuestion(quizNum, diff))
        if j == 1:
            result.append(secondQuestion(quizNum, diff))
        if j == 2:
            result.append(thirdQuestion(quizNum, diff))
        if j == 3:
            result.append(fourthQuestion(quizNum, diff))
        display(HTML(result[i][0]))
        while True:
            try:
               a = int(input("Indicare il numero della risposta desiderata relativamente al quiz n°" + str(quizNum) +"\n"))
            except ValueError:
                print("Input non valido, inserire un numero intero compreso tra 1 e 4.")
                continue
            if a > 4 or a < 1:
                print("Inserire un numero compreso tra 1 e 4.")
                continue
            break
        inputs.append(a)
        html += result[i][0] 
        points = points + molt if int(result[i][1]+1)==inputs[i] else points + 0
        date += str(inputs[i]) + " "
        corrette += str(result[i][1]+1) + " " 
    print("Risposte date: " + date)
    print("Risposte corrette: " + corrette)
    print("Punteggio: " + str(points) +"/"+ str(total))