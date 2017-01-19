<template>
    <md-dialog-alert :md-content="dialog.text" :md-ok-text="dialog.ok" ref="ibtDialogObj" />
</template>
<script>

export default {
    props: {dialog: {default: function(){return {text: 'snap! some error has occurred', ok: 'ok'}}}},

    methods: {
        show(opts) {
            if (!opts) {
                opts = {};
            }
            this.dialog.text = opts.text || this.dialog.text;
            this.dialog.ok = opts.ok || this.dialog.ok;
            this.$refs.ibtDialogObj.open();
        }
    }
}
</script>
<style>
</style>
