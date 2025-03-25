![image](https://github.com/user-attachments/assets/b9b98187-1236-4a87-883c-cd629719b3ec)

## Arquitetura da Solução

![Diagrama de fluxo de um chatbot integrado ao WhatsApp, envolvendo a API do WhatsApp Business, a API da OpenAI e o Heroku. O usuário envia uma mensagem para a API do WhatsApp Business, que a encaminha para um Webhook hospedado no Heroku. O Webhook envia a mensagem para um Wrapper da API da OpenAI, que obtém uma resposta da OpenAI. A resposta é enviada de volta ao Webhook no Heroku, que a repassa para a API do WhatsApp Business, finalizando com o envio da resposta ao usuário no WhatsApp. O Heroku facilita o gerenciamento do Webhook, garantindo um fluxo eficiente de mensagens.](https://github.com/user-attachments/assets/ac37516a-a0ae-41e0-9394-201c56691e38)

Essa imagem ilustra a arquitetura básica, em que:
1. O usuário envia uma mensagem no WhatsApp, que é capturada pela API do WhatsApp Business.
2. A mensagem é encaminhada para um Webhook hospedado no Heroku.
3. O Webhook faz uma requisição à API da OpenAI via um Wrapper.
4. A OpenAI gera uma resposta, que retorna para o Webhook.
5. O Webhook envia a resposta de volta para a API do WhatsApp Business.
6. O WhatsApp entrega a resposta ao usuário. 

---

## **Pré-requisitos: Contas Necessárias**
Para colocar este projeto em funcionamento, você precisará criar contas (algumas exigem cartão de crédito para habilitar o uso de recursos):

1. **Conta na OpenAI**  
   - Necessário **cartão de crédito** para uso da API GPT.  
2. **Conta de desenvolvedor na Meta** (para usar a **Cloud API do WhatsApp**)  
   - Não é exigido cartão de crédito, mas você precisa de um ambiente no [Facebook for Developers](https://developers.facebook.com/).  
3. **Conta no Heroku**  
   - **Poderá exigir um cartão de crédito** para verificação (depende do tipo de plano que você escolher).  

---

## 🔨 **Descrição do Projeto**  
Este projeto consiste na construção de um **chatbot de IA generativa** para responder dúvidas de programação. O bot é integrado à **Cloud API do WhatsApp** e utiliza a **API da OpenAI** para gerar respostas contextuais. A aplicação é desenvolvida em **FastAPI** (Python), garantindo alta performance e escalabilidade.

![](img/amostra.gif)

---

## ✔️ **Técnicas e Tecnologias Utilizadas**  
- **Programação em Python**  
- **Construção de aplicações web com FastAPI**  
- **Integração com a API da OpenAI (ChatCompletions)**  
- **Conexão com a Cloud API do WhatsApp (Meta)**  
- **Construção de Webhook para intermediação de mensagens**  
- **Implantação no Heroku**  

---

## 🛠️ **Como Abrir e Rodar o Projeto Localmente**  

1. **Clone este repositório** ou baixe o código-fonte.  
2. Abra a pasta do projeto no **Visual Studio Code** (ou outro editor de preferência).  
3. Crie e ative um ambiente virtual.  
4. Instale as dependências.  
5. Configure as variáveis de ambiente localmente (arquivo `.env`).  

### **1️⃣ Criar e Ativar o Ambiente Virtual**  

#### **Windows**:
```bash
python -m venv venv-chatbot-wpp
venv-chatbot-wpp\Scripts\activate
```

#### **Mac/Linux**:
```bash
python3 -m venv venv-chatbot-wpp
source venv-chatbot-wpp/bin/activate
```

---

### **2️⃣ Instalar Dependências**  
```bash
pip install -r requirements.txt
```

---

### **3️⃣ Instalar o Heroku CLI (Para Implantação em Nuvem)**  
Caso ainda não tenha o Heroku instalado:

**macOS (via Homebrew):**
```bash
brew tap heroku/brew && brew install heroku
```
**Windows:**
Baixe o Heroku CLI no [site oficial](https://devcenter.heroku.com/articles/heroku-cli).

---

## 🔑 **Configuração de Variáveis de Ambiente**
Antes de executar localmente ou fazer o deploy no Heroku, certifique-se de definir as variáveis de ambiente necessárias.  

### **Em Desenvolvimento Local (arquivo .env)**
Crie o arquivo **`.env`** na raiz do projeto com suas credenciais:

```ini
WHATSAPP_API_TOKEN=SEU_TOKEN
WHATSAPP_CLOUD_NUMBER_ID=SEU_NUMBER_ID
OPENAI_API_KEY=SUA_CHAVE_OPENAI
WHATSAPP_HOOK_TOKEN=SEU_TOKEN_WEBHOOK
PHONE_NUMBER=NUMERO_TELEFONE_COM_CODIGO_PAIS
```

> **Atenção**: Nunca exponha estas chaves em repositórios públicos!

### **No Heroku**
Nas configurações do **Heroku**, acesse a aba “Settings” e clique em “Reveal Config Vars”. Adicione cada variável de ambiente com os mesmos nomes (chave/valor) usados no arquivo `.env`.

Exemplo:

```
WHATSAPP_API_TOKEN         ->  SEU_TOKEN
WHATSAPP_CLOUD_NUMBER_ID   ->  SEU_NUMBER_ID
OPENAI_API_KEY             ->  SUA_CHAVE_OPENAI
WHATSAPP_HOOK_TOKEN        ->  SEU_TOKEN_WEBHOOK
PHONE_NUMBER               ->  NUMERO_TELEFONE_COM_CODIGO_PAIS
```

---

## **Implantação no Heroku**
Após configurar as variáveis de ambiente no Heroku, você pode efetuar o **deploy** do projeto. Existem diversas formas de fazer isso:

- **Via GitHub**: Conecte o repositório ao Heroku e ative o deploy automático ou manual.  
- **Via Git/CLI**: Use o `heroku create` para criar um app, adicione o repositório remoto e faça `git push heroku main`.  

---

## **Testes e Uso**
Depois de publicado no Heroku:

1. Certifique-se de configurar o **Webhook** no **Facebook for Developers**, apontando para a URL do seu app no Heroku, ex.:  
   ```
   https://seuapp.herokuapp.com/webhook/
   ```
2. Valide o **Webhook** informando o **WHATSAPP_HOOK_TOKEN** na configuração do Meta for Developers.  
3. Envie mensagens a partir do WhatsApp para o número configurado.  
4. Se tudo estiver correto, as mensagens chegarão ao endpoint do FastAPI, serão processadas e a resposta chegará via WhatsApp.

---

## **Exemplo de Fluxo de Código (Webhook)**  
Dentro do arquivo `webhook.py`, observe como a notificação é recebida e processada:

```python
@app.post("/webhook/")
async def callback(request: Request):
    # Processa a notificação e extrai dados
    wtsapp_client = WhatsAppClient()
    data = await request.json()
    response = wtsapp_client.process_notification(data)
    
    if response.get("statusCode") == 200:
        # Mensagem válida
        openai_client = OpenAIClient()
        reply = openai_client.complete(message=response["body"])
        
        # Envia resposta ao WhatsApp
        wtsapp_client.send_text_message(
            message=reply, 
            phone_number=response["from_no"]
        )
    
    return {"status": "success"}, 200
```

Esse fluxo garante que, toda vez que o WhatsApp enviar uma requisição ao nosso webhook, a mensagem será processada pela OpenAI para gerar respostas específicas sobre **programação**.

---

## **Conclusão**
Este projeto demonstra como integrar **FastAPI**, **OpenAI** e a **Cloud API do WhatsApp** para criar um chatbot inteligente, focado em dúvidas de programação. A hospedagem no **Heroku** possibilita um ambiente de produção escalável.

> **Obs.:** Lembre-se de que **OpenAI** e **Heroku** podem cobrar pelo uso após certa cota gratuita ou requerer cartão de crédito para verificação de conta.

**Bom desenvolvimento e bons estudos!** 
