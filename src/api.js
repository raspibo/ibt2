// The application's small REST interface, implemented with browser Fetch.
export function resource(template) {
    async function request(method, params = {}, body) {
        const remaining = { ...params };
        const path = template.replace(/\{\/(\w+)\}/g, (_, key) => {
            const value = remaining[key];
            delete remaining[key];
            return value == null ? '' : '/' + encodeURIComponent(value);
        });
        const query = new URLSearchParams(remaining).toString();
        const response = await fetch('/' + path + (query ? '?' + query : ''), {
            method,
            credentials: 'same-origin',
            headers: body === undefined ? {} : { 'Content-Type': 'application/json' },
            body: body === undefined ? undefined : JSON.stringify(body),
        });
        if (!response.ok) {
            const error = new Error(`HTTP ${response.status}`);
            error.status = response.status;
            error.body = await response.json().catch(() => ({}));
            throw error;
        }
        return response;
    }
    return {
        get: params => request('GET', params),
        query: params => request('GET', params),
        save: body => request('POST', {}, body),
        update: (params, body) => request('PUT', params, body),
        delete: params => request('DELETE', params),
    };
}
