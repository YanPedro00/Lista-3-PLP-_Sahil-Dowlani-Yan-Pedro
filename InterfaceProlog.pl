import wx
from swiplserver import PrologMQI

# Função para verificar a compatibilidade usando SWI-Prolog Server
def pode_doar_sangue(nome_doador, nome_receptor, idade, peso, tipo_doador, rh_doador, tipo_receptor, rh_receptor):
    with PrologMQI() as mqi:
        with mqi.create_thread() as prolog_thread:
            prolog_thread.query("consult('DoarSangue.pl').")  # Carregar o arquivo Prolog
            
            # Consultar as regras
            consulta = (
                f"pode_doar_sangue({idade}, {peso}, "
                f"'{tipo_doador}', '{rh_doador}', "
                f"'{tipo_receptor}', '{rh_receptor}')."
            )
            
            resultado = prolog_thread.query(consulta)
            if resultado:
                return f"{nome_doador} está apto para doar sangue para {nome_receptor}!"
            return f"{nome_doador} não pode doar sangue para {nome_receptor}."

# Classe da interface gráfica
class DoacaoSangueApp(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.SetTitle("Verificador de Doação de Sangue")
        self.SetSize((400, 580))
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Inputs para os critérios
        self.nome_doador_label = wx.StaticText(panel, label="Nome do Doador:")
        self.nome_doador_input = wx.TextCtrl(panel)
        self.nome_receptor_label = wx.StaticText(panel, label="Nome do Receptor:")
        self.nome_receptor_input = wx.TextCtrl(panel)
        self.idade_label = wx.StaticText(panel, label="Idade do Doador:")
        self.idade_input = wx.TextCtrl(panel)
        self.peso_label = wx.StaticText(panel, label="Peso do Doador (kg):")
        self.peso_input = wx.TextCtrl(panel)
        self.tipo_doador_label = wx.StaticText(panel, label="Tipo Sanguíneo do Doador (O, A, B, AB):")
        self.tipo_doador_input = wx.TextCtrl(panel)
        self.rh_doador_label = wx.StaticText(panel, label="Fator Rh do Doador (positivo/negativo):")
        self.rh_doador_input = wx.TextCtrl(panel)
        self.tipo_receptor_label = wx.StaticText(panel, label="Tipo Sanguíneo do Receptor (O, A, B, AB):")
        self.tipo_receptor_input = wx.TextCtrl(panel)
        self.rh_receptor_label = wx.StaticText(panel, label="Fator Rh do Receptor (positivo/negativo):")
        self.rh_receptor_input = wx.TextCtrl(panel)
        
        # Botão e saída
        self.check_button = wx.Button(panel, label="Verificar")
        self.result_label = wx.StaticText(panel, label="")
        
        # Layout
        for widget in [
            self.nome_doador_label, self.nome_doador_input, self.nome_receptor_label, self.nome_receptor_input,
            self.idade_label, self.idade_input, self.peso_label, self.peso_input,
            self.tipo_doador_label, self.tipo_doador_input, self.rh_doador_label, self.rh_doador_input,
            self.tipo_receptor_label, self.tipo_receptor_input, self.rh_receptor_label, self.rh_receptor_input,
            self.check_button, self.result_label
        ]:
            sizer.Add(widget, flag=wx.EXPAND | wx.ALL, border=5)
        
        panel.SetSizer(sizer)
        
        # Evento do botão
        self.check_button.Bind(wx.EVT_BUTTON, self.on_check)
    
    def on_check(self, event):
        try:
            nome_doador = self.nome_doador_input.GetValue().strip()
            nome_receptor = self.nome_receptor_input.GetValue().strip()
            idade = int(self.idade_input.GetValue())
            peso = float(self.peso_input.GetValue())
            tipo_doador = self.tipo_doador_input.GetValue().strip().lower()
            rh_doador = self.rh_doador_input.GetValue().strip().lower()
            tipo_receptor = self.tipo_receptor_input.GetValue().strip().lower()
            rh_receptor = self.rh_receptor_input.GetValue().strip().lower()
            
            resultado = pode_doar_sangue(nome_doador, nome_receptor, idade, peso, tipo_doador, rh_doador, tipo_receptor, rh_receptor)
            self.result_label.SetLabel(resultado)
        except ValueError:
            self.result_label.SetLabel("Erro: Certifique-se de preencher os campos corretamente.")

# Execução do aplicativo
if __name__ == "__main__":
    app = wx.App(False)
    frame = DoacaoSangueApp(None)
    frame.Show()
    app.MainLoop()
