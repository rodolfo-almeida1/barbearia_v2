from app.app import app, db, UsuarioAdmin

with app.app_context():
    admin = UsuarioAdmin.query.first()
    if admin:
        admin.funcao = 'super_admin'
        db.session.commit()
        print(f'Administrador {admin.email} atualizado para super_admin')
    else:
        print('Nenhum administrador encontrado')