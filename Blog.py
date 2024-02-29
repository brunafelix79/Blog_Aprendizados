import streamlit as st
from PIL import Image
import pyodbc

st.set_page_config(page_title="Meu Blog")


# Função para verificar se a tabela existe no banco de dados
def table_exists(cursor, table_name):
    try:
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?", (table_name,))
        return cursor.fetchone()[0] > 0
    except pyodbc.Error as e:
        st.error(f"Erro ao verificar se a tabela existe: {e}")
        return False


# Função para criar a tabela no banco de dados
def create_table(cursor, conn):
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY,
            title TEXT,
            content TEXT
        )
        ''')
        conn.commit()
    except pyodbc.Error as e:
        st.error(f"Erro ao criar a tabela: {e}")
        st.stop()


# Função para inserir uma nova postagem no banco de dados
def insert_post(cursor, conn, title, content):
    try:
        cursor.execute('INSERT INTO blog_posts (title, content) VALUES (?, ?)', (title, content))
        conn.commit()
    except pyodbc.Error as e:
        st.error(f"Erro ao inserir uma nova postagem: {e}")


# Função para recuperar todas as postagens do banco de dados
def get_all_posts(cursor):
    try:
        cursor.execute('SELECT * FROM blog_posts')
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except pyodbc.Error as e:
        st.error(f"Erro ao recuperar todas as postagens: {e}")
        return []


# Função para recuperar uma postagem pelo título
def get_post_by_title(cursor, title):
    try:
        cursor.execute('SELECT * FROM blog_posts WHERE title = ?', (title,))
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, cursor.fetchone()))
    except pyodbc.Error as e:
        st.error(f"Erro ao recuperar uma postagem pelo título: {e}")
        return None


# Função principal
def main():
    # String de conexão com o banco de dados
    conn_str = ('DRIVER={SQL Server};'
                'SERVER=;'
                'DATABASE=blog_posts;'
                'UID=;'
                'PWD=;'
                'Trusted_Connection=no;')

    try:
        # Conectar ao banco de dados
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
    except pyodbc.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        st.stop()

    # Verificar se a tabela existe
    if not table_exists(cursor, 'blog_posts'):
        create_table(cursor, conn)

    # Barra lateral para adicionar novas postagens
    with st.sidebar:
        try:
            imagem = Image.open(r'C:\Users\bruna\PycharmProjects\pythonProject\Projetos\blog\icon.png')
            st.sidebar.image(imagem)
        except FileNotFoundError:
            st.sidebar.error("Arquivo de imagem não encontrado: Verifique o caminho do arquivo.")

            # Adicionar nova postagem
        st.header('Novo Projeto')
        new_title = st.text_input('Título do novo projeto')
        new_content = st.text_area('Conteúdo do novo projeto')

        post_button = st.button('Postar')

    # Título principal
    st.title('Meu Mini Blog de Aprendizados')

    if post_button:
        if new_title and new_content:
            insert_post(cursor, conn, new_title, new_content)
            st.success('Nova postagem adicionada com sucesso!')
        else:
            st.warning('Título e Conteúdo são obrigatórios')

    # Projetos existentes
    st.header('Projetos Existentes')
    blog_posts = get_all_posts(cursor)

    post_titles = [post['title'] for post in blog_posts]
    selected_post_title = st.selectbox('Selecione uma postagem', post_titles)
    selected_post = get_post_by_title(cursor, selected_post_title)

    if selected_post:
        st.header(selected_post['title'])
        st.write(selected_post['content'])
    else:
        st.error('Post não encontrado.')

    # Fechar a conexão com o banco de dados
    try:
        conn.close()
    except pyodbc.Error as e:
        st.error(f"Erro ao fechar a conexão com o banco de dados: {e}")


# Executar a função principal
if __name__ == "__main__":
    main()
