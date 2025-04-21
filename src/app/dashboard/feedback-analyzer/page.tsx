import { AnalyzerUI } from "@/components/feedback-analyzer/analyzer-ui";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

export default function FeedbackAnalyzerPage() {
  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center gap-4 mb-4">
        <Link href="/dashboard">
          <Button variant="outline" size="icon">
            <ArrowLeft className="h-4 w-4" />
            <span className="sr-only">Voltar ao Dashboard</span>
          </Button>
        </Link>
        <h1 className="text-2xl font-bold">Analisador de Feedback</h1>
      </div>
      <p>Cole um texto de feedback abaixo para análise pela IA.</p>
      <AnalyzerUI />
    </div>
  );
} 