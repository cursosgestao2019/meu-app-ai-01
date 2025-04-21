# Copie e cole para criar/atualizar o arquivo backend/app/models/ai_models.py:
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- Modelos para RAG ---
class RagQueryInput(BaseModel):
    question: str = Field(..., description="Pergunta para a base RAG", examples=["Qual o status do projeto X?"])
    session_id: Optional[str] = Field(None, description="ID de sessão opcional para histórico")

class RagResponse(BaseModel):
    answer: str = Field(..., description="Resposta gerada pelo RAG")
    sources: Optional[List[Dict[str, Any]]] = Field([], description="Lista de fontes usadas")

# --- Modelos para CrewAI ---
class CrewInput(BaseModel):
    topic: str = Field(..., description="Tópico ou objetivo para a Crew executar")
    parameters: Optional[Dict[str, Any]] = Field({}, description="Parâmetros adicionais para a Crew")

class CrewResponse(BaseModel):
    result: Any = Field(..., description="Resultado final da execução da Crew")
    logs: Optional[List[str]] = Field([], description="Logs ou métricas da execução (opcional)")

# --- Modelos para Guardrails ---
class GuardrailsInput(BaseModel):
    prompt: str = Field(..., description="Prompt para gerar a saída estruturada")
    spec_name: str = Field(..., description="Nome da especificação Guardrails (.rail ou classe Pydantic)")
    num_reasks: int = Field(default=1, ge=0, description="Número de tentativas de correção")

class GuardrailsResponse(BaseModel):
     validated_data: Optional[Dict | List | str] = Field(None, description="Dados validados e estruturados")
     error: Optional[str] = Field(None, description="Mensagem de erro se a validação falhar")

# Novos modelos para o Analisador de Feedback
class FeedbackAnalysisRequest(BaseModel):
    text: str = Field(
        ...,
        max_length=500, # Limite de caracteres (opcional, mas bom)
        description="Texto do feedback a ser analisado."
    )

class FeedbackAnalysisResponse(BaseModel):
    sentiment: str = Field(..., description="Sentimento detectado (Positivo, Negativo ou Neutro)")
    summary: str = Field(..., description="Resumo de uma frase do feedback")
    topics: List[str] = Field(..., description="Lista dos 3 principais tópicos mencionados")