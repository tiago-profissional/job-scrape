import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const authHeader = request.headers.get('authorization');

  // Valida o segredo compartilhado entre o GitHub Actions e a Vercel
  if (authHeader !== `Bearer ${process.env.SCRAPER_API_SECRET}`) {
    return NextResponse.json({ error: 'Não autorizado' }, { status: 401 });
  }

  try {
    const jobs = await request.json();

    if (!Array.isArray(jobs)) {
      return NextResponse.json({ error: 'Payload inválido' }, { status: 400 });
    }

    // TODO: Salvar/atualizar vagas no banco de dados (ex: Supabase, Prisma, Vercel KV)
    console.log(`[Sync Successful] ${jobs.length} vagas recebidas do scraper Python.`);

    return NextResponse.json({
      success: true,
      received: jobs.length,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Erro na rota de sync:', error);
    return NextResponse.json({ error: 'Erro ao processar dados' }, { status: 500 });
  }
}