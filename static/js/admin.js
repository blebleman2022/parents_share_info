// 管理员后台JavaScript
const { createApp } = Vue;

new Vue({
    el: '#app',
    data() {
        return {
            // 登录状态
            isLoggedIn: false,
            currentUser: null,
            token: localStorage.getItem('admin_token'),
            
            // 登录表单
            loginForm: {
                phone: '',
                password: ''
            },
            loginRules: {
                phone: [
                    { required: true, message: '请输入手机号', trigger: 'blur' },
                    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
                ],
                password: [
                    { required: true, message: '请输入密码', trigger: 'blur' }
                ]
            },
            loginLoading: false,
            
            // 菜单
            activeMenu: 'dashboard',
            menuTitles: {
                dashboard: '数据概览',
                configs: '系统配置',
                users: '用户管理',
                resources: '资源管理',
                logs: '操作日志'
            },
            
            // 统计数据
            stats: {},
            
            // 系统配置
            configs: [],
            pointRulesConfig: null,
            userLevelsConfig: null,
            systemSettingsConfig: null,
            otherConfigs: [],

            // 积分规则配置对话框
            pointRulesDialog: {
                visible: false,
                loading: false
            },
            pointRulesForm: {
                register_points: 100,
                upload_points: 20,
                download_cost: 5,
                daily_signin_points: 10,
                daily_download_limit: 10
            },

            // 用户等级配置对话框
            userLevelsDialog: {
                visible: false,
                loading: false
            },
            userLevelsFormList: [],

            // 系统设置配置对话框
            systemSettingsDialog: {
                visible: false,
                loading: false
            },
            systemSettingsForm: {
                max_file_size: 52428800,
                allowed_file_types: ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'jpg', 'png'],
                auto_approve_resources: true,
                maintenance_mode: false
            },

            // 自定义配置对话框
            configDialog: {
                visible: false,
                title: '',
                isEdit: false,
                loading: false
            },
            configForm: {
                config_key: '',
                description: '',
                config_value: {}
            },
            configValueText: '',
            configRules: {
                config_key: [
                    { required: true, message: '请输入配置键', trigger: 'blur' }
                ],
                description: [
                    { required: true, message: '请输入配置描述', trigger: 'blur' }
                ]
            },
            
            // 用户管理
            users: [],
            userSearch: {
                keyword: ''
            },
            userPagination: {
                page: 1,
                size: 20,
                total: 0
            },
            userDialog: {
                visible: false,
                loading: false
            },
            userForm: {
                id: null,
                points: 0,
                level: '',
                is_active: true
            },
            
            // 资源管理
            resources: [],
            resourceSearch: {
                keyword: ''
            },
            resourcePagination: {
                page: 1,
                size: 20,
                total: 0
            },
            resourceDialog: {
                visible: false,
                loading: false
            },
            resourceForm: {
                id: null,
                title: '',
                description: '',
                grade: '',
                subject: '',
                is_active: true
            },
            
            // 操作日志
            logs: [],
            logPagination: {
                page: 1,
                size: 20,
                total: 0
            }
        };
    },
    
    mounted() {
        // 设置axios默认配置
        axios.defaults.baseURL = '/api/v1';
        
        // 如果有token，尝试验证登录状态
        if (this.token) {
            this.checkLoginStatus();
        }
    },
    
    methods: {
        // ==================== 认证相关 ====================
        
        async login() {
            this.$refs.loginForm.validate(async (valid) => {
                if (!valid) return;
                
                this.loginLoading = true;
                try {
                    const response = await axios.post('/auth/login', this.loginForm);
                    
                    // 检查是否为管理员账号
                    if (this.loginForm.phone !== '13901119451') {
                        this.$message.error('无权限访问管理员后台');
                        return;
                    }
                    
                    this.token = response.data.access_token;
                    localStorage.setItem('admin_token', this.token);
                    
                    // 设置axios默认header
                    axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
                    
                    await this.getCurrentUser();
                    this.isLoggedIn = true;
                    this.activeMenu = 'dashboard';
                    await this.loadDashboardData();
                    
                    this.$message.success('登录成功');
                } catch (error) {
                    console.error('登录失败:', error);
                    this.$message.error(error.response?.data?.detail || '登录失败');
                } finally {
                    this.loginLoading = false;
                }
            });
        },
        
        async checkLoginStatus() {
            try {
                axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
                await this.getCurrentUser();
                
                // 检查是否为管理员
                if (this.currentUser.phone !== '13901119451') {
                    throw new Error('无管理员权限');
                }
                
                this.isLoggedIn = true;
                await this.loadDashboardData();
            } catch (error) {
                console.error('验证登录状态失败:', error);
                this.logout();
            }
        },
        
        async getCurrentUser() {
            const response = await axios.get('/auth/me');
            this.currentUser = response.data;
        },
        
        logout() {
            this.isLoggedIn = false;
            this.currentUser = null;
            this.token = null;
            localStorage.removeItem('admin_token');
            delete axios.defaults.headers.common['Authorization'];
            
            // 重置表单
            this.loginForm = { phone: '', password: '' };
            this.$message.success('已退出登录');
        },
        
        // ==================== 菜单导航 ====================
        
        async handleMenuSelect(index) {
            this.activeMenu = index;
            
            switch (index) {
                case 'dashboard':
                    await this.loadDashboardData();
                    break;
                case 'configs':
                    await this.loadConfigs();
                    break;
                case 'users':
                    await this.loadUsers();
                    break;
                case 'resources':
                    await this.loadResources();
                    break;
                case 'logs':
                    await this.loadLogs();
                    break;
            }
        },
        
        // ==================== 数据概览 ====================
        
        async loadDashboardData() {
            try {
                // 这里应该调用统计API，暂时使用模拟数据
                this.stats = {
                    total_users: 156,
                    active_users: 142,
                    total_resources: 89,
                    total_downloads: 1234,
                    today_uploads: 12,
                    today_downloads: 67
                };
            } catch (error) {
                console.error('加载统计数据失败:', error);
                this.$message.error('加载统计数据失败');
            }
        },
        
        // ==================== 系统配置管理 ====================
        
        async loadConfigs() {
            try {
                const response = await axios.get('/admin/configs');
                this.configs = response.data;

                // 解析不同类型的配置
                this.pointRulesConfig = null;
                this.userLevelsConfig = null;
                this.systemSettingsConfig = null;
                this.otherConfigs = [];

                for (const config of this.configs) {
                    if (config.config_key.includes('point_rules')) {
                        this.pointRulesConfig = config.config_value;
                    } else if (config.config_key.includes('user_levels')) {
                        this.userLevelsConfig = config.config_value;
                    } else if (config.config_key.includes('system_settings')) {
                        this.systemSettingsConfig = config.config_value;
                    } else if (
                        // 过滤掉这些应该删除的独立配置项
                        config.config_key === 'allowed_file_types' ||
                        config.config_key === 'demo_config' ||
                        config.config_key === 'max_file_size' ||
                        config.config_key === 'ui_test_config'
                    ) {
                        // 跳过这些配置项，不显示在界面上
                        continue;
                    } else {
                        this.otherConfigs.push(config);
                    }
                }

                // 如果没有找到主要配置，使用默认值
                if (!this.pointRulesConfig) {
                    this.pointRulesConfig = {
                        register_points: 100,
                        upload_points: 20,
                        download_cost: 5,
                        daily_signin_points: 10,
                        daily_download_limit: 10
                    };
                }

                if (!this.userLevelsConfig) {
                    this.userLevelsConfig = {
                        "新手用户": {"min_points": 0, "max_points": 499, "daily_downloads": 5},
                        "活跃用户": {"min_points": 500, "max_points": 1999, "daily_downloads": 10},
                        "资深用户": {"min_points": 2000, "max_points": 4999, "daily_downloads": 15},
                        "专家用户": {"min_points": 5000, "max_points": -1, "daily_downloads": 20}
                    };
                }

                if (!this.systemSettingsConfig) {
                    this.systemSettingsConfig = {
                        max_file_size: 52428800,
                        allowed_file_types: ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'jpg', 'png'],
                        auto_approve_resources: true,
                        maintenance_mode: false
                    };
                }

            } catch (error) {
                console.error('加载配置失败:', error);
                this.$message.error('加载配置失败');
            }
        },
        
        showConfigDialog(config = null) {
            if (config) {
                this.configDialog.title = '编辑配置';
                this.configDialog.isEdit = true;
                this.configForm = {
                    id: config.id,
                    config_key: config.config_key,
                    description: config.description,
                    config_value: config.config_value
                };
                this.configValueText = JSON.stringify(config.config_value, null, 2);
            } else {
                this.configDialog.title = '新增配置';
                this.configDialog.isEdit = false;
                this.configForm = {
                    config_key: '',
                    description: '',
                    config_value: {}
                };
                this.configValueText = '{}';
            }
            this.configDialog.visible = true;
        },
        
        // ==================== 专门的配置编辑方法 ====================

        editPointRules() {
            // 复制当前配置到表单
            this.pointRulesForm = { ...this.pointRulesConfig };
            this.pointRulesDialog.visible = true;
        },

        async savePointRules() {
            this.pointRulesDialog.loading = true;
            try {
                // 找到积分规则配置项
                const pointRulesConfig = this.configs.find(c => c.config_key.includes('point_rules'));

                if (pointRulesConfig) {
                    // 更新现有配置
                    await axios.put(`/admin/configs/${pointRulesConfig.id}`, {
                        config_value: this.pointRulesForm,
                        description: pointRulesConfig.description
                    });
                } else {
                    // 创建新配置
                    await axios.post('/admin/configs', {
                        config_key: 'point_rules_admin',
                        config_value: this.pointRulesForm,
                        description: '积分规则配置'
                    });
                }

                this.$message.success('积分规则配置保存成功');
                this.pointRulesDialog.visible = false;
                await this.loadConfigs();
            } catch (error) {
                console.error('保存积分规则配置失败:', error);
                this.$message.error(error.response?.data?.detail || '保存积分规则配置失败');
            } finally {
                this.pointRulesDialog.loading = false;
            }
        },

        editUserLevels() {
            // 将用户等级配置转换为表单数组
            this.userLevelsFormList = [];
            for (const [name, config] of Object.entries(this.userLevelsConfig)) {
                this.userLevelsFormList.push({
                    name: name,
                    min_points: config.min_points,
                    max_points: config.max_points,
                    daily_downloads: config.daily_downloads
                });
            }
            this.userLevelsDialog.visible = true;
        },

        addLevelConfig() {
            this.userLevelsFormList.push({
                name: '新等级',
                min_points: 0,
                max_points: 999,
                daily_downloads: 5
            });
        },

        removeLevelConfig(index) {
            this.userLevelsFormList.splice(index, 1);
        },

        async saveUserLevels() {
            this.userLevelsDialog.loading = true;
            try {
                // 将表单数组转换为配置对象
                const levelsConfig = {};
                for (const level of this.userLevelsFormList) {
                    if (level.name.trim()) {
                        levelsConfig[level.name] = {
                            min_points: level.min_points,
                            max_points: level.max_points,
                            daily_downloads: level.daily_downloads
                        };
                    }
                }

                // 找到用户等级配置项
                const userLevelsConfig = this.configs.find(c => c.config_key.includes('user_levels'));

                if (userLevelsConfig) {
                    // 更新现有配置
                    await axios.put(`/admin/configs/${userLevelsConfig.id}`, {
                        config_value: levelsConfig,
                        description: userLevelsConfig.description
                    });
                } else {
                    // 创建新配置
                    await axios.post('/admin/configs', {
                        config_key: 'user_levels_admin',
                        config_value: levelsConfig,
                        description: '用户等级配置'
                    });
                }

                this.$message.success('用户等级配置保存成功');
                this.userLevelsDialog.visible = false;
                await this.loadConfigs();
            } catch (error) {
                console.error('保存用户等级配置失败:', error);
                this.$message.error(error.response?.data?.detail || '保存用户等级配置失败');
            } finally {
                this.userLevelsDialog.loading = false;
            }
        },

        editSystemSettings() {
            // 复制当前配置到表单
            this.systemSettingsForm = { ...this.systemSettingsConfig };
            this.systemSettingsDialog.visible = true;
        },

        async saveSystemSettings() {
            this.systemSettingsDialog.loading = true;
            try {
                // 找到系统设置配置项
                const systemSettingsConfig = this.configs.find(c => c.config_key.includes('system_settings'));

                if (systemSettingsConfig) {
                    // 更新现有配置
                    await axios.put(`/admin/configs/${systemSettingsConfig.id}`, {
                        config_value: this.systemSettingsForm,
                        description: systemSettingsConfig.description
                    });
                } else {
                    // 创建新配置
                    await axios.post('/admin/configs', {
                        config_key: 'system_settings_admin',
                        config_value: this.systemSettingsForm,
                        description: '系统基础设置'
                    });
                }

                this.$message.success('系统设置配置保存成功');
                this.systemSettingsDialog.visible = false;
                await this.loadConfigs();
            } catch (error) {
                console.error('保存系统设置配置失败:', error);
                this.$message.error(error.response?.data?.detail || '保存系统设置配置失败');
            } finally {
                this.systemSettingsDialog.loading = false;
            }
        },

        editOtherConfig(config) {
            this.showConfigDialog(config);
        },

        async deleteConfig(config) {
            try {
                await this.$confirm('确定要删除这个配置吗？', '确认删除', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                });

                // 这里应该调用删除API，但当前后端没有删除接口
                // 暂时只是提示
                this.$message.info('删除功能暂未实现');

            } catch (error) {
                if (error !== 'cancel') {
                    console.error('删除配置失败:', error);
                    this.$message.error('删除配置失败');
                }
            }
        },

        editConfig(config) {
            this.showConfigDialog(config);
        },
        
        async saveConfig() {
            this.$refs.configForm.validate(async (valid) => {
                if (!valid) return;
                
                try {
                    // 解析JSON配置值
                    this.configForm.config_value = JSON.parse(this.configValueText);
                } catch (error) {
                    this.$message.error('配置值必须是有效的JSON格式');
                    return;
                }
                
                this.configDialog.loading = true;
                try {
                    if (this.configDialog.isEdit) {
                        await axios.put(`/admin/configs/${this.configForm.id}`, {
                            config_value: this.configForm.config_value,
                            description: this.configForm.description
                        });
                        this.$message.success('配置更新成功');
                    } else {
                        await axios.post('/admin/configs', this.configForm);
                        this.$message.success('配置创建成功');
                    }
                    
                    this.configDialog.visible = false;
                    await this.loadConfigs();
                } catch (error) {
                    console.error('保存配置失败:', error);
                    this.$message.error(error.response?.data?.detail || '保存配置失败');
                } finally {
                    this.configDialog.loading = false;
                }
            });
        },
        
        // ==================== 用户管理 ====================
        
        async loadUsers() {
            try {
                const params = {
                    page: this.userPagination.page,
                    size: this.userPagination.size
                };
                
                if (this.userSearch.keyword) {
                    params.keyword = this.userSearch.keyword;
                }
                
                const response = await axios.get('/admin/users', { params });
                this.users = response.data;
                // 这里应该从响应头或其他地方获取总数，暂时使用估算
                this.userPagination.total = this.users.length >= this.userPagination.size ? 
                    this.userPagination.page * this.userPagination.size + 1 : 
                    (this.userPagination.page - 1) * this.userPagination.size + this.users.length;
            } catch (error) {
                console.error('加载用户失败:', error);
                this.$message.error('加载用户失败');
            }
        },
        
        editUser(user) {
            this.userForm = {
                id: user.id,
                points: user.points,
                level: user.level,
                is_active: user.is_active
            };
            this.userDialog.visible = true;
        },
        
        async saveUser() {
            this.userDialog.loading = true;
            try {
                await axios.put(`/admin/users/${this.userForm.id}`, {
                    points: this.userForm.points,
                    level: this.userForm.level,
                    is_active: this.userForm.is_active
                });
                
                this.$message.success('用户信息更新成功');
                this.userDialog.visible = false;
                await this.loadUsers();
            } catch (error) {
                console.error('更新用户失败:', error);
                this.$message.error(error.response?.data?.detail || '更新用户失败');
            } finally {
                this.userDialog.loading = false;
            }
        },
        
        handleUserPageChange(page) {
            this.userPagination.page = page;
            this.loadUsers();
        },
        
        // ==================== 资源管理 ====================
        
        async loadResources() {
            try {
                const params = {
                    page: this.resourcePagination.page,
                    size: this.resourcePagination.size
                };
                
                if (this.resourceSearch.keyword) {
                    params.keyword = this.resourceSearch.keyword;
                }
                
                const response = await axios.get('/admin/resources', { params });
                this.resources = response.data;
                // 估算总数
                this.resourcePagination.total = this.resources.length >= this.resourcePagination.size ? 
                    this.resourcePagination.page * this.resourcePagination.size + 1 : 
                    (this.resourcePagination.page - 1) * this.resourcePagination.size + this.resources.length;
            } catch (error) {
                console.error('加载资源失败:', error);
                this.$message.error('加载资源失败');
            }
        },
        
        editResource(resource) {
            this.resourceForm = {
                id: resource.id,
                title: resource.title,
                description: resource.description,
                grade: resource.grade,
                subject: resource.subject,
                is_active: resource.is_active
            };
            this.resourceDialog.visible = true;
        },
        
        async saveResource() {
            this.resourceDialog.loading = true;
            try {
                await axios.put(`/admin/resources/${this.resourceForm.id}`, {
                    title: this.resourceForm.title,
                    description: this.resourceForm.description,
                    grade: this.resourceForm.grade,
                    subject: this.resourceForm.subject,
                    is_active: this.resourceForm.is_active
                });
                
                this.$message.success('资源信息更新成功');
                this.resourceDialog.visible = false;
                await this.loadResources();
            } catch (error) {
                console.error('更新资源失败:', error);
                this.$message.error(error.response?.data?.detail || '更新资源失败');
            } finally {
                this.resourceDialog.loading = false;
            }
        },
        
        async deleteResource(resource) {
            try {
                await this.$confirm('确定要删除这个资源吗？', '确认删除', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                });
                
                await axios.delete(`/admin/resources/${resource.id}`);
                this.$message.success('资源删除成功');
                await this.loadResources();
            } catch (error) {
                if (error !== 'cancel') {
                    console.error('删除资源失败:', error);
                    this.$message.error(error.response?.data?.detail || '删除资源失败');
                }
            }
        },
        
        handleResourcePageChange(page) {
            this.resourcePagination.page = page;
            this.loadResources();
        },
        
        // ==================== 操作日志 ====================
        
        async loadLogs() {
            try {
                const params = {
                    page: this.logPagination.page,
                    size: this.logPagination.size
                };
                
                const response = await axios.get('/admin/logs', { params });
                this.logs = response.data;
                // 估算总数
                this.logPagination.total = this.logs.length >= this.logPagination.size ? 
                    this.logPagination.page * this.logPagination.size + 1 : 
                    (this.logPagination.page - 1) * this.logPagination.size + this.logs.length;
            } catch (error) {
                console.error('加载日志失败:', error);
                this.$message.error('加载日志失败');
            }
        },
        
        handleLogPageChange(page) {
            this.logPagination.page = page;
            this.loadLogs();
        },
        
        // ==================== 工具方法 ====================
        
        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleString('zh-CN');
        },

        formatFileSize(bytes) {
            if (!bytes) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
        }
    }
});
