from flask import (Flask, url_for, render_template, request,
                    redirect, flash, jsonify)
import random
import reports

app = Flask(__name__)

app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

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

        # insert and redirect
        conn = reports.getConn("eshumadi_db")
        reportID = reports.insertReport(conn, reportResults)
        if reportID == -1: # submission failed due to duplicate entry
            flash('report already exists')
            return render_template('new_report.html', title='Make a Report')
        else:
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
            if err:
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
        conn = reports.getConn("eshumadi_db")
        reportID = reports.insertReport(conn, reportResults)
        if reportID == -1: # submission failed due to duplicate entry
            flash('report already exists')
            return render_template('new_report.html', 
                                    title='Update | ' + reportDict['name'],
                                    info=reportDict)
        else:
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
    reportResults = {key: formData[key] 
                    for key in ['name', 'meal', 'served', 'hall', 'image', 'notes']}
    reportResults['owner'] = 'NULL'
        
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