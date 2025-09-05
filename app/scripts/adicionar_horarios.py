from app.app import app, db, Barbeiro, HorarioFuncionamento
from datetime import time

def adicionar_horarios():
    """Adiciona horários de funcionamento para os barbeiros."""
    print("A adicionar horários de funcionamento...")
    
    with app.app_context():
        # Verifica se já existem horários cadastrados
        if HorarioFuncionamento.query.count() > 0:
            print("Já existem horários cadastrados no banco de dados.")
            return
        
        # Busca todos os barbeiros ativos
        barbeiros = Barbeiro.query.filter_by(ativo=True).all()
        
        if not barbeiros:
            print("Não foram encontrados barbeiros ativos no banco de dados.")
            return
        
        # Horários padrão para todos os barbeiros
        # Segunda a sexta: 9h às 18h
        # Sábado: 9h às 13h
        # Domingo: fechado
        horarios_padrao = [
            # Segunda-feira (0)
            {'dia_semana': 0, 'hora_inicio': time(9, 0), 'hora_fim': time(18, 0)},
            # Terça-feira (1)
            {'dia_semana': 1, 'hora_inicio': time(9, 0), 'hora_fim': time(18, 0)},
            # Quarta-feira (2)
            {'dia_semana': 2, 'hora_inicio': time(9, 0), 'hora_fim': time(18, 0)},
            # Quinta-feira (3)
            {'dia_semana': 3, 'hora_inicio': time(9, 0), 'hora_fim': time(18, 0)},
            # Sexta-feira (4)
            {'dia_semana': 4, 'hora_inicio': time(9, 0), 'hora_fim': time(18, 0)},
            # Sábado (5)
            {'dia_semana': 5, 'hora_inicio': time(9, 0), 'hora_fim': time(13, 0)}
            # Domingo (6) - Fechado, não adicionar
        ]
        
        # Adiciona os horários para cada barbeiro
        horarios_adicionados = 0
        for barbeiro in barbeiros:
            for horario in horarios_padrao:
                novo_horario = HorarioFuncionamento(
                    barbeiro_id=barbeiro.id,
                    dia_semana=horario['dia_semana'],
                    hora_inicio=horario['hora_inicio'],
                    hora_fim=horario['hora_fim']
                )
                db.session.add(novo_horario)
                horarios_adicionados += 1
        
        # Commit das alterações
        db.session.commit()
        print(f"Foram adicionados {horarios_adicionados} horários de funcionamento ao banco de dados.")


if __name__ == "__main__":
    adicionar_horarios()