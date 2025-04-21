# backend/tests/test_feedback_analyzer.py
import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

# Importa a app e a dependência para o override
from app.main import app as fastapi_app
from app.dependencies import get_authenticated_user
from gotrue.types import User # Para criar um usuário mock

# Marcador para testes assíncronos
pytestmark = pytest.mark.asyncio

# Dados de teste válidos
valid_payload = {"text": "Adorei o produto, muito fácil de usar!"}

# --- Mock para usuário autenticado ---
# Cria um usuário GoTrue simulado
def create_mock_user() -> User:
    now = datetime.now(timezone.utc)
    return User(
        id="fake-user-id-123",
        app_metadata={"provider": "email"},
        user_metadata={"name": "Test User"},
        aud="authenticated",
        email="test@example.com",
        phone="",
        created_at=now,
        confirmed_at=now,
        email_confirmed_at=now,
        phone_confirmed_at=now,
        last_sign_in_at=now,
        role="authenticated",
        updated_at=now,
        identities=[] # Adiciona identities como lista vazia
    )

# Função que substituirá get_authenticated_user
async def override_get_authenticated_user() -> User:
    print("\nDependency Override: Retornando usuário mockado\n")
    return create_mock_user()
# --- Fim do Mock ---


# Teste de sucesso simulando a resposta do serviço
@patch("app.services.feedback_analyzer_service.analyze_feedback_text")
async def test_analyze_feedback_success(mock_analyze_service, test_client: AsyncClient, authenticated_headers: dict):
    # Configura o mock do serviço
    mock_analyze_service.return_value = MagicMock(
        sentiment="Positivo",
        summary="Cliente adorou o produto pela facilidade de uso.",
        topics=["produto", "facilidade de uso", "elogio"]
    )

    # Aplica o override da dependência de autenticação
    fastapi_app.dependency_overrides[get_authenticated_user] = override_get_authenticated_user

    response = await test_client.post("/api/v1/feedback/analyze", json=valid_payload, headers=authenticated_headers)

    # Limpa o override após o teste
    fastapi_app.dependency_overrides = {}

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["sentiment"] == "Positivo"
    assert "facilidade de uso" in json_response["summary"]
    assert "produto" in json_response["topics"]
    mock_analyze_service.assert_called_once_with(valid_payload["text"])

# Teste de erro (ex: texto muito longo)
async def test_analyze_feedback_too_long(test_client: AsyncClient, authenticated_headers: dict):
    # Aplica o override da dependência de autenticação
    fastapi_app.dependency_overrides[get_authenticated_user] = override_get_authenticated_user

    long_text = "a" * 501
    response = await test_client.post("/api/v1/feedback/analyze", json={"text": long_text}, headers=authenticated_headers)

    # Limpa o override após o teste
    fastapi_app.dependency_overrides = {}

    assert response.status_code == 422

# Teste sem autenticação
async def test_analyze_feedback_unauthenticated(test_client: AsyncClient):
    # Garante que não há overrides
    fastapi_app.dependency_overrides = {}

    response = await test_client.post("/api/v1/feedback/analyze", json=valid_payload)
    # Verifica se retorna 403 Forbidden quando nenhum header é passado
    assert response.status_code == 403 # CORRIGIDO AQUI

# Teste simulando erro interno no serviço
@patch("app.services.feedback_analyzer_service.analyze_feedback_text")
async def test_analyze_feedback_service_error(mock_analyze_service, test_client: AsyncClient, authenticated_headers: dict):
     # Configura o mock do serviço para levantar uma exceção
     mock_analyze_service.side_effect = Exception("Erro simulado no serviço")

     # Aplica o override da dependência de autenticação
     fastapi_app.dependency_overrides[get_authenticated_user] = override_get_authenticated_user

     response = await test_client.post("/api/v1/feedback/analyze", json=valid_payload, headers=authenticated_headers)

     # Limpa o override após o teste
     fastapi_app.dependency_overrides = {}

     assert response.status_code == 500
     assert "Erro interno do servidor" in response.json()["detail"] 