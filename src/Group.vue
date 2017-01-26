<template>
    <!-- XXX: too much duplication in this template -->
    <md-layout class="group-layout" md-col gutter="120" md-align="start">
        <md-card v-if="!addNewGroup" md-with-hover @mouseenter.native="focusToNewAttendee()">
            <md-card-header class="group-header">
                <md-layout md-row>
                    <div class="md-title group-title">
                        <md-icon class="group-icon">folder_open</md-icon>&nbsp;{{ group.group }}&nbsp;<span class="counter">{{ counter }}</span>
                    </div>
                    <md-menu md-align-trigger>
                        <md-button class="md-icon-button" md-menu-trigger>
                            <md-icon>more_vert</md-icon>
                        </md-button>
                        <md-menu-content>
                            <md-menu-item @click="openNotesDialog()">
                                <span>edit notes</span>
                                <md-icon>edit</md-icon>
                            </md-menu-item>
                        </md-menu-content>
                    </md-menu>
                </md-layout>
                <md-layout v-if="group.notes" md-row>
                    <div ref="groupNotes" class="group-notes" @click="toggleNotes()">{{ group.notes }}</div>
                </md-layout>
            </md-card-header>
            <md-card-content>
                <md-list md-dense>
                    <attendee v-for="attendee in group.attendees || []" :attendee="attendee" @updated="reload" />
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
    </md-layout>
</template>
<script>

import Attendee from './Attendee';
import IbtDialog from './IbtDialog.vue';

export default {
    props: {group: {}, day: {}, addNewGroup: {default: false}},

    data: function () {
        return {
            newAttendee: '',
            newAttendeeNotes: '',
            newGroup: '',
            groupNotes: '',
            noteDialog: {title: 'Group notes', ok: 'ok', cancel: 'cancel'},
            expandedNote: false
        }
    },

    computed: {
        counter: function() {
            return (this.group.attendees || []).length;
        }
    },

    beforeCreate: function() {
        this.groupsUrl = this.$resource('groups');
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
                this.$refs.dialogObj.show({text: 'unable to add the attendee'});
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
            var data = {day: this.day, group: this.group.group, notes: this.groupNotes};
            this.groupsUrl.update(data).then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to edit group notes'});
            }).then((json) => {
                this.reset();
                this.$emit('updated');
            });
        },

        toggleNotes() {
            if (!this.expandedNote) {
                $(this.$refs.groupNotes).css('text-overflow', 'initial');
                $(this.$refs.groupNotes).css('white-space', 'initial');
                this.expandedNote = true;
            } else {
                $(this.$refs.groupNotes).css('text-overflow', 'ellipsis');
                $(this.$refs.groupNotes).css('white-space', 'nowrap');
                this.expandedNote = false;
            }
        }
    },

    components: { Attendee, IbtDialog }
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

.group-notes {
    font-style: italic;
    padding-left: 15px;
    text-overflow: ellipsis;
    max-width: 400px;
    overflow: hidden;
    white-space: nowrap;
    color: rgba(0, 0, 0, 0.54);
}

.new-group-label {
    left: 30px !important;
}

.group-add-name {
    margin-left: 0px !important;
}

</style>
