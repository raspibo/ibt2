<template>
    <Dialog :visible="visible" modal :header="title" class="ibt-dialog"
            :style="{ width: '30rem', maxWidth: 'calc(100vw - 2rem)' }"
            @update:visible="value => { if (!value) close('cancel'); }">
        <p v-if="content">{{ content }}</p>
        <Textarea v-if="!confirmation" :model-value="modelValue" :aria-label="title"
                  autofocus rows="4" fluid @update:model-value="$emit('update:modelValue', $event)" />
        <template #footer>
            <Button v-if="cancelText" :label="cancelText" severity="secondary" @click="close('cancel')" />
            <Button :label="okText" @click="close('ok')" />
        </template>
    </Dialog>
</template>
<script>
export default {
    props: {
        modelValue: { default: '' }, title: String, content: String,
        okText: { default: 'ok' }, cancelText: { default: 'cancel' }, confirmation: Boolean,
    },
    emits: ['update:modelValue', 'open', 'close'],
    data: () => ({ visible: false }),
    methods: {
        open() { this.$emit('open'); this.visible = true; },
        close(action) {
            if (!this.visible) return;
            this.visible = false;
            this.$emit('close', action);
        },
    },
};
</script>
