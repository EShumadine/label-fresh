import dbi

def getConn(db):
    '''Returns a database connection for that db'''
    dsn = dbi.read_cnf()
    conn = dbi.connect(dsn)
    conn.select_db(db)
    return conn

def insertReport(conn, infoDict):
    '''Inserts a report into the report table given a database connection
    and a dictionary of values. Returns the unique ID of the just-inserted
    report.'''
    curs = dbi.cursor(conn)
    # I need the insert and select statement to happen atomically, otherwise
    # a concurrent insert could cause the returned id to be incorrect
    curs.execute('''LOCK TABLES report WRITE''')
    curs.execute('''
        INSERT INTO report(name,meal,served,hall,image,notes,owner)
        VALUES(%s, %s, %s, %s, %s, %s, %s)
        ''', \
        [infoDict['name'], infoDict['meal'], infoDict['served'], \
        infoDict['hall'], infoDict['image'], infoDict['notes'], \
        infoDict['owner']])
    curs.execute('SELECT LAST_INSERT_ID()')
    reportID = curs.fetchone()[0]
    curs.execute('''UNLOCK TABLES''')
    return reportID

def insertLabels(conn, infoDict, reportID, kind):
    '''Inserts the listed and present/followed allergens or diets (depending
    on kind) given by the provided dictionary and associates them with the 
    given ID. Kind can be one of "allergen" or "diet".'''
    curs = dbi.cursor(conn)
    for key in iter(infoDict):
        for entry in infoDict[key]:
            curs.execute('''
                INSERT INTO label(id,code,labeled,kind)
                VALUES(%s, %s, %s, %s)
                ''', \
                [reportID, entry, key, kind])

def getReport(conn, reportID):
    '''Returns the ID, name, date served, dining hall, mealtime, notes, image, 
    and owner of the report specified by ID as a dictionary.'''
    curs = dbi.dictCursor(conn)
    curs.execute('''
                SELECT * FROM report 
                WHERE report.id = %s
                ''', [reportID])
    return curs.fetchone() # ids are unique

def getLabels(conn, reportID):
    '''Returns the labeled/actual allergens/diets for the given report as a 
    list of dictionaries, where each dictionary represents an allergen/diet.'''
    curs = dbi.dictCursor(conn)
    curs.execute('''
                SELECT code,kind,labeled FROM report 
                INNER JOIN label ON (report.id)
                WHERE report.id = %s
                ''', [reportID])
    return curs.fetchall()

def searchReports(conn, name, hall):
    '''Returns a list of all reports matching the given search string anywhere
    within their name. Hall refers to either the one dining hall being searched
    or "All Dining Halls".'''
    curs = dbi.dictCursor(conn)
    if hall != "All Dining Halls": #specific dining hall
        curs.execute('''
                    SELECT id,name,served,meal,hall FROM report
                    WHERE report.name like %s
                    AND report.hall = %s''', \
                    ["%" + name + "%", hall])
    else:
        curs.execute('''
                    SELECT id,name,served,meal,hall FROM report
                    WHERE report.name like %s''', \
                    ["%" + name + "%"])
    return curs.fetchall()

def buildInfoDict(conn, reportID):
    '''Gets the information about a report (specified by ID) from the database
    and returns it as a dictionary, where the listed/actual allergens/diets
    are represented as lists.'''
    reportDict = getReport(conn,reportID)

    labels = getLabels(conn, reportID)
    reportDict['listedAllergens'] = []
    reportDict['actualAllergens'] = []
    reportDict['listedDiets'] = []
    reportDict['actualDiets'] = []
    for label in labels:
        if label['labeled'] == 'listed':
            if label['kind'] == 'allergen': # listed allergen
                reportDict['listedAllergens'].append(label['code'])
            else: # listed diet
                reportDict['listedDiets'].append(label['code'])
        else: # actual
            if label['kind'] == 'allergen': # actual allergen
                reportDict['actualAllergens'].append(label['code'])
            else: # actual diet
                reportDict['actualDiets'].append(label['code'])
    
    return reportDict

def deleteReport(conn, reportID):
    curs = dbi.cursor(conn)
    rows = curs.execute('''
                        DELETE FROM report
                        WHERE id = %s''', [reportID])
    if rows != 1:
        print("deleted " + str(rows) + " rows")
        return False
    else:
        return True
