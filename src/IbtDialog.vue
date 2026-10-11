<template>
    <IbtPrompt ref="prompt" title="Error" :content="text" :ok-text="ok"
               :cancel-text="''" confirmation />
</template>
<script>
export default {
    data: () => ({ text: 'Something went wrong', ok: 'ok' }),
    methods: {
        show(options = {}) {
            this.text = options.text || this.text;
            this.ok = options.ok || 'ok';
            this.$refs.prompt.open();
        },
    },
};
</script>
