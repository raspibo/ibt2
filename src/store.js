
export default {
    state: {
        loggedInUser: {username: ''}
    },
    mutations: {
        clearLoggedInUser(state, user) {
            state.loggedInUser = {username: ''};
        },
        setLoggedInUser(state, user) {
            state.loggedInUser = user;
        }
    }
};

