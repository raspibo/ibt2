<template>
    <div id="user">
        <article class="ibt-card">
            <header class="ibt-card-header">
                <span class="ibt-title">User: {{ user.username }}</span>
            </header>
            <div class="ibt-card-content">
                <label class="ibt-input-container">
                    <span class="field-label">Email</span>
                    <InputText v-model="user.email" autocorrect="off" autocapitalize="none" />
                </label>

                <div class="ibt-body-2">Change password</div>
                <label id="password-input" class="ibt-input-container">
                    <span class="field-label">New password</span>
                    <Password v-model="user.password" toggle-mask :feedback="false" />
                </label>

                <label v-if="loggedInUser.isAdmin && loggedInUser.username != user.username" class="setting-switch"><ToggleSwitch v-model="user.isAdmin" /><span>is admin</span></label>

                <br />
                <Button id="save-button" class="ibt-raised ibt-primary" @click="save()">Save</Button>
            </div>
        </article>
        <ibt-snackbar ref="snackbarObj" />
        <ibt-dialog ref="dialogObj" />
    </div>
</template>
<script>
import { resource } from './api.js';

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
        this.usersUrl = resource('users{/id}');
    },

    watch: {
        '$route.params.id'(id) { if (id) this.getUser(id); },
    },
    mounted: function() {
        this.getUser(this.$route.params.id);
    },

    methods: {
        getUser(id) {
            this.usersUrl.get({id: id}).then((response) => {
                return response.json();
            }).then((data) => {
                this.user = data || {};
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to get user'});
            });
        },

        save() {
            this.usersUrl.update({id: this.user._id}, this.user).then((response) => {
                return response.json();
            }).then((data) => {
                this.user = data;
                this.$refs.snackbarObj.show('user saved');
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to save user settings'});
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
