/*
 * I'll be there, 2. An oversimplified application to register attendees at a conference or event.
 *
 *  Copyright 2016-2017 Davide Alberani <da@erlug.linux.it>, RaspiBO <info@raspibo.org>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

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
import Users from './Users';
import Toolbar from './Toolbar';

Vue.use(Vuex);
Vue.use(VueRouter);
Vue.use(VueResource);
Vue.use(VueMaterial);

var routes = [
    {path: '/', name: 'home', component: App},
    {path: '/day/', name: 'days', component: App},
    {path: '/day/:day', name: 'day', component: App},
    {path: '/user/', name: 'users', component: Users},
    {path: '/user/:id', name: 'user', component: User}
];

const store = new Vuex.Store(store_data);
const router = new VueRouter({routes});

var vue = new Vue({
    el: '#app',
    store: store,
    template: '<div id="app"><Toolbar /><router-view class="view"></router-view></div>',
    router: router,
    components: { App, Toolbar, Users, User }
});
