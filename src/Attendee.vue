<template>
    <md-list-item class="attendee-list-item md-double-line" :key="attendee._id">
        <md-icon md-iconset="ion-person"></md-icon>
        <div v-if="!edit" class="md-list-text-container">
            <span>{{ attendee.name }}</span>
            <vue-markdown v-if="attendee.notes" ref="attendeeNotes" @click.native="toggleNotes()" class="attendee-notes" :source="attendee.notes" :break="false"></vue-markdown>
        </div>
        <div v-if="edit">
            <md-input-container md-inline>
                <md-input @keyup.enter.native="updateAttendee()" @keydown.esc.native="edit = false" v-model="attendee.name" ref="updateAttendeeName" />
            </md-input-container>
            <div class="notes-editor-list-item">
                <md-input-container md-inline>
                    <label>notes</label>
                    <md-input @keyup.enter.native="updateAttendee()" @keydown.esc.native="edit = false" v-model="attendee.notes" />
                </md-input-container>
            </div>
        </div>

        <md-menu v-if="isAuthorized(attendee.created_by) && !edit" md-align-trigger>
            <md-button class="md-icon-button" md-menu-trigger>
                <md-icon md-iconset="ion-android-more-vertical"></md-icon>
            </md-button>
            <md-menu-content>
                <md-menu-item @click.native="editAttendee()">
                    <span>edit</span>
                    <md-icon md-iconset="ion-edit"></md-icon>
                </md-menu-item>
                <md-menu-item @click.native="deleteAttendee()">
                    <span>delete</span>
                    <md-icon md-iconset="ion-trash-a"></md-icon>
                </md-menu-item>
            </md-menu-content>
        </md-menu>
        <ibt-dialog ref="dialogObj" />
    </md-list-item>
</template>
<script>

import IbtDialog from './IbtDialog.vue';
import VueMarkdown from 'vue-markdown';

export default {
    props: {attendee: {default: {}}},

    data: function () {
        return {
            edit: false,
            expandedNote: false
        }
    },

    computed: {
        loggedInUser() {
            return this.$store.state.loggedInUser;
        },
        settings() {
            return this.$store.state.settings || {};
        }
    },

    beforeCreate: function() {
        this.attendeesUrl = this.$resource('attendees{/id}');
    },

    methods: {
        isAuthorized(ownerID) {
            return (!ownerID && !this.$store.state.settings.protectUnregistered) || this.$store.state.loggedInUser.isAdmin || (this.$store.state.loggedInUser._id && this.$store.state.loggedInUser._id == ownerID);
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
        },

        toggleNotes() {
            if (!this.expandedNote) {
                $(this.$refs.attendeeNotes.$el).find('p').css('text-overflow', 'initial');
                $(this.$refs.attendeeNotes.$el).find('p').css('white-space', 'initial');
                this.expandedNote = true;
            } else {
                $(this.$refs.attendeeNotes.$el).find('p').css('text-overflow', 'ellipsis');
                $(this.$refs.attendeeNotes.$el).find('p').css('white-space', 'nowrap');
                this.expandedNote = false;
            }
        }
    },

    components: { IbtDialog, VueMarkdown }
};

</script>
<style>

.md-list-item .md-list-item-holder>.md-icon:first-child {
    margin-right: 16px;
}

.attendee-list-item {
    min-width: 250px;
}

.attendee-list-item .md-list-item-container {
    padding-left: 0px;
    padding-right: 0px;
}

.attendee-notes {
    font-style: italic !important;
}

.notes-editor-list-item {
    margin-bottom: 0px !important;
    padding-left: 16px;
}

.notes-editor-list-item ul {
    padding-top: 0px !important;
    padding-bottom: 0px !important;
}

.notes-editor-list-item .md-theme-default.md-list {
    background-color: transparent;
}


.notes-editor-list-item button:hover {
    background-color: transparent !important;
}

.attendee-notes > p {
    margin: 0px;
    font-style: italic;
    margin: 0px;
    text-overflow: ellipsis;
    max-width: 400px;
    overflow: hidden;
    white-space: nowrap;
    color: rgba(0, 0, 0, 0.54);
}

</style>
