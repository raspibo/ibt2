/*
 * I'll be there, 2. An oversimplified application to register attendees at a conference or event.
 *
 *  Copyright 2016-2017 Davide Alberani <da@mimante.net>, RaspiBO <info@raspibo.org>
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

import { createApp, h } from 'vue';
import { createStore } from 'vuex';
import { createRouter, createWebHashHistory, RouterView } from 'vue-router';
import PrimeVue from 'primevue/config';
import Aura from '@primeuix/themes/aura';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Textarea from 'primevue/textarea';
import ToggleSwitch from 'primevue/toggleswitch';
import Dialog from 'primevue/dialog';
import IbtPrompt from './IbtPrompt.vue';
import '@fontsource/roboto/latin-400.css';
import '@fontsource/roboto/latin-500.css';
import '@fontsource/roboto/latin-700.css';
import 'primeicons/primeicons.css';
import './style.css';
import store_data from './store.js';
import Toolbar from './Toolbar';
import IbtFooter from './IbtFooter';

const App = () => import('./App.vue');
const User = () => import('./User.vue');
const Users = () => import('./Users.vue');
const GlobalSettings = () => import('./GlobalSettings.vue');
const routes = [
    {path: '/', name: 'home', component: App},
    {path: '/day/', name: 'days', component: App},
    {path: '/day/:day', name: 'day', component: App},
    {path: '/user/', name: 'users', component: Users},
    {path: '/user/:id', name: 'user', component: User},
    {path: '/settings/', name: 'settings', component: GlobalSettings},
];

const store = createStore(store_data);
const router = createRouter({ history: createWebHashHistory(), routes });
const app = createApp({
    render: () => h('div', [h(Toolbar), h(RouterView, { class: 'view' }), h(IbtFooter)]),
});
app.use(store).use(router).use(PrimeVue, {
    theme: { preset: Aura, options: { darkModeSelector: false } },
    locale: { firstDayOfWeek: 1 },
});
for (const [name, component] of Object.entries({ Button, InputText, Password, Textarea, ToggleSwitch, Dialog, IbtPrompt })) {
    app.component(name, component);
}
router.isReady().then(() => app.mount('#app'));
