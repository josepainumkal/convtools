'''
API routes for the VW Platform. Currently defined ad-hoc, but soon will use
some Swagger/Flask tooling to generate and extend.
'''
from flask import jsonify, request, render_template

from . import api


@api.route('/')
def root():
    return render_template('api/index.html')


@api.route('/metadata/build', methods=['GET', 'POST'])
def api_metadata():
    print "In Here!"
    if request.method == 'GET':
        return jsonify(dict(message="Use this route to get some stuff"))
    else:
        return jsonify(dict(name='matt', occupation='', val=11))
