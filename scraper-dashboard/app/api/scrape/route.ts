import { NextRequest } from 'next/server';
import { scrapeStartupJobs } from '@/lib/scraper';
import { getConnection } from '@/lib/db';

export async function GET(req: NextRequest) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      const sendLog = (message: string, type: 'info' | 'success' | 'error' = 'info') => {
        const data = JSON.stringify({ type, message, timestamp: new Date().toISOString() });
        controller.enqueue(encoder.encode(`data: ${data}\n\n`));
      };

      try {
        sendLog('🚀 Iniciando scraper de Startups...', 'info');
        
        const jobs = await scrapeStartupJobs();
        if (jobs.length === 0) {
          sendLog('⚠️ Nenhuma vaga encontrada.', 'error');
          controller.close();
          return;
        }

        sendLog(`📦 Encontradas ${jobs.length} vagas. Salvando...`, 'success');

        const connection = await getConnection();
        sendLog('🔗 Conectado ao MySQL.', 'success');

        let savedCount = 0;
        for (const job of jobs) {
          sendLog(`📝 Processando: ${job.title} (${job.company})`, 'info');
          try {
            await connection.execute(
              `INSERT INTO jobs (external_id, title, company, location, skills, url)
               VALUES (?, ?, ?, ?, ?, ?)
               ON DUPLICATE KEY UPDATE
               title = VALUES(title), company = VALUES(company),
               location = VALUES(location), skills = VALUES(skills), url = VALUES(url)`,
              [job.external_id, job.title, job.company, job.location, job.skills, job.url]
            );
            savedCount++;
            sendLog(`✅ ${job.title} salvo com sucesso! (${savedCount}/${jobs.length})`, 'success');
          } catch (err: any) {
            sendLog(`❌ Erro ao salvar ${job.title}: ${err.message}`, 'error');
          }
        }

        sendLog(`🎉 Finalizado! ${savedCount} vagas salvas.`, 'success');
        controller.close();
      } catch (error: any) {
        sendLog(`💥 Erro crítico: ${error.message}`, 'error');
        controller.close();
      }
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}