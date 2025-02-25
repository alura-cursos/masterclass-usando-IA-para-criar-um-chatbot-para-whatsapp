import os
import requests
import json
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Exemplo de número de telefone carregado da variável de ambiente
PHONE_NUMBER = os.environ.get("PHONE_NUMBER")

class WhatsAppClient:
    """
    Classe responsável pela integração com a API do WhatsApp Cloud (Meta) para envio e recebimento
    de mensagens em um bot ou aplicativo.  
    
    Requisitos de Ambiente:
      - As variáveis de ambiente WHATSAPP_API_TOKEN e WHATSAPP_CLOUD_NUMBER_ID devem estar definidas;
      - Opcionalmente, PHONE_NUMBER pode ser usada para testes diretos;
      - É recomendável usar a biblioteca 'python-dotenv' para carregar as variáveis do arquivo .env.
    
    Fluxo Básico:
      1. Crie uma instância: wts_client = WhatsAppClient()
      2. Use send_text_message(...) ou send_template_message(...) para enviar mensagens.
      3. Chame process_notification(...) para lidar com as notificações de mensagens recebidas (webhook).
    """

    # URL base da API do WhatsApp; versionada conforme documentação oficial
    API_URL = "https://graph.facebook.com/v15.0/"
    
    # Carrega as credenciais da API
    WHATSAPP_API_TOKEN = os.environ.get("WHATSAPP_API_TOKEN")
    WHATSAPP_CLOUD_NUMBER_ID = os.environ.get("WHATSAPP_CLOUD_NUMBER_ID")

    def __init__(self):
        """
        Construtor para configurar o cabeçalho HTTP (Authorization e Content-Type) e montar
        a URL de requisição com base no 'WHATSAPP_CLOUD_NUMBER_ID'.

        Se WHATSAPP_API_TOKEN ou WHATSAPP_CLOUD_NUMBER_ID não estiverem definidos, resultará
        em problemas de autenticação.
        """
        # Define os cabeçalhos padrão para todas as requisições ao WhatsApp Cloud
        self.headers = {
            "Authorization": f"Bearer {self.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json",
        }
        # Concatena a URL base com o 'WHATSAPP_CLOUD_NUMBER_ID' para direcionar as mensagens
        self.API_URL = self.API_URL + str(self.WHATSAPP_CLOUD_NUMBER_ID)

    def send_template_message(self, template_name, language_code, phone_number):
        """
        Envia uma mensagem baseada em um 'template' (modelo) pré-configurado no WhatsApp Cloud.
        
        Parâmetros:
          :param template_name: (str) Nome do template cadastrado no gerenciador de mensagens do WhatsApp.
          :param language_code: (str) Código de idioma do template (exemplo: "pt_BR", "en_US").
          :param phone_number:  (str) Número do destinatário, incluindo o código do país (ex: "5511999999999").
        
        Retorno:
          :return: (int) Código de status da resposta da requisição (esperado 200 em caso de sucesso).
        
        Exemplo de Uso:
          wts_client.send_template_message("hello_world", "en_US", "5511999999999")
        """
        # O 'payload' contém o corpo da mensagem em formato JSON, seguindo o padrão da API do WhatsApp.
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }

        # Envia a mensagem ao endpoint /messages da API do WhatsApp Cloud
        response = requests.post(
            f"{self.API_URL}/messages",
            json=payload,
            headers=self.headers
        )

        # Verifica se o status de retorno é 200 (sucesso)
        # Caso contrário, interrompe com uma exceção para facilitar o debug
        assert response.status_code == 200, f"Erro ao enviar mensagem de template: {response.text}"

        return response.status_code

    def send_text_message(self, message, phone_number):
        """
        Envia uma mensagem de texto simples via WhatsApp Cloud.
        
        Parâmetros:
          :param message: (str) Conteúdo de texto que será enviado ao usuário.
          :param phone_number: (str) Número do destinatário, incluindo o código do país (ex: "5511999999999").
        
        Retorno:
          :return: (int) Código de status da resposta da requisição (esperado 200 em caso de sucesso).
        
        Exemplo de Uso:
          wts_client.send_text_message("Olá, tudo bem?", "5511999999999")
        """
        # Monta o payload da mensagem de texto, seguindo o formato exigido pela API
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }

        # Faz a requisição POST para enviar a mensagem
        response = requests.post(
            f"{self.API_URL}/messages",
            json=payload,
            headers=self.headers
        )
        
        # Exibe o código e o texto de resposta para facilitar depuração
        print(response.status_code)
        print(response.text)

        # Verifica se obteve sucesso ao enviar
        assert response.status_code == 200, f"Erro ao enviar mensagem de texto: {response.text}"

        return response.status_code

    def process_notification(self, data):
        """
        Processa a notificação (webhook) recebida do WhatsApp Cloud. 
        Verifica se a mensagem contém texto, e se existir, retorna as informações necessárias
        para que nosso backend (FastAPI) possa responder.

        Parâmetros:
          :param data: (dict) Dicionário com os dados enviados pelo WhatsApp Cloud via webhook.
        
        Retorno:
          :return: (dict) Estrutura contendo:
                    "statusCode" -> 200 se a mensagem for texto válido, caso contrário 403
                    "body"       -> Conteúdo textual da mensagem
                    "from_no"    -> Número de telefone do remetente
                    "isBase64Encoded" -> Indica se o body está codificado em base64 (False neste caso)
        
        Observação:
          - As notificações do WhatsApp Cloud são enviadas dentro de um JSON com chaves como
            'entry' e 'changes'. Cada nível precisa ser verificado para evitar erros de chave inexistente.
        """
        # Usa o .get() para evitar exceções de chave ausente
        entries = data.get("entry", [])
        
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value")
                if value:
                    if "messages" in value:
                        for message in value["messages"]:
                            # Verifica se o tipo da mensagem é 'text'
                            if message.get("type") == "text":
                                from_no = message.get("from")
                                message_body = message["text"].get("body")
                                print(f"Ack from FastAPI-WtsApp Webhook: {message_body}")
                                
                                # Retorna informações relevantes para nosso fluxo de resposta
                                return {
                                    "statusCode": 200,
                                    "body": message_body,
                                    "from_no": from_no,
                                    "isBase64Encoded": False
                                }

        # Se não encontrou mensagens de texto, retorna um código 403 para indicar que não foi processável
        return {
            "statusCode": 403,
            "body": json.dumps("Método não suportado"),
            "isBase64Encoded": False
        }

# Se este arquivo for executado diretamente, podemos fazer um teste simples
if __name__ == "__main__":
    # Exemplo: Cria uma instância do cliente e envia um template message para o PHONE_NUMBER carregado
    client = WhatsAppClient()
    if PHONE_NUMBER:
        response_code = client.send_template_message("hello_world", "en_US", PHONE_NUMBER)
        print(f"Código de resposta do template message: {response_code}")
    else:
        print("PHONE_NUMBER não definido nas variáveis de ambiente. Verifique o arquivo .env ou as Config Vars.")
