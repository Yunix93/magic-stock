/**
 * 现代化后台管理系统 - 主JavaScript文件
 * 
 * 提供全局JavaScript功能和工具函数
 */

(function() {
    'use strict';
    
    // 全局命名空间
    window.AdminSystem = window.AdminSystem || {};
    
    /**
     * 工具函数
     */
    AdminSystem.Utils = {
        
        /**
         * 防抖函数
         * @param {Function} func 要防抖的函数
         * @param {number} wait 等待时间（毫秒）
         * @param {boolean} immediate 是否立即执行
         * @returns {Function} 防抖后的函数
         */
        debounce: function(func, wait, immediate) {
            var timeout;
            return function() {
                var context = this, args = arguments;
                var later = function() {
                    timeout = null;
                    if (!immediate) func.apply(context, args);
                };
                var callNow = immediate && !timeout;
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
                if (callNow) func.apply(context, args);
            };
        },
        
        /**
         * 节流函数
         * @param {Function} func 要节流的函数
         * @param {number} wait 等待时间（毫秒）
         * @returns {Function} 节流后的函数
         */
        throttle: function(func, wait) {
            var timeout;
            return function() {
                var context = this, args = arguments;
                if (!timeout) {
                    timeout = setTimeout(function() {
                        timeout = null;
                        func.apply(context, args);
                    }, wait);
                }
            };
        },
        
        /**
         * 格式化日期
         * @param {Date|string} date 日期对象或字符串
         * @param {string} format 格式字符串
         * @returns {string} 格式化后的日期字符串
         */
        formatDate: function(date, format) {
            if (!date) return '';
            
            var d = new Date(date);
            if (isNaN(d.getTime())) return '';
            
            format = format || 'YYYY-MM-DD HH:mm:ss';
            
            var year = d.getFullYear();
            var month = String(d.getMonth() + 1).padStart(2, '0');
            var day = String(d.getDate()).padStart(2, '0');
            var hours = String(d.getHours()).padStart(2, '0');
            var minutes = String(d.getMinutes()).padStart(2, '0');
            var seconds = String(d.getSeconds()).padStart(2, '0');
            
            return format
                .replace('YYYY', year)
                .replace('MM', month)
                .replace('DD', day)
                .replace('HH', hours)
                .replace('mm', minutes)
                .replace('ss', seconds);
        },
        
        /**
         * 获取URL参数
         * @param {string} name 参数名
         * @returns {string|null} 参数值
         */
        getUrlParam: function(name) {
            var urlParams = new URLSearchParams(window.location.search);
            return urlParams.get(name);
        },
        
        /**
         * 设置URL参数
         * @param {string} name 参数名
         * @param {string} value 参数值
         */
        setUrlParam: function(name, value) {
            var url = new URL(window.location);
            url.searchParams.set(name, value);
            window.history.pushState({}, '', url);
        },
        
        /**
         * 复制文本到剪贴板
         * @param {string} text 要复制的文本
         * @returns {Promise} 复制结果
         */
        copyToClipboard: function(text) {
            if (navigator.clipboard) {
                return navigator.clipboard.writeText(text);
            } else {
                // 兼容旧浏览器
                var textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                try {
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    return Promise.resolve();
                } catch (err) {
                    document.body.removeChild(textArea);
                    return Promise.reject(err);
                }
            }
        },
        
        /**
         * 生成UUID
         * @returns {string} UUID字符串
         */
        generateUUID: function() {
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                var r = Math.random() * 16 | 0;
                var v = c === 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
        }
    };
    
    /**
     * 存储管理
     */
    AdminSystem.Storage = {
        
        /**
         * 设置本地存储
         * @param {string} key 键名
         * @param {any} value 值
         */
        setLocal: function(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (e) {
                console.warn('localStorage设置失败:', e);
            }
        },
        
        /**
         * 获取本地存储
         * @param {string} key 键名
         * @param {any} defaultValue 默认值
         * @returns {any} 存储的值
         */
        getLocal: function(key, defaultValue) {
            try {
                var item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (e) {
                console.warn('localStorage获取失败:', e);
                return defaultValue;
            }
        },
        
        /**
         * 删除本地存储
         * @param {string} key 键名
         */
        removeLocal: function(key) {
            try {
                localStorage.removeItem(key);
            } catch (e) {
                console.warn('localStorage删除失败:', e);
            }
        },
        
        /**
         * 设置会话存储
         * @param {string} key 键名
         * @param {any} value 值
         */
        setSession: function(key, value) {
            try {
                sessionStorage.setItem(key, JSON.stringify(value));
            } catch (e) {
                console.warn('sessionStorage设置失败:', e);
            }
        },
        
        /**
         * 获取会话存储
         * @param {string} key 键名
         * @param {any} defaultValue 默认值
         * @returns {any} 存储的值
         */
        getSession: function(key, defaultValue) {
            try {
                var item = sessionStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (e) {
                console.warn('sessionStorage获取失败:', e);
                return defaultValue;
            }
        },
        
        /**
         * 删除会话存储
         * @param {string} key 键名
         */
        removeSession: function(key) {
            try {
                sessionStorage.removeItem(key);
            } catch (e) {
                console.warn('sessionStorage删除失败:', e);
            }
        }
    };
    
    /**
     * 主题管理
     */
    AdminSystem.Theme = {
        
        /**
         * 设置主题
         * @param {string} theme 主题名称 ('light', 'dark')
         */
        setTheme: function(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            AdminSystem.Storage.setLocal('theme', theme);
        },
        
        /**
         * 获取当前主题
         * @returns {string} 当前主题
         */
        getTheme: function() {
            return document.documentElement.getAttribute('data-theme') || 
                   AdminSystem.Storage.getLocal('theme', 'light');
        },
        
        /**
         * 切换主题
         */
        toggleTheme: function() {
            var currentTheme = this.getTheme();
            var newTheme = currentTheme === 'light' ? 'dark' : 'light';
            this.setTheme(newTheme);
        }
    };
    
    /**
     * 响应式处理
     */
    AdminSystem.Responsive = {
        
        /**
         * 获取屏幕尺寸类型
         * @returns {string} 尺寸类型 ('mobile', 'tablet', 'desktop')
         */
        getScreenSize: function() {
            var width = window.innerWidth;
            if (width < 768) return 'mobile';
            if (width < 1200) return 'tablet';
            return 'desktop';
        },
        
        /**
         * 是否为移动设备
         * @returns {boolean} 是否为移动设备
         */
        isMobile: function() {
            return this.getScreenSize() === 'mobile';
        },
        
        /**
         * 是否为平板设备
         * @returns {boolean} 是否为平板设备
         */
        isTablet: function() {
            return this.getScreenSize() === 'tablet';
        },
        
        /**
         * 是否为桌面设备
         * @returns {boolean} 是否为桌面设备
         */
        isDesktop: function() {
            return this.getScreenSize() === 'desktop';
        }
    };
    
    /**
     * 布局交互管理
     */
    AdminSystem.Layout = {
        
        /**
         * 初始化用户下拉菜单
         */
        initUserDropdown: function() {
            document.addEventListener('click', function(e) {
                var dropdownBtn = e.target.closest('.user-dropdown-btn');
                var dropdown = e.target.closest('.user-dropdown');
                
                if (dropdownBtn) {
                    e.preventDefault();
                    var menu = dropdownBtn.nextElementSibling;
                    if (menu && menu.classList.contains('user-dropdown-menu')) {
                        var isVisible = menu.style.display === 'block';
                        // 关闭所有下拉菜单
                        document.querySelectorAll('.user-dropdown-menu').forEach(function(m) {
                            m.style.display = 'none';
                        });
                        // 切换当前菜单
                        menu.style.display = isVisible ? 'none' : 'block';
                    }
                } else if (!dropdown) {
                    // 点击外部关闭所有下拉菜单
                    document.querySelectorAll('.user-dropdown-menu').forEach(function(menu) {
                        menu.style.display = 'none';
                    });
                }
            });
        },
        
        /**
         * 初始化侧边栏菜单
         */
        initSidebarMenu: function() {
            // 处理子菜单展开/收起
            document.addEventListener('click', function(e) {
                var menuLink = e.target.closest('.menu-link.has-submenu');
                
                if (menuLink) {
                    e.preventDefault();
                    var menuItem = menuLink.closest('.menu-item');
                    var submenu = menuItem.querySelector('.submenu');
                    
                    if (submenu) {
                        // 切换子菜单显示状态
                        menuItem.classList.toggle('open');
                        
                        // 关闭其他打开的子菜单（可选）
                        var siblings = menuItem.parentNode.querySelectorAll('.menu-item.has-submenu.open');
                        siblings.forEach(function(item) {
                            if (item !== menuItem) {
                                item.classList.remove('open');
                            }
                        });
                    }
                }
            });
            
            // 高亮当前页面对应的菜单项
            this.highlightCurrentMenuItem();
        },
        
        /**
         * 高亮当前页面对应的菜单项
         */
        highlightCurrentMenuItem: function() {
            var currentPath = window.location.pathname;
            
            // 移除所有活动状态
            document.querySelectorAll('.menu-link.active, .submenu-link.active').forEach(function(link) {
                link.classList.remove('active');
            });
            
            // 查找匹配的菜单项
            document.querySelectorAll('.menu-link, .submenu-link').forEach(function(link) {
                var href = link.getAttribute('href');
                if (href === currentPath) {
                    link.classList.add('active');
                    
                    // 如果是子菜单项，展开父菜单
                    var parentMenuItem = link.closest('.menu-item.has-submenu');
                    if (parentMenuItem) {
                        parentMenuItem.classList.add('open');
                    }
                }
            });
        },
        
        /**
         * 初始化移动端菜单
         */
        initMobileMenu: function() {
            var self = this;
            
            // 创建移动端菜单切换按钮
            function createMobileToggle() {
                if (AdminSystem.Responsive.isMobile() && !document.querySelector('.mobile-menu-toggle')) {
                    var header = document.querySelector('.app-header .header-container');
                    if (header) {
                        var toggleBtn = document.createElement('button');
                        toggleBtn.className = 'mobile-menu-toggle';
                        toggleBtn.innerHTML = '☰';
                        toggleBtn.setAttribute('aria-label', '切换菜单');
                        toggleBtn.addEventListener('click', self.toggleMobileMenu);
                        
                        header.insertBefore(toggleBtn, header.firstChild);
                    }
                }
            }
            
            // 监听屏幕尺寸变化
            window.addEventListener('screenSizeChanged', function(e) {
                if (e.detail.size === 'mobile') {
                    createMobileToggle();
                } else {
                    var toggle = document.querySelector('.mobile-menu-toggle');
                    if (toggle) {
                        toggle.remove();
                    }
                    // 关闭移动端菜单
                    var sidebar = document.querySelector('.sidebar');
                    if (sidebar) {
                        sidebar.classList.remove('open');
                    }
                }
            });
            
            // 初始检查
            createMobileToggle();
        },
        
        /**
         * 切换移动端菜单
         */
        toggleMobileMenu: function() {
            var sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                sidebar.classList.toggle('open');
            }
        },
        
        /**
         * 初始化表单增强
         */
        initFormEnhancements: function() {
            // 表单验证
            document.addEventListener('submit', function(e) {
                var form = e.target;
                if (form.classList.contains('needs-validation')) {
                    if (!AdminSystem.Layout.validateForm(form)) {
                        e.preventDefault();
                        e.stopPropagation();
                    }
                }
            });
            
            // 输入框焦点效果
            document.addEventListener('focus', function(e) {
                if (e.target.classList.contains('form-input')) {
                    var formGroup = e.target.closest('.form-group');
                    if (formGroup) {
                        formGroup.classList.add('focused');
                    }
                }
            }, true);
            
            document.addEventListener('blur', function(e) {
                if (e.target.classList.contains('form-input')) {
                    var formGroup = e.target.closest('.form-group');
                    if (formGroup) {
                        formGroup.classList.remove('focused');
                    }
                }
            }, true);
        },
        
        /**
         * 表单验证
         * @param {HTMLFormElement} form 表单元素
         * @returns {boolean} 验证结果
         */
        validateForm: function(form) {
            var isValid = true;
            var inputs = form.querySelectorAll('.form-input[required]');
            
            inputs.forEach(function(input) {
                if (!input.value.trim()) {
                    AdminSystem.Layout.showFieldError(input, '此字段为必填项');
                    isValid = false;
                } else {
                    AdminSystem.Layout.clearFieldError(input);
                }
            });
            
            return isValid;
        },
        
        /**
         * 显示字段错误
         * @param {HTMLElement} input 输入框元素
         * @param {string} message 错误消息
         */
        showFieldError: function(input, message) {
            this.clearFieldError(input);
            
            var errorEl = document.createElement('div');
            errorEl.className = 'form-error';
            errorEl.textContent = message;
            
            input.parentNode.appendChild(errorEl);
            input.classList.add('error');
        },
        
        /**
         * 清除字段错误
         * @param {HTMLElement} input 输入框元素
         */
        clearFieldError: function(input) {
            var errorEl = input.parentNode.querySelector('.form-error');
            if (errorEl) {
                errorEl.remove();
            }
            input.classList.remove('error');
        }
    };
    
    /**
     * 消息提示管理
     */
    AdminSystem.Message = {
        
        /**
         * 显示消息
         * @param {string} message 消息内容
         * @param {string} type 消息类型 ('success', 'error', 'warning', 'info')
         * @param {number} duration 显示时长（毫秒）
         */
        show: function(message, type, duration) {
            type = type || 'info';
            duration = duration || 3000;
            
            // 创建消息容器（如果不存在）
            var container = document.querySelector('.message-container');
            if (!container) {
                container = document.createElement('div');
                container.className = 'message-container';
                document.body.appendChild(container);
            }
            
            // 创建消息元素
            var messageEl = document.createElement('div');
            messageEl.className = 'message message-' + type;
            messageEl.innerHTML = 
                '<span class="message-text">' + message + '</span>' +
                '<button class="message-close" onclick="this.parentElement.remove()">×</button>';
            
            // 添加到容器
            container.appendChild(messageEl);
            
            // 显示动画
            setTimeout(function() {
                messageEl.classList.add('show');
            }, 10);
            
            // 自动隐藏
            setTimeout(function() {
                messageEl.classList.remove('show');
                setTimeout(function() {
                    if (messageEl.parentNode) {
                        messageEl.parentNode.removeChild(messageEl);
                    }
                }, 300);
            }, duration);
        },
        
        /**
         * 显示成功消息
         * @param {string} message 消息内容
         * @param {number} duration 显示时长
         */
        success: function(message, duration) {
            this.show(message, 'success', duration);
        },
        
        /**
         * 显示错误消息
         * @param {string} message 消息内容
         * @param {number} duration 显示时长
         */
        error: function(message, duration) {
            this.show(message, 'error', duration);
        },
        
        /**
         * 显示警告消息
         * @param {string} message 消息内容
         * @param {number} duration 显示时长
         */
        warning: function(message, duration) {
            this.show(message, 'warning', duration);
        },
        
        /**
         * 显示信息消息
         * @param {string} message 消息内容
         * @param {number} duration 显示时长
         */
        info: function(message, duration) {
            this.show(message, 'info', duration);
        }
    };
    
    /**
     * 初始化函数
     */
    AdminSystem.init = function() {
        console.log('🚀 现代化后台管理系统 JavaScript 初始化完成');
        
        // 初始化主题
        var savedTheme = AdminSystem.Storage.getLocal('theme', 'light');
        AdminSystem.Theme.setTheme(savedTheme);
        
        // 初始化布局交互
        AdminSystem.Layout.initUserDropdown();
        AdminSystem.Layout.initSidebarMenu();
        AdminSystem.Layout.initMobileMenu();
        AdminSystem.Layout.initFormEnhancements();
        
        // 监听窗口大小变化
        window.addEventListener('resize', AdminSystem.Utils.throttle(function() {
            // 触发自定义事件
            window.dispatchEvent(new CustomEvent('screenSizeChanged', {
                detail: { size: AdminSystem.Responsive.getScreenSize() }
            }));
        }, 250));
        
        // 监听主题变化（使用现代API）
        if (window.matchMedia) {
            var mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            var handleThemeChange = function(e) {
                if (!AdminSystem.Storage.getLocal('theme')) {
                    AdminSystem.Theme.setTheme(e.matches ? 'dark' : 'light');
                }
            };
            
            // 使用现代API
            if (mediaQuery.addEventListener) {
                mediaQuery.addEventListener('change', handleThemeChange);
            } else {
                // 兼容旧浏览器
                mediaQuery.addListener(handleThemeChange);
            }
        }
        
        // 网络状态监听
        window.addEventListener('online', function() {
            AdminSystem.Message.success('网络连接已恢复');
        });
        
        window.addEventListener('offline', function() {
            AdminSystem.Message.warning('网络连接已断开');
        });
        
        // 页面可见性变化处理
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                console.log('页面隐藏');
            } else {
                console.log('页面显示');
                // 页面重新显示时可以刷新数据
            }
        });
    };
    
    // DOM加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', AdminSystem.init);
    } else {
        AdminSystem.init();
    }
    
})();