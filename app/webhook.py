import os
from fastapi import FastAPI, Request
from app.cliente_whatsapp import WhatsAppClient
from app.cliente_openai import OpenAIClient

# Cria a instância principal do FastAPI
app = FastAPI()

# Carrega o token para validação do Webhook do WhatsApp a partir das variáveis de ambiente
# Este token deve ser o mesmo configurado no Meta for Developers
WHATSAPP_HOOK_TOKEN = os.environ.get("WHATSAPP_HOOK_TOKEN")

@app.get("/")
def iam_alive():
    """
    Endpoint simples para verificar se a API está no ar.
    Retorna uma string indicando que o serviço está vivo.
    
    Exemplo de uso:
      GET /  ->  "Olá Mundo"

    Este endpoint pode ser usado pelo Heroku ou qualquer outro serviço de monitoramento
    para checar rapidamente se a aplicação FastAPI está rodando.
    """
    return "Olá Mundo!"

@app.get("/webhook/")
def subscribe(request: Request):
    """
    Endpoint GET responsável por validar a assinatura do Webhook do WhatsApp.
    
    Fluxo:
      1. O WhatsApp envia uma requisição GET para este endpoint quando configuramos ou alteramos o Webhook.
      2. Recebemos 'hub.verify_token' e 'hub.challenge' como parâmetros de query.
      3. Validamos 'hub.verify_token' comparando com o WHATSAPP_HOOK_TOKEN definido na variável de ambiente.
      4. Se o token for válido, retornamos o 'hub.challenge', confirmando o webhook junto ao WhatsApp.
         Caso contrário, retornamos uma mensagem de falha.
    
    Exemplo de uso:
      GET /webhook/?hub.verify_token=SEU_TOKEN&hub.challenge=123456 -> 123456 (se válido)
    
    :param request: Objeto Request do FastAPI, usado para obter os parâmetros de query.
    :return: Número do desafio (challenge) em caso de sucesso, ou mensagem de falha em caso de token inválido.
    """
    verify_token = request.query_params.get('hub.verify_token')
    challenge = request.query_params.get('hub.challenge')
    
    # Compara o token recebido com o token de ambiente configurado
    if verify_token == WHATSAPP_HOOK_TOKEN and challenge:
        # Se for igual, retorna o challenge como número inteiro
        return int(challenge)
    
    # Caso o token seja inválido, notificamos a falha
    return "Falha na autenticação. Token inválido."

@app.post("/webhook/")
async def callback(request: Request):
    """
    Endpoint POST que recebe notificações (eventos) do WhatsApp e processa as mensagens recebidas.
    
    Fluxo do Callback:
      1. O WhatsApp envia uma requisição POST contendo dados da conversa (mensagens).
      2. Criamos uma instância de WhatsAppClient para interpretar a notificação.
      3. Se a mensagem for válida (statusCode=200 e contiver texto e remetente),
         geramos uma resposta chamando o OpenAIClient.
      4. Enviamos a resposta de volta ao usuário via método 'send_text_message'.
      5. Retornamos um JSON de sucesso (status=success) com código HTTP 200.
    
    Observações:
      - Este endpoint deve ser configurado como o callback do Webhook no Meta for Developers.
      - O uso de 'await request.json()' extrai o corpo da requisição como dicionário (JSON).
    
    :param request: Objeto Request do FastAPI, contendo os dados enviados pelo WhatsApp.
    :return: Um dicionário {'status': 'success'} e código HTTP 200, indicando sucesso.
    """
    print("callback foi chamado...")  # Log simples para indicar que recebemos uma requisição
    
    # Instancia o cliente do WhatsApp para manipular a estrutura da notificação
    wtsapp_client = WhatsAppClient()
    
    # Extrai o conteúdo JSON da requisição assíncrona
    data = await request.json()
    print(f"Recebemos: {data}")
    
    # Processa a notificação usando o método 'process_notification' do WhatsAppClient
    response = wtsapp_client.process_notification(data)
    
    # Se o statusCode for 200, significa que existe uma mensagem de texto processável
    if response.get("statusCode") == 200:
        # Certifica-se de que há conteúdo (body) e o número de origem (from_no)
        if response.get("body") and response.get("from_no"):
            # Cria o cliente da OpenAI para gerar a resposta
            openai_client = OpenAIClient()
            # Chama o método que utiliza o modelo GPT para responder à mensagem
            reply = openai_client.complete(message=response["body"])
            print(f"\nA resposta gerada é: {reply}")
            
            # Envia a mensagem de resposta para o usuário via API do WhatsApp
            wtsapp_client.send_text_message(
                message=reply,
                phone_number=response["from_no"]
            )
            print(f"\nResposta enviada ao WhatsApp Cloud: {response}")
    
    # Retorna um dicionário indicando sucesso, com status code 200
    return {"status": "success"}, 200
