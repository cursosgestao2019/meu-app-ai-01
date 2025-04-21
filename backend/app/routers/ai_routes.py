# Copie e cole para criar/atualizar o arquivo backend/app/routers/ai_routes.py:
from fastapi import APIRouter, HTTPException, Body, status, Depends
import logging
from typing import Dict, Any
# Importe os models Pydantic
from ..models.ai_models import (
    RagQueryInput,
    RagResponse,
    CrewInput,
    CrewResponse,
    GuardrailsInput,
    GuardrailsResponse,
    FeedbackAnalysisRequest,
    FeedbackAnalysisResponse
)
# Importe os services (a lógica real estará lá)
# Estes imports podem dar erro no editor AGORA, mas devem funcionar quando a API rodar
from ..services import rag_service, crew_service, guardrails_service, feedback_analyzer_service
# Importa a dependência de autenticação
from ..dependencies import get_authenticated_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["AI Endpoints"])

@router.post("/rag-query", response_model=RagResponse, summary="Consulta RAG", dependencies=[Depends(get_authenticated_user)])
async def handle_rag_query(query: RagQueryInput = Body(...)):
    """Recebe uma pergunta e retorna uma resposta via RAG."""
    logger.info(f"Recebida consulta RAG: {query.question}")
    try:
        # Chama o serviço RAG (implementação virá na Fase 7)
        # Await necessário pois as funções de serviço serão async
        answer, sources = await rag_service.query_knowledge_base(query.question)
        return RagResponse(answer=answer, sources=sources)
    except rag_service.VectorStoreNotReadyError as e: # Exemplo de erro específico
         logger.warning(f"Erro RAG (Vector Store não pronto): {e}")
         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.error(f"Erro inesperado na consulta RAG: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao processar consulta RAG.")

@router.post("/run-crew", response_model=CrewResponse, summary="Executa uma Crew AI", dependencies=[Depends(get_authenticated_user)])
async def handle_run_crew(crew_input: CrewInput = Body(...)):
    """Inicia uma tarefa complexa usando uma equipe de agentes AI."""
    logger.info(f"Recebido pedido para rodar crew sobre: {crew_input.topic}")
    try:
        # Chama o serviço CrewAI (implementação virá na Fase 7)
        result, logs = await crew_service.run_specific_crew(crew_input.topic, crew_input.parameters)
        return CrewResponse(result=result, logs=logs)
    except ValueError as e: # Exemplo: Tópico não suportado
         logger.warning(f"Erro Crew (Input inválido): {e}")
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro inesperado ao rodar Crew: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao executar a Crew AI.")

@router.post("/generate-structured", response_model=GuardrailsResponse, summary="Gera dados estruturados com validação", dependencies=[Depends(get_authenticated_user)])
async def handle_generate_structured(guard_input: GuardrailsInput = Body(...)):
    """Usa Guardrails para gerar e validar dados a partir de um prompt."""
    logger.info(f"Recebido pedido para gerar dados estruturados com spec: {guard_input.spec_name}")
    try:
        # Chama o serviço Guardrails (implementação virá na Fase 7)
        validated_data = await guardrails_service.generate_and_validate(
            guard_input.prompt,
            guard_input.spec_name,
            guard_input.num_reasks
        )
        # Retorna sucesso com os dados validados
        return GuardrailsResponse(validated_data=validated_data, error=None)
    except guardrails_service.GuardrailsValidationError as e: # Exemplo erro específico
        logger.warning(f"Erro Guardrails (Validação falhou): {e}")
        # Retorna sucesso (status 200), mas com erro na resposta
        return GuardrailsResponse(validated_data=None, error=str(e))
    except FileNotFoundError as e: # Exemplo: Spec não encontrada
         logger.error(f"Erro Guardrails (Spec não encontrada): {e}")
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Erro inesperado na geração com Guardrails: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro na geração estruturada.")

@router.post(
    "/feedback/analyze",
    response_model=FeedbackAnalysisResponse,
    summary="Analisa texto de feedback de cliente",
    dependencies=[Depends(get_authenticated_user)]
)
async def handle_feedback_analysis(
    payload: FeedbackAnalysisRequest = Body(...)
):
    """
    Recebe um texto de feedback, chama o serviço de análise de IA
    e retorna o resultado estruturado.
    """
    logger.info(f"Recebida requisição para analisar feedback: '{payload.text[:50]}...'")
    try:
        # Chama a função do serviço que criamos
        analysis_result = await feedback_analyzer_service.analyze_feedback_text(payload.text)
        return analysis_result
    except HTTPException as http_exc:
         # Re-levanta exceções HTTP que podem vir do serviço (para manter status code e detail)
         raise http_exc
    except Exception as e:
         # Captura qualquer outro erro inesperado
         logger.error(f"Erro não tratado na rota /feedback/analyze: {e}", exc_info=True)
         raise HTTPException(status_code=500, detail="Erro interno do servidor ao processar o feedback.")