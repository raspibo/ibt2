<template>
    <div class="vue-markdown" v-html="compiledMarkdown"></div>
</template>

<script>
import { marked } from 'marked';
import DOMPurify from 'dompurify';

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
            return DOMPurify.sanitize(marked.parse(this.source, {
                breaks: this.breaks
            }));
        }
    }
};
</script>
