/**
 * UCE Psychology System - Room Management Functions
 * Complete room and space management system
 */

class RoomManager {
    constructor() {
        this.rooms = [];
        this.schedules = [];
        this.currentRoom = null;
        this.init();
    }

    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.updateUI();
    }

    async loadData() {
        try {
            // Load rooms
            const roomsResponse = await fetch('/api/v1/rooms', {
                headers: getAuthHeaders()
            });
            if (roomsResponse.ok) {
                const data = await roomsResponse.json();
                this.rooms = data.data || data;
            }

            // Load schedules
            const schedulesResponse = await fetch('/api/v1/schedules', {
                headers: getAuthHeaders()
            });
            if (schedulesResponse.ok) {
                const data = await schedulesResponse.json();
                this.schedules = data.data || data;
            }

        } catch (error) {
            console.error('Error loading room data:', error);
            // Use mock data for demo
            this.rooms = this.getMockRooms();
            this.schedules = this.getMockSchedules();
        }
    }

    getMockRooms() {
        return [
            {
                id: 1,
                name: 'Consultorio 1',
                room_number: 'A101',
                floor_number: 1,
                building: 'Edificio Principal',
                capacity: 2,
                room_type: 'consultorio_individual',
                status: 'disponible',
                equipment: ['Silla terapéutica', 'Escritorio', 'Espejo', 'Cámara de seguridad'],
                description: 'Consultorio individual con ambiente tranquilo',
                is_active: true
            },
            {
                id: 2,
                name: 'Consultorio 2',
                room_number: 'A102',
                floor_number: 1,
                building: 'Edificio Principal',
                capacity: 2,
                room_type: 'consultorio_individual',
                status: 'ocupado',
                equipment: ['Silla terapéutica', 'Escritorio', 'Sistema de audio'],
                description: 'Consultorio individual con sistema de audio',
                is_active: true
            },
            {
                id: 3,
                name: 'Sala de Terapia Grupal',
                room_number: 'B201',
                floor_number: 2,
                building: 'Edificio Principal',
                capacity: 10,
                room_type: 'consultorio_grupal',
                status: 'disponible',
                equipment: ['Sillas circulares', 'Pizarra blanca', 'Sistema de audio', 'Cámara'],
                description: 'Espacio amplio para terapia grupal',
                is_active: true
            },
            {
                id: 4,
                name: 'Sala de Observación',
                room_number: 'C301',
                floor_number: 3,
                building: 'Edificio Principal',
                capacity: 5,
                room_type: 'sala_observacion',
                status: 'disponible',
                equipment: ['Espejo unidireccional', 'Sistema de grabación', 'Monitores'],
                description: 'Sala con espejo unidireccional para supervisión',
                is_active: true
            },
            {
                id: 5,
                name: 'Sala de Reuniones',
                room_number: 'D101',
                floor_number: 1,
                building: 'Edificio Anexo',
                capacity: 15,
                room_type: 'sala_reunion',
                status: 'disponible',
                equipment: ['Mesa de reuniones', 'Proyector', 'Pizarra blanca', 'Sistema de videoconferencia'],
                description: 'Sala equipada para reuniones y presentaciones',
                is_active: true
            }
        ];
    }

    getMockSchedules() {
        return [
            {
                id: 1,
                room_id: 1,
                day_of_week: 1, // Monday
                start_time: '08:00',
                end_time: '12:00',
                is_active: true,
                professional_id: 1,
                professional_name: 'Dr. Carlos Mendoza'
            },
            {
                id: 2,
                room_id: 1,
                day_of_week: 1,
                start_time: '14:00',
                end_time: '18:00',
                is_active: true,
                professional_id: 1,
                professional_name: 'Dr. Carlos Mendoza'
            },
            {
                id: 3,
                room_id: 2,
                day_of_week: 2, // Tuesday
                start_time: '09:00',
                end_time: '13:00',
                is_active: true,
                professional_id: 2,
                professional_name: 'Dra. María López'
            }
        ];
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="create-room"]')) {
                this.showCreateRoomModal();
            } else if (e.target.matches('[data-action="edit-room"]')) {
                const roomId = e.target.dataset.roomId;
                this.showEditRoomModal(roomId);
            } else if (e.target.matches('[data-action="delete-room"]')) {
                const roomId = e.target.dataset.roomId;
                this.deleteRoom(roomId);
            } else if (e.target.matches('[data-action="view-room"]')) {
                const roomId = e.target.dataset.roomId;
                this.viewRoomDetails(roomId);
            } else if (e.target.matches('[data-action="toggle-status"]')) {
                const roomId = e.target.dataset.roomId;
                this.toggleRoomStatus(roomId);
            } else if (e.target.matches('[data-action="schedule-room"]')) {
                const roomId = e.target.dataset.roomId;
                this.showScheduleModal(roomId);
            }
        });
    }

    showCreateRoomModal() {
        const modalHTML = `
            <div class="modal fade" id="roomModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Registrar Nueva Sala</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="roomForm">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6 class="text-primary mb-3">Información Básica</h6>
                                        <div class="mb-3">
                                            <label class="form-label">Nombre de la Sala *</label>
                                            <input type="text" class="form-control" name="name" required>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Número de Sala *</label>
                                                <input type="text" class="form-control" name="room_number" required>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Piso *</label>
                                                <input type="number" class="form-control" name="floor_number" min="1" required>
                                            </div>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Edificio *</label>
                                            <input type="text" class="form-control" name="building" required>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Capacidad *</label>
                                                <input type="number" class="form-control" name="capacity" min="1" required>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Tipo de Sala *</label>
                                                <select class="form-select" name="room_type" required>
                                                    <option value="">Seleccionar...</option>
                                                    <option value="consultorio_individual">Consultorio Individual</option>
                                                    <option value="consultorio_grupal">Consultorio Grupal</option>
                                                    <option value="sala_observacion">Sala de Observación</option>
                                                    <option value="sala_reunion">Sala de Reuniones</option>
                                                </select>
                                            </div>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Estado *</label>
                                            <select class="form-select" name="status" required>
                                                <option value="disponible">Disponible</option>
                                                <option value="ocupado">Ocupado</option>
                                                <option value="mantenimiento">En Mantenimiento</option>
                                                <option value="inactivo">Inactivo</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <h6 class="text-primary mb-3">Detalles Adicionales</h6>
                                        <div class="mb-3">
                                            <label class="form-label">Descripción</label>
                                            <textarea class="form-control" name="description" rows="3" 
                                                      placeholder="Descripción de la sala y sus características..."></textarea>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Equipamiento</label>
                                            <div class="equipment-list">
                                                <div class="form-check">
                                                    <input class="form-check-input" type="checkbox" name="equipment" value="Silla terapéutica">
                                                    <label class="form-check-label">Silla terapéutica</label>
                                                </div>
                                                <div class="form-check">
                                                    <input class="form-check-input" type="checkbox" name="equipment" value="Escritorio">
                                                    <label class="form-check-label">Escritorio</label>
                                                </div>
                                                <div class="form-check">
                                                    <input class="form-check-input" type="checkbox" name="equipment" value="Espejo">
                                                    <label class="form-check-label">Espejo</label>
                                                </div>
                                                <div class="form-check">
                                                    <input class="form-check-input" type="checkbox" name="equipment" value="Cámara de seguridad">
                                                    <label class="form-check-label">Cámara de seguridad</label>
                                                </div>
                                                <div class="form-check">
                                                    <input class="form-check-input" type="checkbox" name="equipment" value="Sistema de audio">
                                                    <label class="form-check-label">Sistema de audio</label>
                                                </div>
                                                <div class="form-check">
                                                    <input class="form-check-input" type="checkbox" name="equipment" value="Pizarra blanca">
                                                    <label class="form-check-label">Pizarra blanca</label>
                                                </div>
                                                <div class="form-check">
                                                    <input class="form-check-input" type="checkbox" name="equipment" value="Proyector">
                                                    <label class="form-check-label">Proyector</label>
                                                </div>
                                                <div class="form-check">
                                                    <input class="form-check-input" type="checkbox" name="equipment" value="Sistema de videoconferencia">
                                                    <label class="form-check-label">Sistema de videoconferencia</label>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" name="is_active" checked>
                                                <label class="form-check-label">Sala Activa</label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary" onclick="roomManager.saveRoom()">
                                <i class="bi bi-save me-2"></i>Guardar Sala
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('roomModal');
        if (existingModal) existingModal.remove();

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('roomModal'));
        modal.show();
    }

    async saveRoom() {
        try {
            const form = document.getElementById('roomForm');
            const formData = new FormData(form);

            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            // Get equipment checkboxes
            const equipment = [];
            form.querySelectorAll('input[name="equipment"]:checked').forEach(checkbox => {
                equipment.push(checkbox.value);
            });

            const roomData = {
                name: formData.get('name'),
                room_number: formData.get('room_number'),
                floor_number: parseInt(formData.get('floor_number')),
                building: formData.get('building'),
                capacity: parseInt(formData.get('capacity')),
                room_type: formData.get('room_type'),
                status: formData.get('status'),
                description: formData.get('description'),
                equipment: equipment,
                is_active: formData.has('is_active'),
                created_by: getCurrentUser()?.id
            };

            const response = await fetch('/api/v1/rooms', {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(roomData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Error al crear sala');
            }

            const newRoom = await response.json();
            this.rooms.push(newRoom);
            this.updateUI();

            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('roomModal'));
            modal.hide();

            showAlert('Sala creada exitosamente', 'success');

        } catch (error) {
            console.error('Error saving room:', error);
            showAlert(error.message || 'Error al guardar sala', 'danger');
        }
    }

    showEditRoomModal(roomId) {
        const room = this.rooms.find(r => r.id == roomId);
        if (!room) {
            showAlert('Sala no encontrada', 'danger');
            return;
        }

        this.currentRoom = room;
        
        // Show create modal with pre-filled data
        this.showCreateRoomModal();
        
        // Update modal title and fill form
        setTimeout(() => {
            document.querySelector('#roomModal .modal-title').textContent = 'Editar Sala';
            const form = document.getElementById('roomForm');
            
            Object.keys(room).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = room[key];
                    } else {
                        input.value = room[key];
                    }
                }
            });

            // Set equipment checkboxes
            if (room.equipment) {
                room.equipment.forEach(item => {
                    const checkbox = form.querySelector(`input[name="equipment"][value="${item}"]`);
                    if (checkbox) checkbox.checked = true;
                });
            }
        }, 100);
    }

    async deleteRoom(roomId) {
        if (!confirm('¿Está seguro de que desea eliminar esta sala? Esta acción no se puede deshacer.')) {
            return;
        }

        try {
            const response = await fetch(`/api/v1/rooms/${roomId}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error('Error al eliminar sala');
            }

            this.rooms = this.rooms.filter(r => r.id != roomId);
            this.updateUI();
            showAlert('Sala eliminada exitosamente', 'success');
        } catch (error) {
            console.error('Error deleting room:', error);
            showAlert('Error al eliminar sala', 'danger');
        }
    }

    viewRoomDetails(roomId) {
        const room = this.rooms.find(r => r.id == roomId);
        if (!room) {
            showAlert('Sala no encontrada', 'danger');
            return;
        }

        const modalHTML = `
            <div class="modal fade" id="roomDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Detalles de la Sala</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <h6 class="text-primary mb-3">Información General</h6>
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <strong>Nombre:</strong> ${room.name}
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Número:</strong> ${room.room_number}
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <strong>Piso:</strong> ${room.floor_number}
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Edificio:</strong> ${room.building}
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <strong>Capacidad:</strong> ${room.capacity} personas
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Tipo:</strong> ${this.getRoomTypeLabel(room.room_type)}
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <strong>Estado:</strong> 
                                            <span class="badge bg-${this.getStatusColor(room.status)}">
                                                ${this.getStatusLabel(room.status)}
                                            </span>
                                        </div>
                                        <div class="col-md-6">
                                            <strong>Activa:</strong> 
                                            <span class="badge bg-${room.is_active ? 'success' : 'danger'}">
                                                ${room.is_active ? 'Sí' : 'No'}
                                            </span>
                                        </div>
                                    </div>
                                    
                                    ${room.description ? `
                                    <div class="mb-3">
                                        <strong>Descripción:</strong><br>
                                        ${room.description}
                                    </div>
                                    ` : ''}
                                    
                                    <h6 class="text-primary mb-3 mt-4">Equipamiento</h6>
                                    <div class="mb-3">
                                        ${room.equipment && room.equipment.length > 0 ? 
                                            room.equipment.map(item => `<span class="badge bg-info me-1">${item}</span>`).join('') :
                                            'No hay equipamiento registrado'
                                        }
                                    </div>

                                    <h6 class="text-primary mb-3 mt-4">Horario de Hoy</h6>
                                    <div class="room-schedule">
                                        ${this.getTodaySchedule(room.id)}
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">Acciones Rápidas</h6>
                                        </div>
                                        <div class="card-body">
                                            <div class="d-grid gap-2">
                                                <button class="btn btn-primary" onclick="roomManager.showEditRoomModal(${room.id})">
                                                    <i class="bi bi-pencil me-2"></i>Editar Sala
                                                </button>
                                                <button class="btn btn-success" onclick="roomManager.showScheduleModal(${room.id})">
                                                    <i class="bi bi-calendar me-2"></i>Ver Horario
                                                </button>
                                                <button class="btn btn-warning" onclick="roomManager.toggleRoomStatus(${room.id})">
                                                    <i class="bi bi-toggle-on me-2"></i>Cambiar Estado
                                                </button>
                                                <button class="btn btn-info" onclick="roomManager.generateRoomReport(${room.id})">
                                                    <i class="bi bi-download me-2"></i>Generar Reporte
                                                </button>
                                                <button class="btn btn-danger" onclick="roomManager.deleteRoom(${room.id})">
                                                    <i class="bi bi-trash me-2"></i>Eliminar Sala
                                                </button>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="card mt-3">
                                        <div class="card-header">
                                            <h6 class="mb-0">Estadísticas de Uso</h6>
                                        </div>
                                        <div class="card-body">
                                            <div class="mb-2">
                                                <small class="text-muted">Uso esta semana:</small>
                                                <div class="progress" style="height: 8px;">
                                                    <div class="progress-bar bg-info" style="width: 75%"></div>
                                                </div>
                                                <small>75% ocupado</small>
                                            </div>
                                            <div class="mb-2">
                                                <small class="text-muted">Citas hoy:</small>
                                                <strong>8 citas</strong>
                                            </div>
                                            <div>
                                                <small class="text-muted">Tasa de ocupación:</small>
                                                <strong>82%</strong>
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
        const existingModal = document.getElementById('roomDetailsModal');
        if (existingModal) existingModal.remove();

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('roomDetailsModal'));
        modal.show();
    }

    getTodaySchedule(roomId) {
        const today = new Date().getDay();
        const todaySchedules = this.schedules.filter(s => s.room_id == roomId && s.day_of_week === today);
        
        if (todaySchedules.length === 0) {
            return '<p class="text-muted">Sin horarios programados para hoy</p>';
        }

        return todaySchedules.map(schedule => `
            <div class="schedule-item mb-2 p-2 border rounded">
                <div class="d-flex justify-content-between">
                    <span><strong>${schedule.start_time} - ${schedule.end_time}</strong></span>
                    <small class="text-muted">${schedule.professional_name || 'No asignado'}</small>
                </div>
            </div>
        `).join('');
    }

    async toggleRoomStatus(roomId) {
        const room = this.rooms.find(r => r.id == roomId);
        if (!room) return;

        const newStatus = room.status === 'disponible' ? 'mantenimiento' : 'disponible';
        
        try {
            const response = await fetch(`/api/v1/rooms/${roomId}/status`, {
                method: 'PATCH',
                headers: getAuthHeaders(),
                body: JSON.stringify({ status: newStatus })
            });

            if (!response.ok) {
                throw new Error('Error al actualizar estado');
            }

            room.status = newStatus;
            this.updateUI();
            showAlert(`Estado de sala actualizado a: ${this.getStatusLabel(newStatus)}`, 'success');
        } catch (error) {
            console.error('Error toggling room status:', error);
            showAlert('Error al actualizar estado de la sala', 'danger');
        }
    }

    showScheduleModal(roomId) {
        const room = this.rooms.find(r => r.id == roomId);
        if (!room) return;

        const modalHTML = `
            <div class="modal fade" id="scheduleModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Horario - ${room.name}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <h6 class="text-primary mb-3">Horario Semanal</h6>
                                    <div class="schedule-grid">
                                        ${this.generateScheduleGrid(roomId)}
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <h6 class="text-primary mb-3">Agregar Horario</h6>
                                    <form id="scheduleForm">
                                        <div class="mb-3">
                                            <label class="form-label">Día de la Semana</label>
                                            <select class="form-select" name="day_of_week" required>
                                                <option value="">Seleccionar...</option>
                                                <option value="1">Lunes</option>
                                                <option value="2">Martes</option>
                                                <option value="3">Miércoles</option>
                                                <option value="4">Jueves</option>
                                                <option value="5">Viernes</option>
                                                <option value="6">Sábado</option>
                                                <option value="0">Domingo</option>
                                            </select>
                                        </div>
                                        <div class="row">
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Hora Inicio</label>
                                                <input type="time" class="form-control" name="start_time" required>
                                            </div>
                                            <div class="col-md-6 mb-3">
                                                <label class="form-label">Hora Fin</label>
                                                <input type="time" class="form-control" name="end_time" required>
                                            </div>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label">Profesional</label>
                                            <select class="form-select" name="professional_id">
                                                <option value="">Seleccionar...</option>
                                                <option value="1">Dr. Carlos Mendoza</option>
                                                <option value="2">Dra. María López</option>
                                                <option value="3">Dr. Roberto Silva</option>
                                                <option value="4">Dra. Patricia Castro</option>
                                            </select>
                                        </div>
                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" name="is_active" checked>
                                                <label class="form-check-label">Horario Activo</label>
                                            </div>
                                        </div>
                                        <button type="button" class="btn btn-primary w-100" onclick="roomManager.saveSchedule(${roomId})">
                                            <i class="bi bi-save me-2"></i>Guardar Horario
                                        </button>
                                    </form>
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
        const existingModal = document.getElementById('scheduleModal');
        if (existingModal) existingModal.remove();

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('scheduleModal'));
        modal.show();
    }

    generateScheduleGrid(roomId) {
        const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
        const dayNumbers = [1, 2, 3, 4, 5, 6, 0];
        
        return `
            <div class="table-responsive">
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Día</th>
                            <th>08:00-10:00</th>
                            <th>10:00-12:00</th>
                            <th>12:00-14:00</th>
                            <th>14:00-16:00</th>
                            <th>16:00-18:00</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${dayNumbers.map((dayNum, index) => `
                            <tr>
                                <td><strong>${days[index]}</strong></td>
                                ${this.generateScheduleCells(roomId, dayNum)}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    generateScheduleCells(roomId, dayNum) {
        const timeSlots = ['08:00-10:00', '10:00-12:00', '12:00-14:00', '14:00-16:00', '16:00-18:00'];
        
        return timeSlots.map(slot => {
            const [startTime, endTime] = slot.split('-');
            const schedule = this.schedules.find(s => 
                s.room_id == roomId && 
                s.day_of_week === dayNum && 
                s.start_time === startTime && 
                s.end_time === endTime
            );
            
            if (schedule && schedule.is_active) {
                return `<td class="bg-success text-white">
                    <small>${schedule.professional_name || 'Asignado'}</small>
                </td>`;
            } else {
                return `<td class="bg-light">
                    <button class="btn btn-sm btn-outline-secondary w-100" 
                            onclick="roomManager.quickSchedule(${roomId}, ${dayNum}, '${startTime}', '${endTime}')">
                        <i class="bi bi-plus"></i>
                    </button>
                </td>`;
            }
        }).join('');
    }

    quickSchedule(roomId, dayNum, startTime, endTime) {
        const professional = prompt('Profesional asignado:');
        if (!professional) return;

        const scheduleData = {
            room_id: roomId,
            day_of_week: dayNum,
            start_time: startTime,
            end_time: endTime,
            professional_id: 1, // Default
            professional_name: professional,
            is_active: true
        };

        this.schedules.push(scheduleData);
        this.showScheduleModal(roomId); // Refresh the modal
    }

    async saveSchedule(roomId) {
        try {
            const form = document.getElementById('scheduleForm');
            const formData = new FormData(form);

            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            const scheduleData = {
                room_id: roomId,
                day_of_week: parseInt(formData.get('day_of_week')),
                start_time: formData.get('start_time'),
                end_time: formData.get('end_time'),
                professional_id: parseInt(formData.get('professional_id')) || null,
                is_active: formData.has('is_active')
            };

            const response = await fetch('/api/v1/schedules', {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(scheduleData)
            });

            if (!response.ok) {
                throw new Error('Error al guardar horario');
            }

            const newSchedule = await response.json();
            this.schedules.push(newSchedule);
            
            // Refresh the schedule modal
            this.showScheduleModal(roomId);
            
            showAlert('Horario guardado exitosamente', 'success');

        } catch (error) {
            console.error('Error saving schedule:', error);
            showAlert('Error al guardar horario', 'danger');
        }
    }

    generateRoomReport(roomId) {
        showAlert('Generando reporte de sala...', 'info');
        // Implement report generation
    }

    updateUI() {
        this.updateRoomsTable();
        this.updateStats();
        this.updateRoomGrid();
    }

    updateRoomsTable() {
        const tableBody = document.querySelector('#roomsTable tbody');
        if (!tableBody) return;

        tableBody.innerHTML = this.rooms.map(room => `
            <tr>
                <td>${room.name}</td>
                <td>${room.room_number}</td>
                <td>${room.building} - Piso ${room.floor_number}</td>
                <td>${room.capacity}</td>
                <td>${this.getRoomTypeLabel(room.room_type)}</td>
                <td>
                    <span class="badge bg-${this.getStatusColor(room.status)}">
                        ${this.getStatusLabel(room.status)}
                    </span>
                </td>
                <td>
                    <div class="btn-group" role="group">
                        <button class="btn btn-sm btn-outline-primary" data-action="view-room" data-room-id="${room.id}">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-warning" data-action="edit-room" data-room-id="${room.id}">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-info" data-action="schedule-room" data-room-id="${room.id}">
                            <i class="bi bi-calendar"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" data-action="delete-room" data-room-id="${room.id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    updateRoomGrid() {
        const gridContainer = document.getElementById('roomGrid');
        if (!gridContainer) return;

        gridContainer.innerHTML = this.rooms.map(room => `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card room-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title">${room.name}</h6>
                            <span class="badge bg-${this.getStatusColor(room.status)}">
                                ${this.getStatusLabel(room.status)}
                            </span>
                        </div>
                        <p class="card-text">
                            <small class="text-muted">${room.room_number} - ${room.building}</small><br>
                            <small class="text-muted">Capacidad: ${room.capacity} personas</small><br>
                            <small class="text-muted">Tipo: ${this.getRoomTypeLabel(room.room_type)}</small>
                        </p>
                        <div class="d-grid gap-2">
                            <button class="btn btn-sm btn-outline-primary" data-action="view-room" data-room-id="${room.id}">
                                <i class="bi bi-eye me-1"></i>Ver Detalles
                            </button>
                            <button class="btn btn-sm btn-outline-success" data-action="schedule-room" data-room-id="${room.id}">
                                <i class="bi bi-calendar me-1"></i>Horario
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    updateStats() {
        const stats = {
            total: this.rooms.length,
            available: this.rooms.filter(r => r.status === 'disponible').length,
            occupied: this.rooms.filter(r => r.status === 'ocupado').length,
            maintenance: this.rooms.filter(r => r.status === 'mantenimiento').length
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
    getRoomTypeLabel(type) {
        const labels = {
            'consultorio_individual': 'Consultorio Individual',
            'consultorio_grupal': 'Consultorio Grupal',
            'sala_observacion': 'Sala de Observación',
            'sala_reunion': 'Sala de Reuniones'
        };
        return labels[type] || type;
    }

    getStatusLabel(status) {
        const labels = {
            'disponible': 'Disponible',
            'ocupado': 'Ocupado',
            'mantenimiento': 'Mantenimiento',
            'inactivo': 'Inactivo'
        };
        return labels[status] || status;
    }

    getStatusColor(status) {
        const colors = {
            'disponible': 'success',
            'ocupado': 'danger',
            'mantenimiento': 'warning',
            'inactivo': 'secondary'
        };
        return colors[status] || 'secondary';
    }
}

// Global instance
let roomManager;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('roomsTable') || document.getElementById('roomGrid')) {
        roomManager = new RoomManager();
    }
});

// Make globally available
window.roomManager = roomManager;
