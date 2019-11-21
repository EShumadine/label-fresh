from flask import (Flask, url_for, render_template, request,
                    redirect, flash, send_from_directory)
from werkzeug import secure_filename
import random, reports, imghdr

app = Flask(__name__)

app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

@app.route('/')
def homepage():
    return render_template('base.html', title='Home')

@app.route('/report/', methods=['GET','POST'])
def new_report():
    if request.method == 'GET':
        return render_template('new_report.html', title='Make a Report')
    elif request.method == 'POST':
        # build dictionary
        reportResults = buildFormDict(request.form)
        if not reportResults: # bad selection
            return render_template('new_report.html', title='Make a Report')

        # insert and redirect
        conn = reports.getConn("eshumadi_db")
        reportID = reports.insertReport(conn, reportResults)
        if reportID == -1: # submission failed due to duplicate entry
            flash('report already exists')
            return render_template('new_report.html', title='Make a Report')
        else:
            reportResults['image'].save(reportResults['imagefile'])
            flash('form submitted')
            return redirect(url_for('view_report', reportID=reportID))
    else:
        return render_template('new_report.html', title='Make a Report')

@app.route('/report/<reportID>/', methods=['GET','POST'])
def view_report(reportID):
    conn = reports.getConn("eshumadi_db")
    if request.method == 'GET':
        reportDict = reports.buildInfoDict(conn, reportID)

        return render_template('view_report.html', 
                                title=reportDict['name'], 
                                info=reportDict)
    else: # form submitted
        if 'delete' in request.form:
            err = reports.deleteReport(conn, reportID)
            if not err:
                flash("Something went wrong.")
                reportDict = reports.buildInfoDict(conn, reportID)
                return render_template('view_report.html', 
                                        title=reportDict['name'], 
                                        info=reportDict)
            else:
                flash("Successfully deleted.")
                return redirect(url_for("homepage"))
        else: # update
            return redirect(url_for("update", reportID=reportID))

@app.route('/update/<reportID>/', methods=['GET','POST'])
def update(reportID):
    conn = reports.getConn("eshumadi_db")
    reportDict = reports.buildInfoDict(conn, reportID)
    if request.method == 'GET':
        return render_template('new_report.html',
                                title='Update | ' + reportDict['name'],
                                info=reportDict)
    else: # form submitted
        reportResults = buildFormDict(request.form)
        
        if not reportResults: # bad selection
            return render_template('new_report.html',
                                    title='Update | ' + reportDict['name'],
                                    info=reportDict)
        
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
                                    info=reportDict)
        else:
            reportResults['image'].save(reportResults['imagefile'])
            flash('form submitted')
            return redirect(url_for('view_report', reportID=reportID))
        
@app.route('/search/')
def search():
    conn = reports.getConn("eshumadi_db")
    results = reports.searchReports(conn, request.args.get('query'), request.args.get('hall'))
    return render_template('search.html', title="Search", 
                                          query=request.args.get('query'), 
                                          hall=request.args.get('hall'), 
                                          numResults=len(results), 
                                          results=results)

def buildFormDict(formData):
    '''Builds a dictionary containing the information from the new report
    or update report form.'''
    reportResults = {key: formData[key] 
                    for key in ['name', 'meal', 'served', 'hall', 'notes']}
    reportResults['owner'] = 'NULL'
    
    imagefile = formData.files['image']
    reportResults['image'] = imagefile
    uniqueID = (reportResults['name'] + reportResults['meal'] + 
                reportResults['served'] + reportResults['hall'])
    fsize = os.fstat(imagefile.stream.fileno()).st_size
    if fsize > app.config['MAX_CONTENT_LENGTH']:
        flash('File too big.')
        return None
    mime_type = imghdr.what(f)
    if not mime_type or mime_type.lower() not in ['jpeg','gif','png']:
        flash('Not recognized as JPEG, GIF or PNG: {}'.format(mime_type))
        return None
    filename = secure_filename('{}.{}'.format(uniqueID,mime_type))
    pathname = os.path.join(app.config['UPLOADS'],filename)
    reportResults['imagefile'] = pathname
    
    for labelType in ['listed-allergens', 'present-allergens', 'listed-diets', 'followed-diets']:
        labels = formData.getlist(labelType)
        if ('None' in labels or 'Unknown' in labels) and len(labels) > 1:
            flash('None or Unknown must be the only checked option in the row.')
            return None
    reportResults['allergens'] = {'listed': formData.getlist('listed-allergens'), 
                                'actual': formData.getlist('present-allergens')}

    reportResults['diets'] = {'listed': formData.getlist('listed-diets'), 
                            'actual': formData.getlist('followed-diets')}
    return reportResults

if __name__ == '__main__':
    import os
    uid = os.getuid()
    app.debug = True
    app.run('0.0.0.0',uid)