<template>
    <div>
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
                <md-button v-if="loggedInUser.isAdmin" id="users-icon" class="md-icon-button" @click="toSettingsPage()">
                    <md-tooltip md-direction="left">global settings</md-tooltip>
                    <md-icon>settings</md-icon>
                </md-button>
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
                    <span id="username-input">
                        <strong id="login-label">Login:</strong>&nbsp;
                        <md-input-container id="username-input-container" class="login-input" md-inline>
                            <md-tooltip md-direction="bottom">login name or create a new user if it doesn't exist</md-tooltip>
                            <md-input ref="usernameInput" @keyup.enter.native="focusToPassword()" v-model="username" placeholder="username" md-inline  autocorrect="off" autocapitalize="none" />
                        </md-input-container>&nbsp;
                    </span>
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
        <vue-markdown v-if="settings.showMotd && settings.motd" class="motd" :source="settings.motd"></vue-markdown>
    </div>
</template>
<script>

import VueMarkdown from './VueMarkdown.vue';
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

        settings() {
            return this.$store.state.settings || {};
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

        toSettingsPage() {
            this.$router.push('/settings/');
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

    components: { IbtDialog, IbtSnackbar, VueMarkdown }
}

</script>
<style scoped>

#toolbar-title {
    flex: 1;
    min-width: 120px;
}

#toolbar {
    display: flex;
    align-items: center;
    padding: 10px 18px;
    background: linear-gradient(135deg, #1e293b 0%, #312e81 28%, #4338ca 100%);
    box-shadow: 0 12px 28px rgba(79, 70, 229, 0.2);
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

#toolbar .md-button {
    border-radius: 12px;
}

#toolbar .md-icon-button .md-icon {
    color: rgba(255, 255, 255, 0.9);
}

#login-form {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: flex-end;
}

.login-input {
    width: 180px;
    margin: 0;
    padding: 0 2px;
    min-height: 24px;
    line-height: 0;
}

#login-label {
    margin-top: 8px;
    color: white;
    font-weight: 600;
}

#username-input,
#password-block {
    display: flex;
    align-items: center;
}

#username-input {
    margin-right: 12px;
}

#password-block {
    gap: 8px;
}

#login-button {
    height: 32px;
}

#logged-in-icon {
    margin-right: 0;
    padding-right: 0;
    color: #f6f72f;
}

#logged-in {
    position: relative;
    top: 8px;
}

#logout-icon {
    margin-left: 0;
    padding-left: 0;
}

.username-link {
    font-weight: 700;
    color: #fef3c7 !important;
}

.button-spacer {
    width: 52px;
}

.home-link {
    font-weight: 800;
    letter-spacing: 0.06em;
    color: white !important;
}

#toolbar .md-input-container {
    min-height: 28px;
}

#toolbar .md-input-container input,
#toolbar .md-input-container label {
    color: white !important;
}

#toolbar .md-input-container:after,
#toolbar .md-input-container:before {
    background-color: rgba(255, 255, 255, 0.55) !important;
}

</style>
<style>

.motd {
    margin: 0 18px 18px;
    padding: 12px 18px;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(252, 231, 243, 0.96), rgba(224, 231, 255, 0.96));
    box-shadow: 0 10px 20px rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(148, 163, 184, 0.2);
}

.motd p {
    margin: 0;
    padding: 4px 0;
    text-align: center;
    color: #334155;
    line-height: 1.5;
}

</style>
