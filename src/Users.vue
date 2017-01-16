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
                            <md-table-head>Email</md-table-head>
                        </md-table-row>
                    </md-table-header>
                    <md-table-body>
                        <md-table-row v-for="(user, index) in users" :key="user._id">
                            <md-table-cell>
                                <router-link :to="userLink(user._id)" class="md-raised md-primary">
                                    {{user.username}}
                                </router-link>
                            </md-table-cell>
                            <md-table-cell>
                                {{user.email}}
                            </md-table-cell>
                        </md-table-row>
                    </md-table-body>
                </md-table>
            </md-card-content>
        </md-card>
    </div>
</template>
<script>

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
                alert('getUsers: unable to get resource');
            }).then((data) => {
                this.users = data.users || [];
            });
        },

        deleteUser(userId) {
            this.usersUrl.update({id: userId}).then((response) => {
                return response.json();
            }, (response) => {
                alert('deleteUser: unable to get resource');
            }).then((data) => {
            });
        }
    }
}
</script>

<style>
#users {
    padding: 10px;
}
</style>

