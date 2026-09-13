// Run with playwright-core and its Chromium browser installed; see docs/UI-TESTING.md.
const assert = require('node:assert/strict');
const { chromium } = require('playwright-core');

(async () => {
    const browser = await chromium.launch({ headless: true });
    try {
        const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
        page.setDefaultTimeout(10000);
        const errors = [];
        const writes = [];
        let currentUser = { username: '' };
        let settings = { protectUnregistered: false, protectGroupNotes: false,
            protectGroupName: false, protectDayNotes: false, showMotd: true, motd: 'Welcome' };
        const day = { day: '2026-09-13', notes: 'Meeting notes', groups: [
            { group: 'Example meeting', notes: 'Group notes', attendees: [
                { _id: '1', name: 'Alice', notes: 'Bringing a laptop', created_by: null }
            ] }
        ] };
        page.on('pageerror', error => { errors.push(error.message); console.error('Browser error:', error.message); });
        await page.route('**/*', async route => {
            const request = route.request();
            const path = new URL(request.url()).pathname;
            const method = request.method();
            const data = method === 'POST' || method === 'PUT' ? request.postDataJSON() : null;
            if (method !== 'GET') writes.push({ path, method, data });
            let body;
            if (path === '/settings') {
                if (data) settings = data;
                body = settings;
            } else if (path === '/login') {
                currentUser = { _id: 'admin', username: data.username, isAdmin: true, email: '' };
                body = currentUser;
            } else if (path === '/logout') {
                currentUser = { username: '' }; body = {};
            } else if (path === '/users/current' || path === '/users/admin') {
                if (data) currentUser = data;
                body = currentUser;
            } else if (path === '/users') {
                body = { users: [currentUser] };
            } else if (path === '/days') {
                body = { days: [{ day: day.day }] };
            } else if (/^\/days\/[^/]+\/info$/.test(path)) {
                if (data) day.notes = data.notes;
                body = day;
            } else if (/^\/days\/[^/]+\/groups\/[^/]+\/info$/.test(path)) {
                const group = day.groups.find(g => g.group === decodeURIComponent(path.split('/')[4]));
                if (data) group.notes = data.notes;
                body = group;
            } else if (/^\/days\/[^/]+$/.test(path)) {
                body = day;
            } else if (path === '/attendees' && data) {
                let group = day.groups.find(g => g.group === data.group);
                if (!group) { group = { group: data.group, notes: '', attendees: [] }; day.groups.push(group); }
                body = { ...data, _id: String(writes.length + 1), created_by: null };
                group.attendees.push(body);
            } else if (path.startsWith('/attendees/')) {
                const id = path.split('/')[2];
                for (const group of day.groups) {
                    if (method === 'DELETE') group.attendees = group.attendees.filter(a => a._id !== id);
                    if (method === 'PUT') group.attendees = group.attendees.map(a => a._id === id ? data : a);
                }
                body = data || {};
            } else {
                // Never forward an unhandled API mutation to a real backend.
                if (method !== 'GET') throw new Error(`Unexpected request: ${method} ${path}`);
                return route.continue();
            }
            return route.fulfill({ json: body });
        });
        if (process.env.IBT2_UI_SCREENSHOT_DIR) await require('node:fs/promises').mkdir(process.env.IBT2_UI_SCREENSHOT_DIR, { recursive: true });
        const screenshot = async name => {
            if (process.env.IBT2_UI_SCREENSHOT_DIR) await page.screenshot({ path: `${process.env.IBT2_UI_SCREENSHOT_DIR}/${name}.png`, fullPage: true });
        };
        const settle = () => page.waitForTimeout(200); // Legacy inputs debounce their model updates by 100 ms.
        const fill = async (locator, value) => { await locator.fill(value); await settle(); };
        const card = page.locator('.group-layout .md-card').filter({ hasText: 'Example meeting' });
        const newCard = page.locator('.group-layout .md-card').filter({ has: page.locator('input.group-add-name') });
        await page.goto(process.env.IBT2_UI_URL || 'http://127.0.0.1:8081');
        await card.waitFor();
        await page.locator('input.group-add-name').waitFor();
        await settle();
        await screenshot('desktop');
        const nameBox = await card.locator('.new-attendee input').boundingBox();
        const notesBox = await card.locator('.new-attendee-notes').boundingBox();
        assert(nameBox.width > 150, 'Attendee input must not collapse');
        assert(Math.abs(nameBox.x - notesBox.x) < 1, 'Attendee and notes fields must align');
        assert(await newCard.locator('input.group-add-name').evaluate(e => e.previousElementSibling.tagName === 'LABEL'));
        await fill(page.getByPlaceholder('username'), 'test-admin');
        await page.getByPlaceholder('username').press('Enter');
        assert(await page.getByPlaceholder('password').evaluate(e => e === document.activeElement));
        await fill(page.getByPlaceholder('password'), 'test-password');
        await page.locator('.md-toggle-password').click();
        assert.equal(await page.getByPlaceholder('password').getAttribute('type'), 'text');
        await page.getByPlaceholder('password').press('Enter');
        await page.locator('#logged-in').waitFor();
        assert.deepEqual(writes.find(w => w.path === '/login').data, { username: 'test-admin', password: 'test-password' });
        await fill(card.locator('.new-attendee input'), 'Bob');
        await fill(card.locator('.new-attendee-notes'), 'Projector');
        await card.locator('.new-attendee-notes').press('Enter');
        await page.getByText('Bob', { exact: true }).waitFor();
        assert.equal(day.groups[0].attendees.at(-1).notes, 'Projector');
        await fill(newCard.locator('input.group-add-name'), 'Second meeting');
        await newCard.locator('input.group-add-name').press('Enter');
        assert(await newCard.locator('.new-attendee input').evaluate(e => e === document.activeElement));
        await fill(newCard.locator('.new-attendee input'), 'Carol');
        await newCard.locator('.attendee-add .md-icon').click();
        await page.getByText('Carol', { exact: true }).waitFor();
        assert.equal(await newCard.locator('input.group-add-name').inputValue(), '');
        const alice = page.locator('.attendee-list-item').filter({ hasText: 'Alice' });
        await alice.locator('.md-menu button').click();
        const editButton = page.locator('.md-menu-content.md-active').getByRole('menuitem', { name: 'edit', exact: true });
        await page.locator('.md-menu-content.md-active').press('ArrowDown');
        assert(await editButton.evaluate(e => e === document.activeElement));
        await editButton.press('Enter');
        const editor = page.locator('.attendee-editor');
        await editor.waitFor();
        await fill(editor.locator('input').first(), 'Alice updated');
        await editor.locator('input').first().press('Enter');
        await page.getByText('Alice updated', { exact: true }).waitFor();
        assert.equal(writes.filter(w => w.path === '/attendees/1' && w.method === 'PUT').length, 1);
        await page.locator('#day-info .md-menu button').click();
        await page.locator('.md-menu-content.md-active .md-menu-item').filter({ hasText: 'edit notes' }).click();
        const dialog = page.locator('.md-dialog-container.md-active .md-dialog');
        await dialog.waitFor();
        await fill(dialog.locator('input, textarea'), 'Updated day notes');
        await dialog.getByRole('button', { name: 'ok', exact: true }).click();
        await page.getByText('Updated day notes', { exact: true }).waitFor();
        // Exercise the other legacy controls and navigation after the compat compiler change.
        await page.locator('button').filter({ has: page.locator('.md-icon', { hasText: /^settings$/ }) }).click();
        await page.locator('#settings').waitFor();
        await page.locator('.md-switch-container').first().click();
        await page.locator('#save-button').click();
        await settle();
        assert.equal(settings.protectUnregistered, true);
        await page.locator('.snackbar-close').click();
        await page.locator('#logged-in-icon').click();
        await page.locator('#user').waitFor();
        await fill(page.locator('#user input').first(), 'test@example.invalid');
        await page.locator('#save-button').click();
        await settle();
        assert.equal(currentUser.email, 'test@example.invalid');
        await page.locator('.home-link').click();
        await card.waitFor();
        for (const width of [1280, 768, 375, 320]) {
            await page.setViewportSize({ width, height: 900 });
            await settle();
            assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Page overflows at ${width}px`);
            for (const input of await page.locator('.group-layout input:visible').all()) {
                const box = await input.boundingBox();
                assert(box.width > 100 && box.x >= 0 && box.x + box.width <= width, `Input clipped at ${width}px`);
            }
        }
        await page.locator('#logout-icon').click();
        await page.getByPlaceholder('username').waitFor();
        for (const width of [375, 320]) {
            await page.setViewportSize({ width, height: 900 }); await settle();
            assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Login overflows at ${width}px`);
            await screenshot(`mobile-${width}`);
        }
        assert.deepEqual(errors, [], 'No browser runtime errors');
        console.log('PASS: layout, login, password toggle, attendee add/edit, group creation, day notes, settings, profile, responsive widths, logout');
    } finally {
        await browser.close();
    }
})().catch(error => { console.error(error); process.exitCode = 1; });
