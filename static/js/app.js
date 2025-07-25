const { createApp } = Vue;
const { ElMessage, ElMessageBox } = ElementPlus;

createApp({
    data() {
        return {
            // 登录状态
            isLoggedIn: false,
            activeTab: 'login',
            loading: false,
            
            // 用户信息
            userInfo: {},
            
            // 登录表单
            loginForm: {
                phone: '',
                password: ''
            },
            loginRules: {
                phone: [
                    { required: true, message: '请输入手机号', trigger: 'blur' },
                    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
                ],
                password: [
                    { required: true, message: '请输入密码', trigger: 'blur' }
                ]
            },
            
            // 注册表单
            registerForm: {
                phone: '',
                password: '',
                confirm_password: '',
                nickname: '',
                child_grade: ''
            },
            registerRules: {
                phone: [
                    { required: true, message: '请输入手机号', trigger: 'blur' },
                    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
                ],
                password: [
                    { required: true, message: '请输入密码', trigger: 'blur' },
                    { min: 6, max: 20, message: '密码长度为6-20位', trigger: 'blur' }
                ],
                confirm_password: [
                    { required: true, message: '请确认密码', trigger: 'blur' },
                    {
                        validator: (rule, value, callback) => {
                            if (value !== this.registerForm.password) {
                                callback(new Error('两次输入的密码不一致'));
                            } else {
                                callback();
                            }
                        },
                        trigger: 'blur'
                    }
                ],
                nickname: [
                    { required: true, message: '请输入昵称', trigger: 'blur' },
                    { min: 2, max: 20, message: '昵称长度为2-20位', trigger: 'blur' }
                ],
                child_grade: [
                    { required: true, message: '请选择孩子年级', trigger: 'change' }
                ]
            },
            
            // 搜索表单
            searchForm: {
                keyword: '',
                grade: '',
                subject: '',
                resource_type: ''
            },
            
            // 上传表单
            uploadForm: {
                title: '',
                grade: [],
                subject: '',
                resource_type: '',
                description: '',
                file: null
            },
            uploadRules: {
                title: [
                    { required: true, message: '请输入资源标题', trigger: 'blur' }
                ],
                grade: [
                    { required: true, message: '请选择年级', trigger: 'change' }
                ],
                subject: [
                    { required: true, message: '请选择科目', trigger: 'change' }
                ],
                resource_type: [
                    { required: true, message: '请选择资源类别', trigger: 'change' }
                ],
                file: [
                    { required: true, message: '请选择文件', trigger: 'change' }
                ]
            },
            
            // 界面状态
            activeContentTab: 'resources',
            showUploadDialog: false,
            showBountyDialog: false,
            uploading: false,

            // 验证码相关（可选功能）
            enableSmsVerification: false, // 是否启用短信验证码
            codeSending: false,
            countdown: 0,
            
            // 数据
            resources: [],
            
            // 配置选项
            grades: [
                '小学1年级', '小学2年级', '小学3年级', '小学4年级', '小学5年级', '预初',
                '初中1年级', '初中2年级', '初中3年级',
                '高中1年级', '高中2年级', '高中3年级'
            ],
            subjects: ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治'],
            resourceTypes: ['课件', '教案', '学案', '作业', '试卷', '题集', '素材', '备课包', '其他']
        };
    },

    computed: {
        // 小学年级
        primaryGrades() {
            return this.grades.filter(grade => grade.includes('小学'));
        },

        // 初中年级
        middleGrades() {
            return this.grades.filter(grade => grade.includes('初中') || grade === '预初');
        },

        // 高中年级
        highGrades() {
            return this.grades.filter(grade => grade.includes('高中'));
        }
    },

    mounted() {
        // 检查本地存储的token
        const token = localStorage.getItem('token');
        if (token) {
            this.setAuthToken(token);
            this.getCurrentUser();
        }
        
        // 加载资源列表
        this.loadResources();
    },
    
    methods: {
        // 密码确认验证
        validateConfirmPassword(rule, value, callback) {
            if (value !== this.registerForm.password) {
                callback(new Error('两次输入的密码不一致'));
            } else {
                callback();
            }
        },

        // 发送验证码（可选功能）
        /*
        async sendVerificationCode() {
            if (!this.registerForm.phone) {
                ElMessage.error('请先输入手机号');
                return;
            }

            if (!/^1[3-9]\d{9}$/.test(this.registerForm.phone)) {
                ElMessage.error('手机号格式不正确');
                return;
            }

            try {
                this.codeSending = true;

                const response = await axios.post('/api/v1/auth/send-code', {
                    phone: this.registerForm.phone,
                    code_type: 'register'
                });

                ElMessage.success('验证码发送成功');

                // 开始倒计时
                this.countdown = 60;
                const timer = setInterval(() => {
                    this.countdown--;
                    if (this.countdown <= 0) {
                        clearInterval(timer);
                    }
                }, 1000);

            } catch (error) {
                console.error('发送验证码失败:', error);
                ElMessage.error(error.response?.data?.detail || '发送验证码失败');
            } finally {
                this.codeSending = false;
            }
        },
        */

        // 设置认证token
        setAuthToken(token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        },
        
        // 登录
        async login() {
            try {
                await this.$refs.loginFormRef.validate();
                this.loading = true;
                
                const response = await axios.post('/api/v1/auth/login', this.loginForm);
                const { access_token, grade_upgraded, new_grade, message } = response.data;

                localStorage.setItem('token', access_token);
                this.setAuthToken(access_token);

                await this.getCurrentUser();
                this.isLoggedIn = true;

                // 如果年级升级了，显示升级提示
                if (grade_upgraded) {
                    ElMessage.success({
                        message: message,
                        duration: 5000,
                        showClose: true
                    });
                } else {
                    ElMessage.success('登录成功');
                }
            } catch (error) {
                console.error('登录失败:', error);
                ElMessage.error(error.response?.data?.detail || '登录失败');
            } finally {
                this.loading = false;
            }
        },
        
        // 注册
        async register() {
            try {
                await this.$refs.registerFormRef.validate();
                this.loading = true;
                
                await axios.post('/api/v1/auth/register', this.registerForm);
                
                ElMessage.success('注册成功，请登录');
                this.activeTab = 'login';
                
                // 清空注册表单
                this.registerForm = {
                    phone: '',
                    password: '',
                    confirm_password: '',
                    nickname: '',
                    child_grade: ''
                };
            } catch (error) {
                console.error('注册失败:', error);
                ElMessage.error(error.response?.data?.detail || '注册失败');
            } finally {
                this.loading = false;
            }
        },
        
        // 获取当前用户信息
        async getCurrentUser() {
            try {
                const response = await axios.get('/api/v1/auth/me');
                this.userInfo = response.data;
                this.isLoggedIn = true;
            } catch (error) {
                console.error('获取用户信息失败:', error);
                this.logout();
            }
        },
        
        // 退出登录
        logout() {
            localStorage.removeItem('token');
            delete axios.defaults.headers.common['Authorization'];
            this.isLoggedIn = false;
            this.userInfo = {};
            ElMessage.success('已退出登录');
        },
        
        // 加载资源列表
        async loadResources() {
            try {
                const response = await axios.get('/api/v1/resources/', {
                    params: this.searchForm
                });
                this.resources = response.data.items || [];
            } catch (error) {
                console.error('加载资源失败:', error);
                this.resources = [];
            }
        },
        
        // 搜索资源
        async searchResources() {
            await this.loadResources();
        },
        
        // 处理文件选择
        handleFileChange(file) {
            this.uploadForm.file = file.raw;
        },

        // 获取文件图标和类型
        getFileIcon(fileName) {
            if (!fileName) return '📄';
            const ext = fileName.toLowerCase().split('.').pop();
            const iconMap = {
                'pdf': '📄 PDF',
                'doc': '📘 DOC',
                'docx': '📘 DOCX',
                'ppt': '📊 PPT',
                'pptx': '📊 PPTX',
                'xls': '📈 XLS',
                'xlsx': '📈 XLSX',
                'jpg': '🖼️ JPG',
                'jpeg': '🖼️ JPEG',
                'png': '🖼️ PNG',
                'zip': '🗜️ ZIP',
                'rar': '🗜️ RAR'
            };
            return iconMap[ext] || '📄 ' + ext.toUpperCase();
        },



        // 切换年级选择
        toggleGrade(grade) {
            const index = this.uploadForm.grade.indexOf(grade);
            if (index > -1) {
                // 如果已选中，则取消选择
                this.uploadForm.grade.splice(index, 1);
            } else {
                // 如果未选中，则添加选择
                this.uploadForm.grade.push(grade);
            }
        },

        // 选择科目
        selectSubject(subject) {
            if (this.uploadForm.subject === subject) {
                // 如果已选中，则取消选择
                this.uploadForm.subject = '';
            } else {
                // 选择新科目
                this.uploadForm.subject = subject;
            }
        },

        // 选择资源类型
        selectResourceType(type) {
            if (this.uploadForm.resource_type === type) {
                // 如果已选中，则取消选择
                this.uploadForm.resource_type = '';
            } else {
                // 选择新类型
                this.uploadForm.resource_type = type;
            }
        },
        
        // 上传资源
        async uploadResource() {
            try {
                // 验证表单
                await this.$refs.uploadFormRef.validate();

                // 额外验证必填字段
                if (!this.uploadForm.file) {
                    ElMessage.error('请选择要上传的文件');
                    return;
                }

                if (!this.uploadForm.grade || this.uploadForm.grade.length === 0) {
                    ElMessage.error('请选择年级');
                    return;
                }

                if (!this.uploadForm.subject) {
                    ElMessage.error('请选择科目');
                    return;
                }

                if (!this.uploadForm.resource_type) {
                    ElMessage.error('请选择资源类别');
                    return;
                }

                this.uploading = true;

                const formData = new FormData();
                formData.append('file', this.uploadForm.file);
                formData.append('title', this.uploadForm.title);

                // 处理年级（必填）
                formData.append('grade', this.uploadForm.grade.join(','));

                // 处理科目（必填）
                formData.append('subject', this.uploadForm.subject);

                // 处理资源类别（必填）
                formData.append('resource_type', this.uploadForm.resource_type);

                // 处理可选字段
                if (this.uploadForm.description) {
                    formData.append('description', this.uploadForm.description);
                }
                
                await axios.post('/api/v1/resources/', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                });
                
                ElMessage.success('资源上传成功，获得20积分');
                this.showUploadDialog = false;
                
                // 重置表单
                this.uploadForm = {
                    title: '',
                    grade: [],
                    subject: '',
                    resource_type: '',
                    description: '',
                    file: null
                };
                
                // 刷新数据
                await this.getCurrentUser();
                await this.loadResources();
                
            } catch (error) {
                console.error('上传失败:', error);
                ElMessage.error(error.response?.data?.detail || '上传失败');
            } finally {
                this.uploading = false;
            }
        },
        
        // 下载资源
        async downloadResource(resource) {
            try {
                await ElMessageBox.confirm(
                    `下载 "${resource.title}" 需要消耗10积分，是否继续？`,
                    '确认下载',
                    {
                        confirmButtonText: '确定',
                        cancelButtonText: '取消',
                        type: 'warning'
                    }
                );
                
                const response = await axios.post(`/api/v1/downloads/${resource.id}`);
                
                // 创建下载链接
                const downloadUrl = response.data.download_url;
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.download = resource.file_name;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                ElMessage.success('下载成功');
                
                // 刷新用户信息
                await this.getCurrentUser();
                
            } catch (error) {
                if (error === 'cancel') return;
                console.error('下载失败:', error);
                ElMessage.error(error.response?.data?.detail || '下载失败');
            }
        },
        

        
        // 格式化日期
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN');
        },
        
        // 处理标签页切换
        handleTabClick(tab) {
            // 可以在这里添加标签页切换的逻辑
        }
    }
}).use(ElementPlus).mount('#app');
