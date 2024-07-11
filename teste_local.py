import pandas as pd
import psycopg2
import streamlit as st


# Defina sua conexão com o banco de dados
def create_connection():
    dbname = 'Jedai'
    user = 'postgres'  # Substitua pelo seu nome de usuário do PostgreSQL
    password = 'Alpha@5060'  # Substitua pela sua senha do PostgreSQL
    host = '127.0.0.1'  # Substitua pelo seu host do PostgreSQL
    port = '5432'  # Porta padrão do PostgreSQL
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    return conn

def carregar_dados_prova_geografia():
    conn = create_connection()
    query = "SELECT questoes, resposta_correta, explicacao FROM prova_geografia"
    df = pd.read_sql(query, conn)
    conn.close()  # Fecha a conexão após carregar os dados

    perguntas = {}
    explicacoes = {}
    todas_alternativas = set()

    for index, row in df.iterrows():
        alternativas = row['questoes'].split('\n')[1:]
        for alternativa in alternativas:
            letra = alternativa.strip().split(')')[0].lower()
            todas_alternativas.add(letra)

    for index, row in df.iterrows():
        alternativas = row['questoes'].split('\n')[1:]
        alternativas_dict = {letra: f"{letra}) Sem alternativa disponível" for letra in todas_alternativas}
        for alternativa in alternativas:
            letra = alternativa.strip().split(')')[0].lower()
            texto = alternativa.strip()[3:]
            alternativas_dict[letra] = f"{letra}) {texto}"
        perguntas[index + 1] = {
            'questao': row['questoes'].split('\n')[0],
            'alternativas': alternativas_dict,
            'resposta_correta': row['resposta_correta'].strip(),  # Mantém a resposta como está no banco de dados
        }
        explicacao = row['explicacao']
        explicacoes[index + 1] = explicacao if explicacao else "Nenhuma explicação disponível."
    return perguntas, explicacoes

def apresentar_pergunta(pergunta, chave):
    st.write("### " + pergunta['questao'])
    alternativas = pergunta['alternativas']
    todas_alternativas = ['a', 'b', 'c', 'd']  # Ordem correta das alternativas
    alternativas_ordenadas = {letra: alternativas.get(letra, "Sem alternativa disponível") for letra in todas_alternativas}
    for letra in todas_alternativas:
        st.write(alternativas_ordenadas[letra])
    resposta = st.radio(label="Escolha uma opção:", options=list(alternativas_ordenadas.keys()), key=f"radio-{chave}")
    if resposta:
        st.session_state['resposta_usuario'] = resposta

def escolher_prova():
    if st.button('Iniciar Prova'):
        st.session_state['prova_atual'] = 'geografia'
        st.session_state['indice_pergunta'] = 0
        st.session_state['acertos'] = 0
        st.session_state['resposta_submetida'] = False
        st.session_state['resposta_usuario'] = ''
        st.rerun()

def executar_prova(perguntas, explicacoes):
    if 'indice_pergunta' not in st.session_state:
        st.session_state.indice_pergunta = 0
        st.session_state.acertos = 0
        st.session_state.resposta_submetida = False

    if 'resposta_contabilizada' not in st.session_state:
        st.session_state.resposta_contabilizada = False

    indice = st.session_state.indice_pergunta
    total_perguntas = len(perguntas)

    st.write(f"Questão {indice + 1} de {total_perguntas} - Acertos: {st.session_state.acertos}")

    if indice >= total_perguntas:
        st.write(f"Você completou a prova! Acertos: {st.session_state.acertos} de {total_perguntas}")
        if st.button("Refazer a prova"):
            st.session_state.indice_pergunta = 0
            st.session_state.acertos = 0
            st.session_state.resposta_submetida = False
            st.session_state.resposta_contabilizada = False
            st.rerun()
    else:
        pergunta_atual = perguntas.get(indice + 1)
        apresentar_pergunta(pergunta_atual, f'radio-{indice}')

        if st.session_state.resposta_submetida:
            resposta_correta = pergunta_atual['resposta_correta']
            resposta_usuario = st.session_state['resposta_usuario']

            st.write(f"Resposta correta: {resposta_correta}")
            st.write(f"Sua resposta: {resposta_usuario}")

            # Ajustando a comparação para considerar a resposta completa do banco de dados
            resposta_correta_formatada = resposta_correta.lower()  # Convertendo para minúsculas
            resposta_usuario_formatada = resposta_usuario.lower()

            if resposta_usuario_formatada == resposta_correta_formatada:
                if not st.session_state.resposta_contabilizada:
                    st.success("Resposta correta!")
                    st.session_state.acertos += 1
                    st.session_state.resposta_contabilizada = True
            else:
                st.error(f"Resposta incorreta. A resposta correta é: {resposta_correta}.")

            explicacao_atual = explicacoes.get(indice + 1)
            st.write("### Explicação:")
            st.write(explicacao_atual)

            if st.button('Próxima pergunta'):
                st.session_state.indice_pergunta += 1
                st.session_state.resposta_submetida = False
                st.session_state.resposta_contabilizada = False
                st.rerun()
        elif st.button('Confirmar resposta', key='confirmar_resposta', disabled=st.session_state.resposta_submetida):
            st.session_state.resposta_submetida = True

# Interface principal
st.title("Sistema de Provas para treino")
perguntas_geografia, explicacoes_geografia = carregar_dados_prova_geografia()

if 'prova_atual' not in st.session_state:
    escolher_prova()
else:
    executar_prova(perguntas_geografia, explicacoes_geografia)

