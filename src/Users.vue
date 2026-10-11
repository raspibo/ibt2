<template>
    <div id="users">
        <article class="ibt-card">
            <header class="ibt-card-header">
                <span class="ibt-title">Users</span>
            </header>
            <div class="ibt-card-content">
                <table class="users-table">
                    <thead>
                        <tr>
                            <th>Username</th>
                            <th class="center-content">Email</th>
                            <th class="center-content">Admin</th>
                            <th v-if="loggedInUser.isAdmin" class="center-content">Delete</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(user, index) in users" :key="user._id">
                            <td>
                                <router-link :to="userLink(user._id)" class="ibt-raised ibt-primary">
                                    {{user.username}}
                                </router-link>
                            </td>
                            <td class="center-content">
                                {{user.email}}
                            </td>
                            <td class="center-content">
                                <i v-if="user.isAdmin" class="ibt-icon pi pi-check" aria-hidden="true"></i>
                            </td>
                            <td v-if="loggedInUser.isAdmin" class="center-content">
                                <Button text aria-label="Delete user" class="ibt-icon-button" @click="deleteUser(user._id)">
                                    <i class="ibt-icon pi pi-trash" aria-hidden="true"></i>
                                </Button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </article>
        <ibt-dialog ref="dialogObj" />
    </div>
</template>
<script>
import { resource } from './api.js';

import IbtDialog from './IbtDialog.vue';

export default {
    data () {
        return {
            users: []
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

    mounted: function() {
        this.getUsers();
    },

    methods: {
        userLink(id) {
            return '/user/' + id;
        },

        getUsers() {
            this.usersUrl.get().then((response) => {
                return response.json();
            }).then((data) => {
                this.users = data.users || [];
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to get the list of users'});
            });
        },

        deleteUser(userId) {
            this.usersUrl.delete({id: userId}).then((response) => {
                return response.json();
            }).then((data) => {
                this.getUsers();
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to delete the user: ' + response.body.message});
            });
        }
    },

    components: { IbtDialog }
}

</script>
<style scoped>

#users {
    padding: 10px;
}

</style>
