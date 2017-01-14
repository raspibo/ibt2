<template>
    <md-layout class="group-layout" md-col gutter="120" md-align="start">
        <md-card v-if="!addNewGroup" md-with-hover @mouseenter.native="focusToNewAttendee()">
            <md-card-header class="group-header">
                <md-layout md-row>
                    <div class="md-title">
                        <md-icon class="group-icon">folder_open</md-icon>&nbsp;Group: {{ group.group }}
                    </div>
                </md-layout>
            </md-card-header>
            <md-card-content>
                <md-list md-dense>
                    <attendee v-for="attendee in group.attendees || []" :attendee="attendee" @updated="reload" />
                    <md-list-item class="attendee-add">
                        <md-icon>person_add</md-icon>
                        <md-input-container class="new-attendee">
                            <md-input ref="newAttendeeInput" @keyup.enter.native="addAttendee(group.group, newAttendee)" v-model="newAttendee" class="attendee-add-name" />
                        </md-input-container>
                    </md-list-item>
                </md-list>
            </md-card-content>
        </md-card>
        <md-card v-if="addNewGroup" md-with-hover @mouseenter.native="focusToNewGroup()" md-align="start">
            <md-card-header class="new-group-header">
                <div class="md-title">
                    <md-input-container class="new-group">
                        <md-icon>create_new_folder</md-icon>&nbsp;&nbsp;<md-input ref="newGroup" v-model="newGroup" @keyup.enter.native="focusToNewAttendee()" class="group-add-name" placeholder="new group" />
                    </md-input-container>
                </div>
            </md-card-header>
            <md-card-content>
                <md-list v-show="newGroup">
                    <md-list-item class="attendee-add">
                        <md-icon>person_add</md-icon>
                        <md-input-container md-inline>
                            <md-input ref="newAttendeeInput" @keyup.enter.native="addAttendee(newGroup, newAttendee)" v-model="newAttendee" class="attendee-add-name" />
                        </md-input-container>
                    </md-list-item>
                </md-list>
            </md-card-content>
        </md-card>
    </md-layout>
</template>
<script>

import Attendee from './Attendee';

export default {
    props: {group: {}, day: {}, addNewGroup: {default: false}},

    data: function () {
        return { newAttendee: '', newGroup: '' }
    },

    beforeCreate: function() {
        this.attendeesUrl = this.$resource('attendees{/id}');
    },

    methods: {
        reset() {
            this.newAttendee = '';
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
            this.attendeesUrl.save({day: this.day, group: group, name: newAttendee}).then((response) => {
                return response.json();
            }, (response) => {
                alert('addAttendee: failed to get resource');
            }).then((json) => {
                this.reset();
                this.$emit('updated');
            });
        }
    },

    components: { Attendee }
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

.new-group-header .md-title {
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
    width: 260px;
}
</style>
