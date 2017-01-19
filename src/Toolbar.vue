<template>
    <md-toolbar id="toolbar" class="md-dense">
        <span v-if="currentPath != 'home' && currentPath != 'day' && currentPath != 'days'">
            <md-button class="md-icon-button" @click="goBack()">
                <md-tooltip md-direction="right">back</md-tooltip>
                <md-icon>backspace</md-icon>&nbsp;
            </md-button>
        </span>
        <span v-else class="button-spacer">&nbsp;</span>
        <h2 id="toolbar-title" class="md-title">
            <router-link :to="{name: 'home'}" class="home-link">ibt2</router-link>
        </h2>
        <span v-if="loggedInUser.username">
            <md-button v-if="loggedInUser.isAdmin" id="users-icon" class="md-icon-button" @click="toUsersPage()">
                <md-tooltip md-direction="left">list of users</md-tooltip>
                <md-icon>people_outline</md-icon>
            </md-button>
            <md-button id="logged-in-icon" class="md-icon-button" @click="toUserPage()">
                <md-tooltip md-direction="left">personal page</md-tooltip>
                <md-icon>person_pin</md-icon>
            </md-button>
            <span id="logged-in" class="md-subheading">
                <router-link :to="userUrl" class="username-link">{{ loggedInUser.username }}</router-link>
            </span>
            <md-button id="logout-icon" class="md-icon-button" @click="logout()">
                <md-tooltip md-direction="left">logout</md-tooltip>
                <md-icon>exit_to_app</md-icon>
            </md-button>
        </span>
        <span v-else>
            <span id="login-form">
                <md-input-container id="username-input" class="login-input" md-inline>
                    <md-tooltip md-direction="bottom">login name or create a new user if it doesn't exist</md-tooltip>
                    <md-input ref="usernameInput" @keyup.enter.native="focusToPassword()" v-model="username" placeholder="username" md-inline />
                </md-input-container>&nbsp;
                <span id="password-block">
                    <md-input-container id="password-input" class="login-input" md-has-password md-inline>
                    <md-tooltip md-direction="bottom">login password or create a new user if it doesn't exist</md-tooltip>
                        <md-input ref="passwordInput" @keyup.enter.native="login()" v-model="password" placeholder="password" type="password" md-line />
                    </md-input-container>
                    <md-button id="login-button" class="md-icon-button" @click="login()">
                        <md-tooltip md-direction="left">login or create a new user if it doesn't exist</md-tooltip>
                        <md-icon>play_circle_outline</md-icon>
                    </md-button>
                </span>
            </span>
        </span>
        <ibt-snackbar ref="snackbarObj" />
        <ibt-dialog ref="dialogObj" />
    </md-toolbar>
</template>
<script>

import IbtDialog from './IbtDialog.vue';
import IbtSnackbar from './IbtSnackbar.vue';

export default {
    data () {
        return {
            username: '',
            password: '',
            dialog: {
                text: 'some error',
                ok: 'ok'
            }
        }
    },

    computed: {
        userUrl: function() {
            var id = this.loggedInUser._id;
            if (!id) {
                return '';
            }
            return '/user/' + this.loggedInUser._id;
        },

        loggedInUser() {
            return this.$store.state.loggedInUser;
        },

        currentPath() {
            return this.$route.name;
        }
    },

    beforeCreate: function() {
        this.usersUrl = this.$resource('users');
        this.currentUserUrl = this.$resource('users/current');
        this.loginUrl = this.$resource('login');
        this.logoutUrl = this.$resource('logout');
    },

    mounted: function() {
        this.getUserInfo();
    },

    methods: {
        goBack() {
            this.$router.back();
        },

        toUserPage() {
            this.$router.push(this.userUrl);
        },

        toUsersPage() {
            this.$router.push('/user/');
        },

        focusToLoginForm() {
            var that = this;
            setTimeout(function() { that.$refs.usernameInput.$el.focus(); }, 400);
        },

        focusToPassword() {
            this.$refs.passwordInput.$el.focus();
        },

        login(opt) {
            opt = opt || {};
            var user_data = {username: this.username, password: this.password};
            this.loginUrl.save(user_data).then((response) => {
                return response.json();
            }, (response) => {
                // Unable to login? Let's try to create the user!
                if (response.status == 401) {
                    if (opt.stopHere) {
                        this.$refs.dialogObj.show({text: 'failed to login and create a new user. Wrong username and password?'});
                    } else {
                        this.createUser(user_data);
                    }
                }
            }).then((data) => {
                this.getUserInfo();
            });
        },

        logout() {
            this.logoutUrl.get().then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'failed to logout'});
            }).then((json) => {
                this.$store.commit('clearLoggedInUser');
                this.$refs.snackbarObj.show('logged out');
            });
        },

        createUser(user_data) {
            user_data.username = user_data.username || {};
            user_data.username = user_data.username || this.username;
            user_data.password = user_data.password || this.password;
            this.usersUrl.save(user_data).then((response) => {
                return response.json();
            }, (response) => {
            }).then((json) => {
                this.login({stopHere: true});
            });

        },

        getUserInfo(callback) {
            this.currentUserUrl.get().then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to get user info'});
            }).then((data) => {
                data = data || {};
                this.$store.commit('setLoggedInUser', data);
                if (callback) {
                    callback(data);
                }
            });
        }
    },

    components: { IbtDialog, IbtSnackbar }
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
    background-color: white;
}

#username-input {
    display: inline;
    float: left;
    margin-right: 20px;
}

#password-input {
    display: inline;
    float: left;
}

#password-block {
    display: inline;
    float: right;
}

#login-button {
    height: 32px;
}

#logged-in-icon {
    margin-right: 0px;
    padding-right: 0px;
    color: #f6f72f !important;
}

#logged-in {
    position: relative;
    top: 10px;

}

#logout-icon {
    margin-left: 0px;
    padding-left: 0px;
}

.username-link {
    font-weight: bold;
    color: #f6f72f !important;
}

.button-spacer {
    width: 52px;
}

.home-link {
    font-weight: bold;
    color: white !important;
}
</style>
