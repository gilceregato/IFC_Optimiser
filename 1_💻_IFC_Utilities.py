# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Created By  : Gilmar Ceregato
# Created Date: 12/12/2024
# version ='0.1'
# ----------------------------------------------------------------------
# O IFC Utilities é um webapp criado com Streamlit para permitir manipulações simples
# de modelos IFC
#
#  Exemplo(s):
#    (completar)
#
#  Attributes:
#    Ex.: Nome_atributo (type): descrição do atributo
#
#  To-dos:
#    * Preencher exemplos
#    * Documentar funções
#    * Preencher a página inicial
# 
# ----------------------------------------------------------------------
__author__ = 'Gilmar Ceregato' 
__copyright__ = 'Copyright 2024, IFC Utilities' 
__credits__ = ['Pessoa 01', 'Pessoa 02'] 
__email__ = 'gilceregato@gmail.com' 
__status__ = 'Prototype' # [Prototype, Development, Production]
# ----------------------------------------------------------------------
# Imports
import ifcopenshell
import ifcpatch
import shutil
import streamlit as st
import tempfile
import os

from datetime import datetime
from pathlib import Path

# ----------------------------------------------------------------------
# Funções

def ifc_upload ():
  # Solicita que o usuário faça o upload de um ou mais arquivos IFC, limitados a 200 Mb cada
  # e salva o arquivo em uma pasta/diretório temporário

  # Parameters:
  # N.A.

  # Returns:
  # ifc_path_list = list(Path): lista dos caminhos dos arquivos na pasta temporária criada 

  ifc_files = st.file_uploader('Faça upload do seu IFC',['ifc'], accept_multiple_files=False)
  ifc_files.read()
  st.write("Nome do arquivo:", ifc_files.name)
  if ifc_files is not None:
    temp_dir = tempfile.mkdtemp()
    ifc_path = os.path.join(temp_dir, ifc_files.name)
    with open(ifc_path, "wb") as f:
      f.write(ifc_files.getvalue())
  
  return ifc_path

def apaga_arquivos_temporários (pasta):
  # Apaga arquivos temporários gerados no processo de validação

  # Parameters:
  # ifc_path_list [list(Path)]: lista dos caminhos até os arquivos IFC que serão validados/ analisados

  # Returns:
  # mensagem = str: aviso de finalização do script

  pasta = Path(pasta).parent
  shutil.rmtree(pasta)
  
  return 'Validação finalizada!'

# ----------------------------------------------------------------------
if __name__ == '__main__':

  # Configuração geral da página no Streamlit
  st.set_page_config(
      page_title="IFC Utilities",
      page_icon="💻",
      layout="wide"
  )

  # Configuração da Sidebar na página
  st.markdown('# IFC Utilities')
  st.sidebar.markdown(':blue[Desenvolvido por Gilmar Ceregato]')
  ## Criando um botão que acessa as especificações de IFC da buildingSmart
  btn = st.sidebar.link_button('Acesse as especificações dos schemas IFC','https://technical.buildingsmart.org/standards/ifc/ifc-schema-specifications/' )

  #Cabeçalho do Dash
  st.title("Bem-vindo ao IFC Utilities!!")

  st.markdown(
      '''
      Este módulo permite otimizar o tamanho de arquivos IFC usando o método de reciclar non-rooted elements
      Esse é um método bastante parecido com o utilizado pelo Solibri Optimiser

      Importante: caso o tamanho dos arquivos seja muito grande o recomendável é utilizar IFCZIP ou "quebrar" o modelo em mais de um arquivo.
      Apenas essa otmização não será suficiente".\n
      '''
  )

  st.divider()
  st.header(':red[Atenção!]')
  st.markdown(
      '''
      Na versão atual as ferramentas tem algumas limitações:\n
      - São aceitos arquivos IFC com até 200 Mb;
  '''
  )

  # Executa a otimização
  ifcs = ifc_upload()
  modelo = ifcopenshell.open(ifcs)
  ifcs_name = Path(ifcs).stem
  
  st.write(Path(ifcs)) #debug
  st.write(Path(ifcs).parent) #debug

  if ifcs is not None:
    ifc_optimised = ifcpatch.execute(
        {"input": "input.ifc",
        "file": modelo,
        "recipe": "RecycleNonRootedElements",
        "arguments": []})

    # Escreve alterações num novo arquivo IFC
    agora=datetime.now().strftime("%Y-%m-%d_T%H:%M") #adicionando timestamp ao nome do arquivo
    nome_novo_arquivo = f'{agora}-Optimised-{ifcs_name}.ifc'
    caminho_nova_pasta = Path(ifcs).parent / nome_novo_arquivo

    st.write(caminho_nova_pasta) #debug

    ifcpatch.write(ifc_optimised, str(caminho_nova_pasta))

    st.write('A migração foi concluída!')
    st.toast('A migração foi concluída!')

    with open(caminho_nova_pasta, "rb") as file:    
          btn = st.download_button(
              label="Download do IFC Otimizado",
              data=file,
              file_name=nome_novo_arquivo,
                  )
    
    btn_end = st.button(label="Clique para limpar arquivos temporários gerados no processo")
    if btn_end:           
      apaga_arquivos_temporários(ifcs)
      st.toast('Arquivos temporários deletados!!')