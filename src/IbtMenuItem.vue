<template>
    <li class="md-list-item md-menu-item" role="none">
        <button type="button" class="md-list-item-container md-button" role="menuitem" @click="select"
                @keydown.enter.prevent.stop @keyup.enter.prevent.stop="select"
                @keydown.space.prevent.stop @keyup.space.prevent.stop="select">
            <slot></slot>
        </button>
    </li>
</template>
<script>
// Vue Material 0.7 selects its clickable list renderer through Vue 2's
// functional data.on API. Under @vue/compat it renders a non-clickable row.
// Keep its menu styling, but use a native button for pointer and keyboard input.
export default {
    emits: ['click'],
    methods: {
        select(event) {
            let parent = this.$parent;
            while (parent && parent.$options.name !== 'md-menu') {
                parent = parent.$parent;
            }
            if (parent) parent.close();
            this.$emit('click', event);
        }
    }
};
</script>
