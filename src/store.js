/*
 * Shared state of the ibt2 app.
 */

export default {
    state: {
        loggedInUser: {username: ''},
        settings: {}
    },
    mutations: {
        clearLoggedInUser(state, user) {
            state.loggedInUser = {username: ''};
        },

        setLoggedInUser(state, user) {
            state.loggedInUser = user;
        },

        updateSettings(state, settings) {
            state.settings = settings;
        }
    }
};

