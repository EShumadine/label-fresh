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
