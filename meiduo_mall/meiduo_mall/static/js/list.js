let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        category_id: category_id,
        hot_skus: [],
        cart_total_count: 0,
        carts: [],
    },
    mounted(){
        // 获取热销商品数据
        this.get_hot_skus();
        // 获取简单购物车数据
        // this.get_carts();
    },
    methods: {
    	// 获取热销商品数据
        get_hot_skus(){
            if (this.category_id) {
                let url = '/hot/'+ this.category_id +'/';
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        this.hot_skus = response.data.hot_skus;
                        for(let i=0; i<this.hot_skus.length; i++){
                            this.hot_skus[i].url = '/detail/' + this.hot_skus[i].id + '/';
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },
        // 获取简单购物车数据
        get_carts(){
        	let url = '/carts/simple/';
            axios.get(url, {
                responseType: 'json',
            })
                .then(response => {
                    this.carts = response.data.cart_skus;
                    this.cart_total_count = 0;
                    for(let i=0;i<this.carts.length;i++){
                        if (this.carts[i].name.length>25){
                            this.carts[i].name = this.carts[i].name.substring(0, 25) + '...';
                        }
                        this.cart_total_count += this.carts[i].count;
                    }
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
    }
});