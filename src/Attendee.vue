<template>
    <md-list-item :key="attendee._id">
        <md-icon>person</md-icon>
        <span v-if="!edit">{{attendee.name}}</span>
        <md-input-container md-inline v-if="edit">
            <md-input @keyup.enter.native="updateAttendee()" v-model="attendee.name" ref="updateAttendeeName" />
        </md-input-container>
        <md-button class="md-icon-button md-list-action" @click="editAttendee()">
            <md-icon>edit</md-icon>
        </md-button>
        <md-button class="md-icon-button md-list-action" @click="deleteAttendee()">
            <md-icon>cancel</md-icon>
        </md-button>
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

    beforeCreate: function() {
        this.attendeesUrl = this.$resource('attendees{/id}');
    },

    methods: {
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
