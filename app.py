#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)

# import static.models
import json
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Config for non expiration token
from static.models import *
jwt = JWTManager(app)


# --------------------------------- API ---------------------------------------------------

@app.route('/')
def root():
    # db.create_all()
    return 'Hello World!'

@app.route('/token/register', methods=['POST'])
def register():
    try:
        print('Register User')
        data = json.loads(request.data)
        customer = Customer(data)
        db.session.add(customer)
        db.session.commit()
        user = Customer.query.filter(Customer.login == data.get('login')).first()
        print('Create Wallet')
        wallet_attr = {'status': True, 'balance': 0, 'owner': user.id}
        wallet = Wallet(wallet_attr)
        db.session.add(wallet)
        db.session.commit()

        return jsonify({'msg': "Register Successful"}), 200

    except Exception as Err :
        print(Err)
        return jsonify({'login': False, 'msg': 'Register fail'}), 401


@app.route('/token/login', methods=['POST'])
# TODO : Remove print function for production
def login():
    print("Login")
    data = json.loads(request.data)
    user = data.get('login', None)
    password = data.get('passwd', None)

    try :
        engine = db.get_engine(app)
        s = db.Session(bind=engine)
        query = s.query(Customer).filter(Customer.login == user, Customer.passwd == password)
        result = query.first()

        if result:

            access_token = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)
            ret = {
                'msg':'Login Succesful',
                'access_token':access_token,
                'refresh_token':refresh_token
            }
            s.close()
            return jsonify(ret), 200

        else :
            s.close()
            return jsonify({"msg": "Problem in Authentication"}), 401

    except Exception as err:
        print(err)
        s.close()
        return jsonify({'Error :', err}), 401


@app.route('/token/refresh', methods=['GET', 'POST'])
@jwt_refresh_token_required
def refresh_token():
    print('Refresh Token')
    try :
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return ({'msg': 'Session Alive', 'status': True, 'access_token': access_token}), 200

    except Exception as Err:
        print(Err)
        return jsonify({'msg':'Session Expired', 'status': False}), 401


@app.route('/api/getuserinfo', methods= ['GET'])
@jwt_required
def get_user_info():
    username = get_jwt_identity()
    try:

        user = Customer.query.filter(Customer.login == username).first()

        res = {'id': user.id,
               'name': user.name,
               'mobile': user.mobile,
               'email': user.email,
               'avatar': user.avatar,
        }

        return jsonify(res), 200

    except Exception as err :
        print(err)
        return jsonify({'msg': 'Error : {}'.format(err), 'status': False}), 401


@app.route('/api/add_ev', methods=['POST'])
@jwt_required
def add_ev():
    try:
        print('Add EV Car')
        username = get_jwt_identity()
        user = Customer.query.filter(Customer.login == username).first()
        data = json.loads(request.data)
        data.update({'ev_owner': user.id})
        ev = Ev(data)
        db.session.add(ev)
        db.session.commit()
        return jsonify({'msg':'Add EV Car Complete', 'status': True}), 200

    except Exception as Err:

        return jsonify({'msg': 'Error : {}'.format(Err), 'status': False}), 401


@app.route('/api/getevinfo', methods=['GET'])
@jwt_required
def get_ev_info():
    print('Get EV Infomation for User')
    try:
        username = get_jwt_identity()
        user = Customer.query.filter(Customer.login == username).first()
        EVs = Ev.query.filter(Ev.ev_owner == user.id).all()

        result = []

        for ev in EVs:
            res = {'ev_id': ev.ev_id,
                   'ev_model': ev.ev_model,
                   'ev_band': ev.ev_band,
                   'ev_img': ev.ev_img,
                   'ev_name': ev.ev_name
            }

            result.append(res)
            del res

        return jsonify({'status': True, 'result': result}), 200

    except Exception as Err:

        return ({'msg': 'Error : {}'.format(Err), 'status': False}), 401


@app.route('/api/ev_update', methods=['PUT'])
@jwt_required
def update_ev():
    print('Update Ev Attribute')
    data = json.loads(request.data)
    ev_id = data.get('ev_id')
    ev_band = data.get('ev_band')
    ev_model = data.get('ev_model')
    ev_name = data.get('ev_name')
    ev_img = data.get('ev_img')

    try:
        username = get_jwt_identity()
        user = Customer.query.filter(Customer.login == username).first()

        ev = Ev.query.filter(Ev.ev_id == ev_id, Ev.ev_owner == user.id).first()
        ev.ev_band = ev_band
        ev.ev_model = ev_model
        ev.ev_img = ev_img
        ev.ev_name = ev_name
        db.session.add(ev)
        db.session.commit()
        return jsonify({'msg': 'Update EV Car Attribute Complete', 'status': True}), 200

    except Exception as Err:
        print(Err)
        return jsonify({'msg': 'Error : {}'.format(Err), 'status': False}),401


@app.route('/api/ev_remove', methods=['POST','DELETE'])
@jwt_required
def remove_ev():
    print('Remove EV Car')
    data = json.loads(request.data)
    ev_id = json.loads(data.get('ev_id'))
    flag = data.get('flag')

    try:

        username = get_jwt_identity()
        user = Customer.query.filter(Customer.login == username).first()

        EVs = Ev.query.filter(Ev.ev_id.in_(ev_id), Ev.ev_owner == user.id).all()
        for ev in EVs:
            db.session.delete(ev)

        db.session.commit()

        return jsonify({'msg': 'Remove EV Complete', 'status': True}), 200

    except Exception as Err:

        return jsonify({'msg': 'Error : {}'.format(Err), 'status': False}), 401


# ---------------------------------- LOG ----------------------------

# TODO : Add the Delete and Update for EV car ##### : 90 % complete
#
# TODO : Add API for top-up Wallet
# TODO : Test Method inside class of Wallet
# TODO : Issue of Store Avatar URI and URL

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0', port = 5000)
