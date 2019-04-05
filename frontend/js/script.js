import '../scss/style.scss';
import Vue from 'vue'
import VueResource from 'vue-resource'
import jQuery from 'jquery';
import VuejsDialog from "vuejs-dialog"

Vue.use(VueResource);
Vue.use(VuejsDialog);
const http = Vue.http;

export default http

!function ($) {

}(jQuery);
var app = new Vue({
    el: '#app',
    data: {
        path: "",
        loading: true,
        show: true,
    },

    methods: {
        post: function () {
            this.show = false;
            this.loading = true;
            this.$http.post("/", {
                path: this.path
            }).then(response => {
                this.loading = false;
                this.show = true;
            }, response => {});
        },
    },
});
