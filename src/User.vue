<template>
    <div id="user">
        <md-card>
            <md-card-header>
                <span class="md-title">User: {{ user.username }}</span>
            </md-card-header>
            <md-card-content>
                <md-input-container>
                    <label>Email</label>
                    <md-input v-model="user.email" />
                </md-input-container>

                <div class="md-body-2">Change password</div>
                <md-input-container id="password-input" md-has-password>
                    <label>New password</label>
                    <md-input v-model="password" type="password" />
                </md-input-container>

                <md-button class="md-raised md-primary" @click="save()">Save</md-button>
            </md-card-content>
        </md-card>
        <ibt-dialog ref="dialogObj" />
    </div>
</template>
<script>

import IbtDialog from './IbtDialog.vue';

export default {
    data () {
        return {
            user: {},
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
            var user_data = {password: this.password, email: this.user.email};
            this.usersUrl.update({id: this.user._id}, user_data).then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to save user settings'});
            }).then((data) => {
                this.user = data;
            });
        }
    },

    components: { IbtDialog }
}
</script>

<style>
#user {
    padding: 10px;
}
</style>
