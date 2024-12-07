import wx
from swiplserver import PrologMQI

def pode_doar(idade, peso, tipo_doador, rh_doador, tipo_receptor, rh_receptor):
    with PrologMQI() as mqi:
        with mqi.create_thread() as prolog:
            prolog.query("consult('DoarSangue.pl').")
            
            # Consultar as regras
            consulta = (
                f"podedoar({idade}, {peso}, "
                f"'{tipo_doador}', '{rh_doador}', "
                f"'{tipo_receptor}', '{rh_receptor}')."
            )
            
            resultado = prolog.query(consulta)
            
            return "    Resultado: Compatíveis" if resultado else "    Resultado: Incompatíveis"
           
        
def identificar_pessoas(fatorrh=None, tipo_sanguineo=None):
    with PrologMQI() as mqi:
        with mqi.create_thread() as prolog:
            prolog.query("consult('DoarSangue.pl').")

            nomes = ""
            i = 0 

            if fatorrh is None:  # Se foi fornecido tipo sanguíneo
                resultado = prolog.query(f"tiposanguineo(X, {tipo_sanguineo}).")
                for nome in resultado:
                    nomes = nomes + nome['X'] + "," 
                    i += 1
                    if i == 3:  # Adiciona uma quebra de linha a cada 3 nomes
                        nomes = nomes + "\n"
                        i = 0 
    
            elif tipo_sanguineo is None:  # Se foi fornecido Fator Rh
                resultado = prolog.query(f"fatorrh(X, {fatorrh}).")
                for nome in resultado:
                    nomes = nomes + nome['X'] + "," 
                    i += 1
                    if i == 3:  # Adiciona uma quebra de linha a cada 3 nomes
                        nomes = nomes + "\n"
                        i = 0

            return nomes

            

def DoadorReceptor(nomePessoa):
    with PrologMQI() as mqi:
        with mqi.create_thread() as prolog:
            prolog.query("consult('DoarSangue.pl').")
            
            # Objetivo: Encontrar esses caras, em formato de strings agrupadas.
            doadores, receptores = "Doa para:\n    ", "Recebe de:\n    "

            # Dados iniciais da pessoa.
            idade = prolog.query(f"idade({nomePessoa}, X).")[0]['X']
            peso = prolog.query(f"peso({nomePessoa}, X).")[0]['X']
            tipo_sanguineo = prolog.query(f"tiposanguineo({nomePessoa}, X).")[0]['X']
            fator_rh = prolog.query(f"fatorrh({nomePessoa}, X).")[0]['X']

            # Caso 0: Pessoa não identificada.
            if not idade or not peso:
                return f"{nomePessoa} não encontrada na base de dados!"
            
            # Caso 1: Observar Situacao Fisica
            resultado_teste_aptidao = prolog.query(f"aptidao({idade}, {peso}).")

            
            if resultado_teste_aptidao: # Se teve resultado Pode Doar
                # Pra quem?

                tipos_compativeis = prolog.query(f"compativel({tipo_sanguineo}, X).") #[a, ab]
                rh_compativeis = prolog.query(f"rhcomp({fator_rh}, X).") # [+]
                
                # Conjuntos 
                pessoas_tipo_compativeis = set()

                for tipo in tipos_compativeis:
                    resultado = prolog.query(f"tiposanguineo(X, {tipo['X']}).")
                    for nome in resultado:
                        pessoas_tipo_compativeis.add(nome['X'])


                pessoas_rh_compativeis = set()

                for rh in rh_compativeis:
                    resultado = prolog.query(f"fatorrh(X, {rh['X']}).")
                    for nome in resultado:
                       pessoas_rh_compativeis.add(nome['X'])

                doa_para = pessoas_tipo_compativeis.intersection(pessoas_rh_compativeis)
                
                i = 0
                for nomepessoa in doa_para:
                    p = nomepessoa  +  "," 
                    i+=1
                    if i == 2:
                        i=0
                        p += "\n    "
                    doadores += p

            # Pessoas as quais nomePessoa pode receber:
            '''
            Algoritmo para identificar as pessoas de quem fulano pode receber sangue.

            Fulano: 
                tiposanguineo(Fulano, X) : ab
                fatorrh(Fulano, X): +

            compativel(X, AB): [a, b, ab]
            rhcomp(X, +): [-, +]

            Para todo tipo sanguíneo resultante, pegue o nome dessas pessoas.
                tiposanguineo(X, a)
                tiposanguineo(X, b)
                tiposanguineo(x, ab)

            Para todo fator rh resultante, pegue o nome dessas pessoas.
                fatorrh(X, -)
                fatorrh(X, +)

            Pegue as pessoas em comum.

            '''
            
            tipos_compativeis = prolog.query(f"compativel(X, {tipo_sanguineo}).")
            rh_compativeis = prolog.query(f"rhcomp(X, {fator_rh}).")

            pessoas_tipo_compativeis = set()

            for tipo in tipos_compativeis:
                    resultado = prolog.query(f"tiposanguineo(X, {tipo['X']}).")
                    for nome in resultado:
                        pessoas_tipo_compativeis.add(nome['X'])

            pessoas_rh_compativeis = set()

            for rh in rh_compativeis:
                resultado = prolog.query(f"fatorrh(X, {rh['X']}).")
                for nome in resultado:
                    pessoas_rh_compativeis.add(nome['X'])

            recebe_de = pessoas_tipo_compativeis.intersection(pessoas_rh_compativeis)
                
            i = 0
            for nomepessoa in recebe_de:
                p = nomepessoa  +  "," 
                i+=1
                if i == 2:
                    i=0
                    p += "\n    "
                receptores += p

            resposta = doadores + "\n" + receptores
            return resposta



class Home(wx.Frame):
    def __init__(self, *args, **kw):
        super(Home, self).__init__(*args, **kw)
        
        self.panel = wx.Panel(self)
        
        # Criação dos botões
        btn_calculadora = wx.Button(self.panel, label="Calculadora de Compatibilidade", pos=(20, 20))
        btn_fulano = wx.Button(self.panel, label="Fulano Doa/Recebe Para/De Quem?", pos=(20, 60))
        btn_encontrar_fator = wx.Button(self.panel, label="Encontrar Pessoas Com Sangue X ou RH Y", pos=(20, 100))

        # Bind dos botões a métodos
        btn_calculadora.Bind(wx.EVT_BUTTON, self.on_calculadora)
        btn_fulano.Bind(wx.EVT_BUTTON, self.on_fulano)
        btn_encontrar_fator.Bind(wx.EVT_BUTTON, self.on_encontrar_fator)

        self.SetSize((400, 200))
        self.SetTitle("HEMOSTASIS")
        self.Centre()
        self.Show()

    def on_calculadora(self, event):
        # Criar e exibir a janela de compatibilidade
        compatibilidade_frame = Compatibilidade(None)
        compatibilidade_frame.Show()     

    def on_fulano(self, event):
        DoarReceber_frame = Doador_Receptor(None)
        DoarReceber_frame.Show()

    def on_encontrar_fator(self, event):
        encontrar_fator_frame = identificarPessoas(None)
        encontrar_fator_frame.Show()

class Compatibilidade(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.SetTitle("Compatibilidade")
        self.SetSize((450, 750))
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Inputs para os critérios
        self.nome_doador_label = wx.StaticText(panel, label="Informações do Doador:")
        self.idade_label = wx.StaticText(panel, label="Idade:")
        self.idade_input = wx.TextCtrl(panel)
        self.peso_label = wx.StaticText(panel, label="Peso(kg):")
        self.peso_input = wx.TextCtrl(panel)
        self.tipo_doador_label = wx.StaticText(panel, label="Tipo Sanguíneo (O, A, B, AB):")
        self.tipo_doador_input = wx.TextCtrl(panel)
        self.rh_doador_label = wx.StaticText(panel, label="Fator Rh(+/-):")
        self.rh_doador_input = wx.TextCtrl(panel)
        self.nome_receptor_label = wx.StaticText(panel, label="Informações do Receptor:")
        self.tipo_receptor_label = wx.StaticText(panel, label="Tipo Sanguíneo(O, A, B, AB):")
        self.tipo_receptor_input = wx.TextCtrl(panel)
        self.rh_receptor_label = wx.StaticText(panel, label="Fator Rh (+/-):")
        self.rh_receptor_input = wx.TextCtrl(panel)
        
        # Botão e saída
        self.check_button = wx.Button(panel, label="Confirmar")
        self.result_label = wx.StaticText(panel, label="")
        
        # Layout
        for widget in [
            self.nome_doador_label,
            self.idade_label, self.idade_input, self.peso_label, self.peso_input,
            self.tipo_doador_label, self.tipo_doador_input, self.rh_doador_label, self.rh_doador_input,
            self.nome_receptor_label, self.tipo_receptor_label, self.tipo_receptor_input, self.rh_receptor_label, self.rh_receptor_input,
            self.check_button, self.result_label
        ]:
            sizer.Add(widget, flag=wx.EXPAND | wx.ALL, border=5)
        
        panel.SetSizer(sizer)
        
        # Evento do botão
        self.check_button.Bind(wx.EVT_BUTTON, self.on_check)
    
    def on_check(self, event):
        try:
            idade = int(self.idade_input.GetValue())
            peso = float(self.peso_input.GetValue())
            tipo_doador = self.tipo_doador_input.GetValue().strip().lower()
            rh_doador = self.rh_doador_input.GetValue().strip().lower()
            tipo_receptor = self.tipo_receptor_input.GetValue().strip().lower()
            rh_receptor = self.rh_receptor_input.GetValue().strip().lower()
            
            resultado = pode_doar(idade, peso, tipo_doador, rh_doador, tipo_receptor, rh_receptor)
            self.result_label.SetLabel(resultado)
        except ValueError:
            self.result_label.SetLabel("Erro: Certifique-se de preencher os campos corretamente.")

class identificarPessoas(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.SetTitle("Buscador")
        self.SetSize((400, 400))
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Inputs para os critérios
        self.tipo_Sanguineo_label = wx.StaticText(panel, label="Tipo Sanguíneo:")
        self.tipo_input = wx.TextCtrl(panel)
        self.espaco = wx.StaticText(panel, label="")
        self.fator_rh_label = wx.StaticText(panel, label="Fator RH:")
        self.fator_input = wx.TextCtrl(panel)

        # Botão e saída
        self.check_buttonTipo = wx.Button(panel, label="Buscar")
        self.result_labelTipo = wx.StaticText(panel, label="")

        # Botão e saída
        self.check_buttonFator = wx.Button(panel, label="Buscar")
        self.result_labelFator = wx.StaticText(panel, label="")

        # Layout
        for widget in [
            self.tipo_Sanguineo_label,
            self.tipo_input, self.check_buttonTipo, self.result_labelTipo, 
            self.espaco, self.fator_rh_label, 
            self.fator_input, self.check_buttonFator, self.result_labelFator
        ]:
            sizer.Add(widget, flag=wx.EXPAND | wx.ALL, border=5)
        
        panel.SetSizer(sizer)

        # Evento do botão
        self.check_buttonTipo.Bind(wx.EVT_BUTTON, self.on_checkTipo)
        self.check_buttonFator.Bind(wx.EVT_BUTTON, self.on_checkFator)
        
    def on_checkTipo(self, event):
        try:
            tipo = self.tipo_input.GetValue().strip().lower()
            resultadoTipo = identificar_pessoas(tipo_sanguineo=tipo)
            self.result_labelTipo.SetLabel(resultadoTipo)
        except ValueError:
            self.result_labelTipo.SetLabel("Erro: Certifique-se de preencher os campos corretamente.")

    def on_checkFator(self, event):
        try:
            fator = self.fator_input.GetValue().strip()
            resultadoFator = identificar_pessoas(fatorrh=fator)
            self.result_labelFator.SetLabel(resultadoFator)
        except ValueError:
            self.result_labelFator.SetLabel("Erro: Certifique-se de preencher os campos corretamente.")
        
class Doador_Receptor(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.SetTitle("Doador/Receptor")
        self.SetSize((400, 400))
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Inputs para os critérios
        self.tipo_Sanguineo_label2 = wx.StaticText(panel, label="Inserir nome:")
        self.nome_input = wx.TextCtrl(panel)
        self.espaco = wx.StaticText(panel, label="")

        # Botão e saída
        self.check_buttonTipo = wx.Button(panel, label="Buscar")
        self.result_label = wx.StaticText(panel, label="")

        # Layout
        for widget in [
            self.tipo_Sanguineo_label2, self.nome_input,
            self.espaco, self.check_buttonTipo, self.result_label
        ]:
            sizer.Add(widget, flag=wx.EXPAND | wx.ALL, border=5)
        
        panel.SetSizer(sizer)

        # Evento do botão
        self.check_buttonTipo.Bind(wx.EVT_BUTTON, self.on_checkTipo)
        
    def on_checkTipo(self, event):
        try:
            nome = self.nome_input.GetValue().strip().lower()
            resultadoTipo = DoadorReceptor(nome)
            self.result_label.SetLabel(resultadoTipo)
        except ValueError:
            self.result_label.SetLabel("Erro: Certifique-se de preencher os campos corretamente.")
        

if __name__ == "__main__":
    app = wx.App(False)
    frame = Home(None, title="Sistema de Controle Sanguineo")
    frame.Show()
    app.MainLoop()

