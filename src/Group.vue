<template>
    <!-- XXX: too much duplication in this template -->
    <div class="ibt-layout layout-column group-layout">
        <article v-if="!addNewGroup" @mouseenter="focusToNewAttendee()" @mouseleave="hasFocus = false" class="ibt-card">
            <header ref="currentGroup" class="ibt-card-header group-header">
                <div class="ibt-layout layout-row">
                    <div class="ibt-title group-title">
                        <i class="ibt-icon pi pi-folder-open group-icon" aria-hidden="true"></i>&nbsp;{{ group.group }}&nbsp;<span class="counter">{{ counter }}</span>
                    </div>
                    <ibt-menu v-if="loggedInUser.isAdmin || !settings.protectGroupNotes || !settings.protectGroupName" :items="menuItems" />
                </div>
                <div v-if="group.notes" class="ibt-layout layout-row">

                    <vue-markdown ref="groupNotes" @click="toggleNotes()" class="group-notes" :source="group.notes" :break="false"></vue-markdown>
                </div>
            </header>
            <div class="ibt-card-content group-card">
                <div class="ibt-list">
                    <attendee v-for="attendee in group.attendees || []" :attendee="attendee" :key="attendee._id" @updated="reload" />
                    <div class="ibt-list-item-container attendee-add">
                        <Button text rounded icon="pi pi-user-plus" aria-label="Add attendee"
                                @click="addAttendee(group.group)" :class="{'ibt-primary': hasFocus}" />
                        <label class="ibt-input-container new-attendee">
                            <span class="field-label"><i>new attendee</i></span>
                            <InputText ref="newAttendeeInput" @keyup.enter="addAttendee(group.group)" v-model="newAttendee" />
                        </label>

                    </div>
                    <label ref="newAttendeeNotes" class="ibt-input-container attendee-notes-container">
                        <span class="field-label"><i>notes</i></span>
                        <InputText class="new-attendee-notes" @keyup.enter="addAttendee(group.group)" v-model="newAttendeeNotes" />
                    </label>
                </div>
            </div>
        </article>
        <article v-if="addNewGroup" @mouseenter="focusToNewGroup()" @mouseleave="hasFocus = false" class="ibt-card">
            <header ref="currentGroup" class="ibt-card-header new-group-header">
                <div class="ibt-title group-title">
                    <label class="ibt-input-container new-group">
                        <i class="ibt-icon pi pi-folder-plus" aria-hidden="true"></i>
                        <span class="field-label"><i>new group</i></span>
                        <InputText @keyup.enter="focusToNewAttendee()" ref="newGroup" v-model="newGroup" class="group-add-name" />
                    </label>
                </div>
            </header>
            <div class="ibt-card-content">
                <div v-show="newGroup" class="ibt-list">
                    <div class="ibt-list-item-container attendee-add">
                        <Button text rounded icon="pi pi-user-plus" aria-label="Add attendee"
                                @click="addAttendee(newGroup)" :class="{'ibt-primary': hasFocus}" />
                        <label class="ibt-input-container new-attendee">
                            <span class="field-label"><i>new attendee</i></span>
                            <InputText ref="newAttendeeInput" @keyup.enter="addAttendee(newGroup)" v-model="newAttendee" />
                        </label>
                    </div>
                    <label ref="newAttendeeNotes" class="ibt-input-container attendee-notes-container">
                        <span class="field-label"><i>notes</i></span>
                        <InputText class="new-attendee-notes" @keyup.enter="addAttendee(newGroup)" v-model="newAttendeeNotes" />
                    </label>
                </div>
            </div>
        </article>
        <ibt-dialog ref="dialogObj" />
        <IbtPrompt
                    v-model="groupNotes"
                    @open="dialogGroupNotesOpen"
                    @close="dialogGroupNotesClose"
                    :title="noteDialog.title"
                    :ok-text="noteDialog.ok"
                    :cancel-text="noteDialog.cancel"
                    ref="dialogGroupNotes">
        </IbtPrompt>
        <IbtPrompt
                    v-model="groupNewName"
                    @open="dialogRenameGroupOpen"
                    @close="dialogRenameGroupClose"
                    :title="renameDialog.title"
                    :ok-text="renameDialog.ok"
                    :cancel-text="renameDialog.cancel"
                    ref="dialogRenameGroup">
        </IbtPrompt>
        <IbtPrompt confirmation
                    @close="dialogDeleteGroupClose"
                    :title="deleteDialog.title"
                    :content="deleteDialog.content"
                    :ok-text="deleteDialog.ok"
                    :cancel-text="deleteDialog.cancel"
                    ref="dialogDeleteGroup">
        </IbtPrompt>
    </div>
</template>
<script>
import { resource } from './api.js';

import Attendee from './Attendee';
import IbtDialog from './IbtDialog.vue';
import IbtMenu from './IbtMenu.vue';
import VueMarkdown from './VueMarkdown.vue';

export default {
    props: {group: {}, day: {}, addNewGroup: {default: false}},
    emits: ['updated'],

    data: function () {
        return {
            newAttendee: '',
            newAttendeeNotes: '',
            newGroup: '',
            groupNotes: '',
            groupNewName: '',
            hasFocus: false,
            noteDialog: {title: 'Group notes', ok: 'ok', cancel: 'cancel'},
            renameDialog: {title: 'Rename group', ok: 'ok', cancel: 'cancel'},
            deleteDialog: {title: 'Delete group', content: 'Really delete this group?', ok: 'ok', cancel: 'cancel'},
            expandedNote: false
        }
    },

    computed: {
        menuItems() {
            return [
                { label: 'edit notes', icon: 'pi pi-pencil', visible: this.loggedInUser.isAdmin || !this.settings.protectGroupNotes, command: () => this.openNotesDialog() },
                { label: 'rename group', icon: 'pi pi-tag', visible: this.loggedInUser.isAdmin || !this.settings.protectGroupName, command: () => this.openRenameGroupDialog() },
                { label: 'delete group', icon: 'pi pi-trash', visible: !!this.loggedInUser.isAdmin, command: () => this.openDeleteGroupDialog() },
            ];
        },
        counter: function() {
            return (this.group.attendees || []).length;
        },
        loggedInUser() {
            return this.$store.state.loggedInUser;
        },
        settings() {
            return this.$store.state.settings || {};
        }
    },

    beforeCreate: function() {
        this.groupsUrl = resource('days{/day}/groups{/group}');
        this.groupsInfoUrl = resource('days{/day}/groups{/group}/info');
        this.attendeesUrl = resource('attendees{/id}');
    },

    methods: {
        reset() {
            this.newAttendee = '';
            this.newAttendeeNotes = '';
            this.newGroup = '';
        },

        reload() {
            this.$emit('updated');
            this.focusToNewAttendee();
        },

        focusToNewGroup() {
            this.$refs.newGroup.$el.focus();
            this.hasFocus = true;
        },

        focusToNewAttendee() {
            this.$refs.newAttendeeInput.$el.focus();
            this.hasFocus = true;
        },

        addAttendee(group, newAttendee) {
            newAttendee = newAttendee || this.newAttendee;
            if (!newAttendee) {
                this.focusToNewAttendee();
                return;
            }
            var attendee = {
                day: this.day,
                group: group,
                name: newAttendee,
                notes: this.newAttendeeNotes
            };
            this.attendeesUrl.save(attendee).then((response) => {
                return response.json();
            }).then((json) => {
                this.reset();
                this.$emit('updated');
            }).catch((response) => {
                var msg = (response && response.body && response.body.message) || '';
                this.$refs.dialogObj.show({text: 'unable to add the attendee: ' + msg});
            });
        },

        openNotesDialog() {
            this.$refs.dialogGroupNotes.open();
        },

        dialogGroupNotesOpen() {
            this.groupNotes = this.group.notes || '';
        },

        dialogGroupNotesClose(type) {
            if (type != 'ok' || !this.group || !this.group.group || !this.day) {
                return;
            }
            this.groupsInfoUrl.update(
                    {day: this.day, group: this.group.group},
                    {notes: this.groupNotes}).then((response) => {
                return response.json();
            }).then((json) => {
                this.group.notes = json.notes;
                this.reset();
                this.$emit('updated');
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to edit group notes'});
            });
        },

        toggleNotes() {
            var el = this.$refs.groupNotes && this.$refs.groupNotes.$el;
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
        },

        openDeleteGroupDialog() {
            this.$refs.dialogDeleteGroup.open();
        },

        dialogDeleteGroupClose(type) {
            if (type != 'ok' || !this.group || !this.group.group || !this.day || !this.loggedInUser.isAdmin) {
                return;
            }
            this.groupsUrl.delete({day: this.day, group: this.group.group}).then((response) => {
                return response.json();
            }).then((json) => {
                this.$emit('updated');
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to delete this group'});
            });
        },

        openRenameGroupDialog() {
            this.$refs.dialogRenameGroup.open();
        },

        dialogRenameGroupOpen() {
            this.groupNewName = this.group.group || '';
        },

        dialogRenameGroupClose(type) {
            if (type != 'ok' || !this.group || !this.group.group || !this.day || !this.groupNewName) {
                return;
            }
            this.groupsUrl.update(
                    {day: this.day, group: this.group.group},
                    {newName: this.groupNewName}).then((response) => {
                return response.json();
            }).then((json) => {
                this.$emit('updated');
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to rename this group'});
            });
        }
    },

    components: { IbtMenu, Attendee, IbtDialog, VueMarkdown }
};

</script>
<style scoped>

.group-layout {
    padding: 10px;
    min-width: 0;
    max-width: 100%;
    flex: 1 1 320px;
    align-self: flex-start;
}

.group-layout > .ibt-card {
    width: 100%;
    border-radius: 22px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(148, 163, 184, 0.22);
    box-shadow: 0 18px 36px rgba(15, 23, 42, 0.08);
}

.new-group-header {
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    padding-top: 0;
    padding-bottom: 0;
}

.group-title {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 700;
    color: #1f2937;
}

.new-group-header .group-title {
    margin-top: 0 !important;
}

.group-header {
    background: linear-gradient(135deg, #e0f2fe 0%, #ddd6fe 100%);
    padding: 16px 18px 12px;
}

.group-icon {
    margin: 0;
    vertical-align: text-top;
}

.new-group {
    min-width: 0;
}

.new-group-header i:after {
    background-color: initial !important;
}

.counter {
    margin-left: 8px;
    background: rgba(255, 255, 255, 0.8);
    color: #334155;
    padding: 4px 8px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    line-height: 1;
}

.new-attendee {
    flex: 1;
    min-width: 0;
    margin-bottom: 0;
}

.attendee-notes-container {
    width: calc(100% - 40px);
    margin-left: 40px;
}

.group-card {
    padding: 10px 14px 14px;
}

</style>
<style>

.group-notes > p, .attendee-notes > p {
    font-style: italic;
    padding-left: 30px;
    margin: 0;
    padding: 0 4px 0 0;
    text-overflow: ellipsis;
    max-width: 400px;
    overflow: hidden;
    white-space: nowrap;
    color: rgba(15, 23, 42, 0.7);
}

.ibt-list-item-container {
    padding: 0 !important;
    margin-left: 0;
    width: 100%;
    border-radius: 12px;
}

.ibt-list-item-container {
    border-radius: 12px;
}

</style>
