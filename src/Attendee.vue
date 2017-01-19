<template>
    <md-list-item class="attendee-list-item" :key="attendee._id">
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
        <ibt-dialog ref="dialogObj" />
    </md-list-item>
</template>
<script>

import IbtDialog from './IbtDialog.vue';

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
            return !ownerID || this.$store.state.loggedInUser.isAdmin || (this.$store.state.loggedInUser._id && this.$store.state.loggedInUser._id == ownerID);
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
                this.$refs.dialogObj.show({text: 'unable to update the attendee'});
            }).then((json) => {
                this.edit = false;
                this.$emit('updated');
            });
        },

        deleteAttendee() {
            this.attendeesUrl.delete({id: this.attendee._id}).then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to delete the attendee'});
            }).then((json) => {
                this.$emit('updated');
            });
        }
    },

    components: {IbtDialog}
};

</script>
<style>
.md-list-item .md-list-item-holder>.md-icon:first-child {
    margin-right: 16px;
}

.attendee-list-item {
    min-width: 250px;
}
</style>
