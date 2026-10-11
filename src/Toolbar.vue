<template>
    <div>
        <div id="toolbar" class="ibt-toolbar ibt-dense">
            <span v-if="currentPath != 'home' && currentPath != 'day' && currentPath != 'days'">
                <Button text aria-label="Back" class="ibt-icon-button" @click="goBack()">

                    <i class="ibt-icon pi pi-arrow-left" aria-hidden="true"></i>&nbsp;
                </Button>
            </span>
            <span v-else class="button-spacer">&nbsp;</span>
            <h2 id="toolbar-title" class="ibt-title">
                <router-link :to="{name: 'home'}" class="home-link">ibt2</router-link>
            </h2>
            <span v-if="loggedInUser.username">
                <Button text v-if="loggedInUser.isAdmin" id="settings-icon" aria-label="Global settings" class="ibt-icon-button" @click="toSettingsPage()">

                    <i class="ibt-icon pi pi-cog" aria-hidden="true"></i>
                </Button>
                <Button text v-if="loggedInUser.isAdmin" id="users-icon" aria-label="Users" class="ibt-icon-button" @click="toUsersPage()">

                    <i class="ibt-icon pi pi-users" aria-hidden="true"></i>
                </Button>
                <Button text id="logged-in-icon" aria-label="Personal page" class="ibt-icon-button" @click="toUserPage()">

                    <i class="ibt-icon pi pi-user" aria-hidden="true"></i>
                </Button>
                <span id="logged-in" class="ibt-subheading">
                    <router-link :to="userUrl" class="username-link">{{ loggedInUser.username }}</router-link>
                </span>
                <Button text id="logout-icon" aria-label="Logout" class="ibt-icon-button" @click="logout()">

                    <i class="ibt-icon pi pi-sign-out" aria-hidden="true"></i>
                </Button>
            </span>
            <span v-else>
                <span id="login-form">
                    <span id="username-input">
                        <strong id="login-label">Login:</strong>&nbsp;
                        <label id="username-input-container" class="ibt-input-container login-input">

                            <InputText ref="usernameInput" aria-label="Username" @keyup.enter="focusToPassword()" v-model="username" placeholder="username"  autocorrect="off" autocapitalize="none" />
                        </label>&nbsp;
                    </span>
                    <span id="password-block">
                        <label id="password-input" class="ibt-input-container login-input">

                            <Password ref="passwordInput" aria-label="Password" :input-props="{ onKeyup: passwordKeyup }" v-model="password" placeholder="password" toggle-mask :feedback="false" />
                        </label>
                        <Button text id="login-button" aria-label="Login" class="ibt-icon-button" @click="login()">

                            <i class="ibt-icon pi pi-sign-in" aria-hidden="true"></i>
                        </Button>
                    </span>
                </span>
            </span>
            <ibt-snackbar ref="snackbarObj" />
            <ibt-dialog ref="dialogObj" />
        </div>
        <vue-markdown v-if="settings.showMotd && settings.motd" class="motd" :source="settings.motd"></vue-markdown>
    </div>
</template>
<script>
import { resource } from './api.js';

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
        this.usersUrl = resource('users');
        this.currentUserUrl = resource('users/current');
        this.loginUrl = resource('login');
        this.logoutUrl = resource('logout');
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
            this.$refs.passwordInput.$el.querySelector('input').focus();
        },

        passwordKeyup(event) {
            if (event.key === 'Enter') this.login();
        },

        login(opt) {
            opt = opt || {};
            var user_data = {username: this.username, password: this.password};
            this.loginUrl.save(user_data).then((response) => {
                return response.json();
            }).then((data) => {
                this.getUserInfo();
            }).catch((response) => {
                // Unable to login? Let's try to create the user!
                if (response.status == 401) {
                    if (opt.stopHere) {
                        this.$refs.dialogObj.show({text: 'failed to login and create a new user. Wrong username and password?'});
                    } else {
                        this.createUser(user_data);
                    }
                } else {
                    this.$refs.dialogObj.show({text: 'unable to sign in'});
                }
            });
        },

        logout() {
            this.logoutUrl.get().then((response) => {
                return response.json();
            }).then((json) => {
                this.$store.commit('clearLoggedInUser');
                this.username = '';
                this.password = '';
                this.$refs.snackbarObj.show('logged out');
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'failed to logout'});
            });
        },

        createUser(user_data) {
            user_data.username = user_data.username || this.username;
            user_data.password = user_data.password || this.password;
            this.usersUrl.save(user_data).then((response) => {
                return response.json();
            }).then((json) => {
                this.login({stopHere: true});
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to create the user'});
            });

        },

        getUserInfo(callback) {
            this.currentUserUrl.get().then((response) => {
                return response.json();
            }).then((data) => {
                data = data || {};
                this.$store.commit('setLoggedInUser', data);
                if (callback) {
                    callback(data);
                }
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to get user info'});
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
    flex-wrap: wrap;
    padding: 10px 18px;
    background: linear-gradient(135deg, #1e293b 0%, #312e81 28%, #4338ca 100%);
    box-shadow: 0 12px 28px rgba(79, 70, 229, 0.2);
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

#toolbar .ibt-button {
    border-radius: 12px;
}

#toolbar .ibt-icon-button :deep(.ibt-icon) {
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

#toolbar .ibt-input-container {
    min-height: 28px;
}

@media screen and (max-width: 600px) {
    .button-spacer {
        display: none;
    }

    #toolbar-title {
        min-width: 80px;
    }

    #login-form {
        padding-bottom: 8px;
    }
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
