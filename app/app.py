from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, time
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import os

# Configuração da aplicação Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-da-aplicacao'

# Configuração da sessão
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutos

# Configuração do SQLAlchemy para SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'barbearia.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração da pasta de uploads
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')
# Criar a pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicialização do SQLAlchemy
db = SQLAlchemy(app)

# Configuração do Flask-Migrate
migrate = Migrate(app, db)

# Configuração do Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return UsuarioAdmin.query.get(int(user_id))

# Definição dos modelos

class Servico(db.Model):
    __tablename__ = 'servicos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    duracao_minutos = db.Column(db.Integer, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    imagem_url = db.Column(db.String(255), nullable=True)
    
    # Relacionamento com agendamentos
    agendamentos = db.relationship('Agendamento', backref='servico', lazy=True)
    
    def __repr__(self):
        return f'<Servico {self.nome}>'


class Barbeiro(db.Model):
    __tablename__ = 'barbeiros'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    especialidade = db.Column(db.String(100))
    data_contratacao = db.Column(db.Date, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    foto_url = db.Column(db.String(255), nullable=True)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='barbeiro', lazy=True)
    horarios = db.relationship('HorarioFuncionamento', backref='barbeiro', lazy=True)
    
    def __repr__(self):
        return f'<Barbeiro {self.nome} {self.sobrenome}>'


class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com agendamentos
    agendamentos = db.relationship('Agendamento', backref='cliente', lazy=True)
    
    def __repr__(self):
        return f'<Cliente {self.nome} {self.sobrenome}>'


class HorarioFuncionamento(db.Model):
    __tablename__ = 'horarios_funcionamento'
    
    id = db.Column(db.Integer, primary_key=True)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0=Segunda, 1=Terça, ..., 6=Domingo
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
    
    def __repr__(self):
        dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        return f'<Horário {dias[self.dia_semana]} {self.hora_inicio}-{self.hora_fim}>'


class DiaSemana(db.Model):
    __tablename__ = 'dias_semana'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), nullable=False)  # Segunda-feira, Terça-feira, etc.
    hora_abertura = db.Column(db.Time, nullable=False)
    hora_fechamento = db.Column(db.Time, nullable=False)
    ativo = db.Column(db.Boolean, default=True)  # Se o dia está aberto ou fechado
    
    def __repr__(self):
        status = "Aberto" if self.ativo else "Fechado"
        return f'<{self.nome}: {self.hora_abertura}-{self.hora_fechamento}, {status}>'


class UsuarioAdmin(UserMixin, db.Model):
    __tablename__ = 'usuarios_admin'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    funcao = db.Column(db.String(20), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def is_admin(self):
        return True
    
    def __repr__(self):
        return f'<UsuarioAdmin {self.nome}>'


class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, agendado, concluído, cancelado
    observacoes = db.Column(db.Text)
    data_agendamento = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Agendamento {self.id} - {self.data} {self.hora_inicio}>'


class Configuracao(db.Model):
    __tablename__ = 'configuracoes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_barbearia = db.Column(db.String(100), default="Barbearia App", nullable=False)
    logo_url = db.Column(db.String(255), nullable=True)
    cor_primaria = db.Column(db.String(7), default="#3498db", nullable=False)
    cor_secundaria = db.Column(db.String(7), default="#2c3e50", nullable=True)
    favicon_url = db.Column(db.String(255), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    endereco = db.Column(db.Text, nullable=True)
    link_instagram = db.Column(db.String(255), nullable=True)
    link_facebook = db.Column(db.String(255), nullable=True)
    # Tempo mínimo em horas que um cliente precisa dar de antecedência para agendar
    antecedencia_minima_horas = db.Column(db.Integer, default=2, nullable=True)
    # Número máximo de dias no futuro que um cliente pode fazer um agendamento
    janela_maxima_dias = db.Column(db.Integer, default=30, nullable=True)
    # Credenciais da Twilio para integração com WhatsApp
    twilio_account_sid = db.Column(db.String(255), nullable=True)
    twilio_auth_token = db.Column(db.String(255), nullable=True)
    twilio_whatsapp_number = db.Column(db.String(20), nullable=True)
    
    def __repr__(self):
        return f'<Configuracao {self.id} - {self.nome_barbearia}>'


# Rota principal - Página de agendamento
@app.route('/')
def index():
    # Buscar todos os serviços ativos
    servicos = Servico.query.filter_by(ativo=True).all()
    
    # Buscar todos os barbeiros ativos
    barbeiros = Barbeiro.query.filter_by(ativo=True).all()
    
    # Buscar configurações
    config = Configuracao.query.first()
    
    return render_template('index.html', servicos=servicos, barbeiros=barbeiros, config=config)


# Rota de logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('admin_id', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))


# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Buscar usuário no banco de dados
        usuario = UsuarioAdmin.query.filter_by(email=username).first()
        
        # Verificar se o usuário existe e a senha está correta
        if usuario and check_password_hash(usuario.password_hash, password):
            # Fazer login com Flask-Login
            login_user(usuario)
            # Manter compatibilidade com código existente
            session['admin_id'] = usuario.id
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Credenciais inválidas. Por favor, tente novamente.', 'danger')
    
    return render_template('login.html')


# Rota de dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Cálculo da faturação semanal (últimos 7 dias)
    from datetime import datetime, timedelta
    import locale
    
    # Configurar locale para formato de data em português
    try:
        locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except:
            pass  # Se não conseguir definir o locale, usa o padrão
    
    # Data atual e data de 7 dias atrás
    hoje = datetime.now().date()
    data_inicio = hoje - timedelta(days=6)  # 7 dias incluindo hoje
    
    # Lista para armazenar as datas e valores de faturação
    datas_faturacao = []
    valores_faturacao = []
    
    # Calcular faturação para cada dia
    for i in range(7):
        data = data_inicio + timedelta(days=i)
        
        # Buscar agendamentos concluídos para esta data
        agendamentos_dia = Agendamento.query.filter(
            Agendamento.data == data,
            Agendamento.status == 'concluído'
        ).all()
        
        # Calcular faturação do dia
        faturacao_dia = sum(agendamento.servico.preco for agendamento in agendamentos_dia)
        
        # Formatar a data para exibição (ex: "Seg, 01/09")
        data_formatada = data.strftime('%a, %d/%m')
        
        # Adicionar às listas
        datas_faturacao.append(data_formatada)
        valores_faturacao.append(round(faturacao_dia, 2))
    
    # Cálculo da popularidade dos serviços
    from sqlalchemy import func
    
    # Buscar todos os serviços ativos
    servicos = Servico.query.filter_by(ativo=True).all()
    
    # Listas para armazenar nomes e contagens
    nomes_servicos = []
    contagens_servicos = []
    
    # Para cada serviço, contar quantos agendamentos existem
    for servico in servicos:
        # Contar agendamentos para este serviço
        contagem = Agendamento.query.filter_by(servico_id=servico.id).count()
        
        # Adicionar às listas apenas se houver pelo menos um agendamento
        if contagem > 0:
            nomes_servicos.append(servico.nome)
            contagens_servicos.append(contagem)
    
    # Estatísticas adicionais para o dashboard
    agendamentos_hoje = Agendamento.query.filter_by(data=hoje).count()
    total_clientes = Cliente.query.count()
    
    # Calcular faturação total (todos os agendamentos concluídos)
    faturacao_total = db.session.query(func.sum(Servico.preco)).join(
        Agendamento, Agendamento.servico_id == Servico.id
    ).filter(Agendamento.status == 'concluído').scalar() or 0
    
    # Renderizar o template com os dados calculados
    return render_template(
        'admin_dashboard.html',
        datas_faturacao=datas_faturacao,
        valores_faturacao=valores_faturacao,
        nomes_servicos=nomes_servicos,
        contagens_servicos=contagens_servicos,
        agendamentos_hoje=agendamentos_hoje,
        total_clientes=total_clientes,
        faturacao_total=round(faturacao_total, 2)
    )


# Rota da agenda
@app.route('/agenda')
def agenda():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Obter parâmetros de filtro
    nome_cliente = request.args.get('nome_cliente', '')
    
    # Iniciar a consulta base
    query = Agendamento.query
    
    # Aplicar filtro de nome de cliente se fornecido
    if nome_cliente:
        # Dividir o termo de busca em palavras individuais
        palavras = nome_cliente.split()
        
        # Iniciar a consulta com join ao Cliente
        query = query.join(Cliente)
        
        # Adicionar uma condição para cada palavra do termo de busca
        for palavra in palavras:
            # Cada palavra deve estar presente no nome ou sobrenome
            query = query.filter(
                db.or_(
                    Cliente.nome.ilike(f'%{palavra}%'),
                    Cliente.sobrenome.ilike(f'%{palavra}%')
                )
            )
    
    # Buscar agendamentos com os filtros aplicados
    agendamentos = query.all()
    
    # Agrupar agendamentos por data
    agendamentos_por_data = {}
    
    for agendamento in agendamentos:
        # Converter a data para string formatada para exibição
        data_formatada = agendamento.data.strftime('%d/%m/%Y')
        
        # Se a data ainda não existe no dicionário, criar uma lista vazia
        if data_formatada not in agendamentos_por_data:
            agendamentos_por_data[data_formatada] = []
        
        # Adicionar o agendamento à lista da data correspondente
        agendamentos_por_data[data_formatada].append(agendamento)
    
    # Renderizar o template com os agendamentos agrupados e o termo de busca
    return render_template('agenda.html', agendamentos_por_data=agendamentos_por_data, nome_cliente=nome_cliente)


# Rotas para gerenciamento de serviços
@app.route('/admin/servicos')
def admin_servicos():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar todos os serviços
    servicos = Servico.query.all()
    
    return render_template('admin_servicos.html', servicos=servicos)


@app.route('/admin/servicos/adicionar', methods=['POST'])
def admin_servicos_adicionar():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Obter dados do formulário
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    preco = request.form.get('preco')
    duracao_minutos = request.form.get('duracao_minutos')
    
    # Validar dados
    if not nome or not preco or not duracao_minutos:
        flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
        return redirect(url_for('admin_servicos'))
    
    try:
        # Converter para os tipos corretos
        preco = float(preco)
        duracao_minutos = int(duracao_minutos)
        
        # Processar o upload da imagem
        imagem_url = None
        imagem_file = request.files.get('imagem')
        if imagem_file and imagem_file.filename:
            try:
                # Garantir que o nome do arquivo seja seguro
                filename = secure_filename(imagem_file.filename)
                # Criar um nome único para o arquivo
                unique_filename = f"servico_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                # Criar diretório para imagens de serviços se não existir
                servicos_upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'servicos')
                os.makedirs(servicos_upload_path, exist_ok=True)
                # Definir o caminho para salvar o arquivo
                filepath = os.path.join(servicos_upload_path, unique_filename)
                # Salvar o arquivo
                imagem_file.save(filepath)
                # Atualizar a URL da imagem (caminho relativo para uso com url_for)
                imagem_url = f"uploads/servicos/{unique_filename}"
            except Exception as e:
                flash(f'Erro ao fazer upload da imagem: {str(e)}', 'danger')
        
        # Criar novo serviço
        novo_servico = Servico(
            nome=nome,
            descricao=descricao,
            preco=preco,
            duracao_minutos=duracao_minutos,
            ativo=True,
            imagem_url=imagem_url
        )
        
        # Adicionar ao banco de dados
        db.session.add(novo_servico)
        db.session.commit()
        
        flash(f'Serviço "{nome}" adicionado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao adicionar serviço: {str(e)}', 'danger')
    
    return redirect(url_for('admin_servicos'))


@app.route('/admin/servicos/editar/<int:id>', methods=['GET', 'POST'])
def admin_servicos_editar(id):
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar o serviço pelo ID
    servico = Servico.query.get_or_404(id)
    
    if request.method == 'POST':
        # Obter dados do formulário
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco')
        duracao_minutos = request.form.get('duracao_minutos')
        ativo = 'ativo' in request.form
        
        # Validar dados
        if not nome or not preco or not duracao_minutos:
            flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
            return render_template('admin_servicos_editar.html', servico=servico)
        
        try:
            # Processar o upload da imagem
            imagem_file = request.files.get('imagem')
            if imagem_file and imagem_file.filename:
                try:
                    # Garantir que o nome do arquivo seja seguro
                    filename = secure_filename(imagem_file.filename)
                    # Criar um nome único para o arquivo
                    unique_filename = f"servico_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                    # Criar diretório para imagens de serviços se não existir
                    servicos_upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'servicos')
                    os.makedirs(servicos_upload_path, exist_ok=True)
                    # Definir o caminho para salvar o arquivo
                    filepath = os.path.join(servicos_upload_path, unique_filename)
                    # Salvar o arquivo
                    imagem_file.save(filepath)
                    # Atualizar a URL da imagem (caminho relativo para uso com url_for)
                    servico.imagem_url = f"uploads/servicos/{unique_filename}"
                except Exception as e:
                    flash(f'Erro ao fazer upload da imagem: {str(e)}', 'danger')
            
            # Atualizar serviço
            servico.nome = nome
            servico.descricao = descricao
            servico.preco = float(preco)
            servico.duracao_minutos = int(duracao_minutos)
            servico.ativo = ativo
            
            # Salvar alterações
            db.session.commit()
            
            flash(f'Serviço "{nome}" atualizado com sucesso!', 'success')
            return redirect(url_for('admin_servicos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar serviço: {str(e)}', 'danger')
    
    # Renderizar formulário de edição
    return render_template('admin_servicos_editar.html', servico=servico)


@app.route('/admin/servicos/apagar/<int:id>', methods=['POST'])
def admin_servicos_apagar(id):
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar o serviço pelo ID
    servico = Servico.query.get_or_404(id)
    
    try:
        # Verificar se o serviço está sendo usado em algum agendamento
        agendamentos = Agendamento.query.filter_by(servico_id=id).count()
        
        if agendamentos > 0:
            # Se estiver sendo usado, apenas marcar como inativo
            servico.ativo = False
            db.session.commit()
            flash(f'O serviço "{servico.nome}" foi desativado pois possui agendamentos associados.', 'warning')
        else:
            # Se não estiver sendo usado, remover do banco de dados
            nome_servico = servico.nome
            db.session.delete(servico)
            db.session.commit()
            flash(f'Serviço "{nome_servico}" removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover serviço: {str(e)}', 'danger')
    
    return redirect(url_for('admin_servicos'))


# Rotas para gerenciar barbeiros
# Redirecionar a rota antiga para a nova
@app.route('/admin/configuracoes')
def admin_configuracoes():
    return redirect(url_for('admin_config_gerais'))

@app.route('/admin/configuracoes/gerais', methods=['GET', 'POST'])
def admin_config_gerais():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar a configuração atual
    config = Configuracao.query.first()
    
    if request.method == 'POST':
        # Obter dados do formulário
        nome_barbearia = request.form.get('nome_barbearia')
        cor_primaria = request.form.get('cor_primaria')
        
        # Verificar se foi enviado um novo logo
        logo_file = request.files.get('logo')
        logo_url = config.logo_url  # Manter o logo atual por padrão
        
        if logo_file and logo_file.filename:
            # Processar o upload do logo
            try:
                # Garantir que o nome do arquivo seja seguro
                filename = secure_filename(logo_file.filename)
                # Criar um nome único para o arquivo
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                # Definir o caminho para salvar o arquivo
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                # Salvar o arquivo
                logo_file.save(filepath)
                # Atualizar a URL do logo
                logo_url = f"/static/uploads/{unique_filename}"
            except Exception as e:
                flash(f'Erro ao fazer upload do logo: {str(e)}', 'danger')
        
        try:
            # Atualizar configuração
            config.nome_barbearia = nome_barbearia
            config.cor_primaria = cor_primaria
            if logo_url:
                config.logo_url = logo_url
            
            # Atualizar informações de contato
            config.telefone = request.form.get('telefone')
            config.endereco = request.form.get('endereco')
            config.link_instagram = request.form.get('link_instagram')
            config.link_facebook = request.form.get('link_facebook')
            
            # Salvar alterações
            db.session.commit()
            
            flash('Configurações atualizadas com sucesso!', 'success')
            return redirect(url_for('admin_config_gerais'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar configurações: {str(e)}', 'danger')
    
    return render_template('admin_config_gerais.html', config=config)

@app.route('/admin/configuracoes/visual', methods=['GET', 'POST'])
def admin_config_visual():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar a configuração atual
    config = Configuracao.query.first()
    
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            cor_secundaria = request.form.get('cor_secundaria')
            
            # Atualizar configuração
            config.cor_secundaria = cor_secundaria
            
            # Processar o upload do favicon
            favicon_file = request.files.get('favicon')
            if favicon_file and favicon_file.filename:
                # Verificar se o arquivo é uma imagem válida
                if favicon_file.filename.split('.')[-1].lower() in ['ico', 'png', 'jpg', 'jpeg']:
                    # Gerar um nome de arquivo único
                    filename = secure_filename(favicon_file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    favicon_filename = f"favicon_{timestamp}_{filename}"
                    
                    # Salvar o arquivo
                    favicon_path = os.path.join('uploads', 'favicon', favicon_filename)
                    full_path = os.path.join(app.static_folder, 'uploads', 'favicon')
                    
                    # Criar o diretório se não existir
                    os.makedirs(full_path, exist_ok=True)
                    
                    # Salvar o arquivo
                    favicon_file.save(os.path.join(app.static_folder, favicon_path))
                    
                    # Atualizar o caminho no banco de dados
                    config.favicon_url = favicon_path
                else:
                    flash('Formato de arquivo inválido para o favicon. Use .ico, .png, .jpg ou .jpeg.', 'warning')
            
            # Salvar alterações
            db.session.commit()
            
            flash('Configurações visuais atualizadas com sucesso!', 'success')
            return redirect(url_for('admin_config_visual'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar configurações visuais: {str(e)}', 'danger')
    
    return render_template('admin_config_visual.html', config=config)

@app.route('/admin/configuracoes/avancadas', methods=['GET', 'POST'])
def admin_config_avancadas():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar a configuração atual
    config = Configuracao.query.first()
    
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            antecedencia_minima_horas = request.form.get('antecedencia_minima_horas', type=int)
            janela_maxima_dias = request.form.get('janela_maxima_dias', type=int)
            
            # Atualizar configuração
            config.antecedencia_minima_horas = antecedencia_minima_horas
            config.janela_maxima_dias = janela_maxima_dias
            
            # Salvar alterações
            db.session.commit()
            
            flash('Regras de agendamento atualizadas com sucesso!', 'success')
            return redirect(url_for('admin_config_avancadas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar regras de agendamento: {str(e)}', 'danger')
    
    return render_template('admin_config_avancadas.html', config=config)


@app.route('/admin/configuracoes/integracoes', methods=['GET', 'POST'])
def admin_config_integracoes():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar a configuração atual
    config = Configuracao.query.first()
    
    if request.method == 'POST':
        try:
            # Obter dados do formulário
            twilio_account_sid = request.form.get('twilio_account_sid')
            twilio_auth_token = request.form.get('twilio_auth_token')
            twilio_whatsapp_number = request.form.get('twilio_whatsapp_number')
            
            # Atualizar configuração
            config.twilio_account_sid = twilio_account_sid
            config.twilio_auth_token = twilio_auth_token
            config.twilio_whatsapp_number = twilio_whatsapp_number
            
            # Salvar alterações
            db.session.commit()
            
            flash('Credenciais da Twilio atualizadas com sucesso!', 'success')
            return redirect(url_for('admin_config_integracoes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar credenciais da Twilio: {str(e)}', 'danger')
    
    return render_template('admin_config_integracoes.html', config=config)


@app.route('/admin/barbeiros')
def admin_barbeiros():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar todos os barbeiros
    barbeiros = Barbeiro.query.all()
    
    return render_template('admin_barbeiros.html', barbeiros=barbeiros)


@app.route('/admin/barbeiros/adicionar', methods=['POST'])
def admin_barbeiros_adicionar():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Obter dados do formulário
    nome = request.form.get('nome')
    especialidade = request.form.get('especialidade')
    foto = request.files.get('foto')
    
    # Validar dados
    if not nome:
        flash('Por favor, preencha o nome do barbeiro.', 'danger')
        return redirect(url_for('admin_barbeiros'))
    
    try:
        # Criar novo barbeiro
        novo_barbeiro = Barbeiro(
            nome=nome,
            sobrenome='',  # Campo obrigatório no modelo, mas não no formulário
            email=f'{nome.lower().replace(" ", "")}@barbearia.com',  # Email temporário
            telefone='',
            especialidade=especialidade,
            ativo=True
        )
        
        # Processar upload de foto, se fornecida
        if foto and foto.filename:
            # Verificar se é uma imagem válida
            if foto.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # Criar nome de arquivo seguro
                filename = secure_filename(foto.filename)
                # Adicionar timestamp para evitar conflitos de nomes
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                # Definir caminho para salvar
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'barbeiros', filename)
                # Salvar arquivo
                foto.save(filepath)
                # Atualizar caminho relativo no banco de dados
                novo_barbeiro.foto_url = f"uploads/barbeiros/{filename}"
            else:
                flash('Formato de arquivo não permitido. Use JPG, PNG ou GIF.', 'warning')
        
        # Adicionar ao banco de dados
        db.session.add(novo_barbeiro)
        db.session.commit()
        
        flash(f'Barbeiro "{nome}" adicionado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao adicionar barbeiro: {str(e)}', 'danger')
    
    return redirect(url_for('admin_barbeiros'))


@app.route('/admin/barbeiros/editar/<int:id>', methods=['GET', 'POST'])
def admin_barbeiros_editar(id):
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar o barbeiro pelo ID
    barbeiro = Barbeiro.query.get_or_404(id)
    
    if request.method == 'POST':
        # Obter dados do formulário
        nome = request.form.get('nome')
        especialidade = request.form.get('especialidade')
        ativo = 'ativo' in request.form
        foto = request.files.get('foto')
        
        # Validar dados
        if not nome:
            flash('Por favor, preencha o nome do barbeiro.', 'danger')
            return render_template('admin_barbeiros_editar.html', barbeiro=barbeiro)
        
        try:
            # Atualizar barbeiro
            barbeiro.nome = nome
            barbeiro.especialidade = especialidade
            barbeiro.ativo = ativo
            
            # Processar upload de foto, se fornecida
            if foto and foto.filename:
                # Verificar se é uma imagem válida
                if foto.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    # Criar nome de arquivo seguro
                    filename = secure_filename(foto.filename)
                    # Adicionar timestamp para evitar conflitos de nomes
                    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                    # Definir caminho para salvar
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'barbeiros', filename)
                    # Salvar arquivo
                    foto.save(filepath)
                    # Atualizar caminho relativo no banco de dados
                    barbeiro.foto_url = f"uploads/barbeiros/{filename}"
                else:
                    flash('Formato de arquivo não permitido. Use JPG, PNG ou GIF.', 'warning')
            
            # Salvar alterações
            db.session.commit()
            
            flash(f'Barbeiro "{nome}" atualizado com sucesso!', 'success')
            return redirect(url_for('admin_barbeiros'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar barbeiro: {str(e)}', 'danger')
    
    # Renderizar formulário de edição
    return render_template('admin_barbeiros_editar.html', barbeiro=barbeiro)


@app.route('/admin/barbeiros/apagar/<int:id>', methods=['POST'])
def admin_barbeiros_apagar(id):
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar o barbeiro pelo ID
    barbeiro = Barbeiro.query.get_or_404(id)
    
    try:
        # Verificar se o barbeiro está sendo usado em algum agendamento
        agendamentos = Agendamento.query.filter_by(barbeiro_id=id).count()
        
        if agendamentos > 0:
            # Se estiver sendo usado, apenas marcar como inativo
            barbeiro.ativo = False
            db.session.commit()
            flash(f'O barbeiro "{barbeiro.nome}" foi desativado pois possui agendamentos associados.', 'warning')
        else:
            # Se não estiver sendo usado, remover do banco de dados
            nome_barbeiro = barbeiro.nome
            db.session.delete(barbeiro)
            db.session.commit()
            flash(f'Barbeiro "{nome_barbeiro}" removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover barbeiro: {str(e)}', 'danger')
    
    return redirect(url_for('admin_barbeiros'))


# Rotas para gerenciar clientes
@app.route('/admin/clientes')
def admin_clientes():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Obter parâmetro de busca, se existir
    busca = request.args.get('busca', '')
    
    # Buscar clientes com filtro, se houver busca
    if busca:
        # Dividir o termo de busca em palavras individuais
        palavras = busca.split()
        
        # Iniciar a consulta base
        query = Cliente.query
        
        # Adicionar uma condição para cada palavra do termo de busca
        for palavra in palavras:
            # Cada palavra deve estar presente no nome ou sobrenome
            query = query.filter(
                db.or_(
                    Cliente.nome.ilike(f'%{palavra}%'),
                    Cliente.sobrenome.ilike(f'%{palavra}%')
                )
            )
        
        # Executar a consulta ordenada por nome
        clientes = query.order_by(Cliente.nome).all()
    else:
        clientes = Cliente.query.order_by(Cliente.nome).all()
    
    # Adicionar funções de URL para verificação de segurança no template
    url_for_security = {
        'admin_clientes_editar': True,
        'admin_clientes_apagar': True
    }
    
    return render_template('admin_clientes.html', clientes=clientes, url_for_security=url_for_security)

@app.route('/admin/clientes/adicionar', methods=['POST'])
def admin_clientes_adicionar():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Obter dados do formulário
    nome = request.form.get('nome')
    telefone = request.form.get('telefone')
    
    # Validar dados
    if not nome or not telefone:
        flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
        return redirect(url_for('admin_clientes'))
    
    # Validar o telefone usando a função existente
    telefone_valido, mensagem_ou_telefone = validar_celular(telefone)
    if not telefone_valido:
        flash(f'Telefone inválido: {mensagem_ou_telefone}', 'danger')
        return redirect(url_for('admin_clientes'))
    
    # Verificar se já existe um cliente com este telefone
    cliente_existente = Cliente.query.filter_by(telefone=mensagem_ou_telefone).first()
    if cliente_existente:
        flash(f'Já existe um cliente cadastrado com este telefone: {cliente_existente.nome} {cliente_existente.sobrenome}', 'warning')
        return redirect(url_for('admin_clientes'))
    
    try:
        # Separar o nome completo em nome e sobrenome
        partes_nome = nome.split(' ', 1)
        primeiro_nome = partes_nome[0]
        sobrenome = partes_nome[1] if len(partes_nome) > 1 else ''
        
        # Criar novo cliente
        novo_cliente = Cliente(
            nome=primeiro_nome,
            sobrenome=sobrenome,
            email=f'{primeiro_nome.lower()}{sobrenome.lower() if sobrenome else ''}@exemplo.com',  # Email padrão
            telefone=mensagem_ou_telefone
        )
        
        # Salvar no banco de dados
        db.session.add(novo_cliente)
        db.session.commit()
        
        flash(f'Cliente {nome} adicionado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao adicionar cliente: {str(e)}', 'danger')
    
    return redirect(url_for('admin_clientes'))


# Rotas para gerenciar horários de funcionamento
@app.route('/admin/horarios')
def admin_horarios():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar todos os dias da semana
    dias = DiaSemana.query.all()
    
    # Se não existirem dias cadastrados, criar os 7 dias da semana
    if not dias:
        dias_nomes = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
        for i, nome in enumerate(dias_nomes):
            # Horário padrão: 9h às 18h para dias de semana, 9h às 13h para sábado, fechado para domingo
            if i < 5:  # Segunda a Sexta
                hora_abertura = datetime.strptime('09:00', '%H:%M').time()
                hora_fechamento = datetime.strptime('18:00', '%H:%M').time()
                ativo = True
            elif i == 5:  # Sábado
                hora_abertura = datetime.strptime('09:00', '%H:%M').time()
                hora_fechamento = datetime.strptime('13:00', '%H:%M').time()
                ativo = True
            else:  # Domingo
                hora_abertura = datetime.strptime('00:00', '%H:%M').time()
                hora_fechamento = datetime.strptime('00:00', '%H:%M').time()
                ativo = False
            
            dia = DiaSemana(nome=nome, hora_abertura=hora_abertura, hora_fechamento=hora_fechamento, ativo=ativo)
            db.session.add(dia)
        
        db.session.commit()
        dias = DiaSemana.query.all()
    
    return render_template('admin_horarios.html', dias=dias)


@app.route('/admin/horarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_horarios_editar(id):
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('index'))
    
    # Buscar o dia pelo ID
    dia = DiaSemana.query.get_or_404(id)
    
    # Se for GET, renderizar o template de edição
    if request.method == 'GET':
        return render_template('admin_horarios_editar.html', dia=dia)
    
    # Obter os novos horários do formulário
    hora_abertura = request.form.get('hora_abertura')
    hora_fechamento = request.form.get('hora_fechamento')
    
    try:
        # Atualizar apenas o campo que foi enviado
        if hora_abertura:
            dia.hora_abertura = datetime.strptime(hora_abertura, '%H:%M').time()
            flash(f'Hora de abertura de {dia.nome} atualizada com sucesso!', 'success')
        
        if hora_fechamento:
            dia.hora_fechamento = datetime.strptime(hora_fechamento, '%H:%M').time()
            flash(f'Hora de fechamento de {dia.nome} atualizada com sucesso!', 'success')
        
        db.session.commit()
    except ValueError:
        flash('Formato de horário inválido. Use o formato HH:MM.', 'danger')
    
    return redirect(url_for('admin_horarios'))


@app.route('/admin/horarios/alternar-status/<int:id>', methods=['POST'])
@login_required
def admin_horarios_alternar_status(id):
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('index'))
    
    # Buscar o dia pelo ID
    dia = DiaSemana.query.get_or_404(id)
    
    # Alternar o status
    dia.ativo = not dia.ativo
    
    db.session.commit()
    
    status = "aberto" if dia.ativo else "fechado"
    flash(f'{dia.nome} agora está {status}.', 'success')
    
    return redirect(url_for('admin_horarios'))


# Rotas para gerenciar horários individuais dos barbeiros
@app.route('/admin/horarios_equipe')
def admin_horarios_equipe():
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar todos os barbeiros
    barbeiros = Barbeiro.query.order_by(Barbeiro.nome).all()
    
    return render_template('admin_barbeiros_horarios.html', barbeiros=barbeiros)


@app.route('/admin/horarios/editar_barbeiro/<int:barbeiro_id>', methods=['GET', 'POST'])
def admin_horarios_editar_barbeiro(barbeiro_id):
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar o barbeiro pelo ID
    barbeiro = Barbeiro.query.get_or_404(barbeiro_id)
    
    # Buscar os horários do barbeiro para cada dia da semana
    horarios = HorarioFuncionamento.query.filter_by(barbeiro_id=barbeiro_id).order_by(HorarioFuncionamento.dia_semana).all()
    
    # Se não existirem horários cadastrados para este barbeiro, criar os 7 dias da semana
    if not horarios or len(horarios) < 7:
        # Verificar quais dias já existem
        dias_existentes = [h.dia_semana for h in horarios]
        
        # Criar os dias que faltam
        for dia in range(7):
            if dia not in dias_existentes:
                # Horário padrão: 9h às 18h para dias de semana, 9h às 13h para sábado, fechado para domingo
                if dia < 5:  # Segunda a Sexta
                    hora_inicio = datetime.strptime('09:00', '%H:%M').time()
                    hora_fim = datetime.strptime('18:00', '%H:%M').time()
                elif dia == 5:  # Sábado
                    hora_inicio = datetime.strptime('09:00', '%H:%M').time()
                    hora_fim = datetime.strptime('13:00', '%H:%M').time()
                else:  # Domingo
                    hora_inicio = datetime.strptime('00:00', '%H:%M').time()
                    hora_fim = datetime.strptime('00:00', '%H:%M').time()
                
                horario = HorarioFuncionamento(barbeiro_id=barbeiro_id, dia_semana=dia, hora_inicio=hora_inicio, hora_fim=hora_fim)
                db.session.add(horario)
        
        db.session.commit()
        horarios = HorarioFuncionamento.query.filter_by(barbeiro_id=barbeiro_id).order_by(HorarioFuncionamento.dia_semana).all()
    
    # Se for POST, processar a atualização de horário
    if request.method == 'POST':
        dia_semana = int(request.form.get('dia_semana'))
        acao = request.form.get('acao')
        
        # Buscar o horário específico para o dia da semana
        horario = HorarioFuncionamento.query.filter_by(barbeiro_id=barbeiro_id, dia_semana=dia_semana).first()
        
        if not horario:
            flash('Horário não encontrado.', 'danger')
            return redirect(url_for('admin_horarios_editar_barbeiro', barbeiro_id=barbeiro_id))
        
        try:
            if acao == 'hora_inicio':
                # Atualizar hora de início
                hora_inicio = request.form.get('hora_inicio')
                horario.hora_inicio = datetime.strptime(hora_inicio, '%H:%M').time()
                flash(f'Hora de abertura atualizada com sucesso!', 'success')
            
            elif acao == 'hora_fim':
                # Atualizar hora de fim
                hora_fim = request.form.get('hora_fim')
                horario.hora_fim = datetime.strptime(hora_fim, '%H:%M').time()
                flash(f'Hora de fechamento atualizada com sucesso!', 'success')
            
            elif acao == 'alternar_status':
                # Verificar se está fechado (00:00 - 00:00)
                hora_inicio_zero = horario.hora_inicio.strftime('%H:%M') == '00:00'
                hora_fim_zero = horario.hora_fim.strftime('%H:%M') == '00:00'
                fechado = hora_inicio_zero and hora_fim_zero
                
                if fechado:
                    # Se estiver fechado, abrir com horário padrão
                    if horario.dia_semana < 5:  # Segunda a Sexta
                        horario.hora_inicio = datetime.strptime('09:00', '%H:%M').time()
                        horario.hora_fim = datetime.strptime('18:00', '%H:%M').time()
                    elif horario.dia_semana == 5:  # Sábado
                        horario.hora_inicio = datetime.strptime('09:00', '%H:%M').time()
                        horario.hora_fim = datetime.strptime('13:00', '%H:%M').time()
                    
                    flash('Dia aberto com horário padrão.', 'success')
                else:
                    # Se estiver aberto, fechar (00:00 - 00:00)
                    horario.hora_inicio = datetime.strptime('00:00', '%H:%M').time()
                    horario.hora_fim = datetime.strptime('00:00', '%H:%M').time()
                    flash('Dia fechado com sucesso.', 'success')
            
            db.session.commit()
        except ValueError:
            flash('Formato de horário inválido. Use o formato HH:MM.', 'danger')
        
        return redirect(url_for('admin_horarios_editar_barbeiro', barbeiro_id=barbeiro_id))
    
    # Renderizar o template com os horários do barbeiro
    return render_template('admin_horario_individual.html', barbeiro=barbeiro, horarios=horarios)


@app.route('/admin/cliente/<int:id>')
def admin_cliente_detalhe(id):
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar o cliente pelo ID
    cliente = Cliente.query.get_or_404(id)
    
    # Buscar agendamentos do cliente
    agendamentos = Agendamento.query.filter_by(cliente_id=id).order_by(Agendamento.data.desc(), Agendamento.hora_inicio).all()
    
    # Adicionar funções de URL para verificação de segurança no template
    url_for_security = {
        'admin_clientes_editar': True
    }
    
    return render_template('admin_cliente_detalhe.html', cliente=cliente, agendamentos=agendamentos, url_for_security=url_for_security)


@app.route('/admin/clientes/editar/<int:id>', methods=['GET', 'POST'])
def admin_clientes_editar(id):
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar o cliente pelo ID
    cliente = Cliente.query.get_or_404(id)
    
    if request.method == 'POST':
        # Obter dados do formulário
        nome = request.form.get('nome')
        sobrenome = request.form.get('sobrenome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        
        # Validar dados
        if not nome or not sobrenome or not email:
            flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
            return render_template('admin_clientes_editar.html', cliente=cliente)
        
        try:
            # Verificar se o email já está em uso por outro cliente
            cliente_existente = Cliente.query.filter(Cliente.email == email, Cliente.id != id).first()
            if cliente_existente:
                flash('Este email já está em uso por outro cliente.', 'danger')
                return render_template('admin_clientes_editar.html', cliente=cliente)
            
            # Atualizar cliente
            cliente.nome = nome
            cliente.sobrenome = sobrenome
            cliente.email = email
            cliente.telefone = telefone
            
            # Salvar alterações
            db.session.commit()
            
            flash(f'Cliente "{nome} {sobrenome}" atualizado com sucesso!', 'success')
            return redirect(url_for('admin_cliente_detalhe', id=cliente.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar cliente: {str(e)}', 'danger')
    
    # Renderizar formulário de edição
    return render_template('admin_clientes_editar.html', cliente=cliente)


@app.route('/admin/clientes/apagar/<int:id>', methods=['POST'])
def admin_clientes_apagar(id):
    # Verificar se o usuário está logado
    if 'admin_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    # Buscar o cliente pelo ID
    cliente = Cliente.query.get_or_404(id)
    
    try:
        # Verificar se o cliente está sendo usado em algum agendamento
        agendamentos = Agendamento.query.filter_by(cliente_id=id).count()
        
        if agendamentos > 0:
            flash(f'O cliente "{cliente.nome} {cliente.sobrenome}" não pode ser removido pois possui agendamentos associados.', 'warning')
        else:
            # Se não estiver sendo usado, remover do banco de dados
            nome_cliente = f"{cliente.nome} {cliente.sobrenome}"
            db.session.delete(cliente)
            db.session.commit()
            flash(f'Cliente "{nome_cliente}" removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover cliente: {str(e)}', 'danger')
    
    return redirect(url_for('admin_clientes'))


# Rota para trocar horários entre agendamentos
@app.route('/admin/agendamento/trocar', methods=['POST'])
@login_required
def admin_agendamento_trocar():
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Acesso restrito a administradores.'}), 403
    
    # Obter os IDs dos agendamentos do corpo da requisição JSON
    data = request.get_json()
    
    if not data or 'agendamento1_id' not in data or 'agendamento2_id' not in data:
        return jsonify({'status': 'error', 'message': 'Dados incompletos. IDs dos agendamentos são necessários.'}), 400
    
    agendamento1_id = data['agendamento1_id']
    agendamento2_id = data['agendamento2_id']
    
    # Buscar os agendamentos no banco de dados
    agendamento1 = Agendamento.query.get(agendamento1_id)
    agendamento2 = Agendamento.query.get(agendamento2_id)
    
    # Verificar se ambos os agendamentos foram encontrados
    if not agendamento1 or not agendamento2:
        return jsonify({'status': 'error', 'message': 'Um ou ambos os agendamentos não foram encontrados.'}), 404
    
    # Verificar se ambos os agendamentos estão com status 'agendado'
    if agendamento1.status != 'agendado' or agendamento2.status != 'agendado':
        return jsonify({'status': 'error', 'message': 'Apenas agendamentos com status "agendado" podem ser trocados.'}), 400
    
    try:
        # Trocar os horários entre os agendamentos
        # Salvar os valores temporariamente
        temp_data = agendamento1.data
        temp_hora_inicio = agendamento1.hora_inicio
        temp_hora_fim = agendamento1.hora_fim
        
        # Atualizar agendamento1 com os valores do agendamento2
        agendamento1.data = agendamento2.data
        agendamento1.hora_inicio = agendamento2.hora_inicio
        agendamento1.hora_fim = agendamento2.hora_fim
        
        # Atualizar agendamento2 com os valores temporários (originalmente do agendamento1)
        agendamento2.data = temp_data
        agendamento2.hora_inicio = temp_hora_inicio
        agendamento2.hora_fim = temp_hora_fim
        
        # Salvar as alterações no banco de dados
        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': 'Horários trocados com sucesso!',
            'agendamento1': {
                'id': agendamento1.id,
                'cliente': f"{agendamento1.cliente.nome} {agendamento1.cliente.sobrenome}",
                'data': agendamento1.data.strftime('%d/%m/%Y'),
                'hora_inicio': agendamento1.hora_inicio.strftime('%H:%M'),
                'hora_fim': agendamento1.hora_fim.strftime('%H:%M')
            },
            'agendamento2': {
                'id': agendamento2.id,
                'cliente': f"{agendamento2.cliente.nome} {agendamento2.cliente.sobrenome}",
                'data': agendamento2.data.strftime('%d/%m/%Y'),
                'hora_inicio': agendamento2.hora_inicio.strftime('%H:%M'),
                'hora_fim': agendamento2.hora_fim.strftime('%H:%M')
            }
        })
    except Exception as e:
        # Em caso de erro, desfazer as alterações
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erro ao trocar horários: {str(e)}'}), 500


# Rotas para confirmar e cancelar agendamentos via AJAX
@app.route('/agendamento/confirmar/<int:id>', methods=['POST'])
@login_required
def agendamento_confirmar(id):
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Acesso restrito a administradores.'}), 403
    
    # Buscar o agendamento pelo ID
    agendamento = Agendamento.query.get_or_404(id)
    
    try:
        # Atualizar o status do agendamento para 'agendado'
        agendamento.status = 'agendado'
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Agendamento confirmado com sucesso!',
            'agendamento_id': agendamento.id,
            'novo_status': 'agendado'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erro ao confirmar agendamento: {str(e)}'}), 500


# API para obter horários disponíveis
@app.route('/api/horarios-disponiveis', methods=['GET'])
def api_horarios_disponiveis():
    # Obter parâmetros da requisição
    data_str = request.args.get('data')
    barbeiro_id = request.args.get('barbeiro_id')
    servico_id = request.args.get('servico_id')
    
    print(f"--- API Recebeu: data={data_str}, servico_id={servico_id}, barbeiro_id={barbeiro_id} ---")
    
    # Validar parâmetros
    if not data_str or not barbeiro_id or not servico_id:
        print(f"!!! ERRO NA API: Parâmetros incompletos !!!")
        return jsonify({
            'status': 'error',
            'message': 'Parâmetros incompletos. Data, barbeiro_id e servico_id são obrigatórios.'
        }), 400
    
    try:
        # Converter a data de string para objeto date
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        barbeiro_id = int(barbeiro_id)
        servico_id = int(servico_id)
        
        # Buscar o serviço para saber a duração
        servico = Servico.query.get(servico_id)
        if not servico:
            print(f"!!! ERRO NA API: Serviço não encontrado com ID {servico_id} !!!")
            return jsonify({'status': 'error', 'message': 'Serviço não encontrado.'}), 404
        print(f"Serviço encontrado: {servico.nome}, duração: {servico.duracao_minutos} minutos")
        
        # Buscar o barbeiro
        barbeiro = Barbeiro.query.get(barbeiro_id)
        if not barbeiro:
            print(f"!!! ERRO NA API: Barbeiro não encontrado com ID {barbeiro_id} !!!")
            return jsonify({'status': 'error', 'message': 'Barbeiro não encontrado.'}), 404
        print(f"Barbeiro encontrado: {barbeiro.nome}")
        
        # Determinar o dia da semana (0=Segunda, 1=Terça, ..., 6=Domingo)
        dia_semana = data.weekday()
        
        # Buscar o horário de funcionamento do barbeiro para este dia
        horario_funcionamento = HorarioFuncionamento.query.filter_by(
            barbeiro_id=barbeiro_id,
            dia_semana=dia_semana
        ).first()
        
        print(f"Dia da semana: {dia_semana} (0=Segunda, 1=Terça, ..., 6=Domingo)")
        
        # Verificar se existe um horário definido para este barbeiro neste dia
        if not horario_funcionamento:
            print(f"!!! INFO: Horário não definido para o barbeiro {barbeiro.nome} no dia {dia_semana}, retornando lista vazia !!!")
            return jsonify({
                'status': 'success',
                'horarios_disponiveis': []
            })
        print(f"Horário de funcionamento encontrado: {horario_funcionamento.hora_inicio.strftime('%H:%M')} - {horario_funcionamento.hora_fim.strftime('%H:%M')}")
            
        # Verificar se o barbeiro trabalha neste dia (horário não é 00:00-00:00)
        hora_inicio = horario_funcionamento.hora_inicio
        hora_fim = horario_funcionamento.hora_fim
        
        # Se o horário for 00:00-00:00, significa que o barbeiro não trabalha neste dia
        if hora_inicio.strftime('%H:%M') == '00:00' and hora_fim.strftime('%H:%M') == '00:00':
            print(f"!!! INFO: O barbeiro não trabalha neste dia (horário 00:00-00:00), retornando lista vazia !!!")
            return jsonify({
                'status': 'success',
                'horarios_disponiveis': []
            })
        
        # Buscar todos os agendamentos do barbeiro para esta data (exceto cancelados)
        agendamentos = Agendamento.query.filter(
            Agendamento.barbeiro_id == barbeiro_id,
            Agendamento.data == data,
            Agendamento.status.in_(['pendente', 'agendado', 'concluído'])
        ).all()
        print(f"Total de agendamentos encontrados para o dia: {len(agendamentos)}")
        
        # Criar lista de horários ocupados
        horarios_ocupados = []
        for agendamento in agendamentos:
            horarios_ocupados.append({
                'inicio': agendamento.hora_inicio,
                'fim': agendamento.hora_fim
            })
        
        # Calcular horários disponíveis em intervalos de 30 minutos
        horarios_disponiveis = []
        duracao_servico = servico.duracao_minutos
        
        # Converter hora_inicio e hora_fim para minutos desde o início do dia
        inicio_minutos = hora_inicio.hour * 60 + hora_inicio.minute
        fim_minutos = hora_fim.hour * 60 + hora_fim.minute
        print(f"Horário de funcionamento em minutos: {inicio_minutos} - {fim_minutos}")
        print(f"Duração do serviço: {duracao_servico} minutos")
        
        # Verificar se a data selecionada é o dia atual
        data_atual = datetime.now().date()
        hora_atual_obj = datetime.now().time()
        is_hoje = (data == data_atual)
        print(f"Data selecionada é hoje? {is_hoje}")
        
        # Gerar horários possíveis em intervalos de 30 minutos
        for minuto in range(inicio_minutos, fim_minutos - duracao_servico + 1, 30):
            hora_slot = time(minuto // 60, minuto % 60)
            hora_fim_slot = time((minuto + duracao_servico) // 60, (minuto + duracao_servico) % 60)
            
            # Verificar se este horário não conflita com nenhum agendamento existente
            conflito = False
            for ocupado in horarios_ocupados:
                # Se o início do novo horário está dentro de um horário ocupado
                if (ocupado['inicio'] <= hora_slot < ocupado['fim']) or \
                   (ocupado['inicio'] < hora_fim_slot <= ocupado['fim']) or \
                   (hora_slot <= ocupado['inicio'] and hora_fim_slot >= ocupado['fim']):
                    conflito = True
                    break
            
            # Se for hoje, verificar se o horário já passou
            if is_hoje and hora_slot <= hora_atual_obj:
                print(f"Horário {hora_slot.strftime('%H:%M')} já passou, ignorando")
                continue
            
            if not conflito:
                horarios_disponiveis.append({
                    'hora_inicio': hora_slot.strftime('%H:%M'),
                    'hora_fim': hora_fim_slot.strftime('%H:%M')
                })
        
        print(f"--- API Vai Retornar: {len(horarios_disponiveis)} horários disponíveis ---")
        print(f"Horários disponíveis: {horarios_disponiveis}")
        return jsonify({
            'status': 'success',
            'horarios_disponiveis': horarios_disponiveis
        })
        
    except ValueError as e:
        print(f"!!! ERRO DE FORMATO NA API: {e} !!!")
        return jsonify({'status': 'error', 'message': f'Erro de formato: {str(e)}'}), 400
    except Exception as e:
        print(f"!!! ERRO NA API: {e} !!!")
        import traceback
        print(traceback.format_exc())
        return jsonify({'status': 'error', 'message': f'Erro ao buscar horários disponíveis: {str(e)}'}), 500


# API para obter horários disponíveis para reagendamento
@app.route('/api/horarios-disponiveis-reagendamento', methods=['GET'])
def api_horarios_disponiveis_reagendamento():
    # Obter parâmetros da requisição
    data_str = request.args.get('data')
    agendamento_id = request.args.get('agendamento_id')
    
    # Validar parâmetros
    if not data_str or not agendamento_id:
        return jsonify({
            'status': 'error',
            'message': 'Parâmetros incompletos. Data e agendamento_id são obrigatórios.'
        }), 400
    
    try:
        # Converter a data de string para objeto date
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        agendamento_id = int(agendamento_id)
        
        # Buscar o agendamento original
        agendamento = Agendamento.query.get(agendamento_id)
        if not agendamento:
            return jsonify({'status': 'error', 'message': 'Agendamento não encontrado.'}), 404
        
        # Obter o serviço e barbeiro do agendamento original
        servico = agendamento.servico
        barbeiro = agendamento.barbeiro
        
        # Determinar o dia da semana (0=Segunda, 1=Terça, ..., 6=Domingo)
        dia_semana = data.weekday()
        
        # Buscar o horário de funcionamento do barbeiro para este dia
        horario_funcionamento = HorarioFuncionamento.query.filter_by(
            barbeiro_id=barbeiro.id,
            dia_semana=dia_semana
        ).first()
        
        # Verificar se existe um horário definido para este barbeiro neste dia
        if not horario_funcionamento:
            return jsonify({
                'status': 'error',
                'message': f'O barbeiro não tem horário definido para este dia.'
            }), 400
            
        # Verificar se o barbeiro trabalha neste dia (horário não é 00:00-00:00)
        hora_inicio = horario_funcionamento.hora_inicio
        hora_fim = horario_funcionamento.hora_fim
        
        # Se o horário for 00:00-00:00, significa que o barbeiro não trabalha neste dia
        if hora_inicio.strftime('%H:%M') == '00:00' and hora_fim.strftime('%H:%M') == '00:00':
            return jsonify({
                'status': 'error',
                'message': f'O barbeiro não trabalha neste dia.'
            }), 400
        
        # Buscar todos os agendamentos do barbeiro para esta data (exceto cancelados e o próprio agendamento)
        agendamentos = Agendamento.query.filter(
            Agendamento.barbeiro_id == barbeiro.id,
            Agendamento.data == data,
            Agendamento.status.in_(['pendente', 'agendado', 'concluído']),
            Agendamento.id != agendamento_id  # Excluir o próprio agendamento
        ).all()
        
        # Criar lista de horários ocupados
        horarios_ocupados = []
        for ag in agendamentos:
            horarios_ocupados.append({
                'inicio': ag.hora_inicio,
                'fim': ag.hora_fim
            })
        
        # Calcular horários disponíveis em intervalos de 30 minutos
        horarios_disponiveis = []
        duracao_servico = servico.duracao_minutos
        
        # Converter hora_inicio e hora_fim para minutos desde o início do dia
        inicio_minutos = hora_inicio.hour * 60 + hora_inicio.minute
        fim_minutos = hora_fim.hour * 60 + hora_fim.minute
        
        # Gerar horários possíveis em intervalos de 30 minutos
        for minuto in range(inicio_minutos, fim_minutos - duracao_servico + 1, 30):
            hora_atual = time(minuto // 60, minuto % 60)
            hora_fim_atual = time((minuto + duracao_servico) // 60, (minuto + duracao_servico) % 60)
            
            # Verificar se este horário não conflita com nenhum agendamento existente
            conflito = False
            for ocupado in horarios_ocupados:
                # Se o início do novo horário está dentro de um horário ocupado
                if (ocupado['inicio'] <= hora_atual < ocupado['fim']) or \
                   (ocupado['inicio'] < hora_fim_atual <= ocupado['fim']) or \
                   (hora_atual <= ocupado['inicio'] and hora_fim_atual >= ocupado['fim']):
                    conflito = True
                    break
            
            if not conflito:
                horarios_disponiveis.append({
                    'hora_inicio': hora_atual.strftime('%H:%M'),
                    'hora_fim': hora_fim_atual.strftime('%H:%M')
                })
        
        return jsonify({
            'status': 'success',
            'horarios_disponiveis': horarios_disponiveis
        })
        
    except ValueError as e:
        return jsonify({'status': 'error', 'message': f'Erro de formato: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erro ao buscar horários disponíveis: {str(e)}'}), 500
    
    try:
        # Converter a data de string para objeto date
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        barbeiro_id = int(barbeiro_id)
        servico_id = int(servico_id)
        
        # Buscar o serviço para saber a duração
        servico = Servico.query.get(servico_id)
        if not servico:
            return jsonify({'status': 'error', 'message': 'Serviço não encontrado.'}), 404
        
        # Buscar o barbeiro
        barbeiro = Barbeiro.query.get(barbeiro_id)
        if not barbeiro:
            return jsonify({'status': 'error', 'message': 'Barbeiro não encontrado.'}), 404
        
        # Determinar o dia da semana (0=Segunda, 1=Terça, ..., 6=Domingo)
        dia_semana = data.weekday()
        
        # Buscar o horário de funcionamento do barbeiro para este dia
        horario_funcionamento = HorarioFuncionamento.query.filter_by(
            barbeiro_id=barbeiro_id,
            dia_semana=dia_semana
        ).first()
        
        # Verificar se existe um horário definido para este barbeiro neste dia
        if not horario_funcionamento:
            return jsonify({
                'status': 'error',
                'message': f'O barbeiro não tem horário definido para este dia.'
            }), 400
            
        # Verificar se o barbeiro trabalha neste dia (horário não é 00:00-00:00)
        hora_inicio = horario_funcionamento.hora_inicio
        hora_fim = horario_funcionamento.hora_fim
        
        # Se o horário for 00:00-00:00, significa que o barbeiro não trabalha neste dia
        if hora_inicio.strftime('%H:%M') == '00:00' and hora_fim.strftime('%H:%M') == '00:00':
            return jsonify({
                'status': 'error',
                'message': f'O barbeiro não trabalha neste dia.'
            }), 400
        
        # Buscar todos os agendamentos do barbeiro para esta data (exceto cancelados)
        agendamentos = Agendamento.query.filter(
            Agendamento.barbeiro_id == barbeiro_id,
            Agendamento.data == data,
            Agendamento.status.in_(['pendente', 'agendado', 'concluído'])
        ).all()
        
        # Criar lista de horários ocupados
        horarios_ocupados = []
        for agendamento in agendamentos:
            horarios_ocupados.append({
                'inicio': agendamento.hora_inicio,
                'fim': agendamento.hora_fim
            })
        
        # Calcular horários disponíveis em intervalos de 30 minutos
        horarios_disponiveis = []
        duracao_servico = servico.duracao_minutos
        
        # Converter hora_inicio e hora_fim para minutos desde o início do dia
        inicio_minutos = hora_inicio.hour * 60 + hora_inicio.minute
        fim_minutos = hora_fim.hour * 60 + hora_fim.minute
        
        # Gerar horários possíveis em intervalos de 30 minutos
        for minuto in range(inicio_minutos, fim_minutos - duracao_servico + 1, 30):
            hora_atual = time(minuto // 60, minuto % 60)
            hora_fim_atual = time((minuto + duracao_servico) // 60, (minuto + duracao_servico) % 60)
            
            # Verificar se este horário não conflita com nenhum agendamento existente
            conflito = False
            for ocupado in horarios_ocupados:
                # Se o início do novo horário está dentro de um horário ocupado
                if (ocupado['inicio'] <= hora_atual < ocupado['fim']) or \
                   (ocupado['inicio'] < hora_fim_atual <= ocupado['fim']) or \
                   (hora_atual <= ocupado['inicio'] and hora_fim_atual >= ocupado['fim']):
                    conflito = True
                    break
            
            if not conflito:
                horarios_disponiveis.append({
                    'hora_inicio': hora_atual.strftime('%H:%M'),
                    'hora_fim': hora_fim_atual.strftime('%H:%M')
                })
        
        return jsonify({
            'status': 'success',
            'horarios_disponiveis': horarios_disponiveis
        })
        
    except ValueError as e:
        return jsonify({'status': 'error', 'message': f'Erro de formato: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erro ao buscar horários disponíveis: {str(e)}'}), 500


# Função para validar telefone
def validar_celular(telefone):
    import re
    # Limpar o número, removendo todos os caracteres não numéricos
    telefone_limpo = re.sub(r'\D', '', telefone)
    
    # Verificar se o número tem 10 ou 11 dígitos
    if len(telefone_limpo) not in [10, 11]:
        return False, 'O número de telefone deve ter 10 ou 11 dígitos.'
    
    # Se tiver 11 dígitos, verificar se o nono dígito é 9
    if len(telefone_limpo) == 11 and telefone_limpo[2] != '9':
        return False, 'Para números de celular com 11 dígitos, o nono dígito deve ser 9.'
    
    return True, telefone_limpo

# Rota para finalizar o agendamento
@app.route('/agendar', methods=['POST'])
def agendar():
    try:
        # Obter dados do formulário JSON
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'Dados não fornecidos.'}), 400
        
        # Validar dados obrigatórios
        required_fields = ['nome', 'telefone', 'servico_id', 'barbeiro_id', 'data', 'hora_inicio']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Campo obrigatório não fornecido: {field}'}), 400
        
        # Validar o telefone
        telefone_valido, mensagem_ou_telefone = validar_celular(data['telefone'])
        if not telefone_valido:
            return jsonify({'status': 'error', 'message': mensagem_ou_telefone}), 400
        
        # Substituir o telefone pelo número limpo
        data['telefone'] = mensagem_ou_telefone
        
        # Buscar o serviço para calcular a hora de fim
        servico = Servico.query.get(data['servico_id'])
        if not servico:
            return jsonify({'status': 'error', 'message': 'Serviço não encontrado.'}), 404
        
        # Converter a data e hora
        data_agendamento = datetime.strptime(data['data'], '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
        
        # Calcular hora de fim baseado na duração do serviço
        hora_fim_minutos = hora_inicio.hour * 60 + hora_inicio.minute + servico.duracao_minutos
        hora_fim = time(hora_fim_minutos // 60, hora_fim_minutos % 60)
        
        # Verificar se já existe um cliente com este telefone
        cliente = Cliente.query.filter_by(telefone=data['telefone']).first()
        
        # Se não existir, criar um novo cliente
        if not cliente:
            nome_completo = data['nome'].split(' ', 1)
            nome = nome_completo[0]
            sobrenome = nome_completo[1] if len(nome_completo) > 1 else ''
            
            cliente = Cliente(
                nome=nome,
                sobrenome=sobrenome,
                email=data.get('email', f'{nome.lower()}{sobrenome.lower()}@exemplo.com'),  # Email padrão se não fornecido
                telefone=data['telefone']
            )
            db.session.add(cliente)
            db.session.flush()  # Para obter o ID do cliente sem fazer commit
        
        # Criar o agendamento
        agendamento = Agendamento(
            cliente_id=cliente.id,
            barbeiro_id=data['barbeiro_id'],
            servico_id=data['servico_id'],
            data=data_agendamento,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            status='pendente',
            observacoes=data.get('observacoes', '')
        )
        
        db.session.add(agendamento)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Agendamento realizado com sucesso!',
            'agendamento_id': agendamento.id
        })
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erro de formato: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erro ao realizar agendamento: {str(e)}'}), 500


@app.route('/agendamento/cancelar/<int:id>', methods=['POST'])
@login_required
def agendamento_cancelar(id):
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Acesso restrito a administradores.'}), 403
    
    # Buscar o agendamento pelo ID
    agendamento = Agendamento.query.get_or_404(id)
    
    try:
        # Atualizar o status do agendamento para 'cancelado'
        agendamento.status = 'cancelado'
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Agendamento cancelado com sucesso!',
            'agendamento_id': agendamento.id,
            'novo_status': 'cancelado'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erro ao cancelar agendamento: {str(e)}'}), 500


# Rota para reagendar um agendamento
@app.route('/agendamento/reagendar/<int:id>', methods=['POST'])
@login_required
def agendamento_reagendar(id):
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Acesso restrito a administradores.'}), 403
    
    # Buscar o agendamento pelo ID
    agendamento = Agendamento.query.get_or_404(id)
    
    # Obter dados do formulário JSON
    data = request.get_json()
    
    if not data:
        return jsonify({'status': 'error', 'message': 'Dados não fornecidos.'}), 400
    
    # Validar dados obrigatórios
    required_fields = ['data', 'hora_inicio']
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'Campo obrigatório não fornecido: {field}'}), 400
    
    try:
        # Converter a data e hora
        data_agendamento = datetime.strptime(data['data'], '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
        
        # Calcular hora de fim baseado na duração do serviço
        servico = agendamento.servico
        hora_fim_minutos = hora_inicio.hour * 60 + hora_inicio.minute + servico.duracao_minutos
        hora_fim = time(hora_fim_minutos // 60, hora_fim_minutos % 60)
        
        # Verificar se o novo horário não conflita com outros agendamentos
        conflitos = Agendamento.query.filter(
            Agendamento.barbeiro_id == agendamento.barbeiro_id,
            Agendamento.data == data_agendamento,
            Agendamento.status.in_(['pendente', 'agendado', 'concluído']),
            Agendamento.id != agendamento.id,
            # Verificar sobreposição de horários
            ((Agendamento.hora_inicio <= hora_inicio) & (Agendamento.hora_fim > hora_inicio)) |
            ((Agendamento.hora_inicio < hora_fim) & (Agendamento.hora_fim >= hora_fim)) |
            ((Agendamento.hora_inicio >= hora_inicio) & (Agendamento.hora_fim <= hora_fim))
        ).first()
        
        if conflitos:
            return jsonify({
                'status': 'error',
                'message': 'Existe um conflito de horário com outro agendamento.'
            }), 400
        
        # Atualizar o agendamento
        agendamento.data = data_agendamento
        agendamento.hora_inicio = hora_inicio
        agendamento.hora_fim = hora_fim
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Agendamento reagendado com sucesso!',
            'agendamento_id': agendamento.id,
            'nova_data': data_agendamento.strftime('%d/%m/%Y'),
            'novo_horario': hora_inicio.strftime('%H:%M')
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': f'Erro de formato: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erro ao reagendar agendamento: {str(e)}'}), 500


# Rota para concluir serviço
@app.route('/admin/agendamento/concluir/<int:agendamento_id>', methods=['POST'])
@login_required
def admin_agendamento_concluir(agendamento_id):
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Acesso restrito a administradores.'}), 403
    
    # Buscar o agendamento pelo ID
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    
    try:
        # Atualizar o status do agendamento para 'concluído'
        agendamento.status = 'concluído'
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Serviço concluído com sucesso!',
            'agendamento_id': agendamento.id,
            'novo_status': 'concluído'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erro ao concluir serviço: {str(e)}'}), 500


# Rota para página de agendamento manual (admin)
@app.route('/admin/agendar', methods=['GET', 'POST'])
@login_required
def admin_agendar():
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        flash('Acesso restrito a administradores.', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Obter dados do formulário
        cliente_id = request.form.get('cliente_id')
        servico_id = request.form.get('servico_id')
        barbeiro_id = request.form.get('barbeiro_id')
        data_str = request.form.get('data')
        hora_inicio_str = request.form.get('hora_inicio')
        
        # Validar dados obrigatórios
        if not all([cliente_id, servico_id, barbeiro_id, data_str, hora_inicio_str]):
            flash('Por favor, preencha todos os campos obrigatórios.', 'warning')
            return redirect(url_for('admin_agendar'))
        
        try:
            # Buscar cliente, serviço e barbeiro
            cliente = Cliente.query.get(cliente_id)
            servico = Servico.query.get(servico_id)
            barbeiro = Barbeiro.query.get(barbeiro_id)
            
            if not cliente or not servico or not barbeiro:
                flash('Cliente, serviço ou barbeiro não encontrado.', 'danger')
                return redirect(url_for('admin_agendar'))
            
            # Converter a data e hora
            data_agendamento = datetime.strptime(data_str, '%Y-%m-%d').date()
            hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
            
            # Calcular hora de fim baseado na duração do serviço
            hora_fim_minutos = hora_inicio.hour * 60 + hora_inicio.minute + servico.duracao_minutos
            hora_fim = time(hora_fim_minutos // 60, hora_fim_minutos % 60)
            
            # Verificar se o horário não conflita com outros agendamentos
            conflitos = Agendamento.query.filter(
                Agendamento.barbeiro_id == barbeiro.id,
                Agendamento.data == data_agendamento,
                Agendamento.status.in_(['pendente', 'agendado']),
                db.or_(
                    # Caso 1: O novo agendamento começa durante um existente
                    db.and_(
                        Agendamento.hora_inicio <= hora_inicio,
                        Agendamento.hora_fim > hora_inicio
                    ),
                    # Caso 2: O novo agendamento termina durante um existente
                    db.and_(
                        Agendamento.hora_inicio < hora_fim,
                        Agendamento.hora_fim >= hora_fim
                    ),
                    # Caso 3: O novo agendamento engloba um existente
                    db.and_(
                        Agendamento.hora_inicio >= hora_inicio,
                        Agendamento.hora_fim <= hora_fim
                    )
                )
            ).first()
            
            if conflitos:
                flash('Este horário já está ocupado.', 'danger')
                return redirect(url_for('admin_agendar'))
            
            # Criar o novo agendamento
            novo_agendamento = Agendamento(
                cliente_id=cliente.id,
                servico_id=servico.id,
                barbeiro_id=barbeiro.id,
                data=data_agendamento,
                hora_inicio=hora_inicio,
                hora_fim=hora_fim,
                status='agendado'  # Já confirmar o agendamento
            )
            
            db.session.add(novo_agendamento)
            db.session.commit()
            
            flash('Agendamento criado com sucesso!', 'success')
            return redirect(url_for('agenda'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar agendamento: {str(e)}', 'danger')
            return redirect(url_for('admin_agendar'))
    
    # Método GET - Renderizar o formulário
    # Buscar todos os serviços ativos
    servicos = Servico.query.filter_by(ativo=True).all()
    
    # Buscar todos os barbeiros ativos
    barbeiros = Barbeiro.query.filter_by(ativo=True).all()
    
    # Buscar todos os clientes
    clientes = Cliente.query.order_by(Cliente.nome).all()
    
    return render_template('admin_agendamento.html', servicos=servicos, barbeiros=barbeiros, clientes=clientes)


# API para obter horários disponíveis (admin)
@app.route('/api/horarios_disponiveis')
@login_required
def api_horarios_disponiveis_admin():
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Acesso restrito a administradores.'}), 403
    
    # Obter parâmetros da requisição
    data_str = request.args.get('data')
    barbeiro_id = request.args.get('barbeiro_id')
    servico_id = request.args.get('servico_id')
    
    # Validar parâmetros
    if not data_str or not barbeiro_id or not servico_id:
        return jsonify({'status': 'error', 'message': 'Parâmetros incompletos.'}), 400
    
    try:
        # Converter a data
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        
        # Buscar o barbeiro e o serviço
        barbeiro = Barbeiro.query.get(barbeiro_id)
        servico = Servico.query.get(servico_id)
        
        if not barbeiro or not servico:
            return jsonify({'status': 'error', 'message': 'Barbeiro ou serviço não encontrado.'}), 404
        
        # Obter o dia da semana (0 = segunda, 6 = domingo)
        dia_semana = data.weekday()
        
        # Buscar o horário de funcionamento do barbeiro para este dia
        horario_barbeiro = HorarioBarbeiro.query.filter_by(
            barbeiro_id=barbeiro.id,
            dia_semana=dia_semana
        ).first()
        
        # Se o barbeiro não trabalha neste dia
        if not horario_barbeiro or not horario_barbeiro.aberto:
            return jsonify({'status': 'success', 'horarios': []})
        
        # Horário de funcionamento do barbeiro
        hora_abertura = horario_barbeiro.hora_abertura
        hora_fechamento = horario_barbeiro.hora_fechamento
        
        # Duração do serviço em minutos
        duracao_servico = servico.duracao_minutos
        
        # Gerar horários possíveis em intervalos de 30 minutos
        horarios_possiveis = []
        hora_atual = hora_abertura
        
        while True:
            # Calcular a hora de término do serviço
            minutos_totais = hora_atual.hour * 60 + hora_atual.minute + duracao_servico
            hora_fim = time(minutos_totais // 60, minutos_totais % 60)
            
            # Verificar se o serviço termina antes do fechamento
            if hora_fim <= hora_fechamento:
                # Adicionar o horário à lista
                horarios_possiveis.append(hora_atual.strftime('%H:%M'))
            
            # Avançar 30 minutos
            minutos_totais = hora_atual.hour * 60 + hora_atual.minute + 30
            hora_atual = time(minutos_totais // 60, minutos_totais % 60)
            
            # Se passou do horário de fechamento, parar
            if hora_atual >= hora_fechamento:
                break
        
        # Buscar agendamentos existentes para este barbeiro nesta data
        agendamentos_existentes = Agendamento.query.filter(
            Agendamento.barbeiro_id == barbeiro.id,
            Agendamento.data == data,
            Agendamento.status.in_(['pendente', 'agendado'])
        ).all()
        
        # Remover horários que já estão ocupados
        horarios_disponiveis = horarios_possiveis.copy()
        for agendamento in agendamentos_existentes:
            hora_inicio_str = agendamento.hora_inicio.strftime('%H:%M')
            if hora_inicio_str in horarios_disponiveis:
                horarios_disponiveis.remove(hora_inicio_str)
        
        return jsonify({'status': 'success', 'horarios': horarios_disponiveis})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Rota para criar agendamento (admin)
@app.route('/admin/agendamento/criar', methods=['POST'])
@login_required
def admin_agendamento_criar():
    # Verificar se o usuário é admin
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Acesso restrito a administradores.'}), 403
    
    # Obter dados do formulário JSON
    data = request.get_json()
    
    if not data:
        return jsonify({'status': 'error', 'message': 'Dados não fornecidos.'}), 400
    
    # Validar dados obrigatórios
    required_fields = ['cliente_id', 'servico_id', 'barbeiro_id', 'data', 'hora_inicio']
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'Campo obrigatório não fornecido: {field}'}), 400
    
    try:
        # Buscar cliente, serviço e barbeiro
        cliente = Cliente.query.get(data['cliente_id'])
        servico = Servico.query.get(data['servico_id'])
        barbeiro = Barbeiro.query.get(data['barbeiro_id'])
        
        if not cliente or not servico or not barbeiro:
            return jsonify({'status': 'error', 'message': 'Cliente, serviço ou barbeiro não encontrado.'}), 404
        
        # Converter a data e hora
        data_agendamento = datetime.strptime(data['data'], '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
        
        # Calcular hora de fim baseado na duração do serviço
        hora_fim_minutos = hora_inicio.hour * 60 + hora_inicio.minute + servico.duracao_minutos
        hora_fim = time(hora_fim_minutos // 60, hora_fim_minutos % 60)
        
        # Verificar se o horário não conflita com outros agendamentos
        conflitos = Agendamento.query.filter(
            Agendamento.barbeiro_id == barbeiro.id,
            Agendamento.data == data_agendamento,
            Agendamento.status.in_(['pendente', 'agendado']),
            db.or_(
                # Caso 1: O novo agendamento começa durante um existente
                db.and_(
                    Agendamento.hora_inicio <= hora_inicio,
                    Agendamento.hora_fim > hora_inicio
                ),
                # Caso 2: O novo agendamento termina durante um existente
                db.and_(
                    Agendamento.hora_inicio < hora_fim,
                    Agendamento.hora_fim >= hora_fim
                ),
                # Caso 3: O novo agendamento engloba um existente
                db.and_(
                    Agendamento.hora_inicio >= hora_inicio,
                    Agendamento.hora_fim <= hora_fim
                )
            )
        ).first()
        
        if conflitos:
            return jsonify({'status': 'error', 'message': 'Este horário já está ocupado.'}), 400
        
        # Criar o novo agendamento
        novo_agendamento = Agendamento(
            cliente_id=cliente.id,
            servico_id=servico.id,
            barbeiro_id=barbeiro.id,
            data=data_agendamento,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            status='agendado'  # Já confirmar o agendamento
        )
        
        db.session.add(novo_agendamento)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Agendamento criado com sucesso!',
            'agendamento_id': novo_agendamento.id
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Erro ao criar agendamento: {str(e)}'}), 500


# Execução da aplicação
if __name__ == '__main__':
    app.run(debug=True, port=5001)