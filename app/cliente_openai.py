import os
from openai import OpenAI

class OpenAIClient:
    """
    Classe responsável por realizar chamadas à API da OpenAI usando uma chave de API definida
    em uma variável de ambiente. Neste exemplo, o chatbot está configurado para responder apenas
    dúvidas relacionadas a programação. Caso o usuário faça perguntas fora desse escopo,
    a IA deve recusar educadamente.
    
    Dependência:
      - Biblioteca 'openai' instalada e configurada.
    
    Requisitos de Ambiente:
      - A variável de ambiente OPENAI_API_KEY deve conter uma chave válida da OpenAI.
      
    Uso Geral:
      1. Instanciar a classe: openai_client = OpenAIClient()
      2. Chamar o método `complete(<mensagem_do_usuario>)` para obter a resposta da IA.
    """

    def __init__(self):
        """
        Construtor que inicializa o objeto 'client' da OpenAI, carregando a chave de API
        de uma variável de ambiente chamada 'OPENAI_API_KEY'.

        Se a variável de ambiente não estiver definida, gera um ValueError.
        Caso esteja definida, o objeto 'self.client' estará apto a fazer chamadas
        para gerar respostas.
        """
        # Carrega a chave de API da variável de ambiente
        api_key = os.environ.get("OPENAI_API_KEY")
        
        # Verifica se a chave foi encontrada; se não, lança um erro
        if not api_key:
            raise ValueError("A variável 'OPENAI_API_KEY' não está definida nas variáveis de ambiente.")
        
        # Cria a instância da OpenAI com a chave obtida
        self.client = OpenAI(api_key=api_key)
        
        # Recomenda-se não exibir a chave para evitar problemas de segurança;
        # imprimimos apenas uma mensagem de sucesso
        print("Chave de API carregada com sucesso!")

    def complete(self, message: str) -> str:
        """
        Gera uma resposta usando o modelo GPT-4 (ou outro modelo configurado) a partir de uma
        string de entrada do usuário.

        :param message: Texto de entrada (pergunta ou instrução) que o usuário deseja enviar.
        :type message: str
        :return: Resposta gerada pela IA em formato de string.
        :rtype: str

        Detalhes Internos:
          - Fazemos uma chamada ao endpoint de chat.completions, passando um contexto 
            em que o "developer" estipula que o chatbot só responderá questões de programação.
          - Se a pergunta for fora desse tema, a IA deve indicar educadamente que não pode ajudar.
        """
        # Cria a solicitação de 'completion' para o modelo, incluindo a role 'developer'
        # com instruções contextuais para limitar o tema das respostas.
        completion = self.client.chat.completions.create(
            model="gpt-4o",  # Modelo configurado (exemplo fictício "gpt-4o")
            messages=[
                {
                    "role": "developer",
                    "content": (
                        "Você é um chatbot e só deve responder perguntas relacionadas ao tema: "
                        "dúvidas de programação. Cordialmente, diga que não pode ajudar em outros temas."
                    ),
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        )

        # Extrai a resposta da primeira escolha retornada pelo modelo (choices[0])
        response = completion.choices[0].message.content
        print(f"Resposta gerada: {response}")

        return response
