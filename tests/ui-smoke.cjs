// Run with playwright-core and its Chromium browser installed; see docs/UI-TESTING.md.
const assert = require('node:assert/strict');
const { chromium } = require('playwright-core');

(async () => {
    const browser = await chromium.launch({ headless: true });
    try {
        const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
        page.setDefaultTimeout(10000);
        const errors = [];
        const warnings = [];
        const writes = [];
        const reads = [];
        let failNextAttendee = false;
        let currentUser = { username: '' };
        let settings = { protectUnregistered: false, protectGroupNotes: false,
            protectGroupName: false, protectDayNotes: false, showMotd: true, motd: 'Welcome' };
        const day = { day: '2026-09-13', notes: 'Meeting notes', groups: [
            { group: 'Example meeting', notes: 'Group notes <img src="x" onerror="window.markdownScriptExecuted = true">', attendees: [
                { _id: '1', name: 'Alice', notes: 'Bringing a laptop', created_by: null }
            ] }
        ] };
        page.on('pageerror', error => { errors.push(error.message); console.error('Browser error:', error.message); });
        page.on('console', message => {
            if (message.type() === 'warning' && message.text().includes('[Vue warn]')) warnings.push(message.text());
        });
        await page.route('**/*', async route => {
            const request = route.request();
            const path = new URL(request.url()).pathname;
            const method = request.method();
            const data = method === 'POST' || method === 'PUT' ? request.postDataJSON() : null;
            if (method !== 'GET') writes.push({ path, method, data });
            else reads.push(new URL(request.url()));
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
            } else if (/^\/days\/[^/]+\/groups\/[^/]+$/.test(path)) {
                const name = decodeURIComponent(path.split('/')[4]);
                const group = day.groups.find(g => g.group === name);
                if (method === 'PUT') group.group = data.newName;
                if (method === 'DELETE') day.groups = day.groups.filter(g => g !== group);
                body = group || {};
            } else if (/^\/days\/[^/]+$/.test(path)) {
                body = { ...day, day: path.split('/')[2] };
            } else if (path === '/attendees' && data) {
                if (failNextAttendee) {
                    failNextAttendee = false;
                    return route.fulfill({ status: 400, json: { message: 'Rejected test attendee' } });
                }
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
        const card = page.locator('.group-layout .ibt-card').filter({ hasText: 'Example meeting' });
        const newCard = page.locator('.group-layout .ibt-card').filter({ has: page.locator('input.group-add-name') });
        await page.clock.setFixedTime(new Date('2026-09-13T12:00:00'));
        await page.goto(process.env.IBT2_UI_URL || 'http://127.0.0.1:8081');
        await card.waitFor();
        await page.locator('input.group-add-name').waitFor();
        await settle();
        await page.locator('#datepicker').waitFor();
        assert.equal(await page.evaluate(() => window.markdownScriptExecuted), undefined);
        assert.equal(await card.locator('.group-notes [onerror]').count(), 0, 'Markdown event handlers are stripped');
        assert.equal(await page.locator('#datepicker .event-date').innerText(), '13');
        await page.locator('#datepicker').getByRole('button', { name: 'Next Month' }).click();
        await settle();
        assert(reads.some(url => url.pathname === '/days' && url.searchParams.get('start') === '2026-10'));
        assert(page.url().endsWith('/day/2026-09-13'), 'Browsing months preserves the selected day');
        await page.locator('#datepicker').getByRole('button', { name: 'Previous Month' }).click();
        await page.locator('#datepicker').getByText('14', { exact: true }).click();
        await page.waitForURL('**/#/day/2026-09-14');
        await page.goBack();
        await page.waitForURL('**/#/day/2026-09-13');
        await screenshot('desktop');
        const nameBox = await card.locator('.new-attendee input').boundingBox();
        const notesBox = await card.locator('.new-attendee-notes').boundingBox();
        assert(nameBox.width > 150, 'Attendee input must not collapse');
        assert(Math.abs(nameBox.x - notesBox.x) < 1, 'Attendee and notes fields must align');
        assert(await newCard.locator('input.group-add-name').evaluate(e => e.previousElementSibling.classList.contains('field-label')));
        await fill(page.getByPlaceholder('username'), 'test-admin');
        await page.getByPlaceholder('username').press('Enter');
        assert(await page.getByPlaceholder('password').evaluate(e => e === document.activeElement));
        await fill(page.getByPlaceholder('password'), 'test-password');
        await page.locator('#password-input [data-pc-section=unmaskicon]').click();
        assert.equal(await page.getByPlaceholder('password').getAttribute('type'), 'text');
        await page.getByPlaceholder('password').press('Enter');
        await page.locator('#logged-in').waitFor();
        assert.deepEqual(writes.find(w => w.path === '/login').data, { username: 'test-admin', password: 'test-password' });
        await fill(card.locator('.new-attendee input'), 'Bob');
        await fill(card.locator('.new-attendee-notes'), 'Projector');
        await card.locator('.new-attendee-notes').press('Enter');
        await page.getByText('Bob', { exact: true }).waitFor();
        assert.equal(day.groups[0].attendees.at(-1).notes, 'Projector');
        failNextAttendee = true;
        await fill(card.locator('.new-attendee input'), 'Retry attendee');
        await card.locator('.new-attendee input').press('Enter');
        const errorDialog = page.getByRole('dialog', { name: 'Error' });
        await errorDialog.waitFor();
        assert((await errorDialog.innerText()).includes('Rejected test attendee'));
        await errorDialog.getByRole('button', { name: 'ok', exact: true }).click();
        assert.equal(await card.locator('.new-attendee input').inputValue(), 'Retry attendee', 'Failed writes preserve the draft');
        await fill(card.locator('.new-attendee input'), '');
        await fill(newCard.locator('input.group-add-name'), 'Second meeting');
        await newCard.locator('input.group-add-name').press('Enter');
        assert(await newCard.locator('.new-attendee input').evaluate(e => e === document.activeElement));
        await fill(newCard.locator('.new-attendee input'), 'Carol');
        await newCard.getByRole('button', { name: 'Add attendee' }).click();
        await page.getByText('Carol', { exact: true }).waitFor();
        assert.equal(await newCard.locator('input.group-add-name').inputValue(), '');
        const alice = page.locator('.attendee-list-item').filter({ hasText: 'Alice' });
        await alice.getByRole('button', { name: 'Actions' }).click();
        const editButton = page.getByRole('menuitem', { name: 'edit', exact: true });
        await page.getByRole('menu').press('Home');
        assert.equal(await page.getByRole('menu').getAttribute('aria-activedescendant'), await editButton.getAttribute('id'));
        await page.getByRole('menu').press('Enter');
        const editor = page.locator('.attendee-editor');
        await editor.waitFor();
        await fill(editor.locator('input').first(), 'Alice updated');
        await editor.locator('input').first().press('Enter');
        await page.getByText('Alice updated', { exact: true }).waitFor();
        assert.equal(writes.filter(w => w.path === '/attendees/1' && w.method === 'PUT').length, 1);
        await page.locator('#day-info').getByRole('button', { name: 'Actions' }).click();
        await page.getByRole('menuitem', { name: 'edit notes' }).click();
        const dialog = page.getByRole('dialog');
        await dialog.waitFor();
        await fill(dialog.locator('input, textarea'), 'Updated day notes');
        await dialog.getByRole('button', { name: 'ok', exact: true }).click();
        await page.getByText('Updated day notes', { exact: true }).waitFor();
        await card.getByRole('button', { name: 'Actions' }).first().click();
        await page.getByRole('menuitem', { name: 'edit notes' }).click();
        await fill(page.getByRole('dialog').getByRole('textbox'), 'Updated group notes');
        await page.getByRole('dialog').getByRole('button', { name: 'ok', exact: true }).click();
        await card.getByText('Updated group notes').waitFor();
        await card.getByRole('button', { name: 'Actions' }).first().click();
        await page.getByRole('menuitem', { name: 'rename group' }).click();
        await fill(page.getByRole('dialog').getByRole('textbox'), 'Renamed / Café');
        await page.getByRole('dialog').getByRole('button', { name: 'ok', exact: true }).click();
        const renamedCard = page.locator('.group-layout .ibt-card').filter({ hasText: 'Renamed / Café' });
        await renamedCard.waitFor();
        await renamedCard.getByRole('button', { name: 'Actions' }).first().click();
        await page.getByRole('menuitem', { name: 'rename group' }).click();
        await fill(page.getByRole('dialog').getByRole('textbox'), 'Example meeting');
        await page.getByRole('dialog').getByRole('button', { name: 'ok', exact: true }).click();
        await card.waitFor();
        assert(writes.some(write => write.path.includes('Renamed%20%2F%20Caf%C3%A9')), 'Group path parameters are URL encoded');
        const secondCard = page.locator('.group-layout .ibt-card').filter({ hasText: 'Second meeting' });
        await secondCard.getByRole('button', { name: 'Actions' }).first().click();
        await page.getByRole('menuitem', { name: 'delete group' }).click();
        await page.getByRole('dialog').getByRole('button', { name: 'cancel', exact: true }).click();
        assert(day.groups.some(group => group.group === 'Second meeting'), 'Cancel preserves the group');
        await secondCard.getByRole('button', { name: 'Actions' }).first().click();
        await page.getByRole('menuitem', { name: 'delete group' }).click();
        await page.getByRole('dialog').getByRole('button', { name: 'ok', exact: true }).click();
        await secondCard.waitFor({ state: 'hidden' });
        // Exercise native Vue 3 controls and navigation.
        await page.getByRole('button', { name: 'Global settings' }).click();
        await page.locator('#settings').waitFor();
        await page.getByRole('switch').first().click();
        await page.locator('#save-button').click();
        await settle();
        assert.equal(settings.protectUnregistered, true);
        await page.locator('.ibt-snackbar').getByRole('button', { name: 'Close' }).click();
        await page.locator('#logged-in-icon').click();
        await page.locator('#user').waitFor();
        await fill(page.locator('#user input').first(), 'test@example.invalid');
        await page.locator('#save-button').click();
        await settle();
        assert.equal(currentUser.email, 'test@example.invalid');
        await page.getByRole('button', { name: 'Users', exact: true }).click();
        await page.locator('#users').waitFor();
        await page.locator('#users').getByRole('link', { name: 'test-admin', exact: true }).click();
        await page.locator('#user').waitFor();
        await Promise.all([
            page.waitForResponse(response => new URL(response.url()).pathname === '/users/admin'),
            page.reload(),
        ]);
        await settle();
        assert.equal(await page.locator('#user input').first().inputValue(), 'test@example.invalid', 'Direct profile links load correctly');
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
        assert.equal(await page.getByPlaceholder('password').inputValue(), '', 'Logout clears the password field');
        assert.equal(await alice.getByRole('button', { name: 'Actions' }).count(), 0, 'Protected attendees cannot be edited after logout');
        await card.getByRole('button', { name: 'Actions' }).first().click();
        assert.equal(await page.getByRole('menuitem', { name: 'delete group' }).count(), 0, 'Group deletion is admin-only');
        await page.getByRole('menu').press('Escape');
        for (const width of [375, 320]) {
            await page.setViewportSize({ width, height: 900 }); await settle();
            assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Login overflows at ${width}px`);
            await screenshot(`mobile-${width}`);
        }
        assert.deepEqual(errors, [], 'No browser runtime errors');
        assert.deepEqual(warnings, [], 'No Vue migration or component warnings');
        console.log('PASS: layout, calendar and history, login, password toggle, attendee add/edit, failed requests, group create/rename/delete/notes, day notes, settings, users, profile, sanitized Markdown, responsive widths, logout');
    } finally {
        await browser.close();
    }
})().catch(error => { console.error(error); process.exitCode = 1; });
