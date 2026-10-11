<template>
    <div class="ibt-menu">
        <Button icon="pi pi-ellipsis-v" text rounded aria-label="Actions" aria-haspopup="true"
                :aria-controls="menuId" @click="$refs.menu.toggle($event)" />
        <Menu ref="menu" :id="menuId" :model="items" popup />
    </div>
</template>
<script>
import { useId } from 'vue';
import Menu from 'primevue/menu';
export default {
    components: { Menu },
    props: { items: { type: Array, required: true } },
    setup() { return { menuId: useId() }; },
};
</script>
