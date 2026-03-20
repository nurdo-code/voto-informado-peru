// Usar ruta relativa para producción. En Render o cualquier host, esto buscará en el mismo dominio.
const API_URL = '';

// DOM Elements
const partiesView = document.getElementById('parties-view');
const candidatesView = document.getElementById('candidates-view');
const partiesList = document.getElementById('parties-list');
const candidatesContainer = document.getElementById('candidates-container');
const refreshBtn = document.getElementById('refresh-btn');
const backBtn = document.getElementById('back-to-parties');
const partyNameTitle = document.getElementById('party-name-title');

// Modal Elements
const modal = document.getElementById('candidate-modal');
const closeBtn = document.querySelector('.close-btn');
const modalName = document.getElementById('modal-candidate-name');
const modalScore = document.getElementById('modal-candidate-score');
const modalNews = document.getElementById('modal-candidate-news');
const modalReasons = document.getElementById('modal-reasons-list');
const modalArticles = document.getElementById('modal-articles-list');

// Utility: Generate Score Color
function getScoreColorClass(score) {
    if (score >= 80) return 'green';
    if (score >= 50) return 'yellow';
    return 'red';
}

// Utility: Generate News Color
function getNewsColorClass(count) {
    return count === 0 ? 'green' : 'red';
}

// Fetch and Render Ranking
async function loadParties() {
    try {
        const res = await fetch(`${API_URL}/ranking`);
        const parties = await res.json();
        
        partiesList.innerHTML = '';
        if (parties.length === 0) {
            partiesList.innerHTML = '<tr><td colspan="5" class="text-center">No hay datos disponibles. Ejecuta scraper.py y analyzer.py en el backend.</td></tr>';
            return;
        }

        parties.forEach((party, index) => {
            const scoreClass = getScoreColorClass(party.score);
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${index + 1}</td>
                <td>
                  <img src="${party.logo_url || ''}" alt="Logo" style="width: 45px; height: 45px; object-fit: contain; border-radius: 4px;">
                </td>
                <td><strong>${party.name}</strong></td>
                <td><span class="score-badge ${scoreClass}">${party.score}</span></td>
                <td><button class="btn secondary" onclick="viewCandidates(${party.id}, '${party.name}')">Ver Candidatos</button></td>
            `;
            partiesList.appendChild(tr);
        });
    } catch (e) {
        console.error(e);
        partiesList.innerHTML = '<tr><td colspan="5" class="text-center">Error al conectar con el servidor.</td></tr>';
    }
}

// Fetch and Render Candidates grouped by Cargo
async function viewCandidates(partyId, partyName) {
    partiesView.classList.remove('active');
    candidatesView.classList.add('active');
    partyNameTitle.textContent = `Candidatos de ${partyName}`;
    candidatesContainer.innerHTML = '<div class="text-center">Cargando candidatos...</div>';

    try {
        const res = await fetch(`${API_URL}/candidates?party_id=${partyId}`);
        const groupedCandidates = await res.json();
        
        candidatesContainer.innerHTML = '';
        if (Object.keys(groupedCandidates).length === 0) {
            candidatesContainer.innerHTML = '<div class="text-center">No hay candidatos para este partido.</div>';
            return;
        }

        // Orden deseado de cargos
        const ordenCargos = ["PRESIDENTE DE LA REPÚBLICA", "PRIMER VICEPRESIDENTE DE LA REPÚBLICA", "SEGUNDO VICEPRESIDENTE DE LA REPÚBLICA", "SENADOR", "DIPUTADO"];
        
        // Extraemos las llaves devueltas y las separamos
        const allCargos = Object.keys(groupedCandidates);
        const remainingCargos = allCargos.filter(c => !ordenCargos.includes(c));
        const finalOrder = [...ordenCargos.filter(c => allCargos.includes(c)), ...remainingCargos];

        // Render each group natively returned using priority order
        for (const cargo of finalOrder) {
            const cands = groupedCandidates[cargo];
            const section = document.createElement('div');
            section.className = 'cargo-section';
            
            // Render Table
            let rowsHtml = '';
            cands.forEach((cand, index) => {
                const scoreClass = getScoreColorClass(cand.score);
                const newsClass = getNewsColorClass(cand.news_count);
                rowsHtml += `
                    <tr>
                        <td width="50">${index + 1}</td>
                        <td><strong>${cand.name}</strong></td>
                        <td width="150"><span class="news-badge ${newsClass}">${cand.news_count} noticias</span></td>
                        <td width="120"><span class="score-badge ${scoreClass}">${cand.score}</span></td>
                        <td width="120"><button class="btn primary" onclick="viewCandidateDetails(${cand.id})">Detalles</button></td>
                    </tr>
                `;
            });

            section.innerHTML = `
                <h3 class="cargo-title">${cargo}</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th width="50">#</th>
                            <th>Candidato</th>
                            <th width="150">Noticias Relevantes</th>
                            <th width="120">Puntaje</th>
                            <th width="120">Ver Detalle</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rowsHtml}
                    </tbody>
                </table>
            `;
            candidatesContainer.appendChild(section);
        }

    } catch (e) {
        console.error(e);
        candidatesContainer.innerHTML = '<div class="text-center">Error al cargar candidatos.</div>';
    }
}

// Fetch and Render Candidate Details (Modal)
async function viewCandidateDetails(candidateId) {
    try {
        const res = await fetch(`${API_URL}/candidate/${candidateId}/articles`);
        const data = await res.json();
        const cand = data.candidate;
        
        modalName.textContent = cand.name;
        
        // Render Score Header
        const scoreClass = getScoreColorClass(cand.score);
        const newsClass = getNewsColorClass(cand.news_count);
        
        modalScore.textContent = cand.score;
        modalScore.className = `score-badge large ${scoreClass}`;
        
        modalNews.textContent = `${cand.news_count} noticias`;
        modalNews.className = `news-badge large ${newsClass}`;
        
        // Render Reasons
        modalReasons.innerHTML = '';
        if (data.reasons.length === 0) {
            modalReasons.innerHTML = '<li>✓ Ningún registro negativo encontrado.</li>';
        } else {
            data.reasons.forEach(r => {
                const li = document.createElement('li');
                li.textContent = `${r.reason} (${r.deduction} pts)`;
                modalReasons.appendChild(li);
            });
        }
        
        // Render Articles
        modalArticles.innerHTML = '';
        if (data.articles.length === 0) {
            modalArticles.innerHTML = '<p style="color: #6b7280; font-style: italic;">No hay noticias recientes en dominios de confianza.</p>';
        } else {
            data.articles.forEach(art => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <span class="article-source">[${art.source}]</span>
                    <a href="${art.url}" target="_blank" class="article-title">${art.title}</a>
                `;
                modalArticles.appendChild(li);
            });
        }
        
        modal.classList.add('active');
    } catch (e) {
        console.error(e);
        alert('Error al cargar los detalles del candidato.');
    }
}

// Events
refreshBtn.addEventListener('click', loadParties);

backBtn.addEventListener('click', () => {
    candidatesView.classList.remove('active');
    partiesView.classList.add('active');
});

closeBtn.addEventListener('click', () => {
    modal.classList.remove('active');
});

window.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.classList.remove('active');
    }
});

// Initialize
loadParties();
