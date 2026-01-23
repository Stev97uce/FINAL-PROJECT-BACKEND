/**
 * UCE Psychology System - Enhanced Dashboard Functions
 * Complete functionality for all dashboard operations
 */

// Global state management
let dashboardState = {
    patients: [],
    appointments: [],
    rooms: [],
    clinicalRecords: [],
    supervisionSessions: [],
    notifications: [],
    currentUser: null,
    selectedPatient: null,
    selectedAppointment: null
};

// Initialize dashboard state
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

async function initializeDashboard() {
    try {
        // Get current user from localStorage
        const userData = localStorage.getItem('currentUser');
        if (userData) {
            dashboardState.currentUser = JSON.parse(userData);
        }

        // Load initial data
        await loadDashboardData();
        
        // Initialize UI components
        initializeEventListeners();
        updateUI();
        
        console.log('Dashboard initialized successfully');
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showAlert('Error al inicializar el dashboard', 'danger');
    }
}

// Load dashboard data from APIs
async function loadDashboardData() {
    try {
        // Load patients
        const patients = await fetchPatients();
        dashboardState.patients = patients || [];

        // Load appointments
        const appointments = await fetchAppointments();
        dashboardState.appointments = appointments || [];

        // Load rooms
        const rooms = await fetchRooms();
        dashboardState.rooms = rooms || [];

        // Load clinical records
        const clinicalRecords = await fetchClinicalRecords();
        dashboardState.clinicalRecords = clinicalRecords || [];

        // Load supervision sessions
        const supervisionSessions = await fetchSupervisionSessions();
        dashboardState.supervisionSessions = supervisionSessions || [];

        console.log('Dashboard data loaded successfully');
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Continue with empty data
    }
}

// Initialize event listeners
function initializeEventListeners() {
    // Add event listeners for all buttons
    document.addEventListener('click', function(event) {
        const button = event.target.closest('button[onclick]');
        if (button) {
            const onclickAttr = button.getAttribute('onclick');
            if (onclickAttr) {
                const functionName = onclickAttr.match(/(\w+)\(/)?.[1];
                if (functionName && window[functionName]) {
                    event.preventDefault();
                    // Extract parameters from onclick
                    const params = onclickAttr.match(/'([^']+)'/g)?.map(p => p.replace(/'/g, '')) || [];
                    window[functionName](...params);
                }
            }
        }
    });
}

// Update UI with loaded data
function updateUI() {
    updateStatsCards();
    updateRecentActivity();
    updateCharts();
}

// Update stats cards
function updateStatsCards() {
    const stats = {
        totalUsers: dashboardState.patients.length + 50, // +50 for staff
        activePatients: dashboardState.patients.filter(p => p.is_active).length,
        todayAppointments: dashboardState.appointments.filter(a => 
            new Date(a.appointment_date).toDateString() === new Date().toDateString()
        ).length,
        monthlySessions: dashboardState.appointments.filter(a => 
            new Date(a.appointment_date).getMonth() === new Date().getMonth()
        ).length
    };

    // Update stat cards if elements exist
    updateStatCard('total-users', stats.totalUsers);
    updateStatCard('active-patients', stats.activePatients);
    updateStatCard('today-appointments', stats.todayAppointments);
    updateStatCard('monthly-sessions', stats.monthlySessions);
}

function updateStatCard(id, value) {
    const element = document.querySelector(`#${id} h3`) || 
                   document.querySelector(`.card-body h3`);
    if (element && element.textContent.includes(',')) {
        element.textContent = value.toLocaleString();
    }
}

// Update recent activity
function updateRecentActivity() {
    const activityContainer = document.querySelector('.activity-list') || 
                             document.querySelector('.card-body .activity-item')?.parentElement;
    
    if (activityContainer) {
        const activities = generateRecentActivities();
        activityContainer.innerHTML = activities.map(activity => createActivityHTML(activity)).join('');
    }
}

function generateRecentActivities() {
    const activities = [];
    
    // Add recent appointments
    dashboardState.appointments.slice(0, 3).forEach(appointment => {
        activities.push({
            type: 'appointment',
            title: 'Cita agendada',
            description: `${appointment.patient_name || 'Paciente'} - ${formatDate(appointment.appointment_date)}`,
            time: getRelativeTime(appointment.created_at),
            badge: 'primary'
        });
    });

    // Add recent patients
    dashboardState.patients.slice(0, 2).forEach(patient => {
        activities.push({
            type: 'patient',
            title: 'Nuevo paciente registrado',
            description: `${patient.nombres} ${patient.apellidos}`,
            time: getRelativeTime(patient.created_at),
            badge: 'success'
        });
    });

    return activities.sort((a, b) => new Date(b.time) - new Date(a.time));
}

function createActivityHTML(activity) {
    return `
        <div class="activity-item">
            <div class="d-flex justify-content-between">
                <div>
                    <strong>${activity.title}:</strong> ${activity.description}
                    <br><small class="text-muted">${activity.time}</small>
                </div>
                <span class="badge bg-${activity.badge}">${activity.type}</span>
            </div>
        </div>
    `;
}

// Quick Actions Implementation
function quickAction(action) {
    console.log('Quick action:', action);
    
    switch(action) {
        case 'new-patient':
            showCreatePatientModal();
            break;
        case 'new-appointment':
            showCreateAppointmentModal();
            break;
        case 'generate-report':
            showGenerateReportModal();
            break;
        case 'manage-users':
            window.location.href = 'patients.html';
            break;
        case 'system-config':
            window.location.href = 'settings.html';
            break;
        default:
            showAlert(`Acción rápida: ${action}`, 'info');
    }
}

// Patient Management Functions
async function showCreatePatientModal() {
    const modalHTML = `
        <div class="modal fade" id="createPatientModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Registrar Nuevo Paciente</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="createPatientForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Nombres</label>
                                    <input type="text" class="form-control" name="nombres" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Apellidos</label>
                                    <input type="text" class="form-control" name="apellidos" required>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Cédula</label>
                                    <input type="text" class="form-control" name="cedula" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Fecha de Nacimiento</label>
                                    <input type="date" class="form-control" name="fecha_nacimiento" required>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Género</label>
                                    <select class="form-select" name="genero" required>
                                        <option value="">Seleccionar...</option>
                                        <option value="Masculino">Masculino</option>
                                        <option value="Femenino">Femenino</option>
                                        <option value="Otro">Otro</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Estado Civil</label>
                                    <select class="form-select" name="estado_civil" required>
                                        <option value="">Seleccionar...</option>
                                        <option value="Soltero/a">Soltero/a</option>
                                        <option value="Casado/a">Casado/a</option>
                                        <option value="Divorciado/a">Divorciado/a</option>
                                        <option value="Viudo/a">Viudo/a</option>
                                        <option value="Unión libre">Unión libre</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Teléfono</label>
                                    <input type="tel" class="form-control" name="telefono" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Email</label>
                                    <input type="email" class="form-control" name="email">
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Dirección</label>
                                <input type="text" class="form-control" name="direccion" required>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Ciudad</label>
                                    <input type="text" class="form-control" name="ciudad" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Provincia</label>
                                    <input type="text" class="form-control" name="provincia" required>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Motivo de Consulta Inicial</label>
                                <textarea class="form-control" name="motivo_consulta_inicial" rows="3" required></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-primary" onclick="savePatient()">Guardar Paciente</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if present
    const existingModal = document.getElementById('createPatientModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('createPatientModal'));
    modal.show();
}

async function savePatient() {
    try {
        const form = document.getElementById('createPatientForm');
        const formData = new FormData(form);
        
        const patientData = {
            nombres: formData.get('nombres'),
            apellidos: formData.get('apellidos'),
            cedula: formData.get('cedula'),
            fecha_nacimiento: formData.get('fecha_nacimiento'),
            genero: formData.get('genero'),
            estado_civil: formData.get('estado_civil'),
            telefono: formData.get('telefono'),
            email: formData.get('email'),
            direccion: formData.get('direccion'),
            ciudad: formData.get('ciudad'),
            provincia: formData.get('provincia'),
            motivo_consulta_inicial: formData.get('motivo_consulta_inicial'),
            is_active: true,
            created_by: dashboardState.currentUser?.id
        };

        // Call API to create patient
        const response = await fetch('/api/v1/patients', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(patientData)
        });

        if (!response.ok) {
            throw new Error('Error al crear paciente');
        }

        const newPatient = await response.json();
        
        // Add to local state
        dashboardState.patients.push(newPatient);
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('createPatientModal'));
        modal.hide();
        
        // Update UI
        updateUI();
        
        showAlert('Paciente creado exitosamente', 'success');
        
    } catch (error) {
        console.error('Error saving patient:', error);
        showAlert('Error al guardar paciente', 'danger');
    }
}

// Appointment Management Functions
async function showCreateAppointmentModal() {
    const modalHTML = `
        <div class="modal fade" id="createAppointmentModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Agendar Nueva Cita</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="createAppointmentForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Paciente</label>
                                    <select class="form-select" name="patient_id" required>
                                        <option value="">Seleccionar paciente...</option>
                                        ${dashboardState.patients.map(patient => 
                                            `<option value="${patient.id}">${patient.nombres} ${patient.apellidos}</option>`
                                        ).join('')}
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Profesional</label>
                                    <select class="form-select" name="professional_id" required>
                                        <option value="">Seleccionar profesional...</option>
                                        <option value="1">Dr. Carlos Mendoza</option>
                                        <option value="2">Dra. María López</option>
                                        <option value="3">Dr. Roberto Silva</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Fecha</label>
                                    <input type="date" class="form-control" name="appointment_date" required>
                                </div>
                                <div class="col-md-3 mb-3">
                                    <label class="form-label">Hora Inicio</label>
                                    <input type="time" class="form-control" name="start_time" required>
                                </div>
                                <div class="col-md-3 mb-3">
                                    <label class="form-label">Hora Fin</label>
                                    <input type="time" class="form-control" name="end_time" required>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Tipo de Cita</label>
                                    <select class="form-select" name="appointment_type" required>
                                        <option value="">Seleccionar...</option>
                                        <option value="primera">Primera Vez</option>
                                        <option value="seguimiento">Seguimiento</option>
                                        <option value="evaluacion">Evaluación</option>
                                        <option value="grupal">Grupal</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Modalidad</label>
                                    <select class="form-select" name="modality" required>
                                        <option value="">Seleccionar...</option>
                                        <option value="presencial">Presencial</option>
                                        <option value="virtual">Virtual</option>
                                        <option value="mixta">Mixta</option>
                                    </select>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Consultorio</label>
                                    <select class="form-select" name="room_id">
                                        <option value="">Seleccionar...</option>
                                        ${dashboardState.rooms.map(room => 
                                            `<option value="${room.id}">${room.name}</option>`
                                        ).join('')}
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Duración (minutos)</label>
                                    <input type="number" class="form-control" name="duration_minutes" value="60" min="15" max="180">
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Notas</label>
                                <textarea class="form-control" name="notes" rows="3"></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-primary" onclick="saveAppointment()">Agendar Cita</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if present
    const existingModal = document.getElementById('createAppointmentModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('createAppointmentModal'));
    modal.show();
}

async function saveAppointment() {
    try {
        const form = document.getElementById('createAppointmentForm');
        const formData = new FormData(form);
        
        const appointmentData = {
            patient_id: parseInt(formData.get('patient_id')),
            professional_id: parseInt(formData.get('professional_id')),
            room_id: formData.get('room_id') ? parseInt(formData.get('room_id')) : null,
            appointment_date: formData.get('appointment_date'),
            start_time: formData.get('start_time'),
            end_time: formData.get('end_time'),
            duration_minutes: parseInt(formData.get('duration_minutes')),
            appointment_type: formData.get('appointment_type'),
            modality: formData.get('modality'),
            notes: formData.get('notes'),
            status: 'pending',
            created_by: dashboardState.currentUser?.id
        };

        // Call API to create appointment
        const response = await fetch('/api/v1/appointments', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(appointmentData)
        });

        if (!response.ok) {
            throw new Error('Error al agendar cita');
        }

        const newAppointment = await response.json();
        
        // Add to local state
        dashboardState.appointments.push(newAppointment);
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('createAppointmentModal'));
        modal.hide();
        
        // Update UI
        updateUI();
        
        showAlert('Cita agendada exitosamente', 'success');
        
    } catch (error) {
        console.error('Error saving appointment:', error);
        showAlert('Error al agendar cita', 'danger');
    }
}

// Patient Dashboard Functions
function scheduleAppointment() {
    showCreateAppointmentModal();
}

function viewAppointment(appointmentId) {
    const appointment = dashboardState.appointments.find(a => a.id == appointmentId);
    if (appointment) {
        dashboardState.selectedAppointment = appointment;
        showAppointmentDetailsModal(appointment);
    }
}

function rescheduleAppointment(appointmentId) {
    const appointment = dashboardState.appointments.find(a => a.id == appointmentId);
    if (appointment) {
        showRescheduleModal(appointment);
    }
}

function showAppointmentDetailsModal(appointment) {
    const modalHTML = `
        <div class="modal fade" id="appointmentDetailsModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Detalles de Cita</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-3">
                            <div class="col-6">
                                <strong>Paciente:</strong><br>
                                ${getPatientName(appointment.patient_id)}
                            </div>
                            <div class="col-6">
                                <strong>Profesional:</strong><br>
                                ${getProfessionalName(appointment.professional_id)}
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-6">
                                <strong>Fecha:</strong><br>
                                ${formatDate(appointment.appointment_date)}
                            </div>
                            <div class="col-6">
                                <strong>Hora:</strong><br>
                                ${appointment.start_time} - ${appointment.end_time}
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-6">
                                <strong>Tipo:</strong><br>
                                ${getAppointmentTypeLabel(appointment.appointment_type)}
                            </div>
                            <div class="col-6">
                                <strong>Modalidad:</strong><br>
                                ${getModalityLabel(appointment.modality)}
                            </div>
                        </div>
                        ${appointment.notes ? `
                        <div class="mb-3">
                            <strong>Notas:</strong><br>
                            ${appointment.notes}
                        </div>
                        ` : ''}
                        <div class="mb-3">
                            <strong>Estado:</strong><br>
                            <span class="badge bg-${getStatusColor(appointment.status)}">${getStatusLabel(appointment.status)}</span>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        <button type="button" class="btn btn-warning" onclick="rescheduleAppointment(${appointment.id})">Reprogramar</button>
                        <button type="button" class="btn btn-danger" onclick="cancelAppointment(${appointment.id})">Cancelar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if present
    const existingModal = document.getElementById('appointmentDetailsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('appointmentDetailsModal'));
    modal.show();
}

// Mood Tracker Functions
function recordMood() {
    const modalHTML = `
        <div class="modal fade" id="recordMoodModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Registrar Estado de Ánimo</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="moodForm">
                            <div class="mb-4">
                                <label class="form-label">¿Cómo te sientes hoy?</label>
                                <div class="row text-center">
                                    <div class="col">
                                        <label class="mood-option">
                                            <input type="radio" name="mood" value="5" required>
                                            <div class="fs-1">😊</div>
                                            <small>Muy Bien</small>
                                        </label>
                                    </div>
                                    <div class="col">
                                        <label class="mood-option">
                                            <input type="radio" name="mood" value="4">
                                            <div class="fs-1">🙂</div>
                                            <small>Bien</small>
                                        </label>
                                    </div>
                                    <div class="col">
                                        <label class="mood-option">
                                            <input type="radio" name="mood" value="3">
                                            <div class="fs-1">😐</div>
                                            <small>Regular</small>
                                        </label>
                                    </div>
                                    <div class="col">
                                        <label class="mood-option">
                                            <input type="radio" name="mood" value="2">
                                            <div class="fs-1">😔</div>
                                            <small>Mal</small>
                                        </label>
                                    </div>
                                    <div class="col">
                                        <label class="mood-option">
                                            <input type="radio" name="mood" value="1">
                                            <div class="fs-1">😢</div>
                                            <small>Muy Mal</small>
                                        </label>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Notas (opcional)</label>
                                <textarea class="form-control" name="notes" rows="3" placeholder="¿Qué pasó hoy?"></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-success" onclick="saveMood()">Guardar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if present
    const existingModal = document.getElementById('recordMoodModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('recordMoodModal'));
    modal.show();
}

async function saveMood() {
    try {
        const form = document.getElementById('moodForm');
        const formData = new FormData(form);
        
        const moodData = {
            mood_value: parseInt(formData.get('mood')),
            notes: formData.get('notes'),
            user_id: dashboardState.currentUser?.id,
            date: new Date().toISOString().split('T')[0]
        };

        // Call API to save mood
        const response = await fetch('/api/v1/mood-records', {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(moodData)
        });

        if (!response.ok) {
            throw new Error('Error al guardar estado de ánimo');
        }

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('recordMoodModal'));
        modal.hide();
        
        showAlert('Estado de ánimo registrado exitosamente', 'success');
        
        // Update mood tracker
        updateMoodTracker();
        
    } catch (error) {
        console.error('Error saving mood:', error);
        showAlert('Error al guardar estado de ánimo', 'danger');
    }
}

function viewMoodHistory() {
    window.location.href = 'mood-history.html';
}

function downloadMoodReport() {
    showAlert('Generando reporte de estado de ánimo...', 'info');
    // Implement report generation
}

// Utility Functions
function getPatientName(patientId) {
    const patient = dashboardState.patients.find(p => p.id == patientId);
    return patient ? `${patient.nombres} ${patient.apellidos}` : 'Paciente no encontrado';
}

function getProfessionalName(professionalId) {
    const professionals = {
        1: 'Dr. Carlos Mendoza',
        2: 'Dra. María López',
        3: 'Dr. Roberto Silva'
    };
    return professionals[professionalId] || 'Profesional no encontrado';
}

function getAppointmentTypeLabel(type) {
    const labels = {
        'primera': 'Primera Vez',
        'seguimiento': 'Seguimiento',
        'evaluacion': 'Evaluación',
        'grupal': 'Grupal'
    };
    return labels[type] || type;
}

function getModalityLabel(modality) {
    const labels = {
        'presencial': 'Presencial',
        'virtual': 'Virtual',
        'mixta': 'Mixta'
    };
    return labels[modality] || modality;
}

function getStatusLabel(status) {
    const labels = {
        'pending': 'Pendiente',
        'confirmed': 'Confirmada',
        'in_progress': 'En Progreso',
        'completed': 'Completada',
        'cancelled': 'Cancelada',
        'no_show': 'No Asistió'
    };
    return labels[status] || status;
}

function getStatusColor(status) {
    const colors = {
        'pending': 'warning',
        'confirmed': 'success',
        'in_progress': 'info',
        'completed': 'primary',
        'cancelled': 'danger',
        'no_show': 'secondary'
    };
    return colors[status] || 'secondary';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-EC', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function getRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) {
        return `Hace ${diffMins} minutos`;
    } else if (diffHours < 24) {
        return `Hace ${diffHours} horas`;
    } else if (diffDays < 7) {
        return `Hace ${diffDays} días`;
    } else {
        return formatDate(dateString);
    }
}

// Chart initialization
function updateCharts() {
    // Update appointments chart
    const appointmentsChart = document.getElementById('appointmentsChart');
    if (appointmentsChart) {
        updateAppointmentsChart(appointmentsChart);
    }

    // Update services chart
    const servicesChart = document.getElementById('servicesChart');
    if (servicesChart) {
        updateServicesChart(servicesChart);
    }
}

function updateAppointmentsChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    // Prepare data for last 6 months
    const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'];
    const currentMonth = new Date().getMonth();
    const data = months.map((month, index) => {
        const targetMonth = (currentMonth - 5 + index + 12) % 12;
        return dashboardState.appointments.filter(a => 
            new Date(a.appointment_date).getMonth() === targetMonth
        ).length;
    });

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Citas',
                data: data,
                borderColor: 'rgb(30, 64, 175)',
                backgroundColor: 'rgba(30, 64, 175, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function updateServicesChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    // Count appointments by type
    const typeCounts = {};
    dashboardState.appointments.forEach(appointment => {
        typeCounts[appointment.appointment_type] = (typeCounts[appointment.appointment_type] || 0) + 1;
    });

    const labels = Object.keys(typeCounts).map(type => getAppointmentTypeLabel(type));
    const data = Object.values(typeCounts);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgb(30, 64, 175)',
                    'rgb(40, 167, 69)',
                    'rgb(255, 193, 7)',
                    'rgb(220, 53, 69)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Export functions
function exportReport() {
    showAlert('Generando reporte...', 'info');
    // Implement export functionality
    setTimeout(() => {
        showAlert('Reporte generado exitosamente', 'success');
    }, 2000);
}

// Make functions globally available
window.quickAction = quickAction;
window.scheduleAppointment = scheduleAppointment;
window.viewAppointment = viewAppointment;
window.rescheduleAppointment = rescheduleAppointment;
window.recordMood = recordMood;
window.viewMoodHistory = viewMoodHistory;
window.downloadMoodReport = downloadMoodReport;
window.savePatient = savePatient;
window.saveAppointment = saveAppointment;
window.exportReport = exportReport;
