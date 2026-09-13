<template>
    <div class="md-menu-content" tabindex="-1" role="menu" @keydown="navigate">
        <md-list><slot></slot></md-list>
    </div>
</template>
<script>
// Keep md-menu's positioning and dismissal, without the legacy content's
// $children traversal and md-option-only keyboard activation.
export default {
    methods: {
        navigate(event) {
            const buttons = Array.from(this.$el.querySelectorAll('[role="menuitem"]'));
            const index = buttons.indexOf(document.activeElement);
            let next;
            if (event.key === 'ArrowDown') next = (index + 1) % buttons.length;
            if (event.key === 'ArrowUp') next = (index <= 0 ? buttons.length : index) - 1;
            if (event.key === 'Home') next = 0;
            if (event.key === 'End') next = buttons.length - 1;
            if (next !== undefined && buttons[next]) {
                event.preventDefault();
                buttons[next].focus();
            }
            if (event.key === 'Escape' || event.key === 'Tab') {
                let parent = this.$parent;
                while (parent && parent.$options.name !== 'md-menu') parent = parent.$parent;
                if (parent) parent.close();
                if (event.key === 'Escape') event.preventDefault();
            }
        }
    }
};
</script>
