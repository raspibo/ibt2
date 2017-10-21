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
    color: white;
    display: block;
    vertical-align: middle;
    min-height: 16px;
    left: 0px;
    right: 0px;
    bottom: 0px;
    position: absolute;
    background-color: #b3e5fc;
}

#footer, #footer a {
    color: rgba(0, 0, 0, .40);
    transition: color 0.5s ease;
}

#footer:hover, #footer:hover a {
    color: rgba(0, 0, 0, .87);
}

#footer:hover a {
    text-decoration: underline;
}

</style>
