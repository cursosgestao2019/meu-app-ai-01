import { createClient } from "@/lib/supabase/server" // Cliente server-side
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { redirect } from "next/navigation" // Para redirecionamento server-side
import Link from "next/link"
import { ModeToggle } from "@/components/ui/mode-toggle" // Botão de tema
import { MessageSquareText } from "lucide-react"; // Importar ícone

// Página Server Component
export default async function DashboardPage() {
  const supabase = await createClient() // Usa await!
  // Obtém a sessão do usuário do lado do servidor
  const { data: { session } } = await supabase.auth.getSession()

  // Se, por algum motivo, não houver sessão (ex: cookie expirado), redireciona para login
  // O middleware geralmente pega isso antes, mas é uma boa prática verificar novamente.
  if (!session) {
    console.log("DashboardPage: Sem sessão encontrada, redirecionando para /login")
    redirect("/login")
  }

  // Obtém os dados do usuário da sessão
  const user = session.user
  console.log(`DashboardPage: Sessão encontrada para usuário ${user.email || user.id}`)

  return (
    // Container principal do dashboard
    <div className="flex min-h-screen w-full flex-col bg-muted/40">
      {/* Cabeçalho fixo (exemplo) */}
      <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6 py-4">
         <div className="flex-1">
             <h1 className="text-2xl font-semibold">Dashboard</h1>
         </div>
         <div className="flex items-center gap-3">
             <span className="text-sm text-muted-foreground hidden sm:inline">
               {user.email} {/* Mostra o email do usuário */}
             </span>
             <ModeToggle /> {/* Botão para trocar tema */}
             {/* Formulário POST para Logout */}
             <form action="/auth/signout" method="post">
               <Button variant="outline" type="submit" size="sm">Sair</Button>
             </form>
         </div>
      </header>

      {/* Conteúdo principal do Dashboard */}
      <main className="flex-1 p-4 sm:px-6 sm:py-0">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 py-6">
            {/* Card de Boas-vindas */}
            <Card>
              <CardHeader>
                <CardTitle>Bem-vindo!</CardTitle>
                <CardDescription>
                  Sessão ativa para {user.email}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Seu ID de Usuário:</p>
                <p className="text-xs font-mono break-all">{user.id}</p>
                {user.last_sign_in_at && (
                    <p className="text-sm text-muted-foreground mt-2">Último login: {new Date(user.last_sign_in_at).toLocaleString()}</p>
                )}
              </CardContent>
            </Card>

            {/* Card para Gerenciar Itens (Placeholder) */}
            <Link href="/dashboard/items">
              <Card className="hover:shadow-md transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Gerenciar Itens</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-xs text-muted-foreground">
                    Crie, visualize, edite e exclua seus itens.
                  </div>
                </CardContent>
              </Card>
            </Link>

            {/* Card para Analisador de Feedback (NOVO) */}
            <Link href="/dashboard/feedback-analyzer">
              <Card className="hover:shadow-md transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    Analisador de Feedback
                  </CardTitle>
                  <MessageSquareText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-xs text-muted-foreground">
                    Analise sentimento e tópicos de textos.
                  </div>
                </CardContent>
              </Card>
            </Link>

            {/* Card para Editar Perfil (Placeholder) */}
            <Card>
              <CardHeader>
                <CardTitle>Perfil</CardTitle>
                <CardDescription>Suas informações de perfil</CardDescription>
              </CardHeader>
              <CardContent>
                <p>Visualize ou atualize seus dados de perfil (nome, bio, etc.).</p>
              </CardContent>
              <CardFooter>
                <Button variant="outline" className="w-full" disabled>
                  Editar Perfil
                </Button>
              </CardFooter>
            </Card>

             {/* Card para Funcionalidades de IA (Placeholder) */}
            <Card className="md:col-span-2 lg:col-span-1">
              <CardHeader>
                <CardTitle>Recursos de IA</CardTitle>
                <CardDescription>Explore as funcionalidades inteligentes</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                 {/* Botões temporariamente desabilitados pois as rotas não existem */}
                 <Button variant="secondary" className="w-full" disabled>
                    Pesquisa Inteligente (RAG)
                 </Button>
                 <Button variant="secondary" className="w-full" disabled>
                    Executar Tarefa (CrewAI)
                 </Button>
              </CardContent>
            </Card>

          </div>
      </main>
    </div>
  )
} 