# backend/tests/test_api_endpoints.py
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

# Importar dependências necessárias para override
from app.dependencies import get_authenticated_user
from .test_feedback_analyzer import override_get_authenticated_user

# --- Testes para Endpoints da API ---

# Usar test_client e test_app de conftest.py
@pytest.mark.asyncio
async def test_read_root_success(test_client: AsyncClient, test_app: FastAPI):
    test_app.dependency_overrides = {} # Garante sem overrides na app correta
    response = await test_client.get("/")
    assert response.status_code == 200
    expected_message = "API de IA está operacional!"
    assert response.json() == {"message": expected_message}, \
        f"Esperado '{expected_message}', recebido '{response.json().get('message')}'"

# --- Testes para Endpoints Placeholder --- 
# Usar test_client e test_app de conftest.py
@pytest.mark.asyncio
async def test_rag_query_placeholder_success(test_client: AsyncClient, test_app: FastAPI, authenticated_headers: dict):
    test_app.dependency_overrides[get_authenticated_user] = override_get_authenticated_user # Aplica override na app correta
    payload = {"question": "O que é Supabase?"}
    response = await test_client.post("/api/v1/rag-query", json=payload, headers=authenticated_headers)
    test_app.dependency_overrides = {} # Limpa override
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] == "Supabase é um Backend como Serviço (BaaS) incrível!"
    assert "sources" in data
    assert isinstance(data["sources"], list)

# Usar test_client e test_app de conftest.py
@pytest.mark.asyncio
async def test_run_crew_placeholder_success(test_client: AsyncClient, test_app: FastAPI, authenticated_headers: dict):
    test_app.dependency_overrides[get_authenticated_user] = override_get_authenticated_user # Aplica override
    payload = {"topic": "Análise de mercado"}
    response = await test_client.post("/api/v1/run-crew", json=payload, headers=authenticated_headers)
    test_app.dependency_overrides = {} # Limpa override
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "summary" in data["result"]
    # <<< CORREÇÃO: Ajusta a asserção para o valor real retornado pelo placeholder
    expected_summary = "Resultado placeholder para a análise do tópico 'Análise de mercado'."
    assert data["result"]["summary"] == expected_summary, \
        f"Esperado '{expected_summary}', recebido '{data['result'].get('summary')}'"
    assert "logs" in data
    assert isinstance(data["logs"], list)

# Usar test_client e test_app de conftest.py
@pytest.mark.asyncio
async def test_generate_structured_placeholder_success(test_client: AsyncClient, test_app: FastAPI, authenticated_headers: dict):
    test_app.dependency_overrides[get_authenticated_user] = override_get_authenticated_user # Aplica override
    payload = {"prompt": "Extraia dados do usuário", "spec_name": "UserProfileSpec"}
    response = await test_client.post("/api/v1/generate-structured", json=payload, headers=authenticated_headers)
    test_app.dependency_overrides = {} # Limpa override
    assert response.status_code == 200
    data = response.json()
    assert "validated_data" in data
    # <<< CORREÇÃO: Verifica as chaves *realmente* retornadas pelo placeholder atual
    # Ajuste estas asserções se o seu placeholder em guardrails_service.py for diferente
    validated_data = data["validated_data"]
    assert "name" in validated_data
    assert validated_data["name"] == "Placeholder User"
    assert "age" in validated_data
    assert validated_data["age"] == 30
    assert "interests" in validated_data
    assert isinstance(validated_data["interests"], list)
    assert "AI" in validated_data["interests"]
    assert data["error"] is None

# --- Testes de Validação de Input --- 
# Usar test_client e test_app de conftest.py
@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [
    ({"wrong_field": "abc"}),
    ({}),
    ({"question": 123}),
])
async def test_rag_query_invalid_input(test_client: AsyncClient, test_app: FastAPI, payload: dict, authenticated_headers: dict):
    test_app.dependency_overrides[get_authenticated_user] = override_get_authenticated_user # Aplica override
    response = await test_client.post("/api/v1/rag-query", json=payload, headers=authenticated_headers)
    test_app.dependency_overrides = {} # Limpa override
    assert response.status_code == 422