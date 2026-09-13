<template>
    <md-list-item class="attendee-list-item md-double-line" :key="attendee._id">
        <md-icon>person</md-icon>
        <div v-if="!edit" class="md-list-text-container">
            <span>{{ attendee.name }}</span>
            <vue-markdown v-if="attendee.notes" ref="attendeeNotes" @click="toggleNotes()" class="attendee-notes" :source="attendee.notes" :break="false"></vue-markdown>
        </div>
        <div v-if="edit" class="attendee-editor">
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
                <md-icon>more_vert</md-icon>
            </md-button>
            <ibt-menu-content>
                <ibt-menu-item @click="editAttendee()">
                    <span>edit</span>
                    <md-icon>edit</md-icon>
                </ibt-menu-item>
                <ibt-menu-item @click="deleteAttendee()">
                    <span>delete</span>
                    <md-icon>delete</md-icon>
                </ibt-menu-item>
            </ibt-menu-content>
        </md-menu>
        <ibt-dialog ref="dialogObj" />
    </md-list-item>
</template>
<script>

import IbtDialog from './IbtDialog.vue';
import IbtMenuItem from './IbtMenuItem.vue';
import IbtMenuContent from './IbtMenuContent.vue';
import VueMarkdown from './VueMarkdown.vue';

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
            this.$nextTick(() => this.$refs.updateAttendeeName.$el.focus());
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
            var el = this.$refs.attendeeNotes && this.$refs.attendeeNotes.$el;
            if (!el) return;
            var p = el.querySelector('p');
            if (!p) return;
            if (!this.expandedNote) {
                p.style.textOverflow = 'initial';
                p.style.whiteSpace = 'initial';
                this.expandedNote = true;
            } else {
                p.style.textOverflow = 'ellipsis';
                p.style.whiteSpace = 'nowrap';
                this.expandedNote = false;
            }
        }
    },

    components: { IbtMenuContent, IbtMenuItem, IbtDialog, VueMarkdown }
};

</script>
<style scoped>

.attendee-list-item {
    min-width: 0;
    margin-bottom: 8px;
}

.attendee-editor {
    flex: 1;
    min-width: 0;
}

.attendee-notes {
    font-style: italic !important;
}

.notes-editor-list-item {
    margin-bottom: 0 !important;
    padding-left: 0;
}

.notes-editor-list-item ul {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

.notes-editor-list-item .md-theme-default.md-list {
    background-color: transparent;
}


.notes-editor-list-item button:hover {
    background-color: transparent !important;
}

.attendee-notes > p {
    margin: 0;
    font-style: italic;
    text-overflow: ellipsis;
    max-width: 400px;
    overflow: hidden;
    white-space: nowrap;
    color: rgba(15, 23, 42, 0.62);
}

</style>
<style>

.md-list-item .md-list-item-holder>.md-icon:first-child {
    margin-right: 16px;
    color: #4f46e5;
}

.attendee-list-item .md-list-item-container {
    padding: 10px 12px;
    border-radius: 14px;
    background: rgba(248, 250, 252, 0.9);
    border: 1px solid rgba(148, 163, 184, 0.2);
}

</style>
