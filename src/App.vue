<template>
    <div id="main-attendees">
        <md-layout md-gutter md-row>
            <md-layout md-column md-flex="20" md-gutter>
                <datepicker id="datepicker" :value="date" :inline="true" :highlighted="highlightedDates" @selected="getDay"></datepicker>
            </md-layout>
            <md-layout id="panel" md-column>
                <md-layout md-row>
                    <group v-for="group in day.groups || []" :group="group" :day="day.day" new-attendee="" @updated="reload" />
                    <group :add-new-group="true" :day="day.day" new-attendee="" new-group="" @updated="reload" />
                </md-layout>
            </md-layout>
        </md-layout>
        <ibt-dialog ref="dialogObj" />
    </div>
</template>
<script>

import Datepicker from 'vuejs-datepicker';
import Group from './Group';
import IbtDialog from './IbtDialog.vue';

export default {
    data() {
        return {
            date: null, // a Date object representing the selected date
            day: {},
            daysSummary: {}
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
        this.attendeesUrl = this.$resource('attendees{/id}');
        this.currentUserUrl = this.$resource('users/current');
        this.loginUrl = this.$resource('login');
        this.logoutUrl = this.$resource('logout');
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
        }
    },

    components: {
        Datepicker, Group, IbtDialog
    }
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

#datepicker {
    padding: 10px;
}

#panel .md-layout {
    flex: initial;
}

#toolbar-title {
    flex: 1;
}

.login-input {
    width: 200px;
    margin: 0px 0px 0px;
    padding-top: 0px;
    padding-left: 4px;
    min-height: 24px;
    line-height: 0px;
    margin-right: 20px;
    background-color: white;
}
</style>
