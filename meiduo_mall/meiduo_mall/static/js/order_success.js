let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
    },
    mounted(){
    },
    methods: {
        // 发起支付
        order_payment(){
            let order_id = get_query_string('order_id');
            let url = '/payment/' + order_id + '/';
            axios.get(url, {
                responseType: 'json'
            })
                .then(response => {
                    if (response.data.code == '0') {
                        // 跳转到支付宝
                        location.href = response.data.alipay_url;
                    } else if (response.data.code == '4101') {
                        location.href = '/login/?next=/orders/info/1/';
                    } else {
                        console.log(response.data);
                        alert(response.data.errmsg);
                    }
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
    }
});