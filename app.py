from flask import Flask,  send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from models import *
from routes import *
from utils import pdf_report

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
cache = Cache(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=[app.config['RATELIMIT_DEFAULT']],
    storage_uri=app.config['RATELIMIT_STORAGE_URL']
)

@app.route('/iot/data/report/<location>/pdf', methods=['GET'])
@limiter.limit("5 per minute")
def get_pdf_report(location):
    try:
        pdf_buffer =pdf_report(location)
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"report_{location}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0')