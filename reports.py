import dbi

def getConn(db):
    '''Returns a database connection for that db'''
    dsn = dbi.read_cnf()
    conn = dbi.connect(dsn)
    conn.select_db(db)
    return conn

def insertReport(conn, infoDict):
    curs = dbi.cursor(conn)
    curs.execute('''
        INSERT INTO report(name,meal,served,hall,image,notes,owner)
        VALUES(%s, %s, %s, %s, %s, %s, %s)
        ''', \
        [infoDict['name'], infoDict['meal'], infoDict['served'], \
        infoDict['hall'], infoDict['image'], infoDict['notes'], \
        infoDict['owner']])
    curs.execute('SELECT LAST_INSERT_ID()')
    return curs.fetchone()[0]

def insertRelations(conn, infoDict, reportID, kind):
    curs = dbi.cursor(conn)
    for key in iter(infoDict):
        for entry in infoDict[key]:
            curs.execute('''
                INSERT INTO label(id,code,labeled,kind)
                VALUES(%s, %s, %s, %s)
                ''', \
                [reportID, entry, key, kind])

def getReport(conn, reportID):
    curs = dbi.dictCursor(conn)
    curs.execute('''
                SELECT * FROM report 
                WHERE report.id = %s
                ''', [reportID])
    return curs.fetchone() # ids are unique

def getLabels(conn, reportID):
    curs = dbi.dictCursor(conn)
    curs.execute('''
                SELECT code,kind,labeled FROM report 
                INNER JOIN label ON (report.id)
                WHERE report.id = %s
                ''', [reportID])
    return curs.fetchall()

def searchReports(conn, name, hall):
    curs = dbi.dictCursor(conn)
    if hall != "All Dining Halls":
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
    reportDict = getReport(conn,reportID)

    labels = getLabels(conn, reportID)
    reportDict['listedAllergens'] = []
    reportDict['actualAllergens'] = []
    reportDict['listedDiets'] = []
    reportDict['actualDiets'] = []
    for label in labels:
        if label['labeled'] == 'listed':
            if label['kind'] == 'allergen':
                reportDict['listedAllergens'].append(label['code'])
            else: # diet
                reportDict['listedDiets'].append(label['code'])
        else: # actual
            if label['kind'] == 'allergen':
                reportDict['actualAllergens'].append(label['code'])
            else: # diet
                reportDict['actualDiets'].append(label['code'])
    
    return reportDict
