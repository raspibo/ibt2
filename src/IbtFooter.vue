<template>
    <md-toolbar id="footer" class="md-dense">
        <span><a href="https://github.com/raspibo/ibt2">ibt2</a> &copy; <a href="http://www.raspibo.org/">RaspiBO</a></span>
    </md-toolbar>
</template>
<script>

export default {}

</script>
<style scoped>

#footer {
    text-align: center;
    color: #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 44px;
    left: 0;
    right: 0;
    bottom: 0;
    position: static;
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.96), rgba(49, 46, 129, 0.96));
    box-shadow: 0 -8px 24px rgba(15, 23, 42, 0.12);
}

#footer, #footer a {
    color: rgba(255, 255, 255, 0.8);
    transition: color 0.2s ease;
}

#footer:hover, #footer:hover a {
    color: rgba(255, 255, 255, 1);
}

#footer:hover a {
    text-decoration: underline;
}

</style>
