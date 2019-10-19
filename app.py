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
        # build dictionaries
        reportResults = {key: request.form[key] \
                          for key in ['name', 'meal', 'served', 'hall', 'image', 'notes']}
        reportResults['owner'] = 'NULL'

        allergenResults = {'listed': request.form.getlist('listed-allergens'), \
                            'actual': request.form.getlist('present-allergens')}

        dietResults = {'listed': request.form.getlist('listed-diets'), \
                        'actual': request.form.getlist('followed-diets')}

        # insert and redirect
        conn = reports.getConn("eshumadi_db")
        try:
            reportID = reports.insertReport(conn, reportResults)
            reports.insertRelations(conn, allergenResults, reportID, 'allergen')
            reports.insertRelations(conn, dietResults, reportID, 'diet')
            flash('form submitted')
            return redirect(url_for('view_report', reportID=reportID))
        except Exception as err:
            flash('form submission error: '+str(err))
            return redirect(url_for('new_report'))
    else:
        return render_template('new_report.html', title='Make a Report')

@app.route('/report/<reportID>/')
def view_report(reportID):
    conn = reports.getConn("eshumadi_db")
    try:
        reportDict = reports.buildInfoDict(conn, reportID)

        return render_template('view_report.html', title=reportDict['name'], info=reportDict)
    except Exception as err:
        flash(str(err))
        return redirect(url_for('homepage'))

@app.route('/report/delete/', methods = ['GET', 'POST'])
def delete_report():
    if request.method == 'POST':
        reportID = int(request.form['reportID'])
        conn = reports.getConn("eshumadi_db")
        err = reports.deleteReport(conn, reportID)
        message = "Something went wrong." if err else flash("Successfully deleted.")
        return jsonify({'error': err, 'message': message})
    else:
        reportID = request.args.get('reportID')
        conn = reports.getConn("eshumadi_db")
        err = reports.deleteReport(conn, reportID)
        if err:
            flash("Something went wrong.")
            return redirect(url_for("view_report", reportID = reportID))
        else:
            flash("Successfully deleted.")
            return redirect(url_for("homepage"))
        
@app.route('/search/')
def search():
    conn = reports.getConn("eshumadi_db")
    results = reports.searchReports(conn, request.args.get('query'), request.args.get('hall'))
    return render_template('search.html', title="Search", \
                                          query=request.args.get('query'), \
                                          hall=request.args.get('hall'), \
                                          numResults=len(results), \
                                          results=results)

if __name__ == '__main__':
    import os
    uid = os.getuid()
    app.debug = True
    app.run('0.0.0.0',uid)