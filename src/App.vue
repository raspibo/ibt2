<template>
    <div id="main-attendees">
        <md-layout md-gutter md-row>
            <md-layout id="datepicker-column" md-flex="20" md-flex-small="100" md-gutter>
                <datepicker id="datepicker" ref="datepicker" :value="date" :inline="true" :highlighted="highlightedDates" :monday-first="true" @selected="getDay" @changedMonth="changeMonth"></datepicker>
                <md-card id="day-info">
                    <md-card-header class="day-info-header">
                        <md-layout md-row>
                            <div class="md-title day-info-title">
                                <md-icon class="day-icon">today</md-icon>&nbsp;{{ day.day }}
                            </div>
                            <md-menu v-if="loggedInUser.isAdmin || !settings.protectDayNotes" md-align-trigger>
                                <md-button class="md-icon-button" md-menu-trigger>
                                    <md-icon>more_vert</md-icon>
                                </md-button>
                                <md-menu-content>
                                    <md-menu-item v-if="loggedInUser.isAdmin || !settings.protectDayNotes" @click="openNotesDialog()">
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
                    <group v-for="group in day.groups || []" :group="group" :day="day.day" :key="group.group" new-attendee="" @updated="reload" />
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
import VueMarkdown from './VueMarkdown.vue';

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
        },

        loggedInUser() {
            return this.$store.state.loggedInUser;
        },

        settings() {
            return this.$store.state.settings || {};
        }
    },

    beforeCreate: function() {
        this.daysUrl = this.$resource('days{/day}');
        this.daysInfoUrl = this.$resource('days{/day}/info');
        this.settingsUrl = this.$resource('settings');
    },

    mounted: function() {
        this.fetchSettings(this.initialize);
    },

    methods: {
        initialize() {
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

        reload() {
            var ym = this.dateToString(this.date, true);
            this.getSummary({start: ym, end: ym});
            this.getDay();
        },

        changeMonth(newDate) {
            if (newDate.timestamp) {
                newDate = new Date(newDate.timestamp);
            }
            var day = new Date();
            day.setTime(newDate instanceof Date ? newDate.getTime() : newDate);
            var ym = this.dateToString(day, true);
            this.getSummary({start: ym, end: ym});
            this.getDay(day);
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
            this.daysInfoUrl.update({day: this.day.day}, data).then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to edit day notes'});
            }).then((json) => {
                this.day.notes = json.notes;
                this.reload();
            });
        },

        fetchSettings(cb) {
            this.settingsUrl.get().then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to fetch settings'});
            }).then((json) => {
                if (!json || json.error) {
                    this.$refs.dialogObj.show({text: 'unable to fetch settings: ' + ((json && json.message) || '')});
                } else {
                    this.$store.commit('updateSettings', json);
                }
                cb();
            });
        }
    },

    components: { Datepicker, Group, IbtDialog, VueMarkdown }
}

</script>
<style scoped>

#main-attendees {
    font-family: 'Avenir', 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #1f2937;
    margin-top: 0;
    padding: 24px 20px 36px;
}

#datepicker-column {
    min-width: 320px;
    max-width: 360px;
    gap: 18px;
}

@media screen and (min-width: 945px) {
    #datepicker-column {
        flex-direction: column;
    }
}

.vdp-datepicker {
    padding: 10px;
    background: rgba(255, 255, 255, 0.88);
    border-radius: 22px;
    box-shadow: 0 18px 44px rgba(15, 23, 42, 0.12);
    border: 1px solid rgba(148, 163, 184, 0.25);
}

#panel {
    gap: 12px;
}

#panel .md-layout {
    flex: initial;
    gap: 16px;
}

#day-info {
    margin: 0;
    width: 100%;
    min-height: 200px;
    border-radius: 22px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid rgba(148, 163, 184, 0.25);
    box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
}

.day-info-title {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.1rem;
    font-weight: 700;
}

.day-info-header {
    background: linear-gradient(135deg, #fbcfe8 0%, #ddd6fe 100%);
    padding: 16px 20px;
}

#day-notes {
    color: #475569;
    line-height: 1.6;
    padding: 12px 18px 18px;
}

#day-notes p {
    margin: 0;
}

.day-icon {
    vertical-align: text-top;
}

</style>
<style>

body {
    margin: 0;
    background:
        radial-gradient(circle at top left, rgba(191, 219, 254, 0.8), transparent 25%),
        linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
    color: #1f2937;
}

#app {
    min-height: 100vh;
}

.md-card,
.md-toolbar,
.md-list,
.md-input-container,
.md-btn,
.md-button {
    border-radius: 18px !important;
}

.vdp-datepicker__calendar > header > span {
    background: linear-gradient(135deg, #f9a8d4 0%, #c4b5fd 100%);
    color: #111827;
}

.vdp-datepicker__calendar > header > span:hover {
    background: linear-gradient(135deg, #f472b6 0%, #8b5cf6 100%) !important;
    color: white !important;
}

.vdp-datepicker__calendar {
    border: none !important;
    box-shadow: none !important;
    border-radius: 18px !important;
    overflow: hidden;
}

.vdp-datepicker__calendar .cell {
    border-radius: 10px;
}

.vdp-datepicker__calendar .cell.selected {
    background: linear-gradient(135deg, #f472b6 0%, #8b5cf6 100%);
    color: white;
}

</style>
