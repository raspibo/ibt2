<template>
    <div id="app">
        <div id="datepicker">
            <datepicker :value="state.date" :inline="true" v-on:selected="getDay"></datepicker>
        </div>
        <div id="panel">
            <ul class="groups">
                <li v-for="group in state.day.groups || []">
                    <div>{{ group.group }}</div>
                    <ul class="attendees">
                        <li v-for="attendee in group.attendees || []">
                            {{attendee.name}}
                        </li>
                        <li class="add-attendee">add: <input v-on:keyup.enter="addAttendee(group.group, newAttendee)" v-model="newAttendee" /></li>
                    </ul>
                </li>
                <li class="add-group"><input v-model="newGroup" /></a>
                <ul v-if="newGroup">
                    <li class="add-attendee">add: <input v-on:keyup.enter="addAttendee(newGroup, newAttendee)" v-model="newAttendee" /></li>
                </ul>
            </ul>
        </div>
    <div>
</template>

<script>

import Datepicker from 'vuejs-datepicker';

export default {
    data () {
        return {
            state: {
                date: new Date(),
                day: {},
            },
            newAttendee: null,
            newGroup: null
        }
    },

    beforeCreate: function() {
        this.daysUrl = this.$resource('days{/day}');
        this.attendeesUrl = this.$resource('attendees{/id}');
    },

    mounted: function() {
        var ym = this.dateToString(this.state.date, true);
        this.getSummary({start: ym, end: ym});
        this.getDay(this.state.date);
    },

    methods: {
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
            console.log('getSummary');
            console.log(params);
            if (!params) {
                params = {};
            }
            params['summary'] = true;
            this.daysUrl.query(params).then((response) => {
                return response.json();
            }, (response) => {
                alert('failed get resource');
            }).then((json) => {
                console.log('summary data');
                console.log(json);
            });
        },

        getDay(day) {
            console.log("getDay");
            console.log(day);
            if (day) {
                day = this.dateToString(day);
            } else {
                day = this.state.day.day;
            }
            this.daysUrl.get({day: day}).then((response) => {
                return response.json();
            }, (response) => {
                alert('failed get resource');
            }).then((json) => {
                console.log('day data');
                console.log(json);
                this.state.day = json;
            });
        },

        addAttendee(group, newAttendee) {
            console.log(group);
            console.log(newAttendee);
            this.newAttendee = '';
            this.attendeesUrl.save({day: this.state.day.day, group: group, name: newAttendee}).then((response) => {
                return response.json();
            }, (response) => {
                alert('failed get resource');
            }).then((json) => {
                console.log('attendee data');
                console.log(json);
                this.getDay();
            });
        }
    },

    components: {
        Datepicker
    }
}
</script>

<style>
#app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;
    margin-top: 60px;
}
</style>
