<template>
    <md-toolbar id="toolbar" class="md-dense">
        <h2 id="toolbar-title" class="md-title">ibt2</h2>
        <span v-if="loggedInUser.username">
            <span id="logged-in">
                Logged in: <router-link :to="userUrl">{{ loggedInUser.username }}</router-link>
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
</template>
<script>

export default {
    data () {
        return {
            username: '',
            password: '',
            showLoginForm: false,
            loggedInUser: {username: ''}
        }
    },

    computed: {
        userUrl: function() {
            var id = this.loggedInUser._id;
            if (!id) {
                return '';
            }
            return '/user/' + this.loggedInUser._id;
        }
    },

    beforeCreate: function() {
        this.currentUserUrl = this.$resource('users/current');
        this.loginUrl = this.$resource('login');
        this.logoutUrl = this.$resource('logout');
    },

    mounted: function() {
        this.getUserInfo();
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
    }
}
</script>

<style>

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
