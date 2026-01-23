/**
 * UCE Psychology System - Appointment Management Functions
 * Complete appointment scheduling and management system
 */

class AppointmentManager {
    constructor() {
        this.appointments = [];
        this.rooms = [];
        this.patients = [];
        this.professionals = [];
        this.currentView = 'calendar';
        this.init();
    }

    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.initializeCalendar();
        this.updateUI();
    }

    async loadData() {
        try {
            // Load appointments
            const appointmentsResponse = await fetch('/api/v1/appointments', {
                headers: getAuthHeaders()
            });
            if (appointmentsResponse.ok) {
                const data = await appointmentsResponse.json();
                this.appointments = data.data || data;
            }

            // Load rooms
            const roomsResponse = await fetch('/api/v1/rooms', {
                headers: getAuthHeaders()
            });
            if (roomsResponse.ok) {
                const data = await roomsResponse.json();
                this.rooms = data.data || data;
            }

            // Load patients
            const patientsResponse = await fetch('/api/v1/patients', {
                headers: getAuthHeaders()
            });
            if (patientsResponse.ok) {
                const data = await patientsResponse.json();
                this.patients = data.data || data;
            }

            // Mock professionals data (should come from API)
            this.professionals = [
                { id: 1, name: 'Dr. Carlos Mendoza', specialty: 'Psicología Clínica' },
                { id: 2, name: 'Dra. María López', specialty: 'Psicoterapia' },
                { id: 3, name: 'Dr. Roberto Silva', specialty: 'Neuropsicología' },
                { id: 4, name: 'Dra. Patricia Castro', specialty: 'Psicología Infantil' }
            ];

        } catch (error) {
            console.error('Error loading appointment data:', error);
        }
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="create-appointment"]')) {
                this.showCreateAppointmentModal();
            } else if (e.target.matches('[data-action="edit-appointment"]')) {
                const appointmentId = e.target.dataset.appointmentId;
                this.showEditAppointmentModal(appointmentId);
            } else if (e.target.matches('[data-action="delete-appointment"]')) {
                const appointmentId = e.target.dataset.appointmentId;
                this.deleteAppointment(appointmentId);
            } else if (e.target.matches('[data-action="confirm-appointment"]')) {
                const appointmentId = e.target.dataset.appointmentId;
                this.confirmAppointment(appointmentId);
            } else if (e.target.matches('[data-action="cancel-appointment"]')) {
                const appointmentId = e.target.dataset.appointmentId;
                this.cancelAppointment(appointmentId);
            } else if (e.target.matches('[data-action="complete-appointment"]')) {
                const appointmentId = e.target.dataset.appointmentId;
                this.completeAppointment(appointmentId);
            } else if (e.target.matches('[data-action="view-calendar"]')) {
                this.switchView('calendar');
            } else if (e.target.matches('[data-action="view-list"]')) {
                this.switchView('list');
            }
        });

        // Filter listeners
        const filterElements = document.querySelectorAll('[data-filter]');
        filterElements.forEach(element => {
            element.addEventListener('change', () => this.applyFilters());
        });
    }

    showCreateAppointmentModal(preselectedData = {}) {
        const modalHTML = `
            <div class="modal fade" id="appointmentModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Agendar Nueva Cita</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="appointmentForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6 class="text-primary mb-3">Información Básica</h6>
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Paciente *</label>
                                                <select class="form-select" name="patient_id" required>
                                                    <option value="">Seleccionar paciente...</option>
                                                    ${this.patients.map(patient => 
                                                        `<option value="${patient.id}" ${preselectedData.patientId == patient.id ? 'selected' : ''}>
                                                            ${patient.nombres} ${patient.apellidos}
                                                        </option>`
                                                    ).join('')}
                                                </select>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Profesional *</label>
                                                <select class="form-select" name="professional_id" required>
                                                    <option value="">Seleccionar profesional...</option>
                                                    ${this.professionals.map(professional => 
                                                        `<option value="${professional.id}" ${preselectedData.professionalId == professional.id ? 'selected' : ''}>
                                                            ${professional.name} - ${professional.specialty}
                                                        </option>`
                                                    ).join('')}
                                                </select>
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-4 mb-3">
                                                <label class="form-label">Fecha *</label>
                                                <input type="date" class="form-control" name="appointment_date" required
                                                       value="${preselectedData.date || ''}">
                                            </div>
                                            <div class="col-md-4 mb-3">
                                                <label class="form-label">Hora Inicio *</label>
                                                <input type="time" class="form-control" name="start_time" required
                                                       value="${preselectedData.startTime || ''}">
                                            </div>
                                            <div class="col-md-4 mb-3">
                                                <label class="form-label">Hora Fin *</label>
                                                <input type="time" class="form-control" name="end_time" required
                                                       value="${preselectedData.endTime || ''}">
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Tipo de Cita *</label>
                                                <select class="form-select" name="appointment_type" required>
                                                    <option value="">Seleccionar...</option>
                                                    <option value="primera">Primera Vez</option>
                                                    <option value="seguimiento">Seguimiento</option>
                                                    <option value="evaluacion">Evaluación</option>
                                                    <option value="grupal">Grupal</option>
                                                    <option value="emergencia">Emergencia</option>
                                                </select>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Modalidad *</label>
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
                                                    ${this.rooms.filter(room => room.status === 'disponible').map(room => 
                                                        `<option value="${room.id}">${room.name} - ${room.room_number}</option>`
                                                    ).join('')}
                                                </select>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Duración (minutos)</label>
                                                <input type="number" class="form-control" name="duration_minutes" 
                                                       value="60" min="15" max="180" step="15">
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <h6 class="text-primary mb-3">Detalles Adicionales</h6>
                                        <div class="mb-3">
                                            <label class="form-label">Notas de la Cita</label>
                                            <textarea class="form-control" name="notes" rows="4" 
                                                      placeholder="Notas importantes sobre la cita..."></textarea>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Instrucciones para el Paciente</label>
                                            <textarea class="form-control" name="patient_instructions" rows="3" 
                                                      placeholder="Instrucciones que el paciente debe seguir antes/durante la cita..."></textarea>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Recordatorio</label>
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" name="send_reminder" checked>
                                                <label class="form-check-label">
                                                    Enviar recordatorio automático
                                                </label>
                                            </div>
                                            <div class="mt-2">
                                                <label class="form-label">Tiempo de recordatorio</label>
                                                <select class="form-select" name="reminder_time">
                                                    <option value="60">1 hora antes</option>
                                                    <option value="120">2 horas antes</option>
                                                    <option value="1440">1 día antes</option>
                                                    <option value="2880">2 días antes</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Availability Check -->
                                <div class="row mt-3">
                                    <div class="col-12">
                                        <div class="alert alert-info d-none" id="availabilityAlert">
                                            <i class="bi bi-info-circle me-2"></i>
                                            <span id="availabilityMessage"></span>
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-info" onclick="appointmentManager.checkAvailability()">
                                <i class="bi bi-search me-2"></i>Ver Disponibilidad
                            </button>
                            <button type="button" class="btn btn-primary" onclick="appointmentManager.saveAppointment()">
                                <i class="bi bi-calendar-check me-2"></i>Agendar Cita
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('appointmentModal');
        if (existingModal) existingModal.remove();

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Setup real-time validation
        this.setupAppointmentValidation();

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('appointmentModal'));
        modal.show();
    }

    setupAppointmentValidation() {
        const form = document.getElementById('appointmentForm');
        const dateInput = form.querySelector('[name="appointment_date"]');
        const startTimeInput = form.querySelector('[name="start_time"]');
        const endTimeInput = form.querySelector('[name="end_time"]');
        const professionalSelect = form.querySelector('[name="professional_id"]');

        const checkAvailability = () => {
            if (dateInput.value && startTimeInput.value && endTimeInput.value && professionalSelect.value) {
                this.checkAvailability();
            }
        };

        [dateInput, startTimeInput, endTimeInput, professionalSelect].forEach(input => {
            input.addEventListener('change', checkAvailability);
        });
    }

    async checkAvailability() {
        const form = document.getElementById('appointmentForm');
        const formData = new FormData(form);
        
        const availabilityData = {
            professional_id: parseInt(formData.get('professional_id')),
            appointment_date: formData.get('appointment_date'),
            start_time: formData.get('start_time'),
            end_time: formData.get('end_time')
        };

        try {
            const response = await fetch('/api/v1/availability/check', {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(availabilityData)
            });

            const result = await response.json();
            const alertDiv = document.getElementById('availabilityAlert');
            const messageSpan = document.getElementById('availabilityMessage');

            if (result.available) {
                alertDiv.className = 'alert alert-success';
                messageSpan.textContent = '✓ El profesional está disponible en este horario';
            } else {
                alertDiv.className = 'alert alert-warning';
                messageSpan.textContent = `⚠ ${result.message || 'El profesional no está disponible en este horario'}`;
            }
            
            alertDiv.classList.remove('d-none');

        } catch (error) {
            console.error('Error checking availability:', error);
            const alertDiv = document.getElementById('availabilityAlert');
            const messageSpan = document.getElementById('availabilityMessage');
            alertDiv.className = 'alert alert-danger';
            messageSpan.textContent = 'Error al verificar disponibilidad';
            alertDiv.classList.remove('d-none');
        }
    }

    async saveAppointment() {
        try {
            const form = document.getElementById('appointmentForm');
            const formData = new FormData(form);

            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

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
                patient_instructions: formData.get('patient_instructions'),
                send_reminder: formData.has('send_reminder'),
                reminder_time: formData.get('reminder_time'),
                status: 'pending',
                created_by: getCurrentUser()?.id
            };

            const response = await fetch('/api/v1/appointments', {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(appointmentData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Error al agendar cita');
            }

            const newAppointment = await response.json();
            this.appointments.push(newAppointment);
            this.updateUI();

            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('appointmentModal'));
            modal.hide();

            showAlert('Cita agendada exitosamente', 'success');

            // Send notification if enabled
            if (appointmentData.send_reminder) {
                this.scheduleReminder(newAppointment);
            }

        } catch (error) {
            console.error('Error saving appointment:', error);
            showAlert(error.message || 'Error al agendar cita', 'danger');
        }
    }

    async scheduleReminder(appointment) {
        try {
            await fetch('/api/v1/notifications/schedule-reminder', {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    appointment_id: appointment.id,
                    reminder_time: appointment.reminder_time
                })
            });
        } catch (error) {
            console.error('Error scheduling reminder:', error);
        }
    }

    showEditAppointmentModal(appointmentId) {
        const appointment = this.appointments.find(a => a.id == appointmentId);
        if (!appointment) {
            showAlert('Cita no encontrada', 'danger');
            return;
        }

        // Pre-fill form with appointment data
        const preselectedData = {
            patientId: appointment.patient_id,
            professionalId: appointment.professional_id,
            date: appointment.appointment_date,
            startTime: appointment.start_time,
            endTime: appointment.end_time
        };

        this.showCreateAppointmentModal(preselectedData);

        // Update modal title and fill form
        setTimeout(() => {
            document.querySelector('#appointmentModal .modal-title').textContent = 'Editar Cita';
            const form = document.getElementById('appointmentForm');
            
            Object.keys(appointment).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = appointment[key];
                    } else {
                        input.value = appointment[key];
                    }
                }
            });
        }, 100);
    }

    async confirmAppointment(appointmentId) {
        try {
            const response = await fetch(`/api/v1/appointments/${appointmentId}/confirm`, {
                method: 'PATCH',
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error('Error al confirmar cita');
            }

            const appointment = this.appointments.find(a => a.id == appointmentId);
            if (appointment) {
                appointment.status = 'confirmed';
                this.updateUI();
            }

            showAlert('Cita confirmada exitosamente', 'success');
        } catch (error) {
            console.error('Error confirming appointment:', error);
            showAlert('Error al confirmar cita', 'danger');
        }
    }

    async cancelAppointment(appointmentId) {
        if (!confirm('¿Está seguro de que desea cancelar esta cita?')) {
            return;
        }

        const reason = prompt('Motivo de cancelación (opcional):');
        
        try {
            const response = await fetch(`/api/v1/appointments/${appointmentId}/cancel`, {
                method: 'PATCH',
                headers: getAuthHeaders(),
                body: JSON.stringify({ cancellation_reason: reason })
            });

            if (!response.ok) {
                throw new Error('Error al cancelar cita');
            }

            const appointment = this.appointments.find(a => a.id == appointmentId);
            if (appointment) {
                appointment.status = 'cancelled';
                appointment.cancellation_reason = reason;
                this.updateUI();
            }

            showAlert('Cita cancelada exitosamente', 'success');
        } catch (error) {
            console.error('Error cancelling appointment:', error);
            showAlert('Error al cancelar cita', 'danger');
        }
    }

    async completeAppointment(appointmentId) {
        try {
            const response = await fetch(`/api/v1/appointments/${appointmentId}/complete`, {
                method: 'PATCH',
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error('Error al completar cita');
            }

            const appointment = this.appointments.find(a => a.id == appointmentId);
            if (appointment) {
                appointment.status = 'completed';
                this.updateUI();
            }

            // Redirect to clinical note creation
            showAlert('Cita completada. Puede añadir notas clínicas ahora.', 'info');
            setTimeout(() => {
                window.location.href = `clinical-record.html?appointment_id=${appointmentId}`;
            }, 2000);

        } catch (error) {
            console.error('Error completing appointment:', error);
            showAlert('Error al completar cita', 'danger');
        }
    }

    async deleteAppointment(appointmentId) {
        if (!confirm('¿Está seguro de que desea eliminar esta cita? Esta acción no se puede deshacer.')) {
            return;
        }

        try {
            const response = await fetch(`/api/v1/appointments/${appointmentId}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error('Error al eliminar cita');
            }

            this.appointments = this.appointments.filter(a => a.id != appointmentId);
            this.updateUI();
            showAlert('Cita eliminada exitosamente', 'success');
        } catch (error) {
            console.error('Error deleting appointment:', error);
            showAlert('Error al eliminar cita', 'danger');
        }
    }

    switchView(view) {
        this.currentView = view;
        
        // Update button states
        document.querySelectorAll('[data-action]').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-action="view-${view}"]`)?.classList.add('active');

        // Update view
        if (view === 'calendar') {
            this.showCalendarView();
        } else {
            this.showListView();
        }
    }

    showCalendarView() {
        const calendarContainer = document.getElementById('calendarContainer');
        const listContainer = document.getElementById('listContainer');
        
        if (calendarContainer) calendarContainer.style.display = 'block';
        if (listContainer) listContainer.style.display = 'none';
        
        this.renderCalendar();
    }

    showListView() {
        const calendarContainer = document.getElementById('calendarContainer');
        const listContainer = document.getElementById('listContainer');
        
        if (calendarContainer) calendarContainer.style.display = 'none';
        if (listContainer) listContainer.style.display = 'block';
        
        this.renderAppointmentsList();
    }

    initializeCalendar() {
        if (document.getElementById('calendar')) {
            // Initialize calendar library or custom implementation
            this.renderCalendar();
        }
    }

    renderCalendar() {
        const calendarElement = document.getElementById('calendar');
        if (!calendarElement) return;

        // Simple calendar implementation
        const today = new Date();
        const currentMonth = today.getMonth();
        const currentYear = today.getFullYear();
        
        // Generate calendar HTML
        const calendarHTML = this.generateCalendarHTML(currentMonth, currentYear);
        calendarElement.innerHTML = calendarHTML;
    }

    generateCalendarHTML(month, year) {
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        
        let html = '<div class="calendar-grid">';
        
        // Day headers
        const dayHeaders = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
        dayHeaders.forEach(day => {
            html += `<div class="calendar-header">${day}</div>`;
        });
        
        // Empty cells for days before month starts
        for (let i = 0; i < firstDay; i++) {
            html += '<div class="calendar-day empty"></div>';
        }
        
        // Days of the month
        for (let day = 1; day <= daysInMonth; day++) {
            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const dayAppointments = this.appointments.filter(a => a.appointment_date === dateStr);
            
            html += `
                <div class="calendar-day ${dayAppointments.length > 0 ? 'has-appointments' : ''}" 
                     data-date="${dateStr}">
                    <div class="calendar-day-number">${day}</div>
                    ${dayAppointments.length > 0 ? `
                        <div class="calendar-appointments">
                            <small>${dayAppointments.length} citas</small>
                        </div>
                    ` : ''}
                </div>
            `;
        }
        
        html += '</div>';
        return html;
    }

    renderAppointmentsList() {
        const listContainer = document.getElementById('appointmentsList');
        if (!listContainer) return;

        const filteredAppointments = this.getFilteredAppointments();
        
        listContainer.innerHTML = filteredAppointments.map(appointment => `
            <div class="card mb-3 appointment-card">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <div class="d-flex align-items-center">
                                <div class="appointment-date me-3">
                                    <div class="date-day">${new Date(appointment.appointment_date).getDate()}</div>
                                    <div class="date-month">${new Date(appointment.appointment_date).toLocaleDateString('es-ES', { month: 'short' })}</div>
                                </div>
                                <div>
                                    <div class="fw-bold">${appointment.start_time} - ${appointment.end_time}</div>
                                    <small class="text-muted">${appointment.duration_minutes} min</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div>
                                <strong>${this.getPatientName(appointment.patient_id)}</strong>
                                <br><small class="text-muted">${this.getProfessionalName(appointment.professional_id)}</small>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <span class="badge bg-${this.getStatusColor(appointment.status)}">
                                ${this.getStatusLabel(appointment.status)}
                            </span>
                            <br><small class="text-muted">${this.getTypeLabel(appointment.appointment_type)}</small>
                        </div>
                        <div class="col-md-2">
                            <div>
                                <i class="bi bi-${appointment.modality === 'virtual' ? 'camera' : 'geo-alt'}"></i>
                                ${this.getModalityLabel(appointment.modality)}
                            </div>
                            ${appointment.room_id ? `<br><small class="text-muted">${this.getRoomName(appointment.room_id)}</small>` : ''}
                        </div>
                        <div class="col-md-2">
                            <div class="btn-group" role="group">
                                ${this.getAppointmentActions(appointment)}
                            </div>
                        </div>
                    </div>
                    ${appointment.notes ? `
                        <div class="mt-2">
                            <small class="text-muted">${appointment.notes}</small>
                        </div>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    getAppointmentActions(appointment) {
        const actions = [];
        
        switch (appointment.status) {
            case 'pending':
                actions.push(`
                    <button class="btn btn-sm btn-success" data-action="confirm-appointment" 
                            data-appointment-id="${appointment.id}" title="Confirmar">
                        <i class="bi bi-check"></i>
                    </button>
                `);
                actions.push(`
                    <button class="btn btn-sm btn-warning" data-action="edit-appointment" 
                            data-appointment-id="${appointment.id}" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                `);
                actions.push(`
                    <button class="btn btn-sm btn-danger" data-action="cancel-appointment" 
                            data-appointment-id="${appointment.id}" title="Cancelar">
                        <i class="bi bi-x"></i>
                    </button>
                `);
                break;
            case 'confirmed':
                actions.push(`
                    <button class="btn btn-sm btn-info" data-action="complete-appointment" 
                            data-appointment-id="${appointment.id}" title="Completar">
                        <i class="bi bi-check2"></i>
                    </button>
                `);
                actions.push(`
                    <button class="btn btn-sm btn-warning" data-action="edit-appointment" 
                            data-appointment-id="${appointment.id}" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                `);
                actions.push(`
                    <button class="btn btn-sm btn-danger" data-action="cancel-appointment" 
                            data-appointment-id="${appointment.id}" title="Cancelar">
                        <i class="bi bi-x"></i>
                    </button>
                `);
                break;
            case 'completed':
                actions.push(`
                    <button class="btn btn-sm btn-info" data-action="view-clinical-note" 
                            data-appointment-id="${appointment.id}" title="Ver Nota Clínica">
                        <i class="bi bi-file-medical"></i>
                    </button>
                `);
                break;
            case 'cancelled':
                actions.push(`
                    <button class="btn btn-sm btn-warning" data-action="edit-appointment" 
                            data-appointment-id="${appointment.id}" title="Reprogramar">
                        <i class="bi bi-arrow-repeat"></i>
                    </button>
                `);
                break;
        }
        
        actions.push(`
            <button class="btn btn-sm btn-outline-danger" data-action="delete-appointment" 
                    data-appointment-id="${appointment.id}" title="Eliminar">
                <i class="bi bi-trash"></i>
            </button>
        `);
        
        return actions.join('');
    }

    getFilteredAppointments() {
        let filtered = [...this.appointments];
        
        // Apply filters
        const statusFilter = document.querySelector('[data-filter="status"]')?.value;
        const professionalFilter = document.querySelector('[data-filter="professional"]')?.value;
        const dateFilter = document.querySelector('[data-filter="date"]')?.value;
        
        if (statusFilter) {
            filtered = filtered.filter(a => a.status === statusFilter);
        }
        
        if (professionalFilter) {
            filtered = filtered.filter(a => a.professional_id == professionalFilter);
        }
        
        if (dateFilter) {
            filtered = filtered.filter(a => a.appointment_date === dateFilter);
        }
        
        // Sort by date and time
        filtered.sort((a, b) => {
            const dateCompare = new Date(a.appointment_date) - new Date(b.appointment_date);
            if (dateCompare !== 0) return dateCompare;
            return a.start_time.localeCompare(b.start_time);
        });
        
        return filtered;
    }

    applyFilters() {
        this.renderAppointmentsList();
    }

    updateUI() {
        this.renderCalendar();
        this.renderAppointmentsList();
        this.updateStats();
    }

    updateStats() {
        const stats = {
            total: this.appointments.length,
            pending: this.appointments.filter(a => a.status === 'pending').length,
            confirmed: this.appointments.filter(a => a.status === 'confirmed').length,
            completed: this.appointments.filter(a => a.status === 'completed').length,
            cancelled: this.appointments.filter(a => a.status === 'cancelled').length,
            today: this.appointments.filter(a => a.appointment_date === new Date().toISOString().split('T')[0]).length
        };

        // Update stat cards
        Object.keys(stats).forEach(key => {
            const element = document.querySelector(`[data-stat="${key}"]`);
            if (element) {
                element.textContent = stats[key];
            }
        });
    }

    // Helper methods
    getPatientName(patientId) {
        const patient = this.patients.find(p => p.id == patientId);
        return patient ? `${patient.nombres} ${patient.apellidos}` : 'Paciente no encontrado';
    }

    getProfessionalName(professionalId) {
        const professional = this.professionals.find(p => p.id == professionalId);
        return professional ? professional.name : 'Profesional no encontrado';
    }

    getRoomName(roomId) {
        const room = this.rooms.find(r => r.id == roomId);
        return room ? room.name : 'Consultorio no encontrado';
    }

    getStatusLabel(status) {
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

    getStatusColor(status) {
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

    getTypeLabel(type) {
        const labels = {
            'primera': 'Primera Vez',
            'seguimiento': 'Seguimiento',
            'evaluacion': 'Evaluación',
            'grupal': 'Grupal',
            'emergencia': 'Emergencia'
        };
        return labels[type] || type;
    }

    getModalityLabel(modality) {
        const labels = {
            'presencial': 'Presencial',
            'virtual': 'Virtual',
            'mixta': 'Mixta'
        };
        return labels[modality] || modality;
    }
}

// Global instance
let appointmentManager;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('appointmentsList') || document.getElementById('calendar')) {
        appointmentManager = new AppointmentManager();
    }
});

// Make globally available
window.appointmentManager = appointmentManager;
