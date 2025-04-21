'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Loader2, Terminal } from 'lucide-react';
import { createClient } from '@/lib/supabase/client'; // Importa o cliente Supabase client-side
import { toast } from "sonner";

// Interface para o resultado da análise (espelha FeedbackAnalysisResponse do backend)
interface AnalysisResult {
  sentiment: string;
  summary: string;
  topics: string[];
}

export function AnalyzerUI() {
  const [inputText, setInputText] = useState<string>('');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Função para obter o token de autenticação atual
  const getAuthToken = async (): Promise<string | null> => {
     const supabase = createClient(); // Cria instância do cliente Supabase client-side
     const { data: { session }, error: sessionError } = await supabase.auth.getSession();

     if (sessionError) {
       console.error("Erro ao obter sessão Supabase:", sessionError);
       setError("Não foi possível obter a sessão de autenticação.");
       return null;
     }
     if (!session) {
       setError("Sessão não encontrada. Faça login novamente.");
       // TODO: Considerar redirecionar para /login programaticamente
       return null;
     }
     return session.access_token; // Retorna o token de acesso da sessão atual
  };

  // Função chamada ao clicar no botão "Analisar Feedback"
  const handleSubmit = async () => {
    setError(null); // Limpa erros anteriores
    setAnalysisResult(null); // Limpa resultados anteriores
    setIsLoading(true); // Ativa estado de carregamento

    const token = await getAuthToken(); // Obtém o token JWT atual

    // Validações iniciais
    if (!inputText.trim()) {
        setError("Por favor, insira um texto para analisar.");
        setIsLoading(false);
        return;
    }
     if (!token) {
         // Mensagem de erro já definida por getAuthToken se token for nulo
         setIsLoading(false);
         return;
     }

    const apiUrl = process.env.NEXT_PUBLIC_PYTHON_API_URL; // Obtém URL do backend do .env.local
    if (!apiUrl) {
      setError("URL da API do Backend não configurada no frontend.");
      setIsLoading(false);
      return;
    }

    // Tenta chamar a API do backend
    try {
      const response = await fetch(`${apiUrl}/api/v1/feedback/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` // Envia o token no cabeçalho
        },
        body: JSON.stringify({ text: inputText }), // Envia o texto no corpo
      });

      // Trata resposta não-OK da API
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `Erro HTTP ${response.status}` }));
        throw new Error(errorData.detail || `Erro HTTP ${response.status}`);
      }

      // Se a resposta for OK, parseia o JSON e atualiza o estado
      const result: AnalysisResult = await response.json();
      setAnalysisResult(result);
      toast("Análise Concluída!", {
        description: "O feedback foi analisado com sucesso.",
      });

    } catch (err: any) { // Captura erros (rede ou lançados manualmente)
      setError(err.message || "Ocorreu um erro ao conectar com a API.");
       toast.error("Erro na Análise", {
         description: err.message || "Não foi possível completar a análise.",
       });
    } finally {
      setIsLoading(false); // Desativa estado de carregamento, independentemente do resultado
    }
  };

  // Renderização do componente JSX
  return (
    <div className="space-y-6">
      {/* Área de texto para input */}
      <Textarea
        placeholder="Cole o feedback do cliente aqui (máx. 500 caracteres)..."
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        rows={6}
        maxLength={500}
        disabled={isLoading} // Desabilita durante carregamento
      />
      {/* Botão de submissão */}
      <Button onClick={handleSubmit} disabled={isLoading || !inputText.trim()}>
        {isLoading ? ( // Mostra spinner se estiver carregando
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Analisando...
          </>
        ) : (
          'Analisar Feedback' // Texto padrão
        )}
      </Button>

      {/* Exibição de erro (se houver) */}
      {error && (
        <Alert variant="destructive">
          <Terminal className="h-4 w-4" />
          <AlertTitle>Erro</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Exibição do resultado (se houver e não estiver carregando) */}
      {analysisResult && !isLoading && (
        <Card>
          <CardHeader>
            <CardTitle>Resultado da Análise</CardTitle>
            <CardDescription>Análise gerada pela IA.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <p><strong>Sentimento:</strong> {analysisResult.sentiment}</p>
            <p><strong>Resumo:</strong> {analysisResult.summary}</p>
            <div>
              <strong>Tópicos Principais:</strong>
              <ul className="list-disc pl-5">
                {analysisResult.topics.map((topic, index) => (
                  <li key={index}>{topic}</li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 