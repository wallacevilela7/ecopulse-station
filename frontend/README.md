# EcoPulse Urbano - Frontend Web Dashboard

Dashboard público e responsivo de monitoramento climático e socioambiental urbano.

## Tecnologias Empregadas
- **HTML5 Semântico & Vanilla CSS Moderno**: Sistema de design tokens, glassmorphism, suporte a Dark/Light mode e micro-animações.
- **JavaScript ES6+**: Arquitetura modular, consumo assíncrono via `fetch()` e atualização em tempo real por polling inteligente.
- **Chart.js**: Renderização de séries temporais de 24 horas (Temperatura, Sensação Térmica, Pressão e Chuva).
- **Leaflet.js**: Georreferenciamento da estação, representação do círculo analítico de abrangência ($r\text{ km}$) e cálculo da distância euclidiana via GPS do navegador.

## Como Executar Localmente
Basta abrir o arquivo `index.html` em qualquer navegador web ou servi-lo através de um servidor HTTP estático:
```bash
python3 -m http.server 3000
```
Acesse: [http://localhost:3000](http://localhost:3000)
Certifique-se de que o backend FastAPI esteja em execução na porta `8000`.
