<template>
    <div id="app">
        <md-toolbar class="md-dense">
            <h2 id="toolbar-title" class="md-title">ibt2</h2>
            <span v-if="loggedInUser.username">
                <span id="logged-in">
                    Logged in: {{ loggedInUser.username }}
                </span>
                <md-button class="md-icon-button" @click="logout()">
                    <md-icon>exit_to_app</md-icon>
                </md-button>
            </span>
            <span v-else>
                <md-button v-show="!showLoginForm" class="md-icon-button" @click="focusToLoginForm()">
                    <md-icon>power_settings_new</md-icon>
                </md-button>
                <span v-show="showLoginForm" id="login-form">
                    <md-input-container id="username-input" class="login-input" md-inline>
                        <md-input ref="usernameInput" @keyup.enter.native="focusToPassword()" v-model="username" placeholder="username" md-inline />&nbsp;
                    </md-input-container>
                    <md-input-container id="password-input" class="login-input" md-inline>
                        <md-input ref="passwordInput" @keyup.enter.native="login()" v-model="password" placeholder="password" type="password" md-line />
                    </md-input-container>
                </span>
            </span>
        </md-toolbar>
        <md-layout md-gutter md-row>
            <md-layout md-column md-flex="20" md-gutter>
                <datepicker id="datepicker" :value="date" :inline="true" @selected="getDay"></datepicker>
            </md-layout>
            <md-layout id="panel" md-column>
                <md-layout md-row>
                    <group v-for="group in day.groups || []" :group="group" :day="day.day" new-attendee="" @updated="reload" />
                    <group :add-new-group="true" :day="day.day" new-attendee="" new-group="" @updated="reload" />
                </md-layout>
            </md-layout>
        </md-layout>
    </div>
</template>
<script>

import Datepicker from 'vuejs-datepicker';
import Group from './Group';

export default {
    data () {
        return {
            date: null, // a Date object representing the selected date
            day: {},
            daysSummary: {},
            username: '',
            password: '',
            showLoginForm: false,
            loggedInUser: {username: ''}
        }
    },

    beforeCreate: function() {
        this.daysUrl = this.$resource('days{/day}');
        this.attendeesUrl = this.$resource('attendees{/id}');
        this.currentUserUrl = this.$resource('users/current');
        this.loginUrl = this.$resource('login');
        this.logoutUrl = this.$resource('logout');
    },

    mounted: function() {
        this.getUserInfo();
        var [year, month, day] = (this.$route.params.day || '').split('-');
        year = parseInt(year);
        month = parseInt(month) - 1;
        day = parseInt(day);
        if (!isNaN(year) && !isNaN(month) && !isNaN(day)) {
            this.date = new Date(year, month, day);
        }
        if (!(this.date && !isNaN(this.date.getTime()))) {
            this.date = new Date();
        }
        this.reload();
    },

    methods: {
        focusToLoginForm() {
            this.showLoginForm = true;
            var that = this;
            setTimeout(function() { that.$refs.usernameInput.$el.focus(); }, 400);
        },

        focusToPassword() {
            this.$refs.passwordInput.$el.focus();
        },

        reload() {
            var ym = this.dateToString(this.date, true);
            this.getSummary({start: ym, end: ym});
            this.getDay();
        },

        dateToString(date, excludeDay) {
            var year = '' + date.getFullYear();
            var month = '' + (date.getMonth() + 1);
            month = '00'.substring(0, 2 - month.length) + month;
            var ym = year + '-' + month;
            if (excludeDay) {
                return ym;
            }
            var day = '' + (date.getDate());
            day = '00'.substring(0, 2 - day.length) + day;
            return ym + '-' + day;
        },

        getSummary(params) {
            if (!params) {
                params = {};
            }
            params['summary'] = true;
            this.daysUrl.query(params).then((response) => {
                return response.json();
            }, (response) => {
                alert('getSummary: failed to get resource');
            }).then((json) => {
                this.daysSummary = json;
            });
        },

        getDay(day) {
            if (day instanceof Date) {
                this.date = day;
                day = this.dateToString(day);
            } else if (this.date && this.date instanceof Date) {
                day = this.dateToString(this.date);
            } else {
                var today = new Date();
                day = this.dateToString(today);
                this.date = today;
            }
            this.$router.push('/day/' + day);
            this.daysUrl.get({day: day}).then((response) => {
                return response.json();
            }, (response) => {
                alert('getDay: failed to get resource');
            }).then((dayData) => {
                if (!dayData.day) {
                    dayData.day = day;
                }
                this.day = dayData;
            });
        },

        login() {
            this.loginUrl.save({username: this.username, password: this.password}).then((response) => {
                return response.json();
            }, (response) => {
                alert('login: failed to get resource');
            }).then((data) => {
                this.showLoginForm = false;
                this.getUserInfo();
            });
        },

        logout() {
            this.logoutUrl.get().then((response) => {
                return response.json();
            }, (response) => {
                alert('logout: failed to get resource');
            }).then((json) => {
                this.loggedInUser = {};
            });
        },

        getUserInfo(callback) {
            this.currentUserUrl.get().then((response) => {
                return response.json();
            }, (response) => {
                alert('getUserInfo: failed to get resource');
            }).then((data) => {
                this.loggedInUser = data || {};
                if (callback) {
                    callback(this.loggedInUser);
                }
            });
        }
    },

    components: {
        Datepicker, Group
    }
}
</script>

<style>
#app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;
    margin-top: 0px;
}

#datepicker {
    padding: 10px;
}

#panel .md-layout {
    flex: initial;
}

#toolbar-title {
    flex: 1;
}

.login-input {
    width: 200px;
    margin: 0px 0px 0px;
    padding-top: 0px;
    padding-left: 4px;
    min-height: 24px;
    line-height: 0px;
    margin-right: 20px;
    background-color: white;
}

#username-input {
    display: inline;
    float: left;
}

#password-input {
    display: inline;
    float: right;
}

#logged-in {
    position: relative;
    top: 10px;

}
</style>
