from app.app import app, db, UsuarioAdmin

with app.app_context():
    admin = UsuarioAdmin.query.filter_by(email='admin@barbearia.com').first()
    if admin:
        print(f"Admin encontrado: ID={admin.id}, Email={admin.email}")
        print(f"Senha hash: {admin.senha_hash}")
    else:
        print("Usuário admin não encontrado no banco de dados.")