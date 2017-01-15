// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import VueRouter from 'vue-router';
import VueResource from 'vue-resource';
import VueMaterial from 'vue-material';
import 'vue-material/dist/vue-material.css';
import 'roboto-fontface/css/roboto/roboto-fontface.css';
import 'material-design-icons/iconfont/material-icons.css';
import jQuery from 'jquery';
import App from './App';
import User from './User';
import Toolbar from './Toolbar';

Vue.use(VueRouter);
Vue.use(VueResource);
Vue.use(VueMaterial);

var routes = [
    {path: '/', component: App},
    {path: '/day/', component: App},
    {path: '/day/:day', component: App},
    {path: '/user/:user', component: User}
];

const router = new VueRouter({routes});

var vue = new Vue({
    el: '#app',
    template: '<div id="app"><Toolbar /><router-view class="view"></router-view></div>',
    router: router,
    components: { App, Toolbar, User }
});
