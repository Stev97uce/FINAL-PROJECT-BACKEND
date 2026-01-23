/**
 * UCE Psychology System - Patient Management Functions
 * Complete CRUD operations for patient management
 */

// Patient CRUD Operations
class PatientManager {
    constructor() {
        this.patients = [];
        this.currentPatient = null;
        this.init();
    }

    async init() {
        await this.loadPatients();
        this.setupEventListeners();
    }

    async loadPatients() {
        try {
            const response = await fetch('/api/v1/patients', {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                this.patients = data.data || data;
                this.updatePatientsTable();
            }
        } catch (error) {
            console.error('Error loading patients:', error);
            this.patients = [];
        }
    }

    setupEventListeners() {
        // Add event listeners for patient management
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="create-patient"]')) {
                this.showCreatePatientModal();
            } else if (e.target.matches('[data-action="edit-patient"]')) {
                const patientId = e.target.dataset.patientId;
                this.showEditPatientModal(patientId);
            } else if (e.target.matches('[data-action="delete-patient"]')) {
                const patientId = e.target.dataset.patientId;
                this.deletePatient(patientId);
            } else if (e.target.matches('[data-action="view-patient"]')) {
                const patientId = e.target.dataset.patientId;
                this.viewPatientDetails(patientId);
            }
        });
    }

    showCreatePatientModal() {
        const modalHTML = `
            <div class="modal fade" id="patientModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Registrar Nuevo Paciente</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="patientForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6 class="text-primary mb-3">Información Personal</h6>
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Nombres *</label>
                                                <input type="text" class="form-control" name="nombres" required>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Apellidos *</label>
                                                <input type="text" class="form-control" name="apellidos" required>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Cédula *</label>
                                                <input type="text" class="form-control" name="cedula" required 
                                                       pattern="[0-9]{10}" title="Ingrese 10 dígitos">
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Fecha de Nacimiento *</label>
                                                <input type="date" class="form-control" name="fecha_nacimiento" required>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Género *</label>
                                                <select class="form-select" name="genero" required>
                                                    <option value="">Seleccionar...</option>
                                                    <option value="Masculino">Masculino</option>
                                                    <option value="Femenino">Femenino</option>
                                                    <option value="Otro">Otro</option>
                                                    <option value="Prefiero no decir">Prefiero no decir</option>
                                                </select>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Estado Civil *</label>
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
                                    </div>
                                    <div class="col-md-6">
                                        <h6 class="text-primary mb-3">Información de Contacto</h6>
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Teléfono Principal *</label>
                                                <input type="tel" class="form-control" name="telefono" required 
                                                       pattern="[0-9]{10}" title="Ingrese 10 dígitos">
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Teléfono Emergencia</label>
                                                <input type="tel" class="form-control" name="telefono_emergencia">
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Email</label>
                                                <input type="email" class="form-control" name="email">
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Contacto Emergencia</label>
                                                <input type="text" class="form-control" name="contacto_emergencia_nombre">
                                            </div>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Dirección *</label>
                                            <input type="text" class="form-control" name="direccion" required>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Ciudad *</label>
                                                <input type="text" class="form-control" name="ciudad" required>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Provincia *</label>
                                                <input type="text" class="form-control" name="provincia" required>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6 class="text-primary mb-3">Información Médica</h6>
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Tipo de Sangre</label>
                                                <select class="form-select" name="tipo_sangre">
                                                    <option value="A+">A+</option>
                                                    <option value="A-">A-</option>
                                                    <option value="B+">B+</option>
                                                    <option value="B-">B-</option>
                                                    <option value="AB+">AB+</option>
                                                    <option value="AB-">AB-</option>
                                                    <option value="O+">O+</option>
                                                    <option value="O-">O-</option>
                                                    <option value="Desconocido">Desconocido</option>
                                                </select>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Ocupación</label>
                                                <input type="text" class="form-control" name="ocupacion">
                                            </div>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Alergias</label>
                                            <textarea class="form-control" name="alergias" rows="2" 
                                                      placeholder="Describir alergias conocidas"></textarea>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Medicamentos Actuales</label>
                                            <textarea class="form-control" name="medicamentos_actuales" rows="2" 
                                                      placeholder="Listar medicamentos actuales"></textarea>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Condiciones Médicas</label>
                                            <textarea class="form-control" name="condiciones_medicas" rows="2" 
                                                      placeholder="Condiciones médicas preexistentes"></textarea>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <h6 class="text-primary mb-3">Información de Consulta</h6>
                                        <div class="mb-3">
                                            <label class="form-label">Institución</label>
                                            <input type="text" class="form-control" name="institucion">
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Motivo de Consulta Inicial *</label>
                                            <textarea class="form-control" name="motivo_consulta_inicial" rows="4" required
                                                      placeholder="Describir el motivo principal de consulta"></textarea>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Relación Contacto Emergencia</label>
                                            <select class="form-select" name="contacto_emergencia_relacion">
                                                <option value="">Seleccionar...</option>
                                                <option value="Padre/Madre">Padre/Madre</option>
                                                <option value="Hermano/a">Hermano/a</option>
                                                <option value="Esposo/a">Esposo/a</option>
                                                <option value="Hijo/a">Hijo/a</option>
                                                <option value="Amigo/a">Amigo/a</option>
                                                <option value="Otro">Otro</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="patientManager.savePatient()">
                                <i class="bi bi-save me-2"></i>Guardar Paciente
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('patientModal');
        if (existingModal) existingModal.remove();

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('patientModal'));
        modal.show();
    }

    async savePatient() {
        try {
            const form = document.getElementById('patientForm');
            const formData = new FormData(form);
            
            // Validate form
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            const patientData = {
                nombres: formData.get('nombres'),
                apellidos: formData.get('apellidos'),
                cedula: formData.get('cedula'),
                fecha_nacimiento: formData.get('fecha_nacimiento'),
                genero: formData.get('genero'),
                estado_civil: formData.get('estado_civil'),
                telefono: formData.get('telefono'),
                telefono_emergencia: formData.get('telefono_emergencia'),
                contacto_emergencia_nombre: formData.get('contacto_emergencia_nombre'),
                contacto_emergencia_relacion: formData.get('contacto_emergencia_relacion'),
                email: formData.get('email'),
                direccion: formData.get('direccion'),
                ciudad: formData.get('ciudad'),
                provincia: formData.get('provincia'),
                tipo_sangre: formData.get('tipo_sangre'),
                alergias: formData.get('alergias'),
                medicamentos_actuales: formData.get('medicamentos_actuales'),
                condiciones_medicas: formData.get('condiciones_medicas'),
                ocupacion: formData.get('ocupacion'),
                institucion: formData.get('institucion'),
                motivo_consulta_inicial: formData.get('motivo_consulta_inicial'),
                is_active: true,
                created_by: getCurrentUser()?.id
            };

            const response = await fetch('/api/v1/patients', {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(patientData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Error al crear paciente');
            }

            const newPatient = await response.json();
            this.patients.push(newPatient);
            this.updatePatientsTable();

            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('patientModal'));
            modal.hide();

            showAlert('Paciente creado exitosamente', 'success');
            
        } catch (error) {
            console.error('Error saving patient:', error);
            showAlert(error.message || 'Error al guardar paciente', 'danger');
        }
    }

    showEditPatientModal(patientId) {
        const patient = this.patients.find(p => p.id == patientId);
        if (!patient) {
            showAlert('Paciente no encontrado', 'danger');
            return;
        }

        this.currentPatient = patient;
        
        // Similar to create modal but with pre-filled data
        this.showCreatePatientModal();
        
        // Fill form with patient data
        setTimeout(() => {
            const form = document.getElementById('patientForm');
            Object.keys(patient).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = patient[key];
                }
            });
            
            // Update modal title
            document.querySelector('#patientModal .modal-title').textContent = 'Editar Paciente';
        }, 100);
    }

    async deletePatient(patientId) {
        if (!confirm('¿Está seguro de que desea eliminar este paciente? Esta acción no se puede deshacer.')) {
            return;
        }

        try {
            const response = await fetch(`/api/v1/patients/${patientId}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error('Error al eliminar paciente');
            }

            this.patients = this.patients.filter(p => p.id != patientId);
            this.updatePatientsTable();
            showAlert('Paciente eliminado exitosamente', 'success');
            
        } catch (error) {
            console.error('Error deleting patient:', error);
            showAlert('Error al eliminar paciente', 'danger');
        }
    }

    viewPatientDetails(patientId) {
        const patient = this.patients.find(p => p.id == patientId);
        if (!patient) {
            showAlert('Paciente no encontrado', 'danger');
            return;
        }

        const modalHTML = `
            <div class="modal fade" id="patientDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Detalles del Paciente</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <h6 class="text-primary mb-3">Información Personal</h6>
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <strong>Nombres:</strong> ${patient.nombres}
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Apellidos:</strong> ${patient.apellidos}
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <strong>Cédula:</strong> ${patient.cedula}
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Fecha de Nacimiento:</strong> ${formatDate(patient.fecha_nacimiento)}
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <strong>Género:</strong> ${patient.genero}
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Estado Civil:</strong> ${patient.estado_civil}
                                        </div>
                                    </div>
                                    
                                    <h6 class="text-primary mb-3 mt-4">Información de Contacto</h6>
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <strong>Teléfono:</strong> ${patient.telefono}
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Email:</strong> ${patient.email || 'No registrado'}
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <div class="col-12">
                                            <strong>Dirección:</strong> ${patient.direccion}, ${patient.ciudad}, ${patient.provincia}
                                        </div>
                                    </div>
                                    
                                    <h6 class="text-primary mb-3 mt-4">Información Médica</h6>
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <strong>Tipo de Sangre:</strong> ${patient.tipo_sangre || 'No registrado'}
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Ocupación:</strong> ${patient.ocupacion || 'No registrada'}
                                        </div>
                                    </div>
                                    ${patient.alergias ? `
                                    <div class="mb-3">
                                        <strong>Alergias:</strong><br>
                                        ${patient.alergias}
                                    </div>
                                    ` : ''}
                                    ${patient.medicamentos_actuales ? `
                                    <div class="mb-3">
                                        <strong>Medicamentos Actuales:</strong><br>
                                        ${patient.medicamentos_actuales}
                                    </div>
                                    ` : ''}
                                    ${patient.condiciones_medicas ? `
                                    <div class="mb-3">
                                        <strong>Condiciones Médicas:</strong><br>
                                        ${patient.condiciones_medicas}
                                    </div>
                                    ` : ''}
                                    
                                    <h6 class="text-primary mb-3 mt-4">Motivo de Consulta</h6>
                                    <div class="mb-3">
                                        ${patient.motivo_consulta_inicial}
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">Acciones Rápidas</h6>
                                        </div>
                                        <div class="card-body">
                                            <div class="d-grid gap-2">
                                                <button class="btn btn-primary" onclick="patientManager.showEditPatientModal(${patient.id})">
                                                    <i class="bi bi-pencil me-2"></i>Editar Paciente
                                                </button>
                                                <button class="btn btn-success" onclick="createAppointmentForPatient(${patient.id})">
                                                    <i class="bi bi-calendar-plus me-2"></i>Agendar Cita
                                                </button>
                                                <button class="btn btn-info" onclick="viewClinicalRecord(${patient.id})">
                                                    <i class="bi bi-file-medical me-2"></i>Ver Expediente
                                                </button>
                                                <button class="btn btn-warning" onclick="generatePatientReport(${patient.id})">
                                                    <i class="bi bi-download me-2"></i>Generar Reporte
                                                </button>
                                                <button class="btn btn-danger" onclick="patientManager.deletePatient(${patient.id})">
                                                    <i class="bi bi-trash me-2"></i>Eliminar Paciente
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="card mt-3">
                                        <div class="card-header">
                                            <h6 class="mb-0">Estado</h6>
                                        </div>
                                        <div class="card-body">
                                            <div class="d-flex justify-content-between align-items-center">
                                                <span>Estado:</span>
                                                <span class="badge bg-${patient.is_active ? 'success' : 'danger'}">
                                                    ${patient.is_active ? 'Activo' : 'Inactivo'}
                                                </span>
                                            </div>
                                            <div class="mt-2">
                                                <small class="text-muted">
                                                    Registrado: ${formatDate(patient.created_at)}
                                                </small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('patientDetailsModal');
        if (existingModal) existingModal.remove();

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('patientDetailsModal'));
        modal.show();
    }

    updatePatientsTable() {
        const tableBody = document.querySelector('#patientsTable tbody');
        if (!tableBody) return;

        tableBody.innerHTML = this.patients.map(patient => `
            <tr>
                <td>${patient.nombres} ${patient.apellidos}</td>
                <td>${patient.cedula}</td>
                <td>${patient.telefono}</td>
                <td>${patient.email || '-'}</td>
                <td>
                    <span class="badge bg-${patient.is_active ? 'success' : 'danger'}">
                        ${patient.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td>
                    <div class="btn-group" role="group">
                        <button class="btn btn-sm btn-outline-primary" data-action="view-patient" data-patient-id="${patient.id}">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-warning" data-action="edit-patient" data-patient-id="${patient.id}">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" data-action="delete-patient" data-patient-id="${patient.id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    // Search functionality
    searchPatients(query) {
        if (!query) {
            this.updatePatientsTable();
            return;
        }

        const filteredPatients = this.patients.filter(patient => 
            patient.nombres.toLowerCase().includes(query.toLowerCase()) ||
            patient.apellidos.toLowerCase().includes(query.toLowerCase()) ||
            patient.cedula.includes(query) ||
            patient.telefono.includes(query)
        );

        const tableBody = document.querySelector('#patientsTable tbody');
        if (tableBody) {
            if (filteredPatients.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="6" class="text-center">No se encontraron pacientes</td></tr>';
            } else {
                // Temporarily update patients array for table update
                const originalPatients = this.patients;
                this.patients = filteredPatients;
                this.updatePatientsTable();
                this.patients = originalPatients;
            }
        }
    }
}

// Global instance
let patientManager;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('patientsTable') || document.querySelector('[data-action="create-patient"]')) {
        patientManager = new PatientManager();
    }
});

// Make globally available
window.patientManager = patientManager;

// Helper functions
function createAppointmentForPatient(patientId) {
    // Close patient details modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('patientDetailsModal'));
    if (modal) modal.hide();
    
    // Open appointment modal with pre-selected patient
    setTimeout(() => {
        showCreateAppointmentModal();
        // Pre-select patient in the form
        setTimeout(() => {
            const patientSelect = document.querySelector('select[name="patient_id"]');
            if (patientSelect) {
                patientSelect.value = patientId;
            }
        }, 500);
    }, 300);
}

function viewClinicalRecord(patientId) {
    window.location.href = `clinical-record.html?patient_id=${patientId}`;
}

function generatePatientReport(patientId) {
    showAlert('Generando reporte del paciente...', 'info');
    // Implement report generation
}

// Search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('patientSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            if (patientManager) {
                patientManager.searchPatients(e.target.value);
            }
        });
    }
});
