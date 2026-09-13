<template>
    <div class="vue-markdown" v-html="compiledMarkdown"></div>
</template>

<script>
import { marked } from 'marked';

// Configure marked with sensible defaults
marked.setOptions({
    gfm: true,
    breaks: false
});

export default {
    name: 'VueMarkdown',
    props: {
        source: {
            type: String,
            default: ''
        },
        breaks: {
            type: Boolean,
            default: false
        }
    },
    computed: {
        compiledMarkdown() {
            if (!this.source) return '';
            return marked.parse(this.source, {
                breaks: this.breaks
            });
        }
    }
};
</script>
