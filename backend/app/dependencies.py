# backend/app/dependencies.py (VERSÃO CORRIGIDA para supabase-py)

import os
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# Imports corrigidos para supabase-py
from supabase import create_client, Client as SupabaseClient
# from supabase import create_client, Client as SupabaseClient, SupabaseAuthError # REMOVIDO SupabaseAuthError
from gotrue.types import User
# from gotrue.errors import AuthApiError # REMOVIDO

logger = logging.getLogger(__name__)

# Esquema para extrair o token Bearer do cabeçalho Authorization
bearer_scheme = HTTPBearer()

# Variáveis de ambiente - VERIFIQUE SE ESTÃO SENDO LIDAS
supabase_url: str = os.environ.get("SUPABASE_URL", "")
supabase_key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "") # Chave de serviço

# <<< ADICIONE ESTE LOG TEMPORÁRIO >>>
logger.info(f"DEBUG: SUPABASE_URL carregada: {'Sim' if supabase_url else 'NÃO'}")
logger.info(f"DEBUG: SUPABASE_SERVICE_ROLE_KEY carregada: {'Sim' if supabase_key else 'NÃO'}")
# <<< FIM DO LOG TEMPORÁRIO >>>

if not supabase_url or not supabase_key:
    logger.error("Variáveis de ambiente SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY não definidas!")
    # Dependendo da sua aplicação, você pode querer lançar um erro aqui para impedir a inicialização

async def get_supabase_client() -> SupabaseClient:
    """Dependência para obter um cliente Supabase."""
    if not supabase_url or not supabase_key:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuração do Supabase ausente no servidor."
        )
    try:
        # create_client é síncrono, mas retorna um cliente que pode fazer chamadas async
        supabase: SupabaseClient = create_client(supabase_url, supabase_key)
        return supabase
    except Exception as e:
        logger.error(f"Falha ao criar cliente Supabase: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Não foi possível conectar ao serviço de backend."
        )

async def get_authenticated_user(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> User:
    """
    Verifica o token JWT usando o cliente Supabase e retorna o objeto User.
    Levanta HTTPException 401 se o token for inválido ou expirado.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        # Tentar obter o usuário. A biblioteca supabase-py pode levantar
        # exceções genéricas ou específicas do gotrue em caso de falha.
        # Nota: A chamada get_user é SÍNCRONA na v2 da lib.
        response = supabase.auth.get_user(token.credentials)
        user = response.user
        if not user:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado ou token inválido.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.debug(f"Usuário autenticado: {user.id} via get_authenticated_user")
        return user
    # Capturar exceção genérica ao obter usuário como falha de autenticação
    except Exception as e:
        # Logar o tipo real da exceção para depuração futura
        logger.warning(f"Erro ao validar token JWT com Supabase (Tipo: {type(e).__name__}): {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido ou expirado.", # Mensagem genérica
            headers={"WWW-Authenticate": "Bearer"},
        ) 