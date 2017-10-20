<template>
    <div id="users">
        <md-card>
            <md-card-header>
                <span class="md-title">Users</span>
            </md-card-header>
            <md-card-content>
                <md-table>
                    <md-table-header>
                        <md-table-row>
                            <md-table-head>Username</md-table-head>
                            <md-table-head class="center-content">Email</md-table-head>
                            <md-table-head class="center-content">Admin</md-table-head>
                            <md-table-head v-if="loggedInUser.isAdmin" class="center-content">Delete</md-table-head>
                        </md-table-row>
                    </md-table-header>
                    <md-table-body>
                        <md-table-row v-for="(user, index) in users" :key="user._id">
                            <md-table-cell>
                                <router-link :to="userLink(user._id)" class="md-raised md-primary">
                                    {{user.username}}
                                </router-link>
                            </md-table-cell>
                            <md-table-cell class="center-content">
                                {{user.email}}
                            </md-table-cell>
                            <md-table-cell class="center-content">
                                <md-icon v-if="user.isAdmin" md-iconset="ion-android-done"></md-icon>
                            </md-table-cell>
                            <md-table-cell v-if="loggedInUser.isAdmin" class="center-content">
                                <md-button class="md-icon-button" @click="deleteUser(user._id)">
                                    <md-icon md-iconset="ion-trash-a"></md-icon>
                                </md-button>
                            </md-table-cell>
                        </md-table-row>
                    </md-table-body>
                </md-table>
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
            users: []
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
        this.getUsers();
    },

    methods: {
        userLink(id) {
            return '/user/' + id;
        },

        getUsers() {
            this.usersUrl.get().then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to get the list of users'});
            }).then((data) => {
                this.users = data.users || [];
            });
        },

        deleteUser(userId) {
            this.usersUrl.delete({id: userId}).then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to delete the user: ' + response.body.message});
            }).then((data) => {
                this.getUsers();
            });
        }
    },

    components: { IbtDialog }
}

</script>
<style>

#users {
    padding: 10px;
}

.center-content > .md-table-head-container {
    text-align: center;
}

.center-content > .md-table-cell-container {
    text-align: center;
    display: block !important;
}

</style>
