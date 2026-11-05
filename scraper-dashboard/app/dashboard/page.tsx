// app/dashboard/page.tsx

// Simulação de dados (substitua isso pelos dados do seu banco de dados depois)
const scrapes = [
  { id: 1, titulo: "Livro: O Sertão e a Chuva", fonte: "Site X", data: "05/09/2026 14:32", status: "Sucesso" },
  { id: 2, titulo: "Artigo: Culinária Nordestina", fonte: "Blog Y", data: "05/09/2026 14:15", status: "Sucesso" },
  { id: 3, titulo: "Dados: Preço do Milho", fonte: "Portal Agro", data: "05/09/2026 13:50", status: "Erro" },
  { id: 4, titulo: "Notícia: Festival de São João", fonte: "Jornal Z", data: "04/09/2026 18:20", status: "Sucesso" },
];

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-[#FFF5EA] p-8">
      {/* Cabeçalho estilo "Vagas Nordestinas" */}
      <div className="max-w-7xl mx-auto mb-8 flex justify-between items-center">
        <h1 className="text-3xl font-extrabold text-[#EA7805]">Minha Dashboard</h1>
        <button className="bg-[#EA7805] hover:bg-[#7E4220] text-white font-bold py-2 px-6 rounded-full transition-colors shadow-md">
          Atualizar Dados
        </button>
      </div>
      
      {/* Cards de Resumo */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-[#F1B435]">
          <h2 className="text-lg font-semibold text-[#191815]">Total de Scrapes</h2>
          <p className="text-3xl font-extrabold text-[#EA7805] mt-2">1.024</p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-[#EA7805]">
          <h2 className="text-lg font-semibold text-[#191815]">Dados Ativos</h2>
          <p className="text-3xl font-extrabold text-[#F1B435] mt-2">87</p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg border-l-4 border-[#7E4220]">
          <h2 className="text-lg font-semibold text-[#191815]">Última Atualização</h2>
          <p className="text-xl font-bold text-[#7E4220] mt-2">Há 5 minutos</p>
        </div>
      </div>

      {/* NOVA SEÇÃO: Histórico Detalhado de Scrapes */}
      <div className="max-w-7xl mx-auto mt-8 bg-white p-6 rounded-xl shadow-lg border border-[#F1B435] mb-8">
        <h2 className="text-xl font-bold text-[#EA7805] mb-4">Detalhes dos Scrapes Capturados</h2>
        
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#7E4220] text-[#FFF5EA]">
                <th className="p-3 rounded-l-lg">ID</th>
                <th className="p-3">Título</th>
                <th className="p-3">Fonte</th>
                <th className="p-3">Data/Hora</th>
                <th className="p-3 rounded-r-lg">Status</th>
              </tr>
            </thead>
            <tbody>
              {scrapes.map((scrape) => (
                <tr key={scrape.id} className="border-b border-[#FFF5EA] hover:bg-[#FFF5EA] transition-colors">
                  <td className="p-3 text-[#191815] font-semibold">#{scrape.id}</td>
                  <td className="p-3 text-[#191815]">{scrape.titulo}</td>
                  <td className="p-3 text-[#7E4220]">{scrape.fonte}</td>
                  <td className="p-3 text-[#7E4220]">{scrape.data}</td>
                  <td className="p-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                      scrape.status === 'Sucesso' 
                        ? 'bg-[#F1B435] text-[#191815]' 
                        : 'bg-[#EA7805] text-white'
                    }`}>
                      {scrape.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Gráfico */}
      <div className="max-w-7xl mx-auto bg-white p-6 rounded-xl shadow-lg border border-[#F1B435]">
        <h2 className="text-lg font-semibold text-[#191815] mb-4">Gráfico de Análise</h2>
        <p className="text-[#7E4220]">Aqui vai o gráfico dos dados raspados.</p>
      </div>
    </div>
  );
}