<template>
    <!-- XXX: too much duplication in this template -->
    <md-layout class="group-layout" md-col gutter="120" md-align="start">
        <md-card v-if="!addNewGroup" md-with-hover @mouseenter.native="focusToNewAttendee()">
            <md-card-header class="group-header">
                <md-layout md-row>
                    <div class="md-title group-title">
                        <md-icon class="group-icon">folder_open</md-icon>&nbsp;{{ group.group }}&nbsp;<span class="counter">{{ counter }}</span>
                    </div>
                    <md-menu v-if="loggedInUser.isAdmin || !settings.protectGroupNotes || !settings.protectGroupName" md-align-trigger>
                        <md-button class="md-icon-button" md-menu-trigger>
                            <md-icon>more_vert</md-icon>
                        </md-button>
                        <md-menu-content>
                            <md-menu-item v-if="loggedInUser.isAdmin || !settings.protectGroupNotes" @click="openNotesDialog()">
                                <span>edit notes</span>
                                <md-icon>edit</md-icon>
                            </md-menu-item>
                            <md-menu-item v-if="loggedInUser.isAdmin || !settings.protectGroupName" @click="openRenameGroupDialog()">
                                <span>rename group</span>
                                <md-icon>label</md-icon>
                            </md-menu-item>
                            <md-menu-item v-if="loggedInUser.isAdmin" @click="openDeleteGroupDialog()">
                                <span>delete group</span>
                                <md-icon>delete</md-icon>
                            </md-menu-item>
                        </md-menu-content>
                    </md-menu>
                </md-layout>
                <md-layout v-if="group.notes" md-row>
                    <md-tooltip md-direction="top">click to expande/collapse notes</md-tooltip>
                    <vue-markdown ref="groupNotes" @click.native="toggleNotes()" class="group-notes" :source="group.notes" :break="false"></vue-markdown>
                </md-layout>
            </md-card-header>
            <md-card-content class="group-card">
                <md-list md-dense>
                    <attendee v-for="attendee in group.attendees || []" :attendee="attendee" :key="attendee.name" @updated="reload" />
                    <md-list-item class="attendee-add">
                        <md-icon @click.native="addAttendee(group.group)">person_add</md-icon>
                        <md-input-container class="new-attendee">
                            <label>new attendee</label>
                            <md-input ref="newAttendeeInput" @keyup.enter.native="addAttendee(group.group)" v-model="newAttendee" />
                        </md-input-container>

                        <md-list-expand>
                            <md-list>
                                <md-list-item class="md-inset">
                                    <md-input-container>
                                        <label>notes</label>
                                        <md-input class="new-attendee-notes" @keyup.enter.native="addAttendee(group.group)" v-model="newAttendeeNotes" />
                                    </md-input-container>
                                </md-list-item>
                            </md-list>
                        </md-list-expand>
                    </md-list-item>
                </md-list>
            </md-card-content>
        </md-card>
        <md-card v-if="addNewGroup" md-with-hover @mouseenter.native="focusToNewGroup()" md-align="start">
            <md-card-header class="new-group-header">
                <div class="md-title group-title">
                    <md-input-container class="new-group">
                        <label class="new-group-label">new group</label>
                        <md-icon>create_new_folder</md-icon>&nbsp;&nbsp;<md-input ref="newGroup" v-model="newGroup" @keyup.enter.native="focusToNewAttendee()" class="group-add-name" />
                    </md-input-container>
                </div>
            </md-card-header>
            <md-card-content>
                <md-list v-show="newGroup">
                    <md-list-item class="attendee-add">
                        <md-icon @click.native="addAttendee(newGroup)">person_add</md-icon>
                        <md-input-container>
                            <label>new attendee</label>
                            <md-input ref="newAttendeeInput" @keyup.enter.native="addAttendee(newGroup)" v-model="newAttendee" />
                        </md-input-container>

                        <md-list-expand>
                            <md-list>
                                <md-list-item class="md-inset">
                                    <md-input-container>
                                        <label>notes</label>
                                        <md-input class="new-attendee-notes" @keyup.enter.native="addAttendee(newGroup)" v-model="newAttendeeNotes" />
                                    </md-input-container>
                                </md-list-item>
                            </md-list>
                        </md-list-expand>
                    </md-list-item>
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
import VueMarkdown from 'vue-markdown';

export default {
    props: {group: {}, day: {}, addNewGroup: {default: false}},

    data: function () {
        return {
            newAttendee: '',
            newAttendeeNotes: '',
            newGroup: '',
            groupNotes: '',
            groupNewName: '',
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
        },

        focusToNewAttendee() {
            this.$refs.newAttendeeInput.$el.focus();
        },

        addAttendee(group, newAttendee) {
            newAttendee = newAttendee || this.newAttendee;
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
            if (!this.expandedNote) {
                $(this.$refs.groupNotes.$el).find('p').css('text-overflow', 'initial');
                $(this.$refs.groupNotes.$el).find('p').css('white-space', 'initial');
                this.expandedNote = true;
            } else {
                $(this.$refs.groupNotes.$el).find('p').css('text-overflow', 'ellipsis');
                $(this.$refs.groupNotes.$el).find('p').css('white-space', 'nowrap');
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

    components: { Attendee, IbtDialog, VueMarkdown }
};

</script>
<style>

.group-layout {
    padding: 10px;
}

.new-group-header {
    background-color: lightsteelblue;
    padding-top: 0px !important;
    padding-bottom: 0px !important;
}

.group-title {
    flex: 1;
}

.new-group-header .group-title {
    margin-top: 0px !important;
}

.group-header {
    background-color: lightblue;
}

.group-icon {
    vertical-align: text-top;
}

.new-attendee {
    width: 50px;
}

.new-group {
    min-width: 250px;
}

.new-group-header i:after {
    background-color: initial !important;
}

.counter {
    margin-left: 4px;
    position: relative;
    bottom: 12px;
    background-color: #eee;
    color: #666;
    padding: 2px 5px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 200;
    line-height: 1;
}

.new-attendee-notes {
    max-width: 120px;
}

.group-notes > p {
    font-style: italic;
    padding-left: 30px;
    margin: 0px;
    text-overflow: ellipsis;
    max-width: 400px;
    overflow: hidden;
    white-space: nowrap;
    color: rgba(0, 0, 0, 0.54);
}

.group-card {
    padding-right: 8px !important;
}

.new-group-label {
    left: 30px !important;
}

.group-add-name {
    margin-left: 0px !important;
}

.attendee-add > button {
    padding-left: 0px !important;
}

</style>
