<template>
    <Teleport to="body">
        <Message v-if="visible" :key="serial" class="ibt-snackbar" closable severity="success"
                 :life="4000" @close="visible = false" @life-end="visible = false">
            {{ message }}
        </Message>
    </Teleport>
</template>
<script>
import Message from 'primevue/message';
export default {
    components: { Message },
    data: () => ({ visible: false, message: '', serial: 0 }),
    methods: {
        show(message = 'Something happened') { this.message = message; this.serial++; this.visible = true; },
    },
};
</script>
