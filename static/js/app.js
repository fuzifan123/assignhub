    const { createApp, ref, computed, onMounted, nextTick, watch } = Vue;

        createApp({
            setup() {
                // Auth State
                const isLoggedIn = ref(!!localStorage.getItem('token'));
                const user = ref(JSON.parse(localStorage.getItem('user') || '{}'));
                const token = ref(localStorage.getItem('token'));
                const isRegisterMode = ref(false);
                const authForm = ref({ email: '', password: '' });
                
                // App State
                const currentView = ref('dashboard');
                const loading = ref(false);
                const dashboard = ref({ courses: [], upcoming_tasks: [] });
                const courses = ref([]);
                const tasks = ref([]);
                const notifications = ref([]);
                
                const statsData = ref(null);
                const searchQuery = ref('');
                const profileForm = ref({ email: '', first_name: '', last_name: '' });
                const passwordForm = ref({ old_password: '', new_password: '' });

                const searchResults = computed(() => {
                if (!searchQuery.value.trim()) return [];
                const q = searchQuery.value.toLowerCase();
                return tasks.value.filter(t =>
                t.title.toLowerCase().includes(q) ||
                (t.description && t.description.toLowerCase().includes(q))
                );
                });

                // Filters
                const filters = ref({
                    course_id: null,
                    status: null,
                    sort_by: 'deadline',
                    order: 'asc'
                });

                // Modals
                const courseModal = ref({ show: false, isEdit: false, form: { name: '' }, id: null });
                const taskModal = ref({ show: false, isEdit: false, form: { title: '', course_id: '', deadline: '', status: 'todo' }, id: null });

                // Axios Config
                const api = axios.create({ baseURL: '/api' });
                api.interceptors.request.use(config => {
                    const savedToken = localStorage.getItem('token');
                    if (token.value || savedToken) {
                        config.headers.Authorization = `Bearer ${token.value || savedToken}`;
                    }
                    return config;
                });

                // Computed
                const stats = computed(() => {
                    return {
                        completedTasks: tasks.value.filter(t => t.status === 'done').length
                    };
                });

                const filteredTasks = computed(() => {
                    let result = [...tasks.value];
                    if (filters.value.course_id) result = result.filter(t => t.course_id == filters.value.course_id);
                    if (filters.value.status) result = result.filter(t => t.status === filters.value.status);
                    
                    result.sort((a, b) => {
                        const valA = new Date(a[filters.value.sort_by]);
                        const valB = new Date(b[filters.value.sort_by]);
                        return filters.value.order === 'asc' ? valA - valB : valB - valA;
                    });
                    return result;
                });

                // Methods
                const notify = (text, type = 'success') => {
                    const id = Date.now();
                    notifications.value.push({ id, text, type });
                    setTimeout(() => {
                        notifications.value = notifications.value.filter(n => n.id !== id);
                    }, 3000);
                };

                const handleAuth = async () => {
                    loading.value = true;
                    try {
                        const endpoint = isRegisterMode.value ? '/register' : '/login';
                        const res = await api.post(endpoint, authForm.value);
                        
                        // Handle simple_jwt response (access/refresh)
                        // If token is direct access token (FastAPI style) or object with access (Django style)
                        const accessToken = res.data.access || res.data.token;
                        
                        if (!accessToken) throw new Error("Invalid token received");

                        token.value = accessToken;
                        user.value = { email: authForm.value.email, id: res.data.id }; // Assuming ID comes back or we need to decode
                        
                        // If user info is not in response, we might need to fetch it or decode token
                        if (res.data.email) user.value.email = res.data.email;
                        
                        localStorage.setItem('token', token.value);
                        localStorage.setItem('user', JSON.stringify(user.value));
                        isLoggedIn.value = true;
                        notify(isRegisterMode.value ? 'Registration successful!' : 'Welcome back!');
                        fetchDashboard();
                        fetchCourses();
                        fetchTasks();
                    } catch (err) {
                        console.error(err);
                        let errorMsg = 'Authentication failed';
                        if (err.response?.data) {
                            // Django DRF errors can be object with field keys
                            const data = err.response.data;
                            if (data.detail) {
                                errorMsg = data.detail;
                            } else {
                                // Join all error messages
                                errorMsg = Object.values(data).flat().join(', ');
                            }
                        }
                        notify(errorMsg, 'error');
                    } finally {
                        loading.value = false;
                    }
                };

                const logout = () => {
                    localStorage.removeItem('token');
                    localStorage.removeItem('user');
                    isLoggedIn.value = false;
                };
                
                const fetchStats = async () => {
                    try {
                        const res = await api.get('/stats');
                        statsData.value = res.data;
                    } catch (err) { console.error(err); }
                };

                const fetchProfile = async () => {
                    try {
                        const res = await api.get('/profile');
                        profileForm.value = res.data;
                    } catch (err) { console.error(err); }
                };

                const saveProfile = async () => {
                    try {
                        await api.put('/profile', {
                        first_name: profileForm.value.first_name,
                        last_name: profileForm.value.last_name
                    });
                    notify('Profile updated successfully');
                } catch (err) { notify('Update failed', 'error'); }
                };

                const changePassword = async () => {
                    try {
                        await api.post('/change-password', passwordForm.value);
                        notify('Password changed successfully');
                        passwordForm.value = { old_password: '', new_password: '' };
                    } catch (err) {
                    const msg = err.response?.data?.detail || 'Failed to change password';
                    notify(msg, 'error');
                    }
                };

                const fetchDashboard = async () => {
                    try {
                        const res = await api.get('/dashboard');
                        dashboard.value = res.data;
                        nextTick(() => lucide.createIcons());
                    } catch (err) { console.error(err); }
                };

                const fetchCourses = async () => {
                    try {
                        const res = await api.get('/courses');
                        courses.value = res.data;
                        nextTick(() => lucide.createIcons());
                    } catch (err) { console.error(err); }
                };

                const fetchTasks = async () => {
                    try {
                        const res = await api.get('/tasks');
                        tasks.value = res.data;
                        nextTick(() => lucide.createIcons());
                    } catch (err) { console.error(err); }
                };

                // Course CRUD
                const openCourseModal = (course = null) => {
                    courseModal.value = {
                        show: true,
                        isEdit: !!course,
                        form: { name: course ? course.name : '' },
                        id: course ? course.id : null
                    };
                };

                const saveCourse = async () => {
                    try {
                        if (courseModal.value.isEdit) {
                            await api.put(`/courses/${courseModal.value.id}`, courseModal.value.form);
                        } else {
                            await api.post('/courses', courseModal.value.form);
                        }
                        notify('Course saved successfully');
                        courseModal.value.show = false;
                        fetchCourses();
                        fetchDashboard();
                    } catch (err) { notify('Operation failed', 'error'); }
                };

                const deleteCourse = async (id) => {
                    if (!confirm('Are you sure you want to delete this course? All related tasks will also be deleted.')) return;
                    try {
                        await api.delete(`/courses/${id}`);
                        notify('Course deleted successfully');
                        fetchCourses();
                        fetchTasks();
                        fetchDashboard();
                    } catch (err) { notify('Delete failed', 'error'); }
                };

                // Task CRUD
                const openTaskModal = (task = null) => {
                    if (courses.value.length === 0) {
                        notify('Please create a course first', 'error');
                        return;
                    }
                    taskModal.value = {
                        show: true,
                        isEdit: !!task,
                        form: { 
                            title: task ? task.title : '', 
                            course_id: task ? task.course_id : courses.value[0].id,
                            deadline: task ? task.deadline.substring(0, 16) : '',
                            status: task ? task.status : 'todo'
                        },
                        id: task ? task.id : null
                    };
                    
                    // Initialize Flatpickr after modal is rendered
                    nextTick(() => {
                        flatpickr("#deadline-picker", {
                            enableTime: true,
                            dateFormat: "Y-m-d H:i",
                            defaultDate: taskModal.value.form.deadline,
                            onChange: (selectedDates, dateStr) => {
                                taskModal.value.form.deadline = dateStr;
                            }
                        });
                    });
                };

                const saveTask = async () => {
                    try {
                        const payload = { ...taskModal.value.form };
                        // Convert to ISO string for backend
                        payload.deadline = new Date(payload.deadline).toISOString();
                        
                        if (taskModal.value.isEdit) {
                            await api.put(`/tasks/${taskModal.value.id}`, payload);
                        } else {
                            await api.post('/tasks', payload);
                        }
                        notify('Task saved successfully');
                        taskModal.value.show = false;
                        fetchTasks();
                        fetchDashboard();
                    } catch (err) { notify('Operation failed', 'error'); }
                };

                const updateTaskStatus = async (id, status) => {
                    try {
                        await api.patch(`/tasks/${id}/status`, { status });
                        notify('Status updated successfully');
                        fetchTasks();
                        fetchDashboard();
                    } catch (err) { notify('Update failed', 'error'); }
                };

                const deleteTask = async (id) => {
                    if (!confirm('Are you sure you want to delete this task?')) return;
                    try {
                        await api.delete(`/tasks/${id}`);
                        notify('Task deleted successfully');
                        fetchTasks();
                        fetchDashboard();
                    } catch (err) { notify('Delete failed', 'error'); }
                };

                // Helpers
                const formatDate = (dateStr) => {
                    if (!dateStr) return '';
                    const date = new Date(dateStr);
                    return date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
                };

                const formatDateSimple = (dateStr) => {
                    if (!dateStr) return '';
                    return new Date(dateStr).toLocaleDateString('en-US');
                };

                const getStatusColor = (status) => {
                    switch (status) {
                        case 'todo': return 'bg-amber-400';
                        case 'doing': return 'bg-indigo-400';
                        case 'done': return 'bg-emerald-400';
                        default: return 'bg-gray-400';
                    }
                };

                const getStatusBadge = (status) => {
                    switch (status) {
                        case 'todo': return 'bg-amber-50 text-amber-700 border border-amber-100';
                        case 'doing': return 'bg-indigo-50 text-indigo-700 border border-indigo-100';
                        case 'done': return 'bg-emerald-50 text-emerald-700 border border-emerald-100';
                        default: return 'bg-gray-50 text-gray-700 border border-gray-100';
                    }
                };

                const isOverdue = (deadline) => {
                    return new Date(deadline) < new Date();
                };

                const isUrgent = (deadline) => {
                    const diff = new Date(deadline) - new Date();
                    return diff > 0 && diff < 7 * 24 * 60 * 60 * 1000;
                };

                const getCountdown = (deadline) => {
                    const diff = new Date(deadline) - new Date();
                    if (diff <= 0) return 'Overdue';
                    
                    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
                    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    
                    return `${days}d ${hours}h`;
                };

                onMounted(() => {
                    if (isLoggedIn.value) {
                        fetchDashboard();
                        fetchCourses();
                        fetchTasks();
                    }
                    lucide.createIcons();
                });

                watch(currentView, (newView) => {
                    nextTick(() => lucide.createIcons());
                    if (newView === 'stats') fetchStats();
                    if (newView === 'profile') fetchProfile();
                });

                watch(() => courseModal.value.show, (newVal) => {
                    if (newVal) nextTick(() => lucide.createIcons());
                });

                watch(() => taskModal.value.show, (newVal) => {
                    if (newVal) nextTick(() => lucide.createIcons());
                });

                watch(isLoggedIn, (newVal) => {
                    if (newVal) {
                        nextTick(() => lucide.createIcons());
                    }
                });

                return {
                    isLoggedIn, user, isRegisterMode, authForm, loading,
                    currentView, dashboard, courses, tasks, stats, filters, filteredTasks,
                    courseModal, taskModal, notifications,
                    handleAuth, logout, openCourseModal, saveCourse, deleteCourse,
                    openTaskModal, saveTask, updateTaskStatus, deleteTask,
                    formatDate, formatDateSimple, getStatusColor, getStatusBadge,
                    isOverdue, isUrgent, getCountdown,
                    statsData, searchQuery, searchResults,
                    profileForm, passwordForm,
                    saveProfile, changePassword, fetchStats
                };
            }
        }).mount('#app');
    