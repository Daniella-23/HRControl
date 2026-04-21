const API_BASE = "http://127.0.0.1:8000/api";
let selectedEmployeeId = null;

// Toast Notification Function
function showToast(message, type = "success") {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerText = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("show");
    }, 100);

    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Page Navigation
function showPage(pageName) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    document.getElementById(`page-${pageName}`).classList.add('active');
    event.target.classList.add('active');

    // Load data based on page
    if (pageName === 'candidates') {
        loadCandidates();
    } else if (pageName === 'employees') {
        loadEmployees();
    } else if (pageName === 'onboarding') {
        loadOnboarding();
    } else if (pageName === 'dashboard') {
        loadDashboard();
    } else if (pageName === 'talent') {
        loadTalent();
    } else if (pageName === 'turnover') {
        loadTurnover();
    } else if (pageName === 'events') {
        loadEvents();
    }
}

// Modal Functions
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// API Helper Functions
async function apiCall(endpoint, method = 'GET', data = null) {
    const fullUrl = `${API_BASE}${endpoint}`;
    console.log(`API Call: ${method} ${fullUrl}`, data ? `Data: ${JSON.stringify(data)}` : '');
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(fullUrl, options);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'API Error');
        }
        const result = await response.json();
        console.log(`API Success: ${method} ${fullUrl}`, result);
        return result;
    } catch (error) {
        console.error('API Error:', error);
        showToast(`Erreur: ${error.message}`, "error");
        throw error;
    }
}

// Candidates Functions
async function loadCandidates() {
    try {
        const candidates = await apiCall('/candidates');
        const listElement = document.getElementById('candidates-list');
        
        if (candidates.length === 0) {
            listElement.innerHTML = '<div class="empty-state">Aucun candidat pour le moment</div>';
            return;
        }

        listElement.innerHTML = candidates.map(candidate => {
            // Normalize and map status from backend to frontend
            let status = (candidate.status || "").toUpperCase();
            
            // Map old statuses to new HR statuses
            const statusMapping = {
                'PENDING': 'EN_ATTENTE',
                'APPROVED': 'ACCEPTE',
                'REJECTED': 'REFUSE'
            };
            
            status = statusMapping[status] || status;
            
            // Fallback to EN_ATTENTE if status is empty or invalid
            if (!status || !['EN_ATTENTE', 'EN_ENTRETIEN', 'ACCEPTE', 'REFUSE'].includes(status)) {
                status = 'EN_ATTENTE';
            }
            
            let workflowButtons = '';
            let statusText = '';
            let statusClass = '';
            
            // Translate status to French
            if (status === 'EN_ATTENTE') {
                statusText = 'EN ATTENTE';
                statusClass = 'status-en-attente';
            } else if (status === 'EN_ENTRETIEN') {
                statusText = 'EN ENTRETIEN';
                statusClass = 'status-en-entretien';
            } else if (status === 'ACCEPTE') {
                statusText = 'ACCEPTÉ';
                statusClass = 'status-accepte';
            } else if (status === 'REFUSE') {
                statusText = 'REFUSÉ';
                statusClass = 'status-refuse';
            }
            
            // Status dropdown
            const statusDropdown = `
                <select onchange="updateCandidateStatus(${candidate.id}, this.value)" class="status-select" value="${status}">
                    <option value="" disabled>Statut</option>
                    <option value="EN_ATTENTE" ${status === 'EN_ATTENTE' ? 'selected' : ''}>EN ATTENTE</option>
                    <option value="EN_ENTRETIEN" ${status === 'EN_ENTRETIEN' ? 'selected' : ''}>EN ENTRETIEN</option>
                    <option value="ACCEPTE" ${status === 'ACCEPTE' ? 'selected' : ''}>ACCEPTÉ</option>
                    <option value="REFUSE" ${status === 'REFUSE' ? 'selected' : ''}>REFUSÉ</option>
                </select>
            `;
            
            // Show "Créer Employé" button only if ACCEPTE
            if (status === 'ACCEPTE') {
                workflowButtons = `
                    <button class="btn btn-primary btn-workflow" onclick="createEmployeeFromCandidate(${candidate.id})">Créer Employé</button>
                    ${statusDropdown}
                `;
            } else {
                workflowButtons = statusDropdown;
            }
            
            return `
            <div class="list-item">
                <div class="list-item-info">
                    <div class="list-item-name">${candidate.name}</div>
                    <div class="list-item-email">${candidate.email}</div>
                </div>
                <div class="list-item-status ${statusClass}">${statusText}</div>
                <div class="list-item-actions">
                    ${workflowButtons}
                    <button class="btn btn-info" onclick="viewCandidateDetails(${candidate.id})">Détails</button>
                    <button class="btn btn-primary" onclick="openEvaluateModal(${candidate.id})">Évaluer</button>
                    <button class="btn btn-danger" onclick="deleteCandidate(${candidate.id})">Supprimer</button>
                </div>
            </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading candidates:', error);
    }
}

async function planInterview(id) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/candidates/${id}/plan-interview`, {
            method: "PUT"
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        showToast('Entretien planifié', 'success');
        loadCandidates();
        loadEvents();
    } catch (error) {
        console.error('Error planning interview:', error);
        showToast('Erreur lors de la planification de l\'entretien', 'error');
    }
}

async function acceptCandidate(id) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/candidates/${id}/approve`, {
            method: "POST"
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        showToast('Candidat accepté', 'success');
        loadCandidates();
        loadEmployees();
        loadEvents();
    } catch (error) {
        console.error('Error accepting candidate:', error);
        showToast('Erreur lors de l\'acceptation du candidat', 'error');
    }
}

async function refuseCandidate(id) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/candidates/${id}/reject`, {
            method: "POST"
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        showToast('Candidat refusé', 'success');
        loadCandidates();
        loadEvents();
    } catch (error) {
        console.error('Error refusing candidate:', error);
        showToast('Erreur lors du refus du candidat', 'error');
    }
}

async function createEmployeeFromCandidate(id) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/candidates/${id}/convert-to-employee`, {
            method: "PUT"
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            if (errorData.detail && errorData.detail.includes("already exists")) {
                showToast('Employé déjà existant', 'success');
                loadCandidates();
                loadEmployees();
                loadEvents();
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        showToast('Employé créé avec succès', 'success');
        loadCandidates();
        loadEmployees();
        loadEvents();
    } catch (error) {
        console.error('Error creating employee from candidate:', error);
        showToast('Erreur lors de la création de l\'employé', 'error');
    }
}

async function updateCandidateStatus(id, newStatus) {
    try {
        // Send status directly to backend without conversion
        const response = await fetch(`http://127.0.0.1:8000/api/candidates/${id}/status`, {
            method: "PUT",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        showToast('Statut mis à jour', 'success');
        loadCandidates();
    } catch (error) {
        console.error('Error updating candidate status:', error);
        showToast('Erreur lors de la mise à jour du statut', 'error');
    }
}

async function createCandidate(event) {
    event.preventDefault();
    const name = document.getElementById('candidate-name').value;
    const email = document.getElementById('candidate-email').value;

    try {
        await apiCall('/candidates', 'POST', { name, email });
        document.getElementById('candidate-form').reset();
        loadCandidates();
        showToast('Candidat créé avec succès', "success");
    } catch (error) {
        console.error('Error creating candidate:', error);
    }
}

async function viewCandidateDetails(candidateId) {
    try {
        const candidates = await apiCall('/candidates');
        const candidate = candidates.find(c => c.id === candidateId);
        
        if (!candidate) {
            showToast('Candidat non trouvé', "error");
            return;
        }

        const content = `
            <div class="detail-row">
                <div class="detail-label">Nom:</div>
                <div class="detail-value">${candidate.name}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Email:</div>
                <div class="detail-value">${candidate.email}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Statut:</div>
                <div class="detail-value">${candidate.statut}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Score:</div>
                <div class="detail-value">${candidate.score}/100</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Commentaire:</div>
                <div class="detail-value">${candidate.commentaire || 'N/A'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Date création:</div>
                <div class="detail-value">${new Date(candidate.created_at).toLocaleDateString('fr-FR')}</div>
            </div>
        `;

        document.getElementById('candidate-details-content').innerHTML = content;
        document.getElementById('candidate-details-modal').style.display = 'block';
    } catch (error) {
        console.error('Error viewing candidate details:', error);
    }
}

function openEvaluateModal(candidateId) {
    document.getElementById('evaluate-candidate-id').value = candidateId;
    document.getElementById('candidate-evaluate-modal').style.display = 'block';
}

async function generateAIEvaluation() {
    try {
        const evaluation = await apiCall('/candidates/generate-evaluation', 'POST');
        document.getElementById('evaluate-score').value = evaluation.score;
        document.getElementById('evaluate-comment').value = evaluation.commentaire;
        showToast('Évaluation IA générée avec succès', "success");
    } catch (error) {
        console.error('Error generating AI evaluation:', error);
        showToast('Erreur lors de la génération IA', "error");
    }
}

async function evaluateCandidate(event) {
    event.preventDefault();
    const candidateId = parseInt(document.getElementById('evaluate-candidate-id').value);
    const score = parseInt(document.getElementById('evaluate-score').value);
    const commentaire = document.getElementById('evaluate-comment').value;

    try {
        await apiCall(`/candidates/${candidateId}/evaluate`, 'PUT', { score, commentaire });
        closeModal('candidate-evaluate-modal');
        document.getElementById('evaluate-form').reset();
        loadCandidates();
        showToast('Évaluation enregistrée avec succès', "success");
    } catch (error) {
        console.error('Error evaluating candidate:', error);
    }
}

async function updateCandidateStatus(candidateId, newStatus) {
    try {
        await apiCall(`/candidates/${candidateId}/status`, 'PUT', { statut: newStatus });
        loadCandidates();
    } catch (error) {
        console.error('Error updating candidate status:', error);
    }
}

async function planInterview(candidateId) {
    try {
        await apiCall(`/candidates/${candidateId}/plan-interview`, 'PUT');
        showToast('Entretien planifié avec succès', "success");
        loadCandidates();
    } catch (error) {
        console.error('Error planning interview:', error);
    }
}

async function acceptCandidate(candidateId) {
    try {
        await apiCall(`/candidates/${candidateId}/accept`, 'PUT');
        showToast('Candidat accepté avec succès', "success");
        loadCandidates();
    } catch (error) {
        console.error('Error accepting candidate:', error);
    }
}

async function rejectCandidate(candidateId) {
    try {
        await apiCall(`/candidates/${candidateId}/reject`, 'PUT');
        showToast('Candidat rejeté', "error");
        loadCandidates();
    } catch (error) {
        console.error('Error rejecting candidate:', error);
    }
}

async function deleteCandidate(candidateId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce candidat?')) {
        return;
    }

    try {
        await apiCall(`/candidates/${candidateId}`, 'DELETE');
        loadCandidates();
        showToast('Candidat supprimé avec succès', "success");
    } catch (error) {
        console.error('Error deleting candidate:', error);
    }
}

async function createEmployeeFromCandidate(candidateId) {
    try {
        await apiCall(`/candidates/${candidateId}/convert-to-employee`, 'PUT');
        showToast('Candidat converti en employé avec succès', "success");
        loadCandidates();
    } catch (error) {
        console.error('Error converting candidate to employee:', error);
    }
}

// Employees Functions
async function loadEmployeeIntoForm(employeeId) {
    try {
        const employees = await apiCall('/employees');
        const employee = employees.find(e => e.id === employeeId);
        
        if (!employee) {
            showToast('Employé non trouvé', "error");
            return;
        }

        selectedEmployeeId = employeeId;

        // Fill form with employee data
        document.getElementById('employee-name').value = employee.name || '';
        document.getElementById('employee-email').value = employee.email || '';
        document.getElementById('employee-date-embauche').value = employee.date_embauche || '';
        document.getElementById('employee-statut').value = employee.statut || 'ACTIF';
        document.getElementById('employee-date-naissance').value = employee.date_naissance || '';
        document.getElementById('employee-statut-familial').value = employee.statut_familial || '';
        document.getElementById('employee-poste').value = employee.poste || '';
        document.getElementById('employee-departement').value = employee.departement || '';
        document.getElementById('employee-niveau').value = employee.niveau || '';
        document.getElementById('employee-salaire').value = employee.salaire_base || '';
        document.getElementById('employee-prime').value = employee.prime || '';
        document.getElementById('employee-transport').value = employee.transport || '';
        document.getElementById('employee-assurance').value = employee.assurance || '';
        document.getElementById('employee-avantages').value = employee.autres_avantages || '';
        document.getElementById('employee-score').value = employee.score || 50;

        // Update button text
        document.querySelector('#employee-form button[type="submit"]').textContent = 'Mettre à jour';

        // Scroll to form
        document.getElementById('employee-form').scrollIntoView({ behavior: 'smooth' });

        showToast('Employé chargé pour modification', "success");
    } catch (error) {
        console.error('Error loading employee into form:', error);
    }
}

async function loadEmployees() {
    try {
        const employees = await apiCall('/employees');
        const listElement = document.getElementById('employees-list');
        
        if (employees.length === 0) {
            listElement.innerHTML = '<div class="empty-state">Aucun employé pour le moment</div>';
            return;
        }

        listElement.innerHTML = employees.map(employee => `
            <div class="list-item">
                <div class="list-item-info">
                    <div class="list-item-name">${employee.name}</div>
                    <div class="list-item-email">${employee.email}</div>
                    <div class="list-item-email">${employee.poste || 'N/A'} - ${employee.departement || 'N/A'}</div>
                </div>
                <div class="list-item-status ${employee.statut}">${employee.statut}</div>
                <div class="list-item-actions">
                    <button class="btn btn-primary" onclick="loadEmployeeIntoForm(${employee.id})">Modifier</button>
                    <button class="btn btn-info" onclick="viewEmployeeDetails(${employee.id})">Détails</button>
                    <button class="btn btn-report" onclick="downloadReport(${employee.id})">Rapport</button>
                    <button class="btn btn-danger" onclick="deleteEmployee(${employee.id})">Supprimer</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading employees:', error);
    }
}

function downloadReport(id) {
    window.open(`http://127.0.0.1:8000/api/employees/${id}/report`, '_blank');
}

async function createEmployee(event) {
    event.preventDefault();
    
    // Get and validate score
    let score = parseInt(document.getElementById('employee-score').value);
    if (isNaN(score) || document.getElementById('employee-score').value === '') {
        score = 50; // Default if empty
    } else if (score > 100) {
        score = 100; // Max 100
    } else if (score < 0) {
        score = 0; // Min 0
    }
    
    const employeeData = {
        name: document.getElementById('employee-name').value,
        email: document.getElementById('employee-email').value,
        date_embauche: document.getElementById('employee-date-embauche').value,
        statut: document.getElementById('employee-statut').value,
        date_naissance: document.getElementById('employee-date-naissance').value || null,
        statut_familial: document.getElementById('employee-statut-familial').value || null,
        poste: document.getElementById('employee-poste').value || null,
        departement: document.getElementById('employee-departement').value || null,
        niveau: document.getElementById('employee-niveau').value || null,
        salaire_base: parseFloat(document.getElementById('employee-salaire').value) || null,
        prime: parseFloat(document.getElementById('employee-prime').value) || null,
        transport: parseFloat(document.getElementById('employee-transport').value) || null,
        assurance: parseFloat(document.getElementById('employee-assurance').value) || null,
        autres_avantages: document.getElementById('employee-avantages').value || null,
        score: score
    };

    try {
        if (selectedEmployeeId) {
            // Update existing employee
            await apiCall(`/employees/${selectedEmployeeId}`, 'PUT', employeeData);
            showToast('Employé mis à jour avec succès', "success");
            loadTurnover(); // Refresh turnover data
        } else {
            // Create new employee
            await apiCall('/employees', 'POST', employeeData);
            showToast('Employé créé avec succès', "success");
        }
        resetEmployeeForm();
        loadEmployees();
    } catch (error) {
        console.error('Error saving employee:', error);
    }
}

function resetEmployeeForm() {
    document.getElementById('employee-form').reset();
    selectedEmployeeId = null;
    document.querySelector('#employee-form button[type="submit"]').textContent = 'Enregistrer Employé';
}

async function viewEmployeeDetails(employeeId) {
    try {
        const employees = await apiCall('/employees');
        const employee = employees.find(e => e.id === employeeId);
        
        if (!employee) {
            showToast('Employé non trouvé', "error");
            return;
        }

        const content = `
            <div class="detail-row">
                <div class="detail-label">Nom:</div>
                <div class="detail-value">${employee.name}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Email:</div>
                <div class="detail-value">${employee.email}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Statut:</div>
                <div class="detail-value">${employee.statut}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Date embauche:</div>
                <div class="detail-value">${employee.date_embauche}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Date naissance:</div>
                <div class="detail-value">${employee.date_naissance || 'N/A'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Statut familial:</div>
                <div class="detail-value">${employee.statut_familial || 'N/A'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Poste:</div>
                <div class="detail-value">${employee.poste || 'N/A'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Département:</div>
                <div class="detail-value">${employee.departement || 'N/A'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Niveau:</div>
                <div class="detail-value">${employee.niveau || 'N/A'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Salaire base:</div>
                <div class="detail-value">${employee.salaire_base ? employee.salaire_base + ' €' : 'N/A'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Prime:</div>
                <div class="detail-value">${employee.prime ? employee.prime + ' €' : 'N/A'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Transport:</div>
                <div class="detail-value">${employee.transport ? employee.transport + ' €' : 'N/A'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Assurance:</div>
                <div class="detail-value">${employee.assurance ? employee.assurance + ' €' : 'N/A'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Autres avantages:</div>
                <div class="detail-value">${employee.autres_avantages || 'N/A'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Date création:</div>
                <div class="detail-value">${new Date(employee.created_at).toLocaleDateString('fr-FR')}</div>
            </div>
        `;

        document.getElementById('employee-details-content').innerHTML = content;
        document.getElementById('employee-details-modal').style.display = 'block';
    } catch (error) {
        console.error('Error viewing employee details:', error);
    }
}

async function deleteEmployee(employeeId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet employé?')) {
        return;
    }

    try {
        await apiCall(`/employees/${employeeId}`, 'DELETE');
        loadEmployees();
        showToast('Employé supprimé avec succès', "success");
    } catch (error) {
        console.error('Error deleting employee:', error);
    }
}

// Onboarding Functions
async function loadOnboarding() {
    try {
        const onboardingList = await apiCall('/onboarding');
        const listElement = document.getElementById('onboarding-list');
        
        if (onboardingList.length === 0) {
            listElement.innerHTML = '<div class="empty-state">Aucun onboarding en cours</div>';
            return;
        }

        listElement.innerHTML = onboardingList.map(onboarding => `
            <div class="list-item">
                <div class="list-item-info">
                    <div class="list-item-name">${onboarding.employee_name}</div>
                    <div class="list-item-email">Progression: ${onboarding.progression.toFixed(0)}%</div>
                </div>
                <div class="onboarding-progress" style="width: 200px;">
                    <div class="onboarding-progress-bar" style="width: ${onboarding.progression}%"></div>
                </div>
                <div class="onboarding-checklist">
                    <div class="checklist-item">
                        <input type="checkbox" ${onboarding.contrat_signe ? 'checked' : ''} 
                               onchange="updateOnboarding(${onboarding.employee_id}, 'contrat_signe', this.checked)">
                        <label>Contrat signé</label>
                    </div>
                    <div class="checklist-item">
                        <input type="checkbox" ${onboarding.email_cree ? 'checked' : ''} 
                               onchange="updateOnboarding(${onboarding.employee_id}, 'email_cree', this.checked)">
                        <label>Email créé</label>
                    </div>
                    <div class="checklist-item">
                        <input type="checkbox" ${onboarding.materiel_attribue ? 'checked' : ''} 
                               onchange="updateOnboarding(${onboarding.employee_id}, 'materiel_attribue', this.checked)">
                        <label>Matériel attribué</label>
                    </div>
                    <div class="checklist-item">
                        <input type="checkbox" ${onboarding.formation_completee ? 'checked' : ''} 
                               onchange="updateOnboarding(${onboarding.employee_id}, 'formation_completee', this.checked)">
                        <label>Formation complétée</label>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading onboarding:', error);
    }
}

async function updateOnboarding(employeeId, field, value) {
    try {
        // Get current onboarding data
        const onboardingList = await apiCall('/onboarding');
        const currentOnboarding = onboardingList.find(o => o.employee_id === employeeId);
        
        if (!currentOnboarding) {
            showToast('Onboarding non trouvé', "error");
            return;
        }

        // Update the specific field
        const updateData = {
            contrat_signe: field === 'contrat_signe' ? value : currentOnboarding.contrat_signe,
            email_cree: field === 'email_cree' ? value : currentOnboarding.email_cree,
            materiel_attribue: field === 'materiel_attribue' ? value : currentOnboarding.materiel_attribue,
            formation_completee: field === 'formation_completee' ? value : currentOnboarding.formation_completee
        };

        await apiCall(`/onboarding/${employeeId}`, 'PUT', updateData);
        loadOnboarding();
    } catch (error) {
        console.error('Error updating onboarding:', error);
    }
}

// Dashboard Functions
async function loadDashboard() {
    try {
        const dashboard = await apiCall('/dashboard');
        
        document.getElementById('stat-candidates').textContent = dashboard.total_candidates;
        document.getElementById('stat-employees').textContent = dashboard.total_employees;
        document.getElementById('stat-approved').textContent = dashboard.candidates_approved;
        document.getElementById('stat-onboarding').textContent = dashboard.avg_onboarding_percentage.toFixed(1) + '%';
        
        // Load additional KPIs
        await loadKPITurnover(dashboard.total_employees);
        await loadKPITalent();
        await loadKPIPerformance();
        await generateHRRecommendations(dashboard);
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

async function loadKPITurnover(totalEmployees) {
    try {
        const turnover = await apiCall('/turnover');
        const riskEmployees = turnover.filter(e => e.risque === 'high' || e.risque === 'medium').length;
        const riskPercentage = totalEmployees > 0 ? (riskEmployees / totalEmployees) * 100 : 0;
        
        document.getElementById('stat-turnover-risk').textContent = riskEmployees;
        
        const turnoverCard = document.getElementById('kpi-turnover');
        const turnoverBadge = document.getElementById('stat-turnover-badge');
        
        turnoverCard.classList.remove('status-green', 'status-orange', 'status-red');
        turnoverBadge.classList.remove('badge-green', 'badge-orange', 'badge-red');
        
        if (riskPercentage > 50) {
            turnoverCard.classList.add('status-red');
            turnoverBadge.textContent = 'Critique';
            turnoverBadge.classList.add('badge-red');
        } else if (riskPercentage >= 20) {
            turnoverCard.classList.add('status-orange');
            turnoverBadge.textContent = 'Moyen';
            turnoverBadge.classList.add('badge-orange');
        } else {
            turnoverCard.classList.add('status-green');
            turnoverBadge.textContent = 'Stable';
            turnoverBadge.classList.add('badge-green');
        }
    } catch (error) {
        console.error('Error loading turnover KPI:', error);
    }
}

async function loadKPITalent() {
    try {
        const talents = await apiCall('/talent');
        
        let highCount = 0;
        let mediumCount = 0;
        let lowCount = 0;
        
        talents.forEach(t => {
            if (t.performance === 'high' || t.potentiel === 'high') highCount++;
            else if (t.performance === 'medium' || t.potentiel === 'medium') mediumCount++;
            else lowCount++;
        });
        
        document.getElementById('talent-high').textContent = highCount;
        document.getElementById('talent-medium').textContent = mediumCount;
        document.getElementById('talent-low').textContent = lowCount;
    } catch (error) {
        console.error('Error loading talent KPI:', error);
    }
}

async function loadKPIPerformance() {
    try {
        const talents = await apiCall('/talent');
        
        let totalScore = 0;
        talents.forEach(t => {
            let score = 0;
            if (t.performance === 'high') score += 3;
            else if (t.performance === 'medium') score += 2;
            else score += 1;
            
            if (t.potentiel === 'high') score += 3;
            else if (t.potentiel === 'medium') score += 2;
            else score += 1;
            
            totalScore += score / 2;
        });
        
        const avgPerformance = talents.length > 0 ? totalScore / talents.length : 0;
        document.getElementById('stat-performance-avg').textContent = avgPerformance.toFixed(1);
        
        const performanceCard = document.getElementById('kpi-performance');
        const performanceBadge = document.getElementById('stat-performance-badge');
        
        performanceCard.classList.remove('status-green', 'status-orange', 'status-red');
        performanceBadge.classList.remove('badge-green', 'badge-orange', 'badge-red');
        
        if (avgPerformance > 2.5) {
            performanceCard.classList.add('status-green');
            performanceBadge.textContent = 'Excellent';
            performanceBadge.classList.add('badge-green');
        } else if (avgPerformance > 1.5) {
            performanceCard.classList.add('status-orange');
            performanceBadge.textContent = 'Moyen';
            performanceBadge.classList.add('badge-orange');
        } else {
            performanceCard.classList.add('status-red');
            performanceBadge.textContent = 'Faible';
            performanceBadge.classList.add('badge-red');
        }
    } catch (error) {
        console.error('Error loading performance KPI:', error);
    }
}

async function generateHRRecommendations(dashboard) {
    try {
        const turnover = await apiCall('/turnover');
        const talents = await apiCall('/talent');
        
        const recommendations = [];
        
        // Check turnover risk
        const highRiskCount = turnover.filter(e => e.risque === 'high').length;
        if (highRiskCount > 0) {
            recommendations.push({
                type: 'warning',
                text: `⚠️ Risque de départ élevé (${highRiskCount} employés), action recommandée`
            });
        }
        
        // Check onboarding
        if (dashboard.avg_onboarding_percentage < 50) {
            recommendations.push({
                type: 'warning',
                text: '⚠️ Onboarding insuffisant, processus à améliorer'
            });
        }
        
        // Check talent distribution
        const lowTalentCount = talents.filter(t => t.performance === 'low' && t.potentiel === 'low').length;
        if (lowTalentCount > talents.length * 0.5) {
            recommendations.push({
                type: 'warning',
                text: '⚠️ Faible niveau global des talents, formation recommandée'
            });
        }
        
        // Check if everything is good
        if (recommendations.length === 0) {
            recommendations.push({
                type: 'success',
                text: '✔️ Situation RH stable, indicateurs au vert'
            });
        }
        
        const recommendationsContainer = document.getElementById('hr-recommendations');
        recommendationsContainer.innerHTML = recommendations.map(r => `
            <div class="recommendation-item ${r.type}">
                ${r.text}
            </div>
        `).join('');
    } catch (error) {
        console.error('Error generating HR recommendations:', error);
    }
}

async function loadTalent() {
    try {
        const talents = await apiCall('/talent');
        
        // Clear all boxes
        const boxes = document.querySelectorAll('.talent-employees');
        boxes.forEach(box => box.innerHTML = '');
        
        // Place each employee in the correct box
        talents.forEach(talent => {
            const boxId = `box-${talent.performance}-${talent.potentiel}`;
            const box = document.getElementById(boxId);
            
            if (box) {
                const employeeDiv = document.createElement('div');
                employeeDiv.className = 'talent-employee';
                employeeDiv.innerHTML = `
                    <div class="talent-employee-name">${talent.nom}</div>
                    <div class="talent-employee-email">${talent.email}</div>
                `;
                box.appendChild(employeeDiv);
            }
        });
    } catch (error) {
        console.error('Error loading talent:', error);
    }
}

async function loadTurnover() {
    try {
        const turnover = await apiCall('/turnover');
        const listElement = document.getElementById('turnover-list');
        
        if (turnover.length === 0) {
            listElement.innerHTML = '<div class="empty-state">Aucun employé pour le moment</div>';
            return;
        }

        listElement.innerHTML = turnover.map(employee => {
            let riskClass = '';
            let riskText = employee.risque.toUpperCase();
            
            if (employee.risque === 'high') {
                riskClass = 'risk-high';
            } else if (employee.risque === 'medium') {
                riskClass = 'risk-medium';
            } else {
                riskClass = 'risk-low';
            }
            
            // Action color coding
            let actionColor = '';
            if (employee.action.includes('urgente')) {
                actionColor = '#dc3545'; // red
            } else if (employee.action.includes('Suivi')) {
                actionColor = '#fd7e14'; // orange
            } else {
                actionColor = '#28a745'; // green
            }
            
            return `
            <div class="list-item">
                <div class="list-item-info">
                    <div class="list-item-name">${employee.nom}</div>
                    <div class="list-item-email">${employee.email}</div>
                </div>
                <div class="list-item-score">Score: ${employee.score}</div>
                <div class="list-item-risk ${riskClass}">${riskText}</div>
                <div class="list-item-action" style="color: ${actionColor}; font-weight: bold; margin-top: 5px;">Action: ${employee.action}</div>
            </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading turnover:', error);
    }
}

// Events Functions
async function loadEvents() {
    try {
        const response = await fetch("http://127.0.0.1:8000/api/events");
        const data = await response.json();

        const container = document.getElementById("events-list");
        container.innerHTML = "";

        if (!data.length) {
            container.innerHTML = "<p>Aucun événement pour le moment</p>";
            return;
        }

        data.forEach(event => {
            const div = document.createElement("div");
            div.className = "card";

            let color = "";
            if (event.type === "employee_created") {
                color = "#28a745"; // green
            } else if (event.type === "employee_updated") {
                color = "#007bff"; // blue
            } else if (event.type === "employee_deleted") {
                color = "#dc3545"; // red
            }

            div.innerHTML = `
                <strong style="color: ${color};">${event.type}</strong><br>
                ${event.message}<br>
                <small style="color: #666;">${event.date}</small>
            `;

            container.appendChild(div);
        });

    } catch (error) {
        console.error("Erreur chargement events:", error);
    }
}

// Chatbot Functions
const panel = document.getElementById("chat-panel");

document.getElementById("chat-toggle").onclick = () => {
    panel.classList.add("open");
};

document.getElementById("close-chat").onclick = () => {
    panel.classList.remove("open");
};

async function sendMessage() {
    const input = document.getElementById("chat-input");
    const msg = input.value;

    if (!msg) return;

    const container = document.getElementById("chat-messages");

    container.innerHTML += `
        <div class="user-msg">
            <b>Toi:</b> ${msg}
        </div>
    `;

    try {
        const res = await fetch("http://127.0.0.1:8000/api/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: msg})
        });

        const data = await res.json();
        container.innerHTML += `
            <div class="bot-msg">
                <b>Bot:</b> ${data.reply}
            </div>
        `;
    } catch (error) {
        container.innerHTML += `
            <div class="bot-msg">
                <b>Bot:</b> Erreur de connexion
            </div>
        `;
        console.error("Erreur chatbot:", error);
    }

    input.value = "";
    container.scrollTop = container.scrollHeight;
}

// Event Listeners
document.getElementById('candidate-form').addEventListener('submit', createCandidate);
document.getElementById('evaluate-form').addEventListener('submit', evaluateCandidate);
document.getElementById('employee-form').addEventListener('submit', createEmployee);

// Initialize - Load candidates by default
document.addEventListener('DOMContentLoaded', function() {
    loadCandidates();
});
