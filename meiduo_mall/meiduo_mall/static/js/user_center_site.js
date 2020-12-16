let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        is_show_edit: false,
        form_address: {
            receiver: '',
            province_id: '',
            city_id: '',
            district_id: '',
            place: '',
            mobile: '',
            tel: '',
            email: '',
        },

        provinces: [],
        cities: [],
        districts: [],
        addresses: JSON.parse(JSON.stringify(addresses)),
        default_address_id: default_address_id,
        editing_address_index: '',
        edit_title_index: '',
        new_title: '',

        error_receiver: false,
        error_place: false,
        error_mobile: false,
        error_tel: false,
        error_email: false,
    },
    mounted() {
        // 获取省份数据
        this.get_provinces();
    },
    watch: {
        // 监听到省份id变化
        'form_address.province_id': function(){
            if (this.form_address.province_id) {
                let url = '/areas/?area_id=' + this.form_address.province_id;
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.code == '0') {
                            this.cities = response.data.sub_data.subs;
                        } else {
                            console.log(response.data);
                            this.cities = [];
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                        this.cities = [];
                    })
            }
        },
        // 监听到城市id变化
        'form_address.city_id': function(){
            if (this.form_address.city_id){
                let url = '/areas/?area_id='+ this.form_address.city_id;
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.code == '0') {
                            this.districts = response.data.sub_data.subs;
                        } else {
                            console.log(response.data);
                            this.districts = [];
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                        this.districts = [];
                    })
            }
        }
    },
    methods: {
        // 展示新增地址弹框
        show_add_site(){
            this.is_show_edit = true;
            // 清空错误提示信息
            this.clear_all_errors();
            // 清空原有数据
            this.form_address.receiver = '';
            this.form_address.province_id = '';
            this.form_address.city_id = '';
            this.form_address.district_id = '';
            this.form_address.place = '';
            this.form_address.mobile = '';
            this.form_address.tel = '';
            this.form_address.email = '';
            this.editing_address_index = '';
        },
        // 展示编辑地址弹框
        show_edit_site(index){
            this.is_show_edit = true;
            this.clear_all_errors();
            this.editing_address_index = index.toString();
            // 只获取要编辑的数据
            this.form_address = JSON.parse(JSON.stringify(this.addresses[index]));
        },
        // 校验收货人
        check_receiver(){
            if (!this.form_address.receiver) {
                this.error_receiver = true;
            } else {
                this.error_receiver = false;
            }
        },
        // 校验收货地址
        check_place(){
            if (!this.form_address.place) {
                this.error_place = true;
            } else {
                this.error_place = false;
            }
        },
        // 校验手机号
        check_mobile(){
            let re = /^1[3-9]\d{9}$/;
            if(re.test(this.form_address.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile = true;
            }
        },
        // 校验固定电话
        check_tel(){
            if (this.form_address.tel) {
                let re = /^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$/;
                if (re.test(this.form_address.tel)) {
                    this.error_tel = false;
                } else {
                    this.error_tel = true;
                }
            } else {
                this.error_tel = false;
            }
        },
        // 校验邮箱
        check_email(){
            if (this.form_address.email) {
                let re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;
                if(re.test(this.form_address.email)) {
                    this.error_email = false;
                } else {
                    this.error_email = true;
                }
            } else {
                this.error_email = false;
            }
        },
        // 清空错误提示信息
        clear_all_errors(){
            this.error_receiver = false;
            this.error_mobile = false;
            this.error_place = false;
            this.error_tel = false;
            this.error_email = false;
        },
        // 获取省份数据
        get_provinces(){
            let url = '/areas/';
            axios.get(url, {
                responseType: 'json'
            })
                .then(response => {
                    if (response.data.code == '0') {
                        this.provinces = response.data.province_list;
                    } else {
                        console.log(response.data);
                        this.provinces = [];
                    }
                })
                .catch(error => {
                    console.log(error.response);
                    this.provinces = [];
                })
        },
        // 新增地址
        save_address(){
            if (this.error_receiver || this.error_place || this.error_mobile || this.error_email || !this.form_address.province_id || !this.form_address.city_id || !this.form_address.district_id ) {
                alert('信息填写有误！');
            } else {
                // 注意：0 == '';返回true; 0 === '';返回false;
                if (this.editing_address_index === '') {
                    // 新增地址
                    let url = '/addresses/create/';
                    axios.post(url, this.form_address, {
                        headers: {
                            'X-CSRFToken':getCookie('csrftoken')
                        },
                        responseType: 'json'
                    })
                        .then(response => {
                            if (response.data.code == '0') {
                                // 局部刷新界面：展示所有地址信息，将新的地址添加到头部
                                this.addresses.splice(0, 0, response.data.address);
                                this.is_show_edit = false;
                            } else if (response.data.code == '4101') {
                                location.href = '/login/?next=/addresses/';
                            } else {
                                alert(response.data.errmsg);
                            }
                        })
                        .catch(error => {
                            console.log(error.response);
                        })
                } else {
                    // 修改地址
                    let url = '/addresses/' + this.addresses[this.editing_address_index].id + '/';
                    axios.put(url, this.form_address, {
                        headers: {
                            'X-CSRFToken':getCookie('csrftoken')
                        },
                        responseType: 'json'
                    })
                        .then(response => {
                            if (response.data.code == '0') {
                                this.addresses[this.editing_address_index] = response.data.address;
                                this.is_show_edit = false;
                            } else if (response.data.code == '4101') {
                                location.href = '/login/?next=/addresses/';
                            } else {
                                alert(response.data.errmsg);
                            }
                        })
                        .catch(error => {
                            alert(error.response);
                        })
                }
            }
        },
        // 删除地址
        delete_address(index){
            let url = '/addresses/' + this.addresses[index].id + '/';
            axios.delete(url, {
                headers: {
                    'X-CSRFToken':getCookie('csrftoken')
                },
                responseType: 'json'
            })
                .then(response => {
                    if (response.data.code == '0') {
                        // 删除对应的标签
                        this.addresses.splice(index, 1);
                    } else if (response.data.code == '4101') {
                        location.href = '/login/?next=/addresses/';
                    }else {
                        alert(response.data.errmsg);
                    }
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
        // 设置默认地址
        set_default(index){
            let url = '/addresses/' + this.addresses[index].id + '/default/';
            axios.put(url, {}, {
                headers: {
                    'X-CSRFToken':getCookie('csrftoken')
                },
                responseType: 'json'
            })
                .then(response => {
                    if (response.data.code == '0') {
                        // 设置默认地址标签
                        this.default_address_id = this.addresses[index].id;
                    } else if (response.data.code == '4101') {
                        location.href = '/login/?next=/addresses/';
                    } else {
                        alert(response.data.errmsg);
                    }
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
        // 展示地址title编辑框
        show_edit_title(index){
            this.edit_title_index = index;
        },
        // 取消保存地址title
        cancel_title(){
            this.edit_title_index = '';
            this.new_title = '';
        },
        // 修改地址title
        save_title(index){
            if (!this.new_title) {
                alert("请填写标题后再保存！");
            } else {
                let url = '/addresses/' + this.addresses[index].id + '/title/';
                axios.put(url, {
                    title: this.new_title
                }, {
                    headers: {
                        'X-CSRFToken':getCookie('csrftoken')
                    },
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.code == '0') {
                            // 更新地址title
                            this.addresses[index].title = this.new_title;
                            this.cancel_title();
                        } else if (response.data.code == '4101') {
                            location.href = '/login/?next=/addresses/';
                        } else {
                            alert(response.data.errmsg);
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },
    }
});