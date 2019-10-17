from flask import (Flask, url_for, render_template, request,
                    redirect)
import random

app = Flask(__name__)

app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

@app.route('/')
def homepage():
    return render_template('base.html', title='Home')

@app.route('/report/', methods=['GET','POST'])
def new_report():
    if request.method == 'GET':
        return render_template('new_report.html', title='Make a Report')
    elif request.method == 'POST':
        results = request.form.to_dict()
        if results['notes'] == '':
            results['notes'] = 'NULL'
        if results['image'] == '':
            results['image'] = 'NULL'
        results['owner'] = 'NULL'
        # insert and redirect
        return render_template('new_report.html', title=results)

if __name__ == '__main__':
    import os
    uid = os.getuid()
    app.debug = True
    app.run('0.0.0.0',uid)