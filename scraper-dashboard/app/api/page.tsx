'use client';

import { useState, useEffect, useRef } from 'react';

interface Log {
  type: 'info' | 'success' | 'error';
  message: string;
  timestamp: string;
}

export default function Home() {
  const [logs, setLogs] = useState<Log[]>([]);
  const [isScraping, setIsScraping] = useState(false);
  const logContainerRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  const startScrape = () => {
    if (isScraping) return;
    setLogs([]);
    setIsScraping(true);

    const eventSource = new EventSource('/api/scrape');
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      try {
        const data: Log = JSON.parse(event.data);
        setLogs((prev) => [...prev, data]);
      } catch (e) {
        console.error('Erro ao parsear log:', e);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      setIsScraping(false);
      eventSourceRef.current = null;
    };

    // Evento customizado para fechar quando o servidor finalizar
    eventSource.addEventListener('close', () => {
      eventSource.close();
      setIsScraping(false);
      eventSourceRef.current = null;
    });
  };

  const getColor = (type: string) => {
    switch (type) {
      case 'success': return 'text-green-400';
      case 'error': return 'text-red-400';
      default: return 'text-blue-400';
    }
  };

  return (
    <main className="min-h-screen bg-gray-900 p-8 text-gray-100">
      <div className="max-w-4xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <span className="text-4xl">🕷️</span> Scraper Dashboard
          </h1>
          <button
            onClick={startScrape}
            disabled={isScraping}
            className={`px-6 py-3 rounded-lg font-bold transition-all ${
              isScraping 
                ? 'bg-gray-600 cursor-not-allowed opacity-50' 
                : 'bg-green-600 hover:bg-green-500 shadow-lg shadow-green-900/30 hover:scale-105'
            }`}
          >
            {isScraping ? '⏳ Executando...' : '▶️ Iniciar Scraping'}
          </button>
        </header>

        <div className="bg-black/80 rounded-xl border border-gray-700 p-4 mb-6 shadow-2xl">
          <div className="flex items-center gap-2 mb-3 text-gray-400 text-sm">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="ml-2 font-mono">terminal@scraper:~/logs$</span>
          </div>
          <div 
            ref={logContainerRef}
            className="h-80 overflow-y-auto font-mono text-sm space-y-1 p-2 bg-black/40 rounded-lg custom-scrollbar"
          >
            {logs.length === 0 && (
              <div className="text-gray-600 italic">
                Aguardando comando... Clique em "Iniciar Scraping" para começar.
              </div>
            )}
            {logs.map((log, index) => (
              <div key={index} className={`${getColor(log.type)} break-words`}>
                <span className="text-gray-500">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                {' '}{log.message}
              </div>
            ))}
            {isScraping && logs.length === 0 && (
              <div className="text-yellow-400 animate-pulse">⏳ Conectando ao servidor...</div>
            )}
          </div>
        </div>

        <div className="text-center text-gray-500 text-sm border-t border-gray-800 pt-4">
          🚀 Feito com Next.js 14, TypeScript e Cheerio | Dados em tempo real via SSE
        </div>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #4a5568;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #718096;
        }
      `}</style>
    </main>
  );
}