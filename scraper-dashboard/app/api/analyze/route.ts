import { NextResponse } from 'next/server';

// Interface do payload de análise
interface AnalyzeRequest {
  resumeText: string;
  jobDescription: string;
}

export async function POST(request: Request) {
  try {
    const body: AnalyzeRequest = await request.json();
    const { resumeText, jobDescription } = body;

    if (!resumeText || !jobDescription) {
      return NextResponse.json(
        { error: 'Currículo e descrição da vaga são obrigatórios.' },
        { status: 400 }
      );
    }

    // Chamada à API de IA (Gemini / OpenAI) solicitando Structured Outputs
    const prompt = `
      Você é um analisador especialista de currículos para TI.
      Compare o currículo abaixo com a vaga descrita e retorne ESTRITAMENTE um objeto JSON válido sem formatação Markdown com o seguinte formato:
      {
        "match_score": number (0-100),
        "matching_skills": string[],
        "missing_skills": string[],
        "summary": string,
        "actionable_recommendations": string[]
      }

      --- VAGA ---
      ${jobDescription}

      --- CURRÍCULO ---
      ${resumeText}
    `;

    // Exemplo usando chamada REST padrão para a API da Gemini ou OpenAI
    const aiResponse = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${process.env.GEMINI_API_KEY}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: {
            responseMimeType: 'application/json',
          },
        }),
      }
    );

    const data = await aiResponse.json();
    const rawResult = data.candidates?.[0]?.content?.parts?.[0]?.text;
    const structuredAnalysis = JSON.parse(rawResult);

    return NextResponse.json({ success: true, data: structuredAnalysis });
  } catch (error) {
    console.error('Erro ao analisar currículo:', error);
    return NextResponse.json(
      { error: 'Falha ao processar análise de currículo.' },
      { status: 500 }
    );
  }
}