import dbi

def getConn(db):
    '''Returns a database connection for that db'''
    dsn = dbi.read_cnf()
    conn = dbi.connect(dsn)
    conn.select_db(db)
    return conn

def insertReport(conn, infoDict):
    curs = dbi.dictCursor(conn)
    curs.execute('''
    INSERT INTO report(name,served,hall,image,notes,owner)
    VALUES(%s, %s, %s, %s, %s, %s)
    ''', \
    [infoDict['name'], infoDict['served'], infoDict['hall'], \
    infoDict['image'], infoDict['notes'], infoDict['owner']])
    return curs.fetchone()