import dbi

def getConn(db):
    '''Returns a database connection for that db'''
    dsn = dbi.read_cnf()
    conn = dbi.connect(dsn)
    conn.select_db(db)
    return conn

def isDuplicate(curs, infoDict):
    '''Returns true if the given report is a duplicate of one already in the
    table, and false otherwise.'''
    curs.execute('''SELECT id FROM report 
                    WHERE name=%s 
                    AND meal=%s
                    AND served=%s
                    AND hall=%s''',
                    [infoDict['name'], infoDict['meal'], infoDict['served'],
                    infoDict['hall']])
    return curs.fetchone() != None

def updateReport(conn, infoDict, reportID, changed):
    '''Updates the report of the given reportID. infoDict contains the new values
    for the report, and changed is a boolean that determines whether or not
    any of the identifying information of the report has been changed (such
    as the name, dining hall, or date served).'''
    curs = dbi.cursor(conn)
    # we don't want anyone else changing anything about this report while we're 
    # changing it, and concurrent changes to other reports could affect whether 
    # this update results in a duplicate entry or not
    curs.execute('''LOCK TABLES report WRITE,label WRITE''')
    if changed: # duplication is only possible if identifying information has changed
        print('checking duplicate')
        if isDuplicate(curs, infoDict):
            curs.execute('''UNLOCK TABLES''') # don't forget to unlock
            return False

    curs.execute('''UPDATE report SET
                    name=%s,meal=%s,served=%s,hall=%s,imagefile=%s,
                    notes=%s,owner=%s
                    WHERE id=%s''',
                    [infoDict['name'], infoDict['meal'], 
                    infoDict['served'], infoDict['hall'], infoDict['imagefile'], 
                    infoDict['notes'], infoDict['owner'],
                    reportID])

    # delete and re-insert labels
    curs.execute('''DELETE FROM label WHERE id=%s''', [reportID])
    insertLabels(conn, infoDict['allergens'], reportID, 'allergen')
    insertLabels(conn, infoDict['diets'], reportID, 'diet')

    curs.execute('''UNLOCK TABLES''') # don't forget to unlock
    return True

def insertReport(conn, infoDict):
    '''Inserts a report into the report table given a database connection
    and a dictionary of values. Returns the unique ID of the just-inserted
    report.'''
    curs = dbi.cursor(conn)
    curs.execute('''LOCK TABLES report WRITE,label WRITE''')
    if isDuplicate(curs, infoDict):
        curs.execute('''UNLOCK TABLES''')
        return -1
    else:
        curs.execute('''
            INSERT INTO report(name,meal,served,hall,imagefile,notes,owner)
            VALUES(%s, %s, %s, %s, %s, %s, %s)
            ''',
            [infoDict['name'], infoDict['meal'], infoDict['served'],
            infoDict['hall'], infoDict['imagefile'], infoDict['notes'], 
            infoDict['owner']])
        curs.execute('SELECT LAST_INSERT_ID()')
        reportID = curs.fetchone()[0]
        insertLabels(conn, infoDict['allergens'], reportID, 'allergen')
        insertLabels(conn, infoDict['diets'], reportID, 'diet')
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
    '''Returns the ID, name, date served, dining hall, mealtime, notes, and 
    owner of the report specified by ID as a dictionary.'''
    curs = dbi.dictCursor(conn)
    curs.execute('''
                SELECT name, served, hall, meal, notes, owner FROM report 
                WHERE report.id = %s
                ''', [reportID])
    return curs.fetchone() # ids are unique

def getLabels(conn, reportID):
    '''Returns the labeled/actual allergens/diets for the given report as a 
    list of dictionaries, where each dictionary represents an allergen/diet.'''
    curs = dbi.dictCursor(conn)
    curs.execute('''
                SELECT code,kind,labeled FROM label
                WHERE id = %s
                ''', [reportID])
    return curs.fetchall()

def getImage(conn, reportID):
    '''Returns the filename of the image associated with the specified report.'''
    curs = dbi.dictCursor(conn)
    curs.execute('''
                SELECT imagefile FROM report
                WHERE id = %s
                ''', [reportID])
    return curs.fetchone()

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
    print(reportDict)
    return reportDict

def getOwner(conn, reportID):
    '''Returns the username of the report's creator.'''
    curs = dbi.dictCursor(conn)
    curs.execute('''
                SELECT owner FROM report
                WHERE id = %s
                ''', [reportID])
    return curs.fetchone()['owner']

def deleteReport(conn, reportID):
    '''Deletes the report given by reportID.'''
    curs = dbi.dictCursor(conn)
    curs.execute('''SELECT imagefile FROM report WHERE id=%s''',[reportID])
    imagefile = curs.fetchone()['imagefile']
    rows = curs.execute('''
                        DELETE FROM report
                        WHERE id = %s''', [reportID])
    if rows != 1:
        print("deleted " + str(rows) + " rows")
        return None
    else:
        return imagefile

def listReports(conn, startDate, numReports):
    '''Returns a list of numReports existing reports from most recent to least recent
    relative to startDate (a datetime instance).'''
    curs = dbi.dictCursor(conn)
    start = startDate.strftime('%Y-%m-%d')
    curs.execute('''
                SELECT id,name,served,meal,hall FROM report
                WHERE served <= %s
                ORDER BY served DESC, hall
                LIMIT %s
                ''',
                [start, numReports])
    return curs.fetchall()
