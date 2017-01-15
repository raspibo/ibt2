<template>
    <div id="user">
        User {{loggedInUser}}
    </div>
</template>
<script>

export default {
    data () {
        return {
        }
    },

    computed: {
        count() {
            return this.$store.state.count;
        },
        loggedInUser() {
            return this.$store.state.loggedInUser;
        }
    },

    beforeCreate: function() {
        this.userUrl = this.$resource('users');
    },

    mounted: function() {
    },

    methods: {
    },

    components: {
    }
}
</script>

<style>
</style>
