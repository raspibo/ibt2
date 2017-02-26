<template>
    <div id="settings">
        <md-card>
            <md-card-header>
                <span class="md-title">Settings</span>
            </md-card-header>
            <md-card-content v-if="loggedInUser.isAdmin">
                <md-switch v-model="shownSettings.protectUnregistered" class="md-warn">protect unregistered attendees (only admins can modify or delete)</md-switch>

                <br />
                <md-switch v-model="shownSettings.protectGroupNotes" class="md-warn">protect group notes</md-switch>

                <br />
                <md-switch v-model="shownSettings.protectGroupName" class="md-warn">protect group name</md-switch>

                <br />
                <md-switch v-model="shownSettings.protectDayNotes" class="md-warn">protect day notes</md-switch>
                <br />
                <md-button id="save-button" class="md-raised md-primary" @click="save()">Save</md-button>
            </md-card-content>
            <md-card-content v-else>
                Only admin are allowed to change global settings.
            </md-card-content>
        </md-card>
        <ibt-dialog ref="dialogObj" />
        <ibt-snackbar ref="snackbarObj" />
    </div>
</template>
<script>

import IbtDialog from './IbtDialog.vue';
import IbtSnackbar from './IbtSnackbar.vue';

export default {

    computed: {
        loggedInUser() {
            return this.$store.state.loggedInUser;
        },

        shownSettings() {
            return this.$store.state.settings || {};
        }
    },

    beforeCreate: function() {
        this.settingsUrl = this.$resource('settings');
    },

    mounted: function() {
        this.fetchSettings();
    },

    methods: {
        fetchSettings() {
            // XXX: duplicated code from App.vue; move this login
            // near the store.
            this.settingsUrl.get().then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to fetch settings'});
            }).then((json) => {
                if (!json || json.error) {
                    this.$refs.dialogObj.show({text: 'unable to fetch settings: ' + (json && json.message) || ''});
                } else {
                    this.$store.commit('updateSettings', json);
                }
            });
        },

        save() {
            this.settingsUrl.save(this.shownSettings).then((response) => {
                return response.json();
            }, (response) => {
                this.$refs.dialogObj.show({text: 'unable to update settings'});
            }).then((json) => {
                if (!json || json.error) {
                    this.$refs.dialogObj.show({text: 'unable to update settings: ' + (json && json.message) || ''});
                } else {
                    this.fetchSettings();
                    this.$refs.snackbarObj.show('settings saved');
                }
            });
        }
    },

    components: { IbtDialog, IbtSnackbar }
}

</script>
<style>

#settings {
    padding: 10px;
}

#save-button {
    margin-top: 40px;
}

</style>
