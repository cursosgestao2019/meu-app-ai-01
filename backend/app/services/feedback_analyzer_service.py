# backend/app/services/feedback_analyzer_service.py

import os
import json
import logging
from openai import AsyncOpenAI, OpenAIError # Importa a lib da OpenAI
from fastapi import HTTPException

from app.models.ai_models import FeedbackAnalysisResponse

logger = logging.getLogger(__name__)

# Inicializa o cliente OpenAI fora da função para reutilização
# Pega a chave da variável de ambiente configurada no .env
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.warning("OPENAI_API_KEY não encontrada. A análise de feedback não funcionará.")
    # Você pode decidir lançar um erro aqui ou permitir que continue (mas falhará na chamada)
    # raise ValueError("Chave da API OpenAI não configurada.")

# Usar AsyncOpenAI para chamadas assíncronas
client = AsyncOpenAI(api_key=api_key)

async def analyze_feedback_text(text: str) -> FeedbackAnalysisResponse:
    """
    Analisa o texto do feedback usando a API da OpenAI.
    """
    if not client.api_key:
         raise HTTPException(status_code=500, detail="Configuração da API OpenAI ausente no servidor.")

    prompt = f"""
    Analise o seguinte feedback de cliente:
    ---
    {text}
    ---

    Sua tarefa é retornar SOMENTE um objeto JSON válido com a seguinte estrutura e conteúdo:
    {{
      "sentiment": "...", // Classifique o sentimento como Positivo, Negativo ou Neutro.
      "summary": "...",   // Gere um resumo conciso de uma frase do ponto principal.
      "topics": ["...", "...", "..."] // Liste os 3 tópicos ou palavras-chave mais importantes mencionados. Se houver menos de 3, liste os que encontrar.
    }}
    Não inclua nenhuma explicação ou texto adicional fora do objeto JSON.
    """

    try:
        logger.info(f"Chamando API OpenAI para analisar feedback: '{text[:50]}...'")
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo", # Modelo recomendado para custo/benefício
            messages=[
                {"role": "system", "content": "Você é um assistente útil que analisa feedback de clientes e retorna a análise em formato JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2, # Baixa temperatura para respostas mais consistentes/determinísticas
            response_format={"type": "json_object"} # Solicita explicitamente JSON
        )

        analysis_content = response.choices[0].message.content
        logger.debug(f"Resposta JSON recebida da OpenAI: {analysis_content}")

        if not analysis_content:
            raise HTTPException(status_code=500, detail="Resposta vazia da API de IA.")

        # Parsear o conteúdo JSON
        analysis_data = json.loads(analysis_content)

        # Validar minimamente a estrutura esperada (Pydantic fará validação mais completa na resposta da rota)
        if not all(key in analysis_data for key in ["sentiment", "summary", "topics"]):
             raise ValueError("Estrutura JSON da resposta da IA está incompleta.")
        if not isinstance(analysis_data.get("topics"), list):
             raise ValueError("Campo 'topics' na resposta da IA não é uma lista.")


        # Retorna os dados parseados (a rota os transformará em FeedbackAnalysisResponse)
        # Usamos .get com fallback para evitar KeyErrors se a IA falhar em incluir um campo
        return FeedbackAnalysisResponse(
             sentiment=analysis_data.get("sentiment", "Erro na Análise"),
             summary=analysis_data.get("summary", "Erro na Análise"),
             topics=analysis_data.get("topics", ["Erro na Análise"])
         )


    except OpenAIError as e:
        logger.error(f"Erro na API OpenAI: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail=f"Erro ao comunicar com o serviço de IA: {e}")
    except json.JSONDecodeError as e:
         logger.error(f"Erro ao parsear JSON da resposta da IA: {analysis_content}", exc_info=True)
         raise HTTPException(status_code=500, detail="Formato inválido na resposta do serviço de IA.")
    except ValueError as e:
         logger.error(f"Erro de validação nos dados da IA: {e} - Dados: {analysis_content}", exc_info=True)
         raise HTTPException(status_code=500, detail=f"Dados inválidos recebidos do serviço de IA: {e}")
    except Exception as e:
        logger.error(f"Erro inesperado na análise de feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno no servidor ao analisar feedback.") 