let vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        username: getCookie('username'),
        hot_skus: [],
        category_id: category_id,
		sku_id: sku_id,
        sku_price: sku_price,
        sku_count: 1,
        sku_amount: 0,
        tab_content: {
		    detail: true,
            pack: false,
            comment: false,
            service: false
        },
        cart_total_count: 0,
        carts: [],
        comments: [],
        score_classes: {
            1: 'stars_one',
            2: 'stars_two',
            3: 'stars_three',
            4: 'stars_four',
            5: 'stars_five',
        },
    },
    mounted(){
		// 获取热销商品数据
        this.get_hot_skus();
        // 记录分类商品的访问量
		this.goods_visit_count();
        // 保存用户浏览记录
		this.save_browse_histories();
		// 获取简单购物车数据
        this.get_carts();
		// 获取商品评价信息
        this.get_goods_comment();
    },
    watch: {
        // 监听商品数量的变化
        sku_count: {
            handler(newValue){
                this.sku_amount = (newValue * this.sku_price).toFixed(2);
            },
            immediate: true
        }
    },
    methods: {
        // 加数量
        on_addition(){
            if (this.sku_count < 5) {
                this.sku_count++;
            } else {
                this.sku_count = 5;
                alert('超过商品数量上限');
            }
        },
        // 减数量
        on_minus(){
            if (this.sku_count > 1) {
                this.sku_count--;
            }
        },
        // 编辑商品数量
        check_sku_count(){
            if (this.sku_count > 5) {
                this.sku_count = 5;
            }
            if (this.sku_count < 1) {
                this.sku_count = 1;
            }
        },
        // 控制页面标签页展示
        on_tab_content(name){
            this.tab_content = {
                detail: false,
                pack: false,
                comment: false,
                service: false
            };
            this.tab_content[name] = true;
        },
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
        // 记录分类商品的访问量
		goods_visit_count(){
        	if (this.category_id) {
        		let url = '/detail/visit/' + this.category_id + '/';
				axios.post(url, {}, {
                    headers: {
                        'X-CSRFToken':getCookie('csrftoken')
                    },
                    responseType: 'json'
                })
					.then(response => {
						console.log(response.data);
					})
					.catch(error => {
						console.log(error.response);
					});
			}
		},
		// 保存用户浏览记录
		save_browse_histories(){
        	if (this.sku_id) {
        		let url = '/browse_histories/';
				axios.post(url, {
                    'sku_id':this.sku_id
                }, {
                    headers: {
                        'X-CSRFToken':getCookie('csrftoken')
                    },
                    responseType: 'json'
                })
					.then(response => {
						console.log(response.data);
					})
					.catch(error => {
						console.log(error.response);
					});
			}
		},
        // 加入购物车
        add_carts(){
            let url = '/carts/';
            axios.post(url, {
                sku_id: parseInt(this.sku_id),
                count: this.sku_count
            }, {
                headers: {
                    'X-CSRFToken':getCookie('csrftoken')
                },
                responseType: 'json',
                withCredentials: true
            })
                .then(response => {
                    if (response.data.code == '0') {
                        alert('添加购物车成功');
                        this.cart_total_count += this.sku_count;
                    } else { // 参数错误
                        alert(response.data.errmsg);
                    }
                })
                .catch(error => {
                    console.log(error.response);
                })
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
        // 获取商品评价信息
        get_goods_comment(){
            if (this.sku_id) {
                let url = '/comments/'+ this.sku_id +'/';
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        this.comments = response.data.comment_list;
                        for(let i=0; i<this.comments.length; i++){
                            this.comments[i].score_class = this.score_classes[this.comments[i].score];
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    });
            }
        },
    }
});