import config
from iturmas.app import app
from iturmas.api import auth_bp, job_bp, crud_bp, search_bp, \
    batch_bp, admin_bp
from iturmas.views.pages import bp as pages_bp
from iturmas.views.pref import bp as pref_bp


app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(crud_bp, url_prefix='/crud')
app.register_blueprint(batch_bp, url_prefix='/batch')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(job_bp, url_prefix='/match')
app.register_blueprint(search_bp, url_prefix='/search')
app.register_blueprint(pref_bp, url_prefix='/pref')
app.register_blueprint(pages_bp)

app.secret_key = config.SECRET_KEY

if __name__ == "__main__":
    app.run('0.0.0.0', port=3000, debug=True)
