// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import Vuex from 'vuex';
import VueRouter from 'vue-router';
import VueResource from 'vue-resource';
import VueMaterial from 'vue-material';
import 'vue-material/dist/vue-material.css';
import 'roboto-fontface/css/roboto/roboto-fontface.css';
import 'material-design-icons/iconfont/material-icons.css';
import jQuery from 'jquery';
import store_data from './store.js';
import App from './App';
import User from './User';
import Toolbar from './Toolbar';

Vue.use(Vuex);
Vue.use(VueRouter);
Vue.use(VueResource);
Vue.use(VueMaterial);

var routes = [
    {path: '/', name: 'root', component: App},
    {path: '/day/', name: 'days', component: App},
    {path: '/day/:day', name: 'day', component: App},
    {path: '/user/:user', name: 'user', component: User}
];

const store = new Vuex.Store(store_data);
const router = new VueRouter({routes});

const store2 = new Vuex.Store({
  state: {
    count: 0
  },
  mutations: {
    increment (state) {
      state.count++;
    }
  }
});


var vue = new Vue({
    el: '#app',
    store: store,
    template: '<div id="app"><Toolbar /><router-view class="view"></router-view></div>',
    router: router,
    components: { App, Toolbar, User }
});
