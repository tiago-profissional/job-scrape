// app/tracker/page.tsx
"use client";

import { useState } from 'react';

// Etapas visuais fixas para preencher os círculos
const steps = [
  "Iniciando scraper de Startups...",
  "Buscando vagas...",
  "Conectando ao MySQL...",
  "Processando e salvando dados...",
  "Finalizando..."
];

export default function Tracker() {
  const [logs, setLogs] = useState<string[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

  const startAutomation = async () => {
    setIsRunning(true);
    setLogs([]);
    setCurrentStep(0);

    try {
      // Conecta ao endpoint real que roda o scraper
      const response = await fetch('/api/scrape', {
        method: 'GET',
        headers: { Accept: 'text/event-stream' },
      });

      if (!response.body) {
        throw new Error("Stream não suportado");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        // O servidor envia linhas como: data: {"type":"...", "message":"..."}\n\n
        const events = chunk.split('\n\n');

        for (const event of events) {
          if (event.startsWith('data: ')) {
            const jsonStr = event.replace('data: ', '');
            try {
              const data = JSON.parse(jsonStr);
              const msg = data.message;

              // Adiciona log no console
              setLogs(prev => [...prev, msg]);

              // Lógica para avançar os círculos com base nas mensagens reais
              if (msg.includes('Iniciando')) setCurrentStep(0);
              else if (msg.includes('Encontradas')) setCurrentStep(1);
              else if (msg.includes('Conectado')) setCurrentStep(2);
              else if (msg.includes('Processando') || msg.includes('salvo')) setCurrentStep(3);
              else if (msg.includes('Finalizado')) setCurrentStep(4);
              
            } catch (e) {
              console.error("Erro ao parsear log:", e);
            }
          }
        }
      }
    } catch (error) {
      setLogs(prev => [...prev, `💥 Erro de conexão: ${error}`]);
    } finally {
      setIsRunning(false);
    }
  };

  // Lógica do "scroll" da janela do navegador baseada na etapa atual
  const scrollY = currentStep < 2 ? 0 : (currentStep - 2) * 80;

  return (
    <div className="min-h-screen bg-[#FFF5EA] p-8">
      <div className="max-w-7xl mx-auto">
        
        {/* Cabeçalho */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-extrabold text-[#EA7805]">Monitor de Automação</h1>
          <button 
            onClick={startAutomation} 
            disabled={isRunning}
            className="bg-[#EA7805] hover:bg-[#7E4220] disabled:opacity-50 text-white font-bold py-2 px-6 rounded-full transition-colors shadow-md"
          >
            {isRunning ? "Robô em execução..." : "Iniciar Robô"}
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* COLUNA 1: Visualização do Site */}
          <div className="bg-white p-6 rounded-xl shadow-lg border border-[#F1B435]">
            <h2 className="text-xl font-bold text-[#191815] mb-4 flex items-center gap-2">
              🖥️ Visualização do Site
            </h2>
            
            <div className="rounded-lg border border-gray-300 overflow-hidden">
              {/* Barra superior */}
              <div className="bg-gray-100 p-2 flex items-center gap-2 border-b">
                <div className="w-3 h-3 rounded-full bg-red-400"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                <div className="w-3 h-3 rounded-full bg-green-400"></div>
                <div className="flex-1 bg-white rounded-md px-3 py-1 text-xs text-gray-500 flex items-center">
                  🔒 https://vagasnordestinas.com
                </div>
              </div>

              {/* Conteúdo */}
              <div className="h-[400px] overflow-hidden bg-[#FFF5EA] p-4 relative">
                <div 
                  className="transition-transform duration-1000 ease-in-out"
                  style={{ transform: `translateY(-${scrollY}px)` }}
                >
                  <div className="text-center mb-6">
                    <h3 className="text-2xl font-bold text-[#EA7805]">Vagas Nordestinas</h3>
                    <p className="text-xs text-[#7E4220]">Encontre seu emprego no sertão</p>
                  </div>

                  {/* Lista de Vagas Falsas (pode ser trocada pelos dados reais depois) */}
                  {[1, 2, 3, 4, 5].map((item, index) => (
                    <div 
                      key={index} 
                      className={`bg-white p-4 rounded-lg shadow-md mb-4 border-l-4 transition-all duration-500 ${
                        currentStep === 3 && index === 0 
                        ? 'border-[#EA7805] scale-105 shadow-lg' 
                        : 'border-gray-200'
                      }`}
                    >
                      <div className="flex justify-between">
                        <h4 className="font-bold text-[#191815]">Vaga de {index === 0 ? 'Analista' : 'Desenvolvedor'} {index + 1}</h4>
                        <span className="text-xs bg-[#F1B435] text-[#191815] px-2 py-1 rounded-full">Remoto</span>
                      </div>
                      <p className="text-sm text-gray-500">Empresa Exemplo {index + 1} • R$ 5.000</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* COLUNA 2: Status e Console */}
          <div className="flex flex-col gap-6">
            
            {/* Passos */}
            <div className="bg-white p-6 rounded-xl shadow-lg border border-[#F1B435]">
              <h2 className="text-xl font-bold text-[#191815] mb-4">🤖 Status do Robô</h2>
              <div className="space-y-4">
                {steps.map((step, index) => {
                  const isCompleted = index < currentStep;
                  const isActive = index === currentStep && isRunning;
                  
                  return (
                    <div key={index} className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold transition-all ${
                        isCompleted ? 'bg-green-500' : 
                        isActive ? 'bg-[#EA7805] animate-pulse' : 
                        'bg-gray-300'
                      }`}>
                        {isCompleted ? '✓' : isActive ? '...' : index + 1}
                      </div>
                      <span className={`font-medium ${isCompleted || isActive ? 'text-[#191815]' : 'text-gray-400'}`}>
                        {step}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Console de Logs em Tempo Real */}
            <div className="bg-[#191815] p-6 rounded-xl shadow-lg flex-1 h-full max-h-[300px] overflow-y-auto">
              <h2 className="text-xl font-bold text-[#FFF5EA] mb-4">🖥️ Console do Sistema</h2>
              <div className="font-mono text-sm space-y-2">
                {logs.map((log, index) => (
                  <p key={index} className="text-[#FFF5EA] break-words">
                    <span className="text-[#F1B435]">[{String(index).padStart(2, '0')}]</span>{' '}
                    <span className="text-[#EA7805]">$</span> {log}
                  </p>
                ))}
                {isRunning && <p className="text-[#F1B435] animate-pulse">▊</p>}
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}