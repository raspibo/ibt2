<template>
    <div id="user">
        <md-card>
            <md-card-header>
                <span class="md-title">User: {{ user.username }}</span>
            </md-card-header>
            <md-card-content>
                <md-input-container>
                    <label>Email</label>
                    <md-input v-model="user.email" autocorrect="off" autocapitalize="none" />
                </md-input-container>

                <div class="md-body-2">Change password</div>
                <md-input-container id="password-input" md-has-password>
                    <label>New password</label>
                    <md-input v-model="user.password" type="password" />
                </md-input-container>

                <md-switch v-if="loggedInUser.isAdmin && loggedInUser.username != user.username" v-model="user.isAdmin" class="md-warn">is admin</md-switch>

                <br />
                <md-button id="save-button" class="md-raised md-primary" @click="save()">Save</md-button>
            </md-card-content>
        </md-card>
        <ibt-snackbar ref="snackbarObj" />
        <ibt-dialog ref="dialogObj" />
    </div>
</template>
<script>

import IbtDialog from './IbtDialog.vue';
import IbtSnackbar from './IbtSnackbar.vue';

export default {
    data() {
        return {
            user: {_id: null, email: '', password: null, isAdmin: false},
            password: null
        }
    },

    computed: {
        loggedInUser() {
            return this.$store.state.loggedInUser;
        }
    },

    beforeCreate: function() {
        this.usersUrl = this.$resource('users{/id}');
    },

    mounted: function() {
        this.$router.afterEach((to, from) => {
            if (this.user._id && this.user._id != this.$route.params.id &&
                    to.name == from.name && to.name == 'user') {
                this.getUser(this.$route.params.id);
            }
        });
        this.getUser(this.$route.params.id);
    },

    methods: {
        getUser(id) {
            this.usersUrl.get({id: id}).then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to get user'});
            }).then((data) => {
                this.user = data || {};
            });
        },

        save() {
            this.usersUrl.update({id: this.user._id}, this.user).then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to save user settings'});
            }).then((data) => {
                this.user = data;
                this.$refs.snackbarObj.show('user saved');
            });
        }
    },

    components: { IbtDialog, IbtSnackbar }
}
</script>

<style scoped>

#user {
    padding: 10px;
}

#save-button {
    margin-top: 40px;
}

</style>
