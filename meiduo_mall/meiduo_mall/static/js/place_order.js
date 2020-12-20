let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        order_submitting: false,
        pay_method: 2,
        nowsite: '',
        payment_amount: '',
    },
    mounted(){
        // 初始化支付金额
        this.payment_amount = payment_amount;
        // 绑定默认地址
        this.nowsite = default_address_id;
    },
    methods: {
        // 提交订单
        on_order_submit(){
            if (!this.nowsite) {
                alert('请补充收货地址');
                return;
            }
            if (!this.pay_method) {
                alert('请选择付款方式');
                return;
            }
            if (this.order_submitting == false){
                this.order_submitting = true;
                let url = '/orders/commit/';
                axios.post(url, {
                    address_id: this.nowsite,
                    pay_method: parseInt(this.pay_method)
                }, {
                    headers:{
                        'X-CSRFToken':getCookie('csrftoken')
                    },
                    responseType: 'json'
                })
                    .then(response => {
                        this.order_submitting = false;
                        if (response.data.code == '0') {
                            location.href = '/orders/success/?order_id='+response.data.order_id
                                        +'&payment_amount='+this.payment_amount
                                        +'&pay_method='+this.pay_method;
                        } else if (response.data.code == '4101') {
                            location.href = '/login/?next=/orders/settlement/';
                        } else {
                            alert(response.data.errmsg);
                        }
                    })
                    .catch(error => {
                        this.order_submitting = false;
                        console.log(error.response);
                    })
            }
        }
    }
});