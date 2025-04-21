# backend/tests/conftest.py
import pytest
import sys
import os
from typing import AsyncGenerator, Dict, Generator

# Garante que o diretório 'backend' esteja no sys.path para imports como 'app.main'
# Permite rodar pytest da raiz ou de dentro de backend/
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir) # /path/to/project/backend
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
    print(f"Adicionado {backend_dir} ao sys.path em conftest.py")

# Agora importa a app FastAPI e outras necessidades
try:
    from app.main import app as fastapi_app # Renomeado para evitar conflito com pytest
    from fastapi import FastAPI
    import httpx # <<< Import httpx para ASGITransport
    # from gotrue.types import User # Não precisamos do User real aqui, só nos mocks dos testes
except ImportError as e:
    pytest.exit(f"Erro fatal: Falha ao importar FastAPI app em conftest.py: {e}. Verifique PYTHONPATH e a estrutura do projeto.", returncode=1)


# Fixture para fornecer a instância da app FastAPI (escopo de sessão)
@pytest.fixture(scope="session")
def test_app() -> FastAPI:
    """Retorna a instância da aplicação FastAPI para os testes."""
    print("Fixture 'test_app' criada.")
    return fastapi_app

# Fixture para fornecer um cliente de teste assíncrono (escopo de sessão)
# Usa pytest-asyncio (ou pytest-anyio se configurado)
@pytest.fixture(scope="session")
async def test_client(test_app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]: # <<< Usa httpx.AsyncClient
    """Cria e fornece um cliente de teste async para interagir com a API."""
    print("Criando AsyncClient para testes...")
    # Usa ASGITransport para evitar DeprecationWarning
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        print("AsyncClient criado.")
        yield client
    print("AsyncClient fechado.")


# Fixture para fornecer headers de autenticação simulados (escopo de sessão)
@pytest.fixture(scope="session")
def authenticated_headers() -> Dict[str, str]:
    """
    Retorna um dicionário com um cabeçalho de autenticação Bearer simulado.
    O token em si não precisa ser válido aqui, pois a dependência 'get_authenticated_user'
    será mockada nos testes que precisam de autenticação bem-sucedida.
    """
    print("Fixture 'authenticated_headers' criada com token falso.")
    return {"Authorization": "Bearer FAKE-TEST-TOKEN-FROM-CONFTEST"}

# --- Potenciais melhorias futuras ---
# - Mock global da dependência get_authenticated_user para retornar um usuário fake
# - Fixtures para criar dados de teste no banco (se necessário)
# - Configuração do backend AnyIO (se não estiver no pytest.ini)
# @pytest.fixture(scope='session')
# def anyio_backend():
#     return 'asyncio' 