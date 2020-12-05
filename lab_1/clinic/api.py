from flasgger.utils import swag_from
from flask import jsonify
from flask import request
from flask_restplus import Resource
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user
from flask_sqlalchemy import SQLAlchemy

from clinic import app, api, login_manager
from clinic.models import News, Doctors, Record, User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class AddNews:
    def __init__(self, title, text):
        self.title = title
        self.text = text

    def add_news(self):
        new_news = News(news_title=self.title, news_text=self.text)
        try:
            app.session.add(new_news)
            app.session.commit()
        except:
            return "Произошла ошибка!"

class NewsAPI(Resource):

    @swag_from("news_json_post.yml")
    def post(self):
        title = request.args.get("news_title")
        text = request.args.get("news_text")
        news = AddNews(title, text)
        news.add_news()
        return jsonify({
            "title": title,
            "text": text
        })

    @swag_from("news_json_get.yml")
    def get(self):
        news = News.query.all()


class DoctorsAPI(Resource):
    @swag_from("doctors_json_get.yml")
    def get(self):
        doc = Doctors.query.all()

    @swag_from("doctors_json_patch.yml")
    def patch(self):
        search_id = int(request.args.get("id"))
        text = str(request.args.get("text"))
        doc = Doctors.query.filter_by(id_doc = search_id).first()
        new_about = doc.doc_about + text
        doc_res = Doctors(id_doc=search_id, doc_name=doc.doc_name, doc_spec=doc.doc_spec, doc_about = new_about)
        try:
            app.session.add(doc_res)
            app.session.commit()
        except:
            return "Произошла ошибка!"
        return jsonify({
            "id": search_id,
            "text": doc.doc_about
        })

class AddDiagnosis:
    def add_diagnosis(self, login_patient, diagnosis):
        new_diagnosis = Record(rec_login=login_patient, rec_diag=diagnosis)
        try:
            app.session.add(new_diagnosis)
            app.session.commit()
            return 'doctor_space'
        except:
            return "Произошла ошибка!"

    def find_record(self, login):
        rec = Record.query.filter_by(rec_login=login).all()
        return rec

class RecordAPI(Resource):

    @swag_from("record_json_get.yml")
    def get(self):
        global username
        diagnos = AddDiagnosis()
        rec = diagnos.find_record(username)


    @swag_from("record_json_post.yml")
    def post(self):
        login_patient = request.args.get("rec_login")
        diagnosis = request.args.get("rec_diag")

        new_diagnosis = AddDiagnosis()
        new_diagnosis.add_diagnosis(login_patient, diagnosis)

        return jsonify({
            "login_patient": login_patient,
            "diagnosis": diagnosis
        })

class Users:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def sign_up(self):
        if self.login and self.password:
            user = User.query.filter_by(sign_login = self.login).first()
            if user and check_password_hash(user.sign_password, self.password):
                login_user(user)
                if user.sign_role == 1:
                    global username
                    username = self.login
                    return 'user_space'
                elif user.sign_role == 2:
                    return 'doctor_space'
                elif user.sign_role == 3:
                    return 'admin_space'
            else:
                return jsonify('Неправильный логин или пароль!')
        else:
            return 'Нет логина или пароля!'

    def registration(self, password2, role):
        if not (self.login or self.password or password2):
            return 'Заполните все поля!'
        elif self.password != password2:
            return 'Пароли не совпадают'
        else:
            hash_password = generate_password_hash(self.password)
            new_user = User(sign_login = self.login, sign_password = hash_password, sign_role = role)
            app.session.add(new_user)
            app.session.commit()

class UserAPI(Resource):
    @swag_from("user_json.yml")
    def post(self):
        login = request.args.get("login")
        password = request.args.get("password")
        user = Users(login, password)
        res = user.sign_up()
        return res


## Api resource routing
api.add_resource(NewsAPI, '/news')
api.add_resource(DoctorsAPI, '/doctors')
api.add_resource(RecordAPI, '/record')
api.add_resource(UserAPI, '/user')


if __name__ == "__main__":
    app.run(debug=True)