# Copie e cole para criar/atualizar o arquivo backend/app/main.py:
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager
import importlib # Para importar routers dinamicamente

# Adiciona o diretório 'backend' ao sys.path para permitir imports relativos como 'from app...'
# quando uvicorn é executado da raiz do projeto (ex: uvicorn backend.app.main:app)
# OU quando executado de dentro de backend/ (ex: uvicorn app.main:app)
# Ajuste: Usar o diretório pai do arquivo atual (__file__) para mais robustez
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir) # Isso deve ser /path/to/atlas/backend
if backend_dir not in sys.path:
     sys.path.insert(0, backend_dir)
     print(f"Adicionado {backend_dir} ao sys.path")

# Carrega variáveis do .env localizado DENTRO da pasta backend
dotenv_path = os.path.join(backend_dir, '.env') # Caminho correto para backend/.env
load_dotenv(dotenv_path=dotenv_path)
print(f"Tentando carregar .env de: {dotenv_path}, Existe: {os.path.exists(dotenv_path)}")

# Configura logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
logger = logging.getLogger(__name__) # Logger para este módulo

# --- Importação de Routers ---
# Tenta importar os routers definidos. Se falhar, a API ainda funciona, mas sem esses endpoints.
router_modules = []
try:
    # Usa import relativo se main.py está dentro de app/
    from .routers import ai_routes
    router_modules.append(ai_routes)
    logger.info("Router 'ai_routes' importado com sucesso de app.routers.")
except ImportError as e:
    logger.warning(f"Não foi possível importar routers de app.routers: {e}. Verifique a estrutura e __init__.py.")
except Exception as e:
    logger.error(f"Erro inesperado ao importar routers: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código de inicialização (ex: carregar modelos, conectar DBs)
    logger.info("API Iniciando...")
    # TODO Fase 7: Adicionar inicialização de serviços (LLMs, Vector DBs) aqui
    # Ex: await rag_service.initialize_vector_store(), crew_service.initialize_llm()
    openai_key_present = os.getenv("OPENAI_API_KEY") is not None and len(os.getenv("OPENAI_API_KEY", "")) > 5
    supabase_conn_present = os.getenv("SUPABASE_DB_CONNECTION_STRING") is not None and "postgres:" in os.getenv("SUPABASE_DB_CONNECTION_STRING", "")
    logger.info(f"Verificação de chaves: OpenAI Key Presente? {openai_key_present}, Supabase Conn String Presente? {supabase_conn_present}")
    if not openai_key_present:
        logger.warning("Chave OPENAI_API_KEY não encontrada ou muito curta no .env!")
    if not supabase_conn_present:
         logger.warning("String de conexão SUPABASE_DB_CONNECTION_STRING não encontrada ou inválida no .env!")
    yield
    # Código de finalização (ex: fechar conexões)
    logger.info("API Finalizando...")

# Cria a instância da aplicação FastAPI
app = FastAPI(
    title="Backend API de IA",
    description="API para servir funcionalidades de RAG, CrewAI e Guardrails.",
    version="0.1.1", # Versão atualizada
    lifespan=lifespan # Associa o ciclo de vida
)

# --- Configuração de CORS ---
# Lista de origens permitidas. Essencial para o frontend poder chamar a API.
# Tenta obter a URL do site principal do .env do frontend (se existir)
# Para isso, precisamos carregar o .env da raiz também (ou ter a var no .env do backend)
# Ajuste: Usar o diretório pai de backend_dir para encontrar a raiz
root_dir = os.path.dirname(backend_dir) # Isso deve ser /path/to/atlas
root_dotenv_path = os.path.join(root_dir, '.env.local') # Assume .env.local na raiz
load_dotenv(dotenv_path=root_dotenv_path, override=False) # Não sobrescreve vars já carregadas
frontend_url = os.getenv("NEXT_PUBLIC_SITE_URL", "http://localhost:3000") # Default para localhost:3000

origins = [
    frontend_url, # URL principal do frontend (lida do .env.local da raiz)
     "http://localhost:8000", # Permitir acesso da própria API (para testes/docs)
     # Adicione outras URLs de desenvolvimento/produção aqui se necessário
     # Ex: URL do Codespaces, Vercel Preview, etc.
]
# Filtra origens nulas ou vazias e remove duplicatas
allowed_origins = list(set(filter(None, origins)))

# Se não houver origens específicas definidas, permita tudo (NÃO recomendado para produção)
if not allowed_origins:
    logger.warning("Nenhuma origem CORS específica definida ou detectada. Permitindo todas as origens ('*'). Configure origins para produção.")
    allowed_origins = ["*"]

logger.info(f"CORS Allowed Origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins, # Passa a lista de origens permitidas
    allow_credentials=True, # Permite envio de cookies (útil para sessões futuras)
    allow_methods=["*"],    # Permite todos os métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],    # Permite todos os headers HTTP
)

# --- Inclusão de Routers ---
# Inclui os endpoints definidos nos módulos de router importados
# api_prefix = "/api/v1" # Não precisamos mais definir aqui
for router_module in router_modules:
     if hasattr(router_module, 'router'):
         # Remover o argumento prefix daqui, pois o router já tem /api/v1
         app.include_router(router_module.router, tags=["AI Services"]) # Removido prefix=api_prefix
         logger.info(f"Router de {router_module.__name__} incluído (prefixo definido no próprio router).") # Mensagem ajustada
     else:
         logger.warning(f"Módulo {router_module.__name__} não possui um atributo 'router'.")

# --- Endpoint Raiz (Verificação) ---
@app.get("/")
async def read_root():
    """ Endpoint raiz para verificar rapidamente se a API está ativa. """
    logger.info("Endpoint raiz ('/') acessado.")
    return {"message": "API de IA está operacional!"}

# --- Execução com Uvicorn (para desenvolvimento local/Codespaces) ---
# Esta parte só executa se o script for rodado diretamente (python backend/app/main.py)
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000)) # Usa a porta 8000 por padrão
    host = os.getenv("HOST", "0.0.0.0") # Ouve em todas as interfaces
    logger.info(f"Iniciando servidor Uvicorn em {host}:{port} (Modo de execução direta)")
    # Use reload=True apenas para desenvolvimento
    # O Uvicorn espera o caminho no formato 'modulo:objeto'
    # Ajuste: Usar 'app.main:app' as uvicorn espera o caminho a partir da pasta onde é executado (backend/)
    uvicorn.run("app.main:app", host=host, port=port, reload=True)