<template>
    <md-list-item :key="attendee._id">
        <md-icon>person</md-icon>
        <span v-if="!edit">{{attendee.name}}</span>
        <md-input-container md-inline v-if="edit">
            <md-input @keyup.enter.native="updateAttendee()" v-model="attendee.name" ref="updateAttendeeName" />
        </md-input-container>

        <md-menu v-if="isAuthorized(attendee.created_by)" md-align-trigger>
            <md-button class="md-icon-button" md-menu-trigger>
                <md-icon>more_vert</md-icon>
            </md-button>
            <md-menu-content>
                <md-menu-item @click="editAttendee()">
                    <span>edit</span>
                    <md-icon>edit</md-icon>
                </md-menu-item>
                <md-menu-item @click="deleteAttendee()">
                    <span>delete</span>
                    <md-icon>cancel</md-icon>
                </md-menu-item>
            </md-menu-content>
        </md-menu>
    </md-list-item>
</template>
<script>

export default {
    props: {attendee: {default: {}}},

    data: function () {
        return {
            edit: false
        }
    },

    computed: {
        loggedInUser() {
            return this.$store.state.loggedInUser;
        }
    },

    beforeCreate: function() {
        this.attendeesUrl = this.$resource('attendees{/id}');
    },

    methods: {
        isAuthorized(ownerID) {
            return this.$store.state.loggedInUser.isAdmin || (this.$store.state.loggedInUser._id && this.$store.state.loggedInUser._id == ownerID);
        },

        editAttendee() {
            this.edit = true;
            // FIXME: it's so wrong it hurts, but any other attempt to set the focus
            // failed, being called too early.  Also, I don't know how I can access
            // Vue.nextTick from here.
            var that = this;
            setTimeout(function() { that.$refs.updateAttendeeName.$el.focus(); }, 400);
        },

        updateAttendee() {
            this.attendeesUrl.update({id: this.attendee._id}, this.attendee).then((response) => {
                return response.json();
            }, (response) => {
                alert('updateAttendee: failed to update resource');
            }).then((json) => {
                this.edit = false;
                this.$emit('updated');
            });
        },

        deleteAttendee() {
            this.attendeesUrl.delete({id: this.attendee._id}).then((response) => {
                return response.json();
            }, (response) => {
                alert('deleteAttendee: failed to delete resource');
            }).then((json) => {
                this.$emit('updated');
            });
        }
    }
};

</script>
<style>

.md-list-item .md-list-item-holder>.md-icon:first-child {
    margin-right: 16px;
}

</style>
