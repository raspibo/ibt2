<template>
    <!-- Material moves the dialog to document.body; keep a stable Vue 3 anchor. -->
    <span><md-dialog-alert :md-content="dialog.text" :md-ok-text="dialog.ok" ref="ibtDialogObj" /></span>
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
<style scoped>
</style>
