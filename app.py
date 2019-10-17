from flask import (Flask, url_for, render_template, request,
                    redirect)
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
        reportesults = {}
        for key in ['name', 'served', 'hall', 'image', 'notes', 'owner']:
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
        #reports.insertReport(reports.getConn('eshumadi_db'), reportResults)
        return render_template('new_report.html', title=Submitted)

if __name__ == '__main__':
    import os
    uid = os.getuid()
    app.debug = True
    app.run('0.0.0.0',uid)