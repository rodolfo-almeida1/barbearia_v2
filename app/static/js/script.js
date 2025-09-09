// Variáveis para armazenar as seleções
let servicoSelecionado = null;
let barbeiroSelecionado = null;
let dataSelecionada = null;
let horarioSelecionado = null;

// Configurar as datas mínima e máxima com base nas regras de negócio
document.addEventListener('DOMContentLoaded', function() {
    // Calcular a data mínima (hoje + antecedência mínima em horas)
    const hoje = new Date();
    const dataMinima = new Date(hoje);
    dataMinima.setHours(hoje.getHours() + parseInt(configAgendamento.antecedenciaMinima || 0, 10));
    
    // Calcular a data máxima (hoje + janela máxima em dias)
    const dataMaxima = new Date(hoje);
    dataMaxima.setDate(hoje.getDate() + parseInt(configAgendamento.janelaMaxima || 30, 10));
    
    // Formatar as datas para o formato YYYY-MM-DD
    const dataMinimaFormatada = dataMinima.toISOString().split('T')[0];
    const dataMaximaFormatada = dataMaxima.toISOString().split('T')[0];
    
    // Aplicar as restrições ao campo de data
    const campoData = document.getElementById('data');
    if (campoData) {
        campoData.setAttribute('min', dataMinimaFormatada);
        campoData.setAttribute('max', dataMaximaFormatada);
        campoData.value = dataMinimaFormatada;
    }
    
    // Inicializar os event listeners
    inicializarEventListeners();
});

/**
 * Inicializa todos os event listeners da página
 */
function inicializarEventListeners() {
    // Seleção de serviço (Passo 1)
    const servicosCards = document.querySelectorAll('#passo1 .card-selecao');
    if (servicosCards && servicosCards.length > 0) {
        servicosCards.forEach(card => {
            card.addEventListener('click', selecionarServico);
            card.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    selecionarServico.call(this);
                }
            });
        });
    }
    
    // Seleção de barbeiro (Passo 2)
    const barbeirosCards = document.querySelectorAll('#passo2 .card-selecao');
    if (barbeirosCards && barbeirosCards.length > 0) {
        barbeirosCards.forEach(card => {
            card.addEventListener('click', selecionarBarbeiro);
            card.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    selecionarBarbeiro.call(this);
                }
            });
        });
    }
    
    // Seleção de data (Passo 3)
    const campoData = document.getElementById('data');
    if (campoData) {
        campoData.addEventListener('change', function() {
            dataSelecionada = this.value;
            carregarHorarios();
        });
    }
    
    // Seleção de horário (Passo 3)
    const selectHorario = document.getElementById('horario');
    if (selectHorario) {
        selectHorario.addEventListener('change', function() {
            horarioSelecionado = this.value;
            // Habilitar o botão de próximo quando um horário for selecionado
            const btnProximo3 = document.getElementById('btn-proximo-3');
            if (btnProximo3) {
                btnProximo3.disabled = !horarioSelecionado;
            }
        });
    }
    
    // Botão próximo do passo 3
    const btnProximo3 = document.getElementById('btn-proximo-3');
    if (btnProximo3) {
        btnProximo3.addEventListener('click', function() {
            avancarPasso(3, 4);
        });
    }
    
    // Finalizar agendamento
    const btnFinalizar = document.getElementById('btn-finalizar');
    if (btnFinalizar) {
        btnFinalizar.addEventListener('click', finalizarAgendamento);
    }
    
    // Carregar horários iniciais se a data já estiver preenchida
    const dataInicial = document.getElementById('data');
    if (dataInicial && dataInicial.value) {
        dataSelecionada = dataInicial.value;
    }
}

/**
 * Função para selecionar um serviço
 */
function selecionarServico() {
    // Remover seleção anterior
    document.querySelectorAll('#passo1 .card-selecao').forEach(c => {
        c.classList.remove('selecionado');
        c.setAttribute('aria-pressed', 'false');
    });
    
    // Adicionar seleção ao card clicado
    this.classList.add('selecionado');
    this.setAttribute('aria-pressed', 'true');
    
    // Armazenar o ID do serviço selecionado
    servicoSelecionado = {
        id: this.dataset.id,
        duracao: this.dataset.duracao
    };
    
    // Avançar para o próximo passo após um breve delay
    setTimeout(() => {
        avancarPasso(1, 2);
    }, 300);
}

/**
 * Função para selecionar um barbeiro
 */
function selecionarBarbeiro() {
    // Remover seleção anterior
    document.querySelectorAll('#passo2 .card-selecao').forEach(c => {
        c.classList.remove('selecionado');
        c.setAttribute('aria-pressed', 'false');
    });
    
    // Adicionar seleção ao card clicado
    this.classList.add('selecionado');
    this.setAttribute('aria-pressed', 'true');
    
    // Armazenar o ID do barbeiro selecionado
    barbeiroSelecionado = this.dataset.id;
    
    // Avançar para o próximo passo após um breve delay
    setTimeout(() => {
        avancarPasso(2, 3);
        // Carregar horários disponíveis para a data atual
        carregarHorarios();
    }, 300);
}

/**
 * Função para avançar para o próximo passo com animação
 * @param {number} atual - Número do passo atual
 * @param {number} proximo - Número do próximo passo
 */
function avancarPasso(atual, proximo) {
    const passoAtual = document.getElementById(`passo${atual}`);
    const passoProximo = document.getElementById(`passo${proximo}`);
    
    // Verificar se os elementos existem
    if (!passoAtual || !passoProximo) {
        console.error(`Elementos de passo ${atual} ou ${proximo} não encontrados`);
        return;
    }
    
    // Adicionar classe para iniciar animação de saída
    passoAtual.classList.remove('ativo');
    passoAtual.classList.add('slide-out-left');
    
    // Após a animação de saída, mostrar o próximo passo
    setTimeout(() => {
        passoAtual.classList.remove('slide-out-left');
        passoAtual.style.display = 'none';
        
        // Mostrar o próximo passo com animação de entrada
        passoProximo.style.display = 'block';
        passoProximo.classList.add('slide-in-right');
        passoProximo.classList.add('ativo');
        
        // Se estiver avançando para o passo 3, focar no campo de data
        if (proximo === 3) {
            setTimeout(() => {
                const dataField = document.getElementById('data');
                if (dataField) {
                    dataField.focus();
                }
            }, 100);
        }
        
        // Remover a classe de animação após a conclusão
        setTimeout(() => {
            if (passoProximo) { // Verificar novamente, pois pode ter sido removido
                passoProximo.classList.remove('slide-in-right');
            }
        }, 500);
    }, 500);
}

/**
 * Função para voltar ao passo anterior com animação
 * @param {number} passo - Número do passo anterior
 */
function voltarPasso(passo) {
    const passoAtual = document.querySelector('.passo.ativo');
    const passoAnterior = document.getElementById(`passo${passo}`);
    
    // Verificar se os elementos existem
    if (!passoAtual || !passoAnterior) {
        console.error(`Elemento de passo atual ou passo ${passo} não encontrado`);
        return;
    }
    
    passoAtual.classList.remove('ativo');
    passoAtual.classList.add('fade-out');
    
    setTimeout(() => {
        passoAtual.classList.remove('fade-out');
        passoAtual.style.display = 'none';
        
        passoAnterior.style.display = 'block';
        passoAnterior.classList.add('fade-in');
        passoAnterior.classList.add('ativo');
        
        setTimeout(() => {
            if (passoAnterior) { // Verificar novamente, pois pode ter sido removido
                passoAnterior.classList.remove('fade-in');
            }
        }, 500);
    }, 500);
}

/**
 * Função para carregar horários disponíveis via AJAX
 */
function carregarHorarios() {
    if (!dataSelecionada) {
        const dataElement = document.getElementById('data');
        if (dataElement) {
            dataSelecionada = dataElement.value;
        } else {
            console.error('Elemento de data não encontrado');
            return;
        }
    }
    
    if (!servicoSelecionado || !barbeiroSelecionado || !dataSelecionada) {
        return;
    }
    
    const horarioSelect = document.getElementById('horario');
    const loadingSpinner = document.getElementById('loading-horarios');
    
    if (!horarioSelect) {
        console.error('Elemento select de horários não encontrado');
        return;
    }
    
    // Mostrar indicador de carregamento
    horarioSelect.disabled = true;
    horarioSelect.innerHTML = '<option value="">Carregando horários...</option>';
    
    if (loadingSpinner) {
        loadingSpinner.classList.remove('d-none');
    }
    
    // Fazer requisição AJAX para a API
    fetch(`/api/horarios-disponiveis?data=${encodeURIComponent(dataSelecionada)}&barbeiro_id=${encodeURIComponent(barbeiroSelecionado)}&servico_id=${encodeURIComponent(servicoSelecionado.id)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na resposta da rede');
            }
            return response.json();
        })
        .then(data => {
            // Verificar se o elemento ainda existe
            if (!horarioSelect) {
                console.error('Elemento select de horários não encontrado após requisição');
                return;
            }
            
            horarioSelect.innerHTML = '';
            
            if (data.status === 'success') {
                if (data.horarios_disponiveis && data.horarios_disponiveis.length > 0) {
                    // Adicionar opção padrão
                    const defaultOption = document.createElement('option');
                    defaultOption.value = '';
                    defaultOption.textContent = 'Selecione um horário';
                    horarioSelect.appendChild(defaultOption);
                    
                    // Adicionar horários disponíveis
                    data.horarios_disponiveis.forEach(horario => {
                        const option = document.createElement('option');
                        option.value = horario.hora_inicio;
                        option.textContent = `${horario.hora_inicio} - ${horario.hora_fim}`;
                        horarioSelect.appendChild(option);
                    });
                    
                    horarioSelect.disabled = false;
                } else {
                    // Lista vazia - barbearia fechada ou sem horários disponíveis
                    const option = document.createElement('option');
                    option.value = '';
                    option.textContent = 'Nenhum horário disponível para este dia';
                    option.disabled = true;
                    horarioSelect.appendChild(option);
                    horarioSelect.disabled = true;
                }
            } else {
                // Erro real na comunicação com o servidor
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'Erro ao carregar horários';
                horarioSelect.appendChild(option);
            }
            
            // Esconder indicador de carregamento
            if (loadingSpinner) {
                loadingSpinner.classList.add('d-none');
            }
        })
        .catch(error => {
            console.error('Erro ao carregar horários:', error);
            
            // Verificar se o elemento ainda existe
            if (horarioSelect) {
                horarioSelect.innerHTML = '<option value="">Erro ao carregar horários</option>';
            }
            
            if (loadingSpinner) {
                loadingSpinner.classList.add('d-none');
            }
        });
}

/**
 * Função para finalizar o agendamento
 */
function finalizarAgendamento() {
    // Verificar se os elementos existem antes de acessá-los
    const nomeElement = document.getElementById('nome');
    const telefoneElement = document.getElementById('telefone');
    const observacoesElement = document.getElementById('observacoes');
    
    if (!nomeElement || !telefoneElement) {
        mostrarMensagem('Erro ao processar o formulário. Elementos não encontrados.', 'erro');
        return;
    }
    
    const nome = nomeElement.value;
    const telefone = telefoneElement.value;
    const observacoes = observacoesElement ? observacoesElement.value : '';
    
    // Validar campos obrigatórios
    if (!nome || !telefone) {
        mostrarMensagem('Por favor, preencha todos os campos obrigatórios.', 'erro');
        return;
    }
    
    // Validar formato do telefone (apenas números, 10 ou 11 dígitos)
    const telefoneNumeros = telefone.replace(/\D/g, '');
    if (telefoneNumeros.length !== 10 && telefoneNumeros.length !== 11) {
        mostrarMensagem('Por favor, insira um telefone válido com 10 ou 11 dígitos.', 'erro');
        return;
    }
    
    // Verificar se todas as seleções necessárias foram feitas
    if (!servicoSelecionado || !barbeiroSelecionado || !dataSelecionada || !horarioSelecionado) {
        mostrarMensagem('Por favor, complete todas as etapas de seleção antes de finalizar.', 'erro');
        return;
    }
    
    // Preparar dados para envio
    const dados = {
        nome: nome,
        telefone: telefoneNumeros, // Enviar apenas os números do telefone
        observacoes: observacoes,
        servico_id: servicoSelecionado.id,
        barbeiro_id: barbeiroSelecionado,
        data: dataSelecionada,
        hora_inicio: horarioSelecionado
    };
    
    // Desabilitar botão para evitar múltiplos envios
    const btnFinalizar = document.getElementById('btn-finalizar');
    if (!btnFinalizar) {
        mostrarMensagem('Erro ao processar o formulário. Botão não encontrado.', 'erro');
        return;
    }
    
    btnFinalizar.disabled = true;
    btnFinalizar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
    
    // Enviar dados via AJAX
    fetch('/agendar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dados)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro na resposta da rede');
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            // Limpar formulário e mostrar mensagem de sucesso
            if (nomeElement) nomeElement.value = '';
            if (telefoneElement) telefoneElement.value = '';
            if (observacoesElement) observacoesElement.value = '';
            
            // Mostrar mensagem de sucesso
            mostrarMensagem('Agendamento realizado com sucesso! Em breve entraremos em contato para confirmar.', 'sucesso');
            
            // Voltar para o passo 1 após alguns segundos
            setTimeout(() => {
                resetarFormulario();
            }, 3000);
        } else {
            // Mostrar mensagem de erro
            mostrarMensagem(`Erro ao realizar agendamento: ${data.message}`, 'erro');
        }
        
        // Reabilitar botão
        if (btnFinalizar) {
            btnFinalizar.disabled = false;
            btnFinalizar.innerHTML = 'Finalizar Agendamento';
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao processar sua solicitação. Por favor, tente novamente.', 'erro');
        
        // Reabilitar botão
        if (btnFinalizar) {
            btnFinalizar.disabled = false;
            btnFinalizar.innerHTML = 'Finalizar Agendamento';
        }
    });
}

/**
 * Função para mostrar mensagens de sucesso ou erro
 * @param {string} texto - Texto da mensagem
 * @param {string} tipo - Tipo da mensagem (sucesso ou erro)
 */
function mostrarMensagem(texto, tipo) {
    const mensagemDiv = document.getElementById('mensagem');
    
    // Verificar se o elemento de mensagem existe
    if (!mensagemDiv) {
        console.error('Elemento de mensagem não encontrado');
        return;
    }
    
    mensagemDiv.textContent = texto;
    mensagemDiv.className = `mensagem ${tipo}`;
    mensagemDiv.style.display = 'block';
    
    // Rolar para o topo para mostrar a mensagem
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Esconder a mensagem após alguns segundos
    setTimeout(() => {
        // Verificar se o elemento ainda existe no DOM
        if (mensagemDiv) {
            mensagemDiv.style.display = 'none';
        }
    }, 5000);
}

/**
 * Função para resetar o formulário e voltar ao passo 1
 */
function resetarFormulario() {
    // Voltar para o passo 1
    voltarPasso(1);
    
    // Limpar seleções
    servicoSelecionado = null;
    barbeiroSelecionado = null;
    
    // Manter a data atual se o elemento existir
    const dataInput = document.getElementById('data');
    if (dataInput) {
        dataSelecionada = dataInput.value;
    } else {
        dataSelecionada = null;
    }
    
    horarioSelecionado = null;
    
    // Limpar seleções visuais
    const cards = document.querySelectorAll('.card-selecao');
    if (cards && cards.length > 0) {
        cards.forEach(card => {
            card.classList.remove('selecionado');
            card.setAttribute('aria-pressed', 'false');
        });
    }
    
    // Resetar o select de horários se existir
    const horarioSelect = document.getElementById('horario');
    if (horarioSelect) {
        horarioSelect.innerHTML = '<option value="">Selecione uma data primeiro</option>';
    }
    
    // Desabilitar o botão de próximo se existir
    const btnProximo3 = document.getElementById('btn-proximo-3');
    if (btnProximo3) {
        btnProximo3.disabled = true;
    }
}