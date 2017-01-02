// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
require("vue-resource")
/*
import 'jquery/dist/jquery.min.js'
import 'materialize-css/bin/materialize.css'
import 'materialize-css/bin/materialize.js'
require("material-ui-vue")
*/
var VueResource = require("vue-resource");
require("jquery");

Vue.use(VueResource);

/* eslint-disable no-new  */
new Vue({
  el: '#app',
  template: '<App/>',
  components: { App }
})
