from flask import (Flask, url_for, render_template, request,
                    redirect, flash, send_from_directory,
                    session)
from werkzeug import secure_filename
import random, reports, imghdr, datetime
from flask_cas import CAS

app = Flask(__name__)

app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

CAS(app)

app.config['CAS_SERVER'] = 'https://login.wellesley.edu:443'
app.config['CAS_LOGIN_ROUTE'] = '/module.php/casserver/cas.php/login'
app.config['CAS_LOGOUT_ROUTE'] = '/module.php/casserver/cas.php/logout'
app.config['CAS_VALIDATE_ROUTE'] = '/module.php/casserver/serviceValidate.php'
app.config['CAS_AFTER_LOGIN'] = 'logged_in'

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

@app.route('/')
def homepage():
    if 'CAS_USERNAME' in session:
        return render_template('base.html', title='Home', username=session['CAS_USERNAME'])
    else:
        return render_template('base.html', title='Home')

@app.route('/logged_in/')
def logged_in():
    flash('Successfully logged in as ' + session['CAS_USERNAME'] + '.')
    return redirect(url_for('homepage'))

@app.route('/report/', methods=['GET','POST'])
def new_report():
    username = None
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']

    if request.method == 'GET':
        return render_template('new_report.html', title='Make a Report', username=username)
    elif request.method == 'POST':
        # build dictionary
        reportResults = buildFormDict(request.form, request)
        if not reportResults: # bad selection
            return render_template('new_report.html', title='Make a Report', username=username)

        # insert and redirect
        conn = reports.getConn("eshumadi_db")
        reportID = reports.insertReport(conn, reportResults)
        if reportID == -1: # submission failed due to duplicate entry
            flash('report already exists')
            return render_template('new_report.html', title='Make a Report', username=username)
        else:
            if reportResults['imagefile']:
                pathname = os.path.join(os.path.join('static',app.config['UPLOADS']),reportResults['imagefile'])
                reportResults['image'].save(pathname)
            flash('form submitted')
            return redirect(url_for('view_report', reportID=reportID))
    else:
        return render_template('new_report.html', title='Make a Report', username=username)

@app.route('/report/<reportID>/', methods=['GET','POST'])
def view_report(reportID):
    conn = reports.getConn("eshumadi_db")
    username = None
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']

    if request.method == 'GET':
        reportDict = reports.buildInfoDict(conn, reportID)

        conn = reports.getConn("eshumadi_db")
        imagefile = reports.getImage(conn, reportID)
        if not imagefile['imagefile']:
            return render_template('view_report.html', 
                                    title=reportDict['name'], 
                                    info=reportDict,
                                    username=username,
                                    owner=(username==reports.getOwner(conn,reportID)))
        else:
            pathname = os.path.join(app.config['UPLOADS'],imagefile['imagefile'])
            return render_template('view_report.html', 
                                    title=reportDict['name'], 
                                    imagesource=pathname, 
                                    info=reportDict,
                                    username=username,
                                    owner=(username==reports.getOwner(conn,reportID)))
    else: # form submitted
        if 'delete' in request.form:
            if username:
                if username != reports.getOwner(conn, reportID):
                    flash('Permission denied.')
                    return render_template('view_report.html', 
                                            title=reportDict['name'], 
                                            info=reportDict,
                                            username=username,
                                            owner=(username==reports.getOwner(conn,reportID)))
            else:
                err = reports.deleteReport(conn, reportID)
                if not err:
                    flash("Something went wrong.")
                    reportDict = reports.buildInfoDict(conn, reportID)
                    return render_template('view_report.html', 
                                            title=reportDict['name'], 
                                            info=reportDict,
                                            username=username,
                                            owner=(username==reports.getOwner(conn,reportID)))
                else:
                    os.remove(os.path.join(os.path.join('static',app.config['UPLOADS']),err))
                    flash("Successfully deleted.")
                    return redirect(url_for("homepage"))
        else: # update
            return redirect(url_for("update", reportID=reportID))

@app.route('/image/<reportID>/')
def image(reportID):
    conn = reports.getConn("eshumadi_db")
    imagefile = reports.getImage(conn, reportID)
    if not imagefile:
        flash('no file found')
        return redirect(url_for(homepage))
    else:
        return send_from_directory(os.path.join('static',app.config['UPLOADS']),imagefile['imagefile'])

@app.route('/update/<reportID>/', methods=['GET','POST'])
def update(reportID):
    conn = reports.getConn("eshumadi_db")
    reportDict = reports.buildInfoDict(conn, reportID)
    username = None
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']

    if username:
        if username != reports.getOwner(conn, reportID):
            flash('Permission denied.')
            return render_template('view_report.html', 
                                    title=reportDict['name'], 
                                    info=reportDict,
                                    username=username)
    else:
        if request.method == 'GET':
            return render_template('new_report.html',
                                    title='Update | ' + reportDict['name'],
                                    info=reportDict,
                                    username=username)
        else: # form submitted
            reportResults = buildFormDict(request.form, request)
        
            if not reportResults: # bad selection
                return render_template('new_report.html',
                                        title='Update | ' + reportDict['name'],
                                        info=reportDict,
                                        username=username)
        
            conn = reports.getConn("eshumadi_db")
            changed = False
            for key in ['name','served','meal','hall']:
                if str(reportResults[key]) != str(reportDict[key]):
                    changed = True
            unique = reports.updateReport(conn, reportResults, reportID, changed)
            if not unique: # submission failed due to duplicate entry
                flash('report already exists')
                return render_template('new_report.html', 
                                        title='Update | ' + reportDict['name'],
                                        info=reportDict,
                                        username=username)
            else:
                pathname = os.path.join(os.path.join('static',app.config['UPLOADS']),reportResults['imagefile'])
                reportResults['image'].save(pathname)
                flash('form submitted')
                return redirect(url_for('view_report', reportID=reportID))
        
@app.route('/search/')
def search():
    conn = reports.getConn("eshumadi_db")
    results = reports.searchReports(conn, request.args.get('query'), request.args.get('hall'))
    username = None
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']

    return render_template('search.html', title="Search", 
                                          query=request.args.get('query'), 
                                          hall=request.args.get('hall'), 
                                          numResults=len(results), 
                                          results=results,
                                          username=username)

@app.route('/view/')
def calendar():
    conn = reports.getConn("eshumadi_db")
    username = None
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']

    info = listSome(datetime.datetime.now(), 10)

    return render_template('calendar.html', title='View',
                                            dates=info[0],
                                            nextDate=info[1])

@app.route('/show-more/', methods=['POST'])
def showMore():
    nextDate = request.form.get('next-date')
    nextDate = datetime.datetime.strptime(nextDate, '%Y-%m-%d')

    conn = reports.getConn("eshumadi_db")
    username = None
    if 'CAS_USERNAME' in session:
        username = session['CAS_USERNAME']
    
    info = listSome(nextDate, 10)

    return render_template('calendar.html', title='View',
                                            dates=info[0],
                                            nextDate=info[1])

def listSome(startDate, numReports):
    '''Returns a dictionary of lists with a total of numReports existing reports 
    from most recent to least recent relative to startDate (a datetime instance)
    and the next start date if there are reports remaining.'''
    results = reports.listReports(conn, startDate, numReports+1)

    nextDate = None
    if len(results) <= numReports:
        dates = set([report['served'] for report in results])
        dateDict = {date: [] for date in dates}
        for report in results:
            dateDict[report['served']].append(report)
    else:
        dates = set([report['served'] for report in results[:-1]])
        dateDict = {date: [] for date in dates}
        for report in results[:-1]:
            dateDict[report['served']].append(report)
        nextDate = (min(dates) - datetime.timedelta(days=1))
    return (dateDict, nextDate)

def buildFormDict(formData, req):
    '''Builds a dictionary containing the information from the new report
    or update report form.'''
    reportResults = {key: formData[key] 
                    for key in ['name', 'meal', 'served', 'hall', 'notes']}
    if 'CAS_USERNAME' in session:
        reportResults['owner'] = session['CAS_USERNAME']
    else:
        reportResults['owner'] = None
    
    imagefile = req.files['image']
    if imagefile:
        reportResults['image'] = imagefile
        uniqueID = (reportResults['name'] + reportResults['meal'] + 
                    reportResults['served'] + reportResults['hall'])
        fsize = os.fstat(imagefile.stream.fileno()).st_size
        if fsize > app.config['MAX_CONTENT_LENGTH']:
            flash('File too big.')
            return None
        mime_type = imghdr.what(imagefile)
        if not mime_type or mime_type.lower() not in ['jpeg','gif','png']:
            flash('Not recognized as JPEG, GIF or PNG: {}'.format(mime_type))
            return None
        filename = secure_filename('{}.{}'.format(uniqueID,mime_type))
        reportResults['imagefile'] = filename
    else:
        reportResults['imagefile'] = None
    
    for labelType in ['listed-allergens', 'present-allergens', 'listed-diets', 'followed-diets']:
        labels = formData.getlist(labelType)
        if len(labels) == 0:
            flash('At least one checkbox in each set must be checked.')
            return None
        if ('None' in labels or 'Unknown' in labels) and len(labels) > 1:
            flash('None or Unknown must be the only checked option in the row.')
            return None
    reportResults['allergens'] = {'listed': formData.getlist('listed-allergens'), 
                                'actual': formData.getlist('present-allergens')}

    reportResults['diets'] = {'listed': formData.getlist('listed-diets'), 
                            'actual': formData.getlist('followed-diets')}
    return reportResults

if __name__ == '__main__':
    import sys, os

    if len(sys.argv) > 1:
        port=int(sys.argv[1])
        if not(1943 <= port <= 1950):
            print('For CAS, choose a port from 1943 to 1950')
            sys.exit()
    else:
        print('CAS not enabled.')
        port=os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)