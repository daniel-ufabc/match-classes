import config
from models import User


def create_admin():
    admin = User.filter(role='admin')
    if not admin:
        admin = User(email='admin', name='Administrator', password=config.ADMIN_PASSWORD, role='admin', code=None)
        admin.save(on_duplicate_key_update=True)

    del admin





