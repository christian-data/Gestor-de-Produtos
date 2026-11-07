from tkinter import ttk
from tkinter import *
import sqlite3

class Produto:
    db = 'database/produtos.db'

    def __init__(self, root):
        self.janela = root
        self.janela.title("Gestor de Produtos")
        self.janela.resizable(1, 1)
        self.janela.wm_iconbitmap('recursos/M6_P2_icon.ico')

        # --- CONTAINER PRINCIPAL (FRAME) ---
        frame = LabelFrame(self.janela, text="Registrar um novo Produto", font=('Calibri', 16, 'bold'))
        frame.grid(row=0, column=0, columnspan=2, pady=10, padx=10)

        # Entrada Nome
        self.etiqueta_nome = Label(frame, text="Nome: ")
        self.etiqueta_nome.grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.nome = Entry(frame)
        self.nome.focus()
        self.nome.grid(row=1, column=1, padx=5, pady=5)

        # Entrada Preço
        self.etiqueta_preço = Label(frame, text="Preço: ")
        self.etiqueta_preço.grid(row=2, column=0, sticky=W, padx=5, pady=5)
        self.preco = Entry(frame)
        self.preco.grid(row=2, column=1, padx=5, pady=5)

        # Botão Guardar Produto
        self.botao_adicionar = ttk.Button(frame, text="Guardar Produto", command=self.add_produto,)
        self.botao_adicionar.grid(row=3, columnspan=2, sticky=W + E, padx=5, pady=5)

        # --- ELEMENTOS DA JANELA PRINCIPAL ---
        self.mensagem = Label(self.janela, text='', fg='green', font=('Calibri', 11, 'bold'))
        self.mensagem.grid(row=1, column=0, columnspan=2, sticky=W + E, pady=5)

        # Estilo da Tabela
        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 11))
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 12, 'bold'))
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

        # Tabela (Row 2)
        self.tabela = ttk.Treeview(self.janela, height=10, columns=(1,), style="mystyle.Treeview")
        self.tabela.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        self.tabela.heading('#0', text='Nome', anchor=CENTER)
        self.tabela.heading('#1', text='Preço', anchor=CENTER)

        # Botões de Eliminar e Editar (Row 3)
        botão_eliminar = ttk.Button(self.janela, text='ELIMINAR', command=self.del_produto)
        botão_eliminar.grid(row=3, column=0, sticky=W + E, padx=10, pady=10)

        botão_editar = ttk.Button(self.janela, text='EDITAR', command=self.edit_produto)
        botão_editar.grid(row=3, column=1, sticky=W + E, padx=10, pady=10,)

        # Carregar produtos iniciais
        try:
            self.get_produtos()
        except sqlite3.OperationalError:
            self.mensagem['text'] = "Erro ao carregar a BD. Certifique-se de que a tabela 'produto' existe."
            self.mensagem['fg'] = 'orange'

    def del_produto(self):
        self.mensagem['text'] = ''
        selecao = self.tabela.selection()

        if not selecao:
            self.mensagem['fg'] = 'red'
            self.mensagem['text'] = 'Por favor, selecione um produto primeiro!'
            return

        nome = self.tabela.item(selecao)['text']
        query = 'DELETE FROM produto WHERE nome = ?'

        try:
            self.db_consulta(query, (nome,))
            self.mensagem['fg'] = 'blue'
            self.mensagem['text'] = 'Produto "{}" eliminado com êxito'.format(nome)
            self.get_produtos()

        except sqlite3.Error as erro:
            self.mensagem['fg'] = 'red'
            self.mensagem['text'] = 'Erro ao eliminar: {}'.format(erro)

    # --- FUNÇÃO EDITAR PRODUTO ---
    def edit_produto(self):
        self.mensagem['text'] = ''
        selecao = self.tabela.selection()

        if not selecao:
            self.mensagem['fg'] = 'red'
            self.mensagem['text'] = 'Por favor, selecione um produto para editar!'
            return

        # Resgata os dados da Treeview
        nome_antigo = self.tabela.item(selecao)['text']
        valores = self.tabela.item(selecao)['values']
        # Pega no primeiro valor da lista se ele existir
        preco_antigo = valores[0] if valores else ""

        # Criação da Janela Pop-up
        self.janela_editar = Toplevel()
        self.janela_editar.title("app Gestor de Produtos")
        self.janela_editar.wm_iconbitmap('recursos/M6_P2_icon.ico')

        # Layout da Janela de Edição
        Label(self.janela_editar, text="Nome Antigo:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        Entry(self.janela_editar, textvariable=StringVar(self.janela_editar, value=nome_antigo), state='readonly').grid(
            row=0, column=1, padx=5, pady=5)

        Label(self.janela_editar, text="Novo Nome:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        novo_nome = Entry(self.janela_editar)
        novo_nome.grid(row=1, column=1, padx=5, pady=5)
        novo_nome.insert(0, nome_antigo)

        Label(self.janela_editar, text="Novo Preço:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        novo_preco = Entry(self.janela_editar)
        novo_preco.grid(row=2, column=1, padx=5, pady=5)
        novo_preco.insert(0, str(preco_antigo))

        # Botão para Guardar as alterações na janela Pop-up
        ttk.Button(self.janela_editar, text="Atualizar o Produto",
                   command=lambda: self.atualizar_produto(novo_nome.get(), nome_antigo, novo_preco.get())).grid(row=3,
                                                                                                                columnspan=2,
                                                                                                                sticky=W + E,
                                                                                                                padx=5,
                                                                                                                pady=10)

    # --- FUNÇÃO PARA EXECUTAR O UPDATE ---
    def atualizar_produto(self, novo_nome, nome_antigo, novo_preco):
        if len(novo_nome) == 0 or len(novo_preco) == 0:
            return

        query = 'UPDATE produto SET nome = ?, preco = ? WHERE nome = ?'
        parametros = (novo_nome, novo_preco, nome_antigo)

        try:
            self.db_consulta(query, parametros)
            self.janela_editar.destroy()
            self.mensagem['fg'] = 'green'
            self.mensagem['text'] = 'Produto "{}" atualizado com sucesso'.format(nome_antigo)
            self.get_produtos()
        except sqlite3.Error as erro:
            self.mensagem['fg'] = 'red'
            self.mensagem['text'] = 'Erro ao atualizar: {}'.format(erro)

    def validacao_nome(self):
        return len(self.nome.get()) != 0

    def validacao_preco(self):
        return len(self.preco.get()) != 0

    def add_produto(self):
        if self.validacao_nome() and self.validacao_preco():
            query = 'INSERT INTO produto VALUES(NULL, ?, ?)'
            parametros = (self.nome.get(), self.preco.get())

            self.db_consulta(query, parametros)

            self.mensagem['fg'] = 'green'
            self.mensagem['text'] = 'Produto {} adicionado com êxito'.format(self.nome.get())

            self.nome.delete(0, END)
            self.preco.delete(0, END)
            self.nome.focus()

            self.get_produtos()
        else:
            self.mensagem['fg'] = 'red'
            self.mensagem['text'] = "O nome e o preço são obrigatórios"

    def db_consulta(self, consulta, parametros=()):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            resultado = cursor.execute(consulta, parametros)
            con.commit()
        return resultado

        # --- MAPEAMENTO DOS ÍNDICES DO SQLITE ---

    def get_produtos(self):
        registos_tabela = self.tabela.get_children()
        for linha in registos_tabela:
            self.tabela.delete(linha)

        query = 'SELECT * FROM produto ORDER BY nome DESC'
        registos_db = self.db_consulta(query)
        for linha in registos_db:
            self.tabela.insert('', 0, text=linha[1], values=(linha[2],))

if __name__ == '__main__':
    root = Tk()
    app = Produto(root)
    root.mainloop()

