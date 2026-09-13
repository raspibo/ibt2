<template>
    <!-- XXX: too much duplication in this template -->
    <md-layout class="group-layout" md-col gutter="120" md-align="start">
        <md-card v-if="!addNewGroup" md-with-hover @mouseenter.native="focusToNewAttendee()" @mouseleave.native="hasFocus = false">
            <md-card-header ref="currentGroup" class="group-header">
                <md-layout md-row>
                    <div class="md-title group-title">
                        <md-icon class="group-icon">folder_open</md-icon>&nbsp;{{ group.group }}&nbsp;<span class="counter">{{ counter }}</span>
                    </div>
                    <md-menu v-if="loggedInUser.isAdmin || !settings.protectGroupNotes || !settings.protectGroupName" md-align-trigger>
                        <md-button class="md-icon-button" md-menu-trigger>
                            <md-icon>more_vert</md-icon>
                        </md-button>
                        <ibt-menu-content>
                            <ibt-menu-item v-if="loggedInUser.isAdmin || !settings.protectGroupNotes" @click="openNotesDialog()">
                                <span>edit notes</span>
                                <md-icon>edit</md-icon>
                            </ibt-menu-item>
                            <ibt-menu-item v-if="loggedInUser.isAdmin || !settings.protectGroupName" @click="openRenameGroupDialog()">
                                <span>rename group</span>
                                <md-icon>label</md-icon>
                            </ibt-menu-item>
                            <ibt-menu-item v-if="loggedInUser.isAdmin" @click="openDeleteGroupDialog()">
                                <span>delete group</span>
                                <md-icon>delete</md-icon>
                            </ibt-menu-item>
                        </ibt-menu-content>
                    </md-menu>
                </md-layout>
                <md-layout v-if="group.notes" md-row>
                    <md-tooltip md-direction="top">click to expande/collapse notes</md-tooltip>
                    <vue-markdown ref="groupNotes" @click="toggleNotes()" class="group-notes" :source="group.notes" :break="false"></vue-markdown>
                </md-layout>
            </md-card-header>
            <md-card-content class="group-card">
                <md-list md-dense>
                    <attendee v-for="attendee in group.attendees || []" :attendee="attendee" :key="attendee._id" @updated="reload" />
                    <md-list-item class="attendee-add">
                        <md-icon @click.native="addAttendee(group.group)" :class="{'md-primary': hasFocus}">person_add</md-icon>
                        <md-input-container class="new-attendee">
                            <label><i>new attendee</i></label>
                            <md-input ref="newAttendeeInput" @keyup.enter.native="addAttendee(group.group)" v-model="newAttendee" />
                        </md-input-container>

                    </md-list-item>
                    <md-input-container ref="newAttendeeNotes" class="attendee-notes-container">
                        <label><i>notes</i></label>
                        <md-input class="new-attendee-notes" @keyup.enter.native="addAttendee(group.group)" v-model="newAttendeeNotes" />
                    </md-input-container>
                </md-list>
            </md-card-content>
        </md-card>
        <md-card v-if="addNewGroup" md-with-hover @mouseenter.native="focusToNewGroup()" @mouseleave.native="hasFocus = false" md-align="start">
            <md-card-header ref="currentGroup" class="new-group-header">
                <div class="md-title group-title">
                    <md-input-container class="new-group">
                        <md-icon>create_new_folder</md-icon>
                        <label><i>new group</i></label>
                        <md-input @keyup.enter.native="focusToNewAttendee()" ref="newGroup" v-model="newGroup" class="group-add-name" />
                    </md-input-container>
                </div>
            </md-card-header>
            <md-card-content>
                <md-list v-show="newGroup" md-dense>
                    <md-list-item class="attendee-add">
                        <md-icon @click.native="addAttendee(newGroup)" :class="{'md-primary': hasFocus}">person_add</md-icon>
                        <md-input-container class="new-attendee">
                            <label><i>new attendee</i></label>
                            <md-input ref="newAttendeeInput" @keyup.enter.native="addAttendee(newGroup)" v-model="newAttendee" />
                        </md-input-container>
                    </md-list-item>
                    <md-input-container ref="newAttendeeNotes" class="attendee-notes-container">
                        <label><i>notes</i></label>
                        <md-input class="new-attendee-notes" @keyup.enter.native="addAttendee(newGroup)" v-model="newAttendeeNotes" />
                    </md-input-container>
                </md-list>
            </md-card-content>
        </md-card>
        <ibt-dialog ref="dialogObj" />
        <md-dialog-prompt
                    v-model="groupNotes"
                    @open="dialogGroupNotesOpen"
                    @close="dialogGroupNotesClose"
                    :md-title="noteDialog.title"
                    :md-ok-text="noteDialog.ok"
                    :md-cancel-text="noteDialog.cancel"
                    ref="dialogGroupNotes">
        </md-dialog-prompt>
        <md-dialog-prompt
                    v-model="groupNewName"
                    @open="dialogRenameGroupOpen"
                    @close="dialogRenameGroupClose"
                    :md-title="renameDialog.title"
                    :md-ok-text="renameDialog.ok"
                    :md-cancel-text="renameDialog.cancel"
                    ref="dialogRenameGroup">
        </md-dialog-prompt>
        <md-dialog-confirm
                    @close="dialogDeleteGroupClose"
                    :md-title="deleteDialog.title"
                    :md-content="deleteDialog.content"
                    :md-ok-text="deleteDialog.ok"
                    :md-cancel-text="deleteDialog.cancel"
                    ref="dialogDeleteGroup">
        </md-dialog-confirm>
    </md-layout>
</template>
<script>

import Attendee from './Attendee';
import IbtDialog from './IbtDialog.vue';
import IbtMenuItem from './IbtMenuItem.vue';
import IbtMenuContent from './IbtMenuContent.vue';
import VueMarkdown from './VueMarkdown.vue';

export default {
    props: {group: {}, day: {}, addNewGroup: {default: false}},

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
        this.groupsUrl = this.$resource('days{/day}/groups{/group}');
        this.groupsInfoUrl = this.$resource('days{/day}/groups{/group}/info');
        this.attendeesUrl = this.$resource('attendees{/id}');
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
            }, (response) => {
                var msg = (response && response.body && response.body.message) || '';
                this.$refs.dialogObj.show({text: 'unable to add the attendee: ' + msg});
            }).then((json) => {
                this.reset();
                this.$emit('updated');
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
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to edit group notes'});
            }).then((json) => {
                this.group.notes = json.notes;
                this.reset();
                this.$emit('updated');
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
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to delete this group'});
            }).then((json) => {
                this.$emit('updated');
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
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to rename this group'});
            }).then((json) => {
                this.$emit('updated');
            });
        }
    },

    components: { IbtMenuContent, IbtMenuItem, Attendee, IbtDialog, VueMarkdown }
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

.group-layout > .md-card {
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

.attendee-add .md-list-item-container > .md-icon:first-child {
    margin-right: 16px;
    cursor: pointer;
}

.attendee-add .md-icon {
    transition: color 0.2s ease;
    color: #4338ca;
}

.attendee-add .md-list-item-container {
    padding: 0 !important;
    margin-left: 0;
    width: 100%;
    border-radius: 12px;
}

.md-list-item-container {
    border-radius: 12px;
}

</style>
