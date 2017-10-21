<template>
    <div id="settings">
        <md-card>
            <md-card-header>
                <span class="md-title">Settings</span>
            </md-card-header>
            <md-card-content v-if="loggedInUser.isAdmin">
                <div class="md-headline">
                    Prevent modifications from unregistered users:
                </div>
                <div class="protection-sect">
                    <md-switch v-model="shownSettings.protectUnregistered" class="md-warn">unregistered attendees (modify and delete)</md-switch>

                    <br />
                    <md-switch v-model="shownSettings.protectGroupNotes" class="md-warn">group notes</md-switch>

                    <br />
                    <md-switch v-model="shownSettings.protectGroupName" class="md-warn">group name</md-switch>

                    <br />
                    <md-switch v-model="shownSettings.protectDayNotes" class="md-warn">day notes</md-switch>

                </div>

                <br />
                <div class="md-headline">
                    Message of the day
                </div>
                <md-switch v-model="shownSettings.showMotd" class="md-warn">show motd</md-switch>

                <md-input-container v-if="shownSettings.showMotd">
                    <label>message</label>
                    <md-textarea v-model="shownSettings.motd"></md-textarea>
                </md-input-container>

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
<style scoped>

#settings {
    padding: 10px;
}

#save-button {
    margin-top: 40px;
}

.protection-sect {
    padding-left: 30px;
}

</style>
