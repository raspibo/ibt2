<template>
    <div id="main-attendees">
        <div class="ibt-layout layout-row">
            <div id="datepicker-column" class="ibt-layout layout-row">
                <DatePicker id="datepicker" :model-value="date" inline @date-select="getDay"
                            @month-change="changeMonth" @year-change="changeMonth">
                    <template #date="slotProps">
                        <span :class="{'event-date': isEventDate(slotProps.date)}">{{ slotProps.date.day }}</span>
                    </template>
                </DatePicker>
                <article id="day-info" class="ibt-card">
                    <header class="ibt-card-header day-info-header">
                        <div class="ibt-layout layout-row">
                            <div class="ibt-title day-info-title">
                                <i class="ibt-icon pi pi-calendar day-icon" aria-hidden="true"></i>&nbsp;{{ day.day }}
                            </div>
                            <ibt-menu v-if="loggedInUser.isAdmin || !settings.protectDayNotes" :items="menuItems" />
                        </div>
                    </header>
                    <div class="ibt-card-content">
                        <div id="day-notes"><vue-markdown :source="day.notes"></vue-markdown></div>
                    </div>
                </article>
            </div>
            <div id="panel" class="ibt-layout layout-column">
                <div class="ibt-layout layout-row">
                    <group v-for="group in day.groups || []" :group="group" :day="day.day" :key="group.group" new-attendee="" @updated="reload" />
                    <group key="__new_group__" :add-new-group="true" :day="day.day" new-attendee="" new-group="" @updated="reload" />
                </div>
            </div>
        </div>
        <ibt-dialog ref="dialogObj" />
        <IbtPrompt
                    v-model="dayNotes"
                    @open="dialogDayNotesOpen"
                    @close="dialogDayNotesClose"
                    :title="noteDialog.title"
                    :ok-text="noteDialog.ok"
                    :cancel-text="noteDialog.cancel"
                    ref="dialogDayNotes">
        </IbtPrompt>
    </div>
</template>
<script>
import { resource } from './api.js';

import DatePicker from 'primevue/datepicker';
import Group from './Group';
import IbtDialog from './IbtDialog.vue';
import IbtMenu from './IbtMenu.vue';
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
        menuItems() {
            return [{ label: 'edit notes', icon: 'pi pi-pencil', command: () => this.openNotesDialog() }];
        },
        loggedInUser() {
            return this.$store.state.loggedInUser;
        },

        settings() {
            return this.$store.state.settings || {};
        }
    },

    beforeCreate: function() {
        this.daysUrl = resource('days{/day}');
        this.daysInfoUrl = resource('days{/day}/info');
        this.settingsUrl = resource('settings');
    },

    mounted: function() {
        this.fetchSettings(this.initialize);
    },

    watch: {
        '$route.params.day'(day) {
            if (!this.date || day !== this.dateToString(this.date)) this.initialize();
        },
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
            if (!this.$route.params.day || !(this.date && !isNaN(this.date.getTime()))) {
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
            const day = new Date(newDate.year, newDate.month - 1, 1);
            var ym = this.dateToString(day, true);
            this.getSummary({start: ym, end: ym});
        },

        isEventDate(date) {
            const value = this.dateToString(new Date(date.year, date.month, date.day));
            return (this.daysSummary.days || []).some(day => day.day === value);
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
            }).then((json) => {
                this.daysSummary = json;
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to get the monthly summary'});
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
            if (this.$route.params.day !== day) this.$router.push('/day/' + day);
            this.daysUrl.get({day: day}).then((response) => {
                return response.json();
            }).then((dayData) => {
                if (!(dayData && dayData.day)) {
                    dayData.day = day;
                }
                this.day = dayData;
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to get information about this day'});
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
            }).then((json) => {
                this.day.notes = json.notes;
                this.reload();
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to edit day notes'});
            });
        },

        fetchSettings(cb) {
            this.settingsUrl.get().then((response) => {
                return response.json();
            }).then((json) => {
                if (!json || json.error) {
                    this.$refs.dialogObj.show({text: 'unable to fetch settings: ' + ((json && json.message) || '')});
                } else {
                    this.$store.commit('updateSettings', json);
                }
                cb();
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to fetch settings'});
            });
        }
    },

    components: { IbtMenu, DatePicker, Group, IbtDialog, VueMarkdown }
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
    min-width: 0;
    flex: 0 0 320px;
    max-width: 360px;
    gap: 18px;
}

@media screen and (min-width: 945px) {
    #datepicker-column {
        flex-direction: column;
    }
}

#panel {
    min-width: 0;
    gap: 12px;
}

#panel > .ibt-layout {
    flex: initial;
    align-items: flex-start;
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
    margin: 0;
    vertical-align: text-top;
}

@media screen and (max-width: 944px) {
    #datepicker-column {
        flex: 1 1 100%;
        max-width: none;
        margin-bottom: 18px;
        justify-content: center;
    }

    #panel {
        flex: 1 1 100%;
    }
}

@media screen and (max-width: 400px) {
    #main-attendees {
        padding: 18px 10px 24px;
    }

}

</style>
