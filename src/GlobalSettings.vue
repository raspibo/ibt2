<template>
    <div id="settings">
        <article class="ibt-card">
            <header class="ibt-card-header">
                <span class="ibt-title">Settings</span>
            </header>
            <div v-if="loggedInUser.isAdmin" class="ibt-card-content">
                <div class="ibt-headline">
                    Prevent modifications from unregistered users:
                </div>
                <div class="protection-sect">
                    <label class="setting-switch"><ToggleSwitch v-model="shownSettings.protectUnregistered" /><span>unregistered attendees (modify and delete)</span></label>

                    <br />
                    <label class="setting-switch"><ToggleSwitch v-model="shownSettings.protectGroupNotes" /><span>group notes</span></label>

                    <br />
                    <label class="setting-switch"><ToggleSwitch v-model="shownSettings.protectGroupName" /><span>group name</span></label>

                    <br />
                    <label class="setting-switch"><ToggleSwitch v-model="shownSettings.protectDayNotes" /><span>day notes</span></label>

                </div>

                <br />
                <div class="ibt-headline">
                    Message of the day
                </div>
                <label class="setting-switch"><ToggleSwitch v-model="shownSettings.showMotd" /><span>show motd</span></label>

                <label v-if="shownSettings.showMotd" class="ibt-input-container">
                    <span class="field-label">message</span>
                    <Textarea v-model="shownSettings.motd"></Textarea>
                </label>

                <br />
                <Button id="save-button" class="ibt-raised ibt-primary" @click="save()">Save</Button>
            </div>
            <div v-else class="ibt-card-content">
                Only admin are allowed to change global settings.
            </div>
        </article>
        <ibt-dialog ref="dialogObj" />
        <ibt-snackbar ref="snackbarObj" />
    </div>
</template>
<script>
import { resource } from './api.js';

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
        this.settingsUrl = resource('settings');
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
            }).then((json) => {
                if (!json || json.error) {
                    this.$refs.dialogObj.show({text: 'unable to fetch settings: ' + ((json && json.message) || '')});
                } else {
                    this.$store.commit('updateSettings', json);
                }
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to fetch settings'});
            });
        },

        save() {
            this.settingsUrl.save(this.shownSettings).then((response) => {
                return response.json();
            }).then((json) => {
                if (!json || json.error) {
                    this.$refs.dialogObj.show({text: 'unable to update settings: ' + (json && json.message) || ''});
                } else {
                    this.fetchSettings();
                    this.$refs.snackbarObj.show('settings saved');
                }
            }).catch((response) => {
                this.$refs.dialogObj.show({text: 'unable to update settings'});
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
