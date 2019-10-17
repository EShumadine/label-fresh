from flask import (Flask, url_for, render_template, request,
                    redirect, flash)
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
        reportResults = {}
        for key in ['name', 'meal', 'served', 'hall', 'image', 'notes']:
            reportResults[key] = request.form[key]
        if reportResults['notes'] == '':
            reportResults['notes'] = 'NULL'
        if reportResults['image'] == '':
            reportResults['image'] = 'NULL'
        reportResults['owner'] = 'NULL'

        allergenResults = {}
        allergenResults['listed'] = request.form.getlist('listed-allergens')
        allergenResults['present'] = request.form.getlist('present-allergens')

        dietResults = {}
        dietResults['listed'] = request.form.getlist('listed-diets')
        dietResults['followed'] = request.form.getlist('followed-diets')

        # insert and redirect
        conn = reports.getConn("eshumadi_db")
        try:
            reportID = reports.insertReport(conn, reportResults)
            reports.insertRelations(conn, allergenResults, reportID, 'allergen')
            reports.insertRelations(conn, dietResults, reportID, 'diet')
            return render_template('new_report.html', title='Submitted')
        except Exception as err:
            flash('form submission error '+str(err))
            return redirect( url_for('homepage') )

if __name__ == '__main__':
    import os
    uid = os.getuid()
    app.debug = True
    app.run('0.0.0.0',uid)