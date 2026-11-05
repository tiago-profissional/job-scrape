import axios from 'axios';
import * as cheerio from 'cheerio';

export interface JobData {
  external_id: string;
  title: string;
  company: string;
  location: string;
  skills: string;
  url: string;
}

export async function scrapeStartupJobs(): Promise<JobData[]> {
  // 🔹 Opção 1: DADOS MOCKADOS (para testar a interface agora)
  // Depois você substitui pela raspagem real.
  
  // Simula um delay para parecer que está buscando dados
  await new Promise(resolve => setTimeout(resolve, 1500));

  return [
    {
      external_id: 'startup_001',
      title: 'Engenheiro de Software Sênior',
      company: 'Stark Bank',
      location: 'São Paulo - SP',
      skills: JSON.stringify(['Node.js', 'React', 'AWS']),
      url: 'https://starkbank.com/careers'
    },
    {
      external_id: 'startup_002',
      title: 'Product Designer',
      company: 'Brex',
      location: 'Remoto',
      skills: JSON.stringify(['Figma', 'UI/UX']),
      url: 'https://brex.com/jobs'
    },
    {
      external_id: 'startup_003',
      title: 'Backend Engineer',
      company: 'Vercel',
      location: 'São Francisco - EUA',
      skills: JSON.stringify(['Rust', 'Go']),
      url: 'https://vercel.com/careers'
    }
  ];

  // 🔹 Opção 2: RASPAGEM REAL (quando você tiver os seletores certos)
  /*
  const url = 'https://www.workatastartup.com/jobs';
  const response = await axios.get(url, {
    headers: { 'User-Agent': 'Mozilla/5.0 ...' }
  });
  const $ = cheerio.load(response.data);
  const jobs: JobData[] = [];
  
  $('div.job-card').each((_, el) => {
    const title = $(el).find('a.job-title').text().trim();
    const company = $(el).find('div.company-name').text().trim();
    // ... preencher os campos e adicionar ao array
  });
  return jobs;
  */
}