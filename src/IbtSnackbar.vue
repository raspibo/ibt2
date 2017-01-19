<template>
    <md-snackbar md-position="top center" ref="snackbar">
        <span>{{ snackbackMessage }}</span>
        <md-button @click="$refs.snackbar.close()" class="snackbar-close">[x]</md-button>
    </md-snackbar>
</template>
<script>

export default {
    data: function() {
        return {snackbackMessage: 'something happened'};
    },

    methods: {
        show(message) {
            this.snackbackMessage = message || snackbackMessage;
            this.$refs.snackbar.open();
        }
    }
}

</script>
<style>

.snackbar-close {
    font-weight: bold;
    color: #f6f72f;
}

</style>
