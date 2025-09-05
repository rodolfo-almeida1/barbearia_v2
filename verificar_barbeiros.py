from app.app import app, db, Barbeiro

with app.app_context():
    print('Barbeiros existentes:')
    barbeiros = Barbeiro.query.all()
    if barbeiros:
        for b in barbeiros:
            print(f'ID: {b.id}, Nome: {b.nome}, Especialidade: {b.especialidade or "N/A"}')
    else:
        print('Nenhum barbeiro cadastrado.')