<template>
    <div id="user">
        User
    </div>
</template>
<script>

export default {
    data () {
        return {
        }
    },

    beforeCreate: function() {
        this.userUrl = this.$resource('users');
    },

    mounted: function() {
    },

    methods: {
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
    },

    components: {
    }
}
</script>

<style>
</style>
