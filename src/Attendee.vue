<template>
    <div class="ibt-list-item-container attendee-list-item" :key="attendee._id">
        <i class="ibt-icon pi pi-user" aria-hidden="true"></i>
        <div v-if="!edit" class="ibt-list-text-container">
            <span>{{ attendee.name }}</span>
            <vue-markdown v-if="attendee.notes" ref="attendeeNotes" @click="toggleNotes()" class="attendee-notes" :source="attendee.notes" :break="false"></vue-markdown>
        </div>
        <div v-if="edit" class="attendee-editor">
            <label class="ibt-input-container">
                <InputText aria-label="Attendee name" @keydown.enter.prevent="updateAttendee()" @keydown.esc="edit = false" v-model="attendee.name" ref="updateAttendeeName" />
            </label>
            <div class="notes-editor-list-item">
                <label class="ibt-input-container">
                    <span class="field-label">notes</span>
                    <InputText @keydown.enter.prevent="updateAttendee()" @keydown.esc="edit = false" v-model="attendee.notes" />
                </label>
            </div>
        </div>

        <ibt-menu v-if="isAuthorized(attendee.created_by) && !edit" :items="menuItems" />
        <ibt-dialog ref="dialogObj" />
    </div>
</template>
<script>
import { resource } from './api.js';

import IbtDialog from './IbtDialog.vue';
import IbtMenu from './IbtMenu.vue';
import VueMarkdown from './VueMarkdown.vue';

export default {
    props: {attendee: {default: () => ({})}},
    emits: ['updated'],

    data: function () {
        return {
            edit: false,
            expandedNote: false
        }
    },

    computed: {
        menuItems() {
            return [
                { label: 'edit', icon: 'pi pi-pencil', command: () => this.editAttendee() },
                { label: 'delete', icon: 'pi pi-trash', command: () => this.deleteAttendee() },
            ];
        },
        loggedInUser() {
            return this.$store.state.loggedInUser;
        },
        settings() {
            return this.$store.state.settings || {};
        }
    },

    beforeCreate: function() {
        this.attendeesUrl = resource('attendees{/id}');
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
            }).then((json) => {
                this.edit = false;
                this.$emit('updated');
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to update the attendee'});
            });
        },

        deleteAttendee() {
            this.attendeesUrl.delete({id: this.attendee._id}).then((response) => {
                return response.json();
            }).then((json) => {
                this.$emit('updated');
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to delete the attendee'});
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

    components: { IbtMenu, IbtDialog, VueMarkdown }
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

.attendee-list-item {
    padding: 10px 12px;
    border-radius: 14px;
    background: rgba(248, 250, 252, 0.9);
    border: 1px solid rgba(148, 163, 184, 0.2);
}

</style>
