<template>
    <div id="main-attendees">
        <md-layout md-gutter md-row>
            <md-layout id="datepicker-column" md-flex="20" md-flex-small="100" md-gutter>
                <datepicker id="datepicker" :value="date" :inline="true" :highlighted="highlightedDates" :monday-first="true" @selected="getDay"></datepicker>
                <md-card id="day-info">
                    <md-card-header class="group-header">
                        <md-layout md-row>
                            <div class="md-title day-info-title">
                                <md-icon class="day-icon">today</md-icon>&nbsp;{{ day.day }}
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
                    </md-card-header>
                    <md-card-content>
                        <div id="day-notes"><vue-markdown :source="day.notes"></vue-markdown></div>
                    </md-card-content>
                </md-card>
            </md-layout>
            <md-layout id="panel" md-column>
                <md-layout md-row>
                    <group v-for="group in day.groups || []" :group="group" :day="day.day" new-attendee="" @updated="reload" />
                    <group :add-new-group="true" :day="day.day" new-attendee="" new-group="" @updated="reload" />
                </md-layout>
            </md-layout>
        </md-layout>
        <ibt-dialog ref="dialogObj" />
        <md-dialog-prompt
                    v-model="dayNotes"
                    @open="dialogDayNotesOpen"
                    @close="dialogDayNotesClose"
                    :md-title="noteDialog.title"
                    :md-ok-text="noteDialog.ok"
                    :md-cancel-text="noteDialog.cancel"
                    ref="dialogDayNotes">
        </md-dialog-prompt>
    </div>
</template>
<script>

import Datepicker from 'vuejs-datepicker';
import Group from './Group';
import IbtDialog from './IbtDialog.vue';
import VueMarkdown from 'vue-markdown';

export default {
    data() {
        return {
            date: null, // a Date object representing the selected date
            day: {},
            daysSummary: {},
            dayNotes: '',
            noteDialog: {title: 'Day notes', ok: 'ok', cancel: 'cancel'}
        }
    },

    computed: {
        highlightedDates() {
            var ds = this.daysSummary.days || [];
            var datesWithGroups = [];
            for (var i=0; i < ds.length; i++) {
                var [year, month, day] = ds[i].day.split('-');
                year = parseInt(year);
                month = parseInt(month) - 1;
                day = parseInt(day);
                if (isNaN(year) || isNaN(month) || isNaN(day)) {
                    continue;
                }
                datesWithGroups.push(new Date(year, month, day));
            }
            return {
                dates: datesWithGroups
            };
        }
    },

    beforeCreate: function() {
        this.daysUrl = this.$resource('days{/day}');
    },

    mounted: function() {
        var [year, month, day] = (this.$route.params.day || '').split('-');
        year = parseInt(year);
        month = parseInt(month) - 1;
        day = parseInt(day);
        if (!isNaN(year) && !isNaN(month) && !isNaN(day)) {
            this.date = new Date(year, month, day);
        }
        if (!(this.date && !isNaN(this.date.getTime()))) {
            this.date = new Date();
        }
        this.reload();
    },

    methods: {
        reload() {
            var ym = this.dateToString(this.date, true);
            this.getSummary({start: ym, end: ym});
            this.getDay();
        },

        dateToString(date, excludeDay) {
            var year = '' + date.getFullYear();
            var month = '' + (date.getMonth() + 1);
            month = '00'.substring(0, 2 - month.length) + month;
            var ym = year + '-' + month;
            if (excludeDay) {
                return ym;
            }
            var day = '' + (date.getDate());
            day = '00'.substring(0, 2 - day.length) + day;
            return ym + '-' + day;
        },

        getSummary(params) {
            if (!params) {
                params = {};
            }
            params['summary'] = true;
            this.daysUrl.query(params).then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to get the monthly summary'});
            }).then((json) => {
                this.daysSummary = json;
            });
        },

        getDay(day) {
            if (day instanceof Date) {
                this.date = day;
                day = this.dateToString(day);
            } else if (this.date && this.date instanceof Date) {
                day = this.dateToString(this.date);
            } else {
                var today = new Date();
                day = this.dateToString(today);
                this.date = today;
            }
            this.$router.push('/day/' + day);
            this.daysUrl.get({day: day}).then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to get information about this day'});
            }).then((dayData) => {
                if (!(dayData && dayData.day)) {
                    dayData.day = day;
                }
                this.day = dayData;
            });
        },

        openNotesDialog() {
            this.$refs.dialogDayNotes.open();
        },

        dialogDayNotesOpen() {
            this.dayNotes = this.day.notes || '';
        },

        dialogDayNotesClose(type) {
            if (type != 'ok' || !this.day) {
                return;
            }
            var data = {day: this.day.day, notes: this.dayNotes};
            this.daysUrl.update(data).then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to edit day notes'});
            }).then((json) => {
                this.day.notes = json.notes;
                this.reload();
            });
        }
    },

    components: { Datepicker, Group, IbtDialog, VueMarkdown }
}

</script>
<style>

#main-attendees {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;
    margin-top: 0px;
}

#datepicker-column {
    min-width: 320px;
}

#datepicker {
    padding: 10px;
}

#panel .md-layout {
    flex: initial;
}

#day-info {
    margin: 10px;
    width: 300px;
    min-height: 200px;
}

.day-info-title {
    flex: 1;
}

#day-notes {
    color: rgba(0, 0, 0, 0.54);
}

.day-icon {
    vertical-align: text-top;
}


</style>
